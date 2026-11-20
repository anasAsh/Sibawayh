import unittest

from archeck.text import has_arabic, iter_words, line_col, mask, stem_candidates


class MaskTest(unittest.TestCase):
    def test_mask_keeps_length_and_newlines(self):
        t = (
            "مرحبا\n```python\nprint(1)\n```\nنص `code` و https://a.b/c\n"
            "﴿بسم الله\nالرحمن﴾ نهاية\n"
        )
        m = mask(t)
        self.assertEqual(len(m), len(t))
        self.assertEqual(
            [i for i, c in enumerate(m) if c == "\n"],
            [i for i, c in enumerate(t) if c == "\n"],
        )

    def test_mask_blanks_code_and_url(self):
        m = mask("انظر `x, y` و https://a.b/c?d=1")
        for bad in ("x", ",", "https"):
            self.assertNotIn(bad, m)

    def test_mask_markdown_link_url_whole(self):
        m = mask("نزّله من [python.org](https://www.python.org/downloads/) ثم ثبّته")
        self.assertNotIn("downloads", m)
        self.assertIn("ثبّته", m)

    def test_mask_path_ascii_only(self):
        self.assertEqual(mask("المعلم/المعلمة.ثم"), "المعلم/المعلمة.ثم")
        self.assertEqual(mask("و/أو.كلمة"), "و/أو.كلمة")
        m = mask("انظر src/app/main.py الآن")
        self.assertNotIn("src", m)
        self.assertNotIn("main.py", m)
        self.assertIn("الآن", m)

    def test_mask_off_on_markers(self):
        t = "<!-- arabic-check: off -->\nمسئول\n<!-- arabic-check: on -->\nمائة"
        m = mask(t)
        self.assertNotIn("مسئول", m)
        self.assertNotIn("arabic-check", m)
        self.assertIn("مائة", m)

    def test_mask_tilde_fence_email_path_quran(self):
        t = "~~~\ncode\n~~~\na@b.com ~/x/y /usr/lib/a.py ﴿آية﴾ باقي"
        m = mask(t)
        for bad in ("code", "a@b.com", "~/x", "a.py", "آية"):
            self.assertNotIn(bad, m)
        self.assertIn("باقي", m)

    def test_mask_yaml_front_matter(self):
        t = "---\ntitle: مقال\ntags: [a, b]\n---\nنص title: هنا\n"
        m = mask(t)
        self.assertEqual(len(m), len(t))
        self.assertEqual(m.count("\n"), t.count("\n"))
        self.assertNotIn("title: مقال", m)
        self.assertNotIn("---", m)
        self.assertIn("نص title: هنا", m)
        # Only at the very start of the text.
        later = "نص\n---\nkey: قيمة\n---\n"
        self.assertEqual(mask(later), later)

    def test_has_arabic(self):
        self.assertTrue(has_arabic("abc ب"))
        self.assertFalse(has_arabic("abc"))


class WordsTest(unittest.TestCase):
    def test_iter_words_offsets(self):
        self.assertEqual(
            list(iter_words("ذهب الطلابُ.")),
            [(0, 3, "ذهب"), (4, 11, "الطلابُ")],
        )

    def test_digits_are_not_word_chars(self):
        self.assertEqual([w for _, _, w in iter_words("كتاب٣ \u0670")], ["كتاب"])

    def test_stem_candidates(self):
        self.assertIn("إسم", stem_candidates("وبالإسم"))
        self.assertIn("مدرسة", stem_candidates("للمدرسة"))

    def test_stem_candidates_order_and_min_length(self):
        c = stem_candidates("الكتابُ")
        self.assertEqual(c[0], "الكتاب")
        self.assertEqual(c[-1], "كتاب")
        self.assertEqual(len(c), len(set(c)))
        self.assertTrue(all(len(x) >= 2 for x in stem_candidates("وب")))

    def test_line_col(self):
        self.assertEqual(line_col("أ\nب", 2), (2, 1))
        self.assertEqual(line_col("أب", 1), (1, 2))


if __name__ == "__main__":
    unittest.main()


class NestedFenceTests(unittest.TestCase):
    def test_four_backtick_fence_wraps_inner_fences(self):
        text = ("قبل\n````markdown\nنص داخلي\n```bash\npip install x\n```\nنص آخر\n````\nبعد\n")
        m = mask(text)
        self.assertIn("قبل", m)
        self.assertIn("بعد", m)
        for hidden in ("نص داخلي", "pip install x", "نص آخر"):
            self.assertNotIn(hidden, m)

    def test_info_string_line_does_not_close_fence(self):
        text = "```\ncode one\n```python\ncode two\n```\nعربي\n"
        m = mask(text)
        self.assertNotIn("code two", m)
        self.assertIn("عربي", m)

    def test_unclosed_fence_masks_to_end(self):
        self.assertNotIn("code", mask("نص\n```\ncode"))
