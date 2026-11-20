# Checks on edited text: over-correction and recall

The golden rule is "never flag correct Arabic". This check measures it without a human scorer: run the checker on edited, published Arabic and review every finding by hand.

## How to run it

```bash
python3 evals/fetch_wiki.py --limit 50          # Arabic Wikipedia featured articles → evals/corpus/wiki/
python3 evals/corpus_check.py evals/corpus/wiki # counts per rule, plus samples in context
python3 evals/inject.py evals/corpus/wiki       # recall: inject one known error per line
python3 evals/fetch_wiki.py --skip 50 --limit 50 --out evals/corpus/wiki-heldout
```

`corpus_check.py` takes any folder of `.txt` or `.md` files, so other clean corpora can be dropped in. Downloads go to `evals/corpus/`, which is gitignored.

## Result (2026-11-20, 50 featured articles, 416,602 words)

| Rule | Severity | Count | Reviewed | False flags |
|---|---|---|---|---|
| misspelling | error | 21 | all | 0 |
| hamza-wasl | error | 8 | all | 0 |
| punct-space | fix | 214 | 20 sampled | 0 |
| tatweel | fix | 44 | sampled | 0 (removes the ـ in بـديجيمون; harmless) |
| persian-letter | fix | 19 → 18 | all | 1, now fixed |
| punct-latin | fix | 2 | all | 0 |
| alif-maqsura | warn | 3 | all | 3 (the surname حتي, Philip Hitti) |
| dialect-word | warn | 2 | all | 2 (the transliterated names شو and هيك) |
| hamza-missing | warn | 1 | all | 1 (انتم inside a table of Sindhi letters) |
| english-line, rtl-line-start | warn | 69 | sampled | expected: English bibliography lines |

- **Errors: 29 flags, 0 false.** Even featured articles contain إثنين، الإتجاه، شئ، دعى، ابتداءًا، يتسائل، عن ما، لاسيما.
- **Fixes: 1 wrong auto-fix in 278.** It converted a Persian ک cited on its own in a table of alphabets. The rule now leaves a lone cited letter alone (test added).
- **Warnings:** the 6 false warnings are all proper names or cited letters. Warnings ask the model to look at the context, so these are acceptable. A name list isn't worth maintaining.

## Limits

- Wikipedia is edited but not professionally proofread; that's why it contains real errors.
- The 50 articles are the first 50 in category order (titles starting with آ and أ), not a random sample.
- This measures false flags only. For recall, see below.

## Recall with injected errors

`inject.py` picks 200 random sites per error type in the clean text, injects one error at a time (for example ،→, or أ→ا), runs the checker on that line and counts the error as caught when a finding covers it. Sites where the clean line already had a finding are skipped.

The word lists were grown from the first set's frequency list, so the honest number is on a **held-out set**: the next 50 featured articles (389,907 words), not used for any change.

| Error injected | Before | **After** |
|---|---|---|
| Latin punctuation (، → ,) | 89% | **89%** |
| Space before ، | 100% | **100%** |
| Wasl alif written إ (الإستخدام) | 22% | **64%** |
| Missing hamza (أ/إ → ا) | 18% | **39%** |
| ة → ه | 5% | **5%** |
| ى → ي | 10% | **10%** |
| ي → ى | 42% | **42%** |
| Persian letter, tatweel | 100% | **100%** |
| Mixed digit systems | 99% | **99%** |
| لم/لن/أن + verb keeping its ن | 97% | **97%** |
| سوف لن | 97% | **97%** |
| هاذا، لاكن، ذالك | 98% | **98%** |

Both columns are on the held-out set, before and after the changes below (on the first set: wasl 33% → 70%, missing hamza 16% → 43%).

What changed:
- **hamza-wasl** also matches the shape of form VII, VIII and X masdars (إنفعال، إفتعال، إستفعال), not only listed words. Form IV masdars (إنتاج، إنفاق) are one letter shorter and never match. Loanwords of the same shape (إستراتيجية، الإنكشارية) are excluded.
- **hamza-missing** has 64 more words, each wrong without its hamza in every context (ان، انه، الا، اهل، الاسلام…). It also ignores cited endings such as ـان.
- **jussive-nun** covers بأن.

On the held-out set, the over-correction check found 0 false errors in 62 error flags. The 4 false warnings were the names بيغ شو (Big Show) and the Sindhi letter table. The Persian-letter fix also converts letters inside a quoted Persian inscription, a rare case left as is.

What stays low, by design:
- **ة/ه and ى/ي** are ambiguous without grammar: مدرسه is wrong, but عليه and فيه are right; إلي and علي are real words. These are left to the model's checklist.
- **Missing hamza** is capped by how many words can be listed safely. ان is always wrong, but بان and لان are real words, so prefixed forms are listed one by one.
- **Latin punctuation next to digits or Latin words** (1929, ثم) is left alone, because 1,000 is a number.
