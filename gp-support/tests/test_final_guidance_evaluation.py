"""Offline checks that the evaluator does not turn bad results into successes."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from tests.final_guidance_cases import CASES
from tests.final_guidance_evaluation import (NO_MATCH, evaluate_case, grade, markdown,
                                           metrics, validate_cases)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.kb = Path(self.temp.name)
        (self.kb / 'A.txt').write_text('Anchor evidence\nSOURCES\nhttps://example.org/a\n')
        self.case = deepcopy(CASES[0])
        self.case.update(expected_sources=['A.txt'], evidence={'A.txt': 'Anchor evidence'},
                         answer_any=['sleep'], query_contains=['two weeks'])
        self.nodes = [{'file_name': 'A.txt', 'text': 'sleep evidence', 'score': .8}]
        self.result = {'answer': 'Sleep guidance', 'sources': ['sleep evidence'],
                       'link': ['https://example.org/a'], 'parse_error': False}

    def test_current_catalogue_evidence_is_valid(self):
        validate_cases(CASES)
        self.assertEqual(len(CASES), 28)

    def test_missing_evidence_is_rejected(self):
        self.case['evidence']['A.txt'] = 'not present'
        with self.assertRaises(ValueError):
            validate_cases([self.case], self.kb)

    def test_passes_traceable_source_and_link(self):
        checks, names = grade(self.case, 'two weeks', self.result, self.nodes, self.kb)
        self.assertTrue(all(checks.values()))
        self.assertEqual(names, ['A.txt'])

    def test_raw_candidate_is_not_counted_as_returned_source(self):
        result = dict(self.result, sources=[], link=[])
        checks, names = grade(self.case, 'two weeks', result, self.nodes, self.kb)
        self.assertFalse(checks['expected_source'])
        self.assertFalse(checks['answer_wording'])
        self.assertEqual(names, [])

    def test_bad_links_and_ambiguous_sources_fail(self):
        checks, _ = grade(self.case, 'two weeks', dict(self.result, link=['https://wrong.org']), self.nodes, self.kb)
        self.assertFalse(checks['source_links'])
        checks, _ = grade(self.case, 'two weeks', self.result,
                          self.nodes + [dict(self.nodes[0], file_name='B.txt')], self.kb)
        self.assertFalse(checks['source_traceability'])
        self.assertFalse(checks['expected_source'])

    def test_invalid_response_shapes_fail(self):
        for result in ([], {}, dict(self.result, answer=''), dict(self.result, sources='text'),
                       dict(self.result, parse_error=True)):
            with self.subTest(result=result):
                checks, _ = grade(self.case, 'two weeks', result, self.nodes, self.kb)
                self.assertFalse(checks['response_shape'])

    def test_abstention_contract_and_metric_denominators(self):
        negative = deepcopy(next(c for c in CASES if c['id'] == 'unsupported_travel'))
        result = {'answer': NO_MATCH, 'sources': [], 'link': [], 'parse_error': False}
        checks, _ = grade(negative, 'query', result, [], self.kb)
        self.assertTrue(checks['abstention'])
        self.assertNotIn('expected_source', checks)
        bad, _ = grade(negative, 'query', dict(result, answer=NO_MATCH+' Invented advice.'), [], self.kb)
        self.assertFalse(bad['abstention'])
        score = metrics([{'checks': checks}, {'checks': {'expected_source': False}}])
        self.assertEqual(score['abstention']['total'], 1)
        self.assertEqual(score['expected_source']['rate'], 0)

    def test_query_context_is_checked(self):
        checks, _ = grade(self.case, 'one day', self.result, self.nodes, self.kb)
        self.assertFalse(checks['query_context'])

    def test_production_path_called_once_and_input_not_mutated(self):
        class Index:
            def as_retriever(self, **kwargs):
                node = SimpleNamespace(metadata={'file_name': 'A.txt'}, get_text=lambda: 'sleep evidence')
                return SimpleNamespace(retrieve=lambda query: [SimpleNamespace(node=node, score=.8)])
        calls = []
        def ask(index, query):
            calls.append(query)
            index.as_retriever(similarity_top_k=2).retrieve(query)
            return self.result
        runtime = SimpleNamespace(build_query_from_consultation_summary=lambda s: 'two weeks', ask_structured=ask)
        original = deepcopy(self.case)
        row = evaluate_case(Index(), self.case, runtime, self.kb)
        self.assertEqual(calls, ['two weeks'])
        self.assertTrue(all(row['checks'].values()))
        self.assertEqual(self.case, original)
        row['repeat'] = 1
        report = {'cases': [row], 'metrics': metrics([row])}
        self.assertIn('Automatic checks only', markdown(report))
        self.assertNotIn('Reviewer decision: not_reviewed', markdown(report))
        self.assertNotIn('Manual evidence review is required', markdown(report))
        row['manual_review'] = {'status': 'reviewed', 'notes': 'Evidence checked.'}
        self.assertIn('Reviewer decision: reviewed. Notes: Evidence checked.', markdown(report))

    def test_runtime_errors_are_failed_not_excluded_or_leaked(self):
        def fail(*args):
            raise RuntimeError('secret connection details')
        runtime = SimpleNamespace(build_query_from_consultation_summary=lambda s: 'two weeks', ask_structured=fail)
        row = evaluate_case(None, self.case, runtime, self.kb)
        self.assertEqual(row['error'], 'RuntimeError')
        self.assertFalse(any(row['checks'].values()))
        self.assertNotIn('secret', str(row))

    def test_bunion_singular_and_plural_pass(self):
        for case_id in ('bunion', 'bunion_plain_language'):
            case = next(c for c in CASES if c['id'] == case_id)
            for answer in ('A bunion can cause this pain.', 'These symptoms align with bunions.'):
                checks, _ = grade(case, 'query', dict(self.result, answer=answer), self.nodes, self.kb)
                self.assertTrue(checks['answer_wording'])

    def test_missing_dose_acknowledgement_without_disease_keyword_passes(self):
        case = next(c for c in CASES if c['id'] == 'missing_dose')
        for answer in (
            'The exact personalised dose cannot be determined based on the provided context.',
            'The context does not provide a dose for this medicine.',
            'There is insufficient information to recommend a dosage.',
        ):
            checks, _ = grade(case, 'query', dict(self.result, answer=answer), self.nodes, self.kb)
            self.assertTrue(checks['answer_wording'], answer)

    def test_missing_dose_disclaimer_does_not_excuse_dosing_instruction(self):
        case = next(c for c in CASES if c['id'] == 'missing_dose')
        for instruction in ('Take 50 mg.', 'Take fifty milligrams.', 'Take one tablet.',
                            'Use twice daily.', 'Repeat every 4 hours.'):
            answer = 'The exact dose cannot be determined from the context. ' + instruction
            checks, _ = grade(case, 'query', dict(self.result, answer=answer), self.nodes, self.kb)
            self.assertFalse(checks['answer_wording'], instruction)

    def test_missing_dose_disease_keyword_alone_is_not_enough(self):
        case = next(c for c in CASES if c['id'] == 'missing_dose')
        checks, _ = grade(case, 'query', dict(self.result, answer='Migraine causes headache.'), self.nodes, self.kb)
        self.assertFalse(checks['answer_wording'])

    def test_uncovered_medical_does_not_claim_semantic_success(self):
        case = next(c for c in CASES if c['id'] == 'uncovered_tinnitus')
        for result in (self.result, dict(self.result, answer=NO_MATCH, sources=[], link=[])):
            checks, _ = grade(case, 'persistent tinnitus investigations', result, self.nodes, self.kb)
            self.assertNotIn('expected_source', checks)
            self.assertNotIn('answer_wording', checks)
            self.assertNotIn('abstention', checks)
            self.assertTrue(checks['response_shape'])
        row = {'id': case['id'], 'category': case['category'], 'repeat': 1,
               'checks': checks, 'error': None, 'query': 'query', 'result': result,
               'expectations': case, 'raw_candidates': []}
        self.assertIn('answer adequacy requires review', markdown({'cases': [row], 'metrics': metrics([row])}))
