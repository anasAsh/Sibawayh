import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "arabic-writing", "scripts", "check_arabic.py")
SEP = "--- arabic-check findings ---"
CLEAN = "ذهب الولد إلى المدرسة."
ENGLISH = "ذهب الولد إلى المدرسة وقرأ كتابا ثم Hello World جميل"


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.cwd = self._tmp.name

    def write(self, data, name="in.txt"):
        path = os.path.join(self.cwd, name)
        with open(path, "wb") as f:
            f.write(data if isinstance(data, bytes) else data.encode("utf-8"))
        return path

    def run_cli(self, *args, stdin=None):
        return subprocess.run(
            [sys.executable, SCRIPT] + list(args), cwd=self.cwd,
            input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_clean_text_exit_0(self):
        r = self.run_cli(self.write(CLEAN))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, b"")

    def test_findings_exit_1(self):
        r = self.run_cli(self.write("إستخدام"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("ERROR  hamza-wasl", r.stdout.decode("utf-8"))
        self.assertTrue(r.stdout.decode("utf-8").startswith("1:1  ERROR  hamza-wasl"))

    def test_fix_mode_output(self):
        r = self.run_cli("--fix", self.write("قال ، ثم"))
        out = r.stdout.decode("utf-8")
        self.assertTrue(out.startswith("قال، ثم"))
        self.assertIn(SEP, out)
        self.assertTrue(out.rstrip("\n").endswith("no findings"))
        self.assertEqual(r.returncode, 0)

    def test_fix_leaves_file_untouched(self):
        p = self.write("قال ، ثم")
        self.run_cli("--fix", p)
        with open(p, "rb") as f:
            self.assertEqual(f.read(), "قال ، ثم".encode("utf-8"))

    def test_fix_mode_remaining_findings_exit_1(self):
        r = self.run_cli("--fix", self.write("قال ، ثم إستخدام"))
        out = r.stdout.decode("utf-8")
        self.assertIn("hamza-wasl", out.split(SEP)[1])
        self.assertEqual(r.returncode, 1)

    def test_json(self):
        r = self.run_cli("--json", self.write("إسم"))
        raw = r.stdout.decode("utf-8")
        data = json.loads(raw)
        self.assertEqual(data["findings"][0]["rule"], "hamza-wasl")
        self.assertEqual(data["findings"][0]["text"], "إسم")
        self.assertEqual(set(data["findings"][0]),
                         {"line", "col", "severity", "rule", "message", "suggestion", "text"})
        self.assertNotIn("\\u", raw)
        self.assertNotIn("fixed_text", data)
        self.assertEqual(r.returncode, 1)

    def test_json_fix(self):
        r = self.run_cli("--json", "--fix", self.write("قال ، ثم"))
        data = json.loads(r.stdout.decode("utf-8"))
        self.assertEqual(data["fixed_text"], "قال، ثم")
        self.assertEqual(data["findings"], [])

    def test_stdin(self):
        r = self.run_cli("-", stdin="إستخدام".encode("utf-8"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("hamza-wasl", r.stdout.decode("utf-8"))

    def test_crlf_preserved(self):
        r = self.run_cli("--fix", self.write("قال ، ثم\r\nنعم".encode("utf-8")))
        out = r.stdout.decode("utf-8")
        self.assertTrue(out.startswith("قال، ثم\r\nنعم"))
        self.assertNotIn("\r\r", out)

    def test_crlf_line_numbers(self):
        r = self.run_cli(self.write("نعم\r\nإستخدام".encode("utf-8")))
        self.assertTrue(r.stdout.decode("utf-8").startswith("2:1  "))

    def test_empty_input(self):
        r = self.run_cli(self.write(""))
        self.assertEqual(r.returncode, 0)

    def test_missing_file(self):
        r = self.run_cli(os.path.join(self.cwd, "nope.txt"))
        self.assertEqual(r.returncode, 2)

    def test_invalid_utf8(self):
        r = self.run_cli(self.write(b"\xff\xfe\x00bad"))
        self.assertEqual(r.returncode, 2)

    def test_usage_error(self):
        r = self.run_cli("--digits", "bogus", self.write(CLEAN))
        self.assertEqual(r.returncode, 2)

    def test_info_only_exit_0(self):
        r = self.run_cli(self.write(ENGLISH))
        self.assertEqual(r.returncode, 0)
        self.assertIn("INFO  stray-english", r.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
