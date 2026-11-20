# Over-correction check on edited text

The golden rule is "never flag correct Arabic". This check measures it without a human scorer: run the checker on edited, published Arabic and review every finding by hand.

## How to run it

```bash
python3 evals/fetch_wiki.py --limit 50          # Arabic Wikipedia featured articles → evals/corpus/wiki/
python3 evals/corpus_check.py evals/corpus/wiki # counts per rule, plus samples in context
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
- This measures false flags only. Recall needs error-annotated data (QALB, ZAEBUC) or synthetic errors.
