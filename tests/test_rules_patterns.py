import unittest

from archeck.engine import check


def of(text, rule, **kw):
    return [f for f in check(text, **kw) if f.rule == rule]


def spans(text, rule, **kw):
    return [text[f.start:f.end] for f in of(text, rule, **kw)]


DENSE = (
    "تم إنشاء المشروع في العام الماضي، وتم تطوير النظام من قبل فريق صغير "
    "من المهندسين، ثم تم اختبار الوظائف بعناية قبل إطلاق النسخة الأولى "
    "للمستخدمين في المنطقة العربية كلها خلال الشهر"
)

_FILLER = (
    "كتب الباحث تقريرا مفصلا عن حالة المدارس في القرى البعيدة وشرح فيه "
    "الصعوبات التي يواجهها المعلمون والطلاب كل يوم "
)


class DigitMixTest(unittest.TestCase):
    def test_digit_mix_auto(self):
        found = of("لدينا 3 ملفات و٤ مجلدات و5 صور", "digit-mix")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].suggestion, "4")
        self.assertEqual(found[0].severity, "warn")

    def test_digit_mix_arabic_option(self):
        text = "لدينا 3 ملفات و٤ مجلدات و5 صور"
        self.assertEqual(spans(text, "digit-mix", digits="arabic"), ["3", "5"])
        self.assertEqual(
            [f.suggestion for f in of(text, "digit-mix", digits="arabic")],
            ["٣", "٥"],
        )

    def test_digit_mix_tie_is_western(self):
        self.assertEqual(spans("لدينا 12 ملفا و٣٤ مجلدا", "digit-mix"), ["٣٤"])

    def test_digits_in_code_ignored(self):
        self.assertEqual(of("الأمر `ls -1` يعرض ٣ ملفات", "digit-mix"), [])

    def test_digits_in_latin_tokens_ignored(self):
        self.assertEqual(of("حمّل ملف mp3 وثبّت IPv6 في ٣ أجهزة", "digit-mix"), [])

    def test_english_only_line_ignored(self):
        self.assertEqual(of("نص فيه ٣ ملفات\nversion 2 of 5", "digit-mix"), [])


class TanweenSpellingTest(unittest.TestCase):
    def test_tanween_mixed(self):
        self.assertEqual(spans("شكراً جزيلًا", "tanween-mixed"), ["شكراً"])
        self.assertEqual(of("شكراً جزيلًا", "tanween-mixed")[0].suggestion, "شكرًا")
        self.assertEqual(of("شكرًا جزيلًا", "tanween-mixed"), [])
        self.assertEqual(of("شكراً جزيلاً", "tanween-mixed"), [])

    def test_spelling_mixed(self):
        found = of("المسئولون", "spelling-mixed")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].suggestion, "المسؤولون")
        self.assertEqual(of("مائة", "spelling-mixed")[0].suggestion, "مئة")
        self.assertEqual(of("المسؤولون عن مئة موظف", "spelling-mixed"), [])


class LatinTest(unittest.TestCase):
    def test_stray_english(self):
        self.assertEqual(spans("هذا feature جديد", "stray-english"), ["feature"])
        self.assertEqual(of("واجهة برمجة التطبيقات (API)", "stray-english"), [])
        self.assertEqual(of("ملف JSON", "stray-english"), [])
        self.assertEqual(of("ميزة جديدة (new feature)", "stray-english"), [])
        # Names and products keep their spelling.
        self.assertEqual(of("ثبّت Docker وأدوات مثل Google Analytics", "stray-english"), [])
        self.assertEqual(of("This is plain English text", "stray-english"), [])
        self.assertEqual(of("نظام Windows ولغة python ومنصة GitHub", "stray-english"), [])

    def test_rtl_line_start(self):
        self.assertEqual(spans("- Python لغة سهلة", "rtl-line-start"), ["Python"])
        self.assertEqual(spans("## 1. Rust أداة", "rtl-line-start"), ["Rust"])
        self.assertEqual(spans("**Rust** لغة سريعة", "rtl-line-start"), ["Rust"])
        self.assertEqual(spans("v1.2-beta، إصدار جديد", "rtl-line-start"), ["v1.2-beta"])
        self.assertIn("Latin word", of("- Rust لغة", "rtl-line-start")[0].message)
        found = of("2024 كان عامًا مميزًا", "rtl-line-start")
        self.assertEqual(len(found), 1)
        self.assertIn("Western digit", found[0].message)
        self.assertEqual(of("٢٠٢٤ كان عامًا مميزًا", "rtl-line-start"), [])
        self.assertEqual(of("---\ntitle: مقال\ndescription: نص\n---\nنص", "rtl-line-start"), [])
        self.assertEqual(of("- لغة Python سهلة", "rtl-line-start"), [])
        self.assertEqual(of("Python is easy to learn", "rtl-line-start"), [])

    def test_rtl_line_start_code_or_link(self):
        # Masked code and URLs at the start of a line still render LTR.
        self.assertEqual(spans("- `git status` يعرض الحالة", "rtl-line-start"),
                         ["`git status`"])
        self.assertEqual(spans("## `API` في النظام", "rtl-line-start"), ["`API`"])
        self.assertEqual(spans("- https://example.com موقع جيد", "rtl-line-start"),
                         ["https://example.com"])
        self.assertEqual(of("- الأمر `git status` يعرض الحالة", "rtl-line-start"), [])
        self.assertEqual(of("```\ngit status يعرض\n```", "rtl-line-start"), [])
        self.assertEqual(of("- `مثال` نص عربي", "rtl-line-start"), [])

    def test_tanween_alif(self):
        self.assertEqual([f.suggestion for f in of("زرت مدرسةًا جديدة", "tanween-alif")],
                         ["مدرسةً"])
        self.assertEqual([f.suggestion for f in of("جاء مساءًا", "tanween-alif")],
                         ["مساءً or مساءَ"])
        self.assertEqual([f.suggestion for f in of("كانوا أعضاءًا", "tanween-alif")],
                         ["أعضاءً or أعضاءَ"])
        self.assertEqual([f.suggestion for f in of("زرت المدرسةاً", "tanween-alif")],
                         ["المدرسة"])
        for wrong, right in (("عادتاً", "عادةً"), ("وخاصتاً", "وخاصةً"),
                             ("نتيجتًا", "نتيجةً"), ("مرتاً", "مرةً")):
            self.assertEqual([f.suggestion for f in of(wrong + " نذهب", "tanween-alif")],
                             [right])
            self.assertEqual(of(wrong + " نذهب", "tanween-mixed"), [])
        # عادتا without tanween is a dual; شيئًا and جزءًا are correct.
        for ok in ("عادتا الطفلين", "قرأت شيئًا وجزءًا", "جاءا معًا", "مدرسةً"):
            self.assertEqual(of(ok, "tanween-alif"), [])
        # Already in misspellings.tsv: reported once.
        self.assertEqual(of("بدأ البناءاً", "tanween-alif"), [])

    def test_compound_number(self):
        found = of("لدينا ثلاثة عشرة طالبًا", "compound-number")
        self.assertEqual([(f.severity, f.suggestion) for f in found],
                         [("error", "ثلاثة عشر (m.) or ثلاث عشرة (f.)")])
        self.assertEqual(of("بعد ثماني عشرة", "compound-number"), [])
        self.assertEqual(of("ثمانية عشرة", "compound-number")[0].suggestion,
                         "ثمانية عشر (m.) or ثماني عشرة (f.)")
        self.assertEqual(spans("جاء بخمسة عشرة سفينة", "compound-number"), ["بخمسة عشرة"])
        found = of("طيلة خمس عشر عامًا", "compound-number")
        self.assertEqual([(f.severity, f.suggestion) for f in found],
                         [("warn", "خمسة عشر (m.) or خمس عشرة (f.)")])
        for ok in ("ثلاثة عشر رجلًا وثلاث عشرة امرأة", "ستة عشر عامًا",
                   "خمسة، عشرة", "خمس عُشر"):
            self.assertEqual(of(ok, "compound-number"), [])
        self.assertEqual(of("1. لغة سهلة", "rtl-line-start"), [])


class GrammarPatternTest(unittest.TestCase):
    def test_sawfa_lan(self):
        found = of("سوف لن أذهب", "sawfa-lan")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].suggestion, "لن")

    def test_number_gender(self):
        self.assertEqual(of("لدينا ثلاث ملفات", "number-gender")[0].suggestion, "ثلاثة")
        self.assertEqual(of("خمسة نصائح مفيدة", "number-gender")[0].suggestion, "خمس")
        self.assertEqual(of("بعد أربع أيام", "number-gender")[0].suggestion, "أربعة")
        self.assertEqual(of("وثمانية سنوات", "number-gender")[0].suggestion, "وثماني")
        self.assertEqual(of("بضعة دقائق", "number-gender")[0].suggestion, "بضع")
        self.assertEqual(of("وبثلاث كتب", "number-gender")[0].suggestion, "وبثلاثة")
        self.assertEqual(spans("قرأت ثلاث كتب", "number-gender"), ["ثلاث"])
        for t in ("على مدى ثلاث `x` كتب", "قرأت ثلاث\n\nكتب"):
            self.assertEqual(of(t, "number-gender"), [], t)
        for t in ("ثلاثة ملفات", "ثلاث خطوات", "خمسة أيام", "سبع سنوات", "ثماني ساعات",
                  "عشرة أسئلة", "بضع سنوات", "خُمس أعضاء المجلس", "ثلاث سيارات",
                  "خمسة عشر يومًا", "ثلاث عشرة سنة", "الأيام الثلاثة", "الخمسة كتب"):
            self.assertEqual(of(t, "number-gender"), [], t)

    def test_maqsura_medial(self):
        self.assertEqual(len(of("وساىل التواصل", "maqsura-medial")), 1)
        self.assertEqual(len(of("علىمقاومة", "maqsura-medial")), 1)
        for t in ("على الطاولة", "مستشفى كبير", "إلى، ومتى؟", "مصطفىً"):
            self.assertEqual(of(t, "maqsura-medial"), [], t)

    def test_jussive_nun(self):
        self.assertEqual(of("لم يكونون هناك", "jussive-nun")[0].suggestion, "يكونوا")
        self.assertEqual(of("لن يذهبون", "jussive-nun")[0].suggestion, "يذهبوا")
        self.assertEqual(of("لم تذهبين", "jussive-nun")[0].suggestion, "تذهبي")
        self.assertEqual(len(of("يجب أن يعملون معا", "jussive-nun")), 1)
        self.assertEqual(of("التزموا بأن يكونون مستعدين", "jussive-nun")[0].suggestion, "يكونوا")
        self.assertEqual(of("لم يكونوا هناك", "jussive-nun"), [])

    def test_jussive_nun_no_false_positives(self):
        for t in ("أن يكون", "لن يكون", "أن تكون", "أن يتكون", "يمكن أن يتعاون",
                  "لم يتبين", "لم يبين السبب", "لم تتبين", "لن يكتبن",
                  "أن يلون", "أنّ تعاون البلدين", "لم يكن", "لم تكوني",
                  "لِمَ تقولون ما لا تفعلون", "لم تتركون الدرس مبكرًا؟",
                  "قال: لم تذهبين إلى هناك؟ ثم سكت"):
            self.assertEqual(of(t, "jussive-nun"), [], t)

    def test_relative_after_indefinite(self):
        self.assertEqual(
            spans("كتاب الذي قرأته", "relative-after-indefinite"), ["كتاب الذي"]
        )
        self.assertEqual(len(of("قرأت كتابًا الذي", "relative-after-indefinite")), 1)
        self.assertEqual(of("كتاب الذي", "relative-after-indefinite")[0].severity, "info")
        for t in ("الكتاب الذي", "كتابه الذي", "هذا الذي", "إن الذين آمنوا",
                  "في الذي", "كل الذين حضروا", "رأيت الذي", "يحب الذين",
                  "شكروا الذين", "ما الذي حدث", "للطلاب الذين", "والكتاب الذي"):
            self.assertEqual(of(t, "relative-after-indefinite"), [], t)

    def test_translationese_density(self):
        found = of(DENSE, "translationese-density")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].severity, "info")
        self.assertIn("تم", found[0].message)
        sparse = "تم " + " ".join([_FILLER] * 6)
        self.assertGreaterEqual(len(sparse.split()), 100)
        self.assertEqual(of(sparse, "translationese-density"), [])

    def test_translationese_span_survives_approved_filter(self):
        text = "بشكل كبير تحسن الأداء بشكل واضح"
        found = of(text, "translationese-density")
        self.assertEqual(len(found), 1)
        self.assertEqual(text[found[0].start:found[0].end], "بشكل كبير")

    def test_temporal_min_qabl_not_counted(self):
        text = "لم أره من قبل. ولم أسمع به من قبل، ولا أعرفه"
        self.assertEqual(of(text, "translationese-density"), [])


if __name__ == "__main__":
    unittest.main()


class EnglishLineTests(unittest.TestCase):
    AR = "هذا شرح قصير لطريقة تثبيت الأداة على جهازك.\nشغّل الأمر التالي ثم انتظر حتى ينتهي التثبيت.\n"

    def test_english_prose_line_in_arabic_document(self):
        text = self.AR + "I assumed two things you should check:\n"
        self.assertEqual([f.severity for f in of(text, "english-line")], ["warn"])

    def test_english_bullet_in_arabic_document(self):
        text = self.AR + "- **Package name:** the commands use the default name.\n"
        self.assertEqual(len(of(text, "english-line")), 1)

    def test_short_english_line_not_flagged(self):
        self.assertEqual(of(self.AR + "### Setup\n", "english-line"), [])

    def test_code_block_not_flagged(self):
        text = self.AR + "```\npip install the tool from the package index\n```\n"
        self.assertEqual(of(text, "english-line"), [])

    def test_english_document_not_flagged(self):
        text = "This is an English document.\nIt has several English lines in it.\n"
        self.assertEqual(of(text, "english-line"), [])

    def test_mixed_line_not_flagged(self):
        text = self.AR + "ثبّت الأداة with the package manager you prefer\n"
        self.assertEqual(of(text, "english-line"), [])
