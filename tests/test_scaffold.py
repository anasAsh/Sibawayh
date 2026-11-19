import unittest


class ScaffoldTest(unittest.TestCase):
    def test_archeck_importable(self):
        import archeck  # noqa: F401


if __name__ == "__main__":
    unittest.main()
