#!/usr/bin/env python3
"""Over-correction check: run the checker on edited, correct Arabic and
count what it flags. On clean text every error or fix is a false flag
until a human confirms it as a real error.

Usage: python3 evals/corpus_check.py [--samples 5] [--min-severity warn]
                                     PATH [PATH ...]
PATH is a .txt/.md file or a directory of them.
"""
import argparse
import os
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "skills", "sibawayeh", "scripts"))

from archeck.engine import check  # noqa: E402
from archeck.text import iter_words, mask  # noqa: E402

SEVERITIES = ["info", "warn", "error", "fix"]
CONTEXT = 30


def files(paths: List[str]) -> List[str]:
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += sorted(os.path.join(p, n) for n in os.listdir(p)
                          if n.endswith((".txt", ".md")))
        else:
            out.append(p)
    return out


def snippet(text: str, start: int, end: int) -> str:
    a, b = max(0, start - CONTEXT), min(len(text), end + CONTEXT)
    s = text[a:start] + "[[" + text[start:end] + "]]" + text[end:b]
    return " ".join(s.split())


def scan(paths: List[str], min_severity: str) -> Tuple[int, Dict, Dict]:
    """Return (words, counts by (rule, severity), samples by rule)."""
    floor = SEVERITIES.index(min_severity)
    words, counts, samples = 0, defaultdict(int), defaultdict(list)
    for path in files(paths):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        words += sum(1 for _ in iter_words(mask(text)))
        for fd in check(text):
            if SEVERITIES.index(fd.severity) < floor:
                continue
            counts[(fd.rule, fd.severity)] += 1
            samples[fd.rule].append(
                "%s: %s" % (os.path.basename(path), snippet(text, fd.start, fd.end)))
    return words, counts, samples


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("paths", nargs="+")
    p.add_argument("--samples", type=int, default=5)
    p.add_argument("--min-severity", choices=SEVERITIES, default="warn")
    args = p.parse_args()
    words, counts, samples = scan(args.paths, args.min_severity)
    if not words:
        sys.exit("No Arabic words found in %s" % " ".join(args.paths))
    print("%d files, %d Arabic words\n" % (len(files(args.paths)), words))
    print("%-26s %-6s %7s %12s" % ("rule", "sev", "count", "per 10k words"))
    for (rule, sev), n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("%-26s %-6s %7d %12.1f" % (rule, sev, n, n * 10000.0 / words))
    for rule in sorted(samples) if args.samples else []:
        print("\n## %s" % rule)
        for s in samples[rule][:args.samples]:
            print("  " + s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
