import os
import re
import unittest

from archeck.engine import check

_GLOSSARY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "arabic-writing", "references", "glossary.md",
)

_SEP_RE = re.compile(r"\|[\s:|-]+\|")
# Rules that legitimately fire on a lone table cell (a Latin acronym in the
# Arabic column, or a cell that starts with one).
_IGNORED_RULES = {"rtl-line-start", "stray-english"}


def glossary_rows():
    """(English, Arabic, Notes) for every data row of the glossary table."""
    with open(_GLOSSARY, encoding="utf-8") as f:
        lines = f.read().splitlines()
    rows = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s.startswith("|") or _SEP_RE.fullmatch(s):
            continue
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if _SEP_RE.fullmatch(nxt):
            continue  # header row
        cells = [c.strip() for c in s.strip("|").split("|")]
        rows.append(cells)
    return rows


class GlossaryTest(unittest.TestCase):
    def setUp(self):
        self.rows = glossary_rows()

    def test_three_columns(self):
        for cells in self.rows:
            self.assertEqual(len(cells), 3, cells)
            self.assertTrue(cells[0] and cells[1], cells)

    def test_row_count(self):
        self.assertGreaterEqual(len(self.rows), 200)

    def test_unique_english(self):
        seen = {}
        for cells in self.rows:
            key = cells[0].lower()
            self.assertNotIn(key, seen, "duplicate English term: " + cells[0])
            seen[key] = True

    def test_sorted_by_english(self):
        keys = [cells[0].lower() for cells in self.rows]
        self.assertEqual(keys, sorted(keys))

    def test_arabic_column_clean(self):
        problems = []
        for cells in self.rows:
            arabic = cells[1]
            for f in check(arabic):
                if f.severity in ("error", "warn") and f.rule not in _IGNORED_RULES:
                    problems.append("%s | %s -> %s: %s" % (
                        cells[0], arabic, f.rule, arabic[f.start:f.end]))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_house_spelling(self):
        # Conventions the checker reports only as fix/info on a lone cell.
        bad = re.compile("ـ|مسئول|مائة|اً|[۰-۹]")
        for cells in self.rows:
            for cell in cells[1:]:
                self.assertIsNone(bad.search(cell), cells)


if __name__ == "__main__":
    unittest.main()
