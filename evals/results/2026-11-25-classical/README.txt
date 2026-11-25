Trial of the classical register (references/classical.md), 2026-11-25. Method and results: ../../classical.md

baseline/         20 classical requests (../../prompts-classical.tsv) answered without the skill
skill/            the same with the skill that has the classical register (release 0.4.0)
skill-0.3.0/      the same with release 0.3.0, which has no classical register
everyday-sample/  20 of the 100 everyday requests (ids 01, 06, 11, 16 of each task) answered with release 0.4.0

Blind pairs, judged by GPT via codex exec (read-only), two judgings per comparison, each with its own A/B order:
  nb1, nb2  skill ("new") against baseline            judge-classical.md
  no1, no2  skill ("new") against skill-0.3.0 ("old") judge-classical.md
  lk1, lk2  everyday-sample ("new") against ../2026-11-23/skill ("published")  judge-everyday.md
key-*.csv: pair, id, a, b.  scores-*.csv: no header; columns as in the last lines of the judge file.
