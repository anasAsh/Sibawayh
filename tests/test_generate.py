import subprocess
import unittest
from unittest import mock

from evals import generate


class RunOneTests(unittest.TestCase):
    def cmd_for(self, with_skill):
        done = subprocess.CompletedProcess([], 0, stdout="نص", stderr="")
        with mock.patch.object(generate.subprocess, "run",
                               return_value=done) as run:
            generate.run_one("اكتب", with_skill)
        return run.call_args[0][0]

    def test_same_allowed_tools_in_both_modes(self):
        base, skill = self.cmd_for(False), self.cmd_for(True)
        self.assertEqual(base, skill)
        i = base.index("--allowedTools")
        self.assertEqual(base[i + 1], generate.c.ALLOWED_TOOLS)
        # The prompt must come before the variadic --allowedTools.
        self.assertLess(base.index("اكتب"), i)


if __name__ == "__main__":
    unittest.main()
