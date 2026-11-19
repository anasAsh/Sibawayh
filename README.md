# Sibawayh (سيبويه)

**An Agent Skill that makes AI agents write correct, natural Arabic and check it before answering.**

AI models write Arabic that is understandable but often wrong or unnatural:
- English sentence structure in Arabic words;
- broken number agreement;
- the wrong hamza;
- English punctuation;
- scrambled right-to-left text whenever English terms or numbers appear.

Arabic readers notice at once. Sibawayh, named after the founding grammarian of Arabic, gives the agent the rules and a checker, so its Modern Standard Arabic (الفصحى) reads like it was written by a careful native writer.

> **Status:** usable, under evaluation. The before/after evaluation (`evals/`) has not been run yet, so there are no measured results to report.

## How it works

The skill loads whenever the agent is about to write Arabic. That covers answers, documents, emails, posts, translations, summaries, UI strings and commit messages. The agent then:

1. **Writes with the rules in mind.** The rules come from `SKILL.md`: prefer verb-first, active sentences; get agreement and numbers right; use Arabic punctuation (، ؛ ؟ « »); keep one digit system; and make the text safe for right-to-left display.
2. **Runs the checker.** `scripts/check_arabic.py` is a small Python script with no dependencies. It auto-fixes what is certain and flags the rest.
3. **Reviews against a checklist**, in priority order: agreement, numbers, case endings, إنّ/أنّ, translationese, register, formatting. It changes only what is wrong.
4. **Answers.** The user sees the final text, not the checker's output.

The script and the model split the work. The script handles mechanical errors, which it catches every time. The model handles grammar that needs understanding.

### Example

Input:

```
تم إستخدام الأداة من قبل الفريق, وهاذا ساعدنا كثيرا.
لدينا 3 ملفات و٤ مجلدات.
الملفات الذين تم رفعهم موجودين هنا
```

The checker's output (format: `line:column  SEVERITY  rule  message  → suggestion`):

```
1:1   INFO   translationese-density  Translationese density 15.8 per 100 words (تم/يتم: 2, من قبل: 1) …
1:4   ERROR  hamza-wasl    Hamzat al-wasl: write a bare alif, not إ (form X masdar)  → استخدام
1:32  FIX    punct-latin   Latin punctuation between Arabic words  → ،
1:34  ERROR  misspelling   Misspelling (no alif after ها)  → وهذا
2:16  WARN   digit-mix     Mixed digit systems; this text uses Western (0-9) digits  → 4
```

Line 3 has agreement errors that no regex can catch reliably. A non-human plural like الملفات takes feminine singular agreement in its relative pronoun, verb and predicate (التي، رُفعت، موجودة). The model's checklist catches these:

```
✗ الملفات الذين تم رفعهم موجودين هنا
✓ الملفات التي رُفعت موجودة هنا
```

## What it covers

| Area | Examples | Handled by |
|---|---|---|
| Punctuation | `,` `?` `;` → ، ؟ ؛ and spacing | Checker (auto-fix) |
| Unicode | Persian ک/ی, presentation forms, tatweel | Checker (auto-fix or warn) |
| Spelling | إستخدام, هاذا, لاكن, الى, إنشاء الله, ة/ه, ى/ي | Checker (word lists) |
| Digits and RTL | mixed 3 and ٣; lines that start with an English word or a digit | Checker |
| Dialect leakage | عشان, بدي, هيك in formal text | Checker |
| Verb endings | لم يكونون, لن يذهبون, سوف لن | Checker plus checklist |
| Agreement and numbers | non-human plurals, ثلاث مهندسين, العدد والمعدود | Checklist and reference tables |
| Translationese | تم + masdar, قام بـ, من قبل, كـ "as a" | Checker (density) plus checklist |
| Technical terms | standard Arabic term with the English term in parentheses | Glossary (450+ terms) |

The design rests on one rule: **never over-correct.** Forms that purists reject but the Cairo Arabic Language Academy approved, such as يعتبر، ساهم في، أكد على، في نفس الوقت and أبحاث, are never flagged. Contested forms are left alone. Auto-fixes only apply where they can't be wrong.

## Install

### Claude Code

As a plugin:

```
/plugin marketplace add anasAsh/Sibawayh
/plugin install arabic-writing@sibawayh
```

From a shell, the same commands are `claude plugin marketplace add anasAsh/Sibawayh` and `claude plugin install arabic-writing@sibawayh`.

Or copy or symlink the skill folder:

```bash
git clone https://github.com/anasAsh/Sibawayh.git
cd Sibawayh
ln -s "$PWD/skills/arabic-writing" ~/.claude/skills/arabic-writing
# or: cp -r skills/arabic-writing ~/.claude/skills/
```

### Cursor, GitHub Copilot and other agents

Copy `skills/arabic-writing/` into the tool's skills folder. The path differs per tool and version, so check that tool's documentation. The skill uses the standard `SKILL.md` format. If an agent has no shell, it falls back to the checklist alone.

## Running the checker by hand

It needs Python 3.8 or later and nothing else.

```bash
python3 skills/arabic-writing/scripts/check_arabic.py file.md          # report findings
python3 skills/arabic-writing/scripts/check_arabic.py --fix file.md    # print the text with safe fixes applied
python3 skills/arabic-writing/scripts/check_arabic.py --json -         # JSON findings from stdin
```

- **Options:** `--digits western|arabic|auto` sets the expected digit system. The default, `auto`, follows the majority in the text.
- **Severities:** `fix` (applied by `--fix`), `error`, `warn`, `info`.
- **Exit code:** 1 when findings above `info` remain, otherwise 0.
- **Skipped regions:** code blocks, inline code, URLs, file paths, emails, YAML front matter, Qur'an quotes in ﴿…﴾, and anything between `<!-- arabic-check: off -->` and `<!-- arabic-check: on -->`.

## Repository layout

```
skills/arabic-writing/
  SKILL.md                 the agent's writing rules, workflow and checklist
  references/              grammar, orthography, style, common errors,
                           approved forms, tech glossary
  scripts/check_arabic.py  the checker (stdlib only)
  scripts/archeck/         checker rules
  scripts/data/            word lists (misspellings, hamza, dialect, approved forms, …)
evals/                     before/after evaluation harness (see evals/README.md)
tests/                     unit tests: python3 -m unittest discover -s tests -t .
research/                  the research notes the rules are based on
docs/                      design and implementation plan
```

## Contributing

Native speakers' review is the most valuable contribution, and these areas need it most:
- **Glossary** (`references/glossary.md`): better or more standard terms. Some terms have no settled Arabic equivalent yet, for example epoch, tokenization and pipeline.
- **Word lists** (`scripts/data/*.tsv`): a new entry must be wrong in *every* context. Add a test in `tests/` for each one.
- **False flags:** if the checker flags correct Arabic, open an issue with the sentence.

Run the tests before opening a pull request:

```bash
python3 -m unittest discover -s tests -t .
```

## License

MIT, see [`LICENSE`](LICENSE). The project contains no GPL code. Any entries adapted from LanguageTool (LGPL) would live only in `skills/arabic-writing/scripts/data/third_party/` with their own licence notice.
