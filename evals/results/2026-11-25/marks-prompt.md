You are an expert Arabic editor (Modern Standard Arabic), acting as a blind judge. Each file in `pairs/` contains a user prompt and two anonymous AI responses, A and B.

For EACH response, find every concrete error in these categories and quote it:
- **grammar**: agreement (including non-human plural → feminine singular), number–noun agreement, visible case endings, verb mood after لم/لن/أن, إنّ/أنّ, idafa, relative pronouns, conditionals;
- **spelling**: hamza, ة/ه, ى/ي, tanween alif, joined/split words;
- **translationese**: clear English calques (تم + masdar where a direct verb fits, قام بـ + masdar, passive + من قبل, كـ "as a", بشكل + adjective, unnatural subject-first order);
- **register**: dialect words, English words outside parentheses or code, English sentences or notes in an Arabic answer;
- **formatting**: Latin punctuation (, ; ?) in Arabic text, wrong spacing around punctuation, mixed digit systems, a line or bullet whose *first word* is Latin. Numbered-list markers (`1.`), counters like `(1/4)`, and numbers or percentages inside a sentence are **not** errors.

Do not count Cairo-Academy-approved forms (يعتبر، ساهم في، أكد على، أجاب على، في نفس الوقت، تخرج من، أبحاث، مدراء، إحصائيات، حوالي، كافة، هام، تواجد) or contested forms (طالما، بينما، سويًّا). Ignore code blocks, URLs, product names and placeholders. Count only language errors, not content differences. When unsure, don't count. When the prompt is in English, English notes to the user outside the Arabic text are not errors.

Judge only the files PAIRS_LIST. Do not modify any files.

Reply with ONLY tab-separated rows, no header, no prose, no code fence. One row per error occurrence (if the same error occurs three times, write three rows), in this exact form:
NN<TAB>A|B<TAB>category<TAB>quote<TAB>fix

- NN is the pair number, category is one of grammar, spelling, translationese, register, formatting.
- quote is the erroneous text copied EXACTLY, character for character, from the response: the shortest span that shows the error (usually 1 to 5 words), all from one line, with no added quotation marks, no Markdown changes and no ellipsis. For a line whose first word is Latin, quote that first word.
- fix is the corrected Arabic wording for that span (short), or empty if the fix is to delete it.
- Use a real tab character between fields. If a response has no errors, write no rows for it.
