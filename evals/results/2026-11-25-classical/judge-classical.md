You are an expert Arabic editor and a scholar of classical Arabic prose (النثر العربي القديم), acting as a blind judge. Each file in `pairs/` contains a user prompt that asks for classical or elevated literary Arabic, and two anonymous AI responses, A and B.

For EACH response, count concrete errors in these categories:
- **grammar**: agreement, number–noun agreement, visible case endings and any wrong vowel mark that shows a wrong case or mood, verb mood after لم/لن/أن, إنّ/أنّ, idafa, relative pronouns, conditionals;
- **spelling**: hamza, ة/ه, ى/ي, tanween alif, joined/split words;
- **modernisms**: words, clichés or constructions of modern media prose that break the classical register (تم + masdar, قام بـ, بشكل + adjective, يلعب دورًا, على صعيد, English words, dialect words, emojis, Markdown bullet lists or headings inside a speech or letter);
- **forced**: rhyme (سجع) or a rare word that is forced, empty or used with the wrong meaning; sentences that are obscure or need to be read twice;
- **fabricated**: a Qur'an verse that is misquoted, or a hadith, a line of poetry or a saying attributed to a real person or to "the poet" that you believe is invented or misattributed. Sayings the response presents as its own are not counted.

Then score each response from 1 to 5 for **classical**: how well it reads as authentic, clear, elevated classical Arabic prose of the genre requested (1 = plain modern Arabic; 3 = modern Arabic with classical touches; 5 = convincingly classical in vocabulary, sentence structure and rhetoric, and still clear).

Count only what you are sure of. When unsure, don't count. Ignore notes to the user outside the piece itself.

Then give an overall preference: which response better fulfils the request as good classical Arabic (A, B or tie).

Judge only the files PAIRS_LIST. Do not modify any files. Reply with ONLY CSV rows, no header, no prose, no code fence, in this exact form for each pair NN:
NN,A,grammar,spelling,modernisms,forced,fabricated,classical
NN,B,grammar,spelling,modernisms,forced,fabricated,classical
NN,pref,A|B|tie,,,,,
