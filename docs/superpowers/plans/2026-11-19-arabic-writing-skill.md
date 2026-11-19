# Arabic Writing Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An open-source Agent Skill that makes an agent write correct, natural Modern Standard Arabic and check it before answering, using a writing guide, reference files, a self-review checklist and a dependency-free Python checker.

**Architecture:** `SKILL.md` carries the writing rules, the workflow and the checklist. `references/` holds the detailed tables and lists, read on demand. `scripts/check_arabic.py` is a stdlib-only CLI over a small `archeck` package: it masks regions it must not touch (code, URLs, Qur'an quotes), runs rule functions that return `Finding`s, auto-applies only `fix`-severity findings, and filters anything in the approved-forms list. An `evals/` harness measures before/after with `claude -p`.

**Tech Stack:** Python 3.8+ standard library only (`re`, `unicodedata`, `argparse`, `json`, `dataclasses`, `unittest`, `subprocess`, `csv`). Markdown. Claude Code CLI for evals.

**Spec:** `docs/superpowers/specs/2026-11-19-arabic-writing-skill-design.md`. Research the spec relies on: `research/01-grammar.md`, `research/02-orthography-punctuation.md`, `research/03-style-errors-tools.md`. Executors read the spec and the research section named in each task.

## Global Constraints

- Python 3.8+ standard library only. No pip installs anywhere in the skill, tests or evals.
- License MIT. Any entries adapted from LanguageTool live only in `skills/arabic-writing/scripts/data/third_party/languagetool_ar.tsv` with `LICENSE-LGPL` and a source note beside it. No code or data from PyArabic, Qalsadi or Ghalatawi.
- `SKILL.md` ≤ 250 lines, YAML frontmatter with `name: arabic-writing` and `description`.
- Conventions the skill enforces: Western digits 0–9 by default (Arabic-Indic only if the user writes with them; never Persian ۰–۹; code always Western); tanween as `ـًا`; `مسؤول` not `مسئول`; `مئة` not `مائة`; Arabic punctuation ، ؛ ؟ « » with no space before and one after; no tatweel; no italics in Arabic.
- Never flag or change anything in `approved_forms.txt` (Cairo Academy approved forms, research/03 §1.4). Forms purists reject without a ruling (research/03 §1.5, e.g. طالما، بينما، سويًّا) are never flagged.
- `fix` severity only for rules with zero false positives on the test suite.
- Severity names exactly: `fix`, `error`, `warn`, `info`.
- Success bar: zero over-corrections and ~50% fewer errors per 100 words on the owner's rubric; no category worse.
- **Deviation from spec §6.1 (layout):** the skill lives at `skills/arabic-writing/` instead of `arabic-writing/`, the standard plugin layout, so `/plugin install` works without extra manifest paths.
- **Exit-code call** (spec left it open): `info` findings alone do not make the exit code 1.

## Review Focus

1. **Mixed Markdown** with fenced code, inline code, URLs and file paths inside Arabic text: `--fix` must leave those bytes untouched. Test in Task 3.
2. **No Arabic at all** (English-only text): no findings, and `--fix` output is byte-identical to the input. Test in Task 3.
3. **Approved forms and Qur'an quotes** (يعتبر، أكد على، أبحاث، ﴿…﴾): never flagged by any rule. Test in Task 4.
4. **Latin punctuation in English segments** of an Arabic line (`(Python, Java)`, `e.g.,`): must not become ، or ؛. Test in Task 3.
5. **Numbers with separators** (`3.5`, `1,000`, `10:30`, `٣٫٥`): no spaces inserted, no comma converted. Test in Task 3.

---

## File map

```
.gitignore  LICENSE  README.md
.claude-plugin/marketplace.json  .claude-plugin/plugin.json
skills/arabic-writing/
  SKILL.md
  references/{grammar,orthography,style,common-errors,approved-forms,glossary}.md
  scripts/check_arabic.py                    # CLI
  scripts/archeck/__init__.py
  scripts/archeck/model.py                   # Finding, severities
  scripts/archeck/text.py                    # mask, words, prefixes, line/col
  scripts/archeck/data.py                    # TSV/list loaders
  scripts/archeck/rules_fix.py               # fix-severity rules
  scripts/archeck/rules_lists.py             # word-list rules
  scripts/archeck/rules_patterns.py          # consistency + pattern rules
  scripts/archeck/engine.py                  # check(), apply_fixes()
  scripts/data/*.tsv|*.txt
tests/__init__.py  tests/test_*.py
evals/prompts.tsv  evals/triggers.tsv  evals/rubric.csv
evals/generate.py  evals/run_triggers.py  evals/report.py
```

Run all tests from the repo root: `python3 -m unittest discover -s tests -t . -v`

---

### Task 1: Repository scaffold

**Files:**
- Create: `.gitignore`, `LICENSE` (MIT, "Anas Al-Hamdan", 2026), `README.md` (title + one-paragraph description + "status: in development"), `skills/arabic-writing/scripts/archeck/__init__.py` (empty), `tests/__init__.py`, `tests/test_scaffold.py`

**Interfaces:**
- Produces: `tests/__init__.py` inserts `<repo>/skills/arabic-writing/scripts` at the front of `sys.path`, so every test can `import archeck`.

- [ ] **Step 1:** `git init` in `/home/anas/dev/arabic-skill`; `.gitignore` covers `__pycache__/`, `*.pyc`, `evals/outputs/`, `.DS_Store`.
- [ ] **Step 2: Write test** `tests/test_scaffold.py::test_archeck_importable`: `import archeck` succeeds.
- [ ] **Step 3:** Run `python3 -m unittest discover -s tests -t . -v`. Expected: 1 test, OK.
- [ ] **Step 4: Commit** everything, including `research/` and `docs/`: `git add -A && git commit -m "chore: scaffold repo with research and design"`

---

### Task 2: Core model, text utilities, data loading

**Files:**
- Create: `scripts/archeck/model.py`, `scripts/archeck/text.py`, `scripts/archeck/data.py`, `scripts/data/approved_forms.txt`, `scripts/data/acronyms.txt` (paths below are relative to `skills/arabic-writing/`)
- Test: `tests/test_text.py`, `tests/test_data.py`

**Interfaces:**
- Produces (`model.py`):
  - `SEVERITIES = ("fix", "error", "warn", "info")`
  - `@dataclass(frozen=True) class Finding: start: int; end: int; severity: str; rule: str; message: str; suggestion: Optional[str] = None; replacement: Optional[str] = None`. `start`/`end` are offsets into the full text; `replacement` is set only for `fix` findings.
- Produces (`text.py`):
  - `ARABIC_LETTER = "[ء-غف-يٱ-ۓ]"` (regex char class string)
  - `has_arabic(s: str) -> bool`
  - `mask(text: str) -> str`: same length as `text`; every char inside a skipped region becomes a space except `\n`. Skipped: fenced code blocks (``` and ~~~), inline code (`…`), URLs (`https?://\S+`, `www\.\S+`), emails, file paths (`\S*/\S+\.\w+` and `~/\S+`), `﴿…﴾`, and text between `<!-- arabic-check: off -->` and `<!-- arabic-check: on -->` (markers included).
  - `iter_words(masked: str) -> Iterator[Tuple[int, int, str]]`: Arabic words (letters plus diacritics U+064B–U+065F, U+0670) with start/end offsets.
  - `stem_candidates(word: str) -> List[str]`: the word with diacritics removed, then with leading `و`/`ف` stripped, then `ب`/`ل`/`ك`, then `ال` (and `لل` → stem). Most-stripped last, no duplicates, no candidate shorter than 2 letters.
  - `line_col(text: str, offset: int) -> Tuple[int, int]`: 1-based.
- Produces (`data.py`):
  - `load_tsv(name: str) -> List[Dict[str, str]]`: reads `scripts/data/<name>`, UTF-8, first line is the header, skips blank lines and lines starting with `#`.
  - `load_list(name: str) -> FrozenSet[str]`: one entry per line, same skipping.
  - Both cached with `functools.lru_cache`.

- [ ] **Step 1: Write tests** in `tests/test_text.py`:
  - `test_mask_keeps_length_and_newlines`: for an input with a fenced block, inline code, a URL and `﴿بسم الله﴾`, `len(mask(t)) == len(t)` and the newlines sit at the same indexes.
  - `test_mask_blanks_code_and_url`: `mask("انظر `x, y` و https://a.b/c?d=1")` contains no `x`, `,` or `https`.
  - `test_mask_off_on_markers`: Arabic between the off/on markers is blanked; Arabic after the `on` marker is kept.
  - `test_iter_words_offsets`: for `"ذهب الطلابُ."`, the words are `ذهب` at (0,3) and `الطلابُ` at (4,11).
  - `test_stem_candidates`: `stem_candidates("وبالإسم")` contains `"إسم"`; `stem_candidates("للمدرسة")` contains `"مدرسة"`.
  - `test_line_col`: `line_col("أ\nب", 2) == (2, 1)`.
- [ ] **Step 2: Write tests** in `tests/test_data.py`:
  - `test_approved_forms_loaded`: `{"يعتبر", "أبحاث", "مدراء"} <= load_list("approved_forms.txt")`.
  - `test_comments_skipped`: no entry starts with `#`.
- [ ] **Step 3:** Run the tests. Expected: FAIL with ImportError.
- [ ] **Step 4: Implement** `model.py`, `text.py`, `data.py` as specified.
- [ ] **Step 5: Create** `approved_forms.txt` from research/03 §1.4: every approved word form, including common inflections the checker could meet (e.g. يعتبر، اعتبر، تعتبر، ساهم، يساهم، أبحاث، إحصائيات، مدراء، تخرج). Add a `# source: research/03 §1.4` header. Create `acronyms.txt` with common tech acronyms (API, URL, HTTP, JSON, AI, CPU, GPU, SQL, PDF, …).
- [ ] **Step 6:** Run the tests. Expected: PASS.
- [ ] **Step 7: Commit** `feat(checker): core model, masking and data loading`

---

### Task 3: Fix rules and the engine

**Files:**
- Create: `scripts/archeck/rules_fix.py`, `scripts/archeck/engine.py`
- Test: `tests/test_rules_fix.py`, `tests/test_engine.py`

**Interfaces:**
- Consumes: `Finding`, `mask`, `iter_words`, `has_arabic`, `load_list` (Task 2).
- Produces:
  - Every rule function has the signature `rule(text: str, masked: str, opts: Dict[str, str]) -> List[Finding]`. `opts["digits"]` is `"western"`, `"arabic"` or `"auto"`.
  - `rules_fix.RULES: List[Callable]`: `punct_latin`, `punct_space`, `persian_letter`, `presentation_form`, `tatweel`, `persian_digit`.
  - `engine.check(text: str, digits: str = "auto") -> List[Finding]`: runs `rules_fix.RULES + rules_lists.RULES + rules_patterns.RULES` (create both modules now with `RULES = []`; Tasks 4–5 fill them). Drops findings whose span text, or any of its `stem_candidates`, is in `approved_forms.txt`. Returns them sorted by `(start, rule)`.
  - `engine.apply_fixes(text: str, findings: List[Finding]) -> str`: applies `fix` findings that have a `replacement`, right to left; skips any that overlap one already applied.
  - `engine.fix_text(text: str, digits: str = "auto") -> str`: repeats `check` + `apply_fixes` until nothing changes (at most 5 rounds).

Rule IDs and behavior (all `fix`):
- `punct-latin`: a `,` `;` `?` whose nearest non-space character on the left is an Arabic letter (or closing `»`/`)` after Arabic) **and** whose nearest non-space character on the right is an Arabic letter, or end of line for `?` → `،` `؛` `؟`.
- `punct-space`: for `، ؛ ؟ . : !` that follow an Arabic letter, remove spaces before the mark; insert one space after if the next character is an Arabic letter. Never touch a mark between two digits.
- `persian-letter`: `ی`→`ي`, `ک`→`ك`, `ہ`→`ه`, `ە`→`ة` only in a word where the rest is Arabic letters.
- `presentation-form`: chars in U+FB50–U+FDFF and U+FE70–U+FEFF → `unicodedata.normalize("NFKC", ch)`.
- `tatweel`: U+0640 between two Arabic letters is removed. Keep it after `هـ` at word end and in `الـ` directly before a Latin letter or digit.
- `persian-digit`: `۰–۹` → Western digits, or Arabic-Indic if `opts["digits"] == "arabic"` or `auto` and Arabic-Indic digits are the majority.

- [ ] **Step 1: Write tests** in `tests/test_rules_fix.py`, each through `engine.fix_text`:
  - `test_punct_latin`: `"ذهبت إلى السوق, ثم عدت"` → `"ذهبت إلى السوق، ثم عدت"`; `"هل جئت?"` → `"هل جئت؟"`.
  - `test_punct_latin_leaves_english` (Review Focus 4): `"لغات مثل (Python, Java) مفيدة"` and `"e.g., نص"` are unchanged.
  - `test_punct_space`: `"قال ، ثم"` → `"قال، ثم"`; `"قال،ثم"` → `"قال، ثم"`.
  - `test_numbers_untouched` (Review Focus 5): `"السعر 3.5 دينار و1,000 و10:30 و٣٫٥"` is unchanged.
  - `test_persian_letters`: `"کتابی"` → `"كتابي"`.
  - `test_presentation_forms`: `"ﻻ"` (لا ligature) → `"لا"`.
  - `test_tatweel`: `"جمـــيل"` → `"جميل"`; `"1445هـ"` and `"الـAPI"` unchanged.
  - `test_persian_digits`: `"العدد ۱۲"` → `"العدد 12"`; with `digits="arabic"` → `"العدد ١٢"`.
- [ ] **Step 2: Write tests** in `tests/test_engine.py`:
  - `test_masked_regions_untouched` (Review Focus 1): input with ```` ```\nx = "a , b"\n``` ````, `` `a,b` ``, `https://x.y/a,b` and `~/dir/file.py` inside Arabic sentences: those exact substrings are still in `fix_text` output.
  - `test_english_only_is_noop` (Review Focus 2): for an English paragraph with commas and `?`, `check(t) == []` and `fix_text(t) == t`.
  - `test_fix_idempotent`: for a messy sample using all six rules, `fix_text(fix_text(t)) == fix_text(t)`.
  - `test_apply_fixes_skips_overlap`: two overlapping fix findings → only the first by position is applied.
- [ ] **Step 3:** Run. Expected: FAIL.
- [ ] **Step 4: Implement** `rules_fix.py`, `engine.py`, and empty `rules_lists.py`/`rules_patterns.py` with `RULES = []`.
- [ ] **Step 5:** Run all tests. Expected: PASS.
- [ ] **Step 6: Commit** `feat(checker): auto-fix rules and engine`

---

### Task 4: Word-list rules

**Files:**
- Create: `scripts/data/{misspellings,wasl_words,hamza_missing,taa_haa,alif_maqsura,dialect_words}.tsv`
- Modify: `scripts/archeck/rules_lists.py`
- Test: `tests/test_rules_lists.py`

**Interfaces:**
- Consumes: `iter_words`, `stem_candidates`, `load_tsv`, `Finding`, `engine.check`.
- Produces: `rules_lists.RULES = [misspelling, hamza_wasl, hamza_missing, taa_haa, alif_maqsura, dialect_word]`.
- TSV header for the first five: `wrong\tright\tnote`. For `dialect_words.tsv`: `word\tmsa\tnote`.
- A word matches when any of its `stem_candidates` equals `wrong` (or `word`). The `suggestion` is the original word with the matched stem replaced by `right`, keeping the stripped prefixes.
- Multi-word entries (`من ما`, `عن ما`, `إنشاء الله`, `سوف لن` is NOT here, it's Task 5) are matched as a regex over the masked text with word boundaries.

| Rule ID | Severity | Data | Source |
|---|---|---|---|
| `misspelling` | error | `misspellings.tsv` | research/02 §8 (fixed misspellings), research/03 §1.1 |
| `hamza-wasl` | error | `wasl_words.tsv` | research/02 §1.1: the ten nouns + forms 7/8/10 verbs and masdars, written with إ |
| `hamza-missing` | warn | `hamza_missing.tsv` | unambiguous particles and pronouns: الى، انا، انت، اذا، او، اكثر، اول; not `ان` (too ambiguous) |
| `taa-haa` | warn | `taa_haa.tsv` | research/02 §2.1 frequent confusions |
| `alif-maqsura` | warn | `alif_maqsura.tsv` | research/02 §2.2–2.3 (فى، الذى، التى، على/علي is NOT listed: ambiguous) |
| `dialect-word` | warn | `dialect_words.tsv` | research/03 §4.1; include هيك، شو، ليش، بدي، عشان، ازاي، دلوقتي، وايد، كتير، هلق |

Keep only entries that are wrong in every context. Anything that is a real word in another meaning (e.g. `علي`, `كتابه`, `مبني`) stays out.

- [ ] **Step 1: Write tests** in `tests/test_rules_lists.py`, using `engine.check` and asserting on `(rule, suggestion)` pairs:
  - `test_misspellings`: `هاذا` → `هذا`; `لاكن` → `لكن`; `إنشاء الله` → `إن شاء الله`; `من ما` → `مما`.
  - `test_hamza_wasl_with_prefix`: `"وبالإستخدام"` → rule `hamza-wasl`, suggestion `"وبالاستخدام"`; `"إسم"` → `"اسم"`.
  - `test_hamza_missing`: `"ذهب الى البيت"` → `hamza-missing`, suggestion `"إلى"`.
  - `test_alif_maqsura`: `"فى"` → `"في"`.
  - `test_dialect`: `"بدي أشرح"` → `dialect-word`, severity `warn`.
  - `test_no_false_positives`: no findings at all for a clean paragraph of correct MSA containing `علي`, `كتابه`, `مبني`, `إن`, `أن`, `استخدام`, `اسم`.
  - `test_approved_never_flagged` (Review Focus 3): no findings for `"يعتبر هذا من أهم الأبحاث، وأكد على ذلك المدراء في نفس الوقت، طالما أن"` and for `"﴿إِنَّا أَعْطَيْنَاكَ﴾"`.
  - `test_every_approved_form_clean`: for each entry in `approved_forms.txt`, `check(entry) == []`.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3: Fill the data files** from the research sections in the table, then **implement** the six rules.
- [ ] **Step 4:** Run all tests. Expected: PASS. If an entry causes a false positive in any test, delete the entry rather than special-casing it.
- [ ] **Step 5: Commit** `feat(checker): word-list rules`

---

### Task 5: Consistency and pattern rules

**Files:**
- Modify: `scripts/archeck/rules_patterns.py`
- Test: `tests/test_rules_patterns.py`

**Interfaces:**
- Consumes: `mask`, `iter_words`, `has_arabic`, `load_list("acronyms.txt")`, `Finding`, `engine.check`.
- Produces: `rules_patterns.RULES` with these rule IDs:

| Rule ID | Severity | Behavior |
|---|---|---|
| `digit-mix` | warn | On lines with Arabic letters, count Western and Arabic-Indic digit runs. Expected system: `opts["digits"]`, or for `auto` the majority (tie → Western). Flag each run of the other system; suggestion = converted run. |
| `tanween-mixed` | info | If both `اً` and `ًا` occur, flag each `اً` with suggestion `ًا` (the convention). |
| `spelling-mixed` | info | Flag `مسئول*` (suggest `مسؤول*`) and `مائة` (suggest `مئة`) always, with the message naming the convention. |
| `stray-english` | info | A Latin word of 2+ letters on a line with Arabic letters, not inside `(…)` on that line, and not in `acronyms.txt` (case-insensitive). |
| `rtl-line-start` | warn | A line with Arabic letters whose content, after stripping leading `#`, `>`, `-`, `*`, `+`, `N.`, `N)` and spaces, starts with a Latin letter or digit. Span = the first token. |
| `sawfa-lan` | warn | `سوف لن` → suggestion `لن`. |
| `jussive-nun` | warn | `لم` followed by a word starting with `ي`/`ت` and ending in `ون`/`ين` (e.g. `لم يكونوا` ok; `لم يكونون` flagged, suggestion drops the `ن` and adds `ا` after `و`). Same for `لن`/`أن`/`كي` (subjunctive) with the `ون` ending. |
| `relative-after-indefinite` | warn | `الذي`/`التي`/`الذين` directly after an Arabic word that has no `ال`/`لل` prefix, does not end in a pronoun suffix (`ه ها هم هن كم نا ي ك`), and is not in a short list of always-definite words (`هذا`, `ذلك`, `هو`, `هي`, …). Message says it's approximate. |
| `translationese-density` | info | Count `تم`/`يتم`/`تمت` + word, `قام`/`يقوم`/`قامت` + `بـ`, `من قبل`, `بشكل` + word, per 100 Arabic words. If the rate > 3.0, one finding spanning the first match, message giving each count and the rate. |

- [ ] **Step 1: Write tests** in `tests/test_rules_patterns.py`, asserting rule IDs from `engine.check`:
  - `test_digit_mix_auto`: `"لدينا 3 ملفات و٤ مجلدات و5 صور"` → one `digit-mix` on `٤`, suggestion `4`.
  - `test_digit_mix_arabic_option`: same text with `digits="arabic"` → `digit-mix` on `3` and `5`.
  - `test_digits_in_code_ignored`: `"الأمر `ls -1` يعرض ٣ ملفات"` → no `digit-mix`.
  - `test_tanween_mixed`: `"شكراً جزيلًا"` → one `tanween-mixed` on `شكراً`; `"شكرًا جزيلًا"` → none.
  - `test_spelling_mixed`: `"المسئولون"` → `spelling-mixed`, suggestion `"المسؤولون"`.
  - `test_stray_english`: `"هذا feature جديد"` → `stray-english`; `"واجهة برمجة التطبيقات (API)"` and `"ملف JSON"` → none.
  - `test_rtl_line_start`: `"- Python لغة سهلة"` → `rtl-line-start`; `"- لغة Python سهلة"` → none; an English-only line → none.
  - `test_sawfa_lan`: `"سوف لن أذهب"` → `sawfa-lan`.
  - `test_jussive_nun`: `"لم يكونون هناك"` and `"لن يذهبون"` → `jussive-nun`; `"لم يكونوا هناك"` → none.
  - `test_relative_after_indefinite`: `"كتاب الذي قرأته"` → flagged; `"الكتاب الذي"`, `"كتابه الذي"`, `"هذا الذي"` → none.
  - `test_translationese_density`: a 30-word paragraph with 3 `تم + masdar` and 1 `من قبل` → one `translationese-density`; a 100-word paragraph with one `تم` → none.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3: Implement** the rules.
- [ ] **Step 4:** Run all tests. Expected: PASS (all earlier tests included).
- [ ] **Step 5: Commit** `feat(checker): consistency and pattern rules`

---

### Task 6: CLI

**Files:**
- Create: `skills/arabic-writing/scripts/check_arabic.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `engine.check`, `engine.fix_text`, `text.line_col`.
- Produces the CLI from spec §5.5:
  - `check_arabic.py [--fix] [--json] [--digits western|arabic|auto] FILE|-`
  - Text output: one finding per line, `{line}:{col}  {SEVERITY}  {rule}  {message}` plus `  → {suggestion}` when present. Severity uppercase.
  - `--fix`: print the fixed text, then the line `--- arabic-check findings ---`, then the remaining findings (checked on the fixed text). If none remain, the separator is followed by `no findings`.
  - `--json`: `{"findings": [{line, col, severity, rule, message, suggestion, text}]}`, plus `"fixed_text"` with `--fix`. `ensure_ascii=False`.
  - Exit: 0 if no `error`/`warn` findings remain (info alone → 0); 1 otherwise; 2 on usage error or unreadable file.
  - Reads UTF-8; accepts CRLF input and preserves CRLF in `--fix` output. `-` reads stdin. Adds its own directory to `sys.path` so it runs from any working directory.

- [ ] **Step 1: Write tests** in `tests/test_cli.py`, running the script with `subprocess.run([sys.executable, SCRIPT, ...])` from a temp working directory:
  - `test_clean_text_exit_0`: a correct Arabic sentence → exit 0 and empty stdout.
  - `test_findings_exit_1`: `"إستخدام"` → exit 1; stdout contains `ERROR  hamza-wasl`.
  - `test_fix_mode_output`: `"قال ، ثم"` with `--fix` → stdout starts with `"قال، ثم"` and contains `--- arabic-check findings ---`.
  - `test_json`: `--json` output parses; `findings[0]["rule"] == "hamza-wasl"` for `"إسم"`; Arabic is not escaped.
  - `test_stdin`: text piped to `-` works.
  - `test_crlf_preserved`: input `"قال ، ثم\r\nنعم"` with `--fix` → fixed text contains `\r\n`.
  - `test_empty_input`: empty file → exit 0.
  - `test_missing_file`: → exit 2.
  - `test_info_only_exit_0`: text whose only finding is `stray-english` → exit 0.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3: Implement** `check_arabic.py` with `argparse`.
- [ ] **Step 4:** Run all tests. Expected: PASS.
- [ ] **Step 5: Commit** `feat(checker): command-line interface`

---

### Task 7: Reference files

**Files:**
- Create: `skills/arabic-writing/references/{grammar,orthography,style,common-errors,approved-forms}.md`
- Test: `tests/test_references.py`

Content rules (spec §5.6): condensed lookup tables with right/wrong pairs, not essays. Each file opens with one line saying when to read it.
- `grammar.md` ← research/01: agreement (non-human plural first), number tables (1–2, 3–10, 11–19, tens, 100/1000, ordinals), visible endings, idafa, إنّ/أنّ, conditionals and فاء, relative pronouns. ≤ 300 lines.
- `orthography.md` ← research/02 §1–7: hamza, ة/ه, ى/ي, joined words, tanween, punctuation, digits (Western default), RTL rules. ≤ 250 lines.
- `style.md` ← research/03 §2–4: translationese patterns with natural alternatives, stock openers, register, technical-term policy. States the density principle ("judge density, don't ban"). ≤ 200 lines.
- `common-errors.md` ← research/03 §1.1–1.3: `[FIRM]` and style-only items only, table: wrong | right | note.
- `approved-forms.md` ← research/03 §1.4: form | one-line reason. States that §1.5 contested forms are also correct and must not be mentioned.

- [ ] **Step 1: Write tests** in `tests/test_references.py`:
  - `test_files_exist_and_sized`: each of the five exists and is within its line limit.
  - `test_approved_lists_in_sync`: every Arabic form in the first column of `approved-forms.md`'s table appears in `approved_forms.txt`.
  - `test_common_errors_not_approved`: no "wrong" entry in `common-errors.md` is in `approved_forms.txt`.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3: Write** the five files.
- [ ] **Step 4:** Run all tests. Expected: PASS.
- [ ] **Step 5: Commit** `docs(skill): reference files`

---

### Task 8: Tech glossary

**Files:**
- Create: `skills/arabic-writing/references/glossary.md`
- Test: `tests/test_glossary.py`

Format: one Markdown table `| English | Arabic | Notes |`, sorted by English, ≥ 200 rows. Common software, web, AI and data terms first. Arabic column: the standard term used by Arab tech writers and academies; acceptable alternatives in Notes; transliterations only where no Arabic term is established (marked "transliteration" in Notes).

- [ ] **Step 1: Write tests** in `tests/test_glossary.py`:
  - `test_row_count`: ≥ 200 data rows.
  - `test_unique_english`: no duplicate English terms (case-insensitive).
  - `test_arabic_column_clean`: running `engine.check` on each Arabic cell gives no `error` or `warn` findings.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3: Write** the glossary.
- [ ] **Step 4:** Run all tests. Expected: PASS.
- [ ] **Step 5: Commit** `docs(skill): starter tech glossary`

---

### Task 9: SKILL.md

**Files:**
- Create: `skills/arabic-writing/SKILL.md`
- Test: `tests/test_skill_md.py`

Content (spec §5.1–5.4, in this order):
1. Frontmatter: `name: arabic-writing`; `description`: in English, says to use it whenever about to write Arabic text (answers, documents, emails, posts, translations into Arabic, UI strings, commit messages, code comments), includes the keywords عربي، العربية، فصحى, and says it checks grammar, spelling, punctuation and style before answering. ≤ 1024 chars.
2. Scope: MSA; dialect requests → formatting checks only; never touch code, quotes, names, verbatim text.
3. Writing rules (spec §5.3, all bullets including the approved-forms bullet and its builder's-check call).
4. Workflow (spec §5.2): when to run the script; command `python3 <skill-dir>/scripts/check_arabic.py --fix <file>`, where `<skill-dir>` is the folder this `SKILL.md` is in; how to treat `fix`/`error`/`warn`/`info`; don't show checker output unless asked; no-shell fallback = checklist only.
5. Self-review checklist (spec §5.4, the seven items in order) with "change only what is wrong".
6. Reference index: each reference file and when to read it.

- [ ] **Step 1: Write tests** in `tests/test_skill_md.py`:
  - `test_frontmatter`: starts with `---`, has `name: arabic-writing` and a `description:` of ≤ 1024 chars containing `Arabic` and `عربي`.
  - `test_length`: ≤ 250 lines.
  - `test_referenced_files_exist`: every `references/*.md` and `scripts/*.py` path mentioned exists.
  - `test_arabic_examples_clean`: Arabic lines in SKILL.md that are not inside a "wrong" example (mark wrong examples with `✗`) give no `error`/`warn` findings.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3: Write** `SKILL.md`.
- [ ] **Step 4:** Run all tests. Expected: PASS.
- [ ] **Step 5: Commit** `feat(skill): SKILL.md writing guide, workflow and checklist`

---

### Task 10: Plugin packaging and install docs

**Files:**
- Create: `.claude-plugin/plugin.json` (`name: "arabic-writing"`, `version: "0.1.0"`, `description`, `author: {"name": "Anas Al-Hamdan"}`, `license: "MIT"`), `.claude-plugin/marketplace.json` (one plugin, `source: "./"`)
- Modify: `README.md`: install sections for Claude Code (plugin and `~/.claude/skills/` symlink), Cursor and Copilot (copy `skills/arabic-writing/` into their skills folder), "running the checker by hand", license notes.

- [ ] **Step 1:** Write both manifests. Confirm the current schema with `claude plugin --help` and the Claude Code plugin docs before finalizing field names.
- [ ] **Step 2:** Run `claude plugin validate .`. Expected: no errors.
- [ ] **Step 3:** Smoke test: `ln -s "$PWD/skills/arabic-writing" ~/.claude/skills/arabic-writing` (ask the owner first; it changes their setup), then `claude -p "اكتب فقرة قصيرة عن فوائد القراءة"` and confirm the skill loads (it appears in the transcript or the answer follows the conventions). Remove the symlink afterwards unless the owner wants to keep it.
- [ ] **Step 4: Commit** `chore: plugin manifest and install docs`

---

### Task 11: Evaluation harness

**Files:**
- Create: `evals/prompts.tsv`, `evals/triggers.tsv`, `evals/rubric.csv`, `evals/generate.py`, `evals/run_triggers.py`, `evals/report.py`, `evals/README.md`
- Test: `tests/test_report.py`

**Interfaces:**
- `prompts.tsv`: `id\ttask_type\tprompt`; 50 rows, 10 each of `email`, `docs`, `social`, `tech_explain`, `translate` (translate prompts include the English source text).
- `triggers.tsv`: `id\tprompt\texpected` with `expected` in `load`, `no_load`, `format_only`; 20 rows across Arabic requests, English requests for Arabic output, mixed, English-only, dialect.
- `generate.py --mode baseline|skill [--only ID]`: for each prompt, runs `claude -p PROMPT --output-format text` in a fresh temp dir. `skill` mode creates `.claude/skills/arabic-writing` in that dir as a symlink to the repo's skill and passes `--allowedTools "Bash(python3:*)" Read Write`. `baseline` mode uses a temp dir without it. Refuses to run if `~/.claude/skills/arabic-writing` exists (it would contaminate the baseline). Writes `evals/outputs/<mode>/<id>.txt`; skips existing files.
- `run_triggers.py`: runs each trigger prompt with `--output-format stream-json --verbose` in a temp dir with the skill linked, and records whether a `Skill` tool use naming `arabic-writing` occurs. Prints a table and the pass count. First step of implementation: run one prompt and inspect the JSON to confirm the event shape.
- `rubric.csv`: header `id,mode,grammar,spelling,translationese,register,formatting,over_corrections,notes`; one row per id × mode, counts blank for the owner to fill.
- `report.py [--rubric evals/rubric.csv] [--outputs evals/outputs]`:
  - `checker_counts(path: str) -> Dict[str, int]` (findings by rule family: `punctuation`, `spelling`, `grammar`, `style`, `formatting`) using `engine.check`.
  - `words(text: str) -> int` (Arabic words via `iter_words`).
  - `rubric_rates(rows) -> Dict[mode, Dict[category, float]]` (errors per 100 words).
  - `verdict(rates, over_corrections: int) -> Tuple[bool, List[str]]`: pass iff `over_corrections == 0`, skill total ≤ 50% of baseline total, and no category's skill rate > baseline rate. Reasons listed when failing.
  - Prints a Markdown table (rubric rates as the headline; checker counts below as supporting detail), then `PASS` or `FAIL` with reasons.

- [ ] **Step 1: Write tests** in `tests/test_report.py` (import `evals.report`; add `evals/__init__.py`):
  - `test_verdict_pass`: baseline total 10.0, skill total 4.0, no category worse, 0 over-corrections → `(True, [])`.
  - `test_verdict_fail_overcorrection`: same rates, 1 over-correction → `False`, reason mentions `over-correction`.
  - `test_verdict_fail_category_worse`: skill `formatting` higher than baseline → `False`.
  - `test_verdict_fail_drop_too_small`: 10.0 → 6.0 → `False`.
  - `test_rubric_rates`: two fixture rows with known counts and word totals → expected per-100 rates.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3: Implement** `report.py`; write `prompts.tsv`, `triggers.tsv`, `rubric.csv` template, `generate.py`, `run_triggers.py`, `evals/README.md` (how to run, how to fill the rubric, blind scoring: shuffle file names before scoring).
- [ ] **Step 4:** Run all tests. Expected: PASS.
- [ ] **Step 5:** Run `python3 evals/generate.py --mode skill --only email-01` and `python3 evals/run_triggers.py` on 2 prompts. Expected: an output file exists; trigger table prints.
- [ ] **Step 6: Commit** `feat(evals): evaluation harness`

---

### Task 12: Run the evaluation and publish results

This task needs the owner; it pauses for their scoring.

- [ ] **Step 1:** Run `python3 evals/generate.py --mode baseline` and `--mode skill` (100 runs, uses the owner's Claude Code usage; confirm with the owner before starting). Run `python3 evals/run_triggers.py`.
- [ ] **Step 2:** Hand the owner the shuffled outputs and `rubric.csv` to score. **Wait.**
- [ ] **Step 3:** Run `python3 evals/report.py`. If `FAIL`, report the reasons to the owner and fix the skill (new tests for each missed error), then re-run the affected prompts. Repeat until `PASS` or the owner decides otherwise.
- [ ] **Step 4:** Update `README.md` with the results table, the trigger pass rate and 3 before/after examples from the outputs.
- [ ] **Step 5: Commit** `docs: evaluation results`
