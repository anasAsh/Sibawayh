import unittest

from archeck.engine import check, fix_text


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

    def test_dot_never_false_positive(self):
        for t in ("د.أحمد", "ج.م.ع", "ص.ب 123", "كلمة ... ثم", "كلمة…ثم",
                  "المعلم/المعلمة.ثم", "كلمة..ثم"):
            self.assertEqual(fix_text(t), t)
        self.assertEqual(fix_text("انتهى . ثم"), "انتهى. ثم")

    def test_punct_latin_crlf(self):
        self.assertEqual(fix_text("هل جئت?\r\nنعم"), "هل جئت؟\r\nنعم")

    def test_numbers_untouched(self):
        t = "السعر 3.5 دينار و1,000 و10:30 و٣٫٥"
        self.assertEqual(fix_text(t), t)

    def test_persian_letters(self):
        self.assertEqual(fix_text("کتاب"), "كتاب")
        self.assertEqual(fix_text("کبیر"), "كبير")

    def test_persian_final_yeh_is_warn_only(self):
        for word in ("علی", "إلی", "حتی"):
            self.assertEqual(fix_text(word), word)
            found = [f for f in check(word) if f.rule == "persian-letter-final"]
            self.assertEqual(len(found), 1, word)
            f = found[0]
            self.assertEqual(f.severity, "warn")
            self.assertIsNone(f.replacement)
            self.assertEqual(f.suggestion, "ي or ى")
            self.assertEqual((f.start, f.end), (len(word) - 1, len(word)))
        # ک is still fixed; the final ی stays for the writer to decide.
        self.assertEqual(fix_text("کرسی"), "كرسی")

    def test_persian_only_letters_skip_token(self):
        for t in ("گفتگوی", "پیک", "چی", "ژیک"):
            self.assertEqual(fix_text(t), t)
            self.assertEqual([f for f in check(t) if f.rule.startswith("persian-letter")], [])

    def test_lone_letter_is_left_alone(self):
        # A letter cited on its own, e.g. in a table of alphabets.
        t = "اللغة السندية: ک -- كهي"
        self.assertEqual(fix_text(t), t)
        self.assertEqual([f for f in check(t) if f.rule.startswith("persian-letter")], [])

    def test_token_without_letters(self):
        for t in ("ـــ", "\u064e"):
            self.assertEqual(fix_text(t), t)

    def test_kurdish_ae_not_mapped(self):
        t = "\u06d5"
        self.assertEqual(fix_text(t), t)

    def test_presentation_forms(self):
        self.assertEqual(fix_text("\ufefb"), "لا")
        self.assertEqual(fix_text("\ufefc"), "لا")

    def test_word_ligatures_kept(self):
        for t in ("\ufdfa", "\ufdf2", "\ufdfc", "محمد \ufdfa"):
            self.assertEqual(fix_text(t), t)
            self.assertEqual([f for f in check(t) if f.rule == "presentation-form"], [])

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
