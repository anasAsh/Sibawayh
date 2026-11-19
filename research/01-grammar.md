# 01 — MSA Grammar (نحو وصرف) Reference for an Arabic Output Checker

Purpose: rules a reviewer can check in **unvowelled** Modern Standard Arabic prose that Claude writes, ordered by how often they break in modern writing. Each rule: brief rule, correct example, typical error with fix, and **Check** = how reliably it can be detected from unvowelled text (High / Medium / Low).

Conventions
- `✗` = wrong, `✓` = correct, `→` = fix.
- **Contested** = classical grammarians or modern academies disagree, or the form is common and tolerated by some authorities. A checker should flag these as *suggestions*, not errors.
- Grading note: "High" means a surface pattern (letters, affixes, a trigger word) mostly decides the case. "Medium" needs some parsing (who is the subject, is the noun human, what gender is the counted noun). "Low" needs meaning or full syntactic analysis.

---

## 0. What is visible in unvowelled text

Short case vowels (ـُ ـَ ـِ) are invisible, so most إعراب on singular nouns and broken plurals cannot be checked. What **is** visible, and so checkable:

| Visible marker | Where it carries case/mood |
|---|---|
| ـون / ـين | sound masculine plural (nom / acc+gen) |
| ـان / ـين | dual (nom / acc+gen) |
| أبو/أبا/أبي, أخو/أخا/أخي, ذو/ذا/ذي, فو/فا/في | الأسماء الخمسة |
| tanween alif ـًا / ـاً | indefinite accusative (object, خبر كان, حال, تمييز, adverbs) |
| final ن of يفعلون/تفعلين/يفعلان | present indicative; dropped in subjunctive/jussive |
| final و/ي/ى of defective verbs | dropped in jussive / imperative (لم يدعُ) |
| long vowel of hollow verbs | shortened in jussive (لم يكن، لم يقل) |
| إ vs أ on إنّ/أنّ | kasra vs fatha choice |
| ت التأنيث on verbs, ة on adjectives | gender agreement |
| ال | definiteness agreement, idafa |
| ـا, ـوا, ـن on verbs | number agreement |
| alif after واو الجماعة | orthography marker of plural verb (كتبوا, لن يذهبوا) |

Consequence for a checker: concentrate on plurals, duals, five nouns, tanween alif, verb endings, agreement letters, and trigger words (إنّ، كان، لم، لن، أن، إنْ، الذي...).

---

## 1. Agreement (المطابقة)

### 1.1 Verb–subject (الفعل والفاعل)

| # | Rule | ✓ | ✗ → fix | Check |
|---|---|---|---|---|
| 1.1a | **Verb before an overt subject stays singular** (dual/plural subject). Gender still agrees. | ذهب الطلابُ / ذهبت الطالباتُ / نجح الطالبان | ✗ ذهبوا الطلاب → ذهب الطلاب; ✗ يطالبون العمال → يطالب العمال; ✗ نجحا الطالبان → نجح الطالبان | High (verb with ـوا/ـون/ـا/ـن directly followed by a plural/dual definite noun that is its subject). *Note:* the plural-marked form ("أكلوني البراغيث", لغة طيئ) is attested but non-standard; always flag. |
| 1.1b | **Verb after its subject agrees fully** (number and gender) because it carries a pronoun. | الطلاب ذهبوا / الطالبتان نجحتا / المهندسات حضرن | ✗ الطلاب ذهب → ذهبوا; ✗ الطالبتان نجحت → نجحتا | Medium–High |
| 1.1c | **Feminine ت on the verb**: obligatory with a real feminine singular/dual subject directly after the verb, and with any feminine pronoun subject. | قالت الوزيرةُ / الشمسُ طلعت | ✗ قال الوزيرة → قالت; ✗ الحكومة أعلن → أعلنت | Medium (needs gender of noun). Optional cases: subject separated from verb (حضر/حضرت الاجتماعَ امرأةٌ); figurative feminine (طلع/طلعت الشمس; prefer طلعت); broken plurals (قال/قالت الرجال). |
| 1.1d | Sound masculine plural subject → masculine verb; sound feminine plural (of real females) → feminine verb. | حضر المعلمون / حضرت المعلمات | ✗ حضرت المعلمون → حضر | High |
| 1.1e | **Country and organization names** as subjects: most country names and all organizations ending in ة are feminine. Some country names are treated as masculine: العراق، الأردن، لبنان، السودان، المغرب، اليمن. | أعلنت مصرُ / أعلن العراقُ / قالت الأمم المتحدة / أكدت الولايات المتحدة | ✗ أكد الولايات المتحدة → أكدت | Medium (needs a lexicon; masculine/feminine for some names is contested, e.g. لبنان/الأردن sometimes feminine). |
| 1.1f | Quantifier subjects (عدد من، بعض، معظم، أغلب، كل): verb before them agrees with the quantifier (singular masculine); pronoun agreement afterwards may follow meaning. | حضر عددٌ من الطلاب / معظم الدول أيّدت (agreement with المضاف إليه allowed) | ✗ حضروا عدد من الطلاب → حضر | Medium. **Contested** for agreement with مضاف إليه (معظم الطلاب حضروا vs حضر); both accepted. |
| 1.1g | Passive subject (نائب الفاعل) follows the same rules. | عُقدت الاجتماعاتُ / اعتُقل المتظاهرون | ✗ اعتقلوا المتظاهرون → اعتُقل | High |

### 1.2 Non-human plurals (جمع غير العاقل)

Rule: a plural of a **non-human** noun takes **feminine singular** agreement for verbs, adjectives, pronouns, demonstratives and relative pronouns. Feminine plural agreement (أيام معدودات) is also classical, mainly with small numbers / جموع القلة, but feminine singular is the default in MSA.

| ✓ | ✗ → fix | Check |
|---|---|---|
| الكتب مفيدة / الكتب التي قرأتها / هذه المشاريع وتمويلها / الدول التي وقّعت | ✗ الكتب مفيدون → مفيدة; ✗ المشاريع وتمويلهم → وتمويلها; ✗ هؤلاء الدول → هذه الدول; ✗ الدول الذين → الدول التي; ✗ الشركات أعلنوا → أعلنت | Medium (needs human/non-human classification; a lexicon of common nouns gets far). **Very high-risk for Claude**: English *they/them/which* invites masculine plural (ـهم، الذين، ـوا) for things, companies, countries, models, tools, files. |

Notes
- Collectives and institutions (الحكومة، الشركة، الفريق، الجيش، الشعب، الناس، القوم): singular agreement by form is safest; plural by meaning is attested (الناس يقولون / الناس تقول — both fine).
- Human feminine plural: prefer اللاتي/اللواتي and feminine plural verbs (الطالبات اللاتي نجحن); التي and feminine singular (الطالبات نجحت) are tolerated in modern prose. **Contested.**

### 1.3 Adjective–noun (النعت والمنعوت)

Rule: a true adjective follows its noun in **case, definiteness, gender, number** (with non-human plurals → feminine singular). Broken-plural human nouns can take broken or sound plural adjectives (رجال كرام / رجال مخلصون).

| ✓ | ✗ → fix | Check |
|---|---|---|
| البرنامج الجديد / برامج جديدة / مهندسون أكفاء / طالبتان متفوقتان / المدينة الكبيرة | ✗ المدينة الكبير → الكبيرة; ✗ البرنامج جديد (as phrase) → البرنامج الجديد; ✗ طالبتان متفوقتين (in nominative) → متفوقتان; ✗ هم مهندسين → مهندسون | Gender: Medium–High. Definiteness: Medium (البرنامج جديد is a valid *sentence*, so only flag when the pair is clearly a phrase, e.g. inside a PP or as object). Case on sound plurals/duals: High when the head's case is visible. |
| Adjective of an idafa: agrees with whichever term it describes. مديرُ الشركةِ الجديدُ (director new) vs الجديدةِ (company new) | — | Low (ambiguous unvowelled unless gender differs). |
| Words feminine without ة (must take feminine agreement): شمس، أرض، حرب، نفس، دار، ريح، بئر، عين، يد، رِجل، سنّ، نار، كأس. Both genders: طريق، سوق، سكين، حال، سبيل. | ✗ الحرب العالمي → العالمية; ✗ حرب طاحن → طاحنة | High with a lexicon. |

### 1.4 The dual (المثنى)

- Nominative ـان, accusative/genitive ـين; nun drops in idafa (§5).
- Verb before dual subject: singular (1.1a). Verb/pronoun after it: dual (نجحا/نجحتا، ـهما).
- Adjectives, demonstratives, relatives in dual must match case: هذان/هذين، هاتان/هاتين، اللذان/اللذين، اللتان/اللتين.
- كلا / كلتا: كلا with masculine, كلتا with feminine. With a following noun they are invariable (كلا الطالبين، في كلتا الحالتين); with a suffix pronoun they inflect (كلاهما / كليهما). Predicate may be singular or dual (كلا الحلّين مناسب / مناسبان); singular is preferred classically.

| ✓ | ✗ → fix | Check |
|---|---|---|
| في هذين اليومين / إن الطرفين اتفقا / في كلتا الحالتين / رأيتهما كليهما | ✗ في هذان اليومين → هذين; ✗ إن الطرفان → الطرفين; ✗ كلا الحالتين → كلتا; ✗ رأيت كلاهما → كليهما | High |

---

## 2. Numbers and counted nouns (العدد والمعدود)

Gender of the counted noun is always judged by its **singular** (حمّام → حمّامات is masculine: ثلاثة حمّامات; سجلّات → ثلاثة سجلّات; ساحة → ثلاث ساحات).

| Range | Gender of number | Counted noun (تمييز) | ✓ | ✗ → fix | Check |
|---|---|---|---|---|---|
| 1, 2 | **Agrees**; normally *after* the noun as adjective | — | كتاب واحد / كتابان اثنان / مدينة واحدة | ✗ واحد كتاب → كتاب واحد; ✗ اثنان كتب → كتابان | High |
| 3–10 | **Reverse** gender (masc noun → number with ة; fem noun → no ة) | genitive **plural** | ثلاثة كتب / ثلاث سيارات / خمسة أيام / عشر دقائق / سبع سنوات | ✗ ثلاث أيام → ثلاثة أيام; ✗ خمسة سنوات → خمس سنوات; ✗ ثلاثة طالب → ثلاثة طلاب | Medium (needs gender lexicon; very common error). |
| 8 | ثمانية (masc noun); with fem noun: ثماني + idafa (ثماني ساعات), standalone ثمانٍ (ساعات ثمانٍ), acc ثمانيَ | — | ثماني سنوات / ثمانية أشهر | ✗ ثمانية سنوات → ثماني سنوات; ثمان سنوات is widespread, a minority allows it (**Contested**) | Medium |
| 10 alone | Reverse: عشرة (m) / عَشْر (f) | genitive plural | عشرة أيام / عشر ساعات | ✗ عشرة ساعات → عشر ساعات | Medium |
| 11, 12 | **Both parts agree** | **accusative singular** | أحد عشر كوكبًا / إحدى عشرة دولةً / اثنا عشر شهرًا (nom) / اثني عشر شهرًا (acc/gen) / اثنتا عشرة / اثنتي عشرة | ✗ إحدى عشر دولة → إحدى عشرة; ✗ اثنا عشر in genitive (بعد اثنا عشر عامًا) → اثني عشر | High for internal consistency, Medium for gender. |
| 13–19 | First part **reverse**, second part (عشر/عشرة) **agrees**; both parts fixed on fatha | **accusative singular** | ثلاثة عشر طالبًا / ثلاث عشرة طالبةً / خمس عشرة دقيقةً | ✗ ثلاثة عشرة طالبًا → ثلاثة عشر; ✗ خمسة عشر دقيقة → خمس عشرة دقيقة; ✗ ثلاثة عشر طلاب → طالبًا | High for "same ة on both parts" (always wrong for 13–19); Medium overall. |
| 20–90 (العقود) | Invariant gender; inflect like sound masc plural (ـون nom / ـين acc+gen) | **accusative singular** | عشرون طالبًا / في ثلاثين يومًا / أربعين دولةً | ✗ عشرون طلاب → طالبًا; ✗ بعد ثلاثون عامًا → ثلاثين عامًا; ✗ عشرين طالب (missing alif) → طالبًا | High (tanween alif + ون/ين visible). |
| 21–99 (معطوف) | Unit follows its own rule (1–2 agree, 3–9 reverse), joined by و to the ten | accusative singular | واحد وعشرون عامًا / إحدى وعشرون دولةً / اثنان وعشرون / ثلاث وعشرون سنةً / خمسة وأربعون يومًا | ✗ ثلاثة وعشرون سنة → ثلاث وعشرون سنةً | Medium |
| 100, 1000 | Invariant (مئة/مائة, ألف). Dual مئتان/مئتين, ألفان/ألفين (مئتا/ألفا in idafa) | **genitive singular** | مئة كتاب / ألف سيارة / مئتا موظف / ألفي دولار (acc/gen) | ✗ مئة كتب → كتاب; ✗ ألف دولارًا → ألف دولار | High |
| 300–900 | مئة stays **singular** after 3–9, often written as one word | genitive singular | ثلاثمئة / خمسمئة طالب | ✗ ثلاث مئات طالب → ثلاثمئة طالب (مئات = "hundreds" vague) | High |
| 3000–10000 | ألف is masculine → number feminine-marked; ألف becomes plural آلاف | — | ثلاثة آلاف / عشرة آلاف دولار | ✗ ثلاث آلاف → ثلاثة آلاف | High |
| مليون، مليار | Masculine; plural ملايين، مليارات | genitive singular | ثلاثة ملايين نسمة / خمسة مليارات دولار | ✗ ثلاث ملايين → ثلاثة ملايين | High |
| Mixed numbers | Counted noun takes the form required by the **last-mentioned** (nearest) number | — | ألف ومئة كتاب / ألف وعشرون كتابًا / مئة وخمسون طالبًا | ✗ ألف وعشرون كتاب → كتابًا | Medium. Writing digits (123 كتابًا / 1500 دولار) sidesteps most errors; recommend digits for numbers > 10 in technical prose. |

Spelling: مئة (modern, Academy-recommended) and مائة (traditional) are both accepted; be consistent. Plural مئات.

### 2.1 Definite numbers

| ✓ | ✗ → fix | Check |
|---|---|---|
| Number as adjective after the noun: الأيام الثلاثة / السنوات الخمس (gender still reversed: الأيام الثلاثة, السنوات الخمس) | ✗ الثلاث سنوات → السنوات الثلاث / ثلاث السنوات | High (ال on a 3–10 number followed by an indefinite plural). Kufan grammar allows الثلاثة الأثواب — **Contested**, but avoid. |
| Compound: ال on the first part only: الأحد عشر كوكبًا / الخمس عشرة دقيقةً | ✗ الخمس العشرة | Low frequency |
| Tens: العشرون طالبًا / الطلاب العشرون | — | — |

### 2.2 Ordinals (العدد الترتيبي)

Rule: ordinals are on pattern فاعل and **agree** with the noun (no reverse gender). Compound ordinals: both parts agree; the first part of 11th is الحادي/الحادية (not الواحد). 1st = الأول/الأولى.

| ✓ | ✗ → fix | Check |
|---|---|---|
| الفصل الثالث / الصفحة الثالثة / القرن الحادي والعشرون / في القرن الحادي والعشرين / الدورة الخامسة عشرة / الطابق الحادي عشر / المرة الأولى | ✗ القرن الواحد والعشرين → الحادي والعشرين; ✗ الدورة الخامس عشر → الخامسة عشرة; ✗ الصفحة الثالث → الثالثة; ✗ الواحد عشر → الحادي عشر | High (fixed strings). |
| Final ordinal: الأخير/الأخيرة (last); آخِر = last, آخَر = other (invisible unvowelled → Low). | — | Low |

### 2.3 Number-like words

| Word | Rule | ✓ | ✗ → fix | Check |
|---|---|---|---|---|
| بضع / بضعة (3–9) | Like 3–9: reverse gender; also بضعة عشر | بضعة أيام / بضع سنوات | ✗ بضعة سنوات → بضع | Medium |
| نيّف | over (a ten): عشرون ونيّف | — | — | Low |
| كم الاستفهامية | Accusative singular | كم كتابًا قرأت؟ | ✗ كم كتب قرأت؟ → كم كتابًا | High |
| كم الخبرية | Genitive singular or plural, often with من | كم من مشكلة حُلّت! | — | Medium |
| عدّة | Behaves like 3–10 (idafa to plural) or as adjective after plural; gender of عدة does not change | عدة دول / دول عدة | — | — |

---

## 3. إعراب visible in unvowelled text

### 3.1 Sound masculine plural, dual, five nouns

| Position | SMP | Dual | الأسماء الخمسة |
|---|---|---|---|
| Nominative: subject, مبتدأ/خبر, اسم كان, خبر إنّ | ـون | ـان | أبو، أخو، ذو |
| Accusative: object, خبر كان, اسم إنّ, حال, مستثنى | ـين | ـين | أبا، أخا، ذا |
| Genitive: after a preposition, مضاف إليه | ـين | ـين | أبي، أخي، ذي |

| ✓ | ✗ → fix | Check |
|---|---|---|
| حضر المسؤولون / التقيت المسؤولين / مع المسؤولين / هم مسؤولون عن… | ✗ حضر المسؤولين → المسؤولون; ✗ هم مسؤولين → مسؤولون; ✗ مع المسؤولون → المسؤولين | After a preposition: **High**. Subject of a verb: Medium–High. خبر of a nominal sentence (هم/نحن + adjective in ـين): **High** and very common error (colloquial ـين leaks in). |
| شركة ذات خبرة / مهندس ذو خبرة / مع مهندس ذي خبرة / كان ذا أثر / يُعدّ ذا أهمية | ✗ مع مهندس ذو خبرة → ذي; ✗ كان ذو أثر → ذا; ✗ قضية ذو أهمية → ذات أهمية | High after prepositions and كان. **Contested**: compound proper names (أبو ظبي، أبو بكر) — strict: inflect (إلى أبي ظبي); widespread modern practice freezes أبو ظبي as a place name. |
| Coordination keeps case: التقيت المهندسين والفنيين | ✗ التقيت المهندسين والفنيون → والفنيين | Medium–High |

Five nouns inflect with letters only when (a) singular, (b) in idafa, (c) not to ي المتكلم (أبي = my father is fixed). ذو always in idafa to a noun (ذو خبرة). Feminine ذات inflects with vowels (invisible).

### 3.2 Accusative tanween alif (ـًا)

Rule: indefinite accusative triptote nouns/adjectives take a written alif with tanween fatha.
Exceptions (no added alif): words ending in ة (مرةً، خاصةً), in ء after alif (سماءً، ابتداءً، مساءً), in ى (هدًى، مستشفًى), diptotes (§4, مساجدَ), and the sound feminine plural (طالباتٍ, accusative with kasra).
Hamza: جزءًا، شيئًا، عبئًا، بطئًا (alif added after hamza on line when preceded by a non-alif letter or on a seat).

Accusative contexts to check: direct object, خبر كان and sisters, second object of ظنّ-verbs, حال, تمييز (incl. after 11–99), مفعول مطلق (شكرًا، جدًا), ظرف (يومًا، صباحًا), اسم إنّ when indefinite and delayed, adverbial accusatives (أيضًا، دائمًا، غالبًا، أحيانًا، تقريبًا، مثلًا، أولًا، ثانيًا، فعلًا، عمومًا، خصوصًا، حاليًا، سابقًا، مسبقًا، معًا), مستثنى after positive complete sentence, adjectives of an indefinite accusative noun.

| ✓ | ✗ → fix | Check |
|---|---|---|
| كتبت تقريرًا مفصلًا / أصبح الأمر ممكنًا / جاء مسرعًا / عشرون موظفًا / شكرًا جزيلًا | ✗ كتبت تقرير مفصل → تقريرًا مفصلًا; ✗ أصبح الأمر ممكن → ممكنًا; ✗ ليس سهل → سهلًا | Medium overall; **High** for: (a) خبر كان/أصبح/ليس/ما زال as a single indefinite word, (b) تمييز after 11–99, (c) fixed adverbs (أيضا، جدا، تقريبا). |
| رأيت مساجدَ كثيرة / زرت مدارسَ / أصواتًا / أوقاتًا / أمواتًا (root ت, broken plural → alif allowed) | ✗ زرت مدارسًا → مدارسَ; ✗ رأيت طالباتًا → طالباتٍ | High (ات+ًا is wrong unless ت is a root letter: أوقات، أصوات، أبيات، أموات، نبات، ثبات). |
| ابتداءً / مساءً / مرةً | ✗ ابتداءًا → ابتداءً; ✗ مرةًا | High |

Style: the tanween mark may sit on the alif (كتاباً) or on the letter before it (كتابًا); both appear. Pick one and be consistent; many modern editors and the Cairo/ Damascus academies' recent publications prefer placement on the letter before the alif. **Contested** (stylistic only).

### 3.3 كان وأخواتها (نواسخ ترفع الاسم وتنصب الخبر)

Members: كان، أصبح، أضحى، أمسى، ظلّ، بات، صار، ليس، ما زال/لا يزال، ما برح، ما فتئ، ما انفكّ، ما دام. Plus verbs of approximation/starting (كاد، أوشك، عسى، بدأ، أخذ، شرع) whose خبر is a present-tense verb clause.

| ✓ | ✗ → fix | Check |
|---|---|---|
| كان المشاركون متحمسين / أصبحت النتائج واضحةً / ليس الحلّ سهلًا / ما زال الطلاب قادرين / كانوا مهندسين | ✗ كان المشاركون متحمسون → متحمسين; ✗ أصبحوا قادرون → قادرين; ✗ كان المشاركين متحمسين → المشاركون | **High** (كان-family + SMP/dual/indefinite single word). |
| Same verb–subject agreement as 1.1: كان الطلاب حاضرين; كانت الحكومة | ✗ كانوا الطلاب حاضرين → كان الطلاب | High |
| ليس agreement: ليست المشكلة / لستُ / ليسوا | ✗ ليس المشكلة سهلة → ليست (preferred; ليس with fem. allowed when separated) | Medium |
| ما زال (continuity, past form) / لا يزال (present form) | لا زال in a declarative continuity sense → ما زال / لا يزال | High. **Contested**: strictly لا زال = optative ("may it not cease"); widely used and tolerated in modern prose. |
| كاد + مضارع without أن (preferred); أوشك/عسى + أن | كاد أن يسقط → كاد يسقط (أن is allowed but weaker) | Medium, **Contested** (both attested). |

### 3.4 إنّ وأخواتها (تنصب الاسم وترفع الخبر)

Members: إنّ، أنّ، كأنّ، لكنّ، ليت، لعلّ. Also لا النافية للجنس (لا شكَّ، لا بدَّ).

| ✓ | ✗ → fix | Check |
|---|---|---|
| إن المهندسين مجتهدون / إن الطرفين متفقان / لعل المسؤولين يدركون | ✗ إن المهندسون → المهندسين; ✗ إن المهندسين مجتهدين → مجتهدون | **High** for اسم directly after إنّ/أنّ/لكنّ. |
| **Delayed اسم** after a frontmatter PP/adverb is still accusative: إن لدى الشركة موظفين أكفاء / إن في ذلك فوائدَ / إن هناك تحدياتٍ / أنّ ثمة خلافًا | ✗ إن لدى الشركة موظفون → موظفين; ✗ أن هناك خلاف → خلافًا | High (إنّ + لدى/في/عند/هناك/ثمة + noun) and very common in modern writing. |
| لكنْ (light) has no effect: لكنِ النتائجُ جاءت | — | Low (لكن/لكنّ look identical unvowelled). |
| لا النافية للجنس: لا شكَّ، لا بدَّ، لا مانعَ من…، لا مسؤولين | ✗ لا شكًا → لا شكَّ | High (no tanween alif after لا + indefinite noun in this construction). |

**إنّ vs أنّ (hamza seat is visible)** — High, frequent.
- **إنّ (kasra)**: sentence start; after قال and its forms (قال، يقول، قيل، القول); after حيث، إذ، ألا، حتى (ابتدائية)، كلا; start of a relative clause (جاء الذي إنّه…); answer of an oath; when its خبر has لام المزحلقة (إنه لصادق); after a verb whose object would be suspended by that لام (علمتُ إنه لصادق).
- **أنّ (fatha)**: where the clause stands for a noun (مصدر مؤول): after verbs other than قال (أعلن، أكّد، ذكر، أوضح، أفاد، أشار إلى، يرى، علم، تبيّن), after prepositions (بأنّ، لأنّ، رغم أنّ), after لو، لولا، ما دام…
- ✗ قال أنّ الاجتماع… → قال إنّ; ✗ أكد إنّ → أكد أنّ; ✗ حيث أنّ → حيث إنّ (**Contested**: حيث أنّ is common and some tolerate it; classical rule requires kasra).
- Note: قال + أنّ is right only when قال means ظنّ (rare) — checker can still flag.

### 3.5 ظنّ وأخواتها (two accusative objects)

Members: ظنّ، حسب، خال، زعم، عدّ، جعل، رأى (opinion)، علم، وجد، ألفى، اتخذ، صيّر، ترك. Modern اعتبر (= عدّ) behaves the same.

| ✓ | ✗ → fix | Check |
|---|---|---|
| وجدتُ الحلَّ مناسبًا / عددتُ المشاركين مؤهلين / جعل المهمةَ سهلةً | ✗ وجدت الحل مناسب → مناسبًا; ✗ اعتبر الخبراء مخطئون → مخطئين (when الخبراء is object) | Medium (need to tell object from subject). |
| اعتبره صديقًا | — | **Contested**: purists (العدناني etc.) say اعتبر = "take a lesson" and prefer عدّه صديقًا; Cairo Academy and most modern usage accept اعتبر = عدّ. Do not flag. |

### 3.6 Verb moods: أن / لن / لم and friends

| Mood | Triggers | Marking visible unvowelled |
|---|---|---|
| Indicative (مرفوع) | default | الأفعال الخمسة keep ن: يذهبون، تذهبين، يذهبان |
| Subjunctive (منصوب) | أنْ، لن، كي/لكي، لـ (التعليل، الجحود)، حتى (future-oriented)، فاء السببية/واو المعية after طلب or نفي، إذن | **ن drops**: لن يذهبوا، أن يكونوا، كي تنجحي، ليتمكنا. Defective verbs keep the letter (لن يدعوَ، أن يرميَ، لن يسعى) |
| Jussive (مجزوم) | لم، لمّا، لا الناهية، لام الأمر، conditional tools (§6) | **ن drops** (لم يذهبوا); **final weak letter drops** (لم يدعُ، لم يرمِ، لم يسعَ، لا تنسَ); **hollow verb shortens** (لم يكن، لم يقل، لم يبع، لم يخف) |

Feminine plural ن (يكتبن) never drops: لن يكتبن، لم يكتبن.

| ✓ | ✗ → fix | Check |
|---|---|---|
| لن يتمكنوا / يجب أن يكونوا / لكي تفهموا / حتى يصلوا | ✗ لن يتمكنون → يتمكنوا; ✗ أن يكونون → يكونوا; ✗ كي تفهمون → تفهموا | **High** |
| لم يكونوا / لم يستطيعوا / لا تنسوا | ✗ لم يكونون → يكونوا | **High** |
| لم يأتِ / لم يبقَ / لم يسعَ / لم يرَ / لا تنسَ / لم ينتهِ / لم يعطِ | ✗ لم يأتي → يأتِ; ✗ لم يبقى → يبقَ; ✗ لا تنسى → لا تنسَ; ✗ لم ينتهي → ينتهِ; ✗ لم يرى → يرَ | **High**, very common. (لم يرَ written لم ير.) |
| لم يكن / لم يقل / لم يعد | ✗ لم يكون → يكن; ✗ لم يعود → يعد | High |
| Imperatives follow the jussive: ادعُ، امشِ، اسعَ، قلْ، كنْ، انتبهوا | ✗ ادعو (to one male) → ادعُ; ✗ انسى → انسَ | High |
| Alif فارقة after plural واو only: كتبوا، لن يكتبوا، لم يذهبوا; **not** after a root و: يدعو، يرجو، يسمو، نرجو | ✗ يرجوا (singular) → يرجو; ✗ مهندسوا الشركة → مهندسو | High |
| لم + present only; never لم + past | ✗ لم ذهب → لم يذهب / ما ذهب | High |
| Future negation: لن (never with س/سوف) | ✗ سوف لن / سوف لا → لن | High |
| لا + past only in دعاء or repeated (لا صدّق ولا صلّى) | ✗ لا ذهب أحد → ما ذهب / لم يذهب | High |
| حتى + present: subjunctive when purpose/future (ادرسوا حتى تنجحوا); indicative only when the action is present at time of speaking (rare) | — | Medium |
| أنْ vs أنّ: أنْ + verb, أنّ + noun/pronoun | ✗ أنّ يذهب → أن يذهب | High |

---

## 4. Diptotes (الممنوع من الصرف)

Effect: no tanween; genitive with fatha. **Visible consequence**: no tanween alif in the indefinite accusative. With ال or in idafa they become normal (في المساجدِ، في مساجدِ المدينة). Invisible otherwise (genitive fatha), so checker focuses on spurious ـًا.

Categories
1. **صيغة منتهى الجموع** (one cause suffices): مفاعل/مفاعيل, فواعل, فعائل, أفاعل… مساجد، مصابيح، مشاريع، رسائل، وسائل، قواعد، تجارب، مصادر، أساليب، دراهم، مناطق، معايير.
2. **Feminine alif** (ممدودة or مقصورة), one cause suffices: صحراء، حمراء، أصدقاء، علماء، وزراء، زملاء، أقرباء، أنبياء، أغنياء، خبراء، رؤساء، شعراء، أشياء (special), ذكرى، كبرى، فوضى.
3. **Proper names** + a second cause: feminine (فاطمة، زينب، مكة، حمزة), foreign (إبراهيم، باريس، لندن), ـان (عثمان، عدنان، سلمان، لبنان), verb pattern (أحمد، يزيد، تغلب), فُعَل (عمر، زحل), compound (حضرموت، بعلبك).
4. **Adjectives** + a second cause: أفعل/فعلاء (أحمر، أزرق), أفعل التفضيل (أكبر، أفضل، أكثر، أقل), فعلان/فعلى (عطشان، غضبان), numerical معدول (مثنى، ثلاث، رباع), أُخَر.

| ✓ | ✗ → fix | Check |
|---|---|---|
| زرنا مدارسَ عديدة / التقيت أصدقاءَ / استخدمنا أساليبَ مختلفة / لديه أشياءُ (no alif) | ✗ مدارسًا → مدارسَ; ✗ أصدقاءً → أصدقاءَ; ✗ أشياءً → أشياءَ; ✗ تجاربًا → تجاربَ | High (pattern-based: a broken plural with alif in 3rd position followed by 2–3 letters + ًا). |
| **Not** diptotes (hamza is a root letter, pattern أفعال): أسماءً، أنباءً، أعداءً، أجزاءً، أبناءً، أحياءً، أنحاءً، آراءً، أعباءً | ✗ flagging أعداءً as wrong | Needed exception list; otherwise false positives. |
| Defective منتهى الجموع (منقوص): nom/gen ـٍ with dropped ي: هذه مبانٍ حديثة / في ليالٍ باردة / معانٍ عميقة; acc keeps ي: رأيت مبانيَ / ليالِيَ | ✗ هذه مباني حديثة → مبانٍ; ✗ في نوادي كثيرة → في نوادٍ | Medium; **Contested in practice**: writing مباني/معاني/ليالي indefinite is extremely common in modern prose; strict grammar requires the dropped ي. Flag as suggestion. |
| Elative: بشكل أكبر / أكثرَ من (no tanween): كان الأمر أكثرَ تعقيدًا | ✗ أكثرًا → أكثرَ; ✗ أفضلًا → أفضلَ | High |
| Diptote proper names in accusative: زرت باريسَ / التقيت أحمدَ | ✗ أحمدًا → أحمدَ | High (for known names). |

---

## 5. Idafa (الإضافة)

| # | Rule | ✓ | ✗ → fix | Check |
|---|---|---|---|---|
| 5a | First term (مضاف) has **no ال** and **no tanween**. | مدير الشركة / كتاب الطالب | ✗ المدير الشركة → مدير الشركة; ✗ الثلاث سنوات → السنوات الثلاث; ✗ الكثير الطلاب → كثير من الطلاب | High. Exception (adjectival idafa, rare): الحسن الخلق، المتعدد الجنسيات — grammatical. |
| 5b | Dual/SMP **drop ن** as مضاف (and plural loses no alif فارقة). | مهندسو الشركة / موظفي الوزارة / طرفا النزاع / طرفي النزاع / معلمو المدرسة / بمساعدة مطوّري البرنامج | ✗ مهندسون الشركة → مهندسو; ✗ موظفين الوزارة → موظفي; ✗ طرفان النزاع → طرفا; ✗ مهندسوا → مهندسو | **High** (ـون/ـين/ـان + definite noun/genitive, no intervening word). |
| 5c | Case of مضاف shows on SMP/dual: nominative ـو / ـا, acc+gen ـي. | قال ممثلو الدول / التقى ممثلي الدول | ✗ قال ممثلي الدول → ممثلو | Medium–High |
| 5d | Second term (مضاف إليه) is genitive: visible on SMP/dual/five nouns. | رأي المختصين / عمل المهندسَين / مساعدة أخي | ✗ رأي المختصون → المختصين | High |
| 5e | **Two مضاف sharing one مضاف إليه**: prefer repeating with a pronoun. | قراءة الدرس وكتابته / مدير الشركة ونائبه | قراءة وكتابة الدرس → قراءة الدرس وكتابته | Medium. **Contested**: allowed by some (Kufan; Cairo Academy tolerates in modern usage); stylistic preference. |
| 5f | Adjective cannot come between مضاف and مضاف إليه. | مدير الشركة الجديد / المدير الجديد للشركة | ✗ مدير الجديد الشركة → مدير الشركة الجديد | Medium |
| 5g | ال on غير / بعض / كل. | المنظمات غير الحكومية / بعضهم / الطلاب كلهم | المنظمات الغير حكومية → غير الحكومية | High. **Contested**: الغير، البعض، الكل are widespread; some academies tolerate البعض/الكل; غير الحكومية is the safe form. |
| 5h | كافة, نفس, عامة as emphasis | الطلاب كافةً / الكتاب نفسه / الناس عامةً | كافة الطلاب; نفس الكتاب | Medium. **Contested**: purists restrict كافة to حال (no idafa, no ال) and prefer الكتاب نفسه; modern lexica (معجم الصواب اللغوي) accept كافة الطلاب and نفس الكتاب. Suggestion only. |

---

## 6. Relative pronouns and demonstratives

### 6.1 Relative pronouns (الأسماء الموصولة)

| Referent | Nom | Acc/Gen |
|---|---|---|
| masc sg | الذي | الذي |
| fem sg, **any non-human plural** | التي | التي |
| masc dual | اللذان | اللذين |
| fem dual | اللتان | اللتين |
| masc plural (human) | الذين | الذين (one ل; invariant) |
| fem plural (human) | اللاتي / اللواتي / اللائي (التي tolerated) | same |
| general | مَن (persons), ما (things) | — |

| Rule | ✓ | ✗ → fix | Check |
|---|---|---|---|
| Relative must match antecedent | الطلاب الذين / الدول التي / الأدوات التي / المشكلتان اللتان | ✗ الأدوات الذين → التي; ✗ الشركات الذين → التي; ✗ الطالبان الذي → اللذان | High (with human/non-human lexicon) |
| Spelling: plural الذين (one ل), dual اللذين (two ل) | الطلاب الذين | ✗ الطلاب اللذين → الذين | High |
| Dual case | رأيت الفريقين اللذين فازا / في المجالين اللذين | ✗ رأيت الفريقين اللذان → اللذين | High |
| **No relative after an indefinite antecedent** (the clause is a صفة) | قرأت كتابًا يشرح… / مشكلة لم تُحلّ | ✗ قرأت كتابًا الذي يشرح → الكتاب الذي / كتابًا يشرح | **High** (indefinite noun + الذي/التي/الذين). Common calque from English *which/that*. |
| عائد (resumptive pronoun) and verb in the صلة agree with antecedent | الطالبة التي نجحت / الخطط التي وضعناها | ✗ الخطط التي وضعناهم → وضعناها | Medium |

### 6.2 Demonstratives

| | Near | Far |
|---|---|---|
| masc sg | هذا | ذلك / ذاك |
| fem sg, non-human plural | هذه | تلك |
| masc dual | هذان / هذين | ذانك (rare) |
| fem dual | هاتان / هاتين | تانك (rare) |
| human plural | هؤلاء | أولئك |

| Rule | ✓ | ✗ → fix | Check |
|---|---|---|---|
| Agree in gender/number; non-human plural → هذه/تلك | هذه الأدوات / تلك المشاريع / هؤلاء الخبراء | ✗ هذا الطريقة → هذه; ✗ هؤلاء المشاريع → هذه; ✗ هذه المشروع → هذا | High (with gender lexicon) |
| Dual case | في هذين المجالين / إن هاتين الدولتين | ✗ في هذان → هذين; ✗ بين هاتان → هاتين | High |
| Demonstrative + ال noun = phrase; + indefinite = sentence: هذا الكتاب (this book) vs هذا كتاب (this is a book). With idafa, demonstrative follows: كتاب الطالب هذا / كتابه هذا | ✗ هذا كتاب الطالب meaning "this student's book" (ambiguous) → كتاب الطالب هذا | Low–Medium |
| Spelling: هذا، هذه، ذلك، هؤلاء، أولئك، لكن (no written alif) | — | ✗ هاذا، ذالك، هاؤلاء | High (orthography) |

---

## 7. Conditionals and other jussive contexts

| # | Rule | ✓ | ✗ → fix | Check |
|---|---|---|---|---|
| 7a | **Jussive tools** (إنْ، مَن، ما، مهما، متى، أينما، حيثما، كيفما، أيّ، أيّان، أنّى) put present-tense verbs of condition and answer in the jussive. | إن تجتهدوا تنجحوا / من يعمل يجدْ / مهما تحاولوا… | ✗ إن تجتهدون تنجحون → تجتهدوا تنجحوا; ✗ من يسعى ينجح → من يسعَ ينجحْ | High for الأفعال الخمسة and weak verbs. |
| 7b | Past tense after these tools is fine (and common in MSA). | إن اجتهدتَ نجحتَ | — | — |
| 7c | **إذا** is not a jussive tool; usually + past. | إذا اجتهدتم نجحتم | ✗ إذا تجتهدوا → إذا اجتهدتم / إذا تجتهدون | High |
| 7d | **لو** (counterfactual) + past; answer with لـ (often). لولا + noun (مبتدأ, خبر deleted) + لـ answer. | لو درس لنجح / لولا الدعمُ لفشل المشروع | ✗ لولا أن الدعم → لولا الدعمُ (لولا أنّ also correct) | Medium |
| 7e | **فاء in the answer** is required when the answer is: a nominal sentence; a request (imperative, prohibition, question); a frozen verb (ليس، عسى، نعم، بئس); preceded by ما / لن / قد / السين / سوف / رُبّما / كأنما. | إذا أردت النجاح فعليك أن تجتهد / إن كان الأمر عاجلًا فاتصل بنا / إن لم تحضر فلن تفهم / إذا كان هذا صحيحًا فهو… | ✗ إذا أردت النجاح عليك أن تجتهد → فعليك; ✗ إن لم تحضر لن تفهم → فلن تفهم; ✗ إذا كان صحيحًا هذا يعني → فهذا يعني | **High** (conditional + answer beginning with a noun, pronoun, عليك/علينا, لن, سوف, قد, ليس, or an imperative; an answer starting with a plain past/present verb such as يجب needs no فاء). Very common error. |
| 7f | **أمّا … فـ**: the فاء is obligatory. | أما الخيار الثاني فهو أبسط | ✗ أما الخيار الثاني هو أبسط → فهو | **High** |
| 7g | **كلّما** appears once; its answer is past and without a second كلما. | كلما زاد الطلب ارتفع السعر | ✗ كلما زاد الطلب كلما ارتفع → حذف كلما الثانية | **High** |
| 7h | **لمّا** (temporal, "when"): + past, answer past, no فاء. لمّا + present = "not yet" (jussive). | لمّا وصل الوفد بدأ الاجتماع / لمّا يصلْ بعد | — | Medium |
| 7i | Jussive in answer to a request (جواب الطلب), optional. | ادرسْ تنجحْ / تعالوا نتحدثْ | — | Low |
| 7j | لا الناهية + jussive; لام الأمر (ولْيكتبْ). | لا تنسوا / لا تقلقْ / ولْيعلم الجميع | ✗ لا تنسون → لا تنسوا; ✗ لا تنسى → لا تنسَ | High |

---

## 8. Prepositions and verb transitivity (تعدية الأفعال)

General principle: classical grammar permits **نيابة حروف الجر** (one preposition standing for another) and **التضمين** (a verb taking the preposition of a synonym). Cairo Academy accepted both, so many "wrong preposition" judgements are **soft**. Flag only pairings that change meaning or are rejected by nearly all authorities; mark the rest as suggestions.

### 8.1 Clear errors or meaning changes (flag)

| ✓ | ✗ | Note | Check |
|---|---|---|---|
| To replace old with new: استبدل الجديدَ **بالقديم** (= took the new, gave up the old) / استعاض عن القديم بالجديد / حلّ الجديد محلّ القديم | استبدل القديم بالجديد (intending "replace old with new") | الباء goes on the item **given up** (Quran 2:61 أتستبدلون الذي هو أدنى بالذي هو خير). Classic reversal; Claude often calques English "replace X with Y". | Low (semantic) — but worth a targeted prompt check. Similar: بدّل/أبدل/تبدّل. |
| بحث **عن** = search for; بحث **في** = investigate/discuss | بحثنا في المفتاح المفقود → بحثنا عن | Meaning differs | Low |
| رغب **في** = want; رغب **عن** = shun | — | Opposite meanings | Low |
| يتطلّب الأمرُ وقتًا (direct) | يتطلّب إلى وقت | — | High |
| يحتاج **إلى** | يحتاج لـ (acceptable), يحتاج الشيءَ (contested) | — | Medium |
| سافر/وصل/انضمّ/أدّى/أشار/توصّل/لجأ/استمع **إلى** | أدّى لـ (acceptable via لام), وصل لـ (acceptable) | soft | Low priority |
| حصل **على**، اعتمد **على**، اطّلع **على**، أشرف **على**، حافظ **على**، ركّز **على**، وافق **على** | حصل لـ → على | — | Medium |
| شارك **في**، أسهم **في**، أثّر **في**، رغب **في**، نجح **في** | — | — | — |
| طالب **بـ** (حقه)، تميّز **بـ**، اتّسم **بـ**، اهتمّ **بـ**، التزم **بـ**، سمح **بـ** | سمح لفلان بالدخول ✓ (لـ for person, بـ for thing) | — | Medium |
| تخلّى **عن**، تحدّث **عن**، أعرب **عن**، عبّر **عن**، كشف **عن**، أسفر **عن**، نتج **عن** | — | — | — |

### 8.2 Contested pairings (suggest, don't block)

| Common modern | Purist preference | Status |
|---|---|---|
| أجاب **على** السؤال | أجاب **عن** السؤال / أجاب السؤالَ | عن is the classical standard; على defended via تضمين. Prefer عن. |
| أكّد **على** الأمر | أكّد الأمرَ / أكّد أنّ | Widely criticized; defended via تضمين (شدّد على، حرص على). Prefer direct object. |
| ساهم في | أسهم في | ساهم classically = cast lots with; Cairo Academy accepts ساهم = شارك. Prefer أسهم. |
| أثّر **على** | أثّر **في** | في is classical; على widely used. Prefer في. |
| تعرّف **على** | تعرّف **إلى** | Both widely accepted. |
| اعتذر **من** فلان | اعتذر **إلى** فلان **عن** الخطأ | Prefer إلى/عن. |
| تخرّج **من** الجامعة | تخرّج **في** الجامعة | Both accepted; في is the purist form. |
| شكره / شكر له | — | Both classical. |
| بالرغم من / رغم أنّ / على الرغم من | على الرغم من | All acceptable. |
| حوالي (= approximately) | نحو، قرابة، زهاء، ما يقرب من | حوالَي = around (spatial); approximate use is widespread and tolerated. |

### 8.3 Common lexical/style errors often lumped with grammar (soft flags)

| Form | Preferred | Status |
|---|---|---|
| سوف لن / سوف لا | لن | Error (High) |
| كما وأنّ | كما أنّ | Error (redundant و) (High) |
| كلما… كلما | single كلما | Error (High) |
| ليس فقط… بل | لا… فحسب، بل / ليس… فحسب، بل | Calque; suggestion |
| تمّ + مصدر (تم إطلاق التحديث) | أُطلق التحديث / أطلقنا التحديث | Grammatical; overuse is a translationese marker. Suggestion. |
| من قِبَل as passive agent (نُشر من قبل الفريق) | نشره الفريق | Calque; suggestion. |
| قام بـ + مصدر (قام بتحليل) | حلّل | Verbose; suggestion. |
| تواجد / متواجد (= exists) | وُجد / موجود | تواجد = feign ecstasy classically; Cairo Academy accepts the modern sense. Suggestion. |
| هامّ | مهمّ | هامّ = worrying classically; widely accepted now. Suggestion. |
| مدراء | مديرون | Common; مديرون is standard. Suggestion. |
| بالتالي | لذا، ومن ثمّ، وعليه | Widely used; purists object. Suggestion. |
| إنّ هكذا قرارات | إنّ قرارات كهذه / مثل هذه القرارات | Error (هكذا is adverbial) — Medium. |
| هب أن… | هبْ… (directly) | Suggestion. |
| نجاحك مبروك | مبارك | Lexical (مبروك = knelt camel). Suggestion. |
| عدم + adjective (غير) / عدم + مصدر | عدم الحضور ✓; غير مسؤول ✓ | ✗ عدم مسؤول → غير مسؤول (High) |

---

## 9. Other high-value rules

| # | Rule | ✓ | ✗ → fix | Check |
|---|---|---|---|---|
| 9.1 | **Nominal sentence**: مبتدأ and خبر nominative. Pronoun + SMP adjective → ـون. | نحن مستعدون / هم مسؤولون / الطلاب متحمسون | ✗ نحن مستعدين → مستعدون; ✗ هم موجودين → موجودون | **High**, frequent (dialect leakage). |
| 9.2 | **Exception (الاستثناء) with إلا**: positive complete → accusative; negative complete → accusative or same case as the excepted-from; incomplete negative (مفرّغ) → case by function. | نجح الطلاب إلا طالبًا / ما نجح إلا طالبٌ واحد / لا يوجد إلا حلّان / لم أر إلا المهندسين | ✗ لا يوجد إلا حلين → حلّان; ✗ ما حضر إلا المهندسين → المهندسون | Medium–High for SMP/dual. |
| 9.3 | غير / سوى take a genitive noun; غير itself carries the case. | من غير المسؤولين / دون غيرهم | — | Medium |
| 9.4 | **حال** is indefinite accusative. | عاد الفريق منتصرًا / عملوا مجتمعين | ✗ عملوا مجتمعون → مجتمعين | Medium–High |
| 9.5 | **تمييز** after quantity/comparatives: accusative indefinite. | أكثر وضوحًا / أقل تكلفةً | ✗ أكثر وضوح → وضوحًا | High (أكثر/أقل/أشد + bare noun) |
| 9.6 | **Elative (أفعل التفضيل)**: with من → invariable masc. sg.; with ال → agrees; in idafa to definite → either. | هذه الطريقة أسرع من تلك / الطريقة الأسرع / هي أفضل الطرق | ✗ هذه الطريقة سرعى من → أسرع من; ✗ الطريقة الأسرع من → أسرع من (ال + من together) | High for "ال…من" and feminine elatives with من. |
| 9.7 | **Comparison of colors/defects and non-أفعل verbs**: use أشدّ/أكثر + تمييز. | أكثر احمرارًا / أكثر استخدامًا | ✗ أحمر من (in comparison) → أشد حمرة; ✗ أستخدم من → أكثر استخدامًا | Medium |
| 9.8 | **Emphasis (توكيد) with نفس/عين/كل/جميع**: follows the noun with a resumptive pronoun that agrees. | الطلاب أنفسهم / الدول كلها / المهندسون جميعهم | ✗ الدول كلهم → كلها | Medium |
| 9.9 | **Coordination (العطف)** keeps the case of the first conjunct. | إن المهندسين والفنيين / حضر المهندسون والفنيون | ✗ إن المهندسين والفنيون → والفنيين | Medium–High |
| 9.10 | **Apposition and badal** follow case. | التقيت أخاك محمدًا | — | Low |
| 9.11 | **منذ / مذ** + past or time noun. | منذ عامين / منذ أن بدأ | — | Low |
| 9.12 | **لدى / عند / مع** + genitive (visible in SMP/dual). | لدى المطوّرين / عند الطرفين | ✗ لدى المطورون → المطورين | High |
| 9.13 | **Vocative (المنادى)**: يا + definite-by-address singular: يا أيها الناس / يا أيتها النفس; يا + مضاف accusative (يا أخا العرب) | ✗ يا أيها المهندسات → يا أيتها | Medium |
| 9.14 | **كلا/كلتا** (see 1.4). | | | High |
| 9.15 | **Gender of verbs with an intervening object/PP is optional**, but default to agreement for safety. | أعلنت الوزارةُ / أعلنت أمس الوزارةُ | — | — |
| 9.16 | **Relative clause/adjective after a pronoun-suffixed noun**: adjective must be definite. | كتابه الجديد | ✗ كتابه جديد (as phrase) → كتابه الجديد | Medium |
| 9.17 | **أيّ** agreement: أيّ for both genders is standard; أيّة tolerated. | أيّ مشكلة / بأيّ طريقة | — | Low (no flag) |

---

## 10. Checker priority list (most frequent × most checkable)

1. Sound masc plural / dual case after prepositions, إنّ (incl. delayed اسم after لدى/في/هناك), كان-family خبر, and nominal-sentence خبر (هم مسؤولين).
2. Dropped ن in subjunctive/jussive (لن/أن/كي/لم/لا الناهية/إنْ + يفعلون).
3. Dropped weak letter / shortened hollow verb after لم, لا الناهية, imperatives (لم يأتي، لا تنسى، لم يكون).
4. Plural verb before an overt plural subject (ذهبوا الطلاب).
5. Non-human plurals: feminine singular agreement for verbs, adjectives, pronouns, التي، هذه (vs ـهم، الذين، هؤلاء).
6. Numbers: reverse gender 3–10 and 13–19, accusative singular تمييز after 11–99, genitive singular after 100/1000, ordinals (الحادي والعشرين، الخامسة عشرة).
7. Idafa: ال on مضاف (الثلاث سنوات), undropped ن (موظفين الشركة).
8. إنّ vs أنّ hamza (قال إنّ / أكّد أنّ).
9. Accusative tanween alif: present where required (خبر كان، تمييز), absent where forbidden (diptotes, ـات, ـة, ـاء).
10. Relative pronoun after an indefinite antecedent; اللذين vs الذين; dual relatives/demonstratives in case.
11. فاء in conditional answers and after أمّا; single كلّما; no سوف لن.
12. Feminine ت with feminine subjects (incl. country/organization names).

---

## 11. Caveats for automation

- Unvowelled ambiguity: كتب (wrote / books), علم, حسن — use POS context before agreement checks.
- Subject vs object: VSO order with case-invisible nouns makes 1.1a and §3.5 partly undecidable; rely on SMP/dual endings.
- Human vs non-human: needs a lexicon; edge cases (companies treated as people, AI models, "users" = المستخدمون human). Pronoun reference to المستخدمين is human (هم); to النماذج/الأدوات/الملفات non-human (ها).
- Proper nouns and foreign words: diptote status of transliterated brand names (غوغل، أمازون) is unsettled; never flag.
- Quoted text, code, dialogue in dialect: skip.
- Prefer "suggestion" severity for everything marked **Contested**.

---

## Sources

Consulted online for this file
- University lecture notes on العدد والمعدود (Al-Mustaqbal University, Iraq): https://www.uomus.edu.iq/img/lectures21/MUCLecture_2025_42151280.pdf ; https://www.uomus.edu.iq/img/lectures21/MUCLecture_2025_5524271.docx
- Al-Mustansiriya University lectures on العدد and الممنوع من الصرف: https://uomustansiriyah.edu.iq/media/lectures/7/7_2020_06_23!10_22_31_AM.docx ; https://www.uomustansiriyah.edu.iq/media/lectures/9/9_2017_09_30!02_31_16_PM.docx
- موسوعة 3rabica, العدد والمعدود: https://3rabica.org/العدد_والمعدود
- Edarabia, قواعد العدد والمعدود: https://www.edarabia.com/ar/?p=26979
- UC Davis, Arabic Without Walls, Grammar Note 7.4 (numbers): https://arabicwithoutwalls.ucdavis.edu/chapter7/grammar_note74.html
- Damascus Arabic Language Academy journal (مجمع اللغة العربية بدمشق), issue 80 article on منع الصرف: https://arabacademy-sy.org/uploads/magazine/mag80/mag80-4-1.pdf
- ديوان العرب, الممنوع من الصرف: https://www.diwanalarab.com/الممنوع-من-الصرف
- ديوان العرب, أخطاء لغوية شائعة: https://diwanalarab.com/أخطاء-لغوية-شائعة-10350
- ديوان العرب, أكلوني البراغيث: https://diwanalarab.com/أكلوني-البراغيث.html
- نبيلة قريني, لغة أكلوني البراغيث, مجلة جسور المعرفة (2020): https://asjp.cerist.dz/en/article/136639
- Mutammimat al-Ajurrumiyya (agreement of verb with overt subject): https://usul.ai/t/mutammimat-ajrumiyya/18
- المكتبة الشاملة, book 7517 (prepositions, تضمين, Cairo Academy decisions): https://shamela.ws/book/7517/288 ; https://shamela.ws/book/7517/683 ; https://shamela.ws/book/7517/85
- الألوكة, أجب عن أم أجب على؟: https://www.alukah.net/literature_language/0/80893/
- موسوعة اللغة العربية, الدرر السنية: https://dorar.net/arabia/2751
- Study on the fate of "common errors" across decades (CRSTDLA): https://crstdla.dz/ojs/index.php/allj/article/view/591
- University of Baghdad, التصويبات اللغوية للأخطاء الشائعة في كتابة الرسائل والأطاريح: https://events.uobaghdad.edu.iq/event/25215/attachments/16797/33402/
- Algerian Ministry of Education, Erreurs les plus fréquentes (Arabic): https://www.education.gov.dz/old//wp-content/uploads/2015/03/Erreurs-les-plus-frequentes-L.A.pdf

Standard references (drawn from prior knowledge, not fetched in this session)
- عباس حسن، النحو الوافي.
- ابن عقيل، شرح ابن عقيل على ألفية ابن مالك.
- مصطفى الغلاييني، جامع الدروس العربية.
- أحمد مختار عمر وآخرون، معجم الصواب اللغوي (2008) — main source for "contested/accepted" verdicts on modern usages.
- محمد العدناني، معجم الأخطاء الشائعة؛ مصطفى جواد، قل ولا تقل.
- قرارات مجمع اللغة العربية بالقاهرة (مجموعة القرارات العلمية) — on التضمين, نيابة حروف الجر, اعتبر, ساهم, تواجد.
- Karin C. Ryding, *A Reference Grammar of Modern Standard Arabic* (Cambridge, 2005).
- E. Badawi, M. G. Carter, A. Gully, *Modern Written Arabic: A Comprehensive Grammar* (Routledge, 2004/2016).
- W. Wright, *A Grammar of the Arabic Language*.
