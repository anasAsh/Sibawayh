#!/usr/bin/env python3
"""Check whether the skill loads for each prompt in triggers.tsv.

  python3 evals/run_triggers.py [--limit N]

A load is an assistant tool_use block named Skill whose input.skill is
arabic-writing, in `claude -p --output-format stream-json --verbose` output.
`format_only` rows are judged manually for behaviour (the skill should only
fix formatting, not rewrite dialect), but count as `load` for the automated
check, because the skill still loads.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402


def skill_loaded(stream: str) -> bool:
    for line in stream.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") != "assistant":
            continue
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if (isinstance(b, dict) and b.get("type") == "tool_use"
                    and b.get("name") == "Skill"
                    and (b.get("input") or {}).get("skill") == "arabic-writing"):
                return True
    return False


def has_result(stream: str) -> bool:
    for line in stream.splitlines():
        try:
            if json.loads(line).get("type") == "result":
                return True
        except (ValueError, AttributeError):
            continue
    return False


def classify(returncode, stream: str, expected: str):
    """Return (loaded, "pass"|"FAIL"|"ERROR"). ERROR means the run itself
    failed (non-zero exit or no result event), so loaded is unknown."""
    if returncode != 0 or not has_result(stream):
        return None, "ERROR"
    loaded = skill_loaded(stream)
    return loaded, ("pass" if loaded == expected_load(expected) else "FAIL")


def expected_load(expected: str) -> bool:
    return expected in ("load", "format_only")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    a = ap.parse_args(argv)
    c.refuse_if_globally_installed()

    rows = c.read_tsv(os.path.join(c.HERE, "triggers.tsv"))
    if a.limit:
        rows = rows[:a.limit]
    print("| id | expected | loaded | result |\n|---|---|---|---|")
    passed = errors = 0
    for r in rows:
        try:
            with c.workdir(True) as d:
                p = subprocess.run(
                    ["claude", "-p", r["prompt"], "--output-format",
                     "stream-json", "--verbose", "--allowedTools",
                     c.ALLOWED_TOOLS],
                    cwd=d, capture_output=True, text=True, encoding="utf-8",
                    timeout=c.TIMEOUT)
            loaded, res = classify(p.returncode, p.stdout, r["expected"])
        except Exception as e:
            loaded, res = None, "ERROR"
        passed += res == "pass"
        errors += res == "ERROR"
        print("| %s | %s | %s | %s |" % (r["id"], r["expected"], loaded, res))
    print("\n%d/%d passed, %d error(s) (errors excluded from passes)"
          % (passed, len(rows), errors))
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
