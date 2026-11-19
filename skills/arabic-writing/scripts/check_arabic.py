#!/usr/bin/env python3
"""Command-line Arabic text checker. Standard library only."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from archeck import engine  # noqa: E402
from archeck.text import line_col  # noqa: E402

SEPARATOR = "--- arabic-check findings ---"


def _read(path):
    if path == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as f:
            data = f.read()
    # Decode bytes directly so "\r\n" is preserved (no newline translation).
    return data.decode("utf-8")


def _write(s):
    sys.stdout.buffer.write(s.encode("utf-8"))
    sys.stdout.buffer.flush()


def _rows(text, findings):
    rows = []
    for f in findings:
        line, col = line_col(text, f.start)
        rows.append({
            "line": line, "col": col, "severity": f.severity, "rule": f.rule,
            "message": f.message, "suggestion": f.suggestion,
            "text": text[f.start:f.end],
        })
    return rows


def _format(rows):
    out = []
    for r in rows:
        s = "{line}:{col}  {sev}  {rule}  {message}".format(
            line=r["line"], col=r["col"], sev=r["severity"].upper(),
            rule=r["rule"], message=r["message"])
        if r["suggestion"]:
            s += "  → " + r["suggestion"]
        out.append(s + "\n")
    return "".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="check_arabic.py", description="Check Arabic text for common errors.")
    p.add_argument("--fix", action="store_true",
                   help="apply safe fixes and print the fixed text")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--digits", choices=("western", "arabic", "auto"), default="auto",
                   help="digit convention (default: auto)")
    p.add_argument("file", metavar="FILE|-", help="file to check, or - for stdin")
    args = p.parse_args(argv)

    try:
        text = _read(args.file)
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write("check_arabic.py: cannot read {}: {}\n".format(args.file, e))
        return 2

    fixed = None
    if args.fix:
        fixed = engine.fix_text(text, digits=args.digits)
        text = fixed
    findings = engine.check(text, digits=args.digits)
    rows = _rows(text, findings)

    if args.json:
        payload = {"findings": rows}
        if fixed is not None:
            payload["fixed_text"] = fixed
        _write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    elif fixed is not None:
        _write(fixed)
        if not fixed.endswith("\n"):
            _write("\n")
        _write(SEPARATOR + "\n")
        _write(_format(rows) if rows else "no findings\n")
    else:
        _write(_format(rows))

    return 1 if any(f.severity in ("fix", "error", "warn") for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
