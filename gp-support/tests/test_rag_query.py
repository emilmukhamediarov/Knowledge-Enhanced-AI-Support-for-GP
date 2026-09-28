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
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name in {'build_query_from_consultation_summary', 'build_follow_up_query'}]
        namespace = {}
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), namespace)
        cls.build = staticmethod(namespace['build_query_from_consultation_summary'])
        cls.build_live = staticmethod(namespace['build_follow_up_query'])

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

    def test_both_paths_preserve_context_without_narrative_or_bookkeeping(self):
        state = {
            'reason_for_visit': 'eye pain', 'symptoms': ['redness'],
            'symptom_location': 'left eye', 'onset': 'yesterday',
            'duration': 'one day', 'severity': 'moderate',
            'relevant_history': ['Does not wear contact lenses', 'No recent eye trauma'],
            'additional_concerns': 'difficulty reading',
            'medical_history': {'status': 'confirmed', 'items': ['asthma']},
            'current_medications': {'status': 'confirmed', 'items': ['salbutamol']},
            'allergies': {'status': 'confirmed', 'items': ['penicillin']},
            'summary': 'NARRATIVE_SENTINEL', 'consultation_id': 987654321,
            'missing_information': ['BOOKKEEPING_SENTINEL'], 'conversation_complete': False,
        }
        original = deepcopy(state)
        for builder in (self.build, self.build_live):
            with self.subTest(builder=builder.__name__):
                query = builder(state)
                for detail in ('eye pain', 'redness', 'left eye', 'yesterday', 'one day',
                               'moderate', 'Does not wear contact lenses', 'No recent eye trauma',
                               'difficulty reading', 'asthma', 'salbutamol', 'penicillin'):
                    self.assertIn(detail, query)
                for excluded in ('NARRATIVE_SENTINEL', 'BOOKKEEPING_SENTINEL', '987654321'):
                    self.assertNotIn(excluded, query)
        self.assertEqual(state, original)

    def test_confirmed_none_overrides_old_profile_in_live_query(self):
        state = {key: {'status': 'confirmed_none', 'items': []}
                 for key in ('medical_history', 'current_medications', 'allergies')}
        profile = {'age': 30, 'medical_history': 'old condition',
                   'medications': ['old medication'], 'allergies': ['old allergy']}
        original = deepcopy(profile)
        live = self.build_live(state, profile)
        for label in ('medical history', 'current medications', 'allergies'):
            self.assertIn(f'Confirmed {label}: none', live)
        self.assertNotIn('old', live)
        self.assertIn('Age: 30', live)
        final = self.build(state)
        for label in ('Medical history', 'Current medications', 'Allergies'):
            self.assertIn(f'{label}: patient reports none', final)
        self.assertEqual(profile, original)

    def test_confirmed_items_override_old_profile(self):
        state = {key: {'status': 'confirmed', 'items': [value]}
                 for key, value in [('medical_history', 'new condition'),
                                    ('current_medications', 'new medication'),
                                    ('allergies', 'new allergy')]}
        profile = {'medical_history': 'old condition', 'medications': ['old medication'],
                   'allergies': ['old allergy']}
        query = self.build_live(state, profile)
        self.assertNotIn('old', query)
        for value in ('new condition', 'new medication', 'new allergy'):
            self.assertIn(value, query)

    def test_unknown_background_uses_labelled_profile_without_inventing_negatives(self):
        profile = {'medical_history': 'asthma', 'medications': ['salbutamol'],
                   'allergies': ['penicillin']}
        for state in ({}, {key: {'status': 'unknown', 'items': []}
                          for key in ('medical_history', 'current_medications', 'allergies')}):
            query = self.build_live(state, profile)
            self.assertIn('Previously recorded medical history: asthma', query)
            self.assertIn('Previously recorded medications: salbutamol', query)
            self.assertIn('Previously recorded allergies: penicillin', query)
            self.assertNotIn('none', query)
            self.assertNotIn('patient reports none', self.build(state))
        self.assertEqual(self.build_live({}), '')

    def test_empty_new_live_fields_are_skipped(self):
        for concerns in (None, '', '   '):
            self.assertEqual(self.build_live({'relevant_history': [],
                                             'additional_concerns': concerns}), '')


if __name__ == '__main__':
    unittest.main()
