import unittest

from archeck.data import load_list, load_tsv
from archeck.engine import check

_FILES = {
    "misspellings.tsv": "wrong",
    "wasl_words.tsv": "wrong",
    "hamza_missing.tsv": "wrong",
    "taa_haa.tsv": "wrong",
    "alif_maqsura.tsv": "wrong",
    "dialect_words.tsv": "word",
}


def pairs(text):
    return [(f.rule, f.suggestion) for f in check(text)]


def rules(text):
    return [f.rule for f in check(text)]


class ListRulesTest(unittest.TestCase):
    def test_misspellings(self):
        self.assertIn(("misspelling", "هذا"), pairs("هاذا"))
        self.assertIn(("misspelling", "لكن"), pairs("لاكن"))
        self.assertIn(("misspelling", "إن شاء الله"), pairs("إنشاء الله"))
        self.assertIn(("misspelling", "مما"), pairs("من ما"))
        self.assertIn(("misspelling", "عما"), pairs("سألته عن ما حدث"))
        self.assertIn(("misspelling", "التي"), pairs("المشاكل اللتي تواجهنا"))
        self.assertNotIn("misspelling", rules("الطالبتين اللتين نجحتا"))
        self.assertNotIn("misspelling", rules("قال والدي"))

    def test_misspelling_keeps_prefix(self):
        self.assertIn(("misspelling", "كذلك"), pairs("كذالك"))
        self.assertIn(("misspelling", "ولكن"), pairs("ولاكن"))
        self.assertIn(("misspelling", "وشيء"), pairs("وشئ"))

    def test_multiword_span_and_diacritics(self):
        text = "سأحضر إِنْشَاءَ اللهِ غدًا"
        found = [f for f in check(text) if f.rule == "misspelling"]
        self.assertEqual(len(found), 1)
        self.assertEqual(text[found[0].start:found[0].end], "إِنْشَاءَ اللهِ")
        self.assertEqual(rules("من ماء"), [])

    def test_hamza_wasl_with_prefix(self):
        self.assertIn(("hamza-wasl", "وبالاستخدام"), pairs("وبالإستخدام"))
        self.assertIn(("hamza-wasl", "اسم"), pairs("إسم"))
        self.assertIn(("hamza-wasl", "للاستخدام"), pairs("للإستخدام"))

    def test_hamza_wasl_masdar_shape(self):
        # Not in wasl_words.tsv; caught by the form VII/VIII/X masdar shape.
        self.assertIn(("hamza-wasl", "واستنباط"), pairs("وإستنباط"))
        self.assertIn(("hamza-wasl", "الانحدار"), pairs("الإنحدار"))
        self.assertIn(("hamza-wasl", "بالاستمساك"), pairs("بالإستمساك"))
        self.assertIn(("hamza-wasl", "الاشتراكية"), pairs("الإشتراكية"))
        self.assertEqual(rules("وإستنباط").count("hamza-wasl"), 1)

    def test_hamza_wasl_shape_skips_form_iv_and_loanwords(self):
        for t in ("إنتاج", "إنفاق", "إنسانية", "إتقان", "إطلاق", "إستبرق",
                  "إستراتيجية", "إستراليا", "الإنكشارية"):
            self.assertNotIn("hamza-wasl", rules(t), t)

    def test_hamza_wasl_span(self):
        text = "تم الإستخدام"
        f = [f for f in check(text) if f.rule == "hamza-wasl"][0]
        self.assertEqual((f.start, f.end), (3, len(text)))
        self.assertEqual(f.severity, "error")
        self.assertIsNone(f.replacement)

    def test_form_iv_masdars_not_wasl(self):
        self.assertEqual(rules("إنتاج إنشاء إتقان إتمام إطلاق إرسال إعلان"), [])

    def test_hamza_missing(self):
        found = [f for f in check("ذهب الى البيت") if f.rule == "hamza-missing"]
        self.assertEqual([(f.suggestion, f.severity) for f in found], [("إلى", "warn")])
        self.assertIn(("hamza-missing", "وإذا"), pairs("واذا"))

    def test_hamza_missing_common_words(self):
        self.assertIn(("hamza-missing", "أن"), pairs("يجب ان نذهب"))
        self.assertIn(("hamza-missing", "وأنه"), pairs("وانه قال"))
        self.assertIn(("hamza-missing", "أهل"), pairs("جمع اهل بيته"))
        self.assertIn(("hamza-missing", "الإسلام"), pairs("في الاسلام"))
        # A cited ending is not a word.
        self.assertNotIn("hamza-missing", rules("المثنى بـان أو ـين"))
        # Prefixed look-alikes stay valid words.
        for t in ("كانت", "بان الحق", "لان الحديد", "واحد", "فان"):
            self.assertNotIn("hamza-missing", rules(t), t)

    def test_hamza_missing_inshaa(self):
        found = [f for f in check("تم انشاء الملف") if f.rule == "hamza-missing"]
        self.assertEqual([(f.suggestion, f.severity) for f in found], [("إنشاء", "warn")])
        for t in ("إنشاء الملف", "الإنشاء", "إنشاءات", "إنشائي"):
            self.assertEqual(rules(t), [], t)

    def test_inshaa_allah_only_misspelling(self):
        # انشاء الله is إن شاء الله, never إنشاء الله.
        for t in ("سنلتقي انشاء الله", "انشاء الله نلتقي"):
            self.assertEqual(pairs(t), [("misspelling", "إن شاء الله")], t)

    def test_taa_haa(self):
        self.assertIn(("taa-haa", "الجامعة"), pairs("الجامعه"))
        self.assertIn(("taa-haa", "للمدرسة"), pairs("للمدرسه"))
        self.assertIn(("taa-haa", "اتجاه"), pairs("اتجاة"))

    def test_alif_maqsura(self):
        self.assertIn(("alif-maqsura", "في"), pairs("فى"))
        self.assertIn(("alif-maqsura", "والذي"), pairs("والذى"))
        self.assertIn(("alif-maqsura", "للذي"), pairs("للذى"))

    def test_dialect(self):
        found = [f for f in check("بدي أشرح") if f.rule == "dialect-word"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].severity, "warn")
        self.assertIn(("dialect-word", "وأريد"), pairs("وبدي"))

    def test_no_false_positives(self):
        text = (
            "قرأ علي كتابه في المكتبة، ثم قال إن المبنى مبني على أساس متين. "
            "وأخبرنا أن استخدام هذا الاسم صحيح، وأن اسم الملف واضح."
        )
        self.assertEqual(check(text), [])

    def test_prefix_collisions_not_flagged(self):
        # Real words that contain a list entry after a prefix is stripped.
        text = (
            "كانت الشمس ساطعة وكانا معًا، وبانت الحقيقة ولانت قلوبهم. "
            "وفى بوعده، وكتب حرف الواو، وأصاب الجرح ورما، ووالى الأمير قومه. "
            "وزار الطالبَ مدرسه في البيت، وهذا كتابه. "
            "أنت فلذة كبدي، وكبدي يتألم."
        )
        self.assertEqual(check(text), [])

    def test_approved_never_flagged(self):
        self.assertEqual(
            check("يعتبر هذا من أهم الأبحاث، وأكد على ذلك المدراء في نفس الوقت، طالما أن"),
            [],
        )
        self.assertEqual(check("﴿إِنَّا أَعْطَيْنَاكَ﴾"), [])

    def test_every_approved_form_clean(self):
        for entry in sorted(load_list("approved_forms.txt")):
            with self.subTest(entry=entry):
                self.assertEqual(check(entry), [])

    def test_data_files_well_formed(self):
        approved = load_list("approved_forms.txt")
        seen = {}
        for name, key in _FILES.items():
            rows = load_tsv(name)
            self.assertGreater(len(rows), 0, name)
            other = "msa" if key == "word" else "right"
            for row in rows:
                with self.subTest(file=name, row=row):
                    self.assertTrue(row.get(key) and row.get(other))
                    self.assertNotEqual(row[key], row[other])
                    self.assertNotIn(row[key], approved)
                    self.assertNotIn(row[key], seen, "duplicate across lists")
                    seen[row[key]] = name

    def test_each_entry_is_flagged(self):
        for name, key in _FILES.items():
            for row in load_tsv(name):
                with self.subTest(file=name, entry=row[key]):
                    self.assertTrue(check(row[key]), row[key])


if __name__ == "__main__":
    unittest.main()
