import unittest
from collections import Counter

from evals import build_lexicon as bl


class BuildLexiconTest(unittest.TestCase):
    def test_hamza_pairs(self):
        c = Counter({"الأطفال": 50, "الاطفال": 0, "أجلس": 50, "وأنس": 50, "الاستخدام": 80,
                     "الإستخدام": 1, "أكثر": 90, "اكثر": 20})
        hamza, _ = bl.pairs(c, 5, 0.01)
        wrong = {w for w, _, _ in hamza}
        self.assertIn("الاطفال", wrong)
        self.assertNotIn("اجلس", wrong)  # also the imperative اجلِس
        self.assertNotIn("وانس", wrong)  # also وانسَ "and forget"
        self.assertNotIn("اكثر", wrong)  # bare form too common in the corpus
        self.assertFalse(any(r.startswith("الإست") for _, r, _ in hamza))

    def test_taa_pairs_definite_or_common_nisba(self):
        c = Counter({"الدولة": 50, "مكتبة": 50, "السلبية": 50, "سلبية": 40, "باقية": 40})
        _, taa = bl.pairs(c, 5, 0.01)
        wrong = {w for w, _, _ in taa}
        self.assertIn("الدوله", wrong)
        self.assertIn("سلبيه", wrong)
        self.assertNotIn("مكتبه", wrong)  # "his office" is a real word
        self.assertNotIn("باقيه", wrong)  # "the rest of it"

    def test_endings(self):
        c = Counter({"المصري": 50, "كانوا": 50, "يدعوا": 50, "والي": 50, "ووالي": 50})
        yaa, waw = bl.endings(c, 5, 0.01)
        self.assertIn("المصرى", {w for w, _, _ in yaa})
        self.assertNotIn("ووالى", {w for w, _, _ in yaa})  # Form III verb
        self.assertEqual({w for w, _, _ in waw}, {"كانو"})  # not the imperfect يدعو

    def test_one_suggestion_per_wrong_form(self):
        rows = bl._best([("واثر", "وإثر", 8), ("واثر", "وأثر", 10)])
        self.assertEqual(rows, [("واثر", "وأثر", 10)])


if __name__ == "__main__":
    unittest.main()
