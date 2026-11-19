# 02 — MSA Orthography (الإملاء), Punctuation (علامات الترقيم) and Digital Typography

Reference for a checker that reviews Arabic text Claude writes. Each rule has: **Rule**, **✓ / ✗** examples, and **Check**:

- **M-regex**: can be checked with a regex, with few false positives
- **M-list**: can be checked with a word list (whitelist or blacklist)
- **J**: needs morphology, context or meaning, so the model must judge (a regex can only raise a candidate)

**Baseline used:** the rules taught in most Arab school curricula. They follow مجمع اللغة العربية بدمشق (*قواعد الإملاء*, published by the Damascus Academy) and the decisions of مجمع اللغة العربية بالقاهرة, which mostly agree. Where a rule changes by region or publisher, it is marked **[VARIES]**.

---

## 1. Hamza (الهمزة)

### 1.1 همزة الوصل vs همزة القطع (start of a word)

**Quick test:** put و or ف before the word. If you still hear the hamza (وَأَكَلَ, وَإِنَّ), it is **قطع**, written أ or إ. If it disappears (وَاكتُبْ, وَاسْمُهُ), it is **وصل**, written as a bare ا.

**Rule (wasl, bare ا):** hamzat al-wasl appears only in these places:

| Category | Members | ✓ | ✗ |
|---|---|---|---|
| The ten nouns (singular and dual only) | ابن، ابنة، ابنم، اسم، است، اثنان، اثنتان، امرؤ، امرأة، اِيمُن (اللهِ) | ابن، اسم، اثنان، اثنتين، امرأة، امرؤ القيس | إبن، إسم، إثنان، إثنين، إمرأة |
| Their plurals take **qat'** | أبناء، أسماء (and the different-root نساء) | أبناء، أسماء | ابناء، اسماء |
| The article | الـ | الكتاب | ألكتاب |
| Form I imperative (non-hamzated root) | اُكتبْ، اِجلسْ، اِفتحْ، اُدرسْ | اكتب، اذهب | إكتب، أذهب (when an imperative is meant) |
| Past, imperative and masdar of 5-letter verbs: VII انفعل، VIII افتعل، IX افعلّ | انطلق/انطلقْ/انطلاق؛ اجتمع/اجتمعْ/اجتماع؛ احمرّ/احمرار | انتظار، اجتماع، اقتصاد، انتخابات، اختيار، اتصال، احترام، اهتمام | إنتظار، إجتماع، إقتصاد، إنتخابات، إختيار، إتصال، إحترام، إهتمام |
| Past, imperative and masdar of 6-letter verbs: X استفعل (plus the rare افعوعل، افعالّ، افعوّل) | استخدم/استخدمْ/استخدام؛ استطاع؛ استثمار | استخدام، استراحة، استثناء، استقلال، استعمال | إستخدام، إستراحة، إستثناء، إستقلال |

**Rule (qat', أ/إ):** everything else, especially:

| Category | ✓ | ✗ |
|---|---|---|
| Particles (all except الـ) | إنّ، أنّ، إن، أن، أو، أم، إلى، إلا، إذا، إذ، إذن، أي، أيّ، أمّا، إمّا، ألا | ان، الى، الا، اذا، او، اي، اما |
| Pronouns | أنا، أنت، أنتم، أنتما، أنتنّ، إيّاك | انا، انت، انتم |
| Form IV أفعل (past, imperative, masdar) | أكرمَ/أكرِمْ/إكرام؛ أعلن/إعلان؛ أنشأ/إنشاء؛ أبدع/إبداع؛ أسلم/إسلام؛ أصدر/إصدار؛ أضاف/إضافة | اعلان، انشاء، ابداع، اسلام، اصدار، اضافة، ارسال، اجراء |
| Form I verbs and masdars from hamzated roots | أخذ/أخْذ، أكل/أكْل، أمر/أمْر، أمل، أذن | اخذ، اكل |
| Present-tense prefix أ (أنا) | أكتبُ، أستخدمُ، أنتظرُ | استخدم (meaning "I use"), انتظر |
| Comparative/elative أفعل | أكبر، أفضل، أكثر، أول | اكبر، افضل، اكثر، اول |
| Plurals أفعال، أفعلة، أفعُل | أبناء، أسماء، أعمال، أسئلة، أنهُر | اعمال، اسئلة |
| Other nouns | أب، أم، أخ، أخت، أرض، إنسان، أمس، أهل، إمام، أستاذ | ارض، انسان، امس، اهل |
| أن (conjunction, opens a clause after a verb) vs إن (start of a sentence, after قال, after a vocative or oath) | قال إنّه...؛ أعلم أنّه...؛ إنّ الله غفور | قال أنّه... (common error) |

- **إن vs أن is J** (it depends on syntax). That a hamza is present at all is M-list.
- **Check:** for wasl/qat' at the start of a word, use **M-list**. Keep a blacklist of ✗ forms: `\bإ(ست|نت|جت|قت|خت|تص|حت|هت|سم\b|بن\b|ثن|مرأ)` catches most errors with إ wrongly added to forms VII/VIII/X and to the ten nouns. A bare ا where a hamza is needed (`\bا(لى|ذا|ن\b|و\b|نا\b)`) is easy with a list of about 30 particles and pronouns. Form IV masdars (إفعال) that lose the hamza need a lexicon (M-list of frequent masdars). Telling a Form I imperative (اكتب) from a first-person present (أكتب) is J.
- **[VARIES]** Egyptian newspapers, Egyptian web content and informal writing everywhere often leave the hamza off إ/أ entirely (الى، ان، اذا). Formal MSA requires it. Claude should always write the hamza.

### 1.2 Wasl hamza dropped in writing

| Rule | ✓ | ✗ |
|---|---|---|
| الـ after the preposition لـ loses its alif | للطالب، لله، للّغة | لالطالب |
| Interrogative أ + wasl verb: the wasl alif drops | أستغفرت لهم؟ (أَ + اِستغفرت) | أاستغفرت |
| Interrogative أ + الـ becomes آ | آلله أذن لكم؟ | أالله |
| اسم loses its alif **only** in the full basmala بسم الله الرحمن الرحيم | بسم الله الرحمن الرحيم؛ باسم الشعب؛ باسم الله نبدأ | بسم الشعب |
| ابن/ابنة drops its alif between two proper names (§3.3) | محمد بن عبد الله | محمد ابن عبد الله (when used as a descriptor) |

Check: the basmala and للـ cases are M-regex. The other rows are J.

### 1.3 Madda (آ)

**Rule:** a fatha hamza followed by a long ā (أا), or a hamza with sukun after a fatha hamza (أأ), is written آ.

✓ آمن، آخر، القرآن، مآل، مرآة، آلة، آن، الآن، ظمآن
✗ أامن، أخر (when آخَر "other" is meant; أُخَر is a different word), قرأن، مرأة (for "mirror"), ألآن، الان

Check: **M-list** (القرآن، الآن، آخر/آخرون، آلة، مرآة). The أخر/آخر pair is J.

### 1.4 Middle hamza (الهمزة المتوسطة)

**Rule:** compare the hamza's own vowel with the vowel of the letter before it. The stronger of the two picks the seat.
**Order of strength:** kasra (ئ) > damma (ؤ) > fatha (أ) > sukun (ء on the line).

| Hamza vowel / previous vowel | Seat | ✓ | ✗ |
|---|---|---|---|
| any / kasra, or kasra / any | ئ | سُئِلَ، رئيس، بِئْر، فِئة، مسائل، أسئلة، مئات، ذئب، يئس | سؤل، رأيس، بإر، أسألة |
| damma / damma, fatha, sukun | ؤ | سُؤال، مُؤمن، رُؤوس، تفاؤل، تشاؤم، تساؤل، يؤدي، مؤسسة | سئال، تفائل، تشائم، تسائل (as a noun) |
| fatha / fatha or sukun | أ | سأل، رأس، يأس، مسألة، جرأة، نشأة، هيأة*، يتأخر، مأساة | مسئلة، جرئة، نشئة |
| sukun / sukun (rare) | — | — | — |

**Exceptions (on the line, ء):**
- A fatha hamza after a long ā: تساءل، قراءة، براءة، عباءة، يتساءل، إجراءات، بناءَه
  - ✗ قرائة، برائة، يتسائل، اجرائات
- A fatha hamza after a long ū, or after و with sukun: مروءة، سموءل، ضوءَه
- A damma hamza after a long ā (some sources): تفاؤل keeps ؤ in the dominant school. **[VARIES]** for forms like يتساءلون and يقرءُون.

**Exceptions (on ي, ئ):**
- A fatha hamza after ي with sukun: هيئة، بيئة، شيئان، خطيئة، بريئة
- *هيئة/هيأة: **[VARIES]**. The strict rule gives هيأة (after ي with sukun, the fatha wins). The Cairo Academy leaned toward هيأة in 1960 but printed هيئة in المعجم الوسيط. **Use هيئة**, which is near-universal.

**[VARIES] damma hamza after a sukun or a long vowel:** for مسؤول، شؤون، يقرؤون، رؤوس:
- Damascus, the Levant and the Gulf write ؤ: مسؤول، شؤون، يقرؤون.
- Egyptian print tradition writes ئ or ء: مسئول، شئون، يقرءون.
- Both are accepted. **Default: ؤ forms.** Do not mix the two in one text.

**[VARIES] مئة/مائة:**
- مائة keeps a historical alif that is not pronounced. Egypt and the Gulf use it, as do classical texts.
- مئة is recommended by the Damascus Academy and many modern guides.
- Both are correct. Be consistent within one text (also ثلاثمئة/ثلاثمائة).

**Check:** the seat depends on vowels, which unvocalized text does not show, so the rule is **J**. In practice use an **M-list** of high-frequency words (سؤال، رئيس، مسؤول، قراءة، تساؤل، تفاؤل، هيئة، بيئة، مسألة، جرأة، نشأة، أسئلة، مسائل، يقرأ، يقرؤون...) plus blacklist patterns:
- `ائة\b` (except مائة)
- `ائات`
- `\bتفائل|\bتشائم|\bيتسائل|\bقرائة|\bبرائة|\bجرئة|\bنشئة|\bمسئلة`

### 1.5 Final hamza (الهمزة المتطرفة)

**Rule:** look only at the vowel of the letter before the hamza. The hamza's own vowel does not matter.

| Previous letter | Seat | ✓ | ✗ |
|---|---|---|---|
| fatha | أ | بدأ، قرأ، ملجأ، مبدأ، يقرأ، خطأ، نبأ، منشأ | بدء (for the verb "began"), خطئ، يقرء |
| damma | ؤ | تباطؤ، تكافؤ، لؤلؤ، تواطؤ، يجرؤ | تباطئ، تكافئ، تكافء |
| kasra | ئ | شاطئ، قارئ، مبادئ، ناشئ، يبتدئ، طوارئ، لاجئ، مُهيِّئ | شاطيء، قاريء، مباديء، لاجيء |
| sukun or long vowel (ا و ي) | ء on the line | سماء، شيء، جزء، ضوء، بطء، دفء، مجيء، بريء، بطيء، هدوء، وضوء | شئ، شيئ، بريئ، بطيئ، جزئ، ضوئ |

**Check:**
- **M-regex** for the very common errors:
  - `شئ\b|شيئ\b`
  - `يء\b` written as `يئ\b` (except after shadda: مهيِّئ، يهيِّئ)
  - `[^ ]ي[ءئ]` combined with a whitelist
  - `اطيء|اريء|اديء|ابيء`: the old ـيء spelling for ـئ after kasra, as in شاطيء
- Otherwise **M-list** plus J.
- **[VARIES]** Older Egyptian print writes final ئ as ىء (شاطىء، مبادىء). This is obsolete. Flag it.

### 1.6 Hamza when suffixes are added

- When a pronoun suffix is added, the hamza becomes a middle hamza and follows §1.4:
  - جزء + ه gives جزؤه (nominative), جزأه (accusative), جزئه (genitive).
  - Most writers use one fixed form and do not follow the case. This is **J** and low priority.
- With a prefix, the initial hamza keeps its alif seat: بأن، لأن، فإن، كأن، سأذهب، بإمكان، لإنجاز.
  - Exceptions: لئلا، لئن، هؤلاء، يومئذ، حينئذ.
  - ✗ لان، بان (as بأن), لإن.
  - Check: **M-regex** `\b[بلفك]ان\b` (as a candidate; بان and لان are also real words, so J for the final call).

---

## 2. Final letters: ة/ه, ى/ي, ا/ى

### 2.1 Taa marbuta ة vs haa ه

**Rule:**
- ة is the feminine/nominal ending. It is pronounced *h* at a pause and *t* in construct or when a suffix is added: مدرسة/مدرستي.
- ه is a root letter (وجه، فقيه، انتباه، مياه، شفاه، اتجاه، أشباه) or the pronoun "his/him" (كتابه، رأيته).
- Plural ـات uses open ت (معلمات), as does the verb ending (كانت).
- **Test:** add ـي or put it in construct. If you hear ت, write ة.

✓ مدرسة، حياة، صلاة، فتاة، قضاة، دعاة، الجامعة، طاقة، فاطمة، حمزة
✗ مدرسه، حياه، الجامعه، فاطمه، قضاه
✓ مياه، اتجاه، انتباه، شفاه، أفواه، الله، وجه
✗ مياة، اتجاة، انتباة، وجة

Watch for word pairs where both spellings are real words:
- كتابة (writing) / كتابه (his book)
- دراسة / دراسه (as in دَرَسَه)
- حلة / حله

**Check:**
- **M-list** for nouns that are always feminine (blacklist of frequent ـه spellings: الجامعه، المدرسه، الحكومه، الدوله، الشركه، اللغه).
- **M-regex** `اة\b` against a whitelist (حياة، صلاة، زكاة، فتاة، قناة، نجاة، مباراة، مساواة، قضاة، رعاة، دعاة، ولاة، غزاة، مأساة، توراة، مرآة) and `اه\b` against a whitelist (اتجاه، انتباه، مياه، شفاه، أفواه، إكراه، اشتباه، جاه، إله، الله).
- **J** for minimal pairs.
- A pronoun suffix on ة changes it to ت (رسالته). ✗ رسالةه.

**Tanween on ة takes no alif.**
- ✓ عادةً، خاصةً، مرةً، نتيجةً، فجأةً
- ✗ عادتاً، خاصتاً، مرتاً، نتيجتاً (a very common error)
- Check: **M-regex** `تاً\b|تًا\b` against a small whitelist of words that really end in ت (وقتاً، بيتاً، صوتاً، موتاً، ثابتاً، سكوتاً، أخواتٍ...). Better: flag عادتا|خاصتا|مرتا|نتيجتا|فجأتا|جملتا|تارتا directly.

### 2.2 Alif maqsura ى vs ي

**Rule:**
- ى is an alif sound at the end of a word, with no dots: على، إلى، مستشفى، مصطفى، رمى، هدى، فتى، أعطى، حتى، متى، لدى، بلى، موسى، عيسى، كبرى، أخرى، ذكرى، فوضى.
- ي is a ya sound, with dots: في، الذي، التي، علي (name)، إليّ، لديّ، القاضي، يمشي، كرسي.

✓ في البيت، الذي قال، ذهب إلى المستشفى
✗ فى البيت، الذى قال، ذهب الي المستشفي

Minimal pairs (J):
- على (on) / علي (the name Ali, or عليّ "on me")
- إلى (to) / إليّ (to me)
- لدى (at, with) / لديّ (I have)
- مبنى (building) / مبني (built)
- معنى / معني
- مستوى / مستوي
- أعمى / أعمي

**[VARIES] Egypt:** Egyptian print and web very often write final ي without dots (فى، الذى، على for علي). This is accepted in Egyptian publishing tradition but is ambiguous and not standard pan-Arab MSA. **Default: always dot final ي.**

**Check:**
- **M-list/M-regex**: flag `\b(فى|الذى|التى|اللذى|الى|حتي|متي|علي(?= ال))\b`.
  - `علي ال...` is almost always an error for على.
  - `الي` + word is almost always an error for إلى.
- High-confidence list of nouns ending in ـى: مستشفى، مستوى، معنى، مبنى (as a noun), مصطفى، موسيقى، كبرى، أخرى، ذكرى، فوضى، دعوى، فتوى، شكوى، حلوى، قرى، ...
- Plus a per-word whitelist of ـي nouns (نادي، وادي، كرسي، ماضي)
- Plus **J** for minimal pairs.
- **Unicode:** Farsi yeh U+06CC shows up as ى in final position but has dots elsewhere. See §7.4.

### 2.3 Final ا vs ى (الألف اللينة)

**Rule:**

**(a) Three-letter words** (verbs and nouns): check the origin of the final letter. Find it from the present tense, the dual, or the masdar.
- From و: write ا. دعا (يدعو)، سما، علا، نجا، شكا، عفا، غزا، رجا، بدا، صفا، عصا (عصوان)، ربا، سنا، خلا
- From ي: write ى. رمى (يرمي)، سعى، قضى، مشى، بنى، جرى، هدى، بكى، فتى (فتيان)، هوى، نوى، روى، حمى

✗ دعى، سمى (as the verb "rose"), نجى، شكى، رما، سعا، قضا، مشا، بنا

**(b) Words of four or more letters:** always write ى, whatever the origin.
- ✓ أعطى، استدعى، انتهى، اشترى، تلقّى، مستشفى، مصطفى، ملتقى، منتدى، اهتدى، تمنّى
- ✗ أعطا، استدعا، انتها، اشترا

**Exception:** if the letter before is ي, write ا to avoid يى.
- ✓ أحيا، استحيا، دنيا، عليا، ثريّا، هدايا، زوايا، قضايا، يحيا (verb). The proper name يحيى is a fixed exception.

**(c) Non-Arabic words and foreign names:** write ا.
- ✓ أمريكا، فرنسا، إيطاليا، بريطانيا، أوروبا، صوفيا، دراما، سينما، بيتزا
- Traditional exceptions keep ى: موسى، عيسى، كسرى، بخارى، متّى
- موسيقى/موسيقا is **[VARIES]**. Academies allow موسيقا, but موسيقى is near-universal. **Use موسيقى.**

**(d) Built-in nouns and particles** (مبنيات) are fixed:
- With ا: إذا، لولا، لوما، ما، لا، كلا، أنا، هذا، مهما، كيفما
- With ى: إلى، على، حتى، بلى، متى، لدى، أنّى، الألى

**(e)** When ى or final ا takes a suffix or the dual:
- ى becomes ا before a pronoun: مستشفاه، إلامَ، على + ه gives عليه، إلى + ه gives إليه, لدى + ك gives لديك.
- ✗ مستشفىه، علىه.

**Check:**
- **M-list** for frequent verbs: build the list from the root/morphology database (دعا/رمى, etc.). Flag ✗ forms such as دعى، نجى، شكى، أعطا، اشترا، انتها.
- The "4+ letters with final ا preceded by a non-ي" heuristic can only flag candidates (J), because foreign words end in ا.

---

## 3. Letters written but not pronounced, and pronounced but not written

### 3.1 Added letters (زيادة)

| Rule | ✓ | ✗ | Check |
|---|---|---|---|
| **الألف الفارقة**: an alif goes after the و of the plural verb (past, imperative, jussive or subjunctive present) | ذهبوا، اكتبوا، لم يكتبوا، لن يذهبوا، كانوا | ذهبو، اكتبو، لم يكتبو | J-assisted: `\b\w+و\b` where the stem is a known verb. M-list for frequent verbs (كانوا، قالوا، ذهبوا، أصبحوا) |
| **No** alif after a root و in a singular verb | يدعو، يرجو، يسمو، ندعو، أرجو، يبدو، يعلو | يدعوا (as a singular), يرجوا، يبدوا | M-list: `\b(ي|ت|ن|أ)(دعو|رجو|بدو|علو|سمو|نمو|شكو|عفو|غزو|تلو|محو)ا\b` is wrong when the subject is singular. يدعوا is valid only as a plural subjunctive (لن يدعوا = لن يدعُوا), so **J** |
| **No** alif after the plural و of a sound masculine noun in construct | معلمو المدرسة، مهندسو الشركة، ذوو الخبرة، أولو العزم | معلموا المدرسة، مهندسوا، ذووا | M-regex candidate: `\b\w+وا (ال)`, then J. Also blacklist ذووا |
| و in عمرو (in nominative and genitive), to tell it apart from عُمَر. It drops in the accusative with tanween: عمرًا | عمرو بن العاص | — | J (names) |
| و in أولئك، أولو، أولي، أولات (pronounced ū as a short u) | أولئك، أولو الألباب | ألئك، اولئك | M-list |
| Historical ا in مائة | §1.4 [VARIES] | | |

### 3.2 Dropped letters (حذف)

| Rule | ✓ | ✗ | Check |
|---|---|---|---|
| The alif of ذا after ها in demonstratives | هذا، هذه، هذان، هذين، هؤلاء، هكذا، ذلك، ذلكم، أولئك | هاذا، هاذه، هاكذا، ذالك، هاؤلاء | **M-regex** `\bها(ذا|ذه|ذان|ذين|ؤلاء|كذا)\b|\bذالك\b` |
| The alif in لكن and لكنّ | لكن، لكنّ، ولكن | لاكن، ولاكن | **M-regex** `\b(و)?لاكن` |
| The alif in الله، إله، الرحمن، اللهم، السموات (Qur'anic) | الله، إله، الرحمن، اللهم | اللاه، إلاه، الرحمان | **M-list**. السماوات is normal in MSA; السموات is Qur'anic/old spelling, so **[VARIES]**, use السماوات |
| The alif in طه، يس، داود، طاوس | داود | داوود | **[VARIES]**: داوود is common in modern use, داود is classical. Low priority |
| Interrogative ما after a preposition loses its alif | لِمَ، عَمَّ، فيمَ، بِمَ، حتّامَ، إلامَ، علامَ | لما (as "why"), عما (as "about what?") | J. But لماذا keeps its alif (✓ لماذا) |
| The alif of ال after لـ | للطالب | لالطالب | M-regex |
| The alif of ابن (see below) | | | |

### 3.3 ابن / ابنة between two names

**Rule:** the alif of ابن (and of ابنة, written بنت/ابنة) drops when **all** of these hold:
1. It comes directly between two proper names (including kunyas and laqabs).
2. The second name is the **father** of the first (or a grandfather or the family eponym).
3. ابن is singular and used as a descriptor (نعت), not as the predicate of a sentence.
4. It is not at the start of a line.

✓ محمد بن عبد الله؛ عمر بن الخطاب؛ أبو بكر بن أبي قحافة؛ علي بن أبي طالب
✓ (kept) ابن خلدون (at the start, no first name before it); الحسين ابن فاطمة (mother; **[VARIES]**, many drop it anyway); محمدٌ ابنُ عبد الله (a full sentence, "Muhammad is the son of..."); جاء ابنُ عمّي; ابنا علي (dual); هذا ابن خالد (not between two names)
✗ محمد ابن عبد الله (in a nasab chain), قال إبن خلدون

**Check:** **J** (it needs named-entity recognition). M-regex can flag the candidate `\b[NAME] ابن [NAME]` and always flag `إبن`.

---

## 4. Words joined and split (الفصل والوصل)

| Rule | ✓ joined | ✓ split (different meaning) | ✗ | Check |
|---|---|---|---|---|
| مِن/عن + ما/مَن: the نون is assimilated, so write them joined with shadda | مِمّا، مِمّن، عمّا، عمّن | — | من ما، عن ما، من من | **M-regex** `\b(من|عن) (ما|من)\b` (except "من من؟" asking "from whom?". Even then مِمَّن is standard) |
| في/بـ/لـ/كـ + ما | فيما، بما، لما، كما | في ما (allowed, but joined is preferred) | — | Low priority |
| كلّما (a temporal conditional, "whenever") vs كلّ ما ("everything that", ما is a relative pronoun) | كلّما زرته أكرمني | كلُّ ما قاله صحيح | كل ما زرته... (for "whenever") | **J** |
| Joined-ما adverbs and particles: ربّما، إنّما، أينما، حيثما، بينما، ريثما، طالما، قلّما، كيفما، مثلما، عندما، حينما (but see لا سيّما below) | ربما، إنما، عندما، بينما، طالما، مثلما | — | رب ما، إن ما (for إنما)، عند ما (for "when"), بين ما (for "while") | **M-regex** for `\b(رب|عند|بين|طال|قل|حين|ريث|مثل) ما\b`. عند ما and مثل ما can be valid with a relative ما (عند ما يملك), so these are candidates |
| لا سيّما is **two words** | لا سيّما، ولا سيّما | — | لاسيما | **M-regex** `لاسيما` |
| أن (subjunctive) + لا gives ألّا | يجب ألّا تتأخر | أن لا (the أن that is a lightened أنّ, before a nominal sentence: أشهد أن لا إله إلا الله) | — | **[VARIES]** "أن لا" for a subjunctive is widely written and many accept it. Prefer ألّا. J |
| إن (conditional) + لا gives إلّا | إلّا تفعلوه تكن فتنة | — | — | J. Rare; do not confuse with exceptive إلّا |
| لـ + أن + لا gives لئلّا; كي + لا gives كيلا/لكيلا | لئلا، لكيلا | لكي لا (accepted) | لأن لا | M-list |
| إذ joined to time nouns | يومئذٍ، حينئذٍ، وقتئذٍ، ساعتئذٍ | — | يوم إذ، حين إذ | **M-regex** |
| Hundreds | ثلاثمئة، خمسمئة، تسعمئة (joined) | ثلاث مئة (accepted by some modern guides, **[VARIES]**) | ثلاثمائه | consistency only |
| Compound numbers 11–19 are split | أحد عشر، خمسة عشر | — | خمسةعشر | M-regex |
| ألا (opening particle) vs ألّا (أن + لا) | ألا إنّ... / ألّا تذهب | — | — | J |
| مهما، كيفما، أينما (always joined) | مهما | — | مه ما | M-regex |
| Proper compound names stay split; ابو + name | عبد الله، عبد الرحمن، أبو ظبي/أبوظبي **[VARIES]** | — | عبدالله **[VARIES: common in the Gulf and in official IDs; formal MSA splits it]** | Low priority. Do not "fix" a user's own name |
| Vocative يا is its own word | يا محمد، يا أيها | — | يامحمد | **M-regex** `\bيا(?=[^ءأإآ ]{3,})` as a candidate (words like ياسمين، يابان、يافا exist, so use a whitelist) |

---

## 5. Tanween (التنوين)

### 5.1 Tanween fath + alif

**Rule:** an indefinite accusative takes ًا (an added alif), **except** after ة, ى, and ء that follows ا.

| Ending | ✓ | ✗ |
|---|---|---|
| ordinary | كتابًا، شكرًا، أيضًا، جدًّا، دائمًا | كتابً، شكرً |
| ة | مدرسةً، عادةً، فجأةً | مدرسةً ا، عادتاً |
| ى | هدًى، فتًى، مستشفًى، معنًى | هدىً ا، فتىا |
| ء after ا | سماءً، ماءً، بناءً، إجراءً، مساءً | سماءًا، ماءاً، بناءاً |
| ء after a non-connecting letter or و (alif added, hamza stays on the line) | جزءًا، ضوءًا، بدءًا، سوءًا، هدوءًا | جزئاً، ضوئاً |
| ء after a connecting letter (hamza moves onto ئ, alif added) | شيئًا، عبئًا، بطئًا، دفئًا | شيءًا، شيأً، شيئاً?\* |
| أ (final, after fatha) | ملجأً، خطأً، مبدأً، نبأً | خطأًا، خطئاً |

\* شيئًا and شيئاً are the same spelling with the tanween mark in a different position (§5.2). شيءًا and شيأً are wrong.

**Check:** **M-regex**:
- `اءا\b` and `اءً?ا\b` (for example سماءا or بناءاً): flag.
- `ةا\b`, `ةً?ا\b`, `تا[ًً]?\b` after known ة-nouns: flag.
- `ىً?ا\b`: flag.
- `ءًا` after a connecting letter (شيءًا): flag, should be شيئًا.
- Words that need ًا but are written without the alif (`[^ةىءأا ]ً\b`): flag. They show up as stray tanween without alif, as in كتابً.

### 5.2 Where the tanween mark goes: ًا vs اً

- **[VARIES]** Both are in wide use.
  - Classical and Qur'anic orthography, the Cairo/Damascus academy line and many modern style guides put the fathatan on the letter **before** the alif: كتابًا. This is the logical position, because the alif is only a seat.
  - Levantine, Gulf and much web text put it on the alif: كتاباً. Many keyboards encourage this.
- **Unicode:** ًا is U+064B before U+0627. اً is U+0627 followed by U+064B.
- **Recommendation:** pick one style per text, default ًا. Never mix both in one text. This is **M-regex** (count both patterns and flag the minority).
- When text is otherwise unvocalized, tanween fath is commonly written only on adverbs and frequent words (أيضًا، جدًا، شكرًا، دائمًا، تقريبًا). That is normal and fine.

---

## 6. Punctuation (علامات الترقيم)

Arabic punctuation was standardized by أحمد زكي باشا in *الترقيم وعلاماته في اللغة العربية* (1912), written at the Egyptian Ministry of Education's request. Later guides extend his system.

### 6.1 Characters to use

| Mark | Arabic name | Code point | Note |
|---|---|---|---|
| ، | الفاصلة / الفصلة | U+060C | **Not** `,` (U+002C) in Arabic running text |
| ؛ | الفاصلة المنقوطة | U+061B | **Not** `;` |
| ؟ | علامة الاستفهام | U+061F | **Not** `?` |
| . | النقطة | U+002E | Arabic uses the ordinary period. **Not** ۔ U+06D4 (Urdu) |
| ! | علامة التعجب | U+0021 | No Arabic variant |
| : | النقطتان | U+003A | |
| « » | علامتا التنصيص | U+00AB / U+00BB | Preferred. "..." (U+0022 or U+201C/U+201D) is also common, **[VARIES]** |
| ( ) | القوسان | U+0028 / U+0029 | Typed in logical order. The bidi algorithm mirrors their glyphs |
| [ ] | المعقوفان | U+005B / U+005D | For editorial insertions |
| ﴿ ﴾ | القوسان المزهّران | U+FD3E / U+FD3F | **Only** around Qur'anic text |
| – / — | الشرطة | U+2013 / U+2014, or `-` | |
| ... / … | علامة الحذف | `...` or U+2026 | |
| ٪ ٫ ٬ | percent / decimal / thousands | U+066A / U+066B / U+066C | Only with Arabic-Indic digits (§7.1) |

- **[VARIES]** The Maghreb (Morocco, Algeria, Tunisia) uses Latin-shaped `,` `;` `?` more often, especially in French-influenced typesetting. Mashriq norms use ، ؛ ؟. **Default: ، ؛ ؟.**
- Check: **M-regex**. In a sentence with Arabic letters, flag `[؀-ۿ]\s*,` and `,\s*[؀-ۿ]` (likewise `;` and `?`). Do not flag inside code spans or URLs, or between Latin and Western-digit tokens (`1,000`).

### 6.2 Spacing

**Rule:**
- No space **before** ، ؛ ؟ ! . : and closing brackets or quotes.
- One space **after** each of them.
- No space just inside brackets or quotes.
- One space before an opening bracket or quote.

✓ `قال: «سأحضر غدًا»، ثم غادر (مسرعًا).`
✗ `قال :« سأحضر غدًا » ، ثم غادر ( مسرعًا ) .`

Check: **M-regex**:
- `\s+[،؛؟!.:)»\]]` (space before)
- `[،؛؟!:](?=[^\s\d»)])` (no space after, except before a closing quote or a digit in times like ١٠:٣٠)
- `[(«\[]\s+` and `\s+[)»\]]`
- doubled marks `،،` or `؟؟` (except `؟!`)

`؟!` and `!!` are used for surprised questions. They are acceptable but informal. Avoid them in formal writing.

### 6.3 When to use each mark

**الفاصلة ، (comma)**
- Between short coordinated sentences that make up one idea: جاء الصيف، واشتد الحر.
- After a vocative: يا علي، تعال.
- After نعم/لا as an answer: لا، لم أحضر.
- Between items in a list. Arabic usually repeats و: زرت مصر، والأردن، ولبنان. Writing "مصر والأردن ولبنان" with no commas is also fine.
- Between a condition and its answer when the condition is long.
- Around a parenthetical, before or after a حال clause, between oath and answer.
- **Not** between a verb and its subject, between a subject and its predicate, or between a muḍāf and its muḍāf ilayh.

**الفاصلة المنقوطة ؛ (semicolon)**
- Between two sentences when the second is the cause of the first: لم يحضر؛ لأنه كان مريضًا.
- Or the result of the first: اجتهد؛ فنجح.
- Between long sentences that already contain commas.
- **[VARIES]** In practice, many writers put ، before لأنّ. The ؛ before لأنّ/إذ is the textbook rule.

**النقطة . (period)**
- At the end of a complete sentence or paragraph, and after abbreviations (د. محمد).

**النقطتان : (colon)**
- After قال/يقول and speech verbs, before quoted speech.
- Before a list or detail, between a term and its definition, before examples (مثل:).

**علامة الاستفهام ؟**
- After a **direct** question, including rhetorical ones: هل حضرت؟ / كيف حالك؟
- Not after an indirect question: سألته هل حضر.
- J for the indirect case. M-regex can flag a sentence that starts with هل/ماذا/لماذا/كيف/متى/أين/من/كم/أيّ and ends in `.`, as a candidate.

**علامة التعجب !**
- After exclamation, emotion, a call for help, and the formulas ما أجمل...! / يا لـ...!

**التنصيص « »**
- Around direct quoted speech and titles, and around a term used as a word (mention).

**الأقواس ( )**
- Around explanations, foreign equivalents, abbreviation expansions and dates.

**الشرطة –**
- Around a parenthetical (جملة اعتراضية), at the start of each speaker's line in a dialogue, between a number and its item at the start of a line, and for ranges.

**Overuse:** Arabic prose naturally links clauses with و/ف/ثم. Do not split every clause with ، as in an English-style serial comma, and do not end every line with `.` in a list. **J**.

### 6.4 Brackets and bidi in right-to-left text

- In Unicode, `(` U+0028 means "opening" in logical order, and the renderer mirrors it in RTL. **Never type `)` first to make it look right.** That produces backwards brackets in correct RTL renderers. Applies to `()[]{}<>«»`.
  - Check: **M-regex** for unbalanced or reversed pairs (a closing bracket before its opener in logical order).
- A **period or punctuation mark after Latin text or digits at the end of an RTL line** can display on the wrong side in plain-text or Markdown renderers that lack a paragraph direction. Fixes:
  1. End the sentence with an Arabic word.
  2. Insert U+200F RLM after the Latin run.
  3. Put the Latin text in parentheses or code spans.
  Claude's output is usually rendered with auto direction per paragraph. A paragraph that **starts** with a Latin word or a digit may be laid out LTR, so start Arabic paragraphs with an Arabic word. **J** (M-regex can flag paragraphs whose first strong character is Latin while most of the text is Arabic).
- «» do not mirror. « always opens on the right in RTL. Check that the logical order is `«...»`.

---

## 7. Typography in digital text

### 7.1 Digits

| Set | Code points | Where it is used |
|---|---|---|
| Western ("Arabic" digits) 0123456789 | U+0030–0039 | The Maghreb (Morocco, Algeria, Tunisia, Libya, Mauritania), plus some pan-Arab digital media, tech, finance and much Gulf web content |
| Arabic-Indic ٠١٢٣٤٥٦٧٨٩ | U+0660–0669 | The Mashriq in print and government use: Egypt, Saudi Arabia, Iraq, Syria, Jordan, the Gulf, Sudan |
| Extended Arabic-Indic ۰۱۲۳۴۵۶۷۸۹ | U+06F0–06F9 | **Persian and Urdu only.** ۴ ۵ ۶ have different shapes. **Never use them in Arabic** |

**Rules:**
1. **Never mix sets in one text.** Never use U+06F0–06F9 at all. This is **M-regex**.
2. Digits are always written with the most significant digit first (left to right) even inside RTL text: ٢٠٢٦, not ٦٢٠٢. Unicode handles this automatically. Do not reverse digits.
3. **Default for Claude:** match the user's own text. If there is no signal, Western digits are a safe, widely read default in digital/tech contexts. Arabic-Indic suits formal Mashriq prose. **[VARIES]**
4. **Always Western digits:** code, version numbers, URLs, IPs, file paths, phone numbers in technical contexts, math or formulas mixed with Latin variables, units next to Latin symbols (5 GB, 3 km/h), and anything the user must copy-paste.
5. Separators:
   - With Western digits use `.` for decimals and `,` for thousands (in most of the Arab East).
   - With Arabic-Indic digits use ٫ U+066B (decimal) and ٬ U+066C (thousands): ٣٫١٤، ١٬٠٠٠.
   - Do not put the Arabic comma ، inside numbers.
   - Use ٪ U+066A or % consistently.
6. Ordinals in running text are usually written as words (الفصل الثالث). Dates in Hijri use هـ (§7.3), Gregorian uses م: ١٤٤٨هـ / ٢٠٢٦م.

### 7.2 Mixing Arabic with Latin text and code

- On first mention, give a technical term in Arabic and then in Latin in parentheses: التعلّم الآلي (Machine Learning). After that, use one form consistently.
- Keep code, identifiers, commands, file names and API names in Latin, inside backticks or code blocks. Never translate, transliterate or put Arabic punctuation inside code. Comments inside code may be Arabic if the user writes that way.
- Put Arabic punctuation **outside** code spans: `استخدم الأمر `git status`، ثم ...`
- Do not join Arabic prefixes to Latin words without a separator, as in بـGit. Use بـ + space, or a tatweel-free rewrite: باستخدام Git. **[VARIES]**: the bـ + Latin form (بـ Git) is a common tech-writing convention. It is the one legitimate tatweel use besides abbreviations.
- Brand and product names are usually left in Latin script, or written in their established Arabic form (جوجل/غوغل is **[VARIES]**: Egypt writes جوجل, the Levant and Gulf write غوغل). Be consistent.
- Transliterating ج/غ for g: **[VARIES]**. Egypt uses ج for /g/, others use غ or ق or ڤ (the ڤ U+06A4 for /v/ appears in the Maghreb and some Gulf branding).

### 7.3 Tatweel / kashida ـ (U+0640)

**Rule:** do not use it in running text.
- It is a typesetting device. Inserted into text, it breaks search, copy-paste, spell-check, screen readers and line breaking.
- ✗ مـحـمـد، الــســلام، جـمـيـل (decorative or emphasis stretching)
- ✗ Using ـ for justification. Renderers do justification. Never use the character for it.

**Allowed:**
- Abbreviation marks: هـ (Hijri) as in ١٤٤٨هـ. Also an isolated letter abbreviation like صـ/ص (page) **[VARIES]**.
- Prefix-to-Latin as in بـ Git.
- Citing letter forms in a lesson: الحرف (عـ) في أول الكلمة.
- Citing a prefix or suffix morpheme: الـ التعريف, ـة, ـه.

**Check:** **M-regex** `ـ`, except `هـ\b` after a digit, `الـ` followed by a space or a word like التعريف/الشمسية, and `[بلكو]ـ\s?[A-Za-z]`.

### 7.4 Unicode hygiene

| Problem | Bad | Good | Check |
|---|---|---|---|
| Persian/Urdu letters in Arabic | ی U+06CC (Farsi yeh), ک U+06A9 (keheh), ہ U+06C1, ە U+06D5, ۀ U+06C0, ۓ, ے U+06D2, ۃ U+06C3 | ي U+064A / ى U+0649, ك U+0643, ه U+0647, ة U+0629 | **M-regex** `[یکہەۀےۃ]`. In Arabic text these are always errors. U+06CC is especially sneaky: it has no dots in final position, so كرسی looks like كرسى |
| Presentation forms (contextual glyphs stored as characters) | U+FB50–U+FDFF, U+FE70–U+FEFF (ﻛﺘﺎﺏ، ﻻ U+FEFB) | base letters (كتاب، لا) | **M-regex**. Fix by NFKC on those ranges only. Exceptions to tolerate: ﷺ U+FDFA and ﷻ U+FDFB (honorifics). Prefer to write them out (صلى الله عليه وسلم) in body text. Always flag ﷲ U+FDF2 and ﷽ U+FDFD |
| ZWNJ U+200C / ZWJ U+200D | inside Arabic words | none | **M-regex**. Not used in standard Arabic orthography (only Persian and Urdu). Strip from Arabic words |
| Non-composed hamza or madda | ا + U+0654 (hamza above), ا + U+0653 (madda), ي + U+0654 | أ U+0623, آ U+0622, ئ U+0626 | **M**: apply NFC normalization, which composes them |
| Alif wasla ٱ U+0671 and Qur'anic marks U+06D6–U+06ED | in MSA prose | ا | **M-regex**. Allowed only inside quoted Qur'anic text |
| Bare hamza in place of a seated one, or vice versa | ٴ U+0674 (high hamza), ء + ي | ئ | M-regex |
| Tatweel | ـ U+0640 | — | §7.3 |
| Stray direction marks | many U+200E/U+200F/U+202A–U+202E/U+2066–U+2069 | at most an RLM where needed | M-regex. Flag embedding or override characters U+202A–U+202E always |
| Dotless or mismatched forms | ٮ U+066E, ڡ U+06A1, ں U+06BA | ب، ف، ن | M-regex (these are archaic or Urdu) |
| Non-breaking space and odd spaces | U+00A0, U+2009, double spaces | single U+0020 | M-regex |
| Diacritic order | — | Run NFC. Canonical order puts fatha, damma and kasra before shadda in storage, which renders correctly | M |

Arabic letter range for the checker: `[ء-غف-ي]` for letters, `[ً-ْٰ]` for harakat plus the dagger alif.

### 7.5 Diacritics (التشكيل)

**Rule:** MSA prose is normally **unvocalized**. Add marks selectively, only where they remove a real ambiguity or help pronunciation. A **wrong** mark is worse than no mark, so a checker must verify every mark that is present.

Add them:
1. **Shadda** where it separates two words: علّم/علم، درّس/درس، قدّم/قدم، مدرّسة/مدرسة.
2. **Passive voice**: ضُرِبَ، كُتِبَ، يُعتبَر، تُوفِّي (✗ تَوَفّى for "died").
3. **Homographs in a context that does not settle them**:
   - عِلْم (knowledge) / عَلَم (flag)
   - الحُبّ (love) / الحَبّ (seeds)
   - مُلك / مَلِك / مَلَك
   - قَدَم / قِدَم
   - أُمّة / أَمَة
   - إنّ / أنّ (shown by the hamza)
4. **Foreign or rare words and proper names**: سُلْوَان، مُوسكُو (optional).
5. **Tanween fath** on common adverbs (أيضًا، جدًّا) (§5.2).
6. Grammatical endings only when the text is about the grammar.
7. **Full vocalization** only for Qur'an, Hadith, poetry, children's or learner texts, or when the user asks.

Avoid:
- Partial vocalization that is wrong or contradicts the grammar. Example: كتبَ الطالبِ (wrong case on the subject).
- Putting tashkeel on the article alif or on hamzat al-wasl.
- Putting sukun on madd letters.
- Doubling marks (two harakat on one letter, except shadda + haraka).

**Check:**
- **M-regex** for malformed sequences:
  - two vowel marks on one letter: `[ً-ِْ]{2,}` without shadda
  - a mark on a space or at the start of a word
  - a haraka directly on ا ى ة that cannot carry it: `ا[َ-ِ]` (fatha/damma/kasra on a plain alif)
  - tanween not at the end of a word
- Whether a mark is **correct** is **J**.

### 7.6 Other small conventions

- **Abbreviations:**
  - د. (دكتور), أ. (أستاذ), م. (مهندس), ص (page), ج (part)
  - هـ / م for eras
  - ق.م (BC), ت (died)
  - Use a period, or no mark at all, consistently. **[VARIES]**
- **Ordinals in lists:**
  - Markdown `1.` lists render correctly in RTL.
  - Arabic numbering (أولًا، ثانيًا) or letter numbering (أ، ب، ج، د) uses the أبجد order in formal documents: أ، ب، ج، د، هـ، و، ز. **[VARIES]**: some use ألفبائي order أ ب ت ث.
- **Interrogative أ with a negative:** ألم، أليس، ألا (✓, joined).
- **Hamza in loanwords:** إنترنت، إستراتيجية/استراتيجية **[VARIES]**, إلكتروني (✓ with إ is dominant), أكاديمية، أوروبا، إيطاليا.

---

## 8. Common spelling errors in modern writing

Check: M-r = regex, M-l = word list, J = judgment.

| ✗ Wrong | ✓ Correct | Rule | Check |
|---|---|---|---|
| إنشاء الله / انشاء الله | إن شاء الله | split; إنشاء means "creation" | M-r |
| لاكن / ولاكن | لكن / ولكن | dropped alif §3.2 | M-r |
| هاذا / هاذه / هاكذا / ذالك | هذا / هذه / هكذا / ذلك | §3.2 | M-r |
| إسم / إبن / إثنان / إمرأة | اسم / ابن / اثنان / امرأة | wasl nouns §1.1 | M-r |
| إستخدام / إنتظار / إجتماع / إقتصاد / إختبار | استخدام / انتظار / اجتماع / اقتصاد / اختبار | wasl masdars VIII/X | M-r |
| اعلان / انشاء / اسلام / ابداع / اجراء | إعلان / إنشاء / إسلام / إبداع / إجراء | Form IV masdar qat' | M-l |
| الى / ان / اذا / انا / او | إلى / إن، أن / إذا / أنا / أو | qat' particles | M-l |
| الي (as a preposition) / فى / الذى / التى / حتي / علي الطاولة | إلى / في / الذي / التي / حتى / على الطاولة | ى/ي §2.2 | M-r (+J for علي) |
| مستشفي / مصطفي / مستوي / معني | مستشفى / مصطفى / مستوى / معنى | ى in 4+ letter words | M-l |
| دعى / نجى / شكى / سمى (verb "rose") | دعا / نجا / شكا / سما | 3-letter verb from و | M-l (سمّى "named" is valid, so J) |
| رما / سعا / مشا / قضا | رمى / سعى / مشى / قضى | 3-letter verb from ي | M-l |
| أعطا / اشترا / انتها / استدعا | أعطى / اشترى / انتهى / استدعى | 4+ letters gives ى | M-l |
| أحيى / دنيى | أحيا / دنيا | preceded by ي gives ا | M-l |
| المدرسه / الجامعه / الحكومه / فاطمه | المدرسة / الجامعة / الحكومة / فاطمة | ة §2.1 | M-l |
| مياة / اتجاة / انتباة | مياه / اتجاه / انتباه | root ه | M-l |
| عادتاً / خاصتاً / مرتاً / نتيجتاً | عادةً / خاصةً / مرةً / نتيجةً | tanween on ة | M-r |
| سماءاً / بناءاً / ماءاً / إجراءاً | سماءً / بناءً / ماءً / إجراءً | no alif after اء §5.1 | M-r |
| شئ / شيئ / شىء | شيء | final hamza after a sukun ي | M-r |
| شيءاً / شيأ | شيئًا | ء + tanween after a connecting letter | M-r |
| جزئ / بطئ (noun) / ضوئ | جزء / بطء / ضوء | final hamza after a sukun | M-l |
| بريئ / بطيئ / مجيئ | بريء / بطيء / مجيء | final hamza after a long ي | M-r `يئ\b` (except مُهيِّئ, يُهيِّئ) |
| شاطيء / مباديء / قاريء | شاطئ / مبادئ / قارئ | final hamza after a kasra | M-r `يء\b` after a long-vowel consonant pattern, M-l |
| تفائل / تشائم / تسائل (noun) | تفاؤل / تشاؤم / تساؤل | damma hamza after ā gives ؤ | M-l |
| يتسائل / قرائة / برائة / إجرائات | يتساءل / قراءة / براءة / إجراءات | fatha hamza after ā gives ء | M-r `ائ(ة|ات)\b`, M-l |
| مسئلة / جرئة / نشئة / رأيس | مسألة / جرأة / نشأة / رئيس | middle hamza strength | M-l |
| مسئول / شئون / يقرءون | مسؤول / شؤون / يقرؤون | **[VARIES]** (Egyptian ئ is accepted). Be consistent | M-l (style) |
| ذهبو / قالو / كانو | ذهبوا / قالوا / كانوا | الألف الفارقة | M-l |
| يدعوا / يرجوا / يبدوا (singular subject) | يدعو / يرجو / يبدو | no alif after a root و | M-l + J |
| معلموا المدرسة / مهندسوا / ذووا | معلمو / مهندسو / ذوو | no alif after a construct noun plural | M-r + J |
| من ما / عن ما | مما / عما | §4 | M-r |
| لاسيما | لا سيما | §4 | M-r |
| رب ما / إن ما (for "only") | ربما / إنما | §4 | M-r + J |
| أن لا (subjunctive) | ألّا | §4 **[VARIES]** | J |
| قال أنّ | قال إنّ | إنّ after قال | M-r `قال(ت|وا)? أن` as a candidate, J |
| قرأن / الان / ألآن / أخر (for آخر) | قرآن / الآن / آخر | madda §1.3 | M-l + J |
| محمد ابن عبد الله (as a nasab) / إبن خلدون | محمد بن عبد الله / ابن خلدون | §3.3 | J / M-r |
| بسم الشعب | باسم الشعب | basmala-only drop | M-r |
| لإن / لان (for "because") / بان (for بأن) | لأن / بأن | hamza after a prefix | M-r + J |
| ايضا / جدا (no hamza or tanween; informal) | أيضًا / جدًّا | qat' + tanween | M-l |
| إذاً vs إذن | both | **[VARIES]** (Cairo accepts both; many prefer إذن) | style |
| مائة / مئة | both | **[VARIES]**. Be consistent | style |
| , ; ? in Arabic text | ، ؛ ؟ | §6.1 | M-r |
| space before ، ؟ . / no space after | `كلمة، كلمة` | §6.2 | M-r |
| مـحـمـد (tatweel) | محمد | §7.3 | M-r |
| ی ک (Persian code points) | ي ك | §7.4 | M-r |
| ۴۵۶ (Persian digits) / mixed ٢٠ and 20 | ٤٥٦ or 456, one set only | §7.1 | M-r |
| الرحمان / إلاه / اللاه | الرحمن / إله / الله | §3.2 | M-l |
| أنشاء الله / ان شاء الله | إن شاء الله | hamza + split | M-r |
| إلتي / ألذي | التي / الذي | الـ is wasl (relative pronouns) | M-r |
| إثر vs أثر | both (different words: إثرَ "right after", أثر "trace/effect") | J | J |

---

## 9. Implementation notes for the checker

1. **Normalize first.** Apply NFC, and map Persian ی/ک to Arabic. Do not silently fix ی that ends in ى without checking the word: كرسی is كرسي, but مستشفی is مستشفى. Map presentation forms to base letters with NFKC applied only to U+FB50–FDFF and U+FE70–FEFF. Strip ZWNJ, ZWJ and tatweel except the whitelisted uses. Do this before any word-list lookup.
2. **Strip prefixes and suffixes before list lookups.** Prefixes: و، ف، ب، ل، ك، س، ال، لل. Suffixes: ـه، ـها، ـهم، ـك، ـكم، ـي، ـنا، ـات، ـون، ـين، ـان. Prefixed words keep hamza seats, as in وإن، فإذا، بالاستخدام.
3. **Skip zones:** fenced code, inline code, URLs, email addresses, Latin-only tokens, and quoted Qur'anic text inside ﴿ ﴾. Qur'anic orthography (رسم عثماني) legitimately breaks MSA rules, for example الصلوة and السموات.
4. **Report severity:**
   - *error*: Persian code points, tatweel, presentation forms, wrong punctuation characters, إسم/إستخدام, هاذا/لاكن, عادتاً, شئ
   - *warning*: candidates that need judgment (ى/ي pairs, إن/أن, كلما/كل ما, ابن)
   - *style*: [VARIES] items, reported only for inconsistency within one text
5. **Consistency checks** across the whole text:
   - digit set
   - tanween placement ًا/اً
   - مسؤول/مسئول family
   - مئة/مائة
   - quote style «» vs ""
   - transliteration (جوجل/غوغل)
   - إذن/إذًا

---

## Sources

- مجمع اللغة العربية بدمشق، *قواعد الإملاء* (the reference behind most Levantine and Gulf school curricula), as summarized in الدرر السنية، *موسوعة اللغة العربية*, sections on همزة الوصل، همزة القطع، الهمزة المتوسطة والمتطرفة: https://dorar.net/arabia/2592, https://dorar.net/arabia/2594, https://dorar.net/arabia/2599, https://dorar.net/arabia/2601, https://dorar.net/arabia/2603, https://dorar.net/arabia/2669 (direct fetch returned HTTP 403; content taken from search extracts)
- *قرارات مجمع اللغة العربية بالقاهرة* (compilation, Al-Nasser University, Yemen): https://www.nu.edu.ye/wp-content/uploads/2014/01/قرارات-مجمع-اللغة-العربية-بالقاهرة.pdf
- Mustansiriyah University, College of Arts, spelling lectures (on هيئة/هيأة and the 1960 Cairo Academy position): https://www.uomustansiriyah.edu.iq/media/lectures/8/8_2018_05_03!12_13_00_AM.docx
- Palestine Technical University (PTUK) course material on the history of the hamza rules (Cairo Academy committee, 1947): https://lms.ptuk.edu.ps/mod/resource/view.php?id=420011
- ALECSO, spelling learning material (examples for the middle hamza, مسؤول): https://arabcodeweek2023.alecso.org/
- ديوان العرب, «ارتفاعًا بهمزة الوصل» (the و/ف test for wasl vs qat'): https://www.diwanalarab.com/ارتفاعا-بهمزة-الوصل
- أحمد زكي باشا، *الترقيم وعلاماته في اللغة العربية* (1912): https://usul.ai/es/t/tarqim-wa-calamat-fi-lugha-carabiyya
- ديوان العرب, «علامات الترقيم في الكتابة العربية ومواضع استعمالها»: https://diwanalarab.com/علامات-الترقيم-في.html
- University of Msila (Algeria) and Al-Mustaqbal University (Iraq) lecture notes on punctuation: https://elearning.univ-msila.dz/moodle/mod/resource/view.php?id=18849, https://www.uomus.edu.iq/img/lectures21/MUCLecture_2024_6854440.pdf
- W3C, *Arabic & Persian Layout Requirements* (alreq), on digit sets by region, separators U+066B and U+066C, kashida vs tatweel, and ZWNJ: https://www.w3.org/TR/alreq/
- W3C, alreq gap analysis: https://www.w3.org/International/alreq/gap-analysis/
- r12a, *Arabic script homographs* (look-alike code points): https://r12a.github.io/scripts/arab/homographs
- Doctor et al., *Graphemic Normalization of the Perso-Arabic Script* (arXiv 2210.12273): https://arxiv.org/pdf/2210.12273
- M. Kaplan, "Every character has a story #18: U+06CC and U+064A": https://archives.miloush.net/michkap/archive/2006/02/14/531572.html
- W3C i18n list, the U+0626 / U+06CC + U+0654 normalization discussion: https://lists.w3.org/Archives/Public/public-i18n-archive/2021JulSep/0253.html
- Apache Lucene, SoraniNormalizer (an example of normalizer behaviour for yeh, keheh and tatweel): https://lucene.apache.org/core/5_5_0/analyzers-common/org/apache/lucene/analysis/ckb/SoraniNormalizer.html
- The Unicode Standard, Arabic block chart (U+0600–06FF) and Arabic Presentation Forms-A/B (U+FB50–FDFF, U+FE70–FEFF), from general knowledge
- Plus general knowledge of standard school إملاء curricula (Egypt, the Levant, the Gulf) and Arab press style practice (for the [VARIES] notes)
