import unittest
from unittest import mock

from archeck.engine import apply_fixes, check, fix_text
from archeck import rules_lists
from archeck.model import Finding


class EngineTest(unittest.TestCase):
    def test_masked_regions_untouched(self):
        pieces = [
            '```\nx = "a , b"\n```',
            "`a,b`",
            "https://x.y/a,b",
            "~/dir/file.py",
        ]
        t = (
            "ذهبت, ثم رأيت\n" + pieces[0] + "\nوقال ، ثم " + pieces[1]
            + " وانظر " + pieces[2] + " و " + pieces[3] + " ثم عدت?"
        )
        out = fix_text(t)
        for p in pieces:
            self.assertIn(p, out)
        self.assertIn("ذهبت،", out)
        self.assertTrue(out.endswith("عدت؟"))

    def test_english_only_is_noop(self):
        t = "Hello, world; is this ok? Yes, it is. See a.b/c.py: done!\nOK , fine."
        self.assertEqual(check(t), [])
        self.assertEqual(fix_text(t), t)

    def test_fix_idempotent(self):
        t = "کتاب, جمـــيل ،ثم \ufefb عدد \u06f1\u06f2 هل جئت? قال;ثم"
        once = fix_text(t)
        self.assertEqual(fix_text(once), once)
        self.assertNotEqual(once, t)

    def test_approved_filter(self):
        t = "هذا يعتبر مهما جدا"
        word = Finding(4, 9, "warn", "fake", "m")
        multi = Finding(0, 9, "warn", "fake", "m")
        self.assertEqual(t[4:9], "يعتبر")
        with mock.patch.object(rules_lists, "RULES", [lambda *a: [word]]):
            self.assertEqual(check(t), [])
        with mock.patch.object(rules_lists, "RULES", [lambda *a: [multi]]):
            self.assertEqual(check(t), [multi])

    def test_approved_form_keeps_grammar_and_tanween_findings(self):
        rules = lambda t: {f.rule for f in check(t)}
        self.assertIn("jussive-nun", rules("لم يعتبرون ذلك مهما"))
        self.assertIn("jussive-nun", rules("لن تعتبرون ذلك مهما"))
        self.assertIn("tanween-mixed",
                      rules("قرأت كتابًا جديدًا ولم أره أبداً من قبل"))

    def test_apply_fixes_skips_overlap(self):
        t = "abcdef"
        a = Finding(1, 4, "fix", "r1", "m", replacement="X")
        b = Finding(3, 5, "fix", "r2", "m", replacement="Y")
        c = Finding(0, 1, "error", "r3", "m", replacement="Z")
        self.assertEqual(apply_fixes(t, [b, a, c]), "aXef")


if __name__ == "__main__":
    unittest.main()
