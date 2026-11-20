import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "evals"))
import inject  # noqa: E402


def corruptor(name):
    return next(c for c in inject.CORRUPTORS if c.name == name)


class InjectTest(unittest.TestCase):
    def test_no_op_replacements_are_not_sites(self):
        lines = inject.doc_lines("في السنة ٢٠٢٤ سجلنا ١٠ حالات جديدة")
        self.assertEqual(inject.sites(lines, corruptor("digit-mix")), [])

    def test_lines_inside_a_code_fence_are_masked(self):
        text = "```text\nهذا مثال برمجي فيه مدرسة\n```\nهذه جملة عن مدرسة كبيرة"
        found = inject.sites(inject.doc_lines(text), corruptor("taa-haa"))
        self.assertEqual({s.line for s in found}, {"هذه جملة عن مدرسة كبيرة"})


if __name__ == "__main__":
    unittest.main()
