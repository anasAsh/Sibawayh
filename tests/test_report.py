import os
import tempfile
import unittest

from evals import report

CATS = ["grammar", "spelling", "translationese", "register", "formatting"]


def rates(total_each, **over):
    d = {c: total_each for c in CATS}
    d.update(over)
    d["total"] = sum(d[c] for c in CATS)
    return d


class VerdictTests(unittest.TestCase):
    def base(self):
        return {
            "baseline": {"grammar": 3.0, "spelling": 3.0, "translationese": 2.0,
                         "register": 1.0, "formatting": 1.0, "total": 10.0},
            "skill": {"grammar": 1.0, "spelling": 1.0, "translationese": 1.0,
                      "register": 0.5, "formatting": 0.5, "total": 4.0},
        }

    def test_verdict_pass(self):
        self.assertEqual(report.verdict(self.base(), 0), (True, []))

    def test_verdict_fail_overcorrection(self):
        ok, reasons = report.verdict(self.base(), 1)
        self.assertFalse(ok)
        self.assertTrue(any("over-correction" in r for r in reasons))

    def test_verdict_fail_category_worse(self):
        r = self.base()
        r["skill"]["formatting"] = 1.5
        r["skill"]["total"] = 4.5
        ok, reasons = report.verdict(r, 0)
        self.assertFalse(ok)
        self.assertTrue(any("formatting" in x for x in reasons))

    def test_verdict_fail_drop_too_small(self):
        r = self.base()
        r["skill"] = {"grammar": 2.0, "spelling": 1.0, "translationese": 1.0,
                      "register": 1.0, "formatting": 1.0, "total": 6.0}
        ok, reasons = report.verdict(r, 0)
        self.assertFalse(ok)
        self.assertTrue(any("50%" in x for x in reasons))

    def test_exactly_half_passes(self):
        r = self.base()
        r["skill"] = {"grammar": 1.5, "spelling": 1.5, "translationese": 1.0,
                      "register": 0.5, "formatting": 0.5, "total": 5.0}
        self.assertTrue(report.verdict(r, 0)[0])


class RubricRatesTests(unittest.TestCase):
    def test_rubric_rates(self):
        rows = [
            {"mode": "baseline", "words": 100, "grammar": 2, "spelling": 1,
             "translationese": 0, "register": 0, "formatting": 1},
            {"mode": "baseline", "words": 100, "grammar": 0, "spelling": 1,
             "translationese": 2, "register": 0, "formatting": 0},
            {"mode": "skill", "words": 200, "grammar": 1, "spelling": 0,
             "translationese": 0, "register": 1, "formatting": 0},
        ]
        r = report.rubric_rates(rows)
        self.assertAlmostEqual(r["baseline"]["grammar"], 1.0)
        self.assertAlmostEqual(r["baseline"]["spelling"], 1.0)
        self.assertAlmostEqual(r["baseline"]["translationese"], 1.0)
        self.assertAlmostEqual(r["baseline"]["total"], 3.5)
        self.assertAlmostEqual(r["skill"]["grammar"], 0.5)
        self.assertAlmostEqual(r["skill"]["total"], 1.0)

    def test_blank_counts_are_skipped(self):
        rows = [
            {"mode": "skill", "words": 100, "grammar": "", "spelling": "",
             "translationese": "", "register": "", "formatting": ""},
            {"mode": "skill", "words": 100, "grammar": 2, "spelling": 0,
             "translationese": 0, "register": 0, "formatting": 0},
        ]
        r = report.rubric_rates(rows)
        self.assertAlmostEqual(r["skill"]["grammar"], 2.0)


class TextTests(unittest.TestCase):
    def test_words(self):
        self.assertEqual(report.words("مرحبا بكم in Cairo، اليوم"), 3)

    def test_checker_counts_families(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("ذهبت الى المدرسة, ثم عدت\n")
            c = report.checker_counts(p)
        self.assertEqual(set(c), {"punctuation", "spelling", "grammar",
                                  "style", "formatting"})
        self.assertGreaterEqual(c["punctuation"], 1)

    def test_load_rubric_blind_key(self):
        with tempfile.TemporaryDirectory() as d:
            rub = os.path.join(d, "r.csv")
            key = os.path.join(d, "k.csv")
            with open(key, "w", encoding="utf-8") as f:
                f.write("blind_id,id,mode\nabc123,email-01,skill\n")
            with open(rub, "w", encoding="utf-8") as f:
                f.write("id,mode,grammar,spelling,translationese,register,"
                        "formatting,over_corrections,notes\n"
                        "abc123,,1,0,0,0,0,0,\n")
            rows = report.load_rubric(rub, key)
        self.assertEqual(rows[0]["id"], "email-01")
        self.assertEqual(rows[0]["mode"], "skill")


if __name__ == "__main__":
    unittest.main()


class RubricValidationTests(unittest.TestCase):
    def row(self, **kw):
        r = {"id": "email-01", "mode": "skill", "grammar": "1", "spelling": "0",
             "translationese": "0", "register": "0", "formatting": "0",
             "over_corrections": "0"}
        r.update(kw)
        return r

    def test_all_blank_is_unscored(self):
        r = self.row(grammar="", spelling="", translationese="", register="",
                     formatting="", over_corrections="")
        self.assertEqual(report.check_rows([r]), [])

    def test_partly_filled_names_row(self):
        errs = report.check_rows([self.row(spelling="")])
        self.assertTrue(any("email-01/skill" in e and "spelling" in e
                            for e in errs))

    def test_skill_row_needs_over_corrections(self):
        errs = report.check_rows([self.row(over_corrections="")])
        self.assertTrue(any("over_corrections" in e for e in errs))
        self.assertEqual(report.check_rows(
            [self.row(mode="baseline", over_corrections="")]), [])

    def test_unresolved_blind_id_named(self):
        with tempfile.TemporaryDirectory() as d:
            rub = os.path.join(d, "r.csv")
            with open(rub, "w", encoding="utf-8") as f:
                f.write("id,mode,grammar,spelling,translationese,register,"
                        "formatting,over_corrections,notes\n"
                        "zzz999,,1,0,0,0,0,0,\n")
            for key in (None, os.path.join(d, "missing.csv")):
                rows = report.load_rubric(rub, key)
                errs = report.check_rows(rows)
                self.assertTrue(any("zzz999" in e for e in errs))
                self.assertNotIn("", report.rubric_rates(
                    [dict(r, words=100) for r in rows]))

    def test_missing_output_file_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                report._words_for(d, self.row())

    def test_main_exits_nonzero_before_verdict(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            rub = os.path.join(d, "r.csv")
            with open(rub, "w", encoding="utf-8") as f:
                f.write("id,mode,grammar,spelling,translationese,register,"
                        "formatting,over_corrections,notes\n"
                        "email-01,skill,1,,,,,,\n")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(err):
                rc = report.main(["--rubric", rub, "--outputs", d,
                                  "--key", os.path.join(d, "none.csv")])
        self.assertEqual(rc, 2)
        self.assertNotIn("PASS", out.getvalue())
        self.assertNotIn("FAIL", out.getvalue())
        self.assertIn("email-01/skill", err.getvalue())
