import os
import re
import unittest

from archeck import engine

_SKILL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "arabic-writing",
)
_SKILL_MD = os.path.join(_SKILL_DIR, "SKILL.md")

_ARABIC_RE = re.compile("[؀-ۿ]")
# SKILL.md is English prose with Arabic examples, so these two rules do not apply.
_IGNORED_RULES = {"rtl-line-start", "stray-english"}


def read_skill():
    with open(_SKILL_MD, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None


class TestSkillMd(unittest.TestCase):
    def test_frontmatter(self):
        text = read_skill()
        self.assertTrue(text.startswith("---\n"))
        fm = frontmatter(text)
        self.assertIsNotNone(fm, "no closing --- for the front matter")
        self.assertRegex(fm, r"(?m)^name: arabic-writing$")
        m = re.search(r"(?m)^description: (.+)$", fm)
        self.assertIsNotNone(m, "description must be a single line")
        desc = m.group(1)
        self.assertLessEqual(len(desc), 1024)
        self.assertIn("Arabic", desc)
        for kw in ("عربي", "العربية", "فصحى"):
            self.assertIn(kw, desc)
        # Arabic task verbs: a bare "لخّص …" request must load the skill.
        for kw in ("لخّص", "أعد صياغة", "صحّح", "راجع", "حرّر", "أجب"):
            self.assertIn(kw, desc)
        for kw in ("summar", "rewrit", "proofread", "review", "edit"):
            self.assertIn(kw, desc.lower())
        # Dialect requests load the skill for its formatting checks.
        for kw in ("عامية", "لهجة"):
            self.assertIn(kw, desc)
        self.assertIn("Do not use for English-only work", desc)

    def test_length(self):
        self.assertLessEqual(len(read_skill().splitlines()), 250)

    def test_sections_in_order(self):
        text = read_skill()
        heads = ["## Scope", "## Writing rules", "## Workflow",
                 "## Self-review checklist", "## References"]
        positions = [text.find(h) for h in heads]
        self.assertNotIn(-1, positions, dict(zip(heads, positions)))
        self.assertEqual(positions, sorted(positions))

    def test_checklist_has_seven_items_in_order(self):
        text = read_skill()
        section = text.split("## Self-review checklist", 1)[1].split("\n## ", 1)[0]
        items = re.findall(r"(?m)^(\d+)\. \*\*([^*]+)\*\*", section)
        self.assertEqual([int(n) for n, _ in items], list(range(1, 8)))
        expected = ["Agreement", "Numbers", "Visible endings", "إنّ",
                    "Translationese", "Register", "Formatting"]
        for (_, title), word in zip(items, expected):
            self.assertIn(word, title)
        self.assertIn("Change only what is wrong", section)

    def test_workflow_command(self):
        text = read_skill()
        self.assertIn("python3 <skill-dir>/scripts/check_arabic.py --fix", text)

    def test_workflow_dialect_mode(self):
        text = read_skill()
        step3 = text.split("3. **Read the output.**", 1)[1].split("\n4. ", 1)[0]
        bullet = [l for l in step3.splitlines() if "dialect" in l]
        self.assertEqual(len(bullet), 1, step3)
        for word in ("`fix`", "digit-mix", "rtl-line-start", "dialect-word",
                     "hamza", "misspelling", "grammar", "item 7"):
            self.assertIn(word, bullet[0])
        skipped = [l for l in step3.splitlines() if "checker skips" in l]
        self.assertEqual(len(skipped), 1)
        self.assertIn("emails", skipped[0])

    def test_referenced_files_exist(self):
        text = read_skill()
        paths = set(re.findall(r"(?:references|scripts)/[\w./-]+\.(?:md|py)", text))
        self.assertTrue(paths)
        for p in paths:
            self.assertTrue(os.path.isfile(os.path.join(_SKILL_DIR, p)), p)
        for name in ("grammar", "orthography", "style", "common-errors",
                     "approved-forms", "glossary"):
            self.assertIn("references/%s.md" % name, text)

    def test_arabic_examples_clean(self):
        for n, line in enumerate(read_skill().splitlines(), 1):
            if not _ARABIC_RE.search(line) or "✗" in line:
                continue
            bad = [f for f in engine.check(line)
                   if f.severity in ("error", "warn") and f.rule not in _IGNORED_RULES]
            self.assertEqual(
                bad, [], "line %d: %s\n%s" % (
                    n, line, [(f.rule, line[f.start:f.end], f.message) for f in bad]))


if __name__ == "__main__":
    unittest.main()
