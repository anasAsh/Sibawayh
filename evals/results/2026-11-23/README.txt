100 prompts (evals/prompts.tsv). Ids 01-10 of each task: answers reused unchanged (baseline from ../2026-11-20/, skill from ../2026-11-22-run2/).
Ids 11-20: prompts added 2026-11-23 and answered once per side with the skill at commit 3ea71e1.
Judged three times, blind, by GPT via codex exec (read-only), each with its own A/B seed; prompt as in ../../ai_judge.md.
marks-2304.tsv: a fourth blind pass (2026-11-24, seed 2304, key in marks-key-2304.csv) in which the same judge quoted each error and a fix
(pair, response, category, quote, fix); prompt in marks-prompt.md (PAIRS_LIST = ten pair files per batch). It is used only for the highlights
on the results page, not for the scores: 459 quoted errors without the skill (2.39 per 100 words), 20 with it (0.10).
