"""Offline query-builder tests; no model downloads or database access."""
import ast
from copy import deepcopy
from pathlib import Path
import unittest


class QueryBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).parents[1] / 'app/services/knowledge_rag.py'
        tree = ast.parse(source.read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'build_query_from_consultation_summary')
        namespace = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), namespace)
        cls.build = staticmethod(namespace[function.name])

    def test_preserves_patient_details_without_mutating_summary(self):
        summary = {
            'reason_for_visit': 'Cough', 'symptoms': ['cough', 'wheezing'],
            'symptom_location': 'chest', 'onset': 'started Monday',
            'duration': 'four weeks', 'severity': '8/10',
            'additional_concerns': 'blood in mucus',
            'medical_history': {'status': 'confirmed', 'items': ['asthma']},
            'current_medications': {'status': 'confirmed', 'items': ['salbutamol']},
            'allergies': {'status': 'confirmed', 'items': ['penicillin', 'latex']},
        }
        original = deepcopy(summary)
        query = self.build(summary)
        for detail in ('wheezing', 'chest', 'asthma', 'salbutamol',
                       'Onset: started Monday', 'Duration: four weeks',
                       'Severity: 8/10', 'Additional concerns: blood in mucus',
                       'Reported allergies: penicillin, latex'):
            self.assertIn(detail, query)
        self.assertEqual(query.lower().count('cough'), 1)
        self.assertEqual(summary, original)

    def test_duration_and_severity_change_query(self):
        base = {'symptoms': ['cough'], 'duration': 'two days', 'severity': 'mild'}
        query = self.build(base)
        self.assertNotEqual(query, self.build({**base, 'duration': 'four weeks'}))
        self.assertNotEqual(query, self.build({**base, 'severity': 'severe'}))

    def test_unknown_and_missing_allergies_are_not_negative_findings(self):
        for allergies in (None, {}, {'status': 'unknown', 'items': ['unconfirmed allergy']},
                          {'status': 'confirmed', 'items': []}):
            with self.subTest(allergies=allergies):
                query = self.build({'symptoms': ['cough'], 'allergies': allergies})
                self.assertNotIn('allerg', query.lower())

    def test_explicit_no_allergies_is_preserved(self):
        query = self.build({'allergies': {'status': 'confirmed_none', 'items': []}})
        self.assertIn('Allergies: patient reports none', query)

    def test_empty_and_blank_fields_keep_fallback(self):
        fallback = 'Clinical guidance and management for patient presentation.'
        self.assertEqual(self.build({}), fallback)
        self.assertEqual(self.build({'onset': None, 'duration': '', 'severity': '  ',
                                    'additional_concerns': None, 'allergies': None}), fallback)

    def test_each_new_text_field_is_used_even_without_symptoms(self):
        for field, label in [('onset', 'Onset'), ('duration', 'Duration'),
                             ('severity', 'Severity'), ('additional_concerns', 'Additional concerns')]:
            with self.subTest(field=field):
                self.assertIn(f'{label}: patient detail', self.build({field: ' patient detail '}))


if __name__ == '__main__':
    unittest.main()
