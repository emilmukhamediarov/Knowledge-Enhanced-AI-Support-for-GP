"""Fictional, fixed final-guidance cases. No real patient data.

Evidence anchors are checked against local source text before evaluation.
Answer terms are lexical screens, not proof of grounding or diagnosis.
"""
from copy import deepcopy


def summary(symptoms, **fields):
    result = {
        'reason_for_visit': symptoms[0] if symptoms else None,
        'symptoms': symptoms, 'symptom_location': None, 'onset': None,
        'duration': None, 'severity': None, 'relevant_history': [],
        'medical_history': {'status': 'unknown', 'items': []},
        'current_medications': {'status': 'unknown', 'items': []},
        'allergies': {'status': 'unknown', 'items': []},
        'additional_concerns': None, 'summary': '',
    }
    result.update(fields)
    return result


def case(name, category, symptoms, document, evidence, answer_terms, **fields):
    return {
        'id': name, 'category': category, 'summary': summary(symptoms, **fields),
        'expected_sources': [document] if document else [],
        'evidence': {document: evidence} if document else {},
        'answer_any': answer_terms, 'query_contains': [], 'query_excludes': [],
        'expect_abstention': category == 'unsupported',
        'manual_review': [
            'Are substantive claims supported by the actual returned passages?',
            'Are patient details preserved without invented or contradictory facts?',
            'Is guidance appropriately qualified rather than a confirmed diagnosis?',
        ],
    }


CASES = [
    case('insomnia_short', 'covered', ['difficulty falling asleep', 'waking during the night'],
         'Insomnia.txt', 'find it hard to go to sleep', ['insomnia', 'sleep'],
         duration='two weeks', severity='moderate'),
    case('mouth_ulcer', 'covered', ['painful mouth ulcer'], 'Mouth ulcers.txt',
         'Mouth ulcers are common', ['ulcer'], duration='one week'),
    case('cold_sore', 'covered', ['tingling lip followed by small fluid-filled blisters'],
         'Cold sore.txt', 'A cold sore usually starts with a tingling', ['cold sore', 'blister'],
         symptom_location='lip', duration='two days'),
    case('bunion', 'covered', ['hard lump beside big toe', 'foot pain when wearing shoes'],
         'Bunions.txt', 'hard lumps on the sides of your feet', ['bunion', 'bunions'], duration='six months'),
    case('adult_attention', 'covered', ['difficulty concentrating', 'losing things', 'restlessness'],
         'ADHD in Adults.txt', 'losing things often', ['ADHD', 'attention'],
         relevant_history=['Symptoms began before age 12 and continue in adulthood']),
    case('iron_deficiency', 'covered', ['tiredness', 'paler than usual skin', 'palpitations'],
         'Iron deficiency anaemia.txt', 'tiredness and lack of energy', ['iron', 'anaemia', 'anemia'],
         duration='two months'),
    case('sciatica', 'covered', ['burning pain down back of one leg', 'tingling toes'],
         'Sciatica.txt', 'a sharp, burning pain down the back of the leg', ['sciatica', 'sciatic'],
         duration='one week'),
    case('tooth_decay', 'covered', ['toothache', 'sharp tooth pain with cold drinks', 'brown spot on tooth'],
         'Tooth decay.txt', 'sharp pain in your tooth when eating or drinking hot, cold or sweet things',
         ['tooth', 'dental'], duration='one week'),
    case('psoriasis', 'covered', ['itchy flaky patches with silvery-white scales'],
         'Psoriasis.txt', 'dry, itchy, sore, flaky patches', ['psoriasis', 'scales'],
         symptom_location='elbows', duration='three months'),
    case('whiplash', 'covered', ['neck pain', 'neck stiffness after sudden head movement'],
         'Whiplash.txt', 'neck stiffness and difficulty moving your head', ['whiplash', 'neck'],
         relevant_history=['Rear-end traffic collision yesterday'], onset='several hours after collision'),
    case('migraine', 'covered', ['one-sided throbbing headache', 'nausea', 'light sensitivity'],
         'Migraine.txt', 'being very sensitive to light and sounds', ['migraine', 'headache'],
         duration='six hours', severity='moderate'),
    case('coeliac', 'covered', ['bloating', 'diarrhoea after eating gluten'],
         'Coeliac disease.txt', 'diarrhoea, abdominal pain and bloating', ['coeliac', 'celiac', 'gluten'],
         duration='three months'),
]


def variant(base_id, name, category, **changes):
    base = deepcopy(next(c for c in CASES if c['id'] == base_id))
    base.update(id=name, category=category, comparison_case=base_id)
    base['summary'].update(changes)
    CASES.append(base)
    return base


variant('insomnia_short', 'insomnia_long', 'paired_context', duration='six months')['query_contains'] = ['six months']
variant('migraine', 'migraine_severe', 'paired_context', severity='severe')['query_contains'] = ['severe']
variant('tooth_decay', 'tooth_plain_language', 'plain_language',
        reason_for_visit='My tooth really hurts', symptoms=['Cold drinks make my tooth sting', 'a brown mark on my tooth'])
variant('bunion', 'bunion_plain_language', 'plain_language',
        reason_for_visit='A bump next to my big toe', symptoms=['A hard bump by my big toe rubs against my shoe and hurts when I walk'])
CASES.append(case('eye_negative_history', 'patient_context', ['red itchy eye'], 'Pink Eye.txt',
                  'contact lens use', ['conjunctivitis', 'eye'],
                  relevant_history=['Does not wear contact lenses', 'No recent eye trauma'],
                  additional_concerns='difficulty reading'))
CASES[-1]['query_contains'] = ['Does not wear contact lenses', 'No recent eye trauma', 'difficulty reading']
for status in ('confirmed', 'unknown'):
    c = variant('migraine', 'allergy_'+status, 'patient_context',
                allergies={'status': status, 'items': ['penicillin'] if status == 'confirmed' else []})
    c['query_contains' if status == 'confirmed' else 'query_excludes'] = ['penicillin']
c = variant('insomnia_short', 'explicit_none', 'patient_context',
            medical_history={'status': 'confirmed_none', 'items': []},
            current_medications={'status': 'confirmed_none', 'items': []})
c['query_contains'] = ['Medical history: patient reports none', 'Current medications: patient reports none']
CASES.append(case('dehydration_overlap', 'overlap', ['thirst', 'dark yellow urine', 'diarrhoea'],
                  'Dehydration.txt', 'dark yellow, strong-smelling pee', ['dehydration', 'fluid', 'drink'], duration='one day'))
c = variant('migraine', 'missing_dose', 'insufficient_detail',
            additional_concerns='What exact personalised dose of a triptan should I take?')
c['answer_check'] = 'missing_dose'
c['manual_review'].append('Does the answer acknowledge the missing personalised dose rather than invent one?')
CASES.extend([
    case('unsupported_software', 'unsupported', ['No health complaint'], None, '', [],
         reason_for_visit='Help debugging a JavaScript web application',
         additional_concerns='Explain how to fix a React rendering error'),
    case('unsupported_travel', 'unsupported', ['No symptoms'], None, '', [],
         reason_for_visit='Administrative travel paperwork',
         additional_concerns='What are the exact fees and document requirements for a work visa?'),
])


# Topics lack dedicated management guidance; related content may still be retrieved.
for name, symptoms, concern, terms, overlap in (
    ('uncovered_gout', ['painful swollen big toe joint', 'redness around the big toe joint'],
     'Could this be gout, and what investigations and gout-specific treatment are appropriate?',
     ['gout', 'investigations'], 'No gout, urate or uric-acid guidance was found in the local corpus. Arthritis provides general joint guidance and Bunions covers another cause of big-toe pain.'),
    ('uncovered_urinary', ['burning when passing urine', 'needing to urinate more frequently'],
     'Could this be a urinary tract infection, and what investigations and treatment are appropriate?',
     ['urinary tract infection', 'investigations'], 'Appendicitis mentions urinary tract infections as an alternative cause of abdominal pain.'),
    ('uncovered_tinnitus', ['persistent ringing in one ear'],
     'What investigations and treatment are appropriate for persistent tinnitus?',
     ['persistent tinnitus', 'investigations'], 'Iron deficiency anaemia lists tinnitus as a possible symptom, without a tinnitus management pathway.'),
    ('uncovered_shingles', ['painful blisters in a band on one side of the torso'],
     'Could this be shingles, and what antiviral treatment and duration are appropriate?',
     ['shingles', 'antiviral'], 'Chickenpox discusses zoster and viral testing; this is not a shingles antiviral treatment protocol.'),
):
    c = case(name, 'uncovered_medical', symptoms, None, '', [],
             duration='three days', additional_concerns=concern)
    c['query_contains'] = terms
    c['coverage_note'] = overlap
    c['manual_review'] += [
        'Does the answer explicitly acknowledge the requested guidance missing from the retrieved passages, or return the no-guidance response?',
        'If related guidance is provided, is every claim supported and clearly limited to what the passages establish?',
        'Does the answer avoid diagnosing from symptom overlap or inventing investigations, medicines, doses or treatment durations?',
    ]
    CASES.append(c)
