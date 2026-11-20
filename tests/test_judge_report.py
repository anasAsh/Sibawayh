import contextlib
import io
import os
import tempfile
import unittest

from evals import judge_report as jr


class JudgeReportTest(unittest.TestCase):
    def run_report(self, scores, key):
        d = tempfile.mkdtemp()
        for mode in ("baseline", "skill"):
            os.makedirs(os.path.join(d, "outputs", mode))
            with open(os.path.join(d, "outputs", mode, "email-01.txt"), "w", encoding="utf-8") as f:
                f.write(" ".join(["كلمة"] * 100))
        sp, kp = os.path.join(d, "s.csv"), os.path.join(d, "k.csv")
        with open(sp, "w", encoding="utf-8") as f:
            f.write(scores)
        with open(kp, "w", encoding="utf-8") as f:
            f.write(key)
        old, jr.HERE = jr.HERE, d
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                jr.main([sp, kp])
        finally:
            jr.HERE = old
        return out.getvalue()

    HEAD = "pair,response,grammar,spelling,translationese,register,formatting,over_corrections\n"
    KEY = "pair,id,a,b\n01,email-01,skill,baseline\n"

    def test_unblinds_and_passes(self):
        out = self.run_report(self.HEAD + "01,A,0,0,1,0,0,0\n01,B,2,0,2,0,0,\n01,pref,A,,,,,\n",
                              self.KEY)
        self.assertIn("Preferred: skill 1, baseline 0, tie 0", out)
        self.assertIn("PASS", out)

    def test_worse_category_fails(self):
        out = self.run_report(self.HEAD + "01,A,0,0,0,0,1,0\n01,B,4,0,0,0,0,\n", self.KEY)
        self.assertIn("FAIL", out)
        self.assertIn("worse: formatting", out)


if __name__ == "__main__":
    unittest.main()
