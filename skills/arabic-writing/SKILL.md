---
name: arabic-writing
description: Use whenever you write, edit or review Arabic text, whatever language the request is in. This covers any answer given in Arabic; summaries, rewrites, edits, proofreading and review of Arabic text; documents, emails, posts, translations into Arabic, UI strings, commit messages and code comments in Arabic. It includes English requests such as "write this email in Arabic", "translate this to Arabic" or "proofread my Arabic", and Arabic requests (عربي، العربية، فصحى، اكتب، ترجم، لخّص، أعد صياغة، صحّح، راجع، حرّر، أجب). Writes correct, natural Modern Standard Arabic and checks grammar, spelling, punctuation and style before answering. Also use for Arabic dialect requests (عامية، لهجة، بالعامية المصرية، بالعامية الخليجية، باللهجة الشامية): it writes in the dialect and checks only formatting. Do not use for English-only work.
---

# Arabic writing

Write correct, natural Modern Standard Arabic (فصحى), then check it before you answer.

## Scope

- **Register:** Modern Standard Arabic. If the user asks for a dialect, write in that dialect and apply only the formatting checks (punctuation, digits, RTL line starts); do not "correct" dialect grammar or words.
- **Classical register, only on request:** if the user asks for classical or elevated literary Arabic (فصحى التراث، أسلوب تراثي، أسلوب القدماء، لغة جزلة, "classical Arabic") or for a genre that is classical by nature (خطبة جمعة، مقامة، وصية، مناظرة أدبية), read `references/classical.md` and write in that register. Otherwise stay in plain MSA: «فصحى» or «رسمي» alone does not mean classical.
- **Never touch** code, quotations, names, titles, or any text the user wants kept verbatim. Fix only your own Arabic, or the user's Arabic when they ask for a review or correction.
- When reviewing someone else's text, change only what is wrong. Never "fix" an approved form (see the last writing rule).

## Writing rules

Brief rules; details and examples live in the references.

- **Register:** MSA, consistent through the whole text. No dialect words unless the user asked for dialect.
- **Whole answer in Arabic:** notes, caveats, assumptions and follow-up offers stay in Arabic too. Don't switch to English for them unless the user wrote in English or asked for it.
- **Natural sentences:** prefer verb-first sentences where natural, and the active voice. Avoid the translationese patterns: تم/يتم + masdar, قام بـ + masdar, passive + من قبل, كـ for "as a", بشكل + adjective. **Judge density, don't ban:** one تم in a text is fine; one per sentence is translationese.
- **Agreement:** non-human plurals take the feminine singular (التي، هذه، ـها، verbs with ت). A verb before a plural subject stays singular.
- **Numbers:** follow the tables in `references/grammar.md`. Prefer digits for large or technical numbers, which also avoids number-word agreement errors.
- **Punctuation:** use ، ؛ ؟ « » with no space before the mark and one space after it.
- **Digits:** one system per text. Default to Western digits (0–9) in all writing, technical or not. Switch to Arabic-Indic digits (٠–٩) only if the user writes with them. Never use Persian digits (۰–۹). Code always uses Western digits.
- **Spelling conventions** (pick once, stay consistent): tanween on the letter before the alif (ـًا); مسؤول, not مسئول; مئة, not مائة.
- **Technical terms:** use the standard Arabic term from `references/glossary.md`. On first use, add the English term in parentheses, e.g. «واجهة برمجة التطبيقات (API)»; after that, write the Arabic term. An English word or acronym never stands bare in an Arabic sentence, not even a familiar one (HTTP، REST، JSON، HTTPS) or a button label: ✗ عبر IPC، ✗ اضغط «Fork»; ✓ عبر الاتصال بين العمليات (IPC)، ✓ اضغط زر الاشتقاق (Fork). Keep code identifiers in backticks, including commands, flags, file names and HTTP methods (`GET`، `POST`).
- **RTL safety in Markdown:** do not start a line, heading or bullet with a Latin word or a digit; reword so the line starts with Arabic. Keep English inside parentheses or backticks.
- **No italics** in Arabic text (use bold or « ») and **no tatweel** (ـ).
- **Approved forms:** never change the forms listed in `references/approved-forms.md`. When writing, you may prefer the more classical option where the references call it more elegant (e.g. في الوقت نفسه), but the checker and the review step never flag or change the approved form. Forms that purists reject without a confirmed Academy ruling (طالما، بينما، سويًّا …) are correct: do not flag them and do not mention them.

## Workflow

1. **Write** the draft with the writing rules in mind.
2. **Run the checker** when a shell is available and the Arabic part is longer than about two sentences, or whenever the text will be saved to a file.
   - Write the draft to a temporary file (for example under `/tmp` or your scratch directory) or pipe it on stdin with `-`. Never write the draft into the user's project.
   - Run:

     ```
     python3 <skill-dir>/scripts/check_arabic.py --fix /tmp/draft.md
     ```

     `<skill-dir>` is the folder that contains this `SKILL.md` file (the skill's base directory, if your agent shows one). For stdin: `python3 <skill-dir>/scripts/check_arabic.py --fix - < draft`.
   - Add `--digits arabic` if the user writes with Arabic-Indic digits.
3. **Read the output.** With `--fix` the script prints the fixed text, then `--- arabic-check findings ---`, then the remaining findings (`line:col  SEVERITY  rule  message  → suggestion`) or `no findings`. Exit code 0 means no `error` or `warn` remains; 1 means some remain; 2 means a usage error (fix the command).
   - `fix`: already applied in the printed text. Use that text as your new draft.
   - `error`: almost always wrong. Fix it unless it is clearly a false positive in context (a quote, a name, an approved form).
   - `warn`: likely wrong or unnatural. Decide each one: fix it, or leave it if it is right in context.
   - `info`: a hint (for example translationese density). Consider it; no change is required.
   - **If the user asked for dialect:** keep only the `fix` results and the `digit-mix` and `rtl-line-start` findings. Ignore `dialect-word`, hamza (`hamza-wasl`, `hamza-missing`), `misspelling`, `tanween-alif`, `merged-particle`, `alif-fariqa` and grammar findings (`sawfa-lan`, `jussive-nun`, `relative-after-indefinite`, `number-gender`, `compound-number`), and in step 4 apply only checklist item 7.
   - The checker skips code, URLs, emails, paths, ﴿…﴾ and YAML front matter. To exclude other text, wrap it in `<!-- arabic-check: off -->` and `<!-- arabic-check: on -->`.
4. **Self-review** with the checklist below, in priority order. The checker cannot see most grammar errors, so do this even when it reports `no findings`.
5. **Output** the final text only. Do not show the checker output or a list of corrections unless the user asked for a review.

**Short replies** (one or two sentences): skip the script, but still make a quick pass over the first checklist items.

**No shell** (or the script fails): skip steps 2–3 and apply the checklist alone, carefully.

## Self-review checklist

Go through these in order. Change only what is wrong; do not rewrite text that is already correct.

1. **Agreement:** every pronoun, relative pronoun, demonstrative, verb and adjective referring to a non-human plural is feminine singular. A verb before a plural subject is singular.
2. **Numbers:** every number + counted noun: gender reversal for 3–10, singular accusative after 11–99, genitive singular after 100 and 1000, and ordinals. Check against `references/grammar.md`.
3. **Visible endings:** ـون/ـين and ـان/ـين by position; ن dropped after أن/لن/لم/كي and in idafa; the weak letter dropped after لم and لا الناهية; the accusative alif where required, and absent on diptotes.
4. **إنّ vs أنّ**, idafa without ال on the first term, no الذي/التي after an indefinite noun, فاء in conditional answers, never سوف before لن (لن alone negates the future).
5. **Translationese:** density, stock paragraph openers, and English idioms translated word for word (`references/style.md` §4.1). In posts and translations, read each sentence and ask whether an Arabic writer would put it that way; rephrase any that follow an English idiom (✗ يصنع الفرق، ✗ جعلوا الحفل ممكنًا، ✗ يضع … تحت الضغط).
6. **Register and language mixing:** no English word or acronym outside parentheses or code (after its first use, the Arabic term alone), no English sentences or notes, no dialect words.
7. **Formatting:** RTL-safe line starts, one digit system, consistent spelling conventions.

## References

Read a reference when the situation calls for it, not all of them every time. Wrong examples are marked ✗ and correct ones ✓.

- `references/grammar.md`: before writing numbers with counted nouns, plurals of things, sound plurals or duals, إنّ/أنّ, conditionals or relative clauses, and when reviewing any of them.
- `references/orthography.md`: when unsure of a hamza seat, ة/ه, ى/ي, a joined or split word, tanween, punctuation, digits, or how to lay out mixed Arabic and English in Markdown.
- `references/style.md`: when a draft sounds translated or machine-written, before writing a long piece, and when choosing register or technical terms.
- `references/common-errors.md`: when reviewing Arabic text (yours or the user's) for frequent errors, and before telling anyone that a form is wrong.
- `references/approved-forms.md`: before flagging or changing any word a purist "قل ولا تقل" list rejects, and whenever a checker finding or your own instinct says a common modern form is wrong.
- `references/classical.md`: only when the user asks for classical or elevated literary Arabic, or for a sermon, maqama, counsel or literary debate.
- `references/glossary.md`: when writing about software, the web, AI or data and you need the standard Arabic term.
