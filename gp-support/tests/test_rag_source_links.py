"""Offline tests for source lookup and the structured RAG response contract."""
import ast
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock


class SourceLinkTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        source = Path(__file__).parents[1] / 'app/services/knowledge_rag.py'
        tree = ast.parse(source.read_text())
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                     and n.name in {'_source_links', '_confidence_info', 'ask_structured'}]
        self.processor = MagicMock()
        self.synth = MagicMock()
        self.ns = dict(Path=Path, re=re, json=json, KNOWLEDGE_BASE_DIR=str(self.folder),
                       SimilarityPostprocessor=MagicMock(return_value=self.processor),
                       get_response_synthesizer=MagicMock(return_value=self.synth),
                       STRUCTURED_QA_PROMPT='unused')
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), self.ns)

    def node(self, name=None, **metadata):
        if name is not None:
            metadata['file_name'] = name
        return SimpleNamespace(node=SimpleNamespace(metadata=metadata, get_text=lambda: 'Retrieved chunk without URL'), score=0.8)

    def test_footer_only_multiple_documents_and_deduplication(self):
        (self.folder / 'a.txt').write_text('Body https://ignore.example\nSOURCES\nhttps://a.example/path\nhttps://b.example/path\n')
        (self.folder / 'b.txt').write_text('Sources:\nhttps://b.example/path\nhttps://c.example/path\n')
        result = self.ns['_source_links']([self.node('a.txt'), self.node('a.txt'), self.node('b.txt')])
        self.assertEqual(result, ['https://a.example/path', 'https://b.example/path', 'https://c.example/path'])

    def test_old_windows_file_path_and_crlf(self):
        (self.folder / 'a.txt').write_bytes(b'Body\r\nSources:\r\nhttps://a.example/path\r\n')
        self.assertEqual(self.ns['_source_links']([self.node(file_path=r'C:\old\knowledge_base\a.txt')]), ['https://a.example/path'])

    def test_missing_files_metadata_and_footers(self):
        (self.folder / 'a.txt').write_text('Body https://not-a-footer.example')
        self.assertEqual(self.ns['_source_links']([self.node('a.txt'), self.node('missing.txt'), self.node()]), [])

    def test_traversal_and_symlinks_outside_base_are_ignored(self):
        with TemporaryDirectory() as outside:
            target = Path(outside) / 'secret.txt'
            target.write_text('SOURCES\nhttps://outside.example')
            (self.folder / 'alias.txt').symlink_to(target)
            self.assertEqual(self.ns['_source_links']([self.node(str(target)), self.node('../secret.txt'), self.node('alias.txt')]), [])

    def response(self, raw, nodes):
        class Response:
            source_nodes = nodes
            def __str__(self):
                return raw
        return Response()

    def test_success_and_parse_error_include_links(self):
        (self.folder / 'a.txt').write_text('SOURCES\nhttps://a.example/path')
        nodes = [self.node('a.txt')]
        index = MagicMock()
        index.as_retriever.return_value.retrieve.return_value = nodes
        self.processor.postprocess_nodes.return_value = nodes
        for raw, error in [(json.dumps({'answer': 'Answer'}), False), ('Invalid JSON', True)]:
            with self.subTest(error=error):
                self.synth.synthesize.return_value = self.response(raw, nodes)
                result = self.ns['ask_structured'](index, 'Question')
                self.assertEqual(result['link'], ['https://a.example/path'])
                self.assertEqual(result['parse_error'], error)

    def test_no_match_returns_empty_links(self):
        index = MagicMock()
        index.as_retriever.return_value.retrieve.return_value = []
        self.processor.postprocess_nodes.return_value = []
        self.assertEqual(self.ns['ask_structured'](index, 'Question')['link'], [])
        self.synth.synthesize.assert_not_called()


if __name__ == '__main__':
    unittest.main()
