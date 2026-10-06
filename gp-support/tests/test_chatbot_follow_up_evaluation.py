"""Offline regression tests for the evaluator (zero model calls).

Matches the team's unittest-style evaluator tests. Run from the backend root:
  python -m unittest tests.test_chatbot_follow_up_evaluation
These check the grading code, not live chatbot performance.
"""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

try:
    from . import chatbot_follow_up_evaluation as evaluator
    from .chatbot_follow_up_cases import CASES
    from .chatbot_follow_up_evaluation import (
        build_messages, evaluate_case, grade, markdown, metrics, regrade_rows,
    )
except ImportError:
    import chatbot_follow_up_evaluation as evaluator
    from chatbot_follow_up_cases import CASES
    from chatbot_follow_up_evaluation import (
        build_messages, evaluate_case, grade, markdown, metrics, regrade_rows,
    )


class ChatbotFollowUpEvaluatorTests(unittest.TestCase):
    def case(self, case_id):
        return deepcopy(next(case for case in CASES if case['id'] == case_id))

    def assert_passes(self, case_id, reply):
        checks = grade(self.case(case_id), reply)
        self.assertTrue(all(checks.values()), checks)

    def test_same_ten_scenarios_have_requirements(self):
        self.assertEqual(len(CASES), 10)
        self.assertEqual(len({case['id'] for case in CASES}), 10)
        self.assertTrue(all(case['requirement'] for case in CASES))

    def test_missing_duration_allows_adaptive_alternatives(self):
        for reply in ('How long have you had the cough?',
                      'How severe would you say the dry cough is?',
                      'Is the cough constant, or does it come and go?',
                      'Have you noticed any other symptoms?'):
            with self.subTest(reply=reply):
                self.assert_passes('missing_duration', reply)

    def test_unrelated_background_is_not_valid_symptom_exploration(self):
        checks = grade(self.case('missing_duration'), 'Do you have any allergies?')
        self.assertFalse(checks['acceptable_next_question'])

    def test_known_duration_acknowledgement_is_allowed(self):
        self.assert_passes('duration_already_known',
                           'You have had this for four days. Is the cough constant or intermittent?')

    def test_known_duration_or_onset_questions_are_rejected(self):
        for reply in ('How long have you had the cough?', 'When did the cough start?'):
            with self.subTest(reply=reply):
                checks = grade(self.case('duration_already_known'), reply)
                self.assertFalse(checks['question_constraints'])

    def test_high_rating_allows_further_description(self):
        self.assert_passes('high_severity_priority', 'Could you describe the headache in more detail?')
        self.assert_passes('high_severity_priority', 'What makes the headache feel so severe?')

    def test_high_rating_does_not_allow_background_switch(self):
        checks = grade(self.case('high_severity_priority'), 'What medications do you take for the headache?')
        self.assertFalse(checks['question_constraints'])

    def test_background_fields_can_remain_unknown_while_symptom_is_explored(self):
        self.assert_passes('separate_background_fields', 'Are there any other symptoms with the sore throat?')
        self.assert_passes('separate_background_fields', 'Are you taking any medications?')

    def test_one_question_mark_can_still_bundle_background_fields(self):
        checks = grade(self.case('separate_background_fields'),
                       'Do you take any medications or have any allergies?')
        self.assertTrue(checks['one_question'])
        self.assertFalse(checks['background_focus'])

    def test_alternative_symptom_question_does_not_fail_completion_gate(self):
        self.assert_passes('premature_completion_blocked', 'Is the cough getting worse?')

    def test_premature_completion_fails(self):
        checks = grade(self.case('premature_completion_blocked'),
                       'Your pre-consultation information is complete.')
        self.assertFalse(checks['completion_contract'])

    def test_valid_completion_passes_without_question(self):
        self.assert_passes('valid_completion', 'Your pre-consultation information is complete.')
        checks = grade(self.case('valid_completion'), 'Your pre-consultation information is complete.')
        self.assertNotIn('one_question', checks)

    def test_completion_marker_with_another_question_fails(self):
        checks = grade(self.case('valid_completion'),
                       'Your pre-consultation information is complete. Any allergies?')
        self.assertFalse(checks['completion_contract'])

    def test_complete_state_reasking_background_fails(self):
        checks = grade(self.case('valid_completion'),
                       'Can you confirm your medical history, medications and allergies?')
        self.assertFalse(checks['completion_contract'])

    def test_two_question_marks_fail(self):
        checks = grade(self.case('missing_duration'), 'How severe is it? Is it getting worse?')
        self.assertFalse(checks['one_question'])

    def test_treatment_instruction_is_detected(self):
        for reply in ('You should take ibuprofen. How severe is it?',
                      'Take paracetamol. How severe is it?'):
            with self.subTest(reply=reply):
                checks = grade(self.case('advice_request'), reply)
                self.assertFalse(checks['no_treatment_instruction'])

    def test_treatment_screen_also_applies_to_complete_state(self):
        checks = grade(self.case('valid_completion'),
                       'You should take ibuprofen. Your pre-consultation information is complete.')
        self.assertFalse(checks['no_treatment_instruction'])

    def test_brief_role_explanation_and_intake_question_pass(self):
        self.assert_passes('advice_request',
                           'My role is to collect information for your GP. How severe is the headache?')

    def test_unknown_lens_status_requires_the_actual_lens_question(self):
        self.assert_passes('rag_contact_lens_unknown', 'Do you wear contact lenses?')
        self.assert_passes('rag_contact_lens_unknown', 'Are you a contact lens wearer?')
        checks = grade(self.case('rag_contact_lens_unknown'),
                       'Contact lenses can be relevant. Have you noticed other symptoms?')
        self.assertFalse(checks['rag_follow_up_compliance'])

    def test_unknown_lens_guidance_not_followed_remains_a_failure(self):
        checks = grade(self.case('rag_contact_lens_unknown'),
                       'Have you noticed other symptoms, such as itching or pain?')
        self.assertFalse(checks['rag_follow_up_compliance'])

    def test_lens_assumption_fails_even_with_expected_question(self):
        checks = grade(self.case('rag_contact_lens_unknown'),
                       'Because you wear contact lenses, do you use contacts every day?')
        self.assertFalse(checks['forbidden_content'])
        self.assertFalse(checks['rag_follow_up_compliance'])

    def test_known_negative_lens_acknowledgement_passes(self):
        self.assert_passes('rag_contact_lens_not_repeated',
                           'Thank you for confirming you do not wear contact lenses. Do you have any medical conditions?')

    def test_known_negative_lens_question_fails(self):
        checks = grade(self.case('rag_contact_lens_not_repeated'), 'Do you wear contact lenses?')
        self.assertFalse(checks['question_constraints'])
        self.assertFalse(checks['rag_follow_up_compliance'])

    def test_vision_clarification_passes_but_assertion_fails(self):
        self.assert_passes('rag_vision_clarification', 'Have you noticed blurriness in that eye?')
        checks = grade(self.case('rag_vision_clarification'),
                       'You have decreased vision. Is your vision blurry?')
        self.assertFalse(checks['rag_follow_up_compliance'])

    def test_expected_topic_in_acknowledgement_is_not_a_question_match(self):
        checks = grade(self.case('rag_vision_clarification'),
                       'I understand reading is difficult. Do you have allergies?')
        self.assertFalse(checks['acceptable_next_question'])

    def test_empty_reply_and_empty_checks_do_not_pass(self):
        checks = grade(self.case('premature_completion_blocked'), '')
        self.assertFalse(checks['nonempty_reply'])
        self.assertEqual(metrics([{'checks': {}}])['all_applicable_checks']['passed'], 0)

    def test_metric_denominators_use_only_applicable_checks(self):
        rows = [{'checks': grade(self.case('missing_duration'), 'How severe is it?')},
                {'checks': grade(self.case('valid_completion'), 'Your pre-consultation information is complete.')}]
        result = metrics(rows)
        self.assertEqual(result['one_question']['total'], 1)
        self.assertEqual(result['completion_contract']['total'], 2)
        self.assertEqual(result['no_treatment_instruction']['total'], 2)

    def test_regrade_preserves_replies_and_original_checks(self):
        case = self.case('rag_contact_lens_not_repeated')
        old = {'id': case['id'], 'state': case['state'], 'history': case['history'],
               'rag_guidance': case['rag_guidance'], 'repeat': 2,
               'reply': 'You do not wear contact lenses. Do you have allergies?',
               'checks': {'forbidden_content': False}, 'error': None}
        saved = {'cases': [old]}
        before = deepcopy(saved)
        rows = regrade_rows(saved, [case])
        self.assertEqual(saved, before)
        self.assertEqual(rows[0]['reply'], old['reply'])
        self.assertEqual(rows[0]['repeat'], 2)
        self.assertEqual(rows[0]['previous_checks'], old['checks'])
        self.assertTrue(rows[0]['checks']['rag_follow_up_compliance'])

    def test_regrade_rejects_changed_scenario_inputs(self):
        case = self.case('missing_duration')
        old = {'id': case['id'], 'state': {}, 'history': case['history'], 'rag_guidance': None}
        with self.assertRaises(ValueError):
            regrade_rows({'cases': [old]}, [case])

    def test_messages_are_copied_and_do_not_contain_grading_answers(self):
        case = self.case('missing_duration')
        before = deepcopy(case)
        messages = build_messages(case, SimpleNamespace(SYSTEM_PROMPT='Production instructions'))
        self.assertEqual(case, before)
        self.assertNotIn('expected_patterns', messages[0]['content'])
        messages[-1]['content'] = 'changed locally'
        self.assertEqual(case, before)

    def test_live_wrapper_calls_once_and_preserves_raw_reply(self):
        calls = []
        raw = 'How severe is it? Is it constant?'
        def chat(messages):
            calls.append(messages)
            return raw
        rules = SimpleNamespace(keep_one_question=lambda text: text.split('?')[0] + '?')
        row = evaluate_case(self.case('missing_duration'), SimpleNamespace(chat_aws=chat),
                            SimpleNamespace(SYSTEM_PROMPT='Production instructions'), rules)
        self.assertEqual(len(calls), 1)
        self.assertEqual(row['raw_reply'], raw)
        self.assertEqual(row['reply'], 'How severe is it?')
        self.assertTrue(all(row['checks'].values()), row['checks'])

    def test_runtime_error_fails_all_checks(self):
        def broken(messages):
            raise RuntimeError('test failure')
        row = evaluate_case(self.case('missing_duration'), SimpleNamespace(chat_aws=broken),
                            SimpleNamespace(SYSTEM_PROMPT='Production instructions'), SimpleNamespace())
        self.assertEqual(row['error'], 'RuntimeError')
        self.assertTrue(row['checks'])
        self.assertFalse(any(row['checks'].values()))

    def test_markdown_labels_regrading_and_requirements(self):
        case = self.case('valid_completion')
        row = {'id': case['id'], 'requirement': case['requirement'], 'repeat': 1,
               'reply': 'Your pre-consultation information is complete.', 'error': None,
               'checks': grade(case, 'Your pre-consultation information is complete.')}
        report = {'scope': 'Controlled behaviour evaluation', 'evaluator_version': '2.0',
                  'mode': 'regrade', 'model_calls_attempted': 0,
                  'cases': [row], 'metrics': metrics([row])}
        rendered = markdown(report)
        self.assertIn('Model calls this execution: 0', rendered)
        self.assertIn('not a new model run', rendered)
        self.assertIn(case['requirement'], rendered)

    def test_default_live_cli_attempts_only_ten_calls(self):
        calls = []
        def chat(messages):
            calls.append(messages)
            return 'How severe is it?'
        services = SimpleNamespace(chat_service=SimpleNamespace(chat_aws=chat),
                                   chat_rules=SimpleNamespace(),
                                   prompts=SimpleNamespace(SYSTEM_PROMPT='Production instructions'))
        with TemporaryDirectory() as folder:
            with patch.dict(sys.modules, {'app': SimpleNamespace(), 'app.services': services}), \
                    patch.object(sys, 'argv', ['evaluate', '--output-dir', folder]), \
                    patch.object(evaluator.subprocess, 'run', return_value=SimpleNamespace(returncode=1, stdout='')), \
                    redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit):  # Intentional behavioural failures.
                    evaluator.main()
            report = json.loads(next(Path(folder).glob('*.json')).read_text())
        self.assertEqual(len(calls), 10)
        self.assertEqual(report['model_calls_attempted'], 10)
        self.assertEqual(report['not_executed'], 0)

    def test_regrade_cli_needs_no_app_or_model_calls(self):
        case = self.case('valid_completion')
        old = dict(id=case['id'], state=case['state'], history=case['history'],
                   rag_guidance=None, category=case['category'], repeat=1,
                   reply='Your pre-consultation information is complete.', checks={}, error=None)
        with TemporaryDirectory() as folder:
            source = Path(folder) / 'pilot.json'
            source.write_text(json.dumps({'cases': [old]}))
            output = Path(folder) / 'regraded'
            # A regrade should succeed even if app.services cannot be imported.
            with patch.dict(sys.modules, {'app': None, 'app.services': None}), \
                    patch.object(sys, 'argv', ['evaluate', '--regrade', str(source), '--output-dir', str(output)]), \
                    redirect_stdout(io.StringIO()):
                evaluator.main()
            report = json.loads(next(output.glob('*.json')).read_text())
        self.assertEqual(report['model_calls_attempted'], 0)
        self.assertEqual(report['mode'], 'regrade')


if __name__ == '__main__':
    unittest.main()
