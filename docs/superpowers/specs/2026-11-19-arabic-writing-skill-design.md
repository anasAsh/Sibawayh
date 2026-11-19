# Arabic Writing Skill — Design

**Date:** 2026-11-19 · **Owner:** Anas Al-Hamdan · **Status:** draft for approval

Background research (read these while building; they hold the actual rules and examples):
- `research/01-grammar.md` — agreement, numbers, visible case endings, idafa, conditionals, prepositions
- `research/02-orthography-punctuation.md` — hamza, ة/ه, ى/ي, punctuation, digits, Unicode, RTL
- `research/03-style-errors-tools.md` — common-errors list with status tags, translationese, LLM-specific errors, tool survey

Owner's project brief: the Claude Doc "Arabic Writing Skill for AI Models" (problem, goal, scope, evaluation). This spec is consistent with it and is the authority for building; where the brief is less specific, follow this spec.

## 1. Intent

AI models write Arabic that is understandable but often wrong or unnatural: English sentence structure in Arabic words, broken number agreement, wrong hamza, English punctuation, and scrambled right-to-left text when English terms or numbers appear. Arabic readers notice at once, and it undermines trust.

The skill makes an agent's Arabic grammatically correct, idiomatic and consistently formatted, and has the agent check its Arabic before the answer goes out. It is open source, portable across agents that support skills (Claude Code first; Cursor, Copilot and others that read `SKILL.md`), and is meant to grow as a community project (JOSA). Success is a **measurable drop in errors** on a fixed evaluation set.

## 2. Goals, non-goals, anti-goals

**Goals**
- Load whenever the agent writes Modern Standard Arabic (MSA) prose of any length, including mixed Arabic/English answers.
- Prevent errors while writing (rules in `SKILL.md`) and catch the rest after writing (checker script + self-review checklist).
- Auto-fix only what is certain; flag the rest for the model to decide.
- Measure the improvement on ~50 texts. **Success bar (owner's decision):** zero over-corrections (no approved form or correct text changed) and a clear drop in total errors, targeting about 50% fewer per 100 words on the owner's rubric. If any category gets worse, the work goes back for changes.

**Non-goals (this version)**
- Dialect writing (Levantine, Gulf, Egyptian). If the user asks for dialect, the skill applies only formatting checks (punctuation, digits, RTL, Unicode) and does not "correct" dialect into MSA.
- Full diacritization (tashkeel).
- CAMeL Tools, LanguageTool, Hunspell or any other installed dependency.
- A Claude Code hook that forces the check. (Possible later; out of scope now.)
- An MCP server version.

**Anti-goals (failure even if it "works")**
- **Over-correction.** Flagging or "fixing" forms the Cairo Academy approved (يعتبر، ساهم في، أكد على، في نفس الوقت، أبحاث، مدراء …) makes the writing stiff and wrong-headed. The skill must never change these.
- **Rewriting good text.** Research shows LLM self-correction tends to rewrite more than needed. The review changes only what is wrong.
- **Breaking content that isn't the model's prose:** code, commands, file paths, URLs, quoted Qur'an/hadith/poetry, proper names, and text the user asked to keep verbatim.
- **Slow, noisy output.** The checker must be fast and quiet when the text is clean; warnings that are usually false positives are worse than none.

## 3. Constraints

- **Portability:** standard Agent Skills layout (`SKILL.md` with YAML frontmatter `name` + `description`, plus `references/` and `scripts/`). No agent-specific features in the core.
- **No installs:** the script uses the Python 3 standard library only; minimum Python 3.8. If no shell/Python is available (e.g. a chat-only agent), the skill still works through the checklist alone.
- **License:** MIT for the project. Any entries adapted from LanguageTool's Arabic lists (LGPL) live in a separate data file under `data/third_party/` with attribution and the LGPL notice. Our own research is the main source for all lists. No code or data from GPL projects (PyArabic, Qalsadi, Ghalatawi).
- **Context budget:** `SKILL.md` stays short (target ≤ 250 lines); detail goes in `references/` and is read only when needed.

## 4. Approaches considered

| | Approach | Trade-off | Decision |
|---|---|---|---|
| A | Instructions only (`SKILL.md` + references), model rereads its own text | Simplest and fully portable, but the model is unreliable at mechanical checks (punctuation code points, Persian letters, digit mixing, hamza on إسم) and self-correction catches only ~2/3 of grammar errors | Rejected |
| **B** | **Instructions + a dependency-free Python checker** | Script catches the certain, mechanical errors every time; model handles meaning-level grammar and style with a checklist; still runs anywhere Python 3 exists | **Chosen by owner** |
| C | B + wrappers around LanguageTool / Hunspell / CAMeL Tools | More coverage, but needs Java, Docker or system packages (breaks "any agent"), and LanguageTool flags some approved forms | Later, as optional add-ons |

Also decided by the owner: skill only, no hook.

## 5. How it works

### 5.1 When it triggers
The frontmatter `description` tells the agent to load the skill whenever it is about to write Arabic text: answers, documents, emails, posts, translations into Arabic, UI strings, commit messages or comments in Arabic. It is written in English with a few Arabic keywords (عربي، العربية، فصحى) so it matches requests in either language.

### 5.2 The workflow in `SKILL.md`
1. **Write with the rules in mind** (§5.3).
2. **Run the checker** on the draft when a shell is available and the Arabic part is more than about two sentences, or whenever the text will be saved to a file. Write the draft to a temp file (or pipe via stdin) and run `python3 scripts/check_arabic.py --fix draft.txt`.
3. **Apply auto-fixes** (the script prints the fixed text) and **decide each flag**: fix it, or leave it if it's a false positive in context.
4. **Self-review with the checklist** (§5.4), in priority order. Change only what is wrong.
5. **Output** the final text. Do not show the checker output or a list of corrections to the user unless they asked for a review.

Short replies (one or two sentences) skip the script but still get a quick mental pass over the checklist's top items.

### 5.3 Writing rules (in `SKILL.md`, brief; detail in references)
- Register: MSA, consistent through the text; no dialect words unless asked for dialect.
- Prefer verb-first sentences where natural; active voice; avoid تم/يتم + masdar, قام بـ + masdar, passive + من قبل, كـ for "as a", بشكل + adjective — **judge density, don't ban** (one تم is fine; one per sentence is translationese).
- Agreement: non-human plurals take feminine singular (التي، هذه، ـها، verbs with ت); verb before plural subject stays singular.
- Numbers: follow the tables in `references/grammar.md`; prefer digits for large or technical numbers to avoid number-word agreement errors.
- Punctuation: ، ؛ ؟ « » ; no space before, one after.
- Digits: one system per text. Default to Western digits (0–9) in all writing, technical or not (owner's decision); switch to Arabic-Indic (٠–٩) only if the user writes with them. Never Persian digits (۰–۹). Code always Western.
- Spelling conventions (pick once, stay consistent): tanween on the letter before the alif (ـًا); مسؤول (not مسئول); مئة (not مائة).
- Technical terms: use the standard Arabic term from the glossary; on first use add the English term in parentheses, e.g. «واجهة برمجة التطبيقات (API)». Keep code identifiers in backticks.
- RTL safety in Markdown: do not start a line, heading or bullet with a Latin word or a digit; reword so the line starts with Arabic. Keep English inside parentheses or backticks.
- No italics in Arabic text (use bold or «») and no tatweel (ـ).
- Never change the approved forms listed in `references/approved-forms.md`. When writing, the model may prefer the more classical option where the references call it more elegant (e.g. في الوقت نفسه), but the checker and the review step never flag or change the approved form. Forms purists reject without a confirmed Academy ruling (طالما، بينما، سويًّا …) are treated as correct: not flagged, not mentioned. *(Builder's-check call.)*

### 5.4 Self-review checklist (in `SKILL.md`, priority order)
1. **Agreement:** every pronoun, relative pronoun, demonstrative, verb and adjective referring to a non-human plural is feminine singular. Verb before a plural subject is singular.
2. **Numbers:** every number + counted noun (gender reversal 3–10, singular accusative after 11–99, genitive singular after 100/1000, ordinals).
3. **Visible endings:** ـون/ـين and ـان/ـين by position; ن dropped after أن/لن/لم/كي and in idafa; weak letter dropped after لم/لا الناهية; accusative alif where required and absent on diptotes.
4. **إنّ vs أنّ**, idafa without ال on the first term, no الذي/التي after an indefinite noun, فاء in conditional answers, no سوف لن.
5. **Translationese density** and stock paragraph openers.
6. **Register and language mixing:** no stray English words outside parentheses/code, no dialect words.
7. **Formatting:** RTL-safe line starts, consistent digits and spelling conventions.

### 5.4.1 Locating the script
`SKILL.md` refers to the script relative to the skill's own folder (agents that support skills expose the skill's base directory; Claude Code shows it when the skill loads). The workflow step says: run `python3 <skill-dir>/scripts/check_arabic.py`. *(Builder's-check call.)*

### 5.5 The checker script (`scripts/check_arabic.py`)

**Interface**
```
python3 check_arabic.py [--fix] [--json] [--digits western|arabic|auto] FILE|-
```
- Default: prints findings, one per line: `line:col  SEVERITY  rule-id  message  → suggestion`.
- `--fix`: applies only `fix`-severity rules and prints the corrected text, then the remaining findings after a separator line.
- `--json`: machine-readable findings (and fixed text with `--fix`).
- `--digits`: expected digit system; `auto` (default) picks the majority in the text and flags the minority.
- Exit code 0 = no findings left after fixes; 1 = findings remain; 2 = usage error.

**Skipped regions:** fenced code blocks, inline code, URLs, email addresses, file paths, and text inside a `<!-- arabic-check: off -->` … `<!-- arabic-check: on -->` pair. Lines with no Arabic letters are ignored except for digit-consistency counting.

**Severities**
- `fix` — certain, applied automatically by `--fix`. Rule of thumb: the rule must have no false positives on the evaluation set.
- `error` — almost certainly wrong; the model should fix it unless context clearly says otherwise.
- `warn` — likely wrong; the model decides.
- `info` — consistency or style notes (e.g. translationese density).

**Rule families** (initial set; rule tables in `research/02` §8–9 and `research/03` are the source)

| Family | Examples | Severity |
|---|---|---|
| Punctuation code points | Latin `,` `;` `?` between Arabic words → ، ؛ ؟ | fix |
| Punctuation spacing | space before ، ؛ ؟ . : ! removed; missing space after added | fix |
| Look-alike letters | Persian ی ک ہ ە → ي ك ه ة; Arabic presentation forms → base letters (NFKC on those ranges only) | fix |
| Tatweel | ـ inside words removed | fix |
| Persian digits | ۰–۹ → the text's digit system | fix |
| Fixed misspellings | هاذا، لاكن، ذالك، شئ/شيئ (as noun)، إنشاء الله، من ما، عن ما، لاسيما، فى/الذى/التى | error (with suggestion) |
| Hamza on wasl words | إسم، إبن، إثنان، إمرأة، إستخدام، إنتقال، إستعمال (forms 7/8/10 + masdars from a list) | error |
| Missing hamza on common words | الى، انا، ان (as particle, ambiguous) → flag | warn |
| ة/ه, ى/ي word lists | frequent confusions from research/02 | warn |
| Tanween placement | اً vs ًا mixed in one text | info (consistency) |
| Spelling consistency | مسؤول/مسئول، مئة/مائة mixed | info |
| Digit consistency | Western and Arabic-Indic digits mixed in prose | warn |
| Dialect words | list (e.g. هيك، شو، ليش، بدي، عشان، ازاي، دلوقتي، وايد) | warn |
| Stray English | Latin words in Arabic prose not in parentheses/backticks and not a known acronym | info |
| RTL line start | Markdown line/heading/bullet in an Arabic paragraph starting with a Latin letter or digit | warn |
| Visible-ending patterns | سوف لن; لم + verb ending ون/ين; لن/أن + ـون; الذي/التي directly after an indefinite noun (approximate) | warn |
| Translationese density | count of تم/يتم + masdar, قام بـ, من قبل, بشكل; report when above a threshold per 100 words | info |

**Never flagged:** anything in `data/approved_forms.txt` (the Academy-approved list from research/03), and Qur'an quotations marked with ﴿ ﴾.

**Data files** (`scripts/data/`, UTF-8 TSV with a header row and a comment column):
`misspellings.tsv`, `wasl_words.tsv`, `taa_haa.tsv`, `alif_maqsura.tsv`, `dialect_words.tsv`, `approved_forms.txt`, `acronyms.txt`, and `third_party/languagetool_ar.tsv` (+ `LICENSE-LGPL` and source note) if any LanguageTool entries are adapted. Matching is on whole words after stripping common prefixes (و، ف، ب، ل، ك، ال) where the rule says so.

### 5.6 References (`references/`)
- `grammar.md` — agreement tables, number–noun tables, visible-ending rules, idafa, إنّ/أنّ, conditionals. Condensed from research/01 into lookup tables with right/wrong pairs.
- `orthography.md` — hamza, ة/ه, ى/ي, joined words, tanween, punctuation and digit policy. From research/02.
- `style.md` — translationese patterns with natural alternatives, stock openers, register guidance. From research/03.
- `common-errors.md` — the common-errors list with its status tags (firm error / style only); approved and contested items are not listed as errors.
- `approved-forms.md` — forms that must not be "fixed", with a one-line reason each.
- `glossary.md` — starter tech glossary (~200 terms): English | Arabic | notes (preferred vs acceptable alternatives).

`SKILL.md` names each reference and says when to read it (e.g. "before writing numbers with counted nouns, read the tables in `references/grammar.md`").

## 6. Distribution
A public GitHub repo (owner's account for now; can move to a JOSA organization later). Users install by copying or symlinking `arabic-writing/` into their agent's skills folder (`~/.claude/skills/` for Claude Code). The repo also carries a minimal Claude Code plugin marketplace manifest so `/plugin install` works. *(Builder's-check call.)*

## 6.1 Repository layout

```
arabic-skill/
  arabic-writing/            # the skill (what users install)
    SKILL.md
    references/ …
    scripts/check_arabic.py
    scripts/data/ …
  tests/                     # unittest for the checker (stdlib only)
  evals/                     # evaluation set and scoring (not shipped with the skill)
  research/                  # existing research notes
  docs/                      # design and plans
  README.md                  # with before/after examples
  LICENSE                    # MIT
```

## 7. Testing and evaluation

**Checker tests** (`tests/`, `unittest`): for each rule family, positive cases (must flag / must fix) and negative cases (must not flag), including every entry in `approved_forms.txt` as a negative case and code-block/URL skipping. `--fix` is idempotent (running it twice changes nothing the second time).

**Trigger tests** (`evals/triggers.md`): ~20 prompts with the expected outcome (skill loads / doesn't / formatting-only): Arabic requests, English requests for Arabic output, mixed requests, English-only tasks, and dialect requests. Run in Claude Code with the skill installed locally; spot-check in one other agent (Cursor or Copilot).

**Real-use loop:** the owner uses the skill day to day (linked into `~/.claude/skills/`); every error that slips through becomes a test case or word-list entry.

**Evaluation** (`evals/`):
- ~50 prompts across five task types (10 each): email/letter, technical documentation, social post, technical explanation with code terms, translation from English.
- For each prompt, generate a response **without** the skill and **with** the skill (same model), saved as text files.
- Score each response with (a) the checker's findings by family and (b) a short human rubric by a native speaker (owner): grammar errors, spelling errors, translationese instances, register slips, formatting/RTL issues — each counted.
- Report errors per 100 words by category, before vs after. **The headline number comes from the owner's human rubric only**, because the with-skill responses have already passed through the checker, so checker counts would be biased toward the skill; checker counts are reported as supporting detail. Also report any over-corrections the skill introduced.
- Responses are generated by a script in `evals/` that runs Claude Code headless (`claude -p`) on each prompt twice, with the skill disabled and enabled, using the owner's own Claude Code login. Claude only for v1; other agents get the manual trigger spot-check only.
- A small script in `evals/` runs the checker over a folder and prints the summary table; the human rubric is a CSV the owner fills in.

## 8. What's left to the builder
- Exact wording of `SKILL.md`, within the rules above.
- Exact regexes and word-list contents, taken from the research files; keeping only entries that don't produce false positives on the tests.
- The translationese-density threshold (start around 3 per 100 words, tune on the eval set).
- How the 200 glossary terms are chosen (common software/AI/web terms first).
- The 50 eval prompts.
