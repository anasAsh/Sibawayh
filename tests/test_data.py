import os
import tempfile
import unittest

from archeck import data
from archeck.data import load_list, load_tsv


class DataTest(unittest.TestCase):
    def test_approved_forms_loaded(self):
        self.assertTrue({"يعتبر", "أبحاث", "مدراء"} <= load_list("approved_forms.txt"))

    def test_item55_and_purist_plural(self):
        forms = load_list("approved_forms.txt")
        self.assertTrue({"نفس", "ذات"} <= forms)
        self.assertNotIn("أبحر", forms)

    def test_comments_skipped(self):
        for e in load_list("approved_forms.txt") | load_list("acronyms.txt"):
            self.assertFalse(e.startswith("#"))
            self.assertTrue(e)
        self.assertIn("API", load_list("acronyms.txt"))

    def test_load_tsv_and_list_parsing(self):
        old = data.DATA_DIR
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "s.tsv"), "w", encoding="utf-8") as f:
                f.write("# c\na\tb\n\n1\t2\n# x\n3\t4\nمسؤول\tx\n")
            with open(os.path.join(d, "s.txt"), "w", encoding="utf-8") as f:
                f.write("# c\n\nأ\n  ب  \nأ\n")
            data.DATA_DIR = d
            data.load_tsv.cache_clear()
            data.load_list.cache_clear()
            try:
                self.assertEqual(
                    load_tsv("s.tsv"),
                    [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}, {"a": "مسؤول", "b": "x"}],
                )
                self.assertEqual(load_list("s.txt"), frozenset({"أ", "ب"}))
            finally:
                data.DATA_DIR = old
                data.load_tsv.cache_clear()
                data.load_list.cache_clear()
