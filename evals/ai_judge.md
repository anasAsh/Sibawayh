# AI-judge pilot

A preliminary check that doesn't need a human scorer. It isn't a replacement for human scoring: AI models are only moderately reliable at judging Arabic grammar.

## How the pilot was run (2026-11-20)

1. Pair the outputs. For each prompt, the baseline and skill outputs were placed in random A/B order in `pairs/pair-NN.md`, together with the prompt. The A/B key was kept outside the judge's folder.
2. Judge with a model from a different family. GPT (through Codex) judged the pairs blind, so Claude wasn't grading its own output.
3. Unblind. Counts and preferences were mapped back to baseline or skill using the key.

## Judge prompt

> You are an expert Arabic editor (Modern Standard Arabic), acting as a blind judge. Each file in `pairs/` contains a user prompt and two anonymous AI responses, A and B.
>
> For EACH response, count concrete errors in these categories:
> - **grammar**: agreement (including non-human plural → feminine singular), number–noun agreement, visible case endings, verb mood after لم/لن/أن, إنّ/أنّ, idafa, relative pronouns, conditionals;
> - **spelling**: hamza, ة/ه, ى/ي, tanween alif, joined/split words;
> - **translationese**: clear English calques (تم + masdar where a direct verb fits, قام بـ + masdar, passive + من قبل, كـ "as a", بشكل + adjective, unnatural subject-first order);
> - **register**: dialect words, English words outside parentheses or code, English sentences or notes in an Arabic answer;
> - **formatting**: Latin punctuation (, ; ?) in Arabic text, wrong spacing around punctuation, mixed digit systems, a line or bullet whose *first word* is Latin. Numbered-list markers (`1.`), counters like `(1/4)`, and numbers or percentages inside a sentence are **not** errors.
>
> Do not count Cairo-Academy-approved forms (يعتبر، ساهم في، أكد على، أجاب على، في نفس الوقت، تخرج من، أبحاث، مدراء، إحصائيات، حوالي، كافة، هام، تواجد) or contested forms (طالما، بينما، سويًّا). Ignore code blocks, URLs, product names and placeholders. Count only language errors, not content differences. When unsure, don't count.
>
> Then give an overall preference: which response reads as more correct and natural Arabic (A, B or tie).

The formatting line above is clearer than the one used in the first pilot. That run counted numbered lists and thread counters as formatting errors, which inflated the formatting counts equally on both sides.

## Pilot result (10 prompts, 2 per task type)

- **Preference:** skill 7, baseline 1, tie 2.
- **Errors**, by category:

  | Category | Baseline | Skill |
  |---|---|---|
  | grammar | 2 | 0 |
  | spelling | 0 | 0 |
  | translationese | 6 | 0 |
  | register | 4 | 4 |
  | formatting | 12 | 11 |

  Formatting is mostly judge noise; see the note above.
- **One real miss on the skill side:** the skill's answer to docs-02 wrote its closing notes in English. This led to the `english-line` checker rule and the "whole answer in Arabic" rule in `SKILL.md`.
