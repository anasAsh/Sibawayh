# Sibawayh (سيبويه): Arabic Writing Skill

An open-source Agent Skill that makes AI agents write correct, natural Modern Standard Arabic (فصحى). It gives the agent a writing guide and checklist (`SKILL.md`), reference notes on grammar, orthography, style and common errors, and a dependency-free Python checker for spelling conventions, punctuation, digits and typical mistakes.

Status: in development; evaluation pending.

## Install

### Claude Code

Option 1, as a plugin from the [Sibawayh marketplace](https://github.com/anasAsh/Sibawayh):

```
/plugin marketplace add anasAsh/Sibawayh
/plugin install arabic-writing@sibawayh
```

From a shell, the same commands are `claude plugin marketplace add anasAsh/Sibawayh` and `claude plugin install arabic-writing@sibawayh`.

Option 2, clone the repo and copy or symlink the skill folder:

```bash
git clone https://github.com/anasAsh/Sibawayh.git
cd Sibawayh
ln -s "$PWD/skills/arabic-writing" ~/.claude/skills/arabic-writing
# or: cp -r skills/arabic-writing ~/.claude/skills/
```

### Cursor and GitHub Copilot

Copy `skills/arabic-writing/` into the tool's skills folder. The folder path differs per tool and version, so check each tool's documentation.

## Running the checker by hand

Requires Python 3.8+ and nothing else.

```bash
python3 skills/arabic-writing/scripts/check_arabic.py file.md          # report findings
python3 skills/arabic-writing/scripts/check_arabic.py --fix file.md    # print text with safe fixes applied
python3 skills/arabic-writing/scripts/check_arabic.py --json -         # JSON findings from stdin
```

Example: for a file whose first line is `هذا مسئول عن الملف, ثم انتهى`, the checker prints (`line:column  SEVERITY  rule  message  → suggestion`):

```
1:5  INFO  spelling-mixed  Convention: مسؤول (hamza on waw), not مسئول  → مسؤول
1:19  FIX  punct-latin  Latin punctuation between Arabic words  → ،
```

Severities are `fix`, `error`, `warn`, `info`. The exit code is 1 when there are findings above `info`, 0 otherwise.

## License

MIT, see `LICENSE`. The project contains no GPL code. Any entries adapted from LanguageTool (LGPL) would live only in `skills/arabic-writing/scripts/data/third_party/languagetool_ar.tsv`, next to `LICENSE-LGPL` and a source note.
