# Evaluation harness

Compares Claude Code with and without the `arabic-writing` skill. Stdlib only.
Needs the `claude` CLI logged in. Each run uses your Claude usage.

Both scripts refuse to run if `~/.claude/skills/arabic-writing` exists (it
would contaminate the baseline). They only check that path; unlink it
yourself and relink afterwards.

Skill mode copies the skill into the temp dir (no symlink), so a model with
Write cannot modify the real skill. The baseline can still be contaminated by
a plugin install of the skill, or by user-level CLAUDE.md and hooks. Check
`/plugin` before running.

## 1. Trigger test

    python3 evals/run_triggers.py [--limit N]

Runs the 20 prompts in `triggers.tsv` with the skill copied into a temp dir
and checks for a `Skill` tool use naming `arabic-writing`. Expected values:
`load`, `no_load`, and `format_only`. `format_only` (dialect requests) is
judged manually for behaviour: the skill should only fix formatting and leave
the dialect alone. The automated check counts it as `load`, since the skill
still loads.

## 2. Generate responses

    python3 evals/generate.py --mode baseline
    python3 evals/generate.py --mode skill [--only email-01]

100 prompts (`prompts.tsv`, 20 each of email, docs, social, tech_explain,
translate). Output goes to `evals/outputs/<mode>/<id>.txt`; existing files are
skipped, failures are written to `<id>.error` (300 s timeout per call). Both
modes allow the same tools, `Bash(python3:*)`, `Read`, `Write`, so the skill
can run its checker and the baseline is not handicapped by tool access.

## 3. Blind scoring

    python3 evals/shuffle.py

Copies outputs to `evals/blind/<random-id>.txt` and writes the private
`evals/blind_key.csv`. Score the blind files without opening the key. Both
are gitignored.

## 4. Fill the rubric

`rubric.csv` has one row per id x mode. For each response count, as integers:
`grammar`, `spelling`, `translationese`, `register`, `formatting` (RTL and
punctuation layout), and `over_corrections` (a correct form the skill made
wrong; fill on skill rows). Leave unscored rows completely blank; they are
ignored. A partly filled row, a scored skill row without `over_corrections`,
an unresolved blind id, or a scored row without an output file stops the
report with an error (exit 2).

For blind scoring, replace `id` with the blind id and leave `mode` empty.
You cannot tell which blind rows are skill rows, so fill `over_corrections`
on every blind row you score (0 if none). The report requires it on rows the
key resolves to skill. Errors on blind rows name only the blind id, so they
do not unblind you.

## 5. Report

    python3 evals/report.py [--rubric evals/rubric.csv] [--outputs evals/outputs]

Prints rubric errors per 100 words (the headline; word counts come from the
output files), checker counts by family (supporting detail only: skill output
has already passed the checker), then `PASS` or `FAIL`. The bar: zero
over-corrections, skill total <= 50% of baseline total, and no category worse.

## Other checks

- [`full_eval.md`](full_eval.md): all 100 prompts, judged blind by an AI model (errors −96%, mean of three judgings).
- [`classical.md`](classical.md): first trial of the classical register (20 requests, AI-judged).
- [`ai_judge.md`](ai_judge.md): the AI-judge method, and the 10-pair pilot.
- [`corpus_check.md`](corpus_check.md): the over-correction check on edited Arabic (Wikipedia featured articles), and recall with injected errors. No human scorer needed.
- [`benchmarks.md`](benchmarks.md): recall against ZAEBUC and QALB, essays and comments that people corrected by hand.
- `build_results_page.py`: rebuilds the [full results page](https://anasash.github.io/Sibawayh/results/) (`docs/results/`, `docs/ar/results/`) from a judged run in `results/`.
- `build_lexicon.py`: rebuilds the checker's frequency lexicons (`scripts/data/lexicon_*`) from downloaded Wikipedia text.
