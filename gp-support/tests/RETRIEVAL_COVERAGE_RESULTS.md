# Retrieval coverage evaluation results

**Indexed documents: 34/34. Retrieved expected documents: 29/34. Runtime errors: 0.**

Top chunks: 2; cutoff: 0.67; model: `BAAI/bge-small-en-v1.5`.

One fixed symptom-based query per document. Exact filename matches are required.
A miss does not prove that a document is never retrievable. Overlapping documents may compete.
Chunk presence does not establish that stored text is complete or up to date.


| Expected document | Indexed chunks | Surviving retrieved documents (score) | Result |
|---|---:|---|---|
| ADHD in Adults.txt | 3 | ADHD in Adults.txt (0.7015); ADHD in Adults.txt (0.6924) | PASS |
| Acne.txt | 2 | Acne.txt (0.6807) | PASS |
| Appendicitis.txt | 5 | Appendicitis.txt (0.8086); Appendicitis.txt (0.7460) | PASS |
| Arthritis.txt | 2 | Arthritis.txt (0.6735) | PASS |
| Asthma.txt | 2 | Asthma.txt (0.7657); Chest Cold (Acute Bronchitis).txt (0.7182) | PASS |
| Bronchitis.txt | 2 | Chest Cold (Acute Bronchitis).txt (0.7797); Bronchitis.txt (0.7507) | PASS |
| Bunions.txt | 2 | Bunions.txt (0.7623); Bunions.txt (0.6711) | PASS |
| Cardiovascular disease.txt | 2 | Cardiovascular disease.txt (0.7084); Chest Cold (Acute Bronchitis).txt (0.6760) | PASS |
| Chest Cold (Acute Bronchitis).txt | 3 | Chest Cold (Acute Bronchitis).txt (0.7755); Cold.txt (0.7641) | PASS |
| Chickenpox (Varicella).txt | 5 | Psoriasis.txt (0.6813) | FAIL |
| Coeliac disease.txt | 3 | Coeliac disease.txt (0.7731); Coeliac disease.txt (0.7520) | PASS |
| Cold sore.txt | 2 | Cold sore.txt (0.6799) | PASS |
| Cold.txt | 3 | Cold.txt (0.7438); Influenza.txt (0.7048) | PASS |
| Covid 19.txt | 4 | None | FAIL |
| Dehydration.txt | 2 | Dehydration.txt (0.7381); Dehydration.txt (0.7234) | PASS |
| Ear Infection.txt | 3 | Ear Infection.txt (0.7964); Ear Infection.txt (0.7221) | PASS |
| Food poisoning.txt | 3 | Food poisoning.txt (0.7686); Food poisoning.txt (0.7601) | PASS |
| Heartburn and acid reflux.txt | 3 | Heartburn and acid reflux.txt (0.7775); Heartburn and acid reflux.txt (0.6780) | PASS |
| Influenza.txt | 2 | Cold.txt (0.7302); Influenza.txt (0.7283) | PASS |
| Insomnia.txt | 3 | Insomnia.txt (0.7071); Insomnia.txt (0.7071) | PASS |
| Iron deficiency anaemia.txt | 3 | Dehydration.txt (0.6851) | FAIL |
| Lyme Disease.txt | 3 | Lyme Disease.txt (0.7726); Lyme Disease.txt (0.7208) | PASS |
| Measles.txt | 4 | Pink Eye.txt (0.7137); Cold.txt (0.7020) | FAIL |
| Meningococcal Disease.txt | 5 | Meningococcal Disease.txt (0.7256); Lyme Disease.txt (0.7003) | PASS |
| Migraine.txt | 3 | Migraine.txt (0.7363); Migraine.txt (0.6767) | PASS |
| Mouth ulcers.txt | 3 | Mouth ulcers.txt (0.7566); Cold sore.txt (0.7304) | PASS |
| Norovirus Stomach Bug.txt | 3 | Food poisoning.txt (0.7363); Food poisoning.txt (0.7351) | FAIL |
| Pink Eye.txt | 3 | Psoriasis.txt (0.6810); Pink Eye.txt (0.6711) | PASS |
| Psoriasis.txt | 3 | Psoriasis.txt (0.6868) | PASS |
| Sciatica.txt | 3 | Sciatica.txt (0.6847) | PASS |
| Sprains and strains.txt | 4 | Sprains and strains.txt (0.6975); Appendicitis.txt (0.6969) | PASS |
| Strep Throat.txt | 2 | Strep Throat.txt (0.7569); Strep Throat.txt (0.6793) | PASS |
| Tooth decay.txt | 2 | Tooth decay.txt (0.7323) | PASS |
| Whiplash.txt | 2 | Whiplash.txt (0.7603) | PASS |

## Index inventory observations

Indexed filenames absent from local corpus: None.
Chunks without usable filename metadata: 0.

## Method and limits

Index presence was checked through read-only SQL. Retrieval used the production query builder,
embedding model, vector store, top-k setting and similarity postprocessor. Database setup was
disabled and the synchronous database connection enforced read-only transactions.
Symptoms overlap between conditions; these are document-coverage probes, not diagnostic tests.
Cases and expectations were fixed before execution. Results were not used to rewrite failed queries.
See [RETRIEVAL_COVERAGE_EVALUATION.md](RETRIEVAL_COVERAGE_EVALUATION.md) for commands.

## Retrieval configuration comparison

The same 34 fixed queries were also tested with four temporary retrieval
configurations.

| Configuration | Exact documents retrieved |
|---|---:|
| Current baseline: `top_k=2`, cutoff `0.67` | 29 / 34 |
| `top_k=3`, cutoff `0.67` | 29 / 34 |
| `top_k=2`, cutoff `0.65` | 30 / 34 |
| `top_k=3`, cutoff `0.65` | 30 / 34 |

Increasing `top_k` from 2 to 3 produced no coverage improvement. Lowering the
cutoff from `0.67` to `0.65` recovered only one additional document for these
queries, while the remaining misses were still displaced by semantically related
documents.

The current `0.67` cutoff is therefore retained as the baseline. It is more
conservative about passing marginally similar chunks to answer generation, which
reduces the chance of adding loosely related evidence to the prompt. A future
change to `0.65` should be supported by a separate final-answer comparison,
including source correctness, unsupported claims and abstention behaviour, rather
than by the one-document coverage increase alone.


## Complete run record

```json
{
  "runtime_sha256": "0d3e2f23362debf58b5f21263debd8d5bc70b89623ee45b937f62de9dc0c370f",
  "evaluator_sha256": "7a0154bf7aadfe9a3b1ae71b57f06959b4e0ef2ff0547faf3365b735398498ed",
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
  "settings": {
    "similarity_cutoff": 0.67,
    "similarity_top_k": 2,
    "embedding_model": "BAAI/bge-small-en-v1.5"
  },
  "table_exists": true,
  "database_read_only": true,
  "extra_indexed_files": [],
  "unnamed_chunks": 0,
  "cases": [
    {
      "expected_document": "ADHD in Adults.txt",
      "summary": {
        "symptoms": [
          "difficulty concentrating, losing things, restlessness since childhood"
        ]
      },
      "evidence_anchor": "losing things often",
      "query": "Clinical guidance, and diagnostic criteria for: difficulty concentrating, losing things, restlessness since childhood.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "ADHD in Adults.txt",
          "score": 0.701510211870379,
          "survived": true,
          "text": "ADHD IN ADULTS:\n\n\nOVERVIEW:\nADHD (attention deficit hyperactivity disorder) is a condition where the brain works differently to most people. If you have ADHD, you may have trouble with things like concentrating and sitting still. There are things you can do to help manage your symptoms.\n\n\nSYMPTOMS OF ADHD (ATTENTION DEFICIT HYPERACTIVITY DISORDER):\nSymptoms of ADHD involve your ability to pay attention to things (being inattentive), having high energy levels (being hyperactive) and your ability to control your impulses (being impulsive).\nYou may show signs of being inattentive, such as:\n- being easily distracted or forgetful\n- finding it hard to organise your time\n- finding it hard to follow instructions or finish tasks\n- losing things often, like your wallet, mobile or keys\nYou may show signs of being hyperactive and impulsive, including:\n- having a lot of energy or feeling restless\n- being very talkative or interrupting conversations\n- making quick decisions without thinking about what might happen as a result\nMost people with ADHD will have symptoms of both the inattentive and hyperactive-impulsive type. Some only show signs of one type.\nThese symptoms usually start before the age of 12.\nADHD is thought to be recognised less often in women than men. This may be because women with ADHD more commonly have inattentive symptoms and these can be harder to recognise than hyperactive symptoms.\n\n\nGETTING HELP WITH ADHD (ATTENTION DEFICIT HYPERACTIVITY DISORDER):\n- If your ADHD symptoms are affecting your studies, work or relationships, make an appointment with a GP to find out what support is available.\n- At your appointment, the GP will ask about your symptoms and how they affect your life. They may also want to consider other conditions that could be causing your symptoms, such as autism, Tourette's or anxiety, to help you get the right care.\n- After the appointment, the GP may decide to refer you for an assessment with a mental health professional specialising in ADHD.\n- If you have already been diagnosed with ADHD in childhood and need help for your symptoms, talk to your GP about getting a referral.\n- People with ADHD may often have other conditions too, such as depression, anxiety or addictions, or a learning difficulty such as dyslexia."
        },
        {
          "file_name": "ADHD in Adults.txt",
          "score": 0.692405900132832,
          "survived": true,
          "text": "WHAT HAPPENS AT AN ADHD ASSESSMENT:\n- Your appointment will be with an ADHD specialist such as a psychiatrist.\n- They’ll ask about the history of your symptoms, particularly if they started when you were a child, and how these symptoms affected you at school.\n- The assessment will focus on different areas of your life, including:\n  * work and education\n  * family and friends\n  * medical history, including any mental health issues\n- The specialist may want to contact someone who knows you well, such as a family member or close friend.\n- If you’re diagnosed with ADHD, the specialist will talk to you about what this means and what will happen next, including what help and support may be available.\n\n\n\nHOW TO MANAGE ADHD (ATTENTION DEFICIT HYPERACTIVITY DISORDER):\n- ADHD can be managed in many ways, including lifestyle changes, changes at work, or medicines.\n- It depends on your symptoms and how they're affecting you. Not everyone needs or wants to take medicine to help manage their ADHD symptoms.\n- When you get a diagnosis of ADHD, your specialist will discuss ways you can be supported.\nLifestyle:\nThere are things you can do to help yourself.\n- Make time for physical activities you enjoy, as exercise has many health benefits and can be a good focus for your energy.\n- Exercise also helps reduce symptoms of anxiety and depression. Anxiety and depression can make your ADHD symptoms worse.\n- It’s important to get enough sleep. Having a regular bedtime and a quiet dark bedroom can help. Try to avoid screens, caffeine, sugar and alcohol close to bedtime.\n- Aim for a healthy, balanced diet and regular mealtimes.\n- You may also find it helpful to talk to friends and family about your ADHD.\nWork, college or university:\n- At your workplace or place of study, you can request changes to help you manage your ADHD. These are called “reasonable adjustments”.\n- Reasonable adjustments may include things like:\n  * having a personalised work space in a quiet area\n  * having written instructions as well as spoken instructions\n  * having help from another person to plan and structure your tasks"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Acne.txt",
      "summary": {
        "symptoms": [
          "oily skin with blackheads and whiteheads on the face"
        ]
      },
      "evidence_anchor": "blackheads",
      "query": "Clinical guidance, and diagnostic criteria for: oily skin with blackheads and whiteheads on the face.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Acne.txt",
          "score": 0.6806997631729079,
          "survived": true,
          "text": "ACNE:\n\n\nOVERVIEW:\n- Acne is a common skin condition that affects most people at some point. It causes spots, oily skin and sometimes skin that's hot or painful to touch.\n\n\nSYMPTOMS OF ACNE:\nAcne most commonly develops on the:\n- face: this affects almost everyone with acne\n- back: this affects more than half of people with acne\n- chest: this affects about 15% of people with acne\n\n\nTYPES OF SPOTS:\nThere are 6 main types of spot caused by acne:\n- blackheads – small black or yellowish bumps that develop on the skin; they're not filled with dirt, but are black because the inner lining of the hair follicle produces colour\n- whiteheads – have a similar appearance to blackheads, but may be firmer and will not empty when squeezed\n- papules – small red bumps that may feel tender or sore\n- pustules – similar to papules, but have a white tip in the centre, caused by a build-up of pus\n- nodules – large hard lumps that build up beneath the surface of the skin and can be painful\n- cysts – the most severe type of spot caused by acne; they're large pus-filled lumps that look similar to boils and carry the greatest risk of causing permanent scarring"
        },
        {
          "file_name": "Acne.txt",
          "score": 0.644625506125371,
          "survived": false,
          "text": "THINGS YOU CAN TRY IF YOU HAVE ACNE:\nThese self-help techniques may be useful:\n- Do not wash affected areas of skin more than twice a day. Frequent washing can irritate the skin and make symptoms worse.\n- Wash the affected area with a mild soap or cleanser and lukewarm water. Very hot or cold water can make acne worse.\n- Do not try to \"clean out\" blackheads or squeeze spots. This can make them worse and cause permanent scarring.\n- Avoid make-up, skincare and suncare products that are oil-based (sometimes labelled “comedogenic”). Use water-based non-comedogenic products, as they’re less likely to block the pores in your skin.\n- Completely remove make-up before going to bed.\n- If dry skin is a problem, use a fragrance-free water-based emollient.\n- Regular exercise cannot improve your acne, but it can boost your mood and improve your self-esteem. Shower as soon as possible once you finish exercising as sweat can irritate your acne.\n- Wash your hair regularly and try to avoid letting your hair fall across your face.\n- Although acne cannot be cured, it can be controlled with treatment.\n- If you develop mild acne, it's a good idea to speak to a pharmacist for advice.\n- Several creams, lotions and gels for treating spots are available to buy from pharmacies.\n- Products containing a low concentration of benzoyl peroxide may be recommended, but be careful as this can bleach clothing.\n- If your acne is severe or appears on your chest and back, it may need to be treated with antibiotics or stronger creams that are only available on prescription.\n- Try to resist the temptation to pick or squeeze the spots, as this can lead to permanent scarring.\n- Treatments can take several months to work, so do not expect results overnight. Once they do start to work, the results are usually good.\n\n\n\nWHEN TO SEEK MEDICAL ADVICE:\n- If you have mild acne, speak to a pharmacist about medicines to treat it.\n- If these do not control your acne, or it's making you feel very unhappy, see a GP.\n- You should see a GP if you have moderate or severe acne or you develop nodules or cysts, as they need to be treated properly to avoid scarring. \n\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/acne/"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Appendicitis.txt",
      "summary": {
        "symptoms": [
          "abdominal pain starting near the belly button and moving to the lower right side, nausea"
        ]
      },
      "evidence_anchor": "belly button",
      "query": "Clinical guidance, and diagnostic criteria for: abdominal pain starting near the belly button and moving to the lower right side, nausea.",
      "indexed_chunks": 5,
      "candidates": [
        {
          "file_name": "Appendicitis.txt",
          "score": 0.80856466293335,
          "survived": true,
          "text": "APPENDICITIS:\n\n\nOVERVIEW:\nAppendicitis is swelling and infection in your appendix (part of your bowel). It usually causes pain in the lower right side of your abdomen (tummy). It needs urgent treatment in hospital.\n\n\nSYMPTOMS OF APPENDICITIS:\n- Symptoms of appendicitis usually start with pain in the middle of your abdomen (tummy), around your belly button. After a few hours the pain usually moves to the lower right side of your abdomen, and gets worse.\n- The pain may feel worse when you move, cough or press on the area. It may feel slightly better when you pull your knees up to your chest.\n- Some people with appendicitis do not have the usual pain symptoms. For example, you might have pain that's less severe, develops more slowly, or in a different place. This can be more likely if you're pregnant and in young children and older people.\n- Other symptoms of appendicitis can include:\n  * feeling or being sick, or loss of appetite\n  * a high temperature\n  * constipation or diarrhoea\n  * peeing more than usual\n  * sudden confusion (in older people)\n-If appendicitis is not treated quickly, your appendix can burst. If this happens your pain may suddenly get better for a short time. You'll then usually have severe pain that spreads to the whole of your abdomen. It may be very painful to move.\n\n\nIF YOU'RE NOT SURE IT'S APPENDICITIS:\nMany other conditions can cause pain in your abdomen, including:\n- urinary tract infections\n- kidney stones or gallstones\n- bowel problems such as irritable bowel syndrome or Crohn's disease\n- conditions affecting your womb or ovaries, such as pelvic inflammatory disease or a ruptured ovarian cyst\n- an ectopic pregnancy\nBut do not try to diagnose the problem yourself. Get medical help if you're worried.\n\n\nASK FOR AN URGENT GP APPOINTMENT OR GET HELP IF:\nYou or your child have pain in your abdomen (tummy) that:\n- is gradually getting worse or does not go away\n- moves to the lower right side of your abdomen"
        },
        {
          "file_name": "Appendicitis.txt",
          "score": 0.7459641695022581,
          "survived": true,
          "text": "GO TO A&E IF:\nYou or your child have:\n- severe pain in your abdomen (tummy)\n- confusion, blotchy or paler than usual skin (on brown or black skin this may be easier to see on the palms of the hands or soles of the feet) or difficulty breathing – these could be signs of sepsis\n\n\nHOW APPENDICITIS IS DIAGNOSED:\n- If you have symptoms of appendicitis, a GP or hospital doctor will feel your abdomen (tummy) to check for pain and swelling.\n- You'll need to go to hospital for tests and treatment. Tests you may have include:\n  * blood tests\n  * testing a sample of your pee\n  * scans such as an ultrasound scan or CT scan to check for swelling in your appendix\n  * a pregnancy test if there's a chance you could be pregnant\n- There's no test that can always show if you have appendicitis. It can be hard to diagnose because the symptoms can be similar to other conditions. Sometimes doctors will try waiting a few hours to see how your symptoms develop in hospital.\n- If your symptoms mean it's very likely you have appendicitis, or if your appendix may have burst, doctors may recommend surgery instead of waiting for more tests."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Arthritis.txt",
      "summary": {
        "symptoms": [
          "persistent joint pain and stiffness affecting daily activities"
        ]
      },
      "evidence_anchor": "joint pain and stiffness",
      "query": "Clinical guidance, and diagnostic criteria for: persistent joint pain and stiffness affecting daily activities.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Arthritis.txt",
          "score": 0.67352662402074,
          "survived": true,
          "text": "Arthritis\n\n\nKEY POINTS\n- Arthritis affects about 1 in 5 U.S. adults.\n- It affects the joints, tissues around the joint, and other connective tissues.\n- Arthritis is a leading cause of work disability among adults.\n- People with other chronic conditions—such as obesity, diabetes, and heart disease—often have arthritis.\n\n\nOVERVIEW\n- Arthritis is a general term for conditions that affect the joints, tissues around joints, and other connective tissues. There are more than 100 types of arthritis.\n- The causes of some forms of arthritis are unknown.\n\nRISK FACTORS\nSome behaviors and characteristics can increase your chances of developing arthritis.\nSeveral of these risk factors are within your control, including:\n- Smoking.\n- Having overweight or obesity.\n- Joint injuries—like from sports, falls, and accidents.\n- Work-related activities that lead to joint injury—like bending, squatting, and other repetitive motions.\n- Learn more about risk factors and what you can do lower your risk of developing arthritis.\n\n\nSYMPTOMS AND DIAGNOSIS\nSymptoms vary by arthritis type but usually include joint pain and stiffness.\nHealth care providers can diagnose arthritis by:\n- Reviewing your health and family history.\n- Doing a physical exam.\n- Taking X-rays.\n- Doing lab tests (as needed).\n- Once you know the type of arthritis you have, you can work with your provider to decide on the best ways to manage and treat it.\n\n\nMANAGING YOUR ARTHRITIS\nIt is important to manage symptoms\nManaging arthritis symptoms helps you:\n- Prevent or delay it from getting worse or causing disability.\n- Reduce pain.\n- Improve your overall health and well-being.\n\n\nWAYS TO MANAGE ARTHRITIS\nFive ways to manage arthritis and its symptoms:\n- Learn self-management skills.\n- Be physically active.\n- Manage your weight.\n- Protect your joints.\n- Talk to your health care provider if you have symptoms. The earlier you receive an arthritis diagnosis, the sooner you can begin treatment to lessen its effects and prevent or delay it from getting worse."
        },
        {
          "file_name": "Sprains and strains.txt",
          "score": 0.663991709709663,
          "survived": false,
          "text": "SOURCES:\nhttps://www.nhs.uk/conditions/sprains-and-strains/"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Asthma.txt",
      "summary": {
        "symptoms": [
          "wheezing, chest tightness and coughing at night, worse after exercise"
        ]
      },
      "evidence_anchor": "coughing at night",
      "query": "Clinical guidance, and diagnostic criteria for: wheezing, chest tightness and coughing at night, worse after exercise.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Asthma.txt",
          "score": 0.765734016895294,
          "survived": true,
          "text": "Asthma\n\nKEY POINTS\n- Asthma is a disease that affects your lungs.\n- It is one of the most common long-term diseases of children, but adults can have asthma, too.\n- Asthma causes wheezing, breathlessness, chest tightness, and coughing at night or early in the morning.\n\nSYMPTOMS\n- Asthma causes wheezing, breathlessness, chest tightness, and coughing at night or early in the morning. \n- If you have asthma, you have it all the time, but you will have asthma attacks only when something bothers your lungs.\n- An asthma attack may include coughing, chest tightness, wheezing, and trouble breathing. \n- The attack happens in your body's airways, which are the paths that carry air to your lungs. As the air moves through your lungs, the airways become smaller, like the branches of a tree are smaller than the tree trunk. During an asthma attack, the sides of the airways in your lungs swell and the airways shrink. Less air gets in and out of your lungs, and mucous that your body makes clogs up the airways.\n- You can control your asthma by knowing the warning signs of an asthma attack, staying away from things that cause an attack, and following your doctor's advice.\n\nDIAGNOSIS\n- It can be hard to tell if someone has asthma, especially in children under age 5. A doctor can help you find out if you have asthma.\n- During a checkup, a doctor may ask if you cough a lot, especially at night. \n- The doctor may also ask whether your breathing problems are worse after physical activity or at certain times of year. \n- The doctor may ask about chest tightness, wheezing, and colds lasting more than 10 days. \n- The docotr may ask whether anyone in your family has or has had asthma, allergies, or other breathing problems. \n- The doctor may ask about your home and whether you have missed school or work or have trouble doing certain things.\n- The doctor may also do a breathing test, called spirometry, to find out how well your lungs are working. Spirometry tests how much air you breathe out after taking a very deep breath before and after you use asthma medicine."
        },
        {
          "file_name": "Chest Cold (Acute Bronchitis).txt",
          "score": 0.718234241008759,
          "survived": true,
          "text": "Chest Cold (Acute Bronchitis) Basics\n\nKEY POINTS\n- Cough keeping you up at night? Congestion? Sore throat? You may have a chest cold (or acute bronchitis).\n- If you're a healthy person without underlying heart or lung problems or a weakened immune system, this information is for you.\n- Viruses usually cause chest colds.\n- Antibiotics will not help you feel better if you have a chest cold.\n\nOverview\nAcute bronchitis (often called a “chest cold”) occurs when the airways of the lungs swell and produce mucus (a thick, sticky fluid).\n\nSymptoms\nSymptoms of acute bronchitis last less than 3 weeks and can include:\n- Coughing with or without mucus\n- Feeling tired\n- Swelling of airways in the lungs produce mucus in the lungs and makes you cough.\n- Congestion\n- Sore throat\n- Mild body aches\n\nCauses\nA virus usually causes a chest cold. Bacteria can sometimes cause a chest cold, but even in these cases, antibiotics are NOT recommended and will not help you feel better.\n\nPrevention\nCDC recommends that all people use core prevention strategies. These are important steps you can take to protect yourself and others from respiratory viruses, including those that cause acute bronchitis:\n- Stay up to date with recommended vaccines and boosters, such as the flu vaccine.\n- Practice good hygiene (practices that improve cleanliness).\n  * Cover your coughs and sneezes\n  * Wash or sanitize your hands often\n  * Clean frequently touched surfaces\n- Take steps for cleaner air.\n  * Bring in fresh outside air\n  * Purify indoor air\n  * Gather outdoors\n\nWhen to seek medical care\nSee a healthcare professional if you have any of the following:\n- Fever that lasts longer than 5 days or fever of 104°F or higher\n- Cough with bloody mucus\n- Shortness of breath or trouble breathing\n- Symptoms that last more than 3 weeks\n- Repeated episodes of bronchitis\n\nThis list is not all-inclusive. Please see a healthcare professional for any symptom that is severe or concerning."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Bronchitis.txt",
      "summary": {
        "symptoms": [
          "coughing up mucus, chest pain when coughing and shortness of breath"
        ]
      },
      "evidence_anchor": "chest pain when coughing",
      "query": "Clinical guidance, and diagnostic criteria for: coughing up mucus, chest pain when coughing and shortness of breath.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Chest Cold (Acute Bronchitis).txt",
          "score": 0.77965511204868,
          "survived": true,
          "text": "Chest Cold (Acute Bronchitis) Basics\n\nKEY POINTS\n- Cough keeping you up at night? Congestion? Sore throat? You may have a chest cold (or acute bronchitis).\n- If you're a healthy person without underlying heart or lung problems or a weakened immune system, this information is for you.\n- Viruses usually cause chest colds.\n- Antibiotics will not help you feel better if you have a chest cold.\n\nOverview\nAcute bronchitis (often called a “chest cold”) occurs when the airways of the lungs swell and produce mucus (a thick, sticky fluid).\n\nSymptoms\nSymptoms of acute bronchitis last less than 3 weeks and can include:\n- Coughing with or without mucus\n- Feeling tired\n- Swelling of airways in the lungs produce mucus in the lungs and makes you cough.\n- Congestion\n- Sore throat\n- Mild body aches\n\nCauses\nA virus usually causes a chest cold. Bacteria can sometimes cause a chest cold, but even in these cases, antibiotics are NOT recommended and will not help you feel better.\n\nPrevention\nCDC recommends that all people use core prevention strategies. These are important steps you can take to protect yourself and others from respiratory viruses, including those that cause acute bronchitis:\n- Stay up to date with recommended vaccines and boosters, such as the flu vaccine.\n- Practice good hygiene (practices that improve cleanliness).\n  * Cover your coughs and sneezes\n  * Wash or sanitize your hands often\n  * Clean frequently touched surfaces\n- Take steps for cleaner air.\n  * Bring in fresh outside air\n  * Purify indoor air\n  * Gather outdoors\n\nWhen to seek medical care\nSee a healthcare professional if you have any of the following:\n- Fever that lasts longer than 5 days or fever of 104°F or higher\n- Cough with bloody mucus\n- Shortness of breath or trouble breathing\n- Symptoms that last more than 3 weeks\n- Repeated episodes of bronchitis\n\nThis list is not all-inclusive. Please see a healthcare professional for any symptom that is severe or concerning."
        },
        {
          "file_name": "Bronchitis.txt",
          "score": 0.750677958090428,
          "survived": true,
          "text": "WHEN AND WHERE TO GET MEDICAL HELP:\n- Bronchitis usually gets better on its own, but you may need medical advice if your symptoms do not get any better.\n- You should also get advice if you have a health issue that makes you more vulnerable to bronchitis, like having diabetes.\n\nAsk for an urgent GP appointment or get help if:\n- you've had a cough for more than 3 weeks and it is not getting better\n- you cough up blood or blood-stained mucus\n- you have chest pain that comes and goes, or when breathing or coughing\n- you're over 65\n- you're pregnant\n- you have a long-term condition, such as diabetes, or a heart, lung or kidney condition\n- you have a weakened immune system – for example, you have a condition that affects the immune system, or - you're having chemotherapy\n- you feel too unwell to do usual daily activities\n- you're feeling short of breath\n\n\nCALL EMERGENCY IF:\n- you are struggling to breathe – you are choking, gasping and unable to speak\n- your lips or skin are turning very pale, blue or grey – on brown or black skin this may be easier to see on the palms of the hands, on the lips, tongue or gums, under the nails or around the eyes\n- you suddenly feel confused – for example, you do not know where you are\n- you're unable to wake your baby or they feel floppy\n\n\n\nTREATMENTS FOR BRONCHITIS:\n- Bronchitis usually clears up without treatment in around 3 weeks. See a GP if your symptoms last longer than 3 weeks.\n- Antibiotics may be offered if your bronchitis is caused by a more serious infection.\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/bronchitis/"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Bunions.txt",
      "summary": {
        "symptoms": [
          "hard lump beside the big toe, foot pain worse in shoes"
        ]
      },
      "evidence_anchor": "hard lumps",
      "query": "Clinical guidance, and diagnostic criteria for: hard lump beside the big toe, foot pain worse in shoes.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Bunions.txt",
          "score": 0.762266976427978,
          "survived": true,
          "text": "BUNIONS:\n\nOVERVIEW:\nBunions are bony lumps that form on the side of the feet. Surgery is the only way to get rid of them, but there are things you can do to ease any pain they cause.\n\nSYMPTOMS OF BUNIONS:\n- The main symptoms of bunions are hard lumps on the sides of your feet, by your big toes.\n- Your big toe may point towards your other toes.\n- You may have hard or swollen skin. The bunion may look red or darker than the skin around it.\n- You may also have pain along the side or bottom of your feet. This is usually worse when wearing shoes and walking.\n\n\nHOW TO EASE BUNION PAIN YOURSELF:\n- You cannot get rid of bunions or stop them getting worse yourself, but there are things you can do to ease any pain.\nDo:\n- wear wide shoes with a low heel and soft sole\n- hold an ice pack (or a bag of frozen peas) wrapped in a tea towel to the bunion for up to 5 minutes at a time\n- try bunion pads (soft pads you put in shoes to stop them rubbing on a bunion) – you can buy these from pharmacies\n- take paracetamol or ibuprofen\n- try to lose weight if you're overweight\nDon’t:\n- do not wear high heels or tight, pointy shoes\n\n\nSEE A GP IF:\n- pain from a bunion has not improved after trying home treatments for a few weeks\n- the pain is stopping you doing your normal activities\n- your bunions are getting worse\n- you have bunions and diabetes – foot problems can be more serious if you have diabetes\n\n\nTREATMENTS FOR BUNIONS:\n- If you have bunions, a GP will look at your foot and ask you about your symptoms.\n- They might refer you to a foot specialist (podiatrist).\n- A GP or podiatrist can advise you about:\n  * things you can do to ease your symptoms\n  * things you can buy or have specially made to reduce bunion pain, such as insoles (orthotics), toe spacers and toe supports (splints)\nYou can also pay to see a foot specialist privately."
        },
        {
          "file_name": "Bunions.txt",
          "score": 0.671093264687864,
          "survived": true,
          "text": "SURGERY:\n- A GP may refer you for surgery if your bunions are very painful or they're having a big effect on your life.\n- Surgery is not done just to improve how your feet look.\nWhat happens during bunion surgery:\n- The most common surgery for bunions is an osteotomy.\nThis involves:\n- Making a small cut or cuts in the skin over your big toe.\n- Cutting or scraping away the bunion.\n- Straightening your toe bone.\n- Fixing your toe bone in place with metal screws or staples put under your skin. These are often left in permanently.\nSurgery is usually done when you're asleep under general anaesthetic. But sometimes it may be done under local anaesthetic (where you're awake but feel no pain).\nMost people go home the same day.\nIt can take a while to recover from bunion surgery.\nYou'll usually need to:\n- rest and keep your feet raised as much as possible for at least 2 weeks\n- avoid driving for 6 to 8 weeks\n- stay off work for 2 to 12 weeks\n- avoid sports for 3 to 6 months\nAfter the operation:\n- your toes might be weaker or stiffer than before\n- your toes may not be perfectly straight\n- your feet may still be painful\nBunions sometimes come back after surgery.\n\n\nHOW TO PREVENT BUNIONS:\n- The cause of bunions is not always known, but you may be more likely to get them if you wear shoes that do not fit properly.\nIt might help to:\n- make sure your shoes are the correct size and have enough room for your toes\n- avoid shoes with high heels or pointy toes\n\n\nSOURCE:\nhttps://www.nhs.uk/conditions/bunions/"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Cardiovascular disease.txt",
      "summary": {
        "symptoms": [
          "chest pain in an older adult who smokes and has high blood pressure"
        ]
      },
      "evidence_anchor": "chest pain",
      "query": "Clinical guidance, and diagnostic criteria for: chest pain in an older adult who smokes and has high blood pressure.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Cardiovascular disease.txt",
          "score": 0.708354771137258,
          "survived": true,
          "text": "CARDIOVASCULAR DISEASE:\n\n\nSYMPTOMS OF CARDIOVASCULAR DISEASE:\n- Symptoms of cardiovascular disease will depend on the condition you have. Some conditions may not have any symptoms.\n- For some people, the first sign that they have CVD may be having chest pain (angina), a heart attack or stroke.\n\n\nTYPES OF CARDIOVASCULAR DISEASE:\n- Cardiovascular disease is a name for a group of conditions that affect your heart and blood vessels. There are many different types of CVD.\n\n\nMain types of CARDIOVASCULAR DISEASE:\n- Coronary heart disease (CHD)\n  * The arteries become blocked by a build-up of fat, making it hard for blood to flow to and from your heart.\n- Peripheral arterial disease (PAD)\n  * A build-up of fat in the arteries causes reduced blood flow to the legs and feet.\n- Aortic disease\n  * A group of conditions that affect the aorta (the largest blood vessel in the body). It can lead to an abdominal aortic aneurysm.\n- Stroke\n  * Blood suddenly stops flowing to a part of your brain because of a blockage. This can affect things like speech and movement.\n\n\nWHO'S AT RISK OF CARDIOVASCULAR DISEASE CARDIOVASCULAR DISEASE:\n- Cardiovascular disease (CVD) is often caused by a build-up of fat in the arteries. This makes it hard for blood to flow through your body and can lead to a blood clot.\n- There are things that may make it more likely you'll get CVD, including:\n  * your lifestyle – such as smoking, drinking too much alcohol, being overweight and not being active\n  * your age – CVD mainly affects people over 50 years old\n  * your sex – men are more likely to get CVD than women\n  * your ethnicity – you may be more likely to get CVD if you're from a South Asian, Black African or African Caribbean ethnic background\n  * having family members with CVD\n  * having certain conditions, such as diabetes, high blood pressure or high cholesterol\n\n\nSEE A GP IF:\n- you think you're at higher risk of having or getting cardiovascular disease (CVD)\nReducing your risk of cardiovascular disease (CVD)"
        },
        {
          "file_name": "Chest Cold (Acute Bronchitis).txt",
          "score": 0.676038941864846,
          "survived": true,
          "text": "Chest Cold (Acute Bronchitis) Basics\n\nKEY POINTS\n- Cough keeping you up at night? Congestion? Sore throat? You may have a chest cold (or acute bronchitis).\n- If you're a healthy person without underlying heart or lung problems or a weakened immune system, this information is for you.\n- Viruses usually cause chest colds.\n- Antibiotics will not help you feel better if you have a chest cold.\n\nOverview\nAcute bronchitis (often called a “chest cold”) occurs when the airways of the lungs swell and produce mucus (a thick, sticky fluid).\n\nSymptoms\nSymptoms of acute bronchitis last less than 3 weeks and can include:\n- Coughing with or without mucus\n- Feeling tired\n- Swelling of airways in the lungs produce mucus in the lungs and makes you cough.\n- Congestion\n- Sore throat\n- Mild body aches\n\nCauses\nA virus usually causes a chest cold. Bacteria can sometimes cause a chest cold, but even in these cases, antibiotics are NOT recommended and will not help you feel better.\n\nPrevention\nCDC recommends that all people use core prevention strategies. These are important steps you can take to protect yourself and others from respiratory viruses, including those that cause acute bronchitis:\n- Stay up to date with recommended vaccines and boosters, such as the flu vaccine.\n- Practice good hygiene (practices that improve cleanliness).\n  * Cover your coughs and sneezes\n  * Wash or sanitize your hands often\n  * Clean frequently touched surfaces\n- Take steps for cleaner air.\n  * Bring in fresh outside air\n  * Purify indoor air\n  * Gather outdoors\n\nWhen to seek medical care\nSee a healthcare professional if you have any of the following:\n- Fever that lasts longer than 5 days or fever of 104°F or higher\n- Cough with bloody mucus\n- Shortness of breath or trouble breathing\n- Symptoms that last more than 3 weeks\n- Repeated episodes of bronchitis\n\nThis list is not all-inclusive. Please see a healthcare professional for any symptom that is severe or concerning."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Chest Cold (Acute Bronchitis).txt",
      "summary": {
        "symptoms": [
          "cough with mucus, congestion, sore throat and mild body aches for two weeks"
        ]
      },
      "evidence_anchor": "Mild body aches",
      "query": "Clinical guidance, and diagnostic criteria for: cough with mucus, congestion, sore throat and mild body aches for two weeks.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Chest Cold (Acute Bronchitis).txt",
          "score": 0.775460051027541,
          "survived": true,
          "text": "Chest Cold (Acute Bronchitis) Basics\n\nKEY POINTS\n- Cough keeping you up at night? Congestion? Sore throat? You may have a chest cold (or acute bronchitis).\n- If you're a healthy person without underlying heart or lung problems or a weakened immune system, this information is for you.\n- Viruses usually cause chest colds.\n- Antibiotics will not help you feel better if you have a chest cold.\n\nOverview\nAcute bronchitis (often called a “chest cold”) occurs when the airways of the lungs swell and produce mucus (a thick, sticky fluid).\n\nSymptoms\nSymptoms of acute bronchitis last less than 3 weeks and can include:\n- Coughing with or without mucus\n- Feeling tired\n- Swelling of airways in the lungs produce mucus in the lungs and makes you cough.\n- Congestion\n- Sore throat\n- Mild body aches\n\nCauses\nA virus usually causes a chest cold. Bacteria can sometimes cause a chest cold, but even in these cases, antibiotics are NOT recommended and will not help you feel better.\n\nPrevention\nCDC recommends that all people use core prevention strategies. These are important steps you can take to protect yourself and others from respiratory viruses, including those that cause acute bronchitis:\n- Stay up to date with recommended vaccines and boosters, such as the flu vaccine.\n- Practice good hygiene (practices that improve cleanliness).\n  * Cover your coughs and sneezes\n  * Wash or sanitize your hands often\n  * Clean frequently touched surfaces\n- Take steps for cleaner air.\n  * Bring in fresh outside air\n  * Purify indoor air\n  * Gather outdoors\n\nWhen to seek medical care\nSee a healthcare professional if you have any of the following:\n- Fever that lasts longer than 5 days or fever of 104°F or higher\n- Cough with bloody mucus\n- Shortness of breath or trouble breathing\n- Symptoms that last more than 3 weeks\n- Repeated episodes of bronchitis\n\nThis list is not all-inclusive. Please see a healthcare professional for any symptom that is severe or concerning."
        },
        {
          "file_name": "Cold.txt",
          "score": 0.764067874197239,
          "survived": true,
          "text": "Preventing and Managing the Common Cold\n\nAre you sneezing, or do you have a stuffy and runny nose? You might have a cold. Antibiotics do not work against viruses that cause colds and will not help you feel better.\n\nWhat is Common Cold?\nA common cold is a mild upper respiratory illness caused by a virus that resolves in a short period of time. Colds can have similar symptoms to flu. It can be difficult (or even impossible) to tell the difference between them based on symptoms alone.\n\nSymptoms\nSymptoms of a cold usually peak within 2 to 3 days, though some (especially runny nose and cough) can last up to 10–14 days. Symptoms can include:\n- Sneezing\n- Nasal congestion\n- Sore throat\n- Cough\n- Fever (although most people with colds do not have fever)\n- Mucus\n  * Clear mucus helps wash viruses from the nose and sinuses\n  * Mucus may change to a white, yellow, or green color after 2–3 days, this is normal\n\nCauses\nMore than 200 viruses can cause a cold, but rhinoviruses are the most common type. Viruses that cause colds can spread from person to person through the air and close personal contact.\n\nWhen to Seek Medical Care*\nSee a healthcare professional if you have:\n- Trouble breathing or fast breathing\n- Dehydration\n- Fever that lasts longer than 4 days\n- Symptoms that last more than 10 days without improvement\n- Symptoms, such as fever or cough, that improve but then return or worsen\n- Worsening of chronic medical conditions\n\n*This list is not all-inclusive. Please see a healthcare professional for any symptom that is severe or concerning.\nTalk to a healthcare professional right away if your child is under 3 months old with a fever of 100.4 °F (38 °C) or higher.\n\nTreatment\nThere is no cure for a cold. It will get better on its own—without antibiotics. Antibiotics won’t help you get better if you have a cold."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Chickenpox (Varicella).txt",
      "summary": {
        "symptoms": [
          "itchy blisters spreading from the chest and back, with spots at different stages"
        ]
      },
      "evidence_anchor": "all stages of development",
      "query": "Clinical guidance, and diagnostic criteria for: itchy blisters spreading from the chest and back, with spots at different stages.",
      "indexed_chunks": 5,
      "candidates": [
        {
          "file_name": "Psoriasis.txt",
          "score": 0.6812679361541321,
          "survived": true,
          "text": "PSORIASIS:\n\n\nOVERVIEW:\n- Psoriasis is a common skin condition that causes itchy and painful patches of dry, flaky skin. It cannot be cured, but there are treatments to help manage your symptoms.\n\n\nSYMPTOMS OF PSORIASIS:\nThe main symptom of psoriasis is dry, itchy, sore, flaky patches of skin that form what look like silvery-white scales.\n\nPSORIASIS PATCHES ARE USUALLY:\n- 1 to 2cm in size\n- an oval or irregular shape.\n- pink or red on white skin, turning silvery-white, and can sometimes turn a waxy yellow or - orange-brown colour\n- grey on brown or black skin, and cause dark marks on the skin after the psoriasis has gone\n- Most people only get a few psoriasis patches, but others get them across large parts of their body. Some people have lots of smaller, scaly patches.\n\n\nYou may also get lots of small brown and yellow spots on the palms of your hands and soles of your feet.\n\nYou can get psoriasis in different parts of your body, but it's mostly found on the:\n- head and behind the ears\n- chest, tummy and back\n- bottom\n- forearms and elbows\n- lower legs and knees\n- You can also get it in the folds of your body, such as your groin, genitals and under your breasts, or on your fingernails. The surface of your nails can have dents and pits.\n\nYou can get psoriasis at any age, but symptoms often start either between the ages of 15 and 25, or 50 and 60 .\n\nThere are usually times where your symptoms get worse (called flare-ups) and times when they're better.\n\n\nSEE A GP IF:\n- you have symptoms of psoriasis\n- you have psoriasis and your treatment is not working or is giving you side effects\n- you have psoriasis and also have pain, stiffness and swelling in your joints that keeps coming back"
        },
        {
          "file_name": "Cold sore.txt",
          "score": 0.654008865356445,
          "survived": false,
          "text": "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear."
        }
      ],
      "retrieved": false,
      "error": null
    },
    {
      "expected_document": "Coeliac disease.txt",
      "summary": {
        "symptoms": [
          "bloating and diarrhoea after eating gluten"
        ]
      },
      "evidence_anchor": "bloating",
      "query": "Clinical guidance, and diagnostic criteria for: bloating and diarrhoea after eating gluten.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Coeliac disease.txt",
          "score": 0.7730585336685181,
          "survived": true,
          "text": "COELIAC DISEASE:\n\nOVERVIEW:\n- Coeliac disease is a condition where your immune system attacks your own tissues when you eat gluten. This damages your gut (small intestine) so your body cannot properly take in nutrients.\n- Coeliac disease can cause a range of symptoms, including diarrhoea, abdominal pain and bloating.\n- Coeliac disease is caused by an adverse reaction to gluten, which is a dietary protein found in 3 types of cereal:\n  * wheat\n  * barley\n  * rye\nGluten is found in any food that contains those cereals, including:\n  * pasta\n  * cakes\n  * breakfast cereals\n  * most types of bread\n  * certain types of sauces\n  * some ready meals\nIn addition, most beers are made with barley.\n\n\nSYMPTOMS OF COELIAC DISEASE:\nEating foods that contain gluten can trigger a range of gut symptoms, such as:\n  * diarrhoea, which may smell particularly unpleasant\n  * stomach aches\n  * bloating and farting (flatulence)\n  * indigestion\n  * constipation\nCoeliac disease can also cause more general symptoms, including:\n  * tiredness (fatigue) as a result of not getting enough nutrients from food (malnutrition)\n  * unintentional weight loss\n  * an itchy rash (dermatitis herpetiformis)\n  * problems getting pregnant (infertility)\n  * nerve damage (peripheral neuropathy)\n  * disorders that affect co-ordination, balance and speech (ataxia)\nChildren with coeliac disease may not grow at the expected rate and may have delayed puberty.\n\n\nWHAT CAUSES COELIAC DISEASE?\n- Coeliac disease is an autoimmune condition. This is where the immune system (the body's defence against infection) mistakenly attacks healthy tissue.\n- In coeliac disease, the immune system mistakes substances found inside gluten as a threat to the body and attacks them.\n- This damages the surface of the small bowel (intestines), disrupting the body's ability to take in nutrients from food.\n- It's not entirely clear what causes the immune system to act this way, but a combination of genetics and the environment appear to play a part."
        },
        {
          "file_name": "Coeliac disease.txt",
          "score": 0.752021670341492,
          "survived": true,
          "text": "TREATING COELIAC DISEASE:\n- There's no cure for coeliac disease, but following a gluten-free diet should help control symptoms and prevent the long-term complications of the condition.\n- Even if you have mild symptoms, changing your diet is still recommended because continuing to eat gluten can lead to serious complications. This may also be the case if tests show that you have some degree of coeliac disease even if you do not have noticeable symptoms.\n- It's important to ensure that your gluten-free diet is healthy and balanced.\n- An increase in the range of available gluten-free foods in recent years has made it possible to eat both a healthy and varied gluten-free diet.\n\n\nCOMPLICATIONS OF COELIAC DISEASE:\n- Complications of coeliac disease only tend to affect people who continue to eat gluten, or those who have not yet been diagnosed with the condition, which can be a common problem in milder cases.\n- Potential long-term complications include:\n  * weakening of the bones (osteoporosis)\n  * iron deficiency anaemia\n  * vitamin B12 or folate deficiency anaemia\n- Less common and more serious complications include some types of cancers, such as bowel cancer, and problems affecting pregnancy, such as your baby having a low birth weight.\n\n\nWHO'S AFFECTED:\n- Coeliac disease is a condition that affects at least 1 in every 100 people in the UK.\n- But some experts think this may be underestimated because milder cases may go undiagnosed or be misdiagnosed as other digestive conditions, such as irritable bowel syndrome (IBS).\n- Reported cases of coeliac disease are higher in women than men.\n- It can develop at any age.\n- People with certain conditions, including type 1 diabetes, autoimmune thyroid disease, Down's syndrome and Turner syndrome, have an increased risk of getting coeliac disease.\n- First-degree relatives (parents, brothers, sisters and children) of people with coeliac disease are also at increased risk of developing the condition."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Cold sore.txt",
      "summary": {
        "symptoms": [
          "tingling lip followed by small fluid-filled blisters"
        ]
      },
      "evidence_anchor": "tingling",
      "query": "Clinical guidance, and diagnostic criteria for: tingling lip followed by small fluid-filled blisters.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Cold sore.txt",
          "score": 0.679883480072021,
          "survived": true,
          "text": "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear."
        },
        {
          "file_name": "Appendicitis.txt",
          "score": 0.6489933729171751,
          "survived": false,
          "text": "GO TO A&E IF:\nYou or your child have:\n- severe pain in your abdomen (tummy)\n- confusion, blotchy or paler than usual skin (on brown or black skin this may be easier to see on the palms of the hands or soles of the feet) or difficulty breathing – these could be signs of sepsis\n\n\nHOW APPENDICITIS IS DIAGNOSED:\n- If you have symptoms of appendicitis, a GP or hospital doctor will feel your abdomen (tummy) to check for pain and swelling.\n- You'll need to go to hospital for tests and treatment. Tests you may have include:\n  * blood tests\n  * testing a sample of your pee\n  * scans such as an ultrasound scan or CT scan to check for swelling in your appendix\n  * a pregnancy test if there's a chance you could be pregnant\n- There's no test that can always show if you have appendicitis. It can be hard to diagnose because the symptoms can be similar to other conditions. Sometimes doctors will try waiting a few hours to see how your symptoms develop in hospital.\n- If your symptoms mean it's very likely you have appendicitis, or if your appendix may have burst, doctors may recommend surgery instead of waiting for more tests."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Cold.txt",
      "summary": {
        "symptoms": [
          "sneezing, blocked nose and sore throat for three days"
        ]
      },
      "evidence_anchor": "Sneezing",
      "query": "Clinical guidance, and diagnostic criteria for: sneezing, blocked nose and sore throat for three days.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Cold.txt",
          "score": 0.743818186039275,
          "survived": true,
          "text": "Preventing and Managing the Common Cold\n\nAre you sneezing, or do you have a stuffy and runny nose? You might have a cold. Antibiotics do not work against viruses that cause colds and will not help you feel better.\n\nWhat is Common Cold?\nA common cold is a mild upper respiratory illness caused by a virus that resolves in a short period of time. Colds can have similar symptoms to flu. It can be difficult (or even impossible) to tell the difference between them based on symptoms alone.\n\nSymptoms\nSymptoms of a cold usually peak within 2 to 3 days, though some (especially runny nose and cough) can last up to 10–14 days. Symptoms can include:\n- Sneezing\n- Nasal congestion\n- Sore throat\n- Cough\n- Fever (although most people with colds do not have fever)\n- Mucus\n  * Clear mucus helps wash viruses from the nose and sinuses\n  * Mucus may change to a white, yellow, or green color after 2–3 days, this is normal\n\nCauses\nMore than 200 viruses can cause a cold, but rhinoviruses are the most common type. Viruses that cause colds can spread from person to person through the air and close personal contact.\n\nWhen to Seek Medical Care*\nSee a healthcare professional if you have:\n- Trouble breathing or fast breathing\n- Dehydration\n- Fever that lasts longer than 4 days\n- Symptoms that last more than 10 days without improvement\n- Symptoms, such as fever or cough, that improve but then return or worsen\n- Worsening of chronic medical conditions\n\n*This list is not all-inclusive. Please see a healthcare professional for any symptom that is severe or concerning.\nTalk to a healthcare professional right away if your child is under 3 months old with a fever of 100.4 °F (38 °C) or higher.\n\nTreatment\nThere is no cure for a cold. It will get better on its own—without antibiotics. Antibiotics won’t help you get better if you have a cold."
        },
        {
          "file_name": "Influenza.txt",
          "score": 0.704772707393233,
          "survived": true,
          "text": "This includes people 65 years and older, people of any age with certain chronic medical conditions (such as asthma, diabetes, or heart disease), pregnant women and children younger than 5 years, but especially those younger than 2 years old.\n\nCold versus flu\n\n| Signs and Symptoms | Cold | Influenza (Flu) |\n| --- | --- | --- |\n| Symptom onset | Gradual | Abrupt |\n| Fever | Rare | Common; lasts 3-4 days |\n| Aches | Slight | Common; often severe |\n| Chills | Uncommon | Fairly common |\n| Fatigue, weakness | Sometimes | Usual |\n| Sneezing | Common | Sometimes |\n| Chest discomfort, cough | Mild to moderate; hacking cough | Common; can be severe |\n| Stuffy nose | Common | Sometimes |\n| Sore throat | Common | Sometimes |\n| Headache | Rare | Common |\n\nSources\nhttps://www.cdc.gov/flu/signs-symptoms/index.html"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Covid 19.txt",
      "summary": {
        "symptoms": [
          "new continuous cough, fever and loss of smell and taste"
        ]
      },
      "evidence_anchor": "sense of smell or taste",
      "query": "Clinical guidance, and diagnostic criteria for: new continuous cough, fever and loss of smell and taste.",
      "indexed_chunks": 4,
      "candidates": [
        {
          "file_name": "Covid 19.txt",
          "score": 0.669220169233075,
          "survived": false,
          "text": "COVID 19:\n\n\nSYMPTOMS OF COVID-19:\nCOVID-19 symptoms can include:\r- a high temperature – you may feel hot, cold or shivery, or your skin is hot to touch onyour chest or back (you do not need to measure your temperature)\r- a new, continuous cough – this means coughing a lot for more than an hour, or 3 or morecoughing episodes in 24 hours\r- a loss or change to your sense of smell or taste\rshortness of breath\r- feeling tired or exhausted\r- an aching body\r- a headache\r- a sore throat\r- a blocked or runny nose\r- loss of appetite\r- diarrhoea\r- feeling sick or being sick\rThe symptoms are very similar to symptoms of other illnesses, such as colds and flu.\rMost people feel better within a few weeks, but it can take longer to recover.\rFor some people, it can be a more serious illness and their symptoms can last longer.\n\n\n\rWHAT TO DO IF YOU HAVE SYMPTOMS OF COVID-19:\rTry to stay at home and avoid contact with other people if you or your child have symptomsand either:\r- have a high temperature\r- do not feel well enough to go to work, school, childcare, or do your normal activities\rYou can go back to your normal activities when you feel better or do not have a hightemperature.\rIf your child has mild symptoms such as a runny nose, sore throat or mild cough, and theyfeel well enough, they can go to school or childcare.\n\n\n\rIF YOU TEST POSITIVE FOR COVID-19:\rMost people do not need to take a\rCOVID-19 rapid lateral flow test (Link: www.nhs.uk/testsand-\rtreatments/covid-19-rapid-lateral-flow-test/)\rif they have symptoms."
        },
        {
          "file_name": "Covid 19.txt",
          "score": 0.668140013924837,
          "survived": false,
          "text": "ASK FOR AN URGENT GP APPOINTMENT:\r- you're worried about your or a child's COVID-19 symptoms or are not sure whatto do\r- the symptoms are getting worse or are not getting better\r- you or a child have other signs of illness, such as a rash, loss of appetite, or feeling weak\r- you or a child have a high temperature that last 5 days or more or does notcome down with paracetamol\r- a child under 3 months old and has a temperature of 38C or higher, or youthink they have a high temperature\r- a child 3 to 6 months old and has a temperature of 39C or higher, or you thinkthey have a high temperature\rIt's particularly important to get help if you're at increased risk of getting ill fromCOVID-19, such as if you're pregnant, aged 60 or over, or have a weakenedimmune system.\r\r\rSOURCES:\nhttps://www.nhs.uk/conditions/covid-19/covid-19-symptoms-and-what-to-do/"
        }
      ],
      "retrieved": false,
      "error": null
    },
    {
      "expected_document": "Dehydration.txt",
      "summary": {
        "symptoms": [
          "thirst, dark yellow urine and dizziness"
        ]
      },
      "evidence_anchor": "dark yellow",
      "query": "Clinical guidance, and diagnostic criteria for: thirst, dark yellow urine and dizziness.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Dehydration.txt",
          "score": 0.738080636377298,
          "survived": true,
          "text": "ASK FOR AN URGENT GP APPOINTMENT IF:\n- you're feeling unusually tired (or your child seems drowsy)\n- you feel dizzy when you stand up and it does not go away\n- you have dark yellow pee or you're peeing less than normal (or your baby has fewer wet nappies)\n- you or your child are breathing quickly or have a fast heart rate\n- your baby or child have few or no tears when they cry\n- your baby has a soft spot on their head that sinks inwards (sunken fontanelle)\nThese can be signs of serious dehydration that need urgent treatment.\n\n\nGO TO ACCIDENT AND EMERGENCY IF:\nYou or somebody else has signs of dehydration and:\n- blue, grey, pale or blotchy skin, lips or tongue – on brown or black skin, this may be easier to see on the palms of the hands or soles of the feet\n- skin that feels cold\n- difficulty breathing, or is taking lots of quick breaths\n- are confused\n- are sleepier than normal or difficult to wake\nThese could be signs of shock, which is a serious complication of dehydration.\n\n\nHOW TO REDUCE THE RISK OF DEHYDRATION:\n- Drinking fluids regularly can reduce the risk of dehydration. Water or diluted sugar-free squash are good choices.\n- You should drink enough during the day so that your pee is a pale colour.\n- Drink more when there's a higher risk of dehydrating. For example, if you're being sick, sweating due to hot weather or exercise, or you have diarrhoea.\n- Children under the age of 5 and older adults should get plenty of fluids as they have an increased risk of dehydration.\n\n\nHELPING SOMEONE YOU CARE FOR:\nA person you care for may not have a sense of how much they're drinking.\n\nYou can help them by:\n- making sure they drink at mealtimes\n- making drinking a social thing\n- offering them food with a high water content – for example, soup, ice cream, jelly and fruits like melon\n\nSOURCES:\nhttps://www.nhs.uk/conditions/dehydration/"
        },
        {
          "file_name": "Dehydration.txt",
          "score": 0.723420457636092,
          "survived": true,
          "text": "DEHYDRATION:\n\n\nSYMPTOMS OF DEHYDRATION:\nSymptoms of dehydration in adults and children include:\n- feeling thirsty\n- headache and feeling light-headed\n- dark yellow, strong-smelling pee\n- peeing less often than usual\n- feeling dizzy or lightheaded\n- feeling tired\n- a dry mouth, lips and tongue\n- sunken eyes\nSigns of dehydration in a baby may include:\n- a sunken soft spot (fontanelle) on top of their head\n- sunken eyes\n- few or no tears when they cry\n- fewer wet nappies than usual\n- being drowsy or irritable\n\n\nCAUSES OF DEHYDRATION:\nDehydration can happen more easily if you:\n- have diabetes\n-have been sick or have diarrhoea\n-have been in the sun, or a hot environment, too long (heatstroke)\n-have drunk too much alcohol\n-sweat a lot after exercising\n-have a high temperature\n-take medicines that make you pee more (diuretics)\n-rely on other people to get you drinks\n\n\nTHINGS YOU CAN DO TO TREAT DEHYDRATION:\n- You should drink fluids if you have symptoms of dehydration.\n- If you feel sick or have been sick, you may find it hard to drink, so start with small sips and then gradually drink more. Avoid caffeinated drinks and alcohol as both will dehydrate you.\n- A pharmacist can help with dehydration:\n  * If you're being sick or have diarrhoea and are losing too much fluid, you need to put back the sugar, salts and minerals your body has lost.\n  * A pharmacist can recommend oral rehydration solutions. These are powders that you mix with water and then drink.\n  * Ask your pharmacist which rehydration solutions are right for you or your child."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Ear Infection.txt",
      "summary": {
        "symptoms": [
          "child with ear pain, fever, tugging at an ear and difficulty sleeping"
        ]
      },
      "evidence_anchor": "tugging at an ear",
      "query": "Clinical guidance, and diagnostic criteria for: child with ear pain, fever, tugging at an ear and difficulty sleeping.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Ear Infection.txt",
          "score": 0.796387958311318,
          "survived": true,
          "text": "Preventing and Treating Ear Infections\n\nIs your child’s ear hurting? It could be an ear infection. Children are more likely than adults to get ear infections. Talk to your child’s doctor about the best treatment. \nSome ear infections, such as middle ear infections, need antibiotic treatment, but many can get better on their own without antibiotics.\n\nWhat is an ear infection?\nThere are different types of ear infections. Middle ear infection (acute otitis media) is an infection in the middle ear. \nAnother condition that affects the middle ear is called otitis media with effusion. It occurs when fluid builds up in the middle ear without being infected and without causing fever, ear pain, or pus buildup in the middle ear.\nWhen the outer ear canal is infected, the condition is called “swimmer’s ear,” which is different from a middle ear infection. \n\nCauses \nMiddle ear infections can be caused by: \n- Bacteria, like Streptococcus pneumoniae and Haemophilus influenzae (nontypeable)—the two most common bacterial causes.\n- Viruses, like those that cause colds or flu.\n\nSymptoms\nCommon symptoms of middle ear infection in children can include:\n- Ear pain.\n- Fever.\n- Fussiness or irritability.\n- Rubbing or tugging at an ear.\n- Difficulty sleeping.\n\nWhen to Seek Medical Care\nSee a doctor if your child has:\n- A fever of 102.2°F (39°C) or higher.\n- Pus, discharge, or fluid coming from the ear.\n- Worsening symptoms.\n- Symptoms of a middle ear infection that last for more than 2–3 days.\n- Hearing loss.\n\nPediatric Warning:\nSee a doctor right away if your child is younger than 3 months old and has a fever greater than 100.4 °F (38 °C). \n\nTreatment\nA doctor will determine what type of illness your child has by asking about symptoms and doing a physical examination. Your doctor can make the diagnosis of a middle ear infection by looking inside your child’s ear to examine the eardrum and see if there is pus in the middle ear. \nAntibiotics are often not needed for middle ear infections because the body’s immune system can fight off the infection on its own."
        },
        {
          "file_name": "Ear Infection.txt",
          "score": 0.7221194936108299,
          "survived": true,
          "text": "Antibiotics are often not needed for middle ear infections because the body’s immune system can fight off the infection on its own. But sometimes antibiotics, such as amoxicillin, are needed to treat infants, severe cases, or cases that last longer than 2–3 days.\nFor mild cases of middle ear infection, your doctor might recommend watchful waiting or delayed antibiotic prescribing. \n\nWatchful waiting: Your child’s doctor may suggest watching and waiting to see if your child needs antibiotics. This gives the immune system time to fight off the infection. If your child doesn’t feel better after 2–3 days of rest, extra fluids, and pain relievers, the doctor will write a prescription for an antibiotic.\n\nDelayed prescribing: Your child’s doctor may give an antibiotic prescription but will suggest that you wait 2–3 days to see if your child is still sick before filling it. \n\nHow to Feel Better \nSome ways to feel better—whether or not antibiotics are needed for an ear infection: \n- Rest.\n- Drink extra water or other fluids.\n- Take acetaminophen or ibuprofen to relieve pain or fever. Ask your doctor or pharmacist what medications are safe for your child to take and what dose to give your child.\n\nOver-the-Counter Medicine and Children\nBe careful about giving over-the-counter medicines to children. Not all over-the-counter medicines are recommended for children of certain ages. \n\nPain relievers: \n- Children younger than 6 months: only give acetaminophen. \n- Children 6 months or older: it is OK to give acetaminophen or ibuprofen. \n- Never give aspirin to children because it can cause Reye’s syndrome, a rare but very serious illness that harms the liver and brain.\n\nBe sure to ask your doctor or pharmacist about the right dosage of over-the-counter medicines for your child’s age and size. Also, tell your child’s doctor and pharmacist about all the prescription and over-the-counter medicines they are taking.\n\nPrevention\nYou can help prevent ear infections by doing your best to stay healthy and keep others healthy.\n- Make sure your child is up to date on vaccinations and gets a flu vaccine every year. The pneumococcal vaccine protects against Streptococcus pneumoniae, a common cause of middle ear infections.\n- Clean your hands."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Food poisoning.txt",
      "summary": {
        "symptoms": [
          "vomiting, diarrhoea and tummy pain beginning after a meal"
        ]
      },
      "evidence_anchor": "eating food",
      "query": "Clinical guidance, and diagnostic criteria for: vomiting, diarrhoea and tummy pain beginning after a meal.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Food poisoning.txt",
          "score": 0.768563999619247,
          "survived": true,
          "text": "FOOD POISONING:\n\nFood poisoning is rarely serious and usually gets better within a week. You can normally treat yourself or your child at home.\n\nSYMPTOMS OF FOOD POISONING:\n- feeling sick or being sick\n- diarrhoea\n- tummy pain\n- a high temperature\n- feeling generally unwell\nThe symptoms usually start within a few hours or a few days of eating food that caused the infection.\nSometimes symptoms do not start for a few weeks.\n\nHOW TO TREAT FOOD POISONING YOURSELF:\nIf you or your child have food poisoning, you can usually treat it at home.\nThe symptoms usually get better within a week.\nDiarrhoea and vomiting can usually be treated at home. The most important thing is to have lots of fluids to avoid dehydration.\n\nDO:\n- stay at home and get plenty of rest\n- drink lots of fluids, such as water or squash – take small sips if you feel sick\n- carry on breast or bottle feeding your baby – if they're being sick, try giving small feeds more often than usual\n- give babies on formula or solid foods small sips of water between feeds\n- eat when you feel able to – it may help to avoid foods that are fatty or spicy\n- take paracetamol if you're in discomfort – check the leaflet before giving it to your child\n\nDON’T:\n- do not have fruit juice or fizzy drinks – they can make diarrhoea worse\n- do not make baby formula weaker – use it at its usual strength\n- do not give children under 12 medicine to stop diarrhoea\n- do not give aspirin to children under 16\n\nA PHARMACIST CAN HELP WITH FOOD POISONING, SPEAK TO A PHARMACIST IF:\n- you or your child (over 5 years) have signs of dehydration, such as dark, smelly pee or peeing less than usual\n- you're an older person, have a weakened immune system, or have other health conditions that increase your risk of dehydration\n- you need to stop diarrhoea for a few hours\n- They may recommend:\n  * oral rehydration powder that you mix with water to make a drink\nmedicine to stop diarrhoea for a few hours, like loperamide (not suitable for children under 12)"
        },
        {
          "file_name": "Food poisoning.txt",
          "score": 0.760114758001004,
          "survived": true,
          "text": "CALL EMERGENCY NOW IF:\n- you're worried about a baby under 12 months\n- your child stops breast or bottle feeding while they're ill\n- a child under 5 years has signs of dehydration, such as fewer wet nappies\n- you or your child (aged 5 years or over) still have signs of dehydration after using oral rehydration sachets\n- you or your child keep being sick and cannot keep fluid down\n- you or your child have bloody diarrhoea or bleeding from the bottom\n- you or your child have diarrhoea for more than 7 days or vomiting for more than 2 days\n- vomit blood or have vomit that looks like ground coffee\n- have green vomit (adults)\n- have yellow-green or green vomit (children)\n- may have swallowed something poisonous\n- have a stiff neck and pain when looking at bright lights\n- have a sudden, severe headache\n- have a sudden, severe tummy ache\n- have blue, grey, pale or blotchy skin, lips or tongue - on brown or black skin this may be easier to see on the palms of the hands or soles of the feet\n- are having severe difficulty breathing, or taking lots of quick, short breaths\n- are confused or not responding as usual\n- What we mean by severe pain\n- Severe pain:\t\n  * always there and so bad it's hard to think or talk\n  * you cannot sleep\n  * it's very hard to move, get out of bed, go to the bathroom, wash or dress\n- Moderate pain:\t\n  * always there\n  * makes it hard to concentrate or sleep\n  * you can manage to get up, wash or dress\n- Mild pain:\t\n  * comes and goes\n  * is annoying but does not stop you doing daily activities\n\nHOW YOU GET FOOD POISONING:\nFood poisoning is caused by eating something that has been contaminated with germs.\nThis can happen if food is:\n- not cooked or reheated thoroughly\n- not stored correctly – for example, it's not been frozen or chilled\n- left out for too long\n- handled by someone who's ill or has not washed their hands\n- eaten after its \"use by\" date\n- Any type of food can cause food poisoning."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Heartburn and acid reflux.txt",
      "summary": {
        "symptoms": [
          "burning sensation in the chest and sour taste in the mouth after eating"
        ]
      },
      "evidence_anchor": "sour taste",
      "query": "Clinical guidance, and diagnostic criteria for: burning sensation in the chest and sour taste in the mouth after eating.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Heartburn and acid reflux.txt",
          "score": 0.777507222369101,
          "survived": true,
          "text": "HEARTBURN AND ACID REFLUX:\n\nOVERVIEW:\nHeartburn is a burning feeling in the chest caused by stomach acid travelling up towards the throat (acid reflux). If it keeps happening, it may be called gastro-oesophageal reflux disease (GORD).\n\n\nSYMPTOMS OF ACID REFLUX:\n- heartburn, a burning sensation in the middle of your chest\nan unpleasant sour taste in your mouth, caused by stomach acid\n- a cough or hiccups that keep coming back\n- a hoarse voice\n- bad breath\n- bloating and feeling sick\nSymptoms are often worse after eating, when lying down and when bending over.\n\n\nCAUSES OF HEARTBURN AND ACID REFLUX\n- Lots of people get heartburn from time to time. There's often no obvious reason why.\n- Sometimes it's caused or made worse by:\n  * certain food and drink – such as coffee, tomatoes, alcohol, chocolate and fatty or spicy foods\n  * being overweight\n  * smoking\n  * pregnancy - find out more about indigestion and heartburn in pregnancy\nstress and anxiety\n  * an increase in some types of hormones, such as progesterone and oestrogen\nsome medicines, such as anti-inflammatory painkillers (like ibuprofen)\n  * a hiatus hernia – when part of your stomach moves up into your chest\n  * a stomach ulcer\n  * a bacterial infection in your stomach\n\n\nHOW YOU CAN EASE HEARTBURN AND ACID REFLUX YOURSELF:\nSimple lifestyle changes can help stop or reduce heartburn.\n\nDo:\n- eat smaller, more frequent meals\n- try to lose weight if you're overweight\n- try to find ways to relax\n\nDon’t:\n- do not have food or drink that triggers your symptoms\n- do not eat within 3 or 4 hours before bed\n- do not wear clothes that are tight around your waist\n- do not smoke\n- do not drink too much alcohol\n- do not stop taking any prescribed medicine without speaking to a doctor first"
        },
        {
          "file_name": "Heartburn and acid reflux.txt",
          "score": 0.678005279124255,
          "survived": true,
          "text": "IMPORTANT:\n- If a PPI does not help, your doctor may suggest trying a different type of medicine called an H2 receptor antagonist, such as famotidine.\n\n\nTESTS AND TREATMENTS FOR SEVERE HEARTBURN AND ACID REFLUX:\nIf medicines do not help or your symptoms are severe, a GP may refer you to a specialist for:\n- tests to find out what's causing your symptoms, such as a gastroscopy (where a thin tube with a camera inside it is passed down your throat and into your stomach)\n- tests to check for bacteria that can cause heartburn – this can be treated with a combination of - antibiotics and PPIs\n- surgery on your stomach or food pipe (oesophagus) to stop acid reflux\n\n\n\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/heartburn-and-acid-reflux/"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Influenza.txt",
      "summary": {
        "symptoms": [
          "sudden fever, chills, body aches, headache and cough"
        ]
      },
      "evidence_anchor": "come on suddenly",
      "query": "Clinical guidance, and diagnostic criteria for: sudden fever, chills, body aches, headache and cough.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Cold.txt",
          "score": 0.730168662374278,
          "survived": true,
          "text": "Preventing and Managing the Common Cold\n\nAre you sneezing, or do you have a stuffy and runny nose? You might have a cold. Antibiotics do not work against viruses that cause colds and will not help you feel better.\n\nWhat is Common Cold?\nA common cold is a mild upper respiratory illness caused by a virus that resolves in a short period of time. Colds can have similar symptoms to flu. It can be difficult (or even impossible) to tell the difference between them based on symptoms alone.\n\nSymptoms\nSymptoms of a cold usually peak within 2 to 3 days, though some (especially runny nose and cough) can last up to 10–14 days. Symptoms can include:\n- Sneezing\n- Nasal congestion\n- Sore throat\n- Cough\n- Fever (although most people with colds do not have fever)\n- Mucus\n  * Clear mucus helps wash viruses from the nose and sinuses\n  * Mucus may change to a white, yellow, or green color after 2–3 days, this is normal\n\nCauses\nMore than 200 viruses can cause a cold, but rhinoviruses are the most common type. Viruses that cause colds can spread from person to person through the air and close personal contact.\n\nWhen to Seek Medical Care*\nSee a healthcare professional if you have:\n- Trouble breathing or fast breathing\n- Dehydration\n- Fever that lasts longer than 4 days\n- Symptoms that last more than 10 days without improvement\n- Symptoms, such as fever or cough, that improve but then return or worsen\n- Worsening of chronic medical conditions\n\n*This list is not all-inclusive. Please see a healthcare professional for any symptom that is severe or concerning.\nTalk to a healthcare professional right away if your child is under 3 months old with a fever of 100.4 °F (38 °C) or higher.\n\nTreatment\nThere is no cure for a cold. It will get better on its own—without antibiotics. Antibiotics won’t help you get better if you have a cold."
        },
        {
          "file_name": "Influenza.txt",
          "score": 0.7283167187884481,
          "survived": true,
          "text": "This includes people 65 years and older, people of any age with certain chronic medical conditions (such as asthma, diabetes, or heart disease), pregnant women and children younger than 5 years, but especially those younger than 2 years old.\n\nCold versus flu\n\n| Signs and Symptoms | Cold | Influenza (Flu) |\n| --- | --- | --- |\n| Symptom onset | Gradual | Abrupt |\n| Fever | Rare | Common; lasts 3-4 days |\n| Aches | Slight | Common; often severe |\n| Chills | Uncommon | Fairly common |\n| Fatigue, weakness | Sometimes | Usual |\n| Sneezing | Common | Sometimes |\n| Chest discomfort, cough | Mild to moderate; hacking cough | Common; can be severe |\n| Stuffy nose | Common | Sometimes |\n| Sore throat | Common | Sometimes |\n| Headache | Rare | Common |\n\nSources\nhttps://www.cdc.gov/flu/signs-symptoms/index.html"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Insomnia.txt",
      "summary": {
        "symptoms": [
          "difficulty falling asleep and waking during the night for two weeks"
        ]
      },
      "evidence_anchor": "find it hard to go to sleep",
      "query": "Clinical guidance, and diagnostic criteria for: difficulty falling asleep and waking during the night for two weeks.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Insomnia.txt",
          "score": 0.707118889901605,
          "survived": true,
          "text": "SEE A GP IF:\n- changing your sleeping habits has not helped your insomnia\n- you've had trouble sleeping for months\n- your insomnia is affecting your daily life in a way that makes it hard for you to cope\n\n\nTREATMENT FROM A GP FOR INSOMNIA:\n- A GP will try to find out what's causing your insomnia so you get the right treatment.\n- Sometimes you'll be offered cognitive behavioural therapy (CBT). This may be face-to-face with a therapist, or through an online self-help programme.\n- This can help you change the thoughts and behaviours that keep you from sleeping.\n- You may be referred to a sleep clinic if you have symptoms of another sleep disorder such as sleep apnoea.\n- GPs now rarely prescribe sleeping pills to treat insomnia. Sleeping pills can have serious side effects and you can become dependent on them.\n- Sleeping pills are only prescribed for a few days, or weeks at the most, if:\n  * your insomnia is very bad\n  * other treatments have not worked\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/insomnia/"
        },
        {
          "file_name": "Insomnia.txt",
          "score": 0.707093477249146,
          "survived": true,
          "text": "INSOMNIA:\n\n\nOVERVIEW:\n- Insomnia means you regularly have problems sleeping. It usually gets better by changing your sleeping habits.\n\n\nSYMPTOMS:\nYou have insomnia if you regularly:\n- find it hard to go to sleep\n- wake up several times during the night\n- lie awake at night\n- wake up early and cannot go back to sleep\n- still feel tired after waking up\n- find it hard to nap during the day even though you're tired\n- feel tired and irritable during the day\n- find it difficult to concentrate during the day because you're tired\nIf you have insomnia for a short time (less than 3 months) it's called short-term insomnia. Insomnia that lasts 3 months or longer is called long-term insomnia.\n\n\nHOW MUCH SLEEP YOU NEED:\nEveryone needs different amounts of sleep.\nOn average:\n- adults need 7 to 9 hours\n- children need 9 to 13 hours\n- toddlers and babies need 12 to 17 hours\nYou probably do not get enough sleep if you're constantly tired during the day.\n\n\nWHAT CAUSES INSOMNIA:\nThe most common causes of insomnia are:\n- stress, anxiety or depression\n- noise\n- a room that's too hot or cold\n- uncomfortable beds\n- alcohol, caffeine or nicotine\n- illegal drugs like cocaine or ecstasy\n- jet lag\n- shift work\nConditions and medicines that can cause insomnia:\n  * mental health conditions, such as schizophrenia or bipolar disorder\n  * Alzheimer's disease or Parkinson's disease\n  * restless legs syndrome\n  * overactive thyroid\n  * menopause\nMany medicines can also cause insomnia.\nThings that keep you from getting a good night's sleep:\n  * long-term pain\n  * sleepwalking\n  * snoring or interrupted breathing while sleeping (sleep apnoea)\n  * suddenly falling asleep anywhere (narcolepsy)\n  * nightmares or night terrors (particularly in children)"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Iron deficiency anaemia.txt",
      "summary": {
        "symptoms": [
          "tiredness, paler than usual skin and palpitations for two months"
        ]
      },
      "evidence_anchor": "paler than usual",
      "query": "Clinical guidance, and diagnostic criteria for: tiredness, paler than usual skin and palpitations for two months.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Dehydration.txt",
          "score": 0.6850996801197731,
          "survived": true,
          "text": "ASK FOR AN URGENT GP APPOINTMENT IF:\n- you're feeling unusually tired (or your child seems drowsy)\n- you feel dizzy when you stand up and it does not go away\n- you have dark yellow pee or you're peeing less than normal (or your baby has fewer wet nappies)\n- you or your child are breathing quickly or have a fast heart rate\n- your baby or child have few or no tears when they cry\n- your baby has a soft spot on their head that sinks inwards (sunken fontanelle)\nThese can be signs of serious dehydration that need urgent treatment.\n\n\nGO TO ACCIDENT AND EMERGENCY IF:\nYou or somebody else has signs of dehydration and:\n- blue, grey, pale or blotchy skin, lips or tongue – on brown or black skin, this may be easier to see on the palms of the hands or soles of the feet\n- skin that feels cold\n- difficulty breathing, or is taking lots of quick breaths\n- are confused\n- are sleepier than normal or difficult to wake\nThese could be signs of shock, which is a serious complication of dehydration.\n\n\nHOW TO REDUCE THE RISK OF DEHYDRATION:\n- Drinking fluids regularly can reduce the risk of dehydration. Water or diluted sugar-free squash are good choices.\n- You should drink enough during the day so that your pee is a pale colour.\n- Drink more when there's a higher risk of dehydrating. For example, if you're being sick, sweating due to hot weather or exercise, or you have diarrhoea.\n- Children under the age of 5 and older adults should get plenty of fluids as they have an increased risk of dehydration.\n\n\nHELPING SOMEONE YOU CARE FOR:\nA person you care for may not have a sense of how much they're drinking.\n\nYou can help them by:\n- making sure they drink at mealtimes\n- making drinking a social thing\n- offering them food with a high water content – for example, soup, ice cream, jelly and fruits like melon\n\nSOURCES:\nhttps://www.nhs.uk/conditions/dehydration/"
        },
        {
          "file_name": "Covid 19.txt",
          "score": 0.669592996263923,
          "survived": false,
          "text": "ASK FOR AN URGENT GP APPOINTMENT:\r- you're worried about your or a child's COVID-19 symptoms or are not sure whatto do\r- the symptoms are getting worse or are not getting better\r- you or a child have other signs of illness, such as a rash, loss of appetite, or feeling weak\r- you or a child have a high temperature that last 5 days or more or does notcome down with paracetamol\r- a child under 3 months old and has a temperature of 38C or higher, or youthink they have a high temperature\r- a child 3 to 6 months old and has a temperature of 39C or higher, or you thinkthey have a high temperature\rIt's particularly important to get help if you're at increased risk of getting ill fromCOVID-19, such as if you're pregnant, aged 60 or over, or have a weakenedimmune system.\r\r\rSOURCES:\nhttps://www.nhs.uk/conditions/covid-19/covid-19-symptoms-and-what-to-do/"
        }
      ],
      "retrieved": false,
      "error": null
    },
    {
      "expected_document": "Lyme Disease.txt",
      "summary": {
        "symptoms": [
          "expanding circular rash after a tick bite, fever and fatigue"
        ]
      },
      "evidence_anchor": "tick bite",
      "query": "Clinical guidance, and diagnostic criteria for: expanding circular rash after a tick bite, fever and fatigue.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Lyme Disease.txt",
          "score": 0.772630155086517,
          "survived": true,
          "text": "EARLY SIGNS AND SYMPTOMS (3 to 30 days after tick bite)\n- Fever, chills, headache, fatigue, muscle and joint aches, and swollen lymph nodes may occur in the absence of rash\n- Erythema migrans (EM) rash \n \t* Occurs in approximately 70 to 80 percent of infected people\n\t* Begins at the site of a tick bite after a delay of 3 to 30 days (average is about 7 days)\n\t* Expands gradually over several days reaching up to 12 inches (30 cm) or more across\n\t* May feel warm to the touch but is rarely itchy or painful\n\t* Sometimes clears as it enlarges, resulting in a target or \"bull's-eye\" appearance\n\t* May appear on any area of the body\n\t* Does not always appear as a \"classic bull's-eye\" rash\n\n\nLATER SIGNS AND SYMPTOMS (days to months after tick bite)\n- Severe headaches and neck stiffness\n- Additional EM rashes on other areas of the body\n- Facial palsy (loss of muscle tone or droop on one or both sides of the face)\n- Arthritis with severe joint pain and swelling, particularly the knees and other large joints.\n- Intermittent pain in tendons, muscles, joints, and bones\n- Heart palpitations or an irregular heartbeat (Lyme carditis)\n- Episodes of dizziness or shortness of breath\n- Inflammation of the brain and spinal cord\n- Nerve pain\n- Shooting pains, numbness, or tingling in the hands or feet"
        },
        {
          "file_name": "Lyme Disease.txt",
          "score": 0.7207657098770139,
          "survived": true,
          "text": "HOW IT SPREADS\n- Lyme disease bacteria causing human infection in the United States are spread to people by blacklegged (Ixodes) ticks.\n\nPREVENTION\n- Prevent tick bites\n- The best defense against Lyme disease is to prevent tick bites. This will reduce your risk of other tickborne diseases as well.\n\nWHAT TO DO AFTER A TICK BITE\n- Remove attached ticks as soon as possible. \n- Depending on the type of tick and how long it was attached, antibiotic prophylaxis might help to prevent Lyme disease. \n- Call your doctor if you develop fever, rash, or other symptoms.\n\nTESTING AND DIAGNOSING\n- CDC recommends the use of FDA-cleared antibody tests for laboratory diagnosis of Lyme disease.\n- When assessing a patient for Lyme disease, your healthcare provider will consider:\n- The signs and symptoms of Lyme disease\n- The likelihood that you have been exposed to infected blacklegged ticks\n- The possibility that other illnesses may cause similar symptoms\n- Results of laboratory tests, when indicated\n\n\nSOURCES\nhttps://www.cdc.gov/lyme/about/index.html\nhttps://www.cdc.gov/lyme/signs-symptoms/index.html\nhttps://www.cdc.gov/lyme/diagnosis-testing/index.html"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Measles.txt",
      "summary": {
        "symptoms": [
          "fever, cough, runny nose, red eyes and a spreading rash"
        ]
      },
      "evidence_anchor": "cough",
      "query": "Clinical guidance, and diagnostic criteria for: fever, cough, runny nose, red eyes and a spreading rash.",
      "indexed_chunks": 4,
      "candidates": [
        {
          "file_name": "Pink Eye.txt",
          "score": 0.713707659994643,
          "survived": true,
          "text": "Bacterial Conjunctivitis Features:\nSigns and symptoms of bacterial conjunctivitis overlap with other causes of conjunctivitis, including viral and allergic conjunctivitis, which can make diagnosis difficult.\nTypical signs and symptoms include:\n- Red eye\n- Purulent discharge that causes eyelids to be matted together\n- Chemosis\n- Decreased vision\n- Eyelid swelling and pain\n\nTreatment and recovery\nMost cases of acute, infectious conjunctivitis in adults are viral and self-limited; these cases do not require antimicrobial treatment. Antiviral medication may be used to treat more serious forms of conjunctivitis. This can include conjunctivitis caused by herpes simplex virus or varicella-zoster virus.\n\nContact lens wearers with bacterial conjunctivitis are at higher risk of bacterial keratitis. They should be asked to remove their contact lenses; treated with topical antibiotics; and promptly evaluated by an ophthalmologist.\n\nPatient counseling\n- Advise patients to remain home if they have viral or bacterial conjunctivitis with systemic signs of illness, especially if they cannot avoid close contact with others. Patients may return to work or school if they receive clinician approval and after any indicated therapy is implemented.\n- Counsel patients with viral conjunctivitis to prevent transmission by washing hands frequently, using separate towels, and avoiding close contact with others.\n\nSources\nhttps://www.cdc.gov/conjunctivitis/hcp/clinical-overview/index.html"
        },
        {
          "file_name": "Cold.txt",
          "score": 0.701964217307318,
          "survived": true,
          "text": "Preventing and Managing the Common Cold\n\nAre you sneezing, or do you have a stuffy and runny nose? You might have a cold. Antibiotics do not work against viruses that cause colds and will not help you feel better.\n\nWhat is Common Cold?\nA common cold is a mild upper respiratory illness caused by a virus that resolves in a short period of time. Colds can have similar symptoms to flu. It can be difficult (or even impossible) to tell the difference between them based on symptoms alone.\n\nSymptoms\nSymptoms of a cold usually peak within 2 to 3 days, though some (especially runny nose and cough) can last up to 10–14 days. Symptoms can include:\n- Sneezing\n- Nasal congestion\n- Sore throat\n- Cough\n- Fever (although most people with colds do not have fever)\n- Mucus\n  * Clear mucus helps wash viruses from the nose and sinuses\n  * Mucus may change to a white, yellow, or green color after 2–3 days, this is normal\n\nCauses\nMore than 200 viruses can cause a cold, but rhinoviruses are the most common type. Viruses that cause colds can spread from person to person through the air and close personal contact.\n\nWhen to Seek Medical Care*\nSee a healthcare professional if you have:\n- Trouble breathing or fast breathing\n- Dehydration\n- Fever that lasts longer than 4 days\n- Symptoms that last more than 10 days without improvement\n- Symptoms, such as fever or cough, that improve but then return or worsen\n- Worsening of chronic medical conditions\n\n*This list is not all-inclusive. Please see a healthcare professional for any symptom that is severe or concerning.\nTalk to a healthcare professional right away if your child is under 3 months old with a fever of 100.4 °F (38 °C) or higher.\n\nTreatment\nThere is no cure for a cold. It will get better on its own—without antibiotics. Antibiotics won’t help you get better if you have a cold."
        }
      ],
      "retrieved": false,
      "error": null
    },
    {
      "expected_document": "Meningococcal Disease.txt",
      "summary": {
        "symptoms": [
          "sudden high fever, stiff neck, confusion and a purple rash"
        ]
      },
      "evidence_anchor": "neck stiffness",
      "query": "Clinical guidance, and diagnostic criteria for: sudden high fever, stiff neck, confusion and a purple rash.",
      "indexed_chunks": 5,
      "candidates": [
        {
          "file_name": "Meningococcal Disease.txt",
          "score": 0.725552976131439,
          "survived": true,
          "text": "CLINICAL FEATURES:\nMeningococcal disease is a serious and potentially life-threatening infection. Common signs and symptoms of meningococcal disease include sudden onset of high fever, neck stiffness, confusion, nausea, vomiting, lethargy, and petechial or purpuric rash. Without prompt and appropriate treatment, the infection can progress rapidly and result in death.\n\nAsymptomatic nasopharyngeal carriage of N. meningitidis is common, but few carriers develop invasive disease, and carriers without an exposure do not require treatment or chemoprophylaxis. Persons who have close contact with persons with invasive disease are at substantially increased risk for acquiring carriage and disease.\n\nPatients infected with N. meningitidis may be contagious in the 7 days before symptom onset and are rendered noninfectious by 24 hours of effective antimicrobial therapy. Cases occur in all age groups; however, children less than 2 years old, adolescents 16 through 23 years old, and adults 85 years of age or older have higher rates of disease than other age groups. In addition, people with certain medical conditions, such as functional or anatomic asplenia; persistent complement component deficiencies (e.g., C3, C5-9, properdin, factor H, factor D or are taking eculizumab or ravulizumab); and HIV infection are at increased risk for meningococcal disease.\n\nThe incubation period of meningococcal disease is 3 to 4 days, with a range of 1 to 10 days."
        },
        {
          "file_name": "Lyme Disease.txt",
          "score": 0.7002719640731809,
          "survived": true,
          "text": "EARLY SIGNS AND SYMPTOMS (3 to 30 days after tick bite)\n- Fever, chills, headache, fatigue, muscle and joint aches, and swollen lymph nodes may occur in the absence of rash\n- Erythema migrans (EM) rash \n \t* Occurs in approximately 70 to 80 percent of infected people\n\t* Begins at the site of a tick bite after a delay of 3 to 30 days (average is about 7 days)\n\t* Expands gradually over several days reaching up to 12 inches (30 cm) or more across\n\t* May feel warm to the touch but is rarely itchy or painful\n\t* Sometimes clears as it enlarges, resulting in a target or \"bull's-eye\" appearance\n\t* May appear on any area of the body\n\t* Does not always appear as a \"classic bull's-eye\" rash\n\n\nLATER SIGNS AND SYMPTOMS (days to months after tick bite)\n- Severe headaches and neck stiffness\n- Additional EM rashes on other areas of the body\n- Facial palsy (loss of muscle tone or droop on one or both sides of the face)\n- Arthritis with severe joint pain and swelling, particularly the knees and other large joints.\n- Intermittent pain in tendons, muscles, joints, and bones\n- Heart palpitations or an irregular heartbeat (Lyme carditis)\n- Episodes of dizziness or shortness of breath\n- Inflammation of the brain and spinal cord\n- Nerve pain\n- Shooting pains, numbness, or tingling in the hands or feet"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Migraine.txt",
      "summary": {
        "symptoms": [
          "one-sided throbbing headache, nausea and sensitivity to light"
        ]
      },
      "evidence_anchor": "sensitive to light",
      "query": "Clinical guidance, and diagnostic criteria for: one-sided throbbing headache, nausea and sensitivity to light.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Migraine.txt",
          "score": 0.736288221324894,
          "survived": true,
          "text": "MIGRAINE:\n\n\nOVERVIEW:\n- Migraine is a condition that causes symptoms such as a severe headache, feeling sick and sensitivity to light. There is treatment to help manage symptoms.\n\n\nSYMPTOMS OF MIGRAINE:\n- Migraine is a condition that causes a set of symptoms known as a migraine attack.\n- The main symptoms of a migraine attack are:\n  * a throbbing headache – this can be severe, often on 1 side of the head and can be worse when you move around\n  * feeling or being sick (nausea and vomiting)\n  * being very sensitive to light and sounds\n- You may also get symptoms at the start of a migraine attack, such as:\n  * feeling very tired and yawning a lot\n  * craving certain foods or feeling thirsty\n  * changes in your mood\n  * a stiff neck\n  * peeing more\n- Some people get warning signs that they're about to have a migraine attack (called aura), such as:\n  * problems with your sight, such as seeing zigzag lines or flashing lights\n  * numbness or a tingling that feels like pins and needles\n  * feeling dizzy\n  * difficulty speaking\n- Aura symptoms should not last for longer than 1 hour.\n- Migraine attacks usually last between 4 hours and 3 days, with early symptoms (such as feeling very tired) starting hours or up to 2 days before the head pain starts and finishing after the headache stops.\n- Some people have migraine attacks several times a week, while others do not have them as often.\n- Migraine attacks that happen just before or during your period are called menstrual migraines. They are often longer and more severe than migraine attacks at other times.\n- Most people find their migraine attacks slowly get better as they get older.\n- In women, migraine often gets better after the menopause and sometimes improves in pregnancy."
        },
        {
          "file_name": "Migraine.txt",
          "score": 0.6767004114329089,
          "survived": true,
          "text": "SEE A GP IF:\n- your migraine attacks are severe or getting worse, or lasting longer than usual\n- you have migraine attacks more than once a week\n- you're finding it difficult to control your migraine\n- you regularly get migraine before or during your period\nAsk for an urgent GP appointment if:\n- You have a migraine attack and:\n  * it's lasted longer than 72 hours\n  * aura symptoms last longer than 1 hour at a time\n  * you're pregnant or just had a baby\n- Call healthline if you or your child:\n  * have a headache that came on suddenly and is extremely painful\n  * have problems speaking or remembering things\n  * lose your vision, or have blurred or double vision\n  * feel drowsy or confused\n  * have a seizure or fit\n  * have a very high temperature and symptoms of meningitis\n  * cannot move or have weakness in the arms or legs on 1 side of your body, or 1 side of your face\n  * have recently had a head injury\n\n\nTREATMENT FOR MIGRAINE:\n- Migraine cannot be cured, but treatment can help:\n  * manage symptoms of a migraine attack\n  * prevent migraines attacks\n- The treatments available will depend on how severe your migraine is and how often you get migraine attacks.\n- You may have to try a combination of treatments before you find something that works for you.\n- Treatment for symptoms of a migraine attack includes:\n  * painkillers, such as ibuprofen and paracetamol\n  * medicines called triptans and gepants\n  * medicines that stop you feeling sick or being sick\n- If you're taking painkillers, take them as soon as your headache starts.\n- Treatment to prevent migraine attacks includes:\n  * medicines that help prevent migraine attacks, such as beta blockers, antidepressants and medicines for epilepsy\n  * acupuncture\n  * relaxation techniques and cognitive behavioural therapy (CBT)\n  * vitamin B2\n- A GP may also recommend making changes to your lifestyle to help manage migraine, such as eating at regular times and drinking less caffeine.\n- If none of these treatments help your symptoms, or they're getting worse, you may be referred to a specialist for further tests and treatment."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Mouth ulcers.txt",
      "summary": {
        "symptoms": [
          "painful sore inside the mouth for one week"
        ]
      },
      "evidence_anchor": "inside the mouth",
      "query": "Clinical guidance, and diagnostic criteria for: painful sore inside the mouth for one week.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Mouth ulcers.txt",
          "score": 0.756616189681531,
          "survived": true,
          "text": "SEE A DENTIST OR GP IF YOUR MOUTH ULCER:\n- lasts longer than 3 weeks\n- is different to other mouth ulcers you've had before, for example if it's bigger than usual or near the back of your throat\n- bleeds or becomes more painful and red – this may be a sign of an infection\nAlthough most mouth ulcers are harmless, a long-lasting mouth ulcer is sometimes a sign of mouth cancer. It's best to get it checked.\nYou should also see a GP if you have other symptoms such as:\n- ulcers anywhere else on your body, such as your skin or genitals\n- painful, red or swollen joints\n\n\nTREATMENT FROM A DENTIST OR GP:\n- A GP or dentist may prescribe stronger medicine to treat severe, persistent or infected mouth ulcers.\nPossible treatments include:\n- steroids given as either a mouth spray, tablets that dissolve in your mouth or tablets that can be dissolved in water\n- painkilling gels, ointments, sprays or tablets\n- mouthwashes to kill or remove any germs in your mouth\n\n\nCHECK IF YOU HAVE A MOUTH ULCER:\n- Mouth ulcers usually appear inside the mouth on the cheeks or lips.\n- Ulcers can also appear on the tongue.\n- You may have more than 1 ulcer at a time.\n- Mouth ulcers are not contagious and should not be confused with cold sores.\n- Cold sores appear on the lips or around the mouth and often begin with a tingling, itching or burning sensation. They can also appear as a small group of pinhead-sized ulcers inside the mouth."
        },
        {
          "file_name": "Cold sore.txt",
          "score": 0.730439825680247,
          "survived": true,
          "text": "COLD SORES:\n\n\nOVERVIEW:\nCold sores are common and usually clear up on their own within 10 days. There are things you can do to help ease the pain.\n\n\nSYMPTOMS OF A COLD SORE:\n- A cold sore usually starts with a tingling, itching or burning feeling.\n- Over the next 48 hours one or more painful blisters will appear on your face.\n- Cold sore blisters are usually small and filled with fluid.\n- The blisters can appear anywhere on the face.\n- The blisters burst and crust over into a scab.\n- Cold sores should start to heal within 10 days, but are contagious and may be irritating or painful while they heal.\n- Certain things may trigger a cold sore, such as illness, sunshine or being on your period.\n\n\nHOW LONG COLD SORES ARE CONTAGIOUS:\n- Cold sores are contagious from the moment you first feel tingling or other signs of a cold sore coming on to when the cold sore has completely healed.\n- They can easily spread to other people and other parts of your body.\n- To help stop cold sores spreading:\n  * wash your hands with soap and water whenever you touch your cold sore\n  * do not kiss anyone while you have a cold sore\n  * do not have oral sex until your cold sore completely heals as you could give your partner genital herpes\nImportant:\n- Kissing a baby if you have a cold sore can lead to neonatal herpes, which is very dangerous to newborn babies.\n\n\nA PHARMACIST CAN HELP WITH COLD SORES:\nA pharmacist can recommend:\n- creams to ease pain and irritation\n- antiviral creams to speed up healing time\n- cold sore patches to protect the skin while it heals\nYou can buy electronic devices from pharmacies that treat cold sores with light or lasers.\nYou may find these helpful, but there's not much evidence to confirm they work.\nIf you regularly get cold sores, use antiviral creams as soon as you recognise the early tingling feeling. They do not always work after blisters appear."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Norovirus Stomach Bug.txt",
      "summary": {
        "symptoms": [
          "sudden vomiting and diarrhoea after close contact with someone with the same symptoms"
        ]
      },
      "evidence_anchor": "Diarrhea, vomiting",
      "query": "Clinical guidance, and diagnostic criteria for: sudden vomiting and diarrhoea after close contact with someone with the same symptoms.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Food poisoning.txt",
          "score": 0.7362716669550551,
          "survived": true,
          "text": "CALL EMERGENCY NOW IF:\n- you're worried about a baby under 12 months\n- your child stops breast or bottle feeding while they're ill\n- a child under 5 years has signs of dehydration, such as fewer wet nappies\n- you or your child (aged 5 years or over) still have signs of dehydration after using oral rehydration sachets\n- you or your child keep being sick and cannot keep fluid down\n- you or your child have bloody diarrhoea or bleeding from the bottom\n- you or your child have diarrhoea for more than 7 days or vomiting for more than 2 days\n- vomit blood or have vomit that looks like ground coffee\n- have green vomit (adults)\n- have yellow-green or green vomit (children)\n- may have swallowed something poisonous\n- have a stiff neck and pain when looking at bright lights\n- have a sudden, severe headache\n- have a sudden, severe tummy ache\n- have blue, grey, pale or blotchy skin, lips or tongue - on brown or black skin this may be easier to see on the palms of the hands or soles of the feet\n- are having severe difficulty breathing, or taking lots of quick, short breaths\n- are confused or not responding as usual\n- What we mean by severe pain\n- Severe pain:\t\n  * always there and so bad it's hard to think or talk\n  * you cannot sleep\n  * it's very hard to move, get out of bed, go to the bathroom, wash or dress\n- Moderate pain:\t\n  * always there\n  * makes it hard to concentrate or sleep\n  * you can manage to get up, wash or dress\n- Mild pain:\t\n  * comes and goes\n  * is annoying but does not stop you doing daily activities\n\nHOW YOU GET FOOD POISONING:\nFood poisoning is caused by eating something that has been contaminated with germs.\nThis can happen if food is:\n- not cooked or reheated thoroughly\n- not stored correctly – for example, it's not been frozen or chilled\n- left out for too long\n- handled by someone who's ill or has not washed their hands\n- eaten after its \"use by\" date\n- Any type of food can cause food poisoning."
        },
        {
          "file_name": "Food poisoning.txt",
          "score": 0.7350713926468619,
          "survived": true,
          "text": "FOOD POISONING:\n\nFood poisoning is rarely serious and usually gets better within a week. You can normally treat yourself or your child at home.\n\nSYMPTOMS OF FOOD POISONING:\n- feeling sick or being sick\n- diarrhoea\n- tummy pain\n- a high temperature\n- feeling generally unwell\nThe symptoms usually start within a few hours or a few days of eating food that caused the infection.\nSometimes symptoms do not start for a few weeks.\n\nHOW TO TREAT FOOD POISONING YOURSELF:\nIf you or your child have food poisoning, you can usually treat it at home.\nThe symptoms usually get better within a week.\nDiarrhoea and vomiting can usually be treated at home. The most important thing is to have lots of fluids to avoid dehydration.\n\nDO:\n- stay at home and get plenty of rest\n- drink lots of fluids, such as water or squash – take small sips if you feel sick\n- carry on breast or bottle feeding your baby – if they're being sick, try giving small feeds more often than usual\n- give babies on formula or solid foods small sips of water between feeds\n- eat when you feel able to – it may help to avoid foods that are fatty or spicy\n- take paracetamol if you're in discomfort – check the leaflet before giving it to your child\n\nDON’T:\n- do not have fruit juice or fizzy drinks – they can make diarrhoea worse\n- do not make baby formula weaker – use it at its usual strength\n- do not give children under 12 medicine to stop diarrhoea\n- do not give aspirin to children under 16\n\nA PHARMACIST CAN HELP WITH FOOD POISONING, SPEAK TO A PHARMACIST IF:\n- you or your child (over 5 years) have signs of dehydration, such as dark, smelly pee or peeing less than usual\n- you're an older person, have a weakened immune system, or have other health conditions that increase your risk of dehydration\n- you need to stop diarrhoea for a few hours\n- They may recommend:\n  * oral rehydration powder that you mix with water to make a drink\nmedicine to stop diarrhoea for a few hours, like loperamide (not suitable for children under 12)"
        }
      ],
      "retrieved": false,
      "error": null
    },
    {
      "expected_document": "Pink Eye.txt",
      "summary": {
        "symptoms": [
          "red eye with thick pus that makes the eyelids stick together"
        ]
      },
      "evidence_anchor": "eyelids",
      "query": "Clinical guidance, and diagnostic criteria for: red eye with thick pus that makes the eyelids stick together.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Psoriasis.txt",
          "score": 0.6809736490249629,
          "survived": true,
          "text": "GO TO A&E IF:\nYou have psoriasis and:\n- your skin quickly turns red and you develop white, pus-filled bumps that join together – redness may be harder to see on brown or black skin\n- have psoriasis patches on your feet that turn yellow-brown and are filled with pus\n- your fingers and toes have red, scaly pus-filled bumps on the tips – redness may be harder to see on brown or black skin\n- These can be signs that you have a more serious condition or an infection.\n\n\nYou may also have other symptoms such as your heart beating fast, or a high temperature, or feeling hot, cold or shivery.\n\n\nTREATMENT FOR PSORIASIS:\nHow your psoriasis is treated depends on the type of psoriasis you have, how severe it is, and where it is on your body.\nThe main treatments are:\n- vitamin D creams, lotions, ointments and gels\n- moisturising creams, lotions, ointments and gels for your skin and to wash with (emollients)\n- steroid creams, lotions or gels\n- other treatments for your skin or scalp, such as coal tar\n- If your psoriasis is more severe, there are other treatments, such as light therapy and medicines.\nYou may need a combination of different treatments.\nA GP can prescribe some treatments, or you may be referred to a skin specialist (dermatologist).\n\n\nLiving with psoriasis can be difficult. If it affects your mental health, you may be referred to a mental health specialist.\n\nIt's not known why or how this happens, but it's thought to be caused by a problem with the immune system.\n\nYou're more likely to have it if a member of your family has psoriasis.\n\nThere are certain things that can make your psoriasis worse or cause a flare-up of symptoms (triggers).\n\n\nTRIGGERS CAN INCLUDE:\n- stress\n- drinking alcohol or smoking\n- living with obesity\n- being pregnant\n- certain medicines\n- infections, such as strep A and HIV\n- cuts, scratches or grazes on your skin\n- sunlight\nPsoriasis is not contagious so you cannot catch it or spread it."
        },
        {
          "file_name": "Pink Eye.txt",
          "score": 0.671095986896994,
          "survived": true,
          "text": "Bacterial Conjunctivitis Features:\nSigns and symptoms of bacterial conjunctivitis overlap with other causes of conjunctivitis, including viral and allergic conjunctivitis, which can make diagnosis difficult.\nTypical signs and symptoms include:\n- Red eye\n- Purulent discharge that causes eyelids to be matted together\n- Chemosis\n- Decreased vision\n- Eyelid swelling and pain\n\nTreatment and recovery\nMost cases of acute, infectious conjunctivitis in adults are viral and self-limited; these cases do not require antimicrobial treatment. Antiviral medication may be used to treat more serious forms of conjunctivitis. This can include conjunctivitis caused by herpes simplex virus or varicella-zoster virus.\n\nContact lens wearers with bacterial conjunctivitis are at higher risk of bacterial keratitis. They should be asked to remove their contact lenses; treated with topical antibiotics; and promptly evaluated by an ophthalmologist.\n\nPatient counseling\n- Advise patients to remain home if they have viral or bacterial conjunctivitis with systemic signs of illness, especially if they cannot avoid close contact with others. Patients may return to work or school if they receive clinician approval and after any indicated therapy is implemented.\n- Counsel patients with viral conjunctivitis to prevent transmission by washing hands frequently, using separate towels, and avoiding close contact with others.\n\nSources\nhttps://www.cdc.gov/conjunctivitis/hcp/clinical-overview/index.html"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Psoriasis.txt",
      "summary": {
        "symptoms": [
          "itchy flaky patches with silvery-white scales on the elbows"
        ]
      },
      "evidence_anchor": "silvery-white scales",
      "query": "Clinical guidance, and diagnostic criteria for: itchy flaky patches with silvery-white scales on the elbows.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Psoriasis.txt",
          "score": 0.686848022121427,
          "survived": true,
          "text": "PSORIASIS:\n\n\nOVERVIEW:\n- Psoriasis is a common skin condition that causes itchy and painful patches of dry, flaky skin. It cannot be cured, but there are treatments to help manage your symptoms.\n\n\nSYMPTOMS OF PSORIASIS:\nThe main symptom of psoriasis is dry, itchy, sore, flaky patches of skin that form what look like silvery-white scales.\n\nPSORIASIS PATCHES ARE USUALLY:\n- 1 to 2cm in size\n- an oval or irregular shape.\n- pink or red on white skin, turning silvery-white, and can sometimes turn a waxy yellow or - orange-brown colour\n- grey on brown or black skin, and cause dark marks on the skin after the psoriasis has gone\n- Most people only get a few psoriasis patches, but others get them across large parts of their body. Some people have lots of smaller, scaly patches.\n\n\nYou may also get lots of small brown and yellow spots on the palms of your hands and soles of your feet.\n\nYou can get psoriasis in different parts of your body, but it's mostly found on the:\n- head and behind the ears\n- chest, tummy and back\n- bottom\n- forearms and elbows\n- lower legs and knees\n- You can also get it in the folds of your body, such as your groin, genitals and under your breasts, or on your fingernails. The surface of your nails can have dents and pits.\n\nYou can get psoriasis at any age, but symptoms often start either between the ages of 15 and 25, or 50 and 60 .\n\nThere are usually times where your symptoms get worse (called flare-ups) and times when they're better.\n\n\nSEE A GP IF:\n- you have symptoms of psoriasis\n- you have psoriasis and your treatment is not working or is giving you side effects\n- you have psoriasis and also have pain, stiffness and swelling in your joints that keeps coming back"
        },
        {
          "file_name": "Lyme Disease.txt",
          "score": 0.6313118558340169,
          "survived": false,
          "text": "EARLY SIGNS AND SYMPTOMS (3 to 30 days after tick bite)\n- Fever, chills, headache, fatigue, muscle and joint aches, and swollen lymph nodes may occur in the absence of rash\n- Erythema migrans (EM) rash \n \t* Occurs in approximately 70 to 80 percent of infected people\n\t* Begins at the site of a tick bite after a delay of 3 to 30 days (average is about 7 days)\n\t* Expands gradually over several days reaching up to 12 inches (30 cm) or more across\n\t* May feel warm to the touch but is rarely itchy or painful\n\t* Sometimes clears as it enlarges, resulting in a target or \"bull's-eye\" appearance\n\t* May appear on any area of the body\n\t* Does not always appear as a \"classic bull's-eye\" rash\n\n\nLATER SIGNS AND SYMPTOMS (days to months after tick bite)\n- Severe headaches and neck stiffness\n- Additional EM rashes on other areas of the body\n- Facial palsy (loss of muscle tone or droop on one or both sides of the face)\n- Arthritis with severe joint pain and swelling, particularly the knees and other large joints.\n- Intermittent pain in tendons, muscles, joints, and bones\n- Heart palpitations or an irregular heartbeat (Lyme carditis)\n- Episodes of dizziness or shortness of breath\n- Inflammation of the brain and spinal cord\n- Nerve pain\n- Shooting pains, numbness, or tingling in the hands or feet"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Sciatica.txt",
      "summary": {
        "symptoms": [
          "burning pain down the back of one leg with tingling toes"
        ]
      },
      "evidence_anchor": "back of the leg",
      "query": "Clinical guidance, and diagnostic criteria for: burning pain down the back of one leg with tingling toes.",
      "indexed_chunks": 3,
      "candidates": [
        {
          "file_name": "Sciatica.txt",
          "score": 0.6847049218064469,
          "survived": true,
          "text": "SCIATICA:\n\n\nOVERVIEW:\nSciatica happens when the sciatic nerve, which runs from your lower back to your feet, is irritated or compressed. It usually gets better in a few weeks to a few months but can last longer.\nIf you get sciatica, there's a chance that it could happen again at some point.\n\n\nSYMPTOMS OF SCIATICA:\nThe symptoms of sciatica usually affect your bottom and the back of one leg, often including your foot and toes.\nYou may feel:\n- a sharp, burning pain down the back of the leg\n- tingling – like pins and needles\n- numbness\n- weakness\nYour symptoms may come on suddenly but they can also start slowly. The pain may be worse when moving, sneezing or coughing.\nYou may also have back pain, but it's not usually as bad as the pain in your leg.\n\n\nYou probably do not have sciatica if you only have back pain.\n\n\nHOW YOU CAN EASE SCIATICA PAIN YOURSELF:\nSciatica usually gets better in a few weeks to a few months, but it can sometimes last longer. It can also return if you've had it before.\nTo help relieve your pain and speed up recovery:\nDo\n- carry on with your normal activities as much as possible\n- try regular exercises for sciatica\n- start gentle exercise as soon as you can – anything that gets you moving can help\n- hold heat packs to the painful areas – you can buy these from pharmacies\n- ask a pharmacist about painkillers (paracetamol is unlikely to help and it's not clear how much NSAIDs, such as ibuprofen, help with sciatica)\nDon’t\n- do not sit or lie down for long periods – even if moving hurts, it's not harmful and can help you get better faster\n\n\nSEE A GP IF:\nYou have sciatica and the pain:\n- has not improved after trying home treatments for a few weeks\n- is getting worse\n- is stopping you doing your normal activities"
        },
        {
          "file_name": "Sciatica.txt",
          "score": 0.66291246755607,
          "survived": false,
          "text": "SEE A GP IF:\nYou have sciatica and the pain:\n- has not improved after trying home treatments for a few weeks\n- is getting worse\n- is stopping you doing your normal activities\n\n\nGO TO A&E IF YOU:\n- have sciatica on both sides\n- have weakness or numbness in both legs that's severe or getting worse\n- have numbness around or under your genitals, or around your bottom (anus)\n- find it hard to start peeing, cannot pee or cannot control when you pee – and this is not normal for you\n- do not notice when you need to poo or cannot control when you poo – and this is not normal for you\n- These could be symptoms of a serious back problem that needs to be treated in hospital as soon as possible.\n\n\n\nTREATMENTS FOR SCIATICA:\nMain treatments for sciatica\nIf you have sciatica, treatments can include:\n- exercises and stretches\n- painkillers\n- physiotherapy – including exercise advice and techniques like massage (manual therapy)\n- Physiotherapy is free of charge on the NHS throughout the UK, but waiting times can be long. You can also get it privately.\n\n\nOTHER TREATMENTS FOR SCIATICA:\nIf your pain is severe and treatments have not helped, you may be referred to a hospital specialist for:\n- a procedure to seal off some of the nerves in your back so they stop sending pain signals (radiofrequency denervation)\n- a painkilling injection such as an epidural to stop you feeling pain\n- surgery – an operation called decompression surgery can sometimes help relieve sciatica\n\n\nHOW TO STOP SCIATICA COMING BACK:\nIf you have sciatica, or have had it in the past, there's a chance you could get it again. But there are some things you can do to reduce your chance of this happening.\nDo:\n- stay active – take regular exercise\n- use a safe technique when lifting heavy objects\n- make sure you have a good posture when sitting and standing\n- sit correctly when using a computer\n- lose weight if you're overweight\nDon’t:\n- do not smoke – smoking can increase your risk of getting sciatica"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Sprains and strains.txt",
      "summary": {
        "symptoms": [
          "twisted ankle with pain, swelling, bruising and difficulty bearing weight"
        ]
      },
      "evidence_anchor": "swollen or bruised",
      "query": "Clinical guidance, and diagnostic criteria for: twisted ankle with pain, swelling, bruising and difficulty bearing weight.",
      "indexed_chunks": 4,
      "candidates": [
        {
          "file_name": "Sprains and strains.txt",
          "score": 0.6975241483733581,
          "survived": true,
          "text": "SPRAINS AND STRAINS:\n\nOVERVIEW:\nSprains and strains are common injuries affecting the muscles and ligaments. Most can be treated at home without seeing a GP.\n\nSYMPTOMS OF A SPRAIN OR STRAIN:\nIt's likely to be a sprain or strain if:\n- you have pain, tenderness or weakness – usually around your ankle, foot, wrist, thumb, knee, leg or back\n- the injured area is swollen or bruised\n- you cannot put weight on the injury or use it normally\n- you have muscle spasms or cramping – where your muscles painfully tighten on their own\n\n\nIS IT A SPRAIN OR A STRAIN?:\nDifferences between sprains and strains\n- Sprains:\t\n  * Torn or twisted ligament (tissue that connects the joints)\n  * Most common in wrists, ankles, thumbs, knees\n\n- Strains:\n  * Overstretched or torn muscle (also known as a pulled muscle)\n  * Most common in feet, legs, back"
        },
        {
          "file_name": "Appendicitis.txt",
          "score": 0.69685592074061,
          "survived": true,
          "text": "GO TO A&E IF:\nYou or your child have:\n- severe pain in your abdomen (tummy)\n- confusion, blotchy or paler than usual skin (on brown or black skin this may be easier to see on the palms of the hands or soles of the feet) or difficulty breathing – these could be signs of sepsis\n\n\nHOW APPENDICITIS IS DIAGNOSED:\n- If you have symptoms of appendicitis, a GP or hospital doctor will feel your abdomen (tummy) to check for pain and swelling.\n- You'll need to go to hospital for tests and treatment. Tests you may have include:\n  * blood tests\n  * testing a sample of your pee\n  * scans such as an ultrasound scan or CT scan to check for swelling in your appendix\n  * a pregnancy test if there's a chance you could be pregnant\n- There's no test that can always show if you have appendicitis. It can be hard to diagnose because the symptoms can be similar to other conditions. Sometimes doctors will try waiting a few hours to see how your symptoms develop in hospital.\n- If your symptoms mean it's very likely you have appendicitis, or if your appendix may have burst, doctors may recommend surgery instead of waiting for more tests."
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Strep Throat.txt",
      "summary": {
        "symptoms": [
          "sudden sore throat, painful swallowing, fever and white patches on the tonsils"
        ]
      },
      "evidence_anchor": "White patches",
      "query": "Clinical guidance, and diagnostic criteria for: sudden sore throat, painful swallowing, fever and white patches on the tonsils.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Strep Throat.txt",
          "score": 0.756919026374817,
          "survived": true,
          "text": "About Strep Throat\n\nKEY POINTS\n- Strep throat is a bacterial infection in the throat and tonsils.\n- Healthcare providers can do a quick test to see if a sore throat is strep throat.\n- Antibiotics can help people with strep throat feel better faster.\n- Speak with a healthcare provider if you have concerns about strep throat.\n\nWhat it is\nStrep throat is a bacterial infection in the throat and tonsils.\n\nWorried your sore throat may be strep throat?\nViruses cause most sore throats. Only around 1 in 10 adults and 3 in 10 children with a sore throat have strep throat.\n\nSymptoms\nIt usually takes 2 to 5 days after exposure to become ill with strep throat.\n\nCommon symptoms may include:\n- Fever\n- Pain when swallowing\n- Red and swollen tonsils\n- Sore throat that started very quickly and may look red\n- Swollen lymph nodes in the front of the neck\n- Tiny, red spots on the roof of the mouth, called petechiae\n- White patches or streaks of pus on the tonsils\n- Swelling, redness, and white patches are common symptoms of strep throat.\n\nLess common symptoms, especially for children, may include:\n- Headache\n- Nausea or vomiting\n- Rash (scarlet fever)\n- Stomach pain\n\nComplications\nComplications can occur after a strep throat infection if the bacteria spread to other parts of the body.\nComplications can include:\n- Abscesses (pockets of pus) around the tonsils or in the neck\n- Ear infections\n- Post-streptococcal glomerulonephritis (a kidney disease)\n- Rheumatic fever (a disease affecting the heart, joints, brain, skin)\n- Sinus infections\n\nRisk factors\nAnyone can get strep throat, but some factors increase the risk of getting it.\n\nAge\nStrep throat is more common in children than adults.\n- Most common: Children 5 through 15 years old\n- Rare: Children younger than 3 years old\n\nClose contact\nClose contact with another person with strep throat is the most common risk factor for illness. For example, if someone has strep throat, the bacteria often spread to other people in their household."
        },
        {
          "file_name": "Strep Throat.txt",
          "score": 0.679333448410034,
          "survived": true,
          "text": "For example, if someone has strep throat, the bacteria often spread to other people in their household.\n- Contact with children: Parents of school-age children and adults who are often in contact with children are at increased risk.\n- Crowded settings can increase the risk of getting any group A strep infection including strep throat. These settings include:\n  * Daycare centers and schools\n  * Detention or correctional facilities\n  * Homeless shelters\n  * Military training facilities\n\nCauses\nGroup A Streptococcus (group A strep bacteria) cause strep throat and are contagious.\n\nPrevention\nPeople can take steps to help protect themselves and others from group A strep infections, including strep throat. These steps include:\n- Wash hands often with soap and water\n- Avoid sharing cups, utensils, and bites of food with people who are sick\n- Wash cups, utensils, and plates after someone who's sick uses them\n- Cover coughs and sneezes\n- Keep wounds clean and bandaged\n- Seek health care if you think you have a group A strep infection\n\nTesting and diagnosis\nHealthcare providers can use several types of tests to diagnose strep throat.\n\nTreatment and recovery\nHealthcare providers treat strep throat with antibiotics.\n\nSimilar conditions: Viral sore throat\nThe following symptoms suggest a virus, not strep throat, is the cause of a sore throat:\n- Cough\n- Runny nose\n- Hoarseness (changes in voice to sound breathy, raspy or strained)\n- Conjunctivitis (pink eye)\n\nStrep carriers\nSome people can test positive for group A strep bacteria but have no symptoms.\n\nSources\nhttps://www.cdc.gov/group-a-strep/about/strep-throat.html"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Tooth decay.txt",
      "summary": {
        "symptoms": [
          "toothache, sharp pain with cold drinks and a brown spot on a tooth"
        ]
      },
      "evidence_anchor": "brown or black spots",
      "query": "Clinical guidance, and diagnostic criteria for: toothache, sharp pain with cold drinks and a brown spot on a tooth.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Tooth decay.txt",
          "score": 0.732307390433121,
          "survived": true,
          "text": "TOOTH DECAY:\n\n\nOVERVIEW:\nTooth decay is often caused by having too much sugary food and drink and not cleaning your teeth and gums regularly. See a dentist as soon as possible if you think you or your child has tooth decay.\n\n\nSYMPTOMS OF TOOTH DECAY:\nTooth decay may not cause any symptoms at first.\nBut if it gets worse it can lead to problems, such as a hole forming in the tooth (dental cavity).\nIf you have a hole in your tooth you may have:\n- toothache (tooth pain)\n- sharp pain in your tooth when eating or drinking hot, cold or sweet things (sensitive teeth)\n- white, brown or black spots on your tooth\n- Sometimes the tooth or gum can become infected, leading to a painful build-up of pus (dental abscess).\n\n\nSEE A DENTIST IF:\n- you have problems with your teeth like toothache or a sharp pain in your tooth when eating or drinking\n- your gums are painful, swollen, or bleed when you brush your teeth\n\n\n\nGET REGULAR DENTAL CHECK-UPS:\nYou should have regular dental check-ups even if you do not have any problems. See a dentist if you have not had a check-up for 2 years (or 1 year if you're under 18).\n\nTREATMENTS FOR TOOTH DECAY:\nTreatment for tooth decay depends on how severe it is.\n- A dentist can prescribe fluoride treatments like mouthwash or varnish to reverse early tooth decay.\n- You'll probably need a filling if you have a hole (cavity) in your tooth.\n- If tooth decay has reached the soft tissue (pulp) in the middle of your tooth, you may need root canal treatment.\n- Sometimes the affected tooth may need to be removed (extraction)."
        },
        {
          "file_name": "Dehydration.txt",
          "score": 0.656861344388805,
          "survived": false,
          "text": "ASK FOR AN URGENT GP APPOINTMENT IF:\n- you're feeling unusually tired (or your child seems drowsy)\n- you feel dizzy when you stand up and it does not go away\n- you have dark yellow pee or you're peeing less than normal (or your baby has fewer wet nappies)\n- you or your child are breathing quickly or have a fast heart rate\n- your baby or child have few or no tears when they cry\n- your baby has a soft spot on their head that sinks inwards (sunken fontanelle)\nThese can be signs of serious dehydration that need urgent treatment.\n\n\nGO TO ACCIDENT AND EMERGENCY IF:\nYou or somebody else has signs of dehydration and:\n- blue, grey, pale or blotchy skin, lips or tongue – on brown or black skin, this may be easier to see on the palms of the hands or soles of the feet\n- skin that feels cold\n- difficulty breathing, or is taking lots of quick breaths\n- are confused\n- are sleepier than normal or difficult to wake\nThese could be signs of shock, which is a serious complication of dehydration.\n\n\nHOW TO REDUCE THE RISK OF DEHYDRATION:\n- Drinking fluids regularly can reduce the risk of dehydration. Water or diluted sugar-free squash are good choices.\n- You should drink enough during the day so that your pee is a pale colour.\n- Drink more when there's a higher risk of dehydrating. For example, if you're being sick, sweating due to hot weather or exercise, or you have diarrhoea.\n- Children under the age of 5 and older adults should get plenty of fluids as they have an increased risk of dehydration.\n\n\nHELPING SOMEONE YOU CARE FOR:\nA person you care for may not have a sense of how much they're drinking.\n\nYou can help them by:\n- making sure they drink at mealtimes\n- making drinking a social thing\n- offering them food with a high water content – for example, soup, ice cream, jelly and fruits like melon\n\nSOURCES:\nhttps://www.nhs.uk/conditions/dehydration/"
        }
      ],
      "retrieved": true,
      "error": null
    },
    {
      "expected_document": "Whiplash.txt",
      "summary": {
        "symptoms": [
          "neck pain and stiffness several hours after a rear-end traffic collision"
        ]
      },
      "evidence_anchor": "several hours",
      "query": "Clinical guidance, and diagnostic criteria for: neck pain and stiffness several hours after a rear-end traffic collision.",
      "indexed_chunks": 2,
      "candidates": [
        {
          "file_name": "Whiplash.txt",
          "score": 0.760315656661987,
          "survived": true,
          "text": "WHIPLASH:\n\n\nOVERVIEW:\nWhiplash is a neck injury caused by sudden movement of the head. It usually gets better within 2 to 3 months, but some people may have symptoms for longer.\n \n\nSYMPTOMS OF WHIPLASH:\nWhiplash most often happens after a traffic accident or a slip or fall. Other common causes include a slip or fall, and sports injuries.\nCommon symptoms of whiplash include:\n- neck pain \n- neck stiffness and difficulty moving your head\n- headaches\n- pain and muscle spasms in the shoulders and arms\nIt can take several hours for the symptoms to start after you injure your neck.\n\n\nTHINGS YOU CAN DO TO TREAT WHIPLASH:\nThere are some things you can do to treat whiplash.\nDo:\n- take painkillers, such as paracetamol or ibuprofen, to help with pain\n- try to continue doing everyday activities – it might hurt a little but it will speed up your recovery\nDon’t:\n- do not use a neck brace or collar to support your neck – this does not help\n- do not rest your neck for long periods of time\n\n\nWHEN AND WHERE TO GET MEDICAL HELP:\nA GP can help if symptoms of whiplash are not getting better. Some symptoms need urgent medical help.\n\n\nSEE A GP IF:\n- symptoms of whiplash have not improved after 1 week\n- painkillers like paracetamol or ibuprofen have not worked\n- you're worried about the pain\n\n\nASK FOR AN URGENT GP APPOINTMENT IF:\nYou have injured your neck and:\n- you have severe pain despite taking paracetamol or ibuprofen\n- you have tingling or pins and needles on 1 or both sides of your body\n- you have problems with walking or sitting upright\n- you have a sudden \"electric shock\" feeling in your neck and back which may also go into your arms and legs\n- your hands, arms or legs feel weak\nThese symptoms could be caused by damage to the nerves in your neck or back. Do not do anything that could be dangerous, such as driving or cycling, until you have spoken to a GP."
        },
        {
          "file_name": "Whiplash.txt",
          "score": 0.6506744027137761,
          "survived": false,
          "text": "TREATMENT FOR WHIPLASH:\n- A GP may prescribe a stronger painkiller such as codeine for whiplash.\n- You should have check-ups with a GP every few weeks if you have whiplash. If your symptoms do not get any better, they may refer you:\n  * to a physiotherapist\n  * to a pain specialist\n  * for psychological support\n\n\nSOURCES:\nhttps://www.nhs.uk/conditions/whiplash/"
        }
      ],
      "retrieved": true,
      "error": null
    }
  ]
}
```


