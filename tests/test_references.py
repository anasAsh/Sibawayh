import os
import re
import unittest

from archeck.data import load_list
from archeck.text import iter_words

_REF_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "arabic-writing", "references",
)

# File -> maximum line count (task 7 brief; the last two are this task's own caps).
_LIMITS = {
    "grammar.md": 300,
    "orthography.md": 250,
    "style.md": 200,
    "common-errors.md": 200,
    "approved-forms.md": 200,
}

_DIACRITICS_RE = re.compile("[ً-ٰٟ]")


def read(name):
    with open(os.path.join(_REF_DIR, name), encoding="utf-8") as f:
        return f.read()


def table_rows(text):
    """Cells of every Markdown table body row (header and separator skipped)."""
    rows = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]+\|", s):
            continue
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if re.fullmatch(r"\|[\s:|-]+\|", nxt):
            continue  # header row
        rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows


def arabic_words(cell):
    return [_DIACRITICS_RE.sub("", w) for _, _, w in iter_words(cell)]


class ReferencesTest(unittest.TestCase):
    def test_files_exist_and_sized(self):
        for name, limit in _LIMITS.items():
            with self.subTest(file=name):
                n = len(read(name).splitlines())
                self.assertGreater(n, 20)
                self.assertLessEqual(n, limit)

    def test_each_file_opens_with_when_to_read(self):
        for name in _LIMITS:
            with self.subTest(file=name):
                lines = [l for l in read(name).splitlines() if l.strip()]
                self.assertTrue(lines[0].startswith("# "))
                self.assertTrue(lines[1].startswith("Read this "), lines[1])

    def test_approved_lists_in_sync(self):
        approved = load_list("approved_forms.txt")
        rows = table_rows(read("approved-forms.md"))
        self.assertGreater(len(rows), 30)
        for row in rows:
            words = arabic_words(row[0])
            with self.subTest(row=row[0]):
                self.assertTrue(words, "first column has no Arabic form")
                for w in words:
                    self.assertIn(w, approved)

    def test_approved_forms_names_contested(self):
        text = read("approved-forms.md")
        for form in ("طالما", "بينما", "سويًّا"):
            self.assertIn(form, text)

    def test_common_errors_not_approved(self):
        approved = load_list("approved_forms.txt")
        rows = table_rows(read("common-errors.md"))
        self.assertGreater(len(rows), 30)
        for row in rows:
            with self.subTest(row=row[0]):
                self.assertTrue(row[0].startswith("✗"), row[0])
                self.assertTrue(row[1].startswith("✓"), row[1])
                for w in arabic_words(row[0]):
                    self.assertNotIn(w, approved)

    def test_common_errors_omit_contested(self):
        rows = table_rows(read("common-errors.md"))
        wrong = " ".join(r[0] for r in rows)
        for form in ("طالما", "بينما", "سويا", "كافة", "هام", "تواجد", "مؤخرا"):
            self.assertNotIn(form, arabic_words(wrong))

    def test_style_states_density_principle(self):
        self.assertIn("judge density, don't ban", read("style.md").lower())

    def test_conventions_in_correct_examples(self):
        # ✓ text never uses the non-default spellings the skill avoids.
        for name in _LIMITS:
            for line in read(name).splitlines():
                if "✗" in line:
                    continue
                with self.subTest(file=name, line=line):
                    self.assertNotRegex(line, "مسئول|مائة|[۰-۹]")
                    self.assertNotRegex(line, "[ء-ي]اً")  # اً


if __name__ == "__main__":
    unittest.main()
