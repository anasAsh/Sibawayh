import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "evals"))
import run_triggers as rt  # noqa: E402


def stream(loaded, result=True):
    ev = [{"type": "system", "subtype": "init"}]
    if loaded:
        ev.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill",
             "input": {"skill": "sibawayeh"}}]}})
    if result:
        ev.append({"type": "result"})
    return "\n".join(json.dumps(e) for e in ev)


class ClassifyTests(unittest.TestCase):
    def test_pass_and_fail(self):
        self.assertEqual(rt.classify(0, stream(True), "load"), (True, "pass"))
        self.assertEqual(rt.classify(0, stream(False), "load"),
                         (False, "FAIL"))
        self.assertEqual(rt.classify(0, stream(False), "no_load"),
                         (False, "pass"))
        self.assertEqual(rt.classify(0, stream(True), "format_only")[1],
                         "pass")

    def test_nonzero_exit_is_error(self):
        self.assertEqual(rt.classify(1, stream(True), "load"), (None, "ERROR"))

    def test_no_result_event_is_error(self):
        self.assertEqual(rt.classify(0, stream(False, result=False),
                                     "no_load"), (None, "ERROR"))
        self.assertEqual(rt.classify(0, "", "load"), (None, "ERROR"))


if __name__ == "__main__":
    unittest.main()
