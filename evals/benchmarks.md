# Benchmarks: essays and comments corrected by people

The checker scored against two public Arabic error-correction corpora, where annotators corrected every word by hand and [ARETA](https://github.com/CAMeL-Lab/arabic-areta) labelled each correction by error type.

| Corpus | What it is | Size used | Licence |
|---|---|---|---|
| **ZAEBUC** | Essays by first-year students at Zayed University (UAE) | dev + test, 9,932 words | CC BY-NC-SA 4.0 |
| **QALB-2014** | Online news comments by native speakers | test, 50,309 words | research and evaluation only |

Neither corpus is redistributed here. Get the token-aligned files from [CAMeL-Lab/arabic-gec](https://github.com/CAMeL-Lab/arabic-gec/tree/master/data/areta_tags/wo_camelira) and run:

```bash
python3 evals/gec_eval.py evals/corpus/zaebuc/zaebuc_{dev,test}.areta.txt
python3 evals/gec_eval.py evals/corpus/qalb/qalb14_test.areta.txt
```

**Recall** is the share of erroneous words that a checker finding covers. The text is tokenized (a space before every punctuation mark), so `punct-space` is not scored.

## Result (2026-11-20)

| Error type (ARETA tag) | ZAEBUC 0.1.2 | ZAEBUC **now** | QALB 0.1.2 | QALB **now** |
|---|---|---|---|---|
| Hamza (OH) | 41% | **68%** | 35% | **59%** |
| و written apart (SP) | 0% | **98%** | 0% | **86%** |
| ة/ه (OT) | 5% | **43%** | 4% | **41%** |
| ى/ي (OA) | 14% | 14% | 26% | **40%** |
| Missing alif after plural و (OW) | 0% | 17% | 3% | 19% |
| يا/لا/ما joined to the next word (MG) | 0% | 25% | 0% | 13% |
| Wrong letter (OR) | 2% | 12% | 5% | 14% |
| **All error types** | **23%** | **53%** | **20%** | **42%** |

The checker's suggestion matches the annotators' correction in 80% (ZAEBUC) and 91% (QALB) of the single-word errors it catches.

All error types includes grammar, word choice and punctuation choices (. or ،), which a script cannot judge and the skill leaves to the model's checklist. On the six spelling types in the table above (hamza, و apart, ة/ه, ى/ي, plural alif, joined particles), recall is 69% on ZAEBUC and 56% on QALB.

## False flags

Every flag on a word the annotators left unchanged was reviewed:

- **ZAEBUC:** 170 Latin commas that this corpus's annotators chose not to convert, 1 real error they missed (بناءا), and 1 counting artifact (ثمانية ساعات is flagged as one finding over two words, of which the annotators changed only the first).
- **QALB:** 83 flags, all errors the annotators left in: عن ما، ان شاء الله، فى، ثلاثة سنوات، الإنشقاق، اسرائيل، and dialect words (QALB keeps dialect).

Two real false flags found during development, واهم ("deluded") and والاهم ("allied with them"), are now excluded: the و in them belongs to the root, not the conjunction.

## What changed to get here

- **waw-split (auto-fix):** و "and" written apart from its word (و الكتاب → والكتاب). In 450 Wikipedia articles every standalone و before a word was an error.
- **Frequency lexicons** built from 3.7 million words of Arabic Wikipedia featured articles (`evals/build_lexicon.py`). An entry says that clean text almost always writes a word with a hamza, ة, ي or a final alif, and almost never without it. They raise warnings, not errors, and each kind is limited to shapes where the other spelling is not a real word:
  - hamza: not اCC or اCCC, which are also imperatives (انسَ، اجلس، اسأل);
  - ة: only definite words (a definite word cannot take a pronoun suffix, while مكتبه "his office" is a word), and common nisba adjectives (سلبيه), but not فاعية (باقيه "the rest of it");
  - ى for a final ي: only definite words and long stems, never verbs (يُسمى/يسمي، نادى/نادي);
  - the plural alif: only past-tense verbs (كانو), not imperfects (أدعو، يرجو).
- **merged-particle:** يا، لا، ما joined to a frequent word, unless the joined form appears in clean text (ياسر، لاعب) or is a لا-compound (لاسلكي).
- **maqsura-medial:** ى inside a word (وساىل → وسائل).
- **number-gender:** 3–10 with a counted noun of the wrong gender (ثلاث ملفات، خمسة دول), from a list of 90 plurals with unambiguous singulars. On the Wikipedia sets reviewed, every flag was a real error, even in featured articles (ثلاثة سنوات، خمسة دول).
- **Misspellings:** اللتي، اللذي، هدا، مادا، هولاء.
- **hamza-wasl** catches form VII, VIII and X masdars by shape, and **hamza-missing** has 64 more always-wrong bare words (see [corpus_check.md](corpus_check.md)).

## Limits

- QALB comments are informal and partly dialect, so they contain error types an MSA writer rarely makes. ZAEBUC is closer to formal writing.
- Lexicon warnings rely on word frequency in Wikipedia, so a rare but correct spelling can be flagged. That is why they are warnings: the model reads the context before changing anything.
