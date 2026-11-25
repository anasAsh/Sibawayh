# Classical register: first trial

Release 0.4.0 adds a classical register (فصحى التراث) that the skill uses only when the request asks for it. This is a first, small trial of it, run on 2026-11-25. It is separate from the main evaluation in [`full_eval.md`](full_eval.md), whose figures describe everyday Modern Standard Arabic.

## Method

- 20 requests for classical or elevated literary Arabic ([`prompts-classical.tsv`](prompts-classical.tsv)): sermons, letters, a maqama, a counsel, a literary debate, rewrites and translations.
- Claude Code answered each one three ways: without the skill, with release 0.3.0 (no classical register), and with release 0.4.0.
- GPT judged blind pairs, twice per comparison. For each answer it counted grammar and spelling errors, modern clichés, forced rhyme or obscure wording, and invented quotations, and gave a score from 1 to 5 for how classical the answer reads. The instructions are in [`results/2026-11-25-classical/judge-classical.md`](results/2026-11-25-classical/judge-classical.md).
- Leak check: 20 of the 100 everyday requests were answered with release 0.4.0 and paired blind with the published answers. The judge counted classical wording that is out of place in an everyday answer.

## Results

Totals over 20 answers; the two figures are the two judgings. The no-skill and 0.4.0 columns come from the pairs of 0.4.0 against no skill; the 0.3.0 column comes from the pairs of 0.4.0 against 0.3.0, where 0.4.0 scored 4.58–4.65 for classical style and 17–19 for forced wording.

| | No skill | Release 0.3.0 | Release 0.4.0 |
|---|---|---|---|
| Classical score, mean (1–5) | 4.05, 3.95 | 4.40, 4.42 | 4.74, 4.68 |
| Forced rhyme or obscure wording | 45, 42 | 26, 32 | 11, 15 |
| Modern clichés | 14, 14 | 6, 6 | 1, 3 |
| Grammar and spelling errors | 2, 2 | 2, 1 | 3, 2 |
| Invented quotations | 0, 1 | 0, 1 | 0, 0 |

- Against no skill, the judge preferred release 0.4.0 in 17 and 19 of the 20 pairs.
- Against release 0.3.0, it preferred release 0.4.0 in 12 and 12, and release 0.3.0 in 7 and 8.
- Leak check: the judge found no classical wording in the everyday answers of release 0.4.0, in either judging.

## Limits

- 20 requests, each answered once per side. This is a trial, not a benchmark.
- An AI model is a weaker judge of classical style than of error counts, and no native reader has scored these answers.
- Release 0.4.0 still averages close to one forced or obscure item per answer.
- The judge counted 2 spelling errors in the 0.4.0 answers in every judging, against 0 or 1 for the others. They have not been reviewed.

The answers, keys and score files are in [`results/2026-11-25-classical/`](results/2026-11-25-classical/).
