# Full evaluation: 100 prompts, with and without the skill

A plain-language description of all the tests is at <https://anasash.github.io/Sibawayh/>.

## Latest: 2026-11-25, release 0.4.0, 100 prompts, judged three times

The skill side was answered again with release 0.4.0 (which adds the classical register, used only on request). The baseline answers are the same files as on 2026-11-23. GPT (through Codex) judged all 100 pairs blind three times, each time with its own random A/B order.

| Judging | Baseline | Skill | Change | Preferred (skill–baseline–tie) |
|---|---|---|---|---|
| 1 | 2.18 | 0.05 | −98% | 92–4–4 |
| 2 | 2.25 | 0.07 | −97% | 93–3–4 |
| 3 | 2.34 | 0.09 | −96% | 92–4–4 |
| **Mean** | **2.26** | **0.07** | **−97%** | |

Errors per 100 words (19,181 baseline words, 22,344 skill words). Over-corrections: 0 in all three. The success bar passes in all three.

| Errors per 100 words (mean) | Baseline | Skill |
|---|---|---|
| Grammar | 0.13 | 0.01 |
| Spelling | 0.01 | 0.00 |
| Translationese | 0.39 | 0.05 |
| Register | 1.50 | 0.01 |
| Formatting | 0.24 | 0.00 |

| Errors per 100 words (mean) | Baseline | Skill | Change |
|---|---|---|---|
| First 50 prompts (used during development) | 2.15 | 0.01 | −99% |
| 50 new prompts (not used for tuning) | 2.37 | 0.12 | −95% |
| Technical explanations | 4.41 | 0.05 | −99% |
| Documentation | 1.74 | 0.11 | −94% |
| Social posts | 1.72 | 0.06 | −97% |
| Translations | 0.93 | 0.13 | −86% |
| Emails | 0.31 | 0.01 | −97% |

The skill's raw error counts were 12, 15 and 20 (11–12 of them translationese), against 18–20 on 2026-11-23. Its answers were also about 12% longer. Answers are generated once per run and vary from run to run: a trial regeneration earlier the same day, with reference edits that were then reverted, scored 0.09–0.13. So the step from −96% to −97% is within run-to-run variation and is not evidence that release 0.4.0 writes better everyday Arabic. What the run does show is that adding the classical register did not make everyday answers worse.

A fourth blind pass in which the judge quotes each error (`marks-2504.tsv`) feeds the highlights on the [results page](https://anasash.github.io/Sibawayh/results/).

**Limits:** as below: one generation per prompt, and an AI judge. Raw data: [`results/2026-11-25/`](results/2026-11-25/).

## 2026-11-23, 100 prompts, judged three times

50 prompts were added to [`prompts.tsv`](prompts.tsv) (ids 11–20 of each task type), written after the skill's last change. Both sides answered them once. The first 50 pairs are the same files as in the 2026-11-22 run. GPT (through Codex) judged all 100 pairs blind three times, each time with its own random A/B order.

| Judging | Baseline | Skill | Change | Preferred (skill–baseline–tie) |
|---|---|---|---|---|
| 1 | 2.29 | 0.10 | −96% | 90–1–9 |
| 2 | 2.20 | 0.09 | −96% | 86–5–9 |
| 3 | 2.16 | 0.09 | −96% | 86–3–11 |
| **Mean** | **2.22** | **0.10** | **−96%** | |

Errors per 100 words (19,181 baseline words, 20,015 skill words). Over-corrections: 0 in all three. The success bar passes in all three.

| Errors per 100 words (mean) | Baseline | Skill |
|---|---|---|
| Grammar | 0.10 | 0.01 |
| Spelling | 0.02 | 0.00 |
| Translationese | 0.40 | 0.07 |
| Register | 1.45 | 0.00 |
| Formatting | 0.24 | 0.01 |

| Errors per 100 words (mean) | Baseline | Skill | Change |
|---|---|---|---|
| First 50 prompts (used during development) | 2.04 | 0.08 | −96% |
| 50 new prompts (never seen before) | 2.40 | 0.11 | −95% |
| Technical explanations | 4.33 | 0.15 | −97% |
| Documentation | 1.76 | 0.10 | −94% |
| Social posts | 1.64 | 0.07 | −96% |
| Translations | 0.91 | 0.07 | −93% |
| Emails | 0.27 | 0.02 | −92% |

About two thirds of the baseline's errors are register errors (277–281 of 419–439), mostly English terms in technical explanations. The skill's remaining errors are mostly translationese (12–17 of 15–20).

**Limits:** as below: one generation per prompt, and an AI judge. Raw data: [`results/2026-11-23/`](results/2026-11-23/).

## 2026-11-22: 50 prompts, judged three times

The skill answered all 50 prompts again, after the changes listed below. The baseline answers are the same files as in the 2026-11-20 run. GPT (through Codex) judged the 50 pairs blind **three times**, each time with its own random A/B order, using the prompt in [`ai_judge.md`](ai_judge.md).

| Judging | Baseline | Skill | Change | Preferred (skill–baseline–tie) |
|---|---|---|---|---|
| 1 | 1.90 | 0.11 | −94% | 46–0–4 |
| 2 | 2.17 | 0.08 | −96% | 42–2–6 |
| 3 | 1.98 | 0.07 | −96% | 43–3–4 |
| **Mean** | **2.02** | **0.09** | **−96%** | |

Errors per 100 words. Over-corrections: 0 in all three. The success bar passes in all three.

| Errors per 100 words (mean) | Baseline | Skill |
|---|---|---|
| Grammar | 0.10 | 0.01 |
| Spelling | 0.01 | 0.00 |
| Translationese | 0.44 | 0.06 |
| Register | 1.31 | 0.00 |
| Formatting | 0.16 | 0.01 |

**What changed since 2026-11-20:**
- `SKILL.md`: no bare English word or acronym in an Arabic sentence, not even HTTP, REST or a button label; after first use, write the Arabic term. Register errors went from 18 to 0.
- A new `calque` checker rule for English idioms translated word for word (يصنع الفرق، جعلوا … ممكنًا، يضع … تحت الضغط), more idioms in `references/style.md` §4.1, and a sentence-by-sentence idiom check for posts and translations.

**The judge's own noise:** the same 50 baseline files scored 1.66 in the first judging and 1.90–2.17 in this run's three, so compare the change within a judging, not raw numbers across runs. An intermediate run (one judging, before the two changes above) scored 2.04 → 0.32 (−84%).

**Limits:** the answers were generated once, so the variation between generation runs is not measured, and a single bad answer moves the total by about 0.1 per 100 words. The judge is an AI model, not a native reader. Raw data: [`results/2026-11-22-run2/`](results/2026-11-22-run2/) (three keys and score files) and [`results/2026-11-22/`](results/2026-11-22/) (the intermediate run).

## First run: 2026-11-20

Claude Code answered all 50 prompts in [`prompts.tsv`](prompts.tsv) twice: once without the skill (baseline) and once with release 0.2.0. These are 10 each of emails, social posts, documentation, technical explanations and translations, in Arabic and in English. A model from a different family (GPT, through Codex) judged the 50 pairs blind, with the method and instructions of the [AI-judge pilot](ai_judge.md).

### Result

| Errors per 100 words | Baseline | Skill | Change |
|---|---|---|---|
| Grammar | 0.11 | 0.00 | −100% |
| Spelling | 0.28 | 0.03 | −89% |
| Translationese | 0.29 | 0.07 | −75% |
| Register | 0.84 | 0.09 | −89% |
| Formatting | 0.14 | 0.00 | −100% |
| **Total** | **1.66** | **0.20** | **−88%** |

- **Preference:** skill 29, baseline 1, tie 20.
- **Over-corrections:** 0.
- **Success bar** (0 over-corrections, at most 50% of the baseline's errors, no category worse): **pass**.
- **By task** (total errors, baseline → skill): technical explanations 112 → 9, documentation 20 → 5, social posts 20 → 3, translations 6 → 2, emails 3 → 0.
- **Words:** 9,686 (baseline) and 9,696 (skill), so the answers are the same length.

Most of the baseline's errors were register and spelling errors in technical explanations: untranslated English terms outside parentheses (Caching, Hypervisor, B-Tree), the article written apart before an English word (الـ API), and lines starting with a Latin word. It also slipped into Gulf dialect in a social post that asked for nothing of the kind (وش، تبي، اللي).

### The skill's remaining errors

19 errors in 50 answers. They led to changes after the run:

- **8** in one answer: HTTP methods (GET، POST) written bare in headings and text. SKILL.md now lists HTTP methods, commands, flags and file names as code to keep in backticks.
- **7 translationese**, mostly English idioms translated word for word (يصنع الفرق، أفكار بقيت معي، يعيد تشكيل الطريقة التي…). They are now in `references/style.md` §4.1. The one pair where the judge preferred the baseline (translate-03) was this kind of error.
- **3 spelling**: بـ written apart from a following code span (بـ `good-first-issue`). Writing a prefix apart before Latin text is common practice, so this one is left as is.
- **1 register**: a Latin word outside code in a heading.

### How it was run

```bash
python3 evals/generate.py --mode baseline
python3 evals/generate.py --mode skill
python3 evals/pair.py evals/judge evals/judge-key.csv   # blind A/B pairs; the key stays outside the judge's folder
# judge pairs/ in batches of 10 with the prompt in ai_judge.md
python3 evals/judge_report.py evals/judge-scores.csv evals/judge-key.csv
```

- **Isolation:** both modes ran with `--setting-sources project`, so an installed copy of the plugin could not load the skill in baseline runs. A test run confirmed that it loads without the flag and not with it.
- **Files:** four answers (docs-05 and docs-06 in baseline mode; docs-06 and docs-10 with the skill) saved their document to a file and only summarised it in the reply. The harness deleted those files, so `generate.py` now appends any file the model writes. Those four were regenerated, and their pairs were judged again.
- **Judge instructions:** the judge was told that when a prompt is in English, English notes to the user outside the Arabic text are not errors. Without that rule, both sides are penalised for notes that are correct.
- **Raw data:** every answer, the blind key and the judge's scores are in [`results/2026-11-20/`](results/2026-11-20/).

### Limits

- **An AI judge, not a human.** AI models are only moderately reliable at judging Arabic grammar. The judge is from a different family from the model being judged, and it was blind, but a native-speaker score is still needed to confirm the size of the effect.
- **One run per prompt.** Answers vary from run to run, and no repeat runs were made.
- **Mid-run change:** a lexicon exception (وانسَ) was added while the skill answers were being generated. It affects one rare word.
