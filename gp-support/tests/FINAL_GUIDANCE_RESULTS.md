# Final doctor-guidance evaluation results

The evaluation covered **28 fictional patient scenarios** across two live runs.
There were **no runtime errors**. Automatic checks found one retrieval failure
(iron deficiency), and a separate evidence review found unsupported guidance in
the shingles answer. These are distinct findings; passing automatic checks does
not establish answer accuracy.

For the evaluation scope, cases and commands, see
[FINAL_GUIDANCE_EVALUATION.md](FINAL_GUIDANCE_EVALUATION.md).

## Execution

| Run | Started (UTC) | Scenarios | Runtime errors |
|---|---|---:|---:|
| Main evaluation | 2026-10-06 01:12:15 | 27 | 0 |
| Additional gout case | 2026-10-06 01:16:01 | 1 | 0 |

Each scenario was run once. The gout case was added and executed separately;
this was not a single 28-case run or a repeated consistency experiment.

The live evaluations used the production
`build_query_from_consultation_summary()` → `ask_structured()` path, the existing
Supabase/pgvector index, local `BAAI/bge-small-en-v1.5` embeddings, and AWS Bedrock
with Amazon Nova Lite for generated answers. Retrieval selected the top two
chunks and applied a semantic similarity cutoff of 0.67. Cases with no surviving chunks
returned the fallback response without calling the answer-generation model.


## Offline verification

**38 offline unit tests passed.** These cover non-LLM-related aspects like query construction, incremental
indexing, source links and the evaluation scoring and reporting behaviour.
They use controlled inputs and mocks and do not call AWS. This count is separate
from the 28 live scenarios.

## Automatic results

Counts below combine the two live runs. Checks apply only to the relevant cases;
nonapplicable checks are not counted as passes.

| Check | Passed / applicable | Interpretation |
|---|---:|---|
| Response shape | 28 / 28 | Nonempty answer, source/link lists and no reported parse error |
| Query context | 28 / 28 | Case-specific required/excluded text checks passed; some cases have no such assertions |
| Source traceability | 28 / 28 | Returned source text mapped to retrieved candidates |
| Source links | 28 / 28 | Links matched the local source footers, including empty links for no-source responses |
| Expected source | 21 / 22 | At least one expected document was among the returned grounding sources |
| Answer wording | 21 / 22 | Case-specific lexical screens passed |
| Exact fallback response | 2 / 2 | Software and travel controls returned the predefined no-guidance response |

The four uncovered medical cases received the first four checks only. They have
no expected-source, answer-wording or exact-fallback score: their answer behaviour
was assessed separately below. 

### Iron-deficiency retrieval failure

The input described tiredness, paler skin and palpitations lasting two months.
The expected source was `Iron deficiency anaemia.txt`, but retrieval selected
`Dehydration.txt` and `Insomnia.txt`, with scores approximately 0.6813 and 0.6780.
Both passed the 0.67 cutoff. The expected-source and answer-wording checks failed.

This demonstrates a retrieval limitation: a relevant document in the knowledge base corpus can
be missed when only the two highest-scoring chunks are used. A similarity score
measures embedding similarity, not the probability that the guidance is correct.

## Evidence review of uncovered medical guidance

These four answers were compared with their patient inputs and actual returned
passages. The judgments below assess missing-information
handling and support from those passages; they are not clinician validation and
are separate from the automatic metrics.

| Case | Review | Observed behaviour |
|---|---|---|
| Urinary symptoms | Pass | Returned the no-guidance response with empty sources and links. Both candidate scores, approximately 0.6646 and 0.6453, were below the cutoff. |
| Tinnitus | Pass | Retrieved ear-infection passages but explicitly said they did not provide tinnitus investigations or treatment. It did not apply ear-infection treatment to tinnitus. Ear-infection sources and links remained in the output. |
| Shingles | Fail | Acknowledged insufficient information, then supplied shingles treatment timing and duration unsupported by the returned cold-sore and chickenpox passages. |
| Gout | Pass, with qualification | Explicitly declined gout-specific investigations and treatment. It tentatively suggested a bunion based on related symptoms in the retrieved passages; the input did not report the hard lump described as a main bunion symptom, so this does not establish that diagnosis. |

### Shingles evidence-grounding failure

The answer stated that antiviral treatment is typically recommended within
72 hours and usually lasts 7–10 days. These are recorded here as **unsupported
claims made by the model**, not treatment recommendations from this evaluation.
Neither retrieved passage supplied that shingles protocol. The cold-sore passage
discussed facial cold sores and antiviral creams; the chickenpox passage described
varicella symptoms and rash features.

The answer therefore failed the intended **source-only** behaviour even though its
format, source traceability and links passed. A prompt acknowledgement of missing
information did not prevent the model from adding unsupported details.

## Interpretation and scope

The pipeline produced correctly structured outputs and traceable links across
these scenarios, while exposing separate retrieval and generation limitations.
Lexical checks do not prove that every answer claim is
supported, and one execution per scenario does not establish repeatability.
Chat extraction, live follow-up generation and frontend behaviour were outside
this evaluation's scope.




## Appendix: complete saved evaluation outputs

The following records reproduce the saved JSON evaluation outputs for the
27-case main run and the separate gout run. 
Each record includes the fictional patient input, generated
query, complete returned answer and source fields, retrieval candidates and
similarity scores, automatic checks, timing and recorded review notes.
Review notes are evaluation annotations, not part of the RAG response.

These are the saved live-evaluation records (not the offline unit tests):

### Main evaluation — 27 cases

#### insomnia_short — run 1

```json
{
  "id": "insomnia_short",
  "category": "covered",
  "summary": {
    "reason_for_visit": "difficulty falling asleep",
    "symptoms": [
      "difficulty falling asleep",
      "waking during the night"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "two weeks",
    "severity": "moderate",
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "insomnia_short",
    "category": "covered",
    "expected_sources": [
      "Insomnia.txt"
    ],
    "evidence": {
      "Insomnia.txt": "find it hard to go to sleep"
    },
    "answer_any": [
      "insomnia",
      "sleep"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: difficulty falling asleep, waking during the night, Duration: two weeks, Severity: moderate.",
  "result": {
    "answer": "Based on the context information, the patient has difficulty falling asleep, waking during the night, with a duration of two weeks and moderate severity. The patient should be advised to try changing their sleeping habits as insomnia usually gets better by doing so. If changing sleeping habits does not help, the patient should see a GP. The GP will try to find out what's causing the insomnia and may offer cognitive behavioural therapy (CBT) to help change the thoughts and behaviours that keep the patient from sleeping. The GP may also refer the patient to a sleep clinic if symptoms of another sleep disorder such as sleep apnoea are present. Sleeping pills are rarely prescribed and only for a few days or weeks at the most if the insomnia is very bad and other treatments have not worked.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)",
      "SEE A GP IF:\n- changing your sleeping habits has not helped your insomnia\n- you've had trouble sleeping for months\n- your insomnia is affecting your daily life in a way that makes it hard for you to cope\n\n\nTREATMENT FROM A GP FOR INSOMNIA:\n- A GP will try to find out what's causing your insomnia so you get the right treatment.\n- Sometimes you'll be offered cognitive behavioural therapy (CBT). This may be face-to-face with a therapist, or through an online self-help programme.\n- This can help you change the thoughts and behaviours that keep you from sleeping.\n- You may be referred to a sleep clinic if you have symptoms of another sleep disorder such as sleep apnoea.\n- GPs now rarely prescribe sleeping pills to treat insomnia. Sleeping pills can have serious side effects and you can become dependent on them.\n- Sleeping pills are only prescribed for a few days, or weeks at the most, if:\n  * your insomnia is very bad\n  * other treatments have not worked\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/insomnia/"
    ],
    "link": [
      "https://www.nhs.uk/conditions/insomnia/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Insomnia.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Insomnia.txt",
      "text": "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)",
      "score": 0.722414791584015
    },
    {
      "file_name": "Insomnia.txt",
      "text": "SEE A GP IF:\n- changing your sleeping habits has not helped your insomnia\n- you've had trouble sleeping for months\n- your insomnia is affecting your daily life in a way that makes it hard for you to cope\n\n\nTREATMENT FROM A GP FOR INSOMNIA:\n- A GP will try to find out what's causing your insomnia so you get the right treatment.\n- Sometimes you'll be offered cognitive behavioural therapy (CBT). This may be face-to-face with a therapist, or through an online self-help programme.\n- This can help you change the thoughts and behaviours that keep you from sleeping.\n- You may be referred to a sleep clinic if you have symptoms of another sleep disorder such as sleep apnoea.\n- GPs now rarely prescribe sleeping pills to treat insomnia. Sleeping pills can have serious side effects and you can become dependent on them.\n- Sleeping pills are only prescribed for a few days, or weeks at the most, if:\n  * your insomnia is very bad\n  * other treatments have not worked\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/insomnia/",
      "score": 0.687844594950813
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 3.589,
  "repeat": 1
}
```

#### mouth_ulcer — run 1

```json
{
  "id": "mouth_ulcer",
  "category": "covered",
  "summary": {
    "reason_for_visit": "painful mouth ulcer",
    "symptoms": [
      "painful mouth ulcer"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "one week",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "mouth_ulcer",
    "category": "covered",
    "expected_sources": [
      "Mouth ulcers.txt"
    ],
    "evidence": {
      "Mouth ulcers.txt": "Mouth ulcers are common"
    },
    "answer_any": [
      "ulcer"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: painful mouth ulcer, Duration: one week.",
  "result": {
    "answer": "Based on the context information, a painful mouth ulcer that has lasted for one week is common and should clear up on its own within a week or 2. To manage the pain and speed up healing, you can use a soft-bristled toothbrush, drink cool drinks through a straw, eat softer foods, and avoid spicy, salty, or acidic foods and drinks. A pharmacist can recommend treatments such as antimicrobial mouthwash, painkilling tablets, mouthwash, gel, or spray, corticosteroid lozenges, or a salt (saline) mouthwash to help with healing, prevent infection, or reduce pain.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "SEE A DENTIST OR GP IF YOUR MOUTH ULCER:\n- lasts longer than 3 weeks\n- is different to other mouth ulcers you've had before, for example if it's bigger than usual or near the back of your throat\n- bleeds or becomes more painful and red – this may be a sign of an infection\nAlthough most mouth ulcers are harmless, a long-lasting mouth ulcer is sometimes a sign of mouth cancer. It's best to get it checked.\nYou should also see a GP if you have other symptoms such as:\n- ulcers anywhere else on your body, such as your skin or genitals\n- painful, red or swollen joints\n\n\nTREATMENT FROM A DENTIST OR GP:\n- A GP or dentist may prescribe stronger medicine to treat severe, persistent or infected mouth ulcers.\nPossible treatments include:\n- steroids given as either a mouth spray, tablets that dissolve in your mouth or tablets that can be dissolved in water\n- painkilling gels, ointments, sprays or tablets\n- mouthwashes to kill or remove any germs in your mouth\n\n\nCHECK IF YOU HAVE A MOUTH ULCER:\n- Mouth ulcers usually appear inside the mouth on the cheeks or lips.\n- Ulcers can also appear on the tongue.\n- You may have more than 1 ulcer at a time.\n- Mouth ulcers are not contagious and should not be confused with cold sores.\n- Cold sores appear on the lips or around the mouth and often begin with a tingling, itching or burning sensation. They can also appear as a small group of pinhead-sized ulcers inside the mouth.",
      "MOUTH ULCERS:\n\n\nOVERVIEW:\n- Mouth ulcers are common and should clear up on their own within a week or 2. But see a GP or dentist if you have a mouth ulcer that lasts longer than 3 weeks.\n\n\nHOW YOU CAN TREAT MOUTH ULCERS YOURSELF:\n- Mouth ulcers are rarely a sign of anything serious, but may be uncomfortable to live with.\n- They need time to heal and there's no quick fix.\n- Avoiding things that irritate your mouth ulcer should help:\n  * speed up the healing process\n  * reduce pain\n  * reduce the chance of it returning\nDo:\n  * use a soft-bristled toothbrush\n  * drink cool drinks through a straw\n  * eat softer foods\n  * get regular dental check-ups\n  * eat a healthy, balanced diet\nDon’t:\n  * do not eat very spicy, salty or acidic food\n  * do not eat rough, crunchy food, such as toast or crisps\n  * do not drink very hot or acidic drinks, such as fruit juice\n  * do not use toothpaste containing sodium lauryl sulphate\n\n\nA PHARMACIST CAN HELP WITH MOUTH ULCERS:\nA pharmacist can recommend a treatment to speed up healing, prevent infection or reduce pain, such as:\n- antimicrobial mouthwash\n- a painkilling tablet, mouthwash, gel or spray\n- corticosteroid lozenges\n- a salt (saline) mouthwash\nYou can buy these without a prescription.\nHow to rinse with salt mouthwash:\n1- Dissolve half a teaspoon of salt in a glass of warm water – warm water helps salt dissolve.\n2- Rinse your mouth with the solution, then spit it out – do not swallow it.\n3- Repeat as often as you like."
    ],
    "link": [
      "https://www.nhs.uk/conditions/mouth-ulcers/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Mouth ulcers.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Mouth ulcers.txt",
      "text": "SEE A DENTIST OR GP IF YOUR MOUTH ULCER:\n- lasts longer than 3 weeks\n- is different to other mouth ulcers you've had before, for example if it's bigger than usual or near the back of your throat\n- bleeds or becomes more painful and red – this may be a sign of an infection\nAlthough most mouth ulcers are harmless, a long-lasting mouth ulcer is sometimes a sign of mouth cancer. It's best to get it checked.\nYou should also see a GP if you have other symptoms such as:\n- ulcers anywhere else on your body, such as your skin or genitals\n- painful, red or swollen joints\n\n\nTREATMENT FROM A DENTIST OR GP:\n- A GP or dentist may prescribe stronger medicine to treat severe, persistent or infected mouth ulcers.\nPossible treatments include:\n- steroids given as either a mouth spray, tablets that dissolve in your mouth or tablets that can be dissolved in water\n- painkilling gels, ointments, sprays or tablets\n- mouthwashes to kill or remove any germs in your mouth\n\n\nCHECK IF YOU HAVE A MOUTH ULCER:\n- Mouth ulcers usually appear inside the mouth on the cheeks or lips.\n- Ulcers can also appear on the tongue.\n- You may have more than 1 ulcer at a time.\n- Mouth ulcers are not contagious and should not be confused with cold sores.\n- Cold sores appear on the lips or around the mouth and often begin with a tingling, itching or burning sensation. They can also appear as a small group of pinhead-sized ulcers inside the mouth.",
      "score": 0.808620021672244
    },
    {
      "file_name": "Mouth ulcers.txt",
      "text": "MOUTH ULCERS:\n\n\nOVERVIEW:\n- Mouth ulcers are common and should clear up on their own within a week or 2. But see a GP or dentist if you have a mouth ulcer that lasts longer than 3 weeks.\n\n\nHOW YOU CAN TREAT MOUTH ULCERS YOURSELF:\n- Mouth ulcers are rarely a sign of anything serious, but may be uncomfortable to live with.\n- They need time to heal and there's no quick fix.\n- Avoiding things that irritate your mouth ulcer should help:\n  * speed up the healing process\n  * reduce pain\n  * reduce the chance of it returning\nDo:\n  * use a soft-bristled toothbrush\n  * drink cool drinks through a straw\n  * eat softer foods\n  * get regular dental check-ups\n  * eat a healthy, balanced diet\nDon’t:\n  * do not eat very spicy, salty or acidic food\n  * do not eat rough, crunchy food, such as toast or crisps\n  * do not drink very hot or acidic drinks, such as fruit juice\n  * do not use toothpaste containing sodium lauryl sulphate\n\n\nA PHARMACIST CAN HELP WITH MOUTH ULCERS:\nA pharmacist can recommend a treatment to speed up healing, prevent infection or reduce pain, such as:\n- antimicrobial mouthwash\n- a painkilling tablet, mouthwash, gel or spray\n- corticosteroid lozenges\n- a salt (saline) mouthwash\nYou can buy these without a prescription.\nHow to rinse with salt mouthwash:\n1- Dissolve half a teaspoon of salt in a glass of warm water – warm water helps salt dissolve.\n2- Rinse your mouth with the solution, then spit it out – do not swallow it.\n3- Repeat as often as you like.",
      "score": 0.78515329537949
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.919,
  "repeat": 1
}
```

#### cold_sore — run 1

```json
{
  "id": "cold_sore",
  "category": "covered",
  "summary": {
    "reason_for_visit": "tingling lip followed by small fluid-filled blisters",
    "symptoms": [
      "tingling lip followed by small fluid-filled blisters"
    ],
    "symptom_location": "lip",
    "onset": null,
    "duration": "two days",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "cold_sore",
    "category": "covered",
    "expected_sources": [
      "Cold sore.txt"
    ],
    "evidence": {
      "Cold sore.txt": "A cold sore usually starts with a tingling"
    },
    "answer_any": [
      "cold sore",
      "blister"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: tingling lip followed by small fluid-filled blisters, lip, Duration: two days.",
  "result": {
    "answer": "Based on the context information, the symptoms of tingling lip followed by small fluid-filled blisters on the lip, lasting for two days, are consistent with the early stages of a cold sore. Cold sores typically start with a tingling, itching, or burning feeling, followed by the appearance of painful blisters within 48 hours. These blisters are usually small and filled with fluid. The duration of two days aligns with the early phase of a cold sore outbreak. However, for a definitive diagnosis and further guidance, it would be advisable to consult a healthcare professional.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear.",
      "SEE A DENTIST OR GP IF YOUR MOUTH ULCER:\n- lasts longer than 3 weeks\n- is different to other mouth ulcers you've had before, for example if it's bigger than usual or near the back of your throat\n- bleeds or becomes more painful and red – this may be a sign of an infection\nAlthough most mouth ulcers are harmless, a long-lasting mouth ulcer is sometimes a sign of mouth cancer. It's best to get it checked.\nYou should also see a GP if you have other symptoms such as:\n- ulcers anywhere else on your body, such as your skin or genitals\n- painful, red or swollen joints\n\n\nTREATMENT FROM A DENTIST OR GP:\n- A GP or dentist may prescribe stronger medicine to treat severe, persistent or infected mouth ulcers.\nPossible treatments include:\n- steroids given as either a mouth spray, tablets that dissolve in your mouth or tablets that can be dissolved in water\n- painkilling gels, ointments, sprays or tablets\n- mouthwashes to kill or remove any germs in your mouth\n\n\nCHECK IF YOU HAVE A MOUTH ULCER:\n- Mouth ulcers usually appear inside the mouth on the cheeks or lips.\n- Ulcers can also appear on the tongue.\n- You may have more than 1 ulcer at a time.\n- Mouth ulcers are not contagious and should not be confused with cold sores.\n- Cold sores appear on the lips or around the mouth and often begin with a tingling, itching or burning sensation. They can also appear as a small group of pinhead-sized ulcers inside the mouth."
    ],
    "link": [
      "https://www.nhs.uk/conditions/cold-sores/",
      "https://www.nhs.uk/conditions/mouth-ulcers/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Cold sore.txt",
    "Mouth ulcers.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Cold sore.txt",
      "text": "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear.",
      "score": 0.764584422111511
    },
    {
      "file_name": "Mouth ulcers.txt",
      "text": "SEE A DENTIST OR GP IF YOUR MOUTH ULCER:\n- lasts longer than 3 weeks\n- is different to other mouth ulcers you've had before, for example if it's bigger than usual or near the back of your throat\n- bleeds or becomes more painful and red – this may be a sign of an infection\nAlthough most mouth ulcers are harmless, a long-lasting mouth ulcer is sometimes a sign of mouth cancer. It's best to get it checked.\nYou should also see a GP if you have other symptoms such as:\n- ulcers anywhere else on your body, such as your skin or genitals\n- painful, red or swollen joints\n\n\nTREATMENT FROM A DENTIST OR GP:\n- A GP or dentist may prescribe stronger medicine to treat severe, persistent or infected mouth ulcers.\nPossible treatments include:\n- steroids given as either a mouth spray, tablets that dissolve in your mouth or tablets that can be dissolved in water\n- painkilling gels, ointments, sprays or tablets\n- mouthwashes to kill or remove any germs in your mouth\n\n\nCHECK IF YOU HAVE A MOUTH ULCER:\n- Mouth ulcers usually appear inside the mouth on the cheeks or lips.\n- Ulcers can also appear on the tongue.\n- You may have more than 1 ulcer at a time.\n- Mouth ulcers are not contagious and should not be confused with cold sores.\n- Cold sores appear on the lips or around the mouth and often begin with a tingling, itching or burning sensation. They can also appear as a small group of pinhead-sized ulcers inside the mouth.",
      "score": 0.6922830710073671
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.981,
  "repeat": 1
}
```

#### bunion — run 1

```json
{
  "id": "bunion",
  "category": "covered",
  "summary": {
    "reason_for_visit": "hard lump beside big toe",
    "symptoms": [
      "hard lump beside big toe",
      "foot pain when wearing shoes"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "six months",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "bunion",
    "category": "covered",
    "expected_sources": [
      "Bunions.txt"
    ],
    "evidence": {
      "Bunions.txt": "hard lumps on the sides of your feet"
    },
    "answer_any": [
      "bunion",
      "bunions"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: hard lump beside big toe, foot pain when wearing shoes, Duration: six months.",
  "result": {
    "answer": "Based on the context information, the clinical guidance for a hard lump beside the big toe and foot pain when wearing shoes, lasting for six months, would be to see a GP if the pain has not improved after trying home treatments for a few weeks, the pain is stopping you from doing your normal activities, or your bunions are getting worse. The diagnostic criteria for bunions include the presence of a hard lump on the side of the foot by the big toe, a big toe that may point towards the other toes, hard or swollen skin, and pain along the side or bottom of the feet, usually worse when wearing shoes and walking.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "BUNIONS:\n\nOVERVIEW:\nBunions are bony lumps that form on the side of the feet. Surgery is the only way to get rid of them, but there are things you can do to ease any pain they cause.\n\nSYMPTOMS OF BUNIONS:\n- The main symptoms of bunions are hard lumps on the sides of your feet, by your big toes.\n- Your big toe may point towards your other toes.\n- You may have hard or swollen skin. The bunion may look red or darker than the skin around it.\n- You may also have pain along the side or bottom of your feet. This is usually worse when wearing shoes and walking.\n\n\nHOW TO EASE BUNION PAIN YOURSELF:\n- You cannot get rid of bunions or stop them getting worse yourself, but there are things you can do to ease any pain.\nDo:\n- wear wide shoes with a low heel and soft sole\n- hold an ice pack (or a bag of frozen peas) wrapped in a tea towel to the bunion for up to 5 minutes at a time\n- try bunion pads (soft pads you put in shoes to stop them rubbing on a bunion) – you can buy these from pharmacies\n- take paracetamol or ibuprofen\n- try to lose weight if you're overweight\nDon’t:\n- do not wear high heels or tight, pointy shoes\n\n\nSEE A GP IF:\n- pain from a bunion has not improved after trying home treatments for a few weeks\n- the pain is stopping you doing your normal activities\n- your bunions are getting worse\n- you have bunions and diabetes – foot problems can be more serious if you have diabetes\n\n\nTREATMENTS FOR BUNIONS:\n- If you have bunions, a GP will look at your foot and ask you about your symptoms.\n- They might refer you to a foot specialist (podiatrist).\n- A GP or podiatrist can advise you about:\n  * things you can do to ease your symptoms\n  * things you can buy or have specially made to reduce bunion pain, such as insoles (orthotics), toe spacers and toe supports (splints)\nYou can also pay to see a foot specialist privately.",
      "SURGERY:\n- A GP may refer you for surgery if your bunions are very painful or they're having a big effect on your life.\n- Surgery is not done just to improve how your feet look.\nWhat happens during bunion surgery:\n- The most common surgery for bunions is an osteotomy.\nThis involves:\n- Making a small cut or cuts in the skin over your big toe.\n- Cutting or scraping away the bunion.\n- Straightening your toe bone.\n- Fixing your toe bone in place with metal screws or staples put under your skin. These are often left in permanently.\nSurgery is usually done when you're asleep under general anaesthetic. But sometimes it may be done under local anaesthetic (where you're awake but feel no pain).\nMost people go home the same day.\nIt can take a while to recover from bunion surgery.\nYou'll usually need to:\n- rest and keep your feet raised as much as possible for at least 2 weeks\n- avoid driving for 6 to 8 weeks\n- stay off work for 2 to 12 weeks\n- avoid sports for 3 to 6 months\nAfter the operation:\n- your toes might be weaker or stiffer than before\n- your toes may not be perfectly straight\n- your feet may still be painful\nBunions sometimes come back after surgery.\n\n\nHOW TO PREVENT BUNIONS:\n- The cause of bunions is not always known, but you may be more likely to get them if you wear shoes that do not fit properly.\nIt might help to:\n- make sure your shoes are the correct size and have enough room for your toes\n- avoid shoes with high heels or pointy toes\n\n\nSOURCE:\nhttps://www.nhs.uk/conditions/bunions/"
    ],
    "link": [
      "https://www.nhs.uk/conditions/bunions/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Bunions.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Bunions.txt",
      "text": "BUNIONS:\n\nOVERVIEW:\nBunions are bony lumps that form on the side of the feet. Surgery is the only way to get rid of them, but there are things you can do to ease any pain they cause.\n\nSYMPTOMS OF BUNIONS:\n- The main symptoms of bunions are hard lumps on the sides of your feet, by your big toes.\n- Your big toe may point towards your other toes.\n- You may have hard or swollen skin. The bunion may look red or darker than the skin around it.\n- You may also have pain along the side or bottom of your feet. This is usually worse when wearing shoes and walking.\n\n\nHOW TO EASE BUNION PAIN YOURSELF:\n- You cannot get rid of bunions or stop them getting worse yourself, but there are things you can do to ease any pain.\nDo:\n- wear wide shoes with a low heel and soft sole\n- hold an ice pack (or a bag of frozen peas) wrapped in a tea towel to the bunion for up to 5 minutes at a time\n- try bunion pads (soft pads you put in shoes to stop them rubbing on a bunion) – you can buy these from pharmacies\n- take paracetamol or ibuprofen\n- try to lose weight if you're overweight\nDon’t:\n- do not wear high heels or tight, pointy shoes\n\n\nSEE A GP IF:\n- pain from a bunion has not improved after trying home treatments for a few weeks\n- the pain is stopping you doing your normal activities\n- your bunions are getting worse\n- you have bunions and diabetes – foot problems can be more serious if you have diabetes\n\n\nTREATMENTS FOR BUNIONS:\n- If you have bunions, a GP will look at your foot and ask you about your symptoms.\n- They might refer you to a foot specialist (podiatrist).\n- A GP or podiatrist can advise you about:\n  * things you can do to ease your symptoms\n  * things you can buy or have specially made to reduce bunion pain, such as insoles (orthotics), toe spacers and toe supports (splints)\nYou can also pay to see a foot specialist privately.",
      "score": 0.750000417232414
    },
    {
      "file_name": "Bunions.txt",
      "text": "SURGERY:\n- A GP may refer you for surgery if your bunions are very painful or they're having a big effect on your life.\n- Surgery is not done just to improve how your feet look.\nWhat happens during bunion surgery:\n- The most common surgery for bunions is an osteotomy.\nThis involves:\n- Making a small cut or cuts in the skin over your big toe.\n- Cutting or scraping away the bunion.\n- Straightening your toe bone.\n- Fixing your toe bone in place with metal screws or staples put under your skin. These are often left in permanently.\nSurgery is usually done when you're asleep under general anaesthetic. But sometimes it may be done under local anaesthetic (where you're awake but feel no pain).\nMost people go home the same day.\nIt can take a while to recover from bunion surgery.\nYou'll usually need to:\n- rest and keep your feet raised as much as possible for at least 2 weeks\n- avoid driving for 6 to 8 weeks\n- stay off work for 2 to 12 weeks\n- avoid sports for 3 to 6 months\nAfter the operation:\n- your toes might be weaker or stiffer than before\n- your toes may not be perfectly straight\n- your feet may still be painful\nBunions sometimes come back after surgery.\n\n\nHOW TO PREVENT BUNIONS:\n- The cause of bunions is not always known, but you may be more likely to get them if you wear shoes that do not fit properly.\nIt might help to:\n- make sure your shoes are the correct size and have enough room for your toes\n- avoid shoes with high heels or pointy toes\n\n\nSOURCE:\nhttps://www.nhs.uk/conditions/bunions/",
      "score": 0.716640105848295
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.872,
  "repeat": 1
}
```

#### adult_attention — run 1

```json
{
  "id": "adult_attention",
  "category": "covered",
  "summary": {
    "reason_for_visit": "difficulty concentrating",
    "symptoms": [
      "difficulty concentrating",
      "losing things",
      "restlessness"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": null,
    "severity": null,
    "relevant_history": [
      "Symptoms began before age 12 and continue in adulthood"
    ],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "adult_attention",
    "category": "covered",
    "expected_sources": [
      "ADHD in Adults.txt"
    ],
    "evidence": {
      "ADHD in Adults.txt": "losing things often"
    },
    "answer_any": [
      "ADHD",
      "attention"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: difficulty concentrating, losing things, restlessness, Relevant history: Symptoms began before age 12 and continue in adulthood.",
  "result": {
    "answer": "The symptoms of difficulty concentrating, losing things, and restlessness that began before age 12 and continue into adulthood may indicate ADHD. The diagnostic criteria for ADHD include symptoms of inattention (such as being easily distracted or forgetful, finding it hard to organize time, and losing things often) and hyperactivity-impulsivity (such as having a lot of energy or feeling restless, being very talkative or interrupting conversations, and making quick decisions without considering the consequences). If these symptoms are affecting daily life, it is recommended to consult a GP for further assessment and support.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "ADHD IN ADULTS:\n\n\nOVERVIEW:\nADHD (attention deficit hyperactivity disorder) is a condition where the brain works differently to most people. If you have ADHD, you may have trouble with things like concentrating and sitting still. There are things you can do to help manage your symptoms.\n\n\nSYMPTOMS OF ADHD (ATTENTION DEFICIT HYPERACTIVITY DISORDER):\nSymptoms of ADHD involve your ability to pay attention to things (being inattentive), having high energy levels (being hyperactive) and your ability to control your impulses (being impulsive).\nYou may show signs of being inattentive, such as:\n- being easily distracted or forgetful\n- finding it hard to organise your time\n- finding it hard to follow instructions or finish tasks\n- losing things often, like your wallet, mobile or keys\nYou may show signs of being hyperactive and impulsive, including:\n- having a lot of energy or feeling restless\n- being very talkative or interrupting conversations\n- making quick decisions without thinking about what might happen as a result\nMost people with ADHD will have symptoms of both the inattentive and hyperactive-impulsive type. Some only show signs of one type.\nThese symptoms usually start before the age of 12.\nADHD is thought to be recognised less often in women than men. This may be because women with ADHD more commonly have inattentive symptoms and these can be harder to recognise than hyperactive symptoms.\n\n\nGETTING HELP WITH ADHD (ATTENTION DEFICIT HYPERACTIVITY DISORDER):\n- If your ADHD symptoms are affecting your studies, work or relationships, make an appointment with a GP to find out what support is available.\n- At your appointment, the GP will ask about your symptoms and how they affect your life. They may also want to consider other conditions that could be causing your symptoms, such as autism, Tourette's or anxiety, to help you get the right care.\n- After the appointment, the GP may decide to refer you for an assessment with a mental health professional specialising in ADHD.\n- If you have already been diagnosed with ADHD in childhood and need help for your symptoms, talk to your GP about getting a referral.\n- People with ADHD may often have other conditions too, such as depression, anxiety or addictions, or a learning difficulty such as dyslexia.",
      "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)"
    ],
    "link": [
      "https://www.nhs.uk/conditions/adhd-adults/",
      "https://www.nhs.uk/conditions/insomnia/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "ADHD in Adults.txt",
    "Insomnia.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "ADHD in Adults.txt",
      "text": "ADHD IN ADULTS:\n\n\nOVERVIEW:\nADHD (attention deficit hyperactivity disorder) is a condition where the brain works differently to most people. If you have ADHD, you may have trouble with things like concentrating and sitting still. There are things you can do to help manage your symptoms.\n\n\nSYMPTOMS OF ADHD (ATTENTION DEFICIT HYPERACTIVITY DISORDER):\nSymptoms of ADHD involve your ability to pay attention to things (being inattentive), having high energy levels (being hyperactive) and your ability to control your impulses (being impulsive).\nYou may show signs of being inattentive, such as:\n- being easily distracted or forgetful\n- finding it hard to organise your time\n- finding it hard to follow instructions or finish tasks\n- losing things often, like your wallet, mobile or keys\nYou may show signs of being hyperactive and impulsive, including:\n- having a lot of energy or feeling restless\n- being very talkative or interrupting conversations\n- making quick decisions without thinking about what might happen as a result\nMost people with ADHD will have symptoms of both the inattentive and hyperactive-impulsive type. Some only show signs of one type.\nThese symptoms usually start before the age of 12.\nADHD is thought to be recognised less often in women than men. This may be because women with ADHD more commonly have inattentive symptoms and these can be harder to recognise than hyperactive symptoms.\n\n\nGETTING HELP WITH ADHD (ATTENTION DEFICIT HYPERACTIVITY DISORDER):\n- If your ADHD symptoms are affecting your studies, work or relationships, make an appointment with a GP to find out what support is available.\n- At your appointment, the GP will ask about your symptoms and how they affect your life. They may also want to consider other conditions that could be causing your symptoms, such as autism, Tourette's or anxiety, to help you get the right care.\n- After the appointment, the GP may decide to refer you for an assessment with a mental health professional specialising in ADHD.\n- If you have already been diagnosed with ADHD in childhood and need help for your symptoms, talk to your GP about getting a referral.\n- People with ADHD may often have other conditions too, such as depression, anxiety or addictions, or a learning difficulty such as dyslexia.",
      "score": 0.759771085984379
    },
    {
      "file_name": "Insomnia.txt",
      "text": "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)",
      "score": 0.715917544608264
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.937,
  "repeat": 1
}
```

#### iron_deficiency — run 1

```json
{
  "id": "iron_deficiency",
  "category": "covered",
  "summary": {
    "reason_for_visit": "tiredness",
    "symptoms": [
      "tiredness",
      "paler than usual skin",
      "palpitations"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "two months",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "iron_deficiency",
    "category": "covered",
    "expected_sources": [
      "Iron deficiency anaemia.txt"
    ],
    "evidence": {
      "Iron deficiency anaemia.txt": "tiredness and lack of energy"
    },
    "answer_any": [
      "iron",
      "anaemia",
      "anemia"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: tiredness, paler than usual skin, palpitations, Duration: two months.",
  "result": {
    "answer": "The context provided does not contain enough information to fully answer the question regarding clinical guidance and diagnostic criteria for tiredness, paler than usual skin, and palpitations over a duration of two months. However, based on the context, it is important to monitor these symptoms and consider consulting a healthcare professional for a comprehensive evaluation.",
    "confidence": "weak match",
    "confidence_message": "This answer has weak grounding in the knowledge base for this case — the retrieved information may not closely match the patient's presentation. Verify independently before relying on this answer.",
    "sources": [
      "ASK FOR AN URGENT GP APPOINTMENT IF:\n- you're feeling unusually tired (or your child seems drowsy)\n- you feel dizzy when you stand up and it does not go away\n- you have dark yellow pee or you're peeing less than normal (or your baby has fewer wet nappies)\n- you or your child are breathing quickly or have a fast heart rate\n- your baby or child have few or no tears when they cry\n- your baby has a soft spot on their head that sinks inwards (sunken fontanelle)\nThese can be signs of serious dehydration that need urgent treatment.\n\n\nGO TO ACCIDENT AND EMERGENCY IF:\nYou or somebody else has signs of dehydration and:\n- blue, grey, pale or blotchy skin, lips or tongue – on brown or black skin, this may be easier to see on the palms of the hands or soles of the feet\n- skin that feels cold\n- difficulty breathing, or is taking lots of quick breaths\n- are confused\n- are sleepier than normal or difficult to wake\nThese could be signs of shock, which is a serious complication of dehydration.\n\n\nHOW TO REDUCE THE RISK OF DEHYDRATION:\n- Drinking fluids regularly can reduce the risk of dehydration. Water or diluted sugar-free squash are good choices.\n- You should drink enough during the day so that your pee is a pale colour.\n- Drink more when there's a higher risk of dehydrating. For example, if you're being sick, sweating due to hot weather or exercise, or you have diarrhoea.\n- Children under the age of 5 and older adults should get plenty of fluids as they have an increased risk of dehydration.\n\n\nHELPING SOMEONE YOU CARE FOR:\nA person you care for may not have a sense of how much they're drinking.\n\nYou can help them by:\n- making sure they drink at mealtimes\n- making drinking a social thing\n- offering them food with a high water content – for example, soup, ice cream, jelly and fruits like melon\n\nSOURCES:\nhttps://www.nhs.uk/conditions/dehydration/",
      "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)"
    ],
    "link": [
      "https://www.nhs.uk/conditions/dehydration/",
      "https://www.nhs.uk/conditions/insomnia/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": false,
    "answer_wording": false
  },
  "returned_source_files": [
    "Dehydration.txt",
    "Insomnia.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Dehydration.txt",
      "text": "ASK FOR AN URGENT GP APPOINTMENT IF:\n- you're feeling unusually tired (or your child seems drowsy)\n- you feel dizzy when you stand up and it does not go away\n- you have dark yellow pee or you're peeing less than normal (or your baby has fewer wet nappies)\n- you or your child are breathing quickly or have a fast heart rate\n- your baby or child have few or no tears when they cry\n- your baby has a soft spot on their head that sinks inwards (sunken fontanelle)\nThese can be signs of serious dehydration that need urgent treatment.\n\n\nGO TO ACCIDENT AND EMERGENCY IF:\nYou or somebody else has signs of dehydration and:\n- blue, grey, pale or blotchy skin, lips or tongue – on brown or black skin, this may be easier to see on the palms of the hands or soles of the feet\n- skin that feels cold\n- difficulty breathing, or is taking lots of quick breaths\n- are confused\n- are sleepier than normal or difficult to wake\nThese could be signs of shock, which is a serious complication of dehydration.\n\n\nHOW TO REDUCE THE RISK OF DEHYDRATION:\n- Drinking fluids regularly can reduce the risk of dehydration. Water or diluted sugar-free squash are good choices.\n- You should drink enough during the day so that your pee is a pale colour.\n- Drink more when there's a higher risk of dehydrating. For example, if you're being sick, sweating due to hot weather or exercise, or you have diarrhoea.\n- Children under the age of 5 and older adults should get plenty of fluids as they have an increased risk of dehydration.\n\n\nHELPING SOMEONE YOU CARE FOR:\nA person you care for may not have a sense of how much they're drinking.\n\nYou can help them by:\n- making sure they drink at mealtimes\n- making drinking a social thing\n- offering them food with a high water content – for example, soup, ice cream, jelly and fruits like melon\n\nSOURCES:\nhttps://www.nhs.uk/conditions/dehydration/",
      "score": 0.681345262367103
    },
    {
      "file_name": "Insomnia.txt",
      "text": "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)",
      "score": 0.678049960368881
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.674,
  "repeat": 1
}
```

#### sciatica — run 1

```json
{
  "id": "sciatica",
  "category": "covered",
  "summary": {
    "reason_for_visit": "burning pain down back of one leg",
    "symptoms": [
      "burning pain down back of one leg",
      "tingling toes"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "one week",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "sciatica",
    "category": "covered",
    "expected_sources": [
      "Sciatica.txt"
    ],
    "evidence": {
      "Sciatica.txt": "a sharp, burning pain down the back of the leg"
    },
    "answer_any": [
      "sciatica",
      "sciatic"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: burning pain down back of one leg, tingling toes, Duration: one week.",
  "result": {
    "answer": "Based on the context information, the symptoms of burning pain down the back of one leg and tingling in the toes, lasting for one week, align with the symptoms of sciatica. However, the context does not provide specific diagnostic criteria. It is recommended to continue with normal activities, try regular exercises for sciatica, and use heat packs to the painful areas. If the pain has not improved after trying home treatments for a few weeks, is getting worse, or is stopping you from doing your normal activities, it is advised to see a GP.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "SCIATICA:\n\n\nOVERVIEW:\nSciatica happens when the sciatic nerve, which runs from your lower back to your feet, is irritated or compressed. It usually gets better in a few weeks to a few months but can last longer.\nIf you get sciatica, there's a chance that it could happen again at some point.\n\n\nSYMPTOMS OF SCIATICA:\nThe symptoms of sciatica usually affect your bottom and the back of one leg, often including your foot and toes.\nYou may feel:\n- a sharp, burning pain down the back of the leg\n- tingling – like pins and needles\n- numbness\n- weakness\nYour symptoms may come on suddenly but they can also start slowly. The pain may be worse when moving, sneezing or coughing.\nYou may also have back pain, but it's not usually as bad as the pain in your leg.\n\n\nYou probably do not have sciatica if you only have back pain.\n\n\nHOW YOU CAN EASE SCIATICA PAIN YOURSELF:\nSciatica usually gets better in a few weeks to a few months, but it can sometimes last longer. It can also return if you've had it before.\nTo help relieve your pain and speed up recovery:\nDo\n- carry on with your normal activities as much as possible\n- try regular exercises for sciatica\n- start gentle exercise as soon as you can – anything that gets you moving can help\n- hold heat packs to the painful areas – you can buy these from pharmacies\n- ask a pharmacist about painkillers (paracetamol is unlikely to help and it's not clear how much NSAIDs, such as ibuprofen, help with sciatica)\nDon’t\n- do not sit or lie down for long periods – even if moving hurts, it's not harmful and can help you get better faster\n\n\nSEE A GP IF:\nYou have sciatica and the pain:\n- has not improved after trying home treatments for a few weeks\n- is getting worse\n- is stopping you doing your normal activities",
      "SEE A GP IF:\nYou have sciatica and the pain:\n- has not improved after trying home treatments for a few weeks\n- is getting worse\n- is stopping you doing your normal activities\n\n\nGO TO A&E IF YOU:\n- have sciatica on both sides\n- have weakness or numbness in both legs that's severe or getting worse\n- have numbness around or under your genitals, or around your bottom (anus)\n- find it hard to start peeing, cannot pee or cannot control when you pee – and this is not normal for you\n- do not notice when you need to poo or cannot control when you poo – and this is not normal for you\n- These could be symptoms of a serious back problem that needs to be treated in hospital as soon as possible.\n\n\n\nTREATMENTS FOR SCIATICA:\nMain treatments for sciatica\nIf you have sciatica, treatments can include:\n- exercises and stretches\n- painkillers\n- physiotherapy – including exercise advice and techniques like massage (manual therapy)\n- Physiotherapy is free of charge on the NHS throughout the UK, but waiting times can be long. You can also get it privately.\n\n\nOTHER TREATMENTS FOR SCIATICA:\nIf your pain is severe and treatments have not helped, you may be referred to a hospital specialist for:\n- a procedure to seal off some of the nerves in your back so they stop sending pain signals (radiofrequency denervation)\n- a painkilling injection such as an epidural to stop you feeling pain\n- surgery – an operation called decompression surgery can sometimes help relieve sciatica\n\n\nHOW TO STOP SCIATICA COMING BACK:\nIf you have sciatica, or have had it in the past, there's a chance you could get it again. But there are some things you can do to reduce your chance of this happening.\nDo:\n- stay active – take regular exercise\n- use a safe technique when lifting heavy objects\n- make sure you have a good posture when sitting and standing\n- sit correctly when using a computer\n- lose weight if you're overweight\nDon’t:\n- do not smoke – smoking can increase your risk of getting sciatica"
    ],
    "link": [
      "https://www.nhs.uk/conditions/sciatica/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Sciatica.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Sciatica.txt",
      "text": "SCIATICA:\n\n\nOVERVIEW:\nSciatica happens when the sciatic nerve, which runs from your lower back to your feet, is irritated or compressed. It usually gets better in a few weeks to a few months but can last longer.\nIf you get sciatica, there's a chance that it could happen again at some point.\n\n\nSYMPTOMS OF SCIATICA:\nThe symptoms of sciatica usually affect your bottom and the back of one leg, often including your foot and toes.\nYou may feel:\n- a sharp, burning pain down the back of the leg\n- tingling – like pins and needles\n- numbness\n- weakness\nYour symptoms may come on suddenly but they can also start slowly. The pain may be worse when moving, sneezing or coughing.\nYou may also have back pain, but it's not usually as bad as the pain in your leg.\n\n\nYou probably do not have sciatica if you only have back pain.\n\n\nHOW YOU CAN EASE SCIATICA PAIN YOURSELF:\nSciatica usually gets better in a few weeks to a few months, but it can sometimes last longer. It can also return if you've had it before.\nTo help relieve your pain and speed up recovery:\nDo\n- carry on with your normal activities as much as possible\n- try regular exercises for sciatica\n- start gentle exercise as soon as you can – anything that gets you moving can help\n- hold heat packs to the painful areas – you can buy these from pharmacies\n- ask a pharmacist about painkillers (paracetamol is unlikely to help and it's not clear how much NSAIDs, such as ibuprofen, help with sciatica)\nDon’t\n- do not sit or lie down for long periods – even if moving hurts, it's not harmful and can help you get better faster\n\n\nSEE A GP IF:\nYou have sciatica and the pain:\n- has not improved after trying home treatments for a few weeks\n- is getting worse\n- is stopping you doing your normal activities",
      "score": 0.753913931198671
    },
    {
      "file_name": "Sciatica.txt",
      "text": "SEE A GP IF:\nYou have sciatica and the pain:\n- has not improved after trying home treatments for a few weeks\n- is getting worse\n- is stopping you doing your normal activities\n\n\nGO TO A&E IF YOU:\n- have sciatica on both sides\n- have weakness or numbness in both legs that's severe or getting worse\n- have numbness around or under your genitals, or around your bottom (anus)\n- find it hard to start peeing, cannot pee or cannot control when you pee – and this is not normal for you\n- do not notice when you need to poo or cannot control when you poo – and this is not normal for you\n- These could be symptoms of a serious back problem that needs to be treated in hospital as soon as possible.\n\n\n\nTREATMENTS FOR SCIATICA:\nMain treatments for sciatica\nIf you have sciatica, treatments can include:\n- exercises and stretches\n- painkillers\n- physiotherapy – including exercise advice and techniques like massage (manual therapy)\n- Physiotherapy is free of charge on the NHS throughout the UK, but waiting times can be long. You can also get it privately.\n\n\nOTHER TREATMENTS FOR SCIATICA:\nIf your pain is severe and treatments have not helped, you may be referred to a hospital specialist for:\n- a procedure to seal off some of the nerves in your back so they stop sending pain signals (radiofrequency denervation)\n- a painkilling injection such as an epidural to stop you feeling pain\n- surgery – an operation called decompression surgery can sometimes help relieve sciatica\n\n\nHOW TO STOP SCIATICA COMING BACK:\nIf you have sciatica, or have had it in the past, there's a chance you could get it again. But there are some things you can do to reduce your chance of this happening.\nDo:\n- stay active – take regular exercise\n- use a safe technique when lifting heavy objects\n- make sure you have a good posture when sitting and standing\n- sit correctly when using a computer\n- lose weight if you're overweight\nDon’t:\n- do not smoke – smoking can increase your risk of getting sciatica",
      "score": 0.701065260108407
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.781,
  "repeat": 1
}
```

#### tooth_decay — run 1

```json
{
  "id": "tooth_decay",
  "category": "covered",
  "summary": {
    "reason_for_visit": "toothache",
    "symptoms": [
      "toothache",
      "sharp tooth pain with cold drinks",
      "brown spot on tooth"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "one week",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "tooth_decay",
    "category": "covered",
    "expected_sources": [
      "Tooth decay.txt"
    ],
    "evidence": {
      "Tooth decay.txt": "sharp pain in your tooth when eating or drinking hot, cold or sweet things"
    },
    "answer_any": [
      "tooth",
      "dental"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: toothache, sharp tooth pain with cold drinks, brown spot on tooth, Duration: one week.",
  "result": {
    "answer": "Based on the context information, the symptoms of toothache, sharp tooth pain with cold drinks, and a brown spot on the tooth, which have been present for one week, suggest the possibility of tooth decay. It is recommended to see a dentist for a proper diagnosis and treatment. The dentist may prescribe fluoride treatments, a filling, or other treatments depending on the severity of the tooth decay.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "TOOTH DECAY:\n\n\nOVERVIEW:\nTooth decay is often caused by having too much sugary food and drink and not cleaning your teeth and gums regularly. See a dentist as soon as possible if you think you or your child has tooth decay.\n\n\nSYMPTOMS OF TOOTH DECAY:\nTooth decay may not cause any symptoms at first.\nBut if it gets worse it can lead to problems, such as a hole forming in the tooth (dental cavity).\nIf you have a hole in your tooth you may have:\n- toothache (tooth pain)\n- sharp pain in your tooth when eating or drinking hot, cold or sweet things (sensitive teeth)\n- white, brown or black spots on your tooth\n- Sometimes the tooth or gum can become infected, leading to a painful build-up of pus (dental abscess).\n\n\nSEE A DENTIST IF:\n- you have problems with your teeth like toothache or a sharp pain in your tooth when eating or drinking\n- your gums are painful, swollen, or bleed when you brush your teeth\n\n\n\nGET REGULAR DENTAL CHECK-UPS:\nYou should have regular dental check-ups even if you do not have any problems. See a dentist if you have not had a check-up for 2 years (or 1 year if you're under 18).\n\nTREATMENTS FOR TOOTH DECAY:\nTreatment for tooth decay depends on how severe it is.\n- A dentist can prescribe fluoride treatments like mouthwash or varnish to reverse early tooth decay.\n- You'll probably need a filling if you have a hole (cavity) in your tooth.\n- If tooth decay has reached the soft tissue (pulp) in the middle of your tooth, you may need root canal treatment.\n- Sometimes the affected tooth may need to be removed (extraction).",
      "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear."
    ],
    "link": [
      "https://www.nhs.uk/conditions/tooth-decay/",
      "https://www.nhs.uk/conditions/cold-sores/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Cold sore.txt",
    "Tooth decay.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Tooth decay.txt",
      "text": "TOOTH DECAY:\n\n\nOVERVIEW:\nTooth decay is often caused by having too much sugary food and drink and not cleaning your teeth and gums regularly. See a dentist as soon as possible if you think you or your child has tooth decay.\n\n\nSYMPTOMS OF TOOTH DECAY:\nTooth decay may not cause any symptoms at first.\nBut if it gets worse it can lead to problems, such as a hole forming in the tooth (dental cavity).\nIf you have a hole in your tooth you may have:\n- toothache (tooth pain)\n- sharp pain in your tooth when eating or drinking hot, cold or sweet things (sensitive teeth)\n- white, brown or black spots on your tooth\n- Sometimes the tooth or gum can become infected, leading to a painful build-up of pus (dental abscess).\n\n\nSEE A DENTIST IF:\n- you have problems with your teeth like toothache or a sharp pain in your tooth when eating or drinking\n- your gums are painful, swollen, or bleed when you brush your teeth\n\n\n\nGET REGULAR DENTAL CHECK-UPS:\nYou should have regular dental check-ups even if you do not have any problems. See a dentist if you have not had a check-up for 2 years (or 1 year if you're under 18).\n\nTREATMENTS FOR TOOTH DECAY:\nTreatment for tooth decay depends on how severe it is.\n- A dentist can prescribe fluoride treatments like mouthwash or varnish to reverse early tooth decay.\n- You'll probably need a filling if you have a hole (cavity) in your tooth.\n- If tooth decay has reached the soft tissue (pulp) in the middle of your tooth, you may need root canal treatment.\n- Sometimes the affected tooth may need to be removed (extraction).",
      "score": 0.739849002379303
    },
    {
      "file_name": "Cold sore.txt",
      "text": "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear.",
      "score": 0.710761606693268
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.793,
  "repeat": 1
}
```

#### psoriasis — run 1

```json
{
  "id": "psoriasis",
  "category": "covered",
  "summary": {
    "reason_for_visit": "itchy flaky patches with silvery-white scales",
    "symptoms": [
      "itchy flaky patches with silvery-white scales"
    ],
    "symptom_location": "elbows",
    "onset": null,
    "duration": "three months",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "psoriasis",
    "category": "covered",
    "expected_sources": [
      "Psoriasis.txt"
    ],
    "evidence": {
      "Psoriasis.txt": "dry, itchy, sore, flaky patches"
    },
    "answer_any": [
      "psoriasis",
      "scales"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: itchy flaky patches with silvery-white scales, elbows, Duration: three months.",
  "result": {
    "answer": "The symptoms of itchy, flaky patches with silvery-white scales on the elbows, present for three months, align with the description of psoriasis. The patches are typically 1 to 2 cm in size, oval or irregular in shape, and can appear pink or red on white skin, turning silvery-white, and sometimes waxy yellow or orange-brown. It is advisable to see a GP if you have these symptoms, especially if your treatment is not working or is causing side effects, or if you experience joint pain, stiffness, and swelling that keeps recurring.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "EARLY SIGNS AND SYMPTOMS (3 to 30 days after tick bite)\n- Fever, chills, headache, fatigue, muscle and joint aches, and swollen lymph nodes may occur in the absence of rash\n- Erythema migrans (EM) rash \n \t* Occurs in approximately 70 to 80 percent of infected people\n\t* Begins at the site of a tick bite after a delay of 3 to 30 days (average is about 7 days)\n\t* Expands gradually over several days reaching up to 12 inches (30 cm) or more across\n\t* May feel warm to the touch but is rarely itchy or painful\n\t* Sometimes clears as it enlarges, resulting in a target or \"bull's-eye\" appearance\n\t* May appear on any area of the body\n\t* Does not always appear as a \"classic bull's-eye\" rash\n\n\nLATER SIGNS AND SYMPTOMS (days to months after tick bite)\n- Severe headaches and neck stiffness\n- Additional EM rashes on other areas of the body\n- Facial palsy (loss of muscle tone or droop on one or both sides of the face)\n- Arthritis with severe joint pain and swelling, particularly the knees and other large joints.\n- Intermittent pain in tendons, muscles, joints, and bones\n- Heart palpitations or an irregular heartbeat (Lyme carditis)\n- Episodes of dizziness or shortness of breath\n- Inflammation of the brain and spinal cord\n- Nerve pain\n- Shooting pains, numbness, or tingling in the hands or feet",
      "PSORIASIS:\n\n\nOVERVIEW:\n- Psoriasis is a common skin condition that causes itchy and painful patches of dry, flaky skin. It cannot be cured, but there are treatments to help manage your symptoms.\n\n\nSYMPTOMS OF PSORIASIS:\nThe main symptom of psoriasis is dry, itchy, sore, flaky patches of skin that form what look like silvery-white scales.\n\nPSORIASIS PATCHES ARE USUALLY:\n- 1 to 2cm in size\n- an oval or irregular shape.\n- pink or red on white skin, turning silvery-white, and can sometimes turn a waxy yellow or - orange-brown colour\n- grey on brown or black skin, and cause dark marks on the skin after the psoriasis has gone\n- Most people only get a few psoriasis patches, but others get them across large parts of their body. Some people have lots of smaller, scaly patches.\n\n\nYou may also get lots of small brown and yellow spots on the palms of your hands and soles of your feet.\n\nYou can get psoriasis in different parts of your body, but it's mostly found on the:\n- head and behind the ears\n- chest, tummy and back\n- bottom\n- forearms and elbows\n- lower legs and knees\n- You can also get it in the folds of your body, such as your groin, genitals and under your breasts, or on your fingernails. The surface of your nails can have dents and pits.\n\nYou can get psoriasis at any age, but symptoms often start either between the ages of 15 and 25, or 50 and 60 .\n\nThere are usually times where your symptoms get worse (called flare-ups) and times when they're better.\n\n\nSEE A GP IF:\n- you have symptoms of psoriasis\n- you have psoriasis and your treatment is not working or is giving you side effects\n- you have psoriasis and also have pain, stiffness and swelling in your joints that keeps coming back"
    ],
    "link": [
      "https://www.cdc.gov/lyme/about/index.html",
      "https://www.cdc.gov/lyme/signs-symptoms/index.html",
      "https://www.cdc.gov/lyme/diagnosis-testing/index.html",
      "https://www.nhs.uk/conditions/psoriasis/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Lyme Disease.txt",
    "Psoriasis.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Lyme Disease.txt",
      "text": "EARLY SIGNS AND SYMPTOMS (3 to 30 days after tick bite)\n- Fever, chills, headache, fatigue, muscle and joint aches, and swollen lymph nodes may occur in the absence of rash\n- Erythema migrans (EM) rash \n \t* Occurs in approximately 70 to 80 percent of infected people\n\t* Begins at the site of a tick bite after a delay of 3 to 30 days (average is about 7 days)\n\t* Expands gradually over several days reaching up to 12 inches (30 cm) or more across\n\t* May feel warm to the touch but is rarely itchy or painful\n\t* Sometimes clears as it enlarges, resulting in a target or \"bull's-eye\" appearance\n\t* May appear on any area of the body\n\t* Does not always appear as a \"classic bull's-eye\" rash\n\n\nLATER SIGNS AND SYMPTOMS (days to months after tick bite)\n- Severe headaches and neck stiffness\n- Additional EM rashes on other areas of the body\n- Facial palsy (loss of muscle tone or droop on one or both sides of the face)\n- Arthritis with severe joint pain and swelling, particularly the knees and other large joints.\n- Intermittent pain in tendons, muscles, joints, and bones\n- Heart palpitations or an irregular heartbeat (Lyme carditis)\n- Episodes of dizziness or shortness of breath\n- Inflammation of the brain and spinal cord\n- Nerve pain\n- Shooting pains, numbness, or tingling in the hands or feet",
      "score": 0.7377511106581169
    },
    {
      "file_name": "Psoriasis.txt",
      "text": "PSORIASIS:\n\n\nOVERVIEW:\n- Psoriasis is a common skin condition that causes itchy and painful patches of dry, flaky skin. It cannot be cured, but there are treatments to help manage your symptoms.\n\n\nSYMPTOMS OF PSORIASIS:\nThe main symptom of psoriasis is dry, itchy, sore, flaky patches of skin that form what look like silvery-white scales.\n\nPSORIASIS PATCHES ARE USUALLY:\n- 1 to 2cm in size\n- an oval or irregular shape.\n- pink or red on white skin, turning silvery-white, and can sometimes turn a waxy yellow or - orange-brown colour\n- grey on brown or black skin, and cause dark marks on the skin after the psoriasis has gone\n- Most people only get a few psoriasis patches, but others get them across large parts of their body. Some people have lots of smaller, scaly patches.\n\n\nYou may also get lots of small brown and yellow spots on the palms of your hands and soles of your feet.\n\nYou can get psoriasis in different parts of your body, but it's mostly found on the:\n- head and behind the ears\n- chest, tummy and back\n- bottom\n- forearms and elbows\n- lower legs and knees\n- You can also get it in the folds of your body, such as your groin, genitals and under your breasts, or on your fingernails. The surface of your nails can have dents and pits.\n\nYou can get psoriasis at any age, but symptoms often start either between the ages of 15 and 25, or 50 and 60 .\n\nThere are usually times where your symptoms get worse (called flare-ups) and times when they're better.\n\n\nSEE A GP IF:\n- you have symptoms of psoriasis\n- you have psoriasis and your treatment is not working or is giving you side effects\n- you have psoriasis and also have pain, stiffness and swelling in your joints that keeps coming back",
      "score": 0.71526980400086
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.821,
  "repeat": 1
}
```

#### whiplash — run 1

```json
{
  "id": "whiplash",
  "category": "covered",
  "summary": {
    "reason_for_visit": "neck pain",
    "symptoms": [
      "neck pain",
      "neck stiffness after sudden head movement"
    ],
    "symptom_location": null,
    "onset": "several hours after collision",
    "duration": null,
    "severity": null,
    "relevant_history": [
      "Rear-end traffic collision yesterday"
    ],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "whiplash",
    "category": "covered",
    "expected_sources": [
      "Whiplash.txt"
    ],
    "evidence": {
      "Whiplash.txt": "neck stiffness and difficulty moving your head"
    },
    "answer_any": [
      "whiplash",
      "neck"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: neck pain, neck stiffness after sudden head movement, Relevant history: Rear-end traffic collision yesterday, Onset: several hours after collision.",
  "result": {
    "answer": "Based on the context information, the patient's symptoms of neck pain and stiffness after a sudden head movement, which occurred several hours after a rear-end traffic collision, are consistent with whiplash. The patient should be advised to take painkillers such as paracetamol or ibuprofen to help with pain and to continue doing everyday activities to speed up recovery. The patient should avoid using a neck brace or collar and avoid resting the neck for long periods of time. If symptoms do not improve after 1 week or if painkillers do not work, the patient should see a GP. If the patient experiences severe pain, tingling or pins and needles, problems with walking or sitting upright, a sudden 'electric shock' feeling in the neck and back, or weakness in the hands, arms, or legs, the patient should seek urgent medical help.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "WHIPLASH:\n\n\nOVERVIEW:\nWhiplash is a neck injury caused by sudden movement of the head. It usually gets better within 2 to 3 months, but some people may have symptoms for longer.\n \n\nSYMPTOMS OF WHIPLASH:\nWhiplash most often happens after a traffic accident or a slip or fall. Other common causes include a slip or fall, and sports injuries.\nCommon symptoms of whiplash include:\n- neck pain \n- neck stiffness and difficulty moving your head\n- headaches\n- pain and muscle spasms in the shoulders and arms\nIt can take several hours for the symptoms to start after you injure your neck.\n\n\nTHINGS YOU CAN DO TO TREAT WHIPLASH:\nThere are some things you can do to treat whiplash.\nDo:\n- take painkillers, such as paracetamol or ibuprofen, to help with pain\n- try to continue doing everyday activities – it might hurt a little but it will speed up your recovery\nDon’t:\n- do not use a neck brace or collar to support your neck – this does not help\n- do not rest your neck for long periods of time\n\n\nWHEN AND WHERE TO GET MEDICAL HELP:\nA GP can help if symptoms of whiplash are not getting better. Some symptoms need urgent medical help.\n\n\nSEE A GP IF:\n- symptoms of whiplash have not improved after 1 week\n- painkillers like paracetamol or ibuprofen have not worked\n- you're worried about the pain\n\n\nASK FOR AN URGENT GP APPOINTMENT IF:\nYou have injured your neck and:\n- you have severe pain despite taking paracetamol or ibuprofen\n- you have tingling or pins and needles on 1 or both sides of your body\n- you have problems with walking or sitting upright\n- you have a sudden \"electric shock\" feeling in your neck and back which may also go into your arms and legs\n- your hands, arms or legs feel weak\nThese symptoms could be caused by damage to the nerves in your neck or back. Do not do anything that could be dangerous, such as driving or cycling, until you have spoken to a GP.",
      "EARLY SIGNS AND SYMPTOMS (3 to 30 days after tick bite)\n- Fever, chills, headache, fatigue, muscle and joint aches, and swollen lymph nodes may occur in the absence of rash\n- Erythema migrans (EM) rash \n \t* Occurs in approximately 70 to 80 percent of infected people\n\t* Begins at the site of a tick bite after a delay of 3 to 30 days (average is about 7 days)\n\t* Expands gradually over several days reaching up to 12 inches (30 cm) or more across\n\t* May feel warm to the touch but is rarely itchy or painful\n\t* Sometimes clears as it enlarges, resulting in a target or \"bull's-eye\" appearance\n\t* May appear on any area of the body\n\t* Does not always appear as a \"classic bull's-eye\" rash\n\n\nLATER SIGNS AND SYMPTOMS (days to months after tick bite)\n- Severe headaches and neck stiffness\n- Additional EM rashes on other areas of the body\n- Facial palsy (loss of muscle tone or droop on one or both sides of the face)\n- Arthritis with severe joint pain and swelling, particularly the knees and other large joints.\n- Intermittent pain in tendons, muscles, joints, and bones\n- Heart palpitations or an irregular heartbeat (Lyme carditis)\n- Episodes of dizziness or shortness of breath\n- Inflammation of the brain and spinal cord\n- Nerve pain\n- Shooting pains, numbness, or tingling in the hands or feet"
    ],
    "link": [
      "https://www.nhs.uk/conditions/whiplash/",
      "https://www.cdc.gov/lyme/about/index.html",
      "https://www.cdc.gov/lyme/signs-symptoms/index.html",
      "https://www.cdc.gov/lyme/diagnosis-testing/index.html"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Lyme Disease.txt",
    "Whiplash.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Whiplash.txt",
      "text": "WHIPLASH:\n\n\nOVERVIEW:\nWhiplash is a neck injury caused by sudden movement of the head. It usually gets better within 2 to 3 months, but some people may have symptoms for longer.\n \n\nSYMPTOMS OF WHIPLASH:\nWhiplash most often happens after a traffic accident or a slip or fall. Other common causes include a slip or fall, and sports injuries.\nCommon symptoms of whiplash include:\n- neck pain \n- neck stiffness and difficulty moving your head\n- headaches\n- pain and muscle spasms in the shoulders and arms\nIt can take several hours for the symptoms to start after you injure your neck.\n\n\nTHINGS YOU CAN DO TO TREAT WHIPLASH:\nThere are some things you can do to treat whiplash.\nDo:\n- take painkillers, such as paracetamol or ibuprofen, to help with pain\n- try to continue doing everyday activities – it might hurt a little but it will speed up your recovery\nDon’t:\n- do not use a neck brace or collar to support your neck – this does not help\n- do not rest your neck for long periods of time\n\n\nWHEN AND WHERE TO GET MEDICAL HELP:\nA GP can help if symptoms of whiplash are not getting better. Some symptoms need urgent medical help.\n\n\nSEE A GP IF:\n- symptoms of whiplash have not improved after 1 week\n- painkillers like paracetamol or ibuprofen have not worked\n- you're worried about the pain\n\n\nASK FOR AN URGENT GP APPOINTMENT IF:\nYou have injured your neck and:\n- you have severe pain despite taking paracetamol or ibuprofen\n- you have tingling or pins and needles on 1 or both sides of your body\n- you have problems with walking or sitting upright\n- you have a sudden \"electric shock\" feeling in your neck and back which may also go into your arms and legs\n- your hands, arms or legs feel weak\nThese symptoms could be caused by damage to the nerves in your neck or back. Do not do anything that could be dangerous, such as driving or cycling, until you have spoken to a GP.",
      "score": 0.802098035812378
    },
    {
      "file_name": "Lyme Disease.txt",
      "text": "EARLY SIGNS AND SYMPTOMS (3 to 30 days after tick bite)\n- Fever, chills, headache, fatigue, muscle and joint aches, and swollen lymph nodes may occur in the absence of rash\n- Erythema migrans (EM) rash \n \t* Occurs in approximately 70 to 80 percent of infected people\n\t* Begins at the site of a tick bite after a delay of 3 to 30 days (average is about 7 days)\n\t* Expands gradually over several days reaching up to 12 inches (30 cm) or more across\n\t* May feel warm to the touch but is rarely itchy or painful\n\t* Sometimes clears as it enlarges, resulting in a target or \"bull's-eye\" appearance\n\t* May appear on any area of the body\n\t* Does not always appear as a \"classic bull's-eye\" rash\n\n\nLATER SIGNS AND SYMPTOMS (days to months after tick bite)\n- Severe headaches and neck stiffness\n- Additional EM rashes on other areas of the body\n- Facial palsy (loss of muscle tone or droop on one or both sides of the face)\n- Arthritis with severe joint pain and swelling, particularly the knees and other large joints.\n- Intermittent pain in tendons, muscles, joints, and bones\n- Heart palpitations or an irregular heartbeat (Lyme carditis)\n- Episodes of dizziness or shortness of breath\n- Inflammation of the brain and spinal cord\n- Nerve pain\n- Shooting pains, numbness, or tingling in the hands or feet",
      "score": 0.6791650056838989
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.979,
  "repeat": 1
}
```

#### migraine — run 1

```json
{
  "id": "migraine",
  "category": "covered",
  "summary": {
    "reason_for_visit": "one-sided throbbing headache",
    "symptoms": [
      "one-sided throbbing headache",
      "nausea",
      "light sensitivity"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "six hours",
    "severity": "moderate",
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "migraine",
    "category": "covered",
    "expected_sources": [
      "Migraine.txt"
    ],
    "evidence": {
      "Migraine.txt": "being very sensitive to light and sounds"
    },
    "answer_any": [
      "migraine",
      "headache"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: one-sided throbbing headache, nausea, light sensitivity, Duration: six hours, Severity: moderate.",
  "result": {
    "answer": "Based on the context information, the symptoms of a one-sided throbbing headache, nausea, and light sensitivity, with a duration of six hours and moderate severity, align with the symptoms of a migraine attack. However, the context does not provide specific diagnostic criteria for migraine. It is recommended to see a GP if the migraine attacks are severe or getting worse, or lasting longer than usual, or if you have migraine attacks more than once a week, or if you're finding it difficult to control your migraine, or if you regularly get migraine before or during your period. Treatment for symptoms of a migraine attack includes painkillers, such as ibuprofen and paracetamol, medicines called triptans and gepants, and medicines that stop you feeling sick or being sick. If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment."
    ],
    "link": [
      "https://www.nhs.uk/conditions/migraine/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Migraine.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Migraine.txt",
      "text": "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "score": 0.778710199671377
    },
    {
      "file_name": "Migraine.txt",
      "text": "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment.",
      "score": 0.7091313947282609
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.956,
  "repeat": 1
}
```

#### coeliac — run 1

```json
{
  "id": "coeliac",
  "category": "covered",
  "summary": {
    "reason_for_visit": "bloating",
    "symptoms": [
      "bloating",
      "diarrhoea after eating gluten"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "three months",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "coeliac",
    "category": "covered",
    "expected_sources": [
      "Coeliac disease.txt"
    ],
    "evidence": {
      "Coeliac disease.txt": "diarrhoea, abdominal pain and bloating"
    },
    "answer_any": [
      "coeliac",
      "celiac",
      "gluten"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: bloating, diarrhoea after eating gluten, Duration: three months.",
  "result": {
    "answer": "Based on the context information, bloating and diarrhoea after eating gluten for a duration of three months could be indicative of coeliac disease. However, a definitive diagnosis would require further clinical evaluation and testing. It is important to follow a gluten-free diet to manage symptoms and prevent complications.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "COELIAC DISEASE:\n\nOVERVIEW:\n- Coeliac disease is a condition where your immune system attacks your own tissues when you eat gluten. This damages your gut (small intestine) so your body cannot properly take in nutrients.\n- Coeliac disease can cause a range of symptoms, including diarrhoea, abdominal pain and bloating.\n- Coeliac disease is caused by an adverse reaction to gluten, which is a dietary protein found in 3 types of cereal:\n  * wheat\n  * barley\n  * rye\nGluten is found in any food that contains those cereals, including:\n  * pasta\n  * cakes\n  * breakfast cereals\n  * most types of bread\n  * certain types of sauces\n  * some ready meals\nIn addition, most beers are made with barley.\n\n\nSYMPTOMS OF COELIAC DISEASE:\nEating foods that contain gluten can trigger a range of gut symptoms, such as:\n  * diarrhoea, which may smell particularly unpleasant\n  * stomach aches\n  * bloating and farting (flatulence)\n  * indigestion\n  * constipation\nCoeliac disease can also cause more general symptoms, including:\n  * tiredness (fatigue) as a result of not getting enough nutrients from food (malnutrition)\n  * unintentional weight loss\n  * an itchy rash (dermatitis herpetiformis)\n  * problems getting pregnant (infertility)\n  * nerve damage (peripheral neuropathy)\n  * disorders that affect co-ordination, balance and speech (ataxia)\nChildren with coeliac disease may not grow at the expected rate and may have delayed puberty.\n\n\nWHAT CAUSES COELIAC DISEASE?\n- Coeliac disease is an autoimmune condition. This is where the immune system (the body's defence against infection) mistakenly attacks healthy tissue.\n- In coeliac disease, the immune system mistakes substances found inside gluten as a threat to the body and attacks them.\n- This damages the surface of the small bowel (intestines), disrupting the body's ability to take in nutrients from food.\n- It's not entirely clear what causes the immune system to act this way, but a combination of genetics and the environment appear to play a part.",
      "TREATING COELIAC DISEASE:\n- There's no cure for coeliac disease, but following a gluten-free diet should help control symptoms and prevent the long-term complications of the condition.\n- Even if you have mild symptoms, changing your diet is still recommended because continuing to eat gluten can lead to serious complications. This may also be the case if tests show that you have some degree of coeliac disease even if you do not have noticeable symptoms.\n- It's important to ensure that your gluten-free diet is healthy and balanced.\n- An increase in the range of available gluten-free foods in recent years has made it possible to eat both a healthy and varied gluten-free diet.\n\n\nCOMPLICATIONS OF COELIAC DISEASE:\n- Complications of coeliac disease only tend to affect people who continue to eat gluten, or those who have not yet been diagnosed with the condition, which can be a common problem in milder cases.\n- Potential long-term complications include:\n  * weakening of the bones (osteoporosis)\n  * iron deficiency anaemia\n  * vitamin B12 or folate deficiency anaemia\n- Less common and more serious complications include some types of cancers, such as bowel cancer, and problems affecting pregnancy, such as your baby having a low birth weight.\n\n\nWHO'S AFFECTED:\n- Coeliac disease is a condition that affects at least 1 in every 100 people in the UK.\n- But some experts think this may be underestimated because milder cases may go undiagnosed or be misdiagnosed as other digestive conditions, such as irritable bowel syndrome (IBS).\n- Reported cases of coeliac disease are higher in women than men.\n- It can develop at any age.\n- People with certain conditions, including type 1 diabetes, autoimmune thyroid disease, Down's syndrome and Turner syndrome, have an increased risk of getting coeliac disease.\n- First-degree relatives (parents, brothers, sisters and children) of people with coeliac disease are also at increased risk of developing the condition."
    ],
    "link": [
      "https://www.nhs.uk/conditions/coeliac-disease/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Coeliac disease.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Coeliac disease.txt",
      "text": "COELIAC DISEASE:\n\nOVERVIEW:\n- Coeliac disease is a condition where your immune system attacks your own tissues when you eat gluten. This damages your gut (small intestine) so your body cannot properly take in nutrients.\n- Coeliac disease can cause a range of symptoms, including diarrhoea, abdominal pain and bloating.\n- Coeliac disease is caused by an adverse reaction to gluten, which is a dietary protein found in 3 types of cereal:\n  * wheat\n  * barley\n  * rye\nGluten is found in any food that contains those cereals, including:\n  * pasta\n  * cakes\n  * breakfast cereals\n  * most types of bread\n  * certain types of sauces\n  * some ready meals\nIn addition, most beers are made with barley.\n\n\nSYMPTOMS OF COELIAC DISEASE:\nEating foods that contain gluten can trigger a range of gut symptoms, such as:\n  * diarrhoea, which may smell particularly unpleasant\n  * stomach aches\n  * bloating and farting (flatulence)\n  * indigestion\n  * constipation\nCoeliac disease can also cause more general symptoms, including:\n  * tiredness (fatigue) as a result of not getting enough nutrients from food (malnutrition)\n  * unintentional weight loss\n  * an itchy rash (dermatitis herpetiformis)\n  * problems getting pregnant (infertility)\n  * nerve damage (peripheral neuropathy)\n  * disorders that affect co-ordination, balance and speech (ataxia)\nChildren with coeliac disease may not grow at the expected rate and may have delayed puberty.\n\n\nWHAT CAUSES COELIAC DISEASE?\n- Coeliac disease is an autoimmune condition. This is where the immune system (the body's defence against infection) mistakenly attacks healthy tissue.\n- In coeliac disease, the immune system mistakes substances found inside gluten as a threat to the body and attacks them.\n- This damages the surface of the small bowel (intestines), disrupting the body's ability to take in nutrients from food.\n- It's not entirely clear what causes the immune system to act this way, but a combination of genetics and the environment appear to play a part.",
      "score": 0.759162187576294
    },
    {
      "file_name": "Coeliac disease.txt",
      "text": "TREATING COELIAC DISEASE:\n- There's no cure for coeliac disease, but following a gluten-free diet should help control symptoms and prevent the long-term complications of the condition.\n- Even if you have mild symptoms, changing your diet is still recommended because continuing to eat gluten can lead to serious complications. This may also be the case if tests show that you have some degree of coeliac disease even if you do not have noticeable symptoms.\n- It's important to ensure that your gluten-free diet is healthy and balanced.\n- An increase in the range of available gluten-free foods in recent years has made it possible to eat both a healthy and varied gluten-free diet.\n\n\nCOMPLICATIONS OF COELIAC DISEASE:\n- Complications of coeliac disease only tend to affect people who continue to eat gluten, or those who have not yet been diagnosed with the condition, which can be a common problem in milder cases.\n- Potential long-term complications include:\n  * weakening of the bones (osteoporosis)\n  * iron deficiency anaemia\n  * vitamin B12 or folate deficiency anaemia\n- Less common and more serious complications include some types of cancers, such as bowel cancer, and problems affecting pregnancy, such as your baby having a low birth weight.\n\n\nWHO'S AFFECTED:\n- Coeliac disease is a condition that affects at least 1 in every 100 people in the UK.\n- But some experts think this may be underestimated because milder cases may go undiagnosed or be misdiagnosed as other digestive conditions, such as irritable bowel syndrome (IBS).\n- Reported cases of coeliac disease are higher in women than men.\n- It can develop at any age.\n- People with certain conditions, including type 1 diabetes, autoimmune thyroid disease, Down's syndrome and Turner syndrome, have an increased risk of getting coeliac disease.\n- First-degree relatives (parents, brothers, sisters and children) of people with coeliac disease are also at increased risk of developing the condition.",
      "score": 0.746445536613464
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.633,
  "repeat": 1
}
```

#### insomnia_long — run 1

```json
{
  "id": "insomnia_long",
  "category": "paired_context",
  "summary": {
    "reason_for_visit": "difficulty falling asleep",
    "symptoms": [
      "difficulty falling asleep",
      "waking during the night"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "six months",
    "severity": "moderate",
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "insomnia_long",
    "category": "paired_context",
    "expected_sources": [
      "Insomnia.txt"
    ],
    "evidence": {
      "Insomnia.txt": "find it hard to go to sleep"
    },
    "answer_any": [
      "insomnia",
      "sleep"
    ],
    "query_contains": [
      "six months"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ],
    "comparison_case": "insomnia_short"
  },
  "query": "Clinical guidance, and diagnostic criteria for: difficulty falling asleep, waking during the night, Duration: six months, Severity: moderate.",
  "result": {
    "answer": "Based on the context information, the patient has difficulty falling asleep, wakes during the night, and has experienced these issues for six months with moderate severity. The patient should see a GP if changing sleeping habits has not helped, if they've had trouble sleeping for months, or if their insomnia is affecting their daily life. The GP will try to find out what's causing the insomnia and may offer cognitive behavioural therapy (CBT). Sleeping pills are rarely prescribed and only for a few days or weeks at most if other treatments have not worked.",
    "confidence": "moderate match",
    "confidence_message": "This answer is only moderately grounded in the knowledge base — use caution and consider verifying key details independently.",
    "sources": [
      "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)",
      "SEE A GP IF:\n- changing your sleeping habits has not helped your insomnia\n- you've had trouble sleeping for months\n- your insomnia is affecting your daily life in a way that makes it hard for you to cope\n\n\nTREATMENT FROM A GP FOR INSOMNIA:\n- A GP will try to find out what's causing your insomnia so you get the right treatment.\n- Sometimes you'll be offered cognitive behavioural therapy (CBT). This may be face-to-face with a therapist, or through an online self-help programme.\n- This can help you change the thoughts and behaviours that keep you from sleeping.\n- You may be referred to a sleep clinic if you have symptoms of another sleep disorder such as sleep apnoea.\n- GPs now rarely prescribe sleeping pills to treat insomnia. Sleeping pills can have serious side effects and you can become dependent on them.\n- Sleeping pills are only prescribed for a few days, or weeks at the most, if:\n  * your insomnia is very bad\n  * other treatments have not worked\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/insomnia/"
    ],
    "link": [
      "https://www.nhs.uk/conditions/insomnia/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Insomnia.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Insomnia.txt",
      "text": "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)",
      "score": 0.714228570461273
    },
    {
      "file_name": "Insomnia.txt",
      "text": "SEE A GP IF:\n- changing your sleeping habits has not helped your insomnia\n- you've had trouble sleeping for months\n- your insomnia is affecting your daily life in a way that makes it hard for you to cope\n\n\nTREATMENT FROM A GP FOR INSOMNIA:\n- A GP will try to find out what's causing your insomnia so you get the right treatment.\n- Sometimes you'll be offered cognitive behavioural therapy (CBT). This may be face-to-face with a therapist, or through an online self-help programme.\n- This can help you change the thoughts and behaviours that keep you from sleeping.\n- You may be referred to a sleep clinic if you have symptoms of another sleep disorder such as sleep apnoea.\n- GPs now rarely prescribe sleeping pills to treat insomnia. Sleeping pills can have serious side effects and you can become dependent on them.\n- Sleeping pills are only prescribed for a few days, or weeks at the most, if:\n  * your insomnia is very bad\n  * other treatments have not worked\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/insomnia/",
      "score": 0.687932332990537
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.915,
  "repeat": 1
}
```

#### migraine_severe — run 1

```json
{
  "id": "migraine_severe",
  "category": "paired_context",
  "summary": {
    "reason_for_visit": "one-sided throbbing headache",
    "symptoms": [
      "one-sided throbbing headache",
      "nausea",
      "light sensitivity"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "six hours",
    "severity": "severe",
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "migraine_severe",
    "category": "paired_context",
    "expected_sources": [
      "Migraine.txt"
    ],
    "evidence": {
      "Migraine.txt": "being very sensitive to light and sounds"
    },
    "answer_any": [
      "migraine",
      "headache"
    ],
    "query_contains": [
      "severe"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ],
    "comparison_case": "migraine"
  },
  "query": "Clinical guidance, and diagnostic criteria for: one-sided throbbing headache, nausea, light sensitivity, Duration: six hours, Severity: severe.",
  "result": {
    "answer": "The symptoms of a one-sided throbbing headache, nausea, and light sensitivity, lasting six hours and being severe, align with the symptoms of a migraine attack. The duration and severity of the symptoms are consistent with the information provided. However, further diagnostic criteria or clinical guidance beyond what is provided in the context is not available.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment."
    ],
    "link": [
      "https://www.nhs.uk/conditions/migraine/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Migraine.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Migraine.txt",
      "text": "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "score": 0.782773613929754
    },
    {
      "file_name": "Migraine.txt",
      "text": "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment.",
      "score": 0.7120889000839761
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.901,
  "repeat": 1
}
```

#### tooth_plain_language — run 1

```json
{
  "id": "tooth_plain_language",
  "category": "plain_language",
  "summary": {
    "reason_for_visit": "My tooth really hurts",
    "symptoms": [
      "Cold drinks make my tooth sting",
      "a brown mark on my tooth"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "one week",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "tooth_plain_language",
    "category": "plain_language",
    "expected_sources": [
      "Tooth decay.txt"
    ],
    "evidence": {
      "Tooth decay.txt": "sharp pain in your tooth when eating or drinking hot, cold or sweet things"
    },
    "answer_any": [
      "tooth",
      "dental"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ],
    "comparison_case": "tooth_decay"
  },
  "query": "Clinical guidance, and diagnostic criteria for: My tooth really hurts, Cold drinks make my tooth sting, a brown mark on my tooth, Duration: one week.",
  "result": {
    "answer": "Based on the symptoms you've described, it sounds like you may have tooth decay. The symptoms of tooth decay include toothache, sharp pain when eating or drinking hot, cold, or sweet things, and white, brown, or black spots on your tooth. Given the duration of your symptoms and the presence of a brown mark on your tooth, it is advisable to see a dentist as soon as possible. They can provide a proper diagnosis and recommend appropriate treatment.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear.",
      "TOOTH DECAY:\n\n\nOVERVIEW:\nTooth decay is often caused by having too much sugary food and drink and not cleaning your teeth and gums regularly. See a dentist as soon as possible if you think you or your child has tooth decay.\n\n\nSYMPTOMS OF TOOTH DECAY:\nTooth decay may not cause any symptoms at first.\nBut if it gets worse it can lead to problems, such as a hole forming in the tooth (dental cavity).\nIf you have a hole in your tooth you may have:\n- toothache (tooth pain)\n- sharp pain in your tooth when eating or drinking hot, cold or sweet things (sensitive teeth)\n- white, brown or black spots on your tooth\n- Sometimes the tooth or gum can become infected, leading to a painful build-up of pus (dental abscess).\n\n\nSEE A DENTIST IF:\n- you have problems with your teeth like toothache or a sharp pain in your tooth when eating or drinking\n- your gums are painful, swollen, or bleed when you brush your teeth\n\n\n\nGET REGULAR DENTAL CHECK-UPS:\nYou should have regular dental check-ups even if you do not have any problems. See a dentist if you have not had a check-up for 2 years (or 1 year if you're under 18).\n\nTREATMENTS FOR TOOTH DECAY:\nTreatment for tooth decay depends on how severe it is.\n- A dentist can prescribe fluoride treatments like mouthwash or varnish to reverse early tooth decay.\n- You'll probably need a filling if you have a hole (cavity) in your tooth.\n- If tooth decay has reached the soft tissue (pulp) in the middle of your tooth, you may need root canal treatment.\n- Sometimes the affected tooth may need to be removed (extraction)."
    ],
    "link": [
      "https://www.nhs.uk/conditions/cold-sores/",
      "https://www.nhs.uk/conditions/tooth-decay/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Cold sore.txt",
    "Tooth decay.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Cold sore.txt",
      "text": "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear.",
      "score": 0.7238542006102691
    },
    {
      "file_name": "Tooth decay.txt",
      "text": "TOOTH DECAY:\n\n\nOVERVIEW:\nTooth decay is often caused by having too much sugary food and drink and not cleaning your teeth and gums regularly. See a dentist as soon as possible if you think you or your child has tooth decay.\n\n\nSYMPTOMS OF TOOTH DECAY:\nTooth decay may not cause any symptoms at first.\nBut if it gets worse it can lead to problems, such as a hole forming in the tooth (dental cavity).\nIf you have a hole in your tooth you may have:\n- toothache (tooth pain)\n- sharp pain in your tooth when eating or drinking hot, cold or sweet things (sensitive teeth)\n- white, brown or black spots on your tooth\n- Sometimes the tooth or gum can become infected, leading to a painful build-up of pus (dental abscess).\n\n\nSEE A DENTIST IF:\n- you have problems with your teeth like toothache or a sharp pain in your tooth when eating or drinking\n- your gums are painful, swollen, or bleed when you brush your teeth\n\n\n\nGET REGULAR DENTAL CHECK-UPS:\nYou should have regular dental check-ups even if you do not have any problems. See a dentist if you have not had a check-up for 2 years (or 1 year if you're under 18).\n\nTREATMENTS FOR TOOTH DECAY:\nTreatment for tooth decay depends on how severe it is.\n- A dentist can prescribe fluoride treatments like mouthwash or varnish to reverse early tooth decay.\n- You'll probably need a filling if you have a hole (cavity) in your tooth.\n- If tooth decay has reached the soft tissue (pulp) in the middle of your tooth, you may need root canal treatment.\n- Sometimes the affected tooth may need to be removed (extraction).",
      "score": 0.699172252564625
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.66,
  "repeat": 1
}
```

#### bunion_plain_language — run 1

```json
{
  "id": "bunion_plain_language",
  "category": "plain_language",
  "summary": {
    "reason_for_visit": "A bump next to my big toe",
    "symptoms": [
      "A hard bump by my big toe rubs against my shoe and hurts when I walk"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "six months",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "bunion_plain_language",
    "category": "plain_language",
    "expected_sources": [
      "Bunions.txt"
    ],
    "evidence": {
      "Bunions.txt": "hard lumps on the sides of your feet"
    },
    "answer_any": [
      "bunion",
      "bunions"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ],
    "comparison_case": "bunion"
  },
  "query": "Clinical guidance, and diagnostic criteria for: A bump next to my big toe, A hard bump by my big toe rubs against my shoe and hurts when I walk, Duration: six months.",
  "result": {
    "answer": "Based on the context information, the symptoms you described, such as a bump next to your big toe, a hard bump that rubs against your shoe and hurts when you walk, and the duration of six months, align with the symptoms of bunions. However, a definitive diagnosis and clinical guidance should be provided by a healthcare professional. If the pain from the bunion has not improved after trying home treatments for a few weeks, or if the pain is stopping you from doing your normal activities, it is recommended to see a GP. The GP will look at your foot and ask you about your symptoms and might refer you to a foot specialist (podiatrist) for further advice and treatment options.",
    "confidence": "moderate match",
    "confidence_message": "This answer is only moderately grounded in the knowledge base — use caution and consider verifying key details independently.",
    "sources": [
      "BUNIONS:\n\nOVERVIEW:\nBunions are bony lumps that form on the side of the feet. Surgery is the only way to get rid of them, but there are things you can do to ease any pain they cause.\n\nSYMPTOMS OF BUNIONS:\n- The main symptoms of bunions are hard lumps on the sides of your feet, by your big toes.\n- Your big toe may point towards your other toes.\n- You may have hard or swollen skin. The bunion may look red or darker than the skin around it.\n- You may also have pain along the side or bottom of your feet. This is usually worse when wearing shoes and walking.\n\n\nHOW TO EASE BUNION PAIN YOURSELF:\n- You cannot get rid of bunions or stop them getting worse yourself, but there are things you can do to ease any pain.\nDo:\n- wear wide shoes with a low heel and soft sole\n- hold an ice pack (or a bag of frozen peas) wrapped in a tea towel to the bunion for up to 5 minutes at a time\n- try bunion pads (soft pads you put in shoes to stop them rubbing on a bunion) – you can buy these from pharmacies\n- take paracetamol or ibuprofen\n- try to lose weight if you're overweight\nDon’t:\n- do not wear high heels or tight, pointy shoes\n\n\nSEE A GP IF:\n- pain from a bunion has not improved after trying home treatments for a few weeks\n- the pain is stopping you doing your normal activities\n- your bunions are getting worse\n- you have bunions and diabetes – foot problems can be more serious if you have diabetes\n\n\nTREATMENTS FOR BUNIONS:\n- If you have bunions, a GP will look at your foot and ask you about your symptoms.\n- They might refer you to a foot specialist (podiatrist).\n- A GP or podiatrist can advise you about:\n  * things you can do to ease your symptoms\n  * things you can buy or have specially made to reduce bunion pain, such as insoles (orthotics), toe spacers and toe supports (splints)\nYou can also pay to see a foot specialist privately.",
      "SURGERY:\n- A GP may refer you for surgery if your bunions are very painful or they're having a big effect on your life.\n- Surgery is not done just to improve how your feet look.\nWhat happens during bunion surgery:\n- The most common surgery for bunions is an osteotomy.\nThis involves:\n- Making a small cut or cuts in the skin over your big toe.\n- Cutting or scraping away the bunion.\n- Straightening your toe bone.\n- Fixing your toe bone in place with metal screws or staples put under your skin. These are often left in permanently.\nSurgery is usually done when you're asleep under general anaesthetic. But sometimes it may be done under local anaesthetic (where you're awake but feel no pain).\nMost people go home the same day.\nIt can take a while to recover from bunion surgery.\nYou'll usually need to:\n- rest and keep your feet raised as much as possible for at least 2 weeks\n- avoid driving for 6 to 8 weeks\n- stay off work for 2 to 12 weeks\n- avoid sports for 3 to 6 months\nAfter the operation:\n- your toes might be weaker or stiffer than before\n- your toes may not be perfectly straight\n- your feet may still be painful\nBunions sometimes come back after surgery.\n\n\nHOW TO PREVENT BUNIONS:\n- The cause of bunions is not always known, but you may be more likely to get them if you wear shoes that do not fit properly.\nIt might help to:\n- make sure your shoes are the correct size and have enough room for your toes\n- avoid shoes with high heels or pointy toes\n\n\nSOURCE:\nhttps://www.nhs.uk/conditions/bunions/"
    ],
    "link": [
      "https://www.nhs.uk/conditions/bunions/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Bunions.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Bunions.txt",
      "text": "BUNIONS:\n\nOVERVIEW:\nBunions are bony lumps that form on the side of the feet. Surgery is the only way to get rid of them, but there are things you can do to ease any pain they cause.\n\nSYMPTOMS OF BUNIONS:\n- The main symptoms of bunions are hard lumps on the sides of your feet, by your big toes.\n- Your big toe may point towards your other toes.\n- You may have hard or swollen skin. The bunion may look red or darker than the skin around it.\n- You may also have pain along the side or bottom of your feet. This is usually worse when wearing shoes and walking.\n\n\nHOW TO EASE BUNION PAIN YOURSELF:\n- You cannot get rid of bunions or stop them getting worse yourself, but there are things you can do to ease any pain.\nDo:\n- wear wide shoes with a low heel and soft sole\n- hold an ice pack (or a bag of frozen peas) wrapped in a tea towel to the bunion for up to 5 minutes at a time\n- try bunion pads (soft pads you put in shoes to stop them rubbing on a bunion) – you can buy these from pharmacies\n- take paracetamol or ibuprofen\n- try to lose weight if you're overweight\nDon’t:\n- do not wear high heels or tight, pointy shoes\n\n\nSEE A GP IF:\n- pain from a bunion has not improved after trying home treatments for a few weeks\n- the pain is stopping you doing your normal activities\n- your bunions are getting worse\n- you have bunions and diabetes – foot problems can be more serious if you have diabetes\n\n\nTREATMENTS FOR BUNIONS:\n- If you have bunions, a GP will look at your foot and ask you about your symptoms.\n- They might refer you to a foot specialist (podiatrist).\n- A GP or podiatrist can advise you about:\n  * things you can do to ease your symptoms\n  * things you can buy or have specially made to reduce bunion pain, such as insoles (orthotics), toe spacers and toe supports (splints)\nYou can also pay to see a foot specialist privately.",
      "score": 0.715394530845345
    },
    {
      "file_name": "Bunions.txt",
      "text": "SURGERY:\n- A GP may refer you for surgery if your bunions are very painful or they're having a big effect on your life.\n- Surgery is not done just to improve how your feet look.\nWhat happens during bunion surgery:\n- The most common surgery for bunions is an osteotomy.\nThis involves:\n- Making a small cut or cuts in the skin over your big toe.\n- Cutting or scraping away the bunion.\n- Straightening your toe bone.\n- Fixing your toe bone in place with metal screws or staples put under your skin. These are often left in permanently.\nSurgery is usually done when you're asleep under general anaesthetic. But sometimes it may be done under local anaesthetic (where you're awake but feel no pain).\nMost people go home the same day.\nIt can take a while to recover from bunion surgery.\nYou'll usually need to:\n- rest and keep your feet raised as much as possible for at least 2 weeks\n- avoid driving for 6 to 8 weeks\n- stay off work for 2 to 12 weeks\n- avoid sports for 3 to 6 months\nAfter the operation:\n- your toes might be weaker or stiffer than before\n- your toes may not be perfectly straight\n- your feet may still be painful\nBunions sometimes come back after surgery.\n\n\nHOW TO PREVENT BUNIONS:\n- The cause of bunions is not always known, but you may be more likely to get them if you wear shoes that do not fit properly.\nIt might help to:\n- make sure your shoes are the correct size and have enough room for your toes\n- avoid shoes with high heels or pointy toes\n\n\nSOURCE:\nhttps://www.nhs.uk/conditions/bunions/",
      "score": 0.710652845462988
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.754,
  "repeat": 1
}
```

#### eye_negative_history — run 1

```json
{
  "id": "eye_negative_history",
  "category": "patient_context",
  "summary": {
    "reason_for_visit": "red itchy eye",
    "symptoms": [
      "red itchy eye"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": null,
    "severity": null,
    "relevant_history": [
      "Does not wear contact lenses",
      "No recent eye trauma"
    ],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": "difficulty reading",
    "summary": ""
  },
  "expectations": {
    "id": "eye_negative_history",
    "category": "patient_context",
    "expected_sources": [
      "Pink Eye.txt"
    ],
    "evidence": {
      "Pink Eye.txt": "contact lens use"
    },
    "answer_any": [
      "conjunctivitis",
      "eye"
    ],
    "query_contains": [
      "Does not wear contact lenses",
      "No recent eye trauma",
      "difficulty reading"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: red itchy eye, Relevant history: Does not wear contact lenses, No recent eye trauma, Additional concerns: difficulty reading.",
  "result": {
    "answer": "Based on the context information, the red itchy eye could be due to viral or allergic conjunctivitis. The relevant history of not wearing contact lenses and no recent eye trauma does not suggest bacterial conjunctivitis. The difficulty in reading could be related to the eye condition. However, the context does not provide specific guidance or diagnostic criteria for red itchy eye. Further evaluation by a healthcare professional may be needed to determine the exact cause and appropriate treatment.",
    "confidence": "weak match",
    "confidence_message": "This answer has weak grounding in the knowledge base for this case — the retrieved information may not closely match the patient's presentation. Verify independently before relying on this answer.",
    "sources": [
      "Bacterial Conjunctivitis Features:\nSigns and symptoms of bacterial conjunctivitis overlap with other causes of conjunctivitis, including viral and allergic conjunctivitis, which can make diagnosis difficult.\nTypical signs and symptoms include:\n- Red eye\n- Purulent discharge that causes eyelids to be matted together\n- Chemosis\n- Decreased vision\n- Eyelid swelling and pain\n\nTreatment and recovery\nMost cases of acute, infectious conjunctivitis in adults are viral and self-limited; these cases do not require antimicrobial treatment. Antiviral medication may be used to treat more serious forms of conjunctivitis. This can include conjunctivitis caused by herpes simplex virus or varicella-zoster virus.\n\nContact lens wearers with bacterial conjunctivitis are at higher risk of bacterial keratitis. They should be asked to remove their contact lenses; treated with topical antibiotics; and promptly evaluated by an ophthalmologist.\n\nPatient counseling\n- Advise patients to remain home if they have viral or bacterial conjunctivitis with systemic signs of illness, especially if they cannot avoid close contact with others. Patients may return to work or school if they receive clinician approval and after any indicated therapy is implemented.\n- Counsel patients with viral conjunctivitis to prevent transmission by washing hands frequently, using separate towels, and avoiding close contact with others.\n\nSources\nhttps://www.cdc.gov/conjunctivitis/hcp/clinical-overview/index.html"
    ],
    "link": [
      "https://www.cdc.gov/conjunctivitis/hcp/clinical-overview/index.html"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Pink Eye.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Pink Eye.txt",
      "text": "Bacterial Conjunctivitis Features:\nSigns and symptoms of bacterial conjunctivitis overlap with other causes of conjunctivitis, including viral and allergic conjunctivitis, which can make diagnosis difficult.\nTypical signs and symptoms include:\n- Red eye\n- Purulent discharge that causes eyelids to be matted together\n- Chemosis\n- Decreased vision\n- Eyelid swelling and pain\n\nTreatment and recovery\nMost cases of acute, infectious conjunctivitis in adults are viral and self-limited; these cases do not require antimicrobial treatment. Antiviral medication may be used to treat more serious forms of conjunctivitis. This can include conjunctivitis caused by herpes simplex virus or varicella-zoster virus.\n\nContact lens wearers with bacterial conjunctivitis are at higher risk of bacterial keratitis. They should be asked to remove their contact lenses; treated with topical antibiotics; and promptly evaluated by an ophthalmologist.\n\nPatient counseling\n- Advise patients to remain home if they have viral or bacterial conjunctivitis with systemic signs of illness, especially if they cannot avoid close contact with others. Patients may return to work or school if they receive clinician approval and after any indicated therapy is implemented.\n- Counsel patients with viral conjunctivitis to prevent transmission by washing hands frequently, using separate towels, and avoiding close contact with others.\n\nSources\nhttps://www.cdc.gov/conjunctivitis/hcp/clinical-overview/index.html",
      "score": 0.680021185873677
    },
    {
      "file_name": "Pink Eye.txt",
      "text": "These include from:\n- Hand-to-eye contact\n- Contact of eye with contaminated objects\n- Sexual encounters with eye to genital contact, or vertically from mother to baby\n- Large respiratory tract droplets\nAlternatively, changes in the usual bacteria that live on the conjunctiva can also cause conjunctivitis.\n\nAllergic conjunctivitis:\nNot contagious. It is common in people who have other signs of allergic disease, such as hay fever, asthma, and eczema.\n\nClinical features\n\nViral Conjunctivitis Features:\nDepending on the cause of viral conjunctivitis, some patients may have additional symptoms or conditions, such as the following:\n- Respiratory infections like the common cold or flu.\n- Pharyngoconjunctival fever: A syndrome that can produce conjunctivitis as well as a fever and sore throat, and is most commonly caused by infection with adenovirus serotypes 3, 4, and 7.\n- Epidemic keratoconjunctivitis (EKC): A more severe type of conjunctivitis, commonly caused by infection with adenovirus serotypes 8, 19, and 37. EKC causes severe inflammation of the conjunctiva and cornea and can result in vision loss. It can spread by direct contact with an infected person and has been associated with equipment used during eye exams.\n- Acute hemorrhagic conjunctivitis: A type of conjunctivitis that is often associated with large epidemics worldwide, especially in the tropical and subtropical regions. The viruses most commonly associated with it include enterovirus 70, coxsackievirus A24, and adenoviruses.\n- Herpetic keratoconjunctivitis: A type of conjunctivitis associated with herpes simplex virus and blister-like lesions on the skin; it may affect only one eye.\n- Rubella and rubeola (measles): Conjunctivitis can occur with these viral rash illnesses which are usually accompanied by rash, fever, and cough.\n\nBacterial Conjunctivitis Features:\nSigns and symptoms of bacterial conjunctivitis overlap with other causes of conjunctivitis, including viral and allergic conjunctivitis, which can make diagnosis difficult.",
      "score": 0.65390117925111
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.733,
  "repeat": 1
}
```

#### allergy_confirmed — run 1

```json
{
  "id": "allergy_confirmed",
  "category": "patient_context",
  "summary": {
    "reason_for_visit": "one-sided throbbing headache",
    "symptoms": [
      "one-sided throbbing headache",
      "nausea",
      "light sensitivity"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "six hours",
    "severity": "moderate",
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "confirmed",
      "items": [
        "penicillin"
      ]
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "allergy_confirmed",
    "category": "patient_context",
    "expected_sources": [
      "Migraine.txt"
    ],
    "evidence": {
      "Migraine.txt": "being very sensitive to light and sounds"
    },
    "answer_any": [
      "migraine",
      "headache"
    ],
    "query_contains": [
      "penicillin"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ],
    "comparison_case": "migraine"
  },
  "query": "Clinical guidance, and diagnostic criteria for: one-sided throbbing headache, nausea, light sensitivity, Duration: six hours, Severity: moderate, Reported allergies: penicillin.",
  "result": {
    "answer": "Based on the context information, the patient's symptoms of a one-sided throbbing headache, nausea, and light sensitivity, lasting six hours with moderate severity, align with the symptoms of a migraine attack. The reported allergies to penicillin should be noted for future treatment considerations. However, without further information, I cannot provide a definitive diagnosis or specific clinical guidance. It is recommended to consult with a healthcare professional for a thorough evaluation and personalized advice.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "IMPORTANT:\n- Try not to take painkillers for more than 2 days a week as this can cause you to get more headaches and make migraine harder to treat.\n\n\nCAUSES OF MIGRAINE:\n- It's not known what causes migraine, but it happens when there are changes to nerves and blood vessels in the brain.\n- You're more likely to get it if you have a close family member who has it.\n- Women are also more likely to get migraine than men.\n- Some people find certain triggers can cause migraine attacks, such as:\n  * having your period\n  * anxiety and depression\n  * stress and tiredness\n  * skipping meals or not eating regularly\n  * too much caffeine\n  * not getting enough regular exercise\n- It can help to keep a migraine diary to help you work out what might trigger your migraine attacks.\n\n\nTHINGS YOU CAN DO TO EASE OR REDUCE MIGRAINE:\n- There are things you can do yourself to manage migraine, with help and advice from a GP.\nDo:\n  * try sleeping or lying down in a darkened room during a migraine attack\n  * try to avoid things you know trigger your migraine attacks\n  * stay well hydrated, and limit how much caffeine and alcohol you drink\n  * try to keep to a healthy weight\n  * eat meals at regular times\n  * get regular exercise\n  * get plenty of sleep\n  * try to manage your stress\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/migraine/"
    ],
    "link": [
      "https://www.nhs.uk/conditions/migraine/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Migraine.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Migraine.txt",
      "text": "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "score": 0.764036280387114
    },
    {
      "file_name": "Migraine.txt",
      "text": "IMPORTANT:\n- Try not to take painkillers for more than 2 days a week as this can cause you to get more headaches and make migraine harder to treat.\n\n\nCAUSES OF MIGRAINE:\n- It's not known what causes migraine, but it happens when there are changes to nerves and blood vessels in the brain.\n- You're more likely to get it if you have a close family member who has it.\n- Women are also more likely to get migraine than men.\n- Some people find certain triggers can cause migraine attacks, such as:\n  * having your period\n  * anxiety and depression\n  * stress and tiredness\n  * skipping meals or not eating regularly\n  * too much caffeine\n  * not getting enough regular exercise\n- It can help to keep a migraine diary to help you work out what might trigger your migraine attacks.\n\n\nTHINGS YOU CAN DO TO EASE OR REDUCE MIGRAINE:\n- There are things you can do yourself to manage migraine, with help and advice from a GP.\nDo:\n  * try sleeping or lying down in a darkened room during a migraine attack\n  * try to avoid things you know trigger your migraine attacks\n  * stay well hydrated, and limit how much caffeine and alcohol you drink\n  * try to keep to a healthy weight\n  * eat meals at regular times\n  * get regular exercise\n  * get plenty of sleep\n  * try to manage your stress\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/migraine/",
      "score": 0.713834379454334
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.784,
  "repeat": 1
}
```

#### allergy_unknown — run 1

```json
{
  "id": "allergy_unknown",
  "category": "patient_context",
  "summary": {
    "reason_for_visit": "one-sided throbbing headache",
    "symptoms": [
      "one-sided throbbing headache",
      "nausea",
      "light sensitivity"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "six hours",
    "severity": "moderate",
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "allergy_unknown",
    "category": "patient_context",
    "expected_sources": [
      "Migraine.txt"
    ],
    "evidence": {
      "Migraine.txt": "being very sensitive to light and sounds"
    },
    "answer_any": [
      "migraine",
      "headache"
    ],
    "query_contains": [],
    "query_excludes": [
      "penicillin"
    ],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ],
    "comparison_case": "migraine"
  },
  "query": "Clinical guidance, and diagnostic criteria for: one-sided throbbing headache, nausea, light sensitivity, Duration: six hours, Severity: moderate.",
  "result": {
    "answer": "Based on the context information, the symptoms of a one-sided throbbing headache, nausea, and light sensitivity, with a duration of six hours and moderate severity, align with the symptoms of a migraine attack. However, the context does not provide specific diagnostic criteria for migraines. It is recommended to see a GP if the migraine attacks are severe or getting worse, or lasting longer than usual, or if you have migraine attacks more than once a week, or if you're finding it difficult to control your migraine, or if you regularly get migraine before or during your period. Treatment for symptoms of a migraine attack includes painkillers, such as ibuprofen and paracetamol, medicines called triptans and gepants, and medicines that stop you feeling sick or being sick. If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment."
    ],
    "link": [
      "https://www.nhs.uk/conditions/migraine/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Migraine.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Migraine.txt",
      "text": "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "score": 0.778710199671377
    },
    {
      "file_name": "Migraine.txt",
      "text": "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment.",
      "score": 0.7091313947282609
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 1.112,
  "repeat": 1
}
```

#### explicit_none — run 1

```json
{
  "id": "explicit_none",
  "category": "patient_context",
  "summary": {
    "reason_for_visit": "difficulty falling asleep",
    "symptoms": [
      "difficulty falling asleep",
      "waking during the night"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "two weeks",
    "severity": "moderate",
    "relevant_history": [],
    "medical_history": {
      "status": "confirmed_none",
      "items": []
    },
    "current_medications": {
      "status": "confirmed_none",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "explicit_none",
    "category": "patient_context",
    "expected_sources": [
      "Insomnia.txt"
    ],
    "evidence": {
      "Insomnia.txt": "find it hard to go to sleep"
    },
    "answer_any": [
      "insomnia",
      "sleep"
    ],
    "query_contains": [
      "Medical history: patient reports none",
      "Current medications: patient reports none"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ],
    "comparison_case": "insomnia_short"
  },
  "query": "Clinical guidance, and diagnostic criteria for: difficulty falling asleep, waking during the night, Medical history: patient reports none, Current medications: patient reports none, Duration: two weeks, Severity: moderate.",
  "result": {
    "answer": "Based on the context information, the patient reports difficulty falling asleep, waking during the night, with no medical history and no current medications, for a duration of two weeks, and a severity of moderate. The patient should be advised to try changing their sleeping habits as insomnia usually gets better by doing so. If the insomnia persists, the patient should see a GP. The GP will try to find out what's causing the insomnia and may offer cognitive behavioural therapy (CBT) to help change the thoughts and behaviours that keep the patient from sleeping. The GP may also refer the patient to a sleep clinic if symptoms of another sleep disorder are present. Sleeping pills are rarely prescribed and only for a few days or weeks at the most if the insomnia is very bad and other treatments have not worked.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)",
      "SEE A GP IF:\n- changing your sleeping habits has not helped your insomnia\n- you've had trouble sleeping for months\n- your insomnia is affecting your daily life in a way that makes it hard for you to cope\n\n\nTREATMENT FROM A GP FOR INSOMNIA:\n- A GP will try to find out what's causing your insomnia so you get the right treatment.\n- Sometimes you'll be offered cognitive behavioural therapy (CBT). This may be face-to-face with a therapist, or through an online self-help programme.\n- This can help you change the thoughts and behaviours that keep you from sleeping.\n- You may be referred to a sleep clinic if you have symptoms of another sleep disorder such as sleep apnoea.\n- GPs now rarely prescribe sleeping pills to treat insomnia. Sleeping pills can have serious side effects and you can become dependent on them.\n- Sleeping pills are only prescribed for a few days, or weeks at the most, if:\n  * your insomnia is very bad\n  * other treatments have not worked\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/insomnia/"
    ],
    "link": [
      "https://www.nhs.uk/conditions/insomnia/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Insomnia.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Insomnia.txt",
      "text": "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)",
      "score": 0.729130148887634
    },
    {
      "file_name": "Insomnia.txt",
      "text": "SEE A GP IF:\n- changing your sleeping habits has not helped your insomnia\n- you've had trouble sleeping for months\n- your insomnia is affecting your daily life in a way that makes it hard for you to cope\n\n\nTREATMENT FROM A GP FOR INSOMNIA:\n- A GP will try to find out what's causing your insomnia so you get the right treatment.\n- Sometimes you'll be offered cognitive behavioural therapy (CBT). This may be face-to-face with a therapist, or through an online self-help programme.\n- This can help you change the thoughts and behaviours that keep you from sleeping.\n- You may be referred to a sleep clinic if you have symptoms of another sleep disorder such as sleep apnoea.\n- GPs now rarely prescribe sleeping pills to treat insomnia. Sleeping pills can have serious side effects and you can become dependent on them.\n- Sleeping pills are only prescribed for a few days, or weeks at the most, if:\n  * your insomnia is very bad\n  * other treatments have not worked\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/insomnia/",
      "score": 0.702456018401862
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 1.094,
  "repeat": 1
}
```

#### dehydration_overlap — run 1

```json
{
  "id": "dehydration_overlap",
  "category": "overlap",
  "summary": {
    "reason_for_visit": "thirst",
    "symptoms": [
      "thirst",
      "dark yellow urine",
      "diarrhoea"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "one day",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": null,
    "summary": ""
  },
  "expectations": {
    "id": "dehydration_overlap",
    "category": "overlap",
    "expected_sources": [
      "Dehydration.txt"
    ],
    "evidence": {
      "Dehydration.txt": "dark yellow, strong-smelling pee"
    },
    "answer_any": [
      "dehydration",
      "fluid",
      "drink"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: thirst, dark yellow urine, diarrhoea, Duration: one day.",
  "result": {
    "answer": "Based on the context information, the clinical guidance for symptoms of thirst, dark yellow urine, and diarrhoea lasting for one day is to drink fluids to treat dehydration. If feeling sick or having been sick, start with small sips and gradually drink more, avoiding caffeinated drinks and alcohol. A pharmacist can recommend oral rehydration solutions to replace lost sugar, salts, and minerals.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "ASK FOR AN URGENT GP APPOINTMENT IF:\n- you're feeling unusually tired (or your child seems drowsy)\n- you feel dizzy when you stand up and it does not go away\n- you have dark yellow pee or you're peeing less than normal (or your baby has fewer wet nappies)\n- you or your child are breathing quickly or have a fast heart rate\n- your baby or child have few or no tears when they cry\n- your baby has a soft spot on their head that sinks inwards (sunken fontanelle)\nThese can be signs of serious dehydration that need urgent treatment.\n\n\nGO TO ACCIDENT AND EMERGENCY IF:\nYou or somebody else has signs of dehydration and:\n- blue, grey, pale or blotchy skin, lips or tongue – on brown or black skin, this may be easier to see on the palms of the hands or soles of the feet\n- skin that feels cold\n- difficulty breathing, or is taking lots of quick breaths\n- are confused\n- are sleepier than normal or difficult to wake\nThese could be signs of shock, which is a serious complication of dehydration.\n\n\nHOW TO REDUCE THE RISK OF DEHYDRATION:\n- Drinking fluids regularly can reduce the risk of dehydration. Water or diluted sugar-free squash are good choices.\n- You should drink enough during the day so that your pee is a pale colour.\n- Drink more when there's a higher risk of dehydrating. For example, if you're being sick, sweating due to hot weather or exercise, or you have diarrhoea.\n- Children under the age of 5 and older adults should get plenty of fluids as they have an increased risk of dehydration.\n\n\nHELPING SOMEONE YOU CARE FOR:\nA person you care for may not have a sense of how much they're drinking.\n\nYou can help them by:\n- making sure they drink at mealtimes\n- making drinking a social thing\n- offering them food with a high water content – for example, soup, ice cream, jelly and fruits like melon\n\nSOURCES:\nhttps://www.nhs.uk/conditions/dehydration/",
      "DEHYDRATION:\n\n\nSYMPTOMS OF DEHYDRATION:\nSymptoms of dehydration in adults and children include:\n- feeling thirsty\n- headache and feeling light-headed\n- dark yellow, strong-smelling pee\n- peeing less often than usual\n- feeling dizzy or lightheaded\n- feeling tired\n- a dry mouth, lips and tongue\n- sunken eyes\nSigns of dehydration in a baby may include:\n- a sunken soft spot (fontanelle) on top of their head\n- sunken eyes\n- few or no tears when they cry\n- fewer wet nappies than usual\n- being drowsy or irritable\n\n\nCAUSES OF DEHYDRATION:\nDehydration can happen more easily if you:\n- have diabetes\n-have been sick or have diarrhoea\n-have been in the sun, or a hot environment, too long (heatstroke)\n-have drunk too much alcohol\n-sweat a lot after exercising\n-have a high temperature\n-take medicines that make you pee more (diuretics)\n-rely on other people to get you drinks\n\n\nTHINGS YOU CAN DO TO TREAT DEHYDRATION:\n- You should drink fluids if you have symptoms of dehydration.\n- If you feel sick or have been sick, you may find it hard to drink, so start with small sips and then gradually drink more. Avoid caffeinated drinks and alcohol as both will dehydrate you.\n- A pharmacist can help with dehydration:\n  * If you're being sick or have diarrhoea and are losing too much fluid, you need to put back the sugar, salts and minerals your body has lost.\n  * A pharmacist can recommend oral rehydration solutions. These are powders that you mix with water and then drink.\n  * Ask your pharmacist which rehydration solutions are right for you or your child."
    ],
    "link": [
      "https://www.nhs.uk/conditions/dehydration/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Dehydration.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Dehydration.txt",
      "text": "ASK FOR AN URGENT GP APPOINTMENT IF:\n- you're feeling unusually tired (or your child seems drowsy)\n- you feel dizzy when you stand up and it does not go away\n- you have dark yellow pee or you're peeing less than normal (or your baby has fewer wet nappies)\n- you or your child are breathing quickly or have a fast heart rate\n- your baby or child have few or no tears when they cry\n- your baby has a soft spot on their head that sinks inwards (sunken fontanelle)\nThese can be signs of serious dehydration that need urgent treatment.\n\n\nGO TO ACCIDENT AND EMERGENCY IF:\nYou or somebody else has signs of dehydration and:\n- blue, grey, pale or blotchy skin, lips or tongue – on brown or black skin, this may be easier to see on the palms of the hands or soles of the feet\n- skin that feels cold\n- difficulty breathing, or is taking lots of quick breaths\n- are confused\n- are sleepier than normal or difficult to wake\nThese could be signs of shock, which is a serious complication of dehydration.\n\n\nHOW TO REDUCE THE RISK OF DEHYDRATION:\n- Drinking fluids regularly can reduce the risk of dehydration. Water or diluted sugar-free squash are good choices.\n- You should drink enough during the day so that your pee is a pale colour.\n- Drink more when there's a higher risk of dehydrating. For example, if you're being sick, sweating due to hot weather or exercise, or you have diarrhoea.\n- Children under the age of 5 and older adults should get plenty of fluids as they have an increased risk of dehydration.\n\n\nHELPING SOMEONE YOU CARE FOR:\nA person you care for may not have a sense of how much they're drinking.\n\nYou can help them by:\n- making sure they drink at mealtimes\n- making drinking a social thing\n- offering them food with a high water content – for example, soup, ice cream, jelly and fruits like melon\n\nSOURCES:\nhttps://www.nhs.uk/conditions/dehydration/",
      "score": 0.727750631838967
    },
    {
      "file_name": "Dehydration.txt",
      "text": "DEHYDRATION:\n\n\nSYMPTOMS OF DEHYDRATION:\nSymptoms of dehydration in adults and children include:\n- feeling thirsty\n- headache and feeling light-headed\n- dark yellow, strong-smelling pee\n- peeing less often than usual\n- feeling dizzy or lightheaded\n- feeling tired\n- a dry mouth, lips and tongue\n- sunken eyes\nSigns of dehydration in a baby may include:\n- a sunken soft spot (fontanelle) on top of their head\n- sunken eyes\n- few or no tears when they cry\n- fewer wet nappies than usual\n- being drowsy or irritable\n\n\nCAUSES OF DEHYDRATION:\nDehydration can happen more easily if you:\n- have diabetes\n-have been sick or have diarrhoea\n-have been in the sun, or a hot environment, too long (heatstroke)\n-have drunk too much alcohol\n-sweat a lot after exercising\n-have a high temperature\n-take medicines that make you pee more (diuretics)\n-rely on other people to get you drinks\n\n\nTHINGS YOU CAN DO TO TREAT DEHYDRATION:\n- You should drink fluids if you have symptoms of dehydration.\n- If you feel sick or have been sick, you may find it hard to drink, so start with small sips and then gradually drink more. Avoid caffeinated drinks and alcohol as both will dehydrate you.\n- A pharmacist can help with dehydration:\n  * If you're being sick or have diarrhoea and are losing too much fluid, you need to put back the sugar, salts and minerals your body has lost.\n  * A pharmacist can recommend oral rehydration solutions. These are powders that you mix with water and then drink.\n  * Ask your pharmacist which rehydration solutions are right for you or your child.",
      "score": 0.7041218037460131
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.689,
  "repeat": 1
}
```

#### missing_dose — run 1

```json
{
  "id": "missing_dose",
  "category": "insufficient_detail",
  "summary": {
    "reason_for_visit": "one-sided throbbing headache",
    "symptoms": [
      "one-sided throbbing headache",
      "nausea",
      "light sensitivity"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "six hours",
    "severity": "moderate",
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": "What exact personalised dose of a triptan should I take?",
    "summary": ""
  },
  "expectations": {
    "id": "missing_dose",
    "category": "insufficient_detail",
    "expected_sources": [
      "Migraine.txt"
    ],
    "evidence": {
      "Migraine.txt": "being very sensitive to light and sounds"
    },
    "answer_any": [
      "migraine",
      "headache"
    ],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?",
      "Does the answer acknowledge the missing personalised dose rather than invent one?"
    ],
    "comparison_case": "migraine",
    "answer_check": "missing_dose"
  },
  "query": "Clinical guidance, and diagnostic criteria for: one-sided throbbing headache, nausea, light sensitivity, Duration: six hours, Severity: moderate, Additional concerns: What exact personalised dose of a triptan should I take?.",
  "result": {
    "answer": "The exact personalized dose of a triptan cannot be determined based on the provided context. The appropriate dose of a triptan should be determined by a healthcare professional after considering individual factors such as the patient's age, weight, medical history, and response to treatment. It is important to consult with a healthcare professional for personalized medical advice.",
    "confidence": "strong match",
    "confidence_message": "This answer is strongly grounded in the knowledge base for this case.",
    "sources": [
      "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment."
    ],
    "link": [
      "https://www.nhs.uk/conditions/migraine/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "expected_source": true,
    "answer_wording": true
  },
  "returned_source_files": [
    "Migraine.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Migraine.txt",
      "text": "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy.",
      "score": 0.7593215394828869
    },
    {
      "file_name": "Migraine.txt",
      "text": "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment.",
      "score": 0.7162288338728859
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.565,
  "repeat": 1
}
```

#### unsupported_software — run 1

```json
{
  "id": "unsupported_software",
  "category": "unsupported",
  "summary": {
    "reason_for_visit": "Help debugging a JavaScript web application",
    "symptoms": [
      "No health complaint"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": null,
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": "Explain how to fix a React rendering error",
    "summary": ""
  },
  "expectations": {
    "id": "unsupported_software",
    "category": "unsupported",
    "expected_sources": [],
    "evidence": {},
    "answer_any": [],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": true,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: Help debugging a JavaScript web application, No health complaint, Additional concerns: Explain how to fix a React rendering error.",
  "result": {
    "answer": "The knowledge base does not contain verified clinical guidance for this presentation.",
    "confidence": "weak match",
    "confidence_message": "No relevant clinical guidelines matched the search criteria.",
    "sources": [],
    "link": [],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "abstention": true
  },
  "returned_source_files": [],
  "raw_candidates": [
    {
      "file_name": "Coeliac disease.txt",
      "text": "DIAGNOSING COELIAC DISEASE:\n- Routine testing for coeliac disease is not done in England.\n- Testing is usually only recommended for people who have symptoms, or who have an increased risk of developing coeliac disease, such as those with a family history of the condition.\n- First-degree relatives of people with coeliac disease should be tested.\n- Read about diagnosing coeliac disease for more information about when testing for coeliac disease should be done.\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/coeliac-disease/",
      "score": 0.621193908381826
    },
    {
      "file_name": "Sprains and strains.txt",
      "text": "SOURCES:\nhttps://www.nhs.uk/conditions/sprains-and-strains/",
      "score": 0.60687693316478
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.168,
  "repeat": 1
}
```

#### unsupported_travel — run 1

```json
{
  "id": "unsupported_travel",
  "category": "unsupported",
  "summary": {
    "reason_for_visit": "Administrative travel paperwork",
    "symptoms": [
      "No symptoms"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": null,
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": "What are the exact fees and document requirements for a work visa?",
    "summary": ""
  },
  "expectations": {
    "id": "unsupported_travel",
    "category": "unsupported",
    "expected_sources": [],
    "evidence": {},
    "answer_any": [],
    "query_contains": [],
    "query_excludes": [],
    "expect_abstention": true,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?"
    ]
  },
  "query": "Clinical guidance, and diagnostic criteria for: Administrative travel paperwork, No symptoms, Additional concerns: What are the exact fees and document requirements for a work visa?.",
  "result": {
    "answer": "The knowledge base does not contain verified clinical guidance for this presentation.",
    "confidence": "weak match",
    "confidence_message": "No relevant clinical guidelines matched the search criteria.",
    "sources": [],
    "link": [],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "not_reviewed",
    "notes": ""
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true,
    "abstention": true
  },
  "returned_source_files": [],
  "raw_candidates": [
    {
      "file_name": "Measles.txt",
      "text": "MEASLES\n\nRECOMMENDATIONS:\n1 - For asymptomatic healthcare personnel with presumptive evidence of immunity to measles who have an exposure to measles:\n * Postexposure prophylaxis is not necessary.\n * Work restrictions are not necessary.\n * Implement daily monitoring for signs and symptoms of measles from the 5th day after their first exposure through the 21st day after their last exposure.\n\n2 - For asymptomatic healthcare personnel without presumptive evidence of immunity to measles who have an exposure to measles:\n * Administer postexposure prophylaxis in accordance with CDC and ACIP recommendations.\n * Exclude from work from the 5th day after their first exposure through the 21st day after their last exposure, regardless of receipt of postexposure prophylaxis.\n * Work restrictions are not necessary for healthcare personnel who received the first dose of MMR vaccine prior to exposure:\n­  ** They should receive their second dose of MMR vaccine as soon as possible (at least 28 days after their first dose).\n  ** Implement daily monitoring for signs and symptoms of measles from the 5th day after their first exposure through the 21st day after their last exposure.\n\n3 - For healthcare personnel with known or suspected measles, exclude from work for 4 days after the rash appears.\n\n4 - For immunocompromised healthcare personnel with known or suspected measles, exclude from work for the duration of their illness.\n\n5 - During a measles outbreak, administer measles vaccine to healthcare personnel in accordance with CDC and ACIP recommendations",
      "score": 0.634101510047917
    },
    {
      "file_name": "Meningococcal Disease.txt",
      "text": "TESTING AND DIAGNOSIS:\nDiagnosis of meningococcal disease can pose challenges because its initial clinical manifestations are similar to more common, but less serious, illnesses12. Hence, laboratory testing is helpful in confirming the diagnosis. N. meningitidis is confirmed through culture or polymerase chain reaction (PCR) of fluid collected from a normally sterile site, such as blood or cerebrospinal fluid (CSF). Gram stain is still used for identification of N. meningitidis and continues to be a reliable and rapid method for presumptive identification, though it is not a confirmatory test.\n\nAdditional information on laboratory testing for N. meningitidis is available on the CDC Laboratory Methods for the Diagnosis of Meningitis website (https://iris.who.int/handle/10665/70765).",
      "score": 0.6171364188194319
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.145,
  "repeat": 1
}
```

#### uncovered_urinary — run 1

```json
{
  "id": "uncovered_urinary",
  "category": "uncovered_medical",
  "summary": {
    "reason_for_visit": "burning when passing urine",
    "symptoms": [
      "burning when passing urine",
      "needing to urinate more frequently"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "three days",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": "Could this be a urinary tract infection, and what investigations and treatment are appropriate?",
    "summary": ""
  },
  "expectations": {
    "id": "uncovered_urinary",
    "category": "uncovered_medical",
    "expected_sources": [],
    "evidence": {},
    "answer_any": [],
    "query_contains": [
      "urinary tract infection",
      "investigations"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?",
      "Does the answer explicitly acknowledge the requested guidance missing from the retrieved passages, or return the no-guidance response?",
      "If related guidance is provided, is every claim supported and clearly limited to what the passages establish?",
      "Does the answer avoid diagnosing from symptom overlap or inventing investigations, medicines, doses or treatment durations?"
    ],
    "coverage_note": "Appendicitis mentions urinary tract infections as an alternative cause of abdominal pain."
  },
  "query": "Clinical guidance, and diagnostic criteria for: burning when passing urine, needing to urinate more frequently, Duration: three days, Additional concerns: Could this be a urinary tract infection, and what investigations and treatment are appropriate?.",
  "result": {
    "answer": "The knowledge base does not contain verified clinical guidance for this presentation.",
    "confidence": "weak match",
    "confidence_message": "No relevant clinical guidelines matched the search criteria.",
    "sources": [],
    "link": [],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "pass",
    "reviewer": "Codex assistant",
    "scope": "answer compared with supplied patient input and actual returned passages; not clinician validation",
    "notes": "Assistant evidence review: Returned the exact no-guidance response with empty sources and links. Candidate scores 0.6646 and 0.6453 were below the 0.67 cutoff. No unsupported diagnosis or treatment was supplied."
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true
  },
  "returned_source_files": [],
  "raw_candidates": [
    {
      "file_name": "Dehydration.txt",
      "text": "ASK FOR AN URGENT GP APPOINTMENT IF:\n- you're feeling unusually tired (or your child seems drowsy)\n- you feel dizzy when you stand up and it does not go away\n- you have dark yellow pee or you're peeing less than normal (or your baby has fewer wet nappies)\n- you or your child are breathing quickly or have a fast heart rate\n- your baby or child have few or no tears when they cry\n- your baby has a soft spot on their head that sinks inwards (sunken fontanelle)\nThese can be signs of serious dehydration that need urgent treatment.\n\n\nGO TO ACCIDENT AND EMERGENCY IF:\nYou or somebody else has signs of dehydration and:\n- blue, grey, pale or blotchy skin, lips or tongue – on brown or black skin, this may be easier to see on the palms of the hands or soles of the feet\n- skin that feels cold\n- difficulty breathing, or is taking lots of quick breaths\n- are confused\n- are sleepier than normal or difficult to wake\nThese could be signs of shock, which is a serious complication of dehydration.\n\n\nHOW TO REDUCE THE RISK OF DEHYDRATION:\n- Drinking fluids regularly can reduce the risk of dehydration. Water or diluted sugar-free squash are good choices.\n- You should drink enough during the day so that your pee is a pale colour.\n- Drink more when there's a higher risk of dehydrating. For example, if you're being sick, sweating due to hot weather or exercise, or you have diarrhoea.\n- Children under the age of 5 and older adults should get plenty of fluids as they have an increased risk of dehydration.\n\n\nHELPING SOMEONE YOU CARE FOR:\nA person you care for may not have a sense of how much they're drinking.\n\nYou can help them by:\n- making sure they drink at mealtimes\n- making drinking a social thing\n- offering them food with a high water content – for example, soup, ice cream, jelly and fruits like melon\n\nSOURCES:\nhttps://www.nhs.uk/conditions/dehydration/",
      "score": 0.664599617445493
    },
    {
      "file_name": "Mouth ulcers.txt",
      "text": "SEE A DENTIST OR GP IF YOUR MOUTH ULCER:\n- lasts longer than 3 weeks\n- is different to other mouth ulcers you've had before, for example if it's bigger than usual or near the back of your throat\n- bleeds or becomes more painful and red – this may be a sign of an infection\nAlthough most mouth ulcers are harmless, a long-lasting mouth ulcer is sometimes a sign of mouth cancer. It's best to get it checked.\nYou should also see a GP if you have other symptoms such as:\n- ulcers anywhere else on your body, such as your skin or genitals\n- painful, red or swollen joints\n\n\nTREATMENT FROM A DENTIST OR GP:\n- A GP or dentist may prescribe stronger medicine to treat severe, persistent or infected mouth ulcers.\nPossible treatments include:\n- steroids given as either a mouth spray, tablets that dissolve in your mouth or tablets that can be dissolved in water\n- painkilling gels, ointments, sprays or tablets\n- mouthwashes to kill or remove any germs in your mouth\n\n\nCHECK IF YOU HAVE A MOUTH ULCER:\n- Mouth ulcers usually appear inside the mouth on the cheeks or lips.\n- Ulcers can also appear on the tongue.\n- You may have more than 1 ulcer at a time.\n- Mouth ulcers are not contagious and should not be confused with cold sores.\n- Cold sores appear on the lips or around the mouth and often begin with a tingling, itching or burning sensation. They can also appear as a small group of pinhead-sized ulcers inside the mouth.",
      "score": 0.6452734508621489
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.142,
  "repeat": 1
}
```

#### uncovered_tinnitus — run 1

```json
{
  "id": "uncovered_tinnitus",
  "category": "uncovered_medical",
  "summary": {
    "reason_for_visit": "persistent ringing in one ear",
    "symptoms": [
      "persistent ringing in one ear"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "three days",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": "What investigations and treatment are appropriate for persistent tinnitus?",
    "summary": ""
  },
  "expectations": {
    "id": "uncovered_tinnitus",
    "category": "uncovered_medical",
    "expected_sources": [],
    "evidence": {},
    "answer_any": [],
    "query_contains": [
      "persistent tinnitus",
      "investigations"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?",
      "Does the answer explicitly acknowledge the requested guidance missing from the retrieved passages, or return the no-guidance response?",
      "If related guidance is provided, is every claim supported and clearly limited to what the passages establish?",
      "Does the answer avoid diagnosing from symptom overlap or inventing investigations, medicines, doses or treatment durations?"
    ],
    "coverage_note": "Iron deficiency anaemia lists tinnitus as a possible symptom, without a tinnitus management pathway."
  },
  "query": "Clinical guidance, and diagnostic criteria for: persistent ringing in one ear, Duration: three days, Additional concerns: What investigations and treatment are appropriate for persistent tinnitus?.",
  "result": {
    "answer": "The provided context does not contain information about persistent ringing in one ear, its investigations, or treatment. Therefore, I cannot provide a response based solely on the given context.",
    "confidence": "weak match",
    "confidence_message": "This answer has weak grounding in the knowledge base for this case — the retrieved information may not closely match the patient's presentation. Verify independently before relying on this answer.",
    "sources": [
      "Antibiotics are often not needed for middle ear infections because the body’s immune system can fight off the infection on its own. But sometimes antibiotics, such as amoxicillin, are needed to treat infants, severe cases, or cases that last longer than 2–3 days.\nFor mild cases of middle ear infection, your doctor might recommend watchful waiting or delayed antibiotic prescribing. \n\nWatchful waiting: Your child’s doctor may suggest watching and waiting to see if your child needs antibiotics. This gives the immune system time to fight off the infection. If your child doesn’t feel better after 2–3 days of rest, extra fluids, and pain relievers, the doctor will write a prescription for an antibiotic.\n\nDelayed prescribing: Your child’s doctor may give an antibiotic prescription but will suggest that you wait 2–3 days to see if your child is still sick before filling it. \n\nHow to Feel Better \nSome ways to feel better—whether or not antibiotics are needed for an ear infection: \n- Rest.\n- Drink extra water or other fluids.\n- Take acetaminophen or ibuprofen to relieve pain or fever. Ask your doctor or pharmacist what medications are safe for your child to take and what dose to give your child.\n\nOver-the-Counter Medicine and Children\nBe careful about giving over-the-counter medicines to children. Not all over-the-counter medicines are recommended for children of certain ages. \n\nPain relievers: \n- Children younger than 6 months: only give acetaminophen. \n- Children 6 months or older: it is OK to give acetaminophen or ibuprofen. \n- Never give aspirin to children because it can cause Reye’s syndrome, a rare but very serious illness that harms the liver and brain.\n\nBe sure to ask your doctor or pharmacist about the right dosage of over-the-counter medicines for your child’s age and size. Also, tell your child’s doctor and pharmacist about all the prescription and over-the-counter medicines they are taking.\n\nPrevention\nYou can help prevent ear infections by doing your best to stay healthy and keep others healthy.\n- Make sure your child is up to date on vaccinations and gets a flu vaccine every year. The pneumococcal vaccine protects against Streptococcus pneumoniae, a common cause of middle ear infections.\n- Clean your hands.",
      "- Make sure your child is up to date on vaccinations and gets a flu vaccine every year. The pneumococcal vaccine protects against Streptococcus pneumoniae, a common cause of middle ear infections.\n- Clean your hands. \n- Breastfeed exclusively until your baby is 6 months old and continue to breastfeed for at least 12 months. \n- Don’t smoke and avoid exposure to secondhand smoke.\n\nSources\nhttps://www.cdc.gov/antibiotic-use/communication-resources/preventing-treating-ear-infections.html"
    ],
    "link": [
      "https://www.cdc.gov/antibiotic-use/communication-resources/preventing-treating-ear-infections.html"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "pass",
    "reviewer": "Codex assistant",
    "scope": "answer compared with supplied patient input and actual returned passages; not clinician validation",
    "notes": "Assistant evidence review: The answer explicitly says the context does not contain information about persistent ringing, investigations or treatment. Retrieved Ear Infection.txt passages discuss middle-ear infection treatment and prevention, not tinnitus management. The answer did not apply those treatments to tinnitus. Related ear-infection links remain in the output despite the abstaining answer."
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true
  },
  "returned_source_files": [
    "Ear Infection.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Ear Infection.txt",
      "text": "Antibiotics are often not needed for middle ear infections because the body’s immune system can fight off the infection on its own. But sometimes antibiotics, such as amoxicillin, are needed to treat infants, severe cases, or cases that last longer than 2–3 days.\nFor mild cases of middle ear infection, your doctor might recommend watchful waiting or delayed antibiotic prescribing. \n\nWatchful waiting: Your child’s doctor may suggest watching and waiting to see if your child needs antibiotics. This gives the immune system time to fight off the infection. If your child doesn’t feel better after 2–3 days of rest, extra fluids, and pain relievers, the doctor will write a prescription for an antibiotic.\n\nDelayed prescribing: Your child’s doctor may give an antibiotic prescription but will suggest that you wait 2–3 days to see if your child is still sick before filling it. \n\nHow to Feel Better \nSome ways to feel better—whether or not antibiotics are needed for an ear infection: \n- Rest.\n- Drink extra water or other fluids.\n- Take acetaminophen or ibuprofen to relieve pain or fever. Ask your doctor or pharmacist what medications are safe for your child to take and what dose to give your child.\n\nOver-the-Counter Medicine and Children\nBe careful about giving over-the-counter medicines to children. Not all over-the-counter medicines are recommended for children of certain ages. \n\nPain relievers: \n- Children younger than 6 months: only give acetaminophen. \n- Children 6 months or older: it is OK to give acetaminophen or ibuprofen. \n- Never give aspirin to children because it can cause Reye’s syndrome, a rare but very serious illness that harms the liver and brain.\n\nBe sure to ask your doctor or pharmacist about the right dosage of over-the-counter medicines for your child’s age and size. Also, tell your child’s doctor and pharmacist about all the prescription and over-the-counter medicines they are taking.\n\nPrevention\nYou can help prevent ear infections by doing your best to stay healthy and keep others healthy.\n- Make sure your child is up to date on vaccinations and gets a flu vaccine every year. The pneumococcal vaccine protects against Streptococcus pneumoniae, a common cause of middle ear infections.\n- Clean your hands.",
      "score": 0.683397671085527
    },
    {
      "file_name": "Ear Infection.txt",
      "text": "- Make sure your child is up to date on vaccinations and gets a flu vaccine every year. The pneumococcal vaccine protects against Streptococcus pneumoniae, a common cause of middle ear infections.\n- Clean your hands. \n- Breastfeed exclusively until your baby is 6 months old and continue to breastfeed for at least 12 months. \n- Don’t smoke and avoid exposure to secondhand smoke.\n\nSources\nhttps://www.cdc.gov/antibiotic-use/communication-resources/preventing-treating-ear-infections.html",
      "score": 0.6758678160866449
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.681,
  "repeat": 1
}
```

#### uncovered_shingles — run 1

```json
{
  "id": "uncovered_shingles",
  "category": "uncovered_medical",
  "summary": {
    "reason_for_visit": "painful blisters in a band on one side of the torso",
    "symptoms": [
      "painful blisters in a band on one side of the torso"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "three days",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": "Could this be shingles, and what antiviral treatment and duration are appropriate?",
    "summary": ""
  },
  "expectations": {
    "id": "uncovered_shingles",
    "category": "uncovered_medical",
    "expected_sources": [],
    "evidence": {},
    "answer_any": [],
    "query_contains": [
      "shingles",
      "antiviral"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?",
      "Does the answer explicitly acknowledge the requested guidance missing from the retrieved passages, or return the no-guidance response?",
      "If related guidance is provided, is every claim supported and clearly limited to what the passages establish?",
      "Does the answer avoid diagnosing from symptom overlap or inventing investigations, medicines, doses or treatment durations?"
    ],
    "coverage_note": "Chickenpox discusses zoster and viral testing; this is not a shingles antiviral treatment protocol."
  },
  "query": "Clinical guidance, and diagnostic criteria for: painful blisters in a band on one side of the torso, Duration: three days, Additional concerns: Could this be shingles, and what antiviral treatment and duration are appropriate?.",
  "result": {
    "answer": "The context provided does not contain enough information to fully answer the question about painful blisters in a band on one side of the torso. However, based on the symptoms described, it could potentially be shingles, which is not covered in the provided context. For shingles, antiviral treatment is typically recommended within 72 hours of symptom onset to reduce the severity and duration of the outbreak. The duration of antiviral treatment usually ranges from 7 to 10 days. It is important to consult with a healthcare professional for a proper diagnosis and treatment plan.",
    "confidence": "moderate match",
    "confidence_message": "This answer is only moderately grounded in the knowledge base — use caution and consider verifying key details independently.",
    "sources": [
      "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear.",
      "Clinical features:\n- A mild prodrome of fever and malaise may occur 1 to 2 days before rash onset, particularly in adults. In children, the rash is often the first sign of disease.\n\n\nSymptoms in unvaccinated patients:\n- The rash is generalized and pruritic. It progresses rapidly from macular to papular to vesicular lesions before crusting. Lesions are typically present in all stages of development at the same time.\n- The rash usually appears on the chest, back, and face first, then spreads over the entire body. The lesions are usually most concentrated on the chest and back. Symptoms typically last 4 to 7 days.\n- In healthy children, varicella is generally mild, with an itchy rash, malaise, and temperature up to 102°F for 2 to 3 days. Infants, adolescents, adults, pregnant women, and immunocompromised people are at risk for more severe disease and have a higher incidence of complications.\n- Recovery from primary varicella infection usually provides immunity for life. In otherwise healthy people, a second occurrence of varicella is uncommon. The second occurrence of varicella may be more likely to occur in people with weakened immune systems.\n- As with other viral infections, re-exposure to natural (wild-type) varicella may lead to re-infection that boosts antibody titers without causing illness or detectable viremia.\n\n\nSymptoms in vaccinated patients (breakthrough varicella):\n- Breakthrough varicella is infection with wild-type varicella-zoster virus (VZV) occurring in a vaccinated person more than 42 days after varicella vaccination.\n- Breakthrough varicella is usually mild. Patients typically are afebrile or have low fever and develop fewer than 50 skin lesions. They usually have a shorter illness compared to unvaccinated people who get varicella. The rash is more likely to be predominantly maculopapular rather than vesicular. However, 25% to 30% of people vaccinated with one dose who get breakthrough varicella will have clinical features similar to unvaccinated people with varicella."
    ],
    "link": [
      "https://www.nhs.uk/conditions/cold-sores/",
      "https://www.cdc.gov/chickenpox/hcp/clinical-overview/index.html",
      "https://www.cdc.gov/chickenpox/hcp/clinical-signs/index.html"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "fail",
    "reviewer": "Codex assistant",
    "scope": "answer compared with supplied patient input and actual returned passages; not clinician validation",
    "notes": "Assistant evidence review: The answer says the context does not contain enough information, but then suggests shingles and states antiviral treatment is recommended within 72 hours and usually lasts 7 to 10 days. Neither returned passage supports that diagnosis inference or shingles treatment timing/duration. Cold sore.txt discusses facial cold sores, healing within 10 days and early antiviral creams; Chickenpox (Varicella).txt describes varicella rash features and symptoms lasting 4 to 7 days. Neither establishes the asserted shingles protocol. Failure: generation added unsupported guidance after retrieving related but insufficient passages. This is an evidence-grounding judgment, not a judgment about external medical correctness."
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true
  },
  "returned_source_files": [
    "Chickenpox (Varicella).txt",
    "Cold sore.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Cold sore.txt",
      "text": "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear.",
      "score": 0.717004299163818
    },
    {
      "file_name": "Chickenpox (Varicella).txt",
      "text": "Clinical features:\n- A mild prodrome of fever and malaise may occur 1 to 2 days before rash onset, particularly in adults. In children, the rash is often the first sign of disease.\n\n\nSymptoms in unvaccinated patients:\n- The rash is generalized and pruritic. It progresses rapidly from macular to papular to vesicular lesions before crusting. Lesions are typically present in all stages of development at the same time.\n- The rash usually appears on the chest, back, and face first, then spreads over the entire body. The lesions are usually most concentrated on the chest and back. Symptoms typically last 4 to 7 days.\n- In healthy children, varicella is generally mild, with an itchy rash, malaise, and temperature up to 102°F for 2 to 3 days. Infants, adolescents, adults, pregnant women, and immunocompromised people are at risk for more severe disease and have a higher incidence of complications.\n- Recovery from primary varicella infection usually provides immunity for life. In otherwise healthy people, a second occurrence of varicella is uncommon. The second occurrence of varicella may be more likely to occur in people with weakened immune systems.\n- As with other viral infections, re-exposure to natural (wild-type) varicella may lead to re-infection that boosts antibody titers without causing illness or detectable viremia.\n\n\nSymptoms in vaccinated patients (breakthrough varicella):\n- Breakthrough varicella is infection with wild-type varicella-zoster virus (VZV) occurring in a vaccinated person more than 42 days after varicella vaccination.\n- Breakthrough varicella is usually mild. Patients typically are afebrile or have low fever and develop fewer than 50 skin lesions. They usually have a shorter illness compared to unvaccinated people who get varicella. The rash is more likely to be predominantly maculopapular rather than vesicular. However, 25% to 30% of people vaccinated with one dose who get breakthrough varicella will have clinical features similar to unvaccinated people with varicella.",
      "score": 0.701876062042949
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 0.715,
  "repeat": 1
}
```

### Additional gout evaluation — 1 case

#### Run metadata and aggregate metrics

```json
{
  "created_utc": "20261006T011601481181Z",
  "git_commit": "a180107ec46954988a710cc4466321195db71a4a",
  "local_kb_sha256": {
    "ADHD in Adults.txt": "9230dc7b7e4ce8658f9499b0625332e26f96abaf64b3badec3a899ffdfbac863",
    "Acne.txt": "921638da3cba1267a6769886863ac0250ebf0b5afc50f71d84977e048e83822d",
    "Appendicitis.txt": "92dc9055cc47bb2f92b8a0144a5d2ad8de532656185fa5294bd092a5d1aca325",
    "Arthritis.txt": "a1df289eb16012d4f9e8aaf1d7e1374bfe2cfa5e1a11f85db7b04c696fdd75c5",
    "Asthma.txt": "c8088ce42111834aa1ecc5bebb34159b2faf5dcca28b6073e25b02f622ee16a8",
    "Bronchitis.txt": "3bafe246d64ae5af90837ed7919baec10015194d4e1f66194b083b11d029c338",
    "Bunions.txt": "d15e30d445deff5c676b2d57f9e3ca93af33361104350b5601a2c12d4919085c",
    "Cardiovascular disease.txt": "3c8b47898e13ebc296f336fae52a208256b3b98e50316f8d7ccea3aa1aed0e70",
    "Chest Cold (Acute Bronchitis).txt": "735efb832c1cd3737d96718762ceca98700f94961818f749ab15ef5603345537",
    "Chickenpox (Varicella).txt": "e249a41877828d21ed1f9a8ce2cd7ecd0fe74216e5a80ffca467f4ac09466d3b",
    "Coeliac disease.txt": "c98263738f251e2559556ace7b5f7f320217471b980c79bcaf87823099a535f0",
    "Cold sore.txt": "4aa45bda48683380159206377188dd7c1ceabcdca3d691a2ce7d2fae9954b9c1",
    "Cold.txt": "149d83801090e3922fe3bb4216fdefa6e8fcfbce6834d8d53b413a7c74ce19c7",
    "Covid 19.txt": "62123691e300deb7cafec4dd6bfca478fd47eddcab073018049cd82ac0c2a545",
    "Dehydration.txt": "15742dcad7b5f5b3075044a5c6e566929febc5a617550431bfba4dd7b64afd85",
    "Ear Infection.txt": "40f99ba6c0dfa5e44f576e44b5fae39b72782f4fcb6197a96bed3ecf2c9030a8",
    "Food poisoning.txt": "58d625922390987eb12201846e948ec5fdfcc75e2e2f365f5fd5cea0f6208547",
    "Heartburn and acid reflux.txt": "052074146f50a2ac6d7fbb8a1ef2938729547c48c6041b1433f0003521c86f51",
    "Influenza.txt": "fa0c205395723f2b1003e8a9c5ed469fe3c3df609635825eb41a5b9a2f7c9a84",
    "Insomnia.txt": "4a68918574d74edf4c390a2367aed6b094a117df296e6d25dc112706eca35b3d",
    "Iron deficiency anaemia.txt": "46eea963ac06a51f3da0f24021c52101d00c60f4f1a8f182d03921f4278de3f1",
    "Lyme Disease.txt": "d291fba95822d49b495c27b1fbaa04e2a3e8ca1814a74b2cba3b8360635748ce",
    "Measles.txt": "4ab90eb82122e5b3738360d9b9946c40f14636d585c3c1d1ee9948868c134a2d",
    "Meningococcal Disease.txt": "02bbab6b350de48957a1f12ec2f9e133dfce51b315d9d122909877ec4aaee6a8",
    "Migraine.txt": "d6d7253517cdda7f959873ae56d88950715c29b0da55918e4d60394933e1c8c1",
    "Mouth ulcers.txt": "aa55cb312fd7585ffa7731214894cf4e1329d41ce7e6d4fe8289020487f900f4",
    "Norovirus Stomach Bug.txt": "dd4171c27fcf06af29d1c2aabdfa38ede247a77bb9dffcf7ca4d2c8b8256e4f8",
    "Pink Eye.txt": "be9c04f17a4bf04538afe5fe3f0c25b9f809f7d65a8d2522b611c53e36898a2c",
    "Psoriasis.txt": "2a886a97993ee2aa12b6ada17f52d5f91d3a487b652217b9a3ad5b1845ba5e09",
    "Sciatica.txt": "e51e39e7c8c3885c6e47ea4115237b0399b4ee5243c685f49965386db78552ce",
    "Sprains and strains.txt": "4270eeda7fe3578d9bd6f82bdda7e172b3d9e10993ed12d469c3b8669dffcd35",
    "Strep Throat.txt": "95381ddb9fdc0e50ec04c6b32058206fcc0c36431c400b171f344638efdf0ac1",
    "Tooth decay.txt": "f316f06022064d3bd2109cb210caaa9c5807581dfb86d5c6eb750bb6cd9cf3f9",
    "Whiplash.txt": "fe9c642f2eee6279d24e2a7f0d0dc95f3892d16abd0139ea91aadda3ba30c906"
  },
  "runtime_sha256": "0d3e2f23362debf58b5f21263debd8d5bc70b89623ee45b937f62de9dc0c370f",
  "cases_sha256": "3d4b99d36db5da35d0648f5fcceef6696e0aa68c0eac799c84058d1e932f30f3",
  "scope": "final guidance only; fixed summary inputs; no chat extraction evaluation",
  "database_contents_verified_against_local_files": false,
  "metrics": {
    "query_context": {
      "passed": 1,
      "total": 1,
      "rate": 1.0
    },
    "response_shape": {
      "passed": 1,
      "total": 1,
      "rate": 1.0
    },
    "source_links": {
      "passed": 1,
      "total": 1,
      "rate": 1.0
    },
    "source_traceability": {
      "passed": 1,
      "total": 1,
      "rate": 1.0
    }
  }
}
```

#### uncovered_gout — run 1

```json
{
  "id": "uncovered_gout",
  "category": "uncovered_medical",
  "summary": {
    "reason_for_visit": "painful swollen big toe joint",
    "symptoms": [
      "painful swollen big toe joint",
      "redness around the big toe joint"
    ],
    "symptom_location": null,
    "onset": null,
    "duration": "three days",
    "severity": null,
    "relevant_history": [],
    "medical_history": {
      "status": "unknown",
      "items": []
    },
    "current_medications": {
      "status": "unknown",
      "items": []
    },
    "allergies": {
      "status": "unknown",
      "items": []
    },
    "additional_concerns": "Could this be gout, and what investigations and gout-specific treatment are appropriate?",
    "summary": ""
  },
  "expectations": {
    "id": "uncovered_gout",
    "category": "uncovered_medical",
    "expected_sources": [],
    "evidence": {},
    "answer_any": [],
    "query_contains": [
      "gout",
      "investigations"
    ],
    "query_excludes": [],
    "expect_abstention": false,
    "manual_review": [
      "Are substantive claims supported by the actual returned passages?",
      "Are patient details preserved without invented or contradictory facts?",
      "Is guidance appropriately qualified rather than a confirmed diagnosis?",
      "Does the answer explicitly acknowledge the requested guidance missing from the retrieved passages, or return the no-guidance response?",
      "If related guidance is provided, is every claim supported and clearly limited to what the passages establish?",
      "Does the answer avoid diagnosing from symptom overlap or inventing investigations, medicines, doses or treatment durations?"
    ],
    "coverage_note": "No gout, urate or uric-acid guidance was found in the local corpus. Arthritis provides general joint guidance and Bunions covers another cause of big-toe pain."
  },
  "query": "Clinical guidance, and diagnostic criteria for: painful swollen big toe joint, redness around the big toe joint, Duration: three days, Additional concerns: Could this be gout, and what investigations and gout-specific treatment are appropriate?.",
  "result": {
    "answer": "The context provided does not contain enough information to fully answer the question regarding gout, investigations, and gout-specific treatment. However, based on the context, the symptoms described could be consistent with a bunion. If gout is suspected, further investigation and gout-specific treatment would be beyond the scope of the provided context.",
    "confidence": "moderate match",
    "confidence_message": "This answer is only moderately grounded in the knowledge base — use caution and consider verifying key details independently.",
    "sources": [
      "BUNIONS:\n\nOVERVIEW:\nBunions are bony lumps that form on the side of the feet. Surgery is the only way to get rid of them, but there are things you can do to ease any pain they cause.\n\nSYMPTOMS OF BUNIONS:\n- The main symptoms of bunions are hard lumps on the sides of your feet, by your big toes.\n- Your big toe may point towards your other toes.\n- You may have hard or swollen skin. The bunion may look red or darker than the skin around it.\n- You may also have pain along the side or bottom of your feet. This is usually worse when wearing shoes and walking.\n\n\nHOW TO EASE BUNION PAIN YOURSELF:\n- You cannot get rid of bunions or stop them getting worse yourself, but there are things you can do to ease any pain.\nDo:\n- wear wide shoes with a low heel and soft sole\n- hold an ice pack (or a bag of frozen peas) wrapped in a tea towel to the bunion for up to 5 minutes at a time\n- try bunion pads (soft pads you put in shoes to stop them rubbing on a bunion) – you can buy these from pharmacies\n- take paracetamol or ibuprofen\n- try to lose weight if you're overweight\nDon’t:\n- do not wear high heels or tight, pointy shoes\n\n\nSEE A GP IF:\n- pain from a bunion has not improved after trying home treatments for a few weeks\n- the pain is stopping you doing your normal activities\n- your bunions are getting worse\n- you have bunions and diabetes – foot problems can be more serious if you have diabetes\n\n\nTREATMENTS FOR BUNIONS:\n- If you have bunions, a GP will look at your foot and ask you about your symptoms.\n- They might refer you to a foot specialist (podiatrist).\n- A GP or podiatrist can advise you about:\n  * things you can do to ease your symptoms\n  * things you can buy or have specially made to reduce bunion pain, such as insoles (orthotics), toe spacers and toe supports (splints)\nYou can also pay to see a foot specialist privately.",
      "SURGERY:\n- A GP may refer you for surgery if your bunions are very painful or they're having a big effect on your life.\n- Surgery is not done just to improve how your feet look.\nWhat happens during bunion surgery:\n- The most common surgery for bunions is an osteotomy.\nThis involves:\n- Making a small cut or cuts in the skin over your big toe.\n- Cutting or scraping away the bunion.\n- Straightening your toe bone.\n- Fixing your toe bone in place with metal screws or staples put under your skin. These are often left in permanently.\nSurgery is usually done when you're asleep under general anaesthetic. But sometimes it may be done under local anaesthetic (where you're awake but feel no pain).\nMost people go home the same day.\nIt can take a while to recover from bunion surgery.\nYou'll usually need to:\n- rest and keep your feet raised as much as possible for at least 2 weeks\n- avoid driving for 6 to 8 weeks\n- stay off work for 2 to 12 weeks\n- avoid sports for 3 to 6 months\nAfter the operation:\n- your toes might be weaker or stiffer than before\n- your toes may not be perfectly straight\n- your feet may still be painful\nBunions sometimes come back after surgery.\n\n\nHOW TO PREVENT BUNIONS:\n- The cause of bunions is not always known, but you may be more likely to get them if you wear shoes that do not fit properly.\nIt might help to:\n- make sure your shoes are the correct size and have enough room for your toes\n- avoid shoes with high heels or pointy toes\n\n\nSOURCE:\nhttps://www.nhs.uk/conditions/bunions/"
    ],
    "link": [
      "https://www.nhs.uk/conditions/bunions/"
    ],
    "parse_error": false
  },
  "error": null,
  "manual_review": {
    "status": "pass",
    "reviewer": "Codex assistant",
    "scope": "Missing-guidance handling and comparison with retrieved passages; not clinician validation",
    "notes": "Assistant evidence review: the answer explicitly states that gout investigations and treatment are beyond the supplied context, and gives no gout-specific medicines, doses or tests. It cautiously says symptoms could be consistent with a bunion; the returned passage describes big-toe pain, swollen skin and redness. This is a qualified possibility, not a confirmed diagnosis. Limitation: the input does not report the hard lump identified as a main bunion symptom, so this response does not establish a bunion diagnosis. Both retrieved passages concern bunions (scores approximately 0.7185 and 0.6976). This single run meets the missing-guidance criterion; it does not prove repeatability."
  },
  "checks": {
    "response_shape": true,
    "query_context": true,
    "source_traceability": true,
    "source_links": true
  },
  "returned_source_files": [
    "Bunions.txt"
  ],
  "raw_candidates": [
    {
      "file_name": "Bunions.txt",
      "text": "BUNIONS:\n\nOVERVIEW:\nBunions are bony lumps that form on the side of the feet. Surgery is the only way to get rid of them, but there are things you can do to ease any pain they cause.\n\nSYMPTOMS OF BUNIONS:\n- The main symptoms of bunions are hard lumps on the sides of your feet, by your big toes.\n- Your big toe may point towards your other toes.\n- You may have hard or swollen skin. The bunion may look red or darker than the skin around it.\n- You may also have pain along the side or bottom of your feet. This is usually worse when wearing shoes and walking.\n\n\nHOW TO EASE BUNION PAIN YOURSELF:\n- You cannot get rid of bunions or stop them getting worse yourself, but there are things you can do to ease any pain.\nDo:\n- wear wide shoes with a low heel and soft sole\n- hold an ice pack (or a bag of frozen peas) wrapped in a tea towel to the bunion for up to 5 minutes at a time\n- try bunion pads (soft pads you put in shoes to stop them rubbing on a bunion) – you can buy these from pharmacies\n- take paracetamol or ibuprofen\n- try to lose weight if you're overweight\nDon’t:\n- do not wear high heels or tight, pointy shoes\n\n\nSEE A GP IF:\n- pain from a bunion has not improved after trying home treatments for a few weeks\n- the pain is stopping you doing your normal activities\n- your bunions are getting worse\n- you have bunions and diabetes – foot problems can be more serious if you have diabetes\n\n\nTREATMENTS FOR BUNIONS:\n- If you have bunions, a GP will look at your foot and ask you about your symptoms.\n- They might refer you to a foot specialist (podiatrist).\n- A GP or podiatrist can advise you about:\n  * things you can do to ease your symptoms\n  * things you can buy or have specially made to reduce bunion pain, such as insoles (orthotics), toe spacers and toe supports (splints)\nYou can also pay to see a foot specialist privately.",
      "score": 0.718549838325411
    },
    {
      "file_name": "Bunions.txt",
      "text": "SURGERY:\n- A GP may refer you for surgery if your bunions are very painful or they're having a big effect on your life.\n- Surgery is not done just to improve how your feet look.\nWhat happens during bunion surgery:\n- The most common surgery for bunions is an osteotomy.\nThis involves:\n- Making a small cut or cuts in the skin over your big toe.\n- Cutting or scraping away the bunion.\n- Straightening your toe bone.\n- Fixing your toe bone in place with metal screws or staples put under your skin. These are often left in permanently.\nSurgery is usually done when you're asleep under general anaesthetic. But sometimes it may be done under local anaesthetic (where you're awake but feel no pain).\nMost people go home the same day.\nIt can take a while to recover from bunion surgery.\nYou'll usually need to:\n- rest and keep your feet raised as much as possible for at least 2 weeks\n- avoid driving for 6 to 8 weeks\n- stay off work for 2 to 12 weeks\n- avoid sports for 3 to 6 months\nAfter the operation:\n- your toes might be weaker or stiffer than before\n- your toes may not be perfectly straight\n- your feet may still be painful\nBunions sometimes come back after surgery.\n\n\nHOW TO PREVENT BUNIONS:\n- The cause of bunions is not always known, but you may be more likely to get them if you wear shoes that do not fit properly.\nIt might help to:\n- make sure your shoes are the correct size and have enough room for your toes\n- avoid shoes with high heels or pointy toes\n\n\nSOURCE:\nhttps://www.nhs.uk/conditions/bunions/",
      "score": 0.697554147535068
    }
  ],
  "retrieval_settings": [
    {
      "similarity_top_k": 2
    }
  ],
  "seconds": 4.325,
  "repeat": 1
}
```
