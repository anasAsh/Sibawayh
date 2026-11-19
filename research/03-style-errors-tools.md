# 03 — Arabic style, common errors, LLM-specific failure modes, and checking tools

Research notes for a Claude skill that checks Arabic text Claude writes before the user sees it.
Compiled 2026-11-19. Arabic examples are given as **✗ wrong → ✓ preferred**.

Status labels used throughout:

- **[FIRM]**: an error by near-consensus (orthography, morphology, grammar). Safe to auto-flag.
- **[ACCEPTED]**: once listed as a "common error" but **approved by مجمع اللغة العربية بالقاهرة** (Cairo Academy) or otherwise widely accepted. The skill **must not** flag these as errors. At most it can offer the purist form as an optional style suggestion.
- **[CONTESTED]**: purists reject it, usage is very widespread, and I could not confirm an academy ruling. Flag only as a soft style note.
- **[STYLE]**: grammatical, but heavy, calqued or wordy. A style suggestion, not an error.

Main takeaway: purist "قل ولا تقل" lists (العدناني، مصطفى جواد، أسعد داغر "تذكرة الكاتب"، زهدي جار الله) reject many forms the Cairo Academy later approved through تضمين (one verb or preposition taking on another's meaning), قياس, or attestation. A checker built naively from those books would produce many false positives and make Claude's Arabic stiffer. Spend most of the effort on **[FIRM]** errors and on **translationese**, since those are what actually make LLM Arabic read badly.

---

## 1. Common usage errors (الأخطاء الشائعة / قل ولا تقل)

Sources: LanguageTool-ar `replaces.txt` / `grammar.xml` (mostly from Taha Zerrouki's *aghlat*/*fareh* databases), the arapenz.com summary of Cairo Academy approvals (53 items), مصطفى جواد *قل ولا تقل*, العدناني *معجم الأخطاء الشائعة*, plus general knowledge. Where an item says [ACCEPTED], the source is the Cairo Academy approval as reported by arapenz unless noted otherwise.

### 1.1 Orthography (all [FIRM]; most frequent in real text and cheapest to check)

| # | ✗ | ✓ | Note |
|---|---|---|---|
| 1 | الى، انشاء، اكثر، اذا | إلى، إنشاء، أكثر، إذا | Missing hamza on alif (همزة القطع). The single most common Arabic error in web text and in QALB. LLMs do it less often, but it happens, especially in lists and headings. |
| 2 | إستخدام، إنتقال، إستيراد | استخدام، انتقال، استيراد | Hamzat al-wasl in the masdars of أفعال خماسية/سداسية must not carry hamza. |
| 3 | الإطلاع | الاطّلاع | Same rule (masdar of اطّلع). It is in LT's list. |
| 4 | مدرسه، الشبكه | مدرسة، الشبكة | ة/ه confusion at word end. |
| 5 | الذى، فى، علي (=على) | الذي، في، على | ى/ي confusion. "الذى/فى" is an Egyptian print convention, but in pan-Arab MSA it is wrong. |
| 6 | استنفاذ | استنفاد | Root ن ف د (to run out), not ن ف ذ. |
| 7 | اضطرد | اطّرد | |
| 8 | البرئ، شيئ | البريء، شيء | Hamza seat rules. |
| 9 | مسئول / مسؤول mixed | pick one, usually مسؤول، شؤون | Both are valid regional spellings (Egypt: مسئول). LT `coherency.txt` flags **mixing** them. Consistency check. |
| 10 | لاكن، هاذا، ذالك | لكن، هذا، ذلك | Silent alif is not written. |
| 11 | كتاباً vs كتابًا mixed | one convention | Both placements of tanwīn al-fatḥ are accepted. Flag mixing only. |
| 12 | إنشاء الله (in the sense "God willing") | إن شاء الله | |
| 13 | على حدى / على حدا | على حِدَة | LT rule `collo_0043`. |
| 14 | مائة / مئة | both valid | مئة is modern and recommended. Flag mixing only. |

### 1.2 Morphology and agreement (mostly [FIRM]; these are where LLMs fail most)

| # | ✗ | ✓ | Note |
|---|---|---|---|
| 15 | ثلاث كتب / ثلاثة صفحات | ثلاثة كتب / ثلاث صفحات | Numbers 3–10 take the **opposite** gender of the singular of the counted noun. LT has `number_under_10_*`. |
| 16 | أحد عشر خطوة | إحدى عشرة خطوة | Compound numbers 11–19: both parts follow their own rules. LT `number_11_*`. |
| 17 | خمسة عشر ملفات | خمسة عشر ملفًا | 11–99 take a singular accusative تمييز. |
| 18 | ثلاثة ملف / عشرة ملفًا | ثلاثة ملفات | 3–10 take a plural genitive. |
| 19 | أحد الطالبات | إحدى الطالبات | أحد/إحدى agree with the noun. |
| 20 | بضع أيام | بضعة أيام | بضع/بضعة follows the 3–10 rule. |
| 21 | هذا الشبكة / ذلك الطريقة | هذه الشبكة / تلك الطريقة | Demonstrative gender agreement. LT `gender_000x` (33 rules, using POS tags). |
| 22 | الملفات الذين / الملفات موجودون | الملفات التي / الملفات موجودة | Non-human plurals take **feminine singular** agreement. A classic error of English-thinking writers and of LLMs. |
| 23 | ذهبوا الطلاب | ذهب الطلاب | In VSO order the verb is singular (لغة "أكلوني البراغيث" is non-standard). |
| 24 | المستخدمين يستطيعون (as subject) | المستخدمون يستطيعون | Sound masculine plural case: ـون in the nominative. LLMs often freeze ـين everywhere, a dialect habit. |
| 25 | إن المطورون | إن المطورين | Accusative after إنّ. LT `grammar_0002_nawasikh_*`. |
| 26 | لم يكتبون / لا تنسى (prohibition) | لم يكتبوا / لا تنسَ | Jussive after لم/لمّا/لا الناهية. LT `grammar_0010_jazem_*`. |
| 27 | كان المشروع ناجح | كان المشروع ناجحًا | خبر كان is accusative. |
| 28 | أخين | أخوين | Dual of أخ restores the و. |
| 29 | أراضي (nominative, indefinite) | أراضٍ | Defective nouns drop the ي: أغانٍ، محامٍ. **[ACCEPTED]**: the Academy allows keeping the ي (أغاني جديدة) "عند الحاجة". Low priority. |
| 30 | مدير ومعلمو المدرسة | مدير المدرسة ومعلموها | Two مضاف sharing one مضاف إليه. Purists reject it, and it is common in journalism. **[CONTESTED]**, but the ✓ form is always safe. |

### 1.3 Particles and fixed expressions

| # | ✗ | ✓ | Status / note |
|---|---|---|---|
| 31 | سوف لن / سوف لا | لن / لا | [FIRM] for سوف لن. LT `redund_0001`. |
| 32 | لا زال يعمل (meaning "still") | ما زال / لا يزال | [FIRM]. لا زال is a prayer formula (لا زلتَ بخير). LT `replaces.txt`. |
| 33 | كما وأن | كما أن / و… | [FIRM] per LT: two conjunctions cannot stack. |
| 34 | ما من أحد إلا ويعرف | إلا يعرف | [FIRM] (LT `collo_0009`). The و after إلا is redundant. |
| 35 | حتى أنه | حتى إنه | [FIRM]. حتى is ابتدائية here, so إنّ is mandatory. |
| 36 | كلما درستَ كلما فهمت | كلما درستَ فهمت | [FIRM]. Do not repeat كلما. |
| 37 | إلى عند | إلى | [FIRM] (LT redundancy). |
| 38 | عدا عن ذلك | فضلًا عن ذلك | [FIRM] per LT `collo_0042`. |
| 39 | لأول وهلة | أولَ وهلة | [STYLE] (LT). |
| 40 | كم عدد الملفات؟ | كم ملفًّا؟ / ما عدد الملفات؟ | [STYLE] (LT redundancy). |
| 41 | وأخيرًا وليس آخرًا | وأخيرًا | [STYLE]. Calque of "last but not least". |
| 42 | سويًّا (meaning "together") | معًا | [CONTESTED]. سويّ means "straight, balanced". LT flags it. |
| 43 | ليس فقط… بل أيضًا | لا… فحسب، بل… | [STYLE]. A calque of "not only… but also" (see §2). |
| 44 | طالما (meaning "as long as") | ما دام | [CONTESTED]. طالما classically means "often". |
| 45 | بالنسبة لي / أما بالنسبة إلى | لي / أما… | [STYLE]. LT `redundancies.txt`. |
| 46 | بينما (mid-sentence, contrastive) | في حين / على حين | [CONTESTED]. LT says بينما belongs at the head of the clause. Very common in good modern prose, so it is low priority. |

### 1.4 Items purists reject but the Cairo Academy approved (**[ACCEPTED]: do not flag**)

| # | Form flagged by purists | Purist form | Academy basis |
|---|---|---|---|
| 47 | يُعتبر (meaning يُعدّ) | يُعدّ | تضمين |
| 48 | ساهم / يساهم | أسهم / يُسهم | تضمين |
| 49 | أكّد على | أكّد (transitive) | approved |
| 50 | أجاب على السؤال | أجاب عن | تضمين حرف معنى حرف |
| 51 | أثّر على / أثّر بـ | أثّر في | same |
| 52 | تخرّج من الجامعة | تخرّج في | approved (non-physical exit) |
| 53 | اعتذر له / اعتذر عن الحضور | اعتذر إليه | approved |
| 54 | تحدّث مع، اتفق مع، اجتمع مع | تحدث إلى، اتفقا | approved (افتعل + مع) |
| 55 | في نفس الوقت / في ذات الوقت | في الوقت نفسه / ذاته | approved. The ✓ form is still more elegant: a [STYLE] option. |
| 56 | لم أفعله أبدًا (past negation) | قطّ | approved |
| 57 | حوالي عشرين | نحو عشرين | approved |
| 58 | مدراء | مديرون | approved |
| 59 | أبحاث | بحوث | approved (فَعْل → أفعال). LT still suggests بحوث; disable that rule. |
| 60 | إحصائيات، إمكانيات، فعاليات | إحصاءات، إمكانات | approved (مصدر صناعي) |
| 61 | أظافر | أظفار | approved. LT still flags it; disable. |
| 62 | الحياة الأفضل، الطريقة الأسهل | الفضلى | approved (أفعل التفضيل with ال, unattested forms) |
| 63 | الخمسة كتب، الألف ميل | خمسة الكتب / الكتب الخمسة | approved |
| 64 | البعض، الكل (with ال) | بعضهم، كلهم | approved |
| 65 | بصفته مديرًا | — | approved |
| 66 | أهرامات، خصائص (for خصيصة) | أهرام | approved (جمع الجمع). LT still flags أهرامات. |
| 67 | رجال بواسل | بُسَلاء | approved. LT still flags it. |
| 68 | أربعة بحور (plural of abundance with 3–10) | أربعة أبحر | approved |
| 69 | إخصائي، أخصائي | اختصاصي | approved |
| 70 | اللاسلكي، اللاوعي | — | approved (ال on negated compound) |
| 71 | سار بشكل حسن، بصورة جديدة | — | approved. "بشكل + adj" is still a [STYLE] smell when overused (see §2). |
| 72 | تهميش، تسييس، تطبيع، تنميط | — | approved coinages |
| 73 | شغوف بالقراءة، مهارات حياتية | مشغوف، حيوية | approved |

### 1.5 Still contested (soft suggestion at most)

| # | Form | Purist form | Note |
|---|---|---|---|
| 74 | الطلاب كافة ✓ vs **كافة الطلاب / الكافة** | الطلاب كافّةً | Classical كافة is حال only. Modern usage is overwhelmingly كافة + مضاف. I found no confirmed Academy decision in this research. Treat as [CONTESTED] and prefer the ✓ form. |
| 75 | أمر هامّ | أمر مُهِمّ | Classically هامّ means "worrying". Ubiquitous now. Prefer مهم. |
| 76 | تواجد (meaning "be present") | وُجِد / حضر / يوجد | Classically تواجد means "to feign ecstasy". Ubiquitous. Prefer وُجد/حضر. |
| 77 | الرئيسي / الرئيسية | الرئيس / الرئيسة | مصطفى جواد. Overwhelmingly used; low priority. |
| 78 | استبيان | استبانة | LT flags it. |
| 79 | العديد من | كثير من / عدد من | Purists: عديد = معدود. Widely accepted. |
| 80 | مؤخرًا | أخيرًا / منذ مدة قريبة | LT `worduse_0002`. Note that أخيرًا is ambiguous ("finally"). |
| 81 | متأكد من | متيقن من / واثق من | LT `word_use_0005`. |
| 82 | استلم الرسالة | تسلّم الرسالة | استلم = touched (the Black Stone). LT `verb_208`. Respected editors still enforce تسلّم. |
| 83 | قام بـ + masdar (قام بتثبيت الحزمة) | ثبّت الحزمة | Dictionaries record it, but LT calls it ركيك. The single most useful [STYLE] rule for LLM output (see §2). |
| 84 | مبروك | مبارَك | Colloquial origin. |
| 85 | شيّق (book) | شائق | جواد: شيّق = "longing", شائق = "arousing longing". |
| 86 | الكثير من | كثير من | Definite الكثير is criticised. Prefer كثير من. |

---

## 2. Translationese and calques from English (الترجمة الحرفية / العُجمة)

The skill should treat these as **style** issues with high payoff: one or two are acceptable, but a dense cluster of them is what makes text read as "translated" or machine-written. The fixes below are the natural MSA alternatives.

### 2.1 Voice and verb structure

1. **Agentive passive with من قِبَل / من طرف / بواسطة**
   ✗ تمت الموافقة على الطلب من قبل المدير. → ✓ وافق المدير على الطلب.
   Classical Arabic uses the passive precisely when the agent is **not** mentioned. If the agent is known, use the active voice. (Arabic translation-studies literature classes من قبل/من طرف as structural calque, النسخ البنيوي.) Rule: a passive verb or تمّ with من قبل/من طرف/بواسطة + agent → rewrite as active. [STYLE, high priority]

2. **تمّ / يتمّ + masdar** (the most recognisable LLM tell)
   ✗ تم إنشاء الملف وتم حفظه. → ✓ أُنشئ الملف وحُفظ. / أنشأنا الملف وحفظناه.
   ✗ يتم استخدام هذه الدالة لـ… → ✓ تُستخدم هذه الدالة لـ… / نستخدم هذه الدالة لـ…
   Use the proper مبني للمجهول, or better, an active verb with a real subject. One تم per page is tolerable; a heuristic threshold of more than one per ~150 words is a useful flag. [STYLE, high priority]

3. **قام بـ / يقوم بـ + masdar** ("does the X-ing")
   ✗ قم بتثبيت الحزمة ثم قم بتشغيل الأمر. → ✓ ثبّت الحزمة ثم شغّل الأمر.
   In instructions, use the direct imperative. LT has `syntax_0000_Qam_bi`. [STYLE, high priority]

4. **يمكنك + verb overuse** ("you can…")
   ✗ يمكنك فتح الملف ثم يمكنك تعديله. → ✓ افتح الملف وعدّله.

5. **يلعب دورًا (plays a role)**: a French/English calque (*joue un rôle*).
   ✓ يؤدّي دورًا / له أثر في / يُسهم في. [CONTESTED but widely used; prefer يؤدي]

6. **يأخذ مكانًا (takes place)** → ✓ يجري / يُعقد / يقع / يحدث. **يأخذ بعين الاعتبار** → ✓ يراعي / يأخذ في الحسبان. **يُلقي نظرة / دعنا نلقي نظرة على** → ✓ لننظر في / نستعرض. **يطرح سؤالًا** (fine). **يصنع فرقًا** (makes a difference) → ✓ يُحدث فرقًا / يغيّر.

### 2.2 كـ ("as a") and adverb calques

7. **كـ meaning "in the capacity of"**
   ✗ يعمل كمهندس / استخدم Redis كذاكرة مؤقتة → ✓ يعمل مهندسًا / استخدم Redis ذاكرةً مؤقتة (حال) / استخدم Redis بوصفه ذاكرة مؤقتة.
   كـ is for **similarity** (كالبحر). The "as a" sense is a calque. [STYLE; very frequent in LLM output]

8. **بشكل + adjective / بطريقة + adjective for English -ly adverbs**
   ✗ يعمل بشكل صحيح / بشكل فعال / بشكل كبير → ✓ يعمل كما ينبغي / بفاعلية / كثيرًا، أو مفعول مطلق: يتحسن الأداء تحسنًا كبيرًا.
   It is Academy-approved, but in clusters it is a strong translationese marker. LT flags بشكل عام → عمومًا / بوجهٍ عام.

9. **واحد من أهم / واحدة من أكثر** ("one of the most") → ✓ من أهم… / من أكثر…

### 2.3 Connectors and sentence openers

10. **بالتالي / وبالتالي** ("therefore"). LT calls it ركيكة. ✓ لذا / لذلك / ومن ثَمّ / فـ / وعليه.
11. **على حدٍّ سواء**: correct only *after a coordinated pair*, meaning "alike": ✓ للمبتدئين والمحترفين على حد سواء. Misuse: placing it after a single item, or using it to mean "also" or "at the same time".
12. **في نفس الوقت** → ✓ في الوقت نفسه. Same for **بنفس الطريقة** → ✓ بالطريقة نفسها, and **ذات الشيء** → ✓ الشيء ذاته. Academy-approved, so offer it as an option only.
13. **ليس فقط… ولكن أيضًا** → ✓ لا… فحسب، بل… / لا يقتصر على… بل يشمل…
14. **من المهم ملاحظة أن / تجدر الإشارة إلى أن / من الجدير بالذكر أن** (It's worth noting): usually delete it and state the fact.
15. **ومع ذلك، / علاوة على ذلك، / بالإضافة إلى ذلك، / في الختام،** at the start of consecutive paragraphs: the English essay template. Vary them or drop them. Arabic links clauses with **و / فـ / ثم / بل / إذ / حيث** rather than adverbial openers plus a comma. Note: the "humanizer-ar-msa" skill claims علاوة على ذلك is *wrong*. That is overstated: it is standard MSA. The problem is **frequency**, not correctness.
16. **بكلمات أخرى** (in other words) → ✓ أي / بعبارة أخرى. **في نهاية اليوم** (at the end of the day) → ✓ في المحصلة. **على الجانب الآخر** (on the other hand) → ✓ في المقابل / من جهة أخرى.
17. **من خلال** overused for "through/via/by". LT suggests بـ / عبر / في / بواسطة / باستعمال according to context.
18. **إذا… فإنّ…** after every condition, and **حيث** as a universal connector ("where/whereas"): both are overuse markers.

### 2.4 Word order and determination

19. **SVO where VSO is natural**: ✗ الشركة أعلنت عن إصدار جديد. → ✓ أعلنت الشركة إصدارًا جديدًا.
    A nominal sentence (mubtada' first) is fine for topic/contrast and in headings. A stream of "Noun + verb" sentences, however, reads as translated. Also note **أعلن عن** → أعلن (transitive) [STYLE].
20. **Over/under-use of ال in iḍāfa**: ✗ الدليل المستخدم (meaning "the user's guide") → ✓ دليل المستخدم. The first noun of an iḍāfa never takes ال. Both LLMs and English-thinkers produce noun + ال-noun pseudo-compounds (✗ الملف الإعدادات → ✓ ملف الإعدادات).
21. **English-style adjective stacking / noun compounds**: ✗ نظام إدارة قاعدة بيانات علائقية مفتوح المصدر → split it or use a relative clause.
22. **Possessive repetition** (English "your"): ✗ افتح ملفك ثم احفظ ملفك في مجلدك. → ✓ افتح الملف واحفظه في المجلد.
23. **Pronoun-first / cleft calques**: ✗ إنه من المهم أن… → ✓ من المهم أن… (or delete it). ✗ هناك العديد من الطرق التي يمكن… → ✓ ثمة طرق عدة لـ… / يمكن… بطرق عدة.

### 2.5 Punctuation and typography (largely mechanical; scriptable)

24. Use Arabic punctuation: **،** (U+060C) not `,`, **؛** (U+061B) not `;`, **؟** (U+061F) not `?`. LT handles these with `replaces.txt` (`?=؟`) and `Arabic*WhitespaceRule`.
25. No space **before** punctuation; one space after it. (LT: ArabicCommaWhitespaceRule, QuestionMark…, SemiColon…)
26. **Comma splices / comma chains**: English writers chain clauses with commas. Arabic either uses و/فـ or ends the sentence with a full stop. In the other direction, LLMs sometimes produce extremely long و-chains with no full stop. Flag sentences longer than about 60 words or with more than 4 commas.
27. Quotation marks: «…» or "…", used consistently. Do not mix with English “…”.
28. Tatweel (ـ, U+0640) should never appear in running text. Strip stray diacritics; diacritize only for disambiguation (see §3).
29. **Numerals**: choose one system per text. Mashriq: Arabic-Indic ٠١٢٣٤٥٦٧٨٩ (U+0660–0669) is traditional. The Maghreb, and most tech and UI writing, use Western 0–9. Never mix them in one text. Never use Persian ۴۵۶ (U+06F4–06F6). With Arabic-Indic digits, use ٫ (decimal) and ٬ (thousands). In code, versions, CLI flags and identifiers, digits **must** stay Western.
30. Percent: ٪ with Arabic-Indic digits, % with Western digits.

---

## 3. Errors specific to LLM-generated Arabic

### 3.1 What is documented (peer-reviewed or preprint)

| Finding | Source |
|---|---|
| **Language confusion**: in an Arabic prompt the model replies fully or partly in English, switches language line by line, or inserts isolated English words. Arabic is one of the languages measured at word level. LLM-based detection of word-level code-switching reached only ~86 F1, so the authors used heuristics (English words that don't normally occur in Arabic text). Mitigation: few-shot examples, multilingual SFT, and preference tuning. | Marchisio et al. 2024, *Understanding and Mitigating Language Confusion in LLMs* (Cohere), arXiv 2406.20052; code at github.com/for-ai/language-confusion |
| **Dialect vs MSA (diglossia)**: LLMs are fluent but poor at producing the *requested* dialect. They drift back to MSA, and post-training (instruction/RLHF) **reduces** dialect proficiency. Models also mix MSA forms into dialect output. | Robinson et al., **AL-QASIDA** (arXiv 2412.04193); MBZUAI ArabCulture-Dialogue (Hala-9B and Qwen3-8B scored 0.02–0.04 dialectness when asked for dialect); Saudi-Dialect-ALLaM (arXiv 2508.13525) measures "MSA leakage" with a 5-way dialect-ID classifier |
| **Gender agreement**: on gender-rewriting tasks, Arabic scores are lower and more variable than French or Hindi. Models change gender marking on entities that should not change in multi-entity sentences. | MORPHOGEN (arXiv 2604.18914, 2026) |
| **Grammatical error correction**: GPT-4 with expert prompting reaches ~65.5 F1 on QALB, about 5 points over the baseline, but it is still clearly below small fine-tuned seq2seq models (~73 F1). LLMs tend to *rewrite* rather than minimally edit. Implication: an LLM self-check of its own Arabic is useful but unreliable on fine morphology. | Kwon et al. 2023, *ChatGPT for Arabic GEC* / *Beyond English* (arXiv 2308.04492, 2312.08400) |
| ChatGPT is outperformed by fine-tuned smaller models on most Arabic NLU/NLG tasks, and is weaker on dialects. The human-evaluation rubric grades grammar, syntax, and fluency problems. | Khondaker et al., **GPTAraEval** (arXiv 2305.14976) |
| **English→Arabic translation** is the weak direction. Errors cluster in complex sentences and come from literal transfer of English structure. | Al-Andalus journal 2024 study; Jordan J. Modern Lang. & Lit. 2025; Frontiers in AI 2025 (GPT-4o post-editing) |
| **Bidi rendering**: Arabic mixed with English code spans, inline English terms, or punctuation renders in scrambled order in chat UIs (Claude Code VS Code extension, Claude Desktop, Cursor). Fenced code blocks are forced LTR. Proposed renderer fixes: Unicode bidi isolates or `unicode-bidi: plaintext`. | anthropics/claude-code issue #39720 and claudeissues.com reports #52316, #57419, #64727, #75196; Cursor forum threads |
| Existing Arabic benchmarks themselves contain many spelling and language-rule errors (e.g., 70% of the sampled Arabic INCLUDE items had severe spelling errors), so models learn from noisy Arabic. | *From Guidelines to Practice* (arXiv 2506.01920) |

### 3.2 Practitioner observations (not peer-reviewed; treat as hypotheses)

The `othmanadi/humanizer-semitic` skill pack (MIT, 2026; `humanizer-ar-msa`, `-shami`, `-egt`) lists 28 "AI tells" for MSA. The relevant ones:
- hedging overload (من المهم، يُعتقد أن، من الضروري)
- cliché openers (في العصر الحديث، في الآونة الأخيرة)
- formulaic conclusions (في الختام، وختامًا)
- **تم/يتم overuse** (rated critical)
- impersonal passives (يُعتبر، يُلاحَظ)
- overused transitions (بالإضافة إلى، وبالتالي، علاوة على ذلك)
- uniform sentence and paragraph length
- list and markdown overuse
- long و-chains
- unnecessary ال
- repeated nouns where a pronoun would do
- **inconsistent or wrong partial diacritics**
- formal MSA used in dialogue

The Shami variant notes that **سوف** and MSA verb forms leak into dialect output. Caveat: some of its claims are overstated (for example, that علاوة على ذلك is always wrong). Its 1.3-BLEU statistic is unsourced.

### 3.3 Additional failure modes to target (from experience with LLM Arabic; not formally measured)

1. **Number–noun agreement** (§1.2 #15–20). This is the most frequent hard grammatical error in fluent LLM Arabic, especially with digits in templates ("3 ملفات" is fine, but writing the number out goes wrong: ✗ ثلاث ملفات).
2. **Non-human plural agreement** (✗ الخيارات المتاحون / التي… هم) and verb–subject number in VSO order.
3. **Addressee gender**: defaulting to masculine (أنتَ، افعلْ) when the user is known to be female, or switching mid-reply. For unknown users, masculine generic is the norm. Use it consistently; don't mix in forms like (ـي/ـين).
4. **Case-ending errors** in sound plurals and duals: ✗ المستخدمين as subject; ✗ يوجد خيارين → ✓ يوجد خياران; ✗ إن المطورون → ✓ إن المطورين; ✗ أصبح الكود جاهز → ✓ جاهزًا.
5. **Dialect leakage into MSA**: Egyptian/Levantine/Gulf items: عشان، بس (meaning "only/but"), كمان، هيك، إيش، ده، دي، اللي (LT `darja.txt` has 241 entries), ـين plural everywhere, بـ- prefix on present verbs (بيعمل), هـ/حـ future marker. Also Egyptian spelling (ى for final ي).
6. **Code-switched English terms** without Arabic gloss, often with English plural or possessive morphology: ✗ الـ APIs, ✗ الـ commits تبعك.
7. **Calque density** (§2): تم + masdar, قام بـ, كـ "as", بشكل + adj, من قبل, من خلال, واحد من أهم.
8. **Machine-translation idioms**: "يلعب دورًا حاسمًا", "يمهد الطريق", "يسلط الضوء على", "في عالم اليوم سريع التغير", "رحلة" (journey) for any process, "غوص عميق" (deep dive).
9. **Punctuation**: Latin `,` `;` `?`; a space before ،; English quotes; `!` overuse.
10. **Bidi / markdown hazards**:
    - a bullet or heading **starting with an English word or a digit** takes LTR direction in many renderers, flipping the whole line
    - a line ending with an English word or `code` puts the Arabic full stop on the wrong side
    - parentheses around English inside Arabic look reversed in some views
    - tables with mixed-direction cells misalign

    Mitigations: start each list item and heading with an Arabic word; keep English inside `code` spans or parentheses mid-sentence rather than at line start or end; optionally use U+2068/U+2069 (FSI/PDI) isolates or U+200F (RLM) after a trailing LTR run (renderer-dependent, so use them sparingly).
11. **Diacritics**: random partial tashkīl (one word in a sentence fully vowelled) and wrong case vowels on it. Policy: no diacritics except a shadda or vowel to disambiguate (عُلِم vs عَلَم), and when present they must be correct.
12. **Numerals**: mixing ٣ and 3 in one answer; Persian digits; Arabic-Indic digits inside code.
13. **Over-formality**: classical and ornate vocabulary (إذ إنّ، لا سيما، حريّ بالذكر) in casual technical help, or saj'-like padding.

---

## 4. Register and technical terminology

### 4.1 Register

- **Default: Modern Standard Arabic (فصحى معاصرة)**, a "semi-formal" MSA: correct grammar, modern vocabulary, short sentences, no ornament. This is the register of good tech journalism (e.g., Arabic Wikipedia, BBC Arabic tech pages, Microsoft/Apple Arabic docs).
- **Dialect only if the user writes in a dialect *and* the context is casual**, or if the user explicitly asks. Even then, technical content usually stays in MSA. Arab users commonly accept "MSA reply to a dialect question". The reverse (dialect words in an MSA reply) reads as an error. **Never mix**: one register per reply. A dialect-word scan (LT `darja.txt`, CAMeL Tools dialect ID) is a cheap guard.
- **Formal vs semi-formal markers**:
  - Formal: إنّ…، نحو، إذ، لدى، يُرجى، حضرتكم.
  - Semi-formal, recommended for assistant replies: direct imperatives (افتح، شغّل), first-person plural for the writer (نستخدم، سنضيف), and short nominal-plus-verbal sentences.
  - Avoid: dialect-flavoured spoken forms (هلق، دلوقتي، زي، عشان); bureaucratic padding (نحيطكم علمًا، يسرّنا إفادتكم، ليكن في علمكم; LT flags these); hyper-classical rarities.
- **Consistency checks**: addressee gender and number (أنتَ / أنتِ / أنتم); one spelling convention (مسؤول/مسئول, ة vs ه in loanwords); one numeral system; one quote style.

### 4.2 Technical terms

Recommended policy, consistent with Microsoft/Apple Arabic localisation practice and Arabic tech writing:

1. **Use the established Arabic term when one exists and is actually used**, and give the English term in parentheses **on first mention only**: «واجهة برمجة التطبيقات (API)», then «الواجهة» or «API» consistently.
2. **Keep in Latin script, in `code`**: identifiers, commands, file names, product and brand names, library names, flags, and anything the user must type. Never transliterate these: ✗ «بايثون» in code context. Prose may use بايثون/Python, but pick one per reply; brand names are usually left in Latin script in tech text.
3. **Transliterate (تعريب صوتي)** only for terms whose Arabic coinage is not used in practice, and keep it to well-established forms: بروتوكول، خوارزمية، تقنية، برمجيات، إنترنت، كوكيز (often «ملفات تعريف الارتباط (cookies)»).
4. **Don't invent a translation.** If unsure, use English in parentheses.
5. **Arabic morphology on English words**: ✗ الـ commits، ✗ deployات. Rephrase: «الإيداعات (commits)» or «عمليات commit».

Common established equivalents:

| English | Arabic | English | Arabic |
|---|---|---|---|
| file / folder | ملف / مجلد | server / client | خادم / عميل |
| database | قاعدة بيانات | query | استعلام |
| function / method | دالّة (Syria: تابع) / طريقة، أسلوب (method) | variable / constant | متغير / ثابت |
| array / list | مصفوفة / قائمة | string | سلسلة نصية |
| loop | حلقة (تكرار) | condition | شرط |
| library / framework | مكتبة / إطار عمل | package / dependency | حزمة / اعتمادية |
| repository | مستودع | branch / merge | فرع / دمج |
| commit | إيداع (often kept as commit) | pull request | طلب دمج (pull request) |
| bug / debug | علّة، خطأ برمجي / تنقيح، تصحيح الأخطاء | deploy | نشر |
| cache | ذاكرة تخزين مؤقت | container | حاوية |
| thread / process | خيط / عملية | interface | واجهة |
| browser | متصفح | cloud | السحابة |
| open source | مفتوح المصدر | encryption | تشفير |
| machine learning | تعلّم الآلة | AI | الذكاء الاصطناعي |
| model / training | نموذج / تدريب | fine-tuning | ضبط دقيق / مواءمة |
| token (LLM) | رمز (token) | prompt | موجِّه / مُطالبة (prompt); no settled term |
| endpoint | نقطة نهاية | schema | مخطط |
| settings / configuration | إعدادات / تهيئة | install / update | تثبيت / تحديث |

Terminology sources to consult or pull lists from: Microsoft Terminology (the Microsoft Language Portal collection, downloadable as TBX), the Unified Dictionaries of مكتب تنسيق التعريب (ALECSO, e.g. المعجم الموحد لمصطلحات المعلوماتية), and the Cairo Academy's computing glossaries. Arabeyes' old glossary is useful for FOSS terms.

---

## 5. Existing tools and resources

PyPI data was checked live on 2026-11-19 through `https://pypi.org/pypi/<pkg>/json` (pip itself isn't installed on this machine). apt data comes from `apt-cache` on Ubuntu (resolute).

### 5.1 Summary table

| Tool | What it does | License | Local install | Usable from a skill script? |
|---|---|---|---|---|
| **LanguageTool (Arabic module)** | Rule-based grammar and style checker. Arabic: 444 rules in 14 categories, plus replace lists, spelling via Hunspell. | LGPL-2.1 (code); rule data as in repo | Java 17+ server (≈250 MB), Docker (`erikvl87/languagetool`), or `language-tool-python` 3.4.0 (PyPI, py≥3.9; downloads LT and needs Java). Public API `api.languagetool.org/v2/check?language=ar` works (tested). | **Yes.** Best ready-made option. HTTP JSON output. The public API sends text to a third party; a local Docker server avoids that. No Java on this machine; Docker 29 is present. |
| **LT rule files as data** | `grammar.xml` (418 KB), `replaces.txt` (666 pairs), `darja.txt` (241 dialect/loanword → MSA), `homophones.txt`, `redundancies.txt`, `wordiness.txt`, `coherency.txt`, `diacritics.txt`, `arabic_verb_masdar.txt` / `arabic_masdar_verb.txt` (≈160 KB each) | LGPL-2.1 | Plain files | **Yes, no Java needed**: the `.txt` lists load straight into a Python regex/lookup checker. `grammar.xml` POS-based rules need LT's tagger, but the simple token-sequence ones can be ported. |
| **CAMeL Tools** (NYU Abu Dhabi) | Morphological analysis and disambiguation, tokenization, **dialect identification** (city/country level), NER, sentiment, normalization, transliteration, dediacritization | MIT | `pip install camel-tools` (v1.6.0, 2026-06, **requires Python ≥3.11**), then `camel_data -i light` or `defaults` (large; BERT models via HF) | **Yes.** Good for: dialect-leak detection (DID), morphology-based agreement checks (gender, number, rationality of nouns), normalization. Heavy (torch for BERT components). |
| **CAMeL-Lab arabic-gec models** | AraBART GEC + CAMeLBERT GED (QALB-14/15, ZAEBUC), text-editing GEC models | MIT (HF tags) | HF Transformers; needs CAMeL morph preprocessing | Possible, but heavy (GPU preferable) and tuned to human L1/L2 errors (QALB is ~orthography-dominated), not to fluent LLM prose. Low priority. |
| **Farasa** (QCRI) / **farasapy** | Segmentation, POS, NER, lemmatization, diacritization, dependency parsing | farasapy MIT; **Farasa jars research-only, commercial use requires a license** | `pip install farasapy` (0.1.1, 2025-09), downloads jars, needs Java | Technically yes. License and the Java dependency make it unattractive; CAMeL Tools covers the same ground. |
| **MADAMIRA** (Columbia) | Morphological analysis/disambiguation (MSA + Egyptian) | Academic license by request; Java | Not on pip/apt | **No.** Superseded by CAMeL Tools. |
| **Qalsadi** | Morphological analyzer and lemmatizer (Taha Zerrouki; uses the Arramooz dictionary) | GPL | `pip install qalsadi` (0.5.1, 2025-07) | Yes. Lightweight, pure Python. Useful for POS/gender lookups when porting LT rules. |
| **PyArabic** | Arabic text utilities: strip tashkeel/tatweel, normalize hamza, number-to-words (`araby`, `number`) | GPL | `pip install pyarabic` (0.6.15, 2022) | **Yes.** Trivial dependency. Its `number` module can verify number–noun phrases (ArNumbers with gender). |
| **Mishkal** | Rule-based diacritizer | GPL | `pip install mishkal` (0.4.1, 2021) | Yes, but low accuracy compared with neural diacritizers. Only needed if diacritics are checked. |
| **Ghalatawi** | Autocorrect: word list + regex for common misspellings (hamza, ة/ه, ى/ي) | GPL-3.0 | `pip install ghalatawi` (0.3, 2023) | **Yes.** Directly relevant for orthography. |
| **Fareh** (linuxscout/fareh) | Database of common-error rules (`ArabicCommunErrors*.ods`) feeding LT | GPL-3.0 | git clone | Data source for rules. |
| **Aghlat** (linuxscout/aghlat) | Arabic misspelling corpus | AGPL-3.0 | git clone | Test data. |
| **Ayaspell / hunspell-ar** | Hunspell dictionary (ar + 18 locale aliases) | GPL-2+ / LGPL-2.1+ / MPL-1.1 | `apt install hunspell hunspell-ar` (3.5.2014-11-08, Ubuntu main); PyPI `spylls` (pure-Python Hunspell), `cyhunspell`, `pyenchant` | **Yes**: `hunspell -d ar -l` lists unknown words. Old (2014) and weak on modern tech vocabulary, so expect false positives on loanwords. Use as a hamza/typo net, with an allow-list. |
| **ar-corrector** | Simple n-gram spelling corrector | ? | PyPI 1.1.6 (2021) | Unmaintained; skip. |
| **Microsoft Office Arabic proofing** | Spelling + grammar in Word/Outlook/Editor (long-standing Arabic grammar checker; "Alef ↔ hamza" options, strict vs. non-strict) | Proprietary | Windows/Mac Office only | **No** scriptable local API. The Bing Spell Check API (part of the Bing Search APIs) was retired in 2025. |
| **Sahehly / صحّح** (Sakhr) | AI spelling + grammar + full tashkeel; web app; pricing page lists "API" | Proprietary SaaS | No | Only through a paid cloud API. It sends user text off-machine. A 2024 comparison (Sakhr vs Qalam vs Lisan) found Sahehly best at grammar. Not a default. |
| **Qalam / قلم** (qalam.ai, Mawdoo3) | AI spelling, grammar and diacritics; WordPress, Google Workspace, Office, iOS, Mac | Proprietary SaaS | No | Cloud only; best at spelling in the same 2024 comparison. Not a default. |
| **QALB corpus** | ~2M-word manually corrected Arabic (L1 comments 2014, L2 essays 2015); QALB-2014/2015 shared tasks (EMNLP/ACL ANLP workshops) | Research licence on request | Data only | Benchmarking. Error-type taxonomy (orthography, morphology, syntax, punctuation, etc.) useful for categorizing checks. Note: QALB is dominated by orthographic and punctuation errors; syntactic errors are a few percent. |
| **ZAEBUC**, A7'ta (أخطاء) corpus | L1 essay GEC corpus; sentence pairs from "common errors" books (arXiv 2411.04588) | Research | Data | Test sets for a checker. |
| **language-confusion benchmark** | Detects English leakage in non-English replies | Apache-2.0 (Cohere for-ai) | git | Its word-level heuristic is reusable for flagging English words in Arabic output. |

### 5.2 LanguageTool Arabic in detail (the best ready-made rule source)

Location: `languagetool-language-modules/ar/src/main/resources/org/languagetool/rules/ar/` (authors: Taha Zerrouki, Sohaib Afifi et al., 2019–). Java rules are in `.../java/org/languagetool/rules/ar/`.

`grammar.xml` categories and rule counts (counted from the file):

| Category | # | Examples |
|---|---|---|
| GENDER_AGREEMENT | 33 | demonstratives (هذا/هذه، ذلك/تلك، هذان/هاتان) vs noun gender, using POS tags |
| NUMBER_AGREEMENT | 22 | 1, 2, 3–10, 11, 12, 13–19 masc/fem |
| GRAMMAR_ERROR | 5 | jussive after لم/لمّا/لا الناهية |
| SYNTAX_COMMON_ERRORS | 107 | collocations: أقسم بأن، إلا و، حتى أنه، عدا عن، على حدى، بكل معنى الكلمة، كما وأن، من خلال، وبالتالي |
| WRONG_USE | 100 | verb usage: تأكد من، فشل في، استلم، استقل سيارة، استلفت… |
| COMMON_ERRORS_ON_ONE_WORD_USE | 63 | مؤخرًا، متأكد، ذاتًا، خطير، بأكمله |
| COMMON_ERRORS_ON_ADJECTIVES | 47 | أمر هام، حد كبير، النتائج الأفضل، شيء بسيط |
| COMMON_VERBS_ERRORS | 29 | wrong preposition with transitive verbs: ذكر بأن، قال بأن، علم بأن، تعصب ضد |
| REDUNDENCY_PHRASES | 7 | سوف لن، وأخيرًا وليس آخرًا، إلى عند |
| WRITING_STYLE | 2 | tanwīn al-naṣb placement |
| SEMANTICS | 10 | date/weekday consistency, month lengths |
| TO_REVIEW / TEST_NEW_FEATURES | 50 | off by default or experimental: قام بعمل، بشكل عام، nawāsikh with duals and plurals |
| COMMON_ERRORS_SYNTAX | 2 | القيام بـ |

Java rules: `ArabicCommaWhitespaceRule`, `…QuestionMarkWhitespaceRule`, `…SemiColonWhitespaceRule`, `ArabicDoublePunctuationRule`, `ArabicWordRepeatRule`, `ArabicHunspellSpellerRule`, `ArabicSimpleReplaceRule` (replaces.txt), `ArabicDarjaRule` (darja.txt), `ArabicHomophonesRule` (ض/ظ etc.), `ArabicRedundancyRule`, `ArabicWordinessRule` (هناك خطأ في → في… خطأ; ليكن في علم → نُعلم; لي عظيم الشرف → يشرفني), `ArabicWordCoherencyRule` (مسؤول/مسئول, شؤون/شئون, الذي/الذى), `ArabicTransVerbRule` (verb transitivity via the masdar↔verb lists), `ArabicInflectedOneWordReplaceRule` (أبحاث→بحوث, أحفاد→حفدة), `ArabicDiacriticsRule`, `ArabicConfusionProbabilityRule` (n-gram; needs data).

A live test of the public API with «هذا الشبكة كبيرة. ذهبت الى المدرسة وقام بعمل الواجب. سوف لن أذهب» returned: `gender_0001_hadha` (→ هذه الشبكة), `AR_SIMPLE_REPLACE` (الى → إلى), `syntax_0000_Qam_bi_test` (قام بعمل), `redund_0001_sawfa_lan` (→ لن). Every flag was correct.

Caveats for reuse:
- Several LT rules flag **Academy-approved** forms (أبحاث، أظافر، أهرامات، البواسل، استبيان، العديد…). These need an exclusion list (§1.4).
- `replaces.txt` mixes hard errors with purist lexical preferences: البنود → فقرات, أرشيف → محفوظات, استوديو → مرسم, إسفلت → زفت. Most `darja.txt` loanword entries (أرشيف، أجندة، إستاد) are **not** errors in modern MSA; only its true dialect words are useful.
- The POS-dependent XML rules need LT's Arabic tagger. Porting them standalone means re-implementing with Qalsadi or CAMeL morphology.

### 5.3 Practical recommendation for the skill

Realistic local stack, from lightest to heaviest:

1. **Pure-Python regex/lexicon checker (no dependencies; always run).** Covers:
   - Latin punctuation and spacing
   - numeral mixing and Persian digits
   - tatweel and stray diacritics
   - hamzat al-qaṭʿ/al-waṣl on a curated word list
   - ى/ي and ة/ه in known words
   - dialect-word list (filtered from LT `darja.txt` plus extra lists)
   - calque patterns: تم/يتم + masdar, قام بـ, من قبل after a passive, كـ + indefinite noun of role, بشكل + adj density, من خلال, بالتالي, واحد من أهم, ليس فقط, في نفس
   - FIRM fixed expressions from §1 (سوف لن، لا زال، كما وأن، حتى أنه، كلما…كلما، إلا و)
   - English-word leakage outside `code`
   - bidi hazards: list items or headings starting with Latin/digits
   - mixed spelling conventions

   Data can be seeded from LT's `.txt` files (LGPL, so keep the attribution), minus the §1.4 exclusions.
2. **Optional Hunspell pass** (`apt install hunspell hunspell-ar`, or `spylls` from PyPI) for typo and hamza detection, with a tech-vocabulary allow-list.
3. **Optional LanguageTool** (local Docker `erikvl87/languagetool`, or the public API only with user consent) for its POS-based gender and number rules.
4. **Optional CAMeL Tools** (Python ≥3.11) for dialect identification and morphology-based agreement checks. Too heavy to require.
5. **Final pass by Claude itself** using a checklist built from §1–§4. GEC research shows LLMs catch much but over-edit. The checklist should prioritize **FIRM** grammar (numbers, agreement, case after إنّ/كان/لم) and **calque density**, and explicitly forbid "correcting" §1.4 [ACCEPTED] forms.

---

## Sources

**Common errors / academy decisions**
- LanguageTool Arabic rules: https://github.com/languagetool-org/languagetool/tree/master/languagetool-language-modules/ar/src/main/resources/org/languagetool/rules/ar (grammar.xml, replaces.txt, darja.txt, redundancies.txt, wordiness.txt, coherency.txt, inflected_one_word.txt; fetched 2026-11-19)
- Fareh rules DB: https://github.com/linuxscout/fareh · Aghlat corpus: https://github.com/linuxscout/aghlat · Ghalatawi: https://github.com/linuxscout/ghalatawi
- حسين صادق، «الأخطاء اللغوية الشائعة… ما أجازه مجمع اللغة العربية بالقاهرة» (53 approved items): https://www.arapenz.com/common-mistakes-in-arabic-writing-part-1/
- مصطفى جواد، *قل ولا تقل* (examples: السكك الحديد، الرئيس/الرئيسة، الهُويّة، شائق) via https://www.abjjad.com/book/2192999864/ and https://new.saaid.org/twitter/f10.pdf; critique: «أغاليط مصطفى جواد», https://lark.uowasit.edu.iq/index.php/lark/article/view/4124
- مدونة مؤمن الوزان (on جواد's list and Academy approvals): http://mudawnatmumin.blogspot.com/2018/06/1.html
- Sources of Cairo Academy decisions (فيصل المنصور): http://faysalmansour.blogspot.com/2020/01/blog-post_31.html · «جملة قرارات مجمع اللغة العربية بالقاهرة»: https://www.nu.edu.ye/wp-content/uploads/2014/01/جملة-قرارات-مجمع-اللغة-العربية-بالقاهرة.pdf
- Debate on Academy permissiveness: https://diffah.alaraby.co.uk/diffah/print//herenow/2023/9/18/حول-إجازة-مجمع-اللغة-العربية-كلمة-ترند
- العدناني، *معجم الأخطاء الشائعة* (1973) and *معجم الأغلاط اللغوية المعاصرة* (1984): background knowledge, not fetched.

**Translationese**
- «الترجمة الحرفية وغزو الدخيل في اللغة العربية المعاصرة», مجلة اللسانيات (CRSTDLA): https://crstdla.dz/ojs/index.php/allj/article/download/244/206
- USJ translation-terminology glossary («يلعب دورًا» as calque): https://etib-certtal-terminologie.usj.edu.lb/?p=3327
- Univ. Sétif 2 course notes on النسخ البنيوي (من قبل/من طرف): https://cte.univ-setif2.dz/moodle/mod/resource/view.php?id=91329

**LLM Arabic quality**
- Marchisio et al. 2024, Language Confusion: https://arxiv.org/abs/2406.20052
- AL-QASIDA: https://arxiv.org/abs/2412.04193 · Saudi-Dialect-ALLaM: https://arxiv.org/abs/2508.13525 · ALLaM 34B UI eval: https://arxiv.org/abs/2508.17378 · MBZUAI ArabCulture-Dialogue: https://mbzuai.ac.ae/news/ai-can-spot-the-right-answer-at-an-emirati-wedding-saying-it-in-emirati-is-harder/
- MORPHOGEN (gender agreement): https://arxiv.org/abs/2604.18914
- Kwon et al., ChatGPT for Arabic GEC: https://arxiv.org/abs/2308.04492 · Beyond English: https://arxiv.org/abs/2312.08400
- GPTAraEval: https://arxiv.org/abs/2305.14976
- From Guidelines to Practice (Arabic eval guidelines): https://arxiv.org/abs/2506.01920
- Frontiers in AI 2025 (GPT-4o post-editing): https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1526293/pdf
- ChatGPT E→A complex sentences (Al-Andalus 2024): https://andalusuniv.net/AUSTNEW/andalus/../magazine/sh/2024/11/98/91aefa7551319d48bbdbf66190bdb320.pdf · Jordan J. Mod. Lang. Lit.: https://jjmll.yu.edu.jo/index.php/jjmll/article/download/279/285/12054
- humanizer-semitic skills (practitioner): https://github.com/othmanadi/humanizer-semitic (skills/humanizer-ar-msa/SKILL.md)
- Bidi rendering reports: https://github.com/anthropics/claude-code/issues/39720 · https://claudeissues.com/issue/52316-bidirectional-text-rendering-mixed-arabic-english-on-the-same-line-breaks-visual · https://claudeissues.com/issue/64727-bug-code-blocks-with-rtl-text-hebrew-arabic-render-ltr-bidi-layout-is-broken · https://forum.cursor.com/t/arabic-english-mixed-text-is-visually-reordered-incorrectly-in-cursor-chat-rtl-ltr-issue/152615

**Tools**
- CAMeL Tools: https://github.com/CAMeL-Lab/camel_tools · PyPI https://pypi.org/project/camel-tools/
- CAMeL arabic-gec: https://github.com/CAMeL-Lab/arabic-gec · models https://huggingface.co/CAMeL-Lab/arabart-qalb15-gec-ged-13 · Alhafni et al. EMNLP 2023: https://aclanthology.org/2023.emnlp-main.396
- farasapy: https://github.com/MagedSaeed/farasapy · Farasa: https://farasa.qcri.org/
- Qalsadi / PyArabic / Mishkal / Tashaphyne: https://github.com/linuxscout (PyPI pages checked)
- Ayaspell: https://ayaspell.sourceforge.net/ · https://github.com/munzirtaha/ayaspell · Ubuntu `hunspell-ar` package (copyright file inspected)
- language-tool-python: https://pypi.org/project/language-tool-python/ · LanguageTool API: https://api.languagetool.org/v2/
- Sahehly: https://sahehly.com/en/spelling-and-grammar-check · pricing https://sahehly.com/en/pricing
- Qalam: https://wordpress.org/plugins/qalam/ · AppSource listing https://appsource.microsoft.com/en-us/product/office/WA200002574
- Sakhr/Qalam/Lisan comparison: https://jarts.journals.ekb.eg/article_435453.html · Sahehly evaluation (Arabiyatuna 2024): https://doaj.org/article/1e0252c7ea654c26aeb23c9dbdbe9507
- IJNet guide to 50 Arabic proofreading tools: https://ijnet.org/en/node/14124
- QALB shared tasks: Mohit et al. 2014 (ANLP@EMNLP), Rozovskaya et al. 2015 (ANLP@ACL); Arabic GEC dataset from "common errors" books: https://arxiv.org/abs/2411.04588
- Cohere language-confusion code: https://github.com/for-ai/language-confusion
