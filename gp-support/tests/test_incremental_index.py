"""Offline tests of indexing orchestration, without loading models or credentials."""
import ast
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock


class IncrementalIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve()
        # Execute the real function in isolation so these tests need neither
        # AWS/database credentials nor the large embedding-model dependencies.
        source = Path(__file__).parents[1] / 'app/services/knowledge_rag.py'
        tree = ast.parse(source.read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'update_index')
        self.store = MagicMock()
        self.connection = MagicMock()
        self.db = MagicMock()
        self.db.get_bind.return_value.begin.return_value.__enter__.return_value = self.connection
        self.reader = MagicMock()
        self.node = MagicMock(metadata={})
        self.settings = SimpleNamespace(text_splitter=MagicMock(), embed_model=MagicMock())
        self.settings.text_splitter.get_nodes_from_documents.return_value = [self.node]
        self.settings.embed_model.get_text_embedding_batch.return_value = [[0.1, 0.2]]
        self.namespace = dict(Path=Path, KNOWLEDGE_BASE_DIR=str(self.folder),
                              _configure_models=MagicMock(), _get_vector_store=lambda: self.store,
                              VectorStoreIndex=MagicMock(), text=lambda sql: sql,
                              SimpleDirectoryReader=self.reader, Settings=self.settings,
                              MetadataMode=SimpleNamespace(EMBED='embed'))
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), self.namespace)

    def run_update(self, names=(), exists=True):
        self.connection.execute.side_effect = [None, SimpleNamespace(scalar=lambda: exists), list((n,) for n in names)] if exists else [None, SimpleNamespace(scalar=lambda: False)]
        return self.namespace['update_index'](self.db)

    def test_only_new_files_are_embedded_and_repeat_is_noop(self):
        for name in ('old.txt', 'new.txt', '.hidden.txt'):
            (self.folder / name).write_text('text')
        self.run_update(['old.txt'])
        self.assertEqual(self.reader.call_args.kwargs['input_files'], [str(self.folder / 'new.txt')])
        self.assertTrue(self.reader.call_args.kwargs['raise_on_error'])
        self.store.add.assert_called_once_with([self.node])
        self.assertEqual(self.node.embedding, [0.1, 0.2])
        self.reader.reset_mock()
        self.run_update(['old.txt', 'new.txt'])
        self.reader.assert_not_called()
        self.assertEqual(self.store.add.call_count, 1)

    def test_missing_table_accepts_first_file(self):
        (self.folder / 'first.txt').write_text('text')
        self.run_update(exists=False)
        self.store.add.assert_called_once()

    def test_embedding_failure_does_not_write(self):
        (self.folder / 'new.txt').write_text('text')
        self.settings.embed_model.get_text_embedding_batch.side_effect = RuntimeError('embedding failed')
        with self.assertRaisesRegex(RuntimeError, 'embedding failed'):
            self.run_update()
        self.store.add.assert_not_called()

    def test_empty_directory_is_noop(self):
        self.run_update()
        self.store.add.assert_not_called()

    def test_empty_document_is_not_saved(self):
        (self.folder / 'empty.txt').touch()
        self.settings.text_splitter.get_nodes_from_documents.return_value = []
        self.run_update()
        self.store.add.assert_not_called()

    def test_database_failure_propagates_and_stops_later_files(self):
        for name in ('a.txt', 'b.txt'):
            (self.folder / name).write_text('text')
        self.store.add.side_effect = RuntimeError('database failed')
        with self.assertRaisesRegex(RuntimeError, 'database failed'):
            self.run_update()
        self.assertEqual(self.reader.call_count, 1)


if __name__ == '__main__':
    unittest.main()
