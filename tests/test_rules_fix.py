import unittest

from archeck.engine import fix_text


class FixRulesTest(unittest.TestCase):
    def test_punct_latin(self):
        self.assertEqual(fix_text("ذهبت إلى السوق, ثم عدت"), "ذهبت إلى السوق، ثم عدت")
        self.assertEqual(fix_text("هل جئت?"), "هل جئت؟")
        self.assertEqual(fix_text("قال; ثم"), "قال؛ ثم")

    def test_punct_latin_leaves_english(self):
        for t in ("لغات مثل (Python, Java) مفيدة", "e.g., نص"):
            self.assertEqual(fix_text(t), t)

    def test_punct_space(self):
        self.assertEqual(fix_text("قال ، ثم"), "قال، ثم")
        self.assertEqual(fix_text("قال،ثم"), "قال، ثم")

    def test_numbers_untouched(self):
        t = "السعر 3.5 دينار و1,000 و10:30 و٣٫٥"
        self.assertEqual(fix_text(t), t)

    def test_persian_letters(self):
        self.assertEqual(fix_text("کتابی"), "كتابي")

    def test_presentation_forms(self):
        self.assertEqual(fix_text("\ufefb"), "لا")

    def test_tatweel(self):
        self.assertEqual(fix_text("جمـــيل"), "جميل")
        for t in ("1445هـ", "الـAPI"):
            self.assertEqual(fix_text(t), t)

    def test_persian_digits(self):
        self.assertEqual(fix_text("العدد \u06f1\u06f2"), "العدد 12")
        self.assertEqual(
            fix_text("العدد \u06f1\u06f2", digits="arabic"), "العدد \u0661\u0662"
        )


if __name__ == "__main__":
    unittest.main()
