# Evaluation harness

Compares Claude Code with and without the `arabic-writing` skill. Stdlib only.
Needs the `claude` CLI logged in. Each run uses your Claude usage.

Both scripts refuse to run if `~/.claude/skills/arabic-writing` exists (it
would contaminate the baseline). They only check that path; unlink it
yourself and relink afterwards.

## 1. Trigger test

    python3 evals/run_triggers.py [--limit N]

Runs the 20 prompts in `triggers.tsv` with the skill linked into a temp dir
and checks for a `Skill` tool use naming `arabic-writing`. Expected values:
`load`, `no_load`, and `format_only`. `format_only` (dialect requests) is
judged manually for behaviour: the skill should only fix formatting and leave
the dialect alone. The automated check counts it as `load`, since the skill
still loads.

## 2. Generate responses

    python3 evals/generate.py --mode baseline
    python3 evals/generate.py --mode skill [--only email-01]

50 prompts (`prompts.tsv`, 10 each of email, docs, social, tech_explain,
translate). Output goes to `evals/outputs/<mode>/<id>.txt`; existing files are
skipped, failures are written to `<id>.error` (300 s timeout per call). Skill
mode allows `Bash(python3:*)`, `Read`, `Write` so the skill can run its
checker.

## 3. Blind scoring

    python3 evals/shuffle.py

Copies outputs to `evals/blind/<random-id>.txt` and writes the private
`evals/blind_key.csv`. Score the blind files without opening the key. Both
are gitignored.

## 4. Fill the rubric

`rubric.csv` has one row per id x mode. For each response count, as integers:
`grammar`, `spelling`, `translationese`, `register`, `formatting` (RTL and
punctuation layout), and `over_corrections` (a correct form the skill made
wrong; fill on skill rows). Leave unscored rows blank; they are ignored.
For blind scoring, replace `id` with the blind id and leave `mode` empty.

## 5. Report

    python3 evals/report.py [--rubric evals/rubric.csv] [--outputs evals/outputs]

Prints rubric errors per 100 words (the headline; word counts come from the
output files), checker counts by family (supporting detail only: skill output
has already passed the checker), then `PASS` or `FAIL`. The bar: zero
over-corrections, skill total <= 50% of baseline total, and no category worse.
