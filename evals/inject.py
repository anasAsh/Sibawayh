#!/usr/bin/env python3
"""Recall check: inject one known error into a line of clean Arabic, run
the checker, and see whether a finding covers the injected error.

Usage: python3 evals/inject.py [--sites 200] [--seed 1] [--samples 3]
                               PATH [PATH ...]
PATH is a .txt/.md file or a directory of them (see fetch_wiki.py).
"""
import argparse
import os
import random
import re
import sys
from collections import Counter
from typing import Callable, List, NamedTuple, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from corpus_check import files  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "skills", "sibawayeh", "scripts"))
from archeck.engine import check, fix_text  # noqa: E402
from archeck.text import mask  # noqa: E402

L = "ء-ي"  # Arabic letters
NB = "(?<![%s])" % L  # no Arabic letter before
NA = "(?![%s])" % L  # no Arabic letter after
_AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


class Corruptor(NamedTuple):
    name: str
    pattern: "re.Pattern"
    repl: Callable[["re.Match"], str]
    line_ok: Callable[[str], bool] = lambda line: True


def _const(s):
    return lambda m: s


CORRUPTORS = [
    Corruptor("punct-latin", re.compile("[،؛؟]"),
              lambda m: {"،": ",", "؛": ";", "؟": "?"}[m.group()]),
    Corruptor("punct-space", re.compile("(?<=[%s])،(?= )" % L), _const(" ،")),
    # Bare alif of a form VII, VIII or X verb or masdar written as إ.
    Corruptor("hamza-wasl", re.compile(
        NB + "((?:[وفبل]|[وفب]?ال|لل)?)ا(?=(?:ست|ن[فطقسكشضحخعجب]|[جحخعقكمز]ت|ت[خجصفحس]|ثن)[%s])" % L),
        lambda m: m.group(1) + "إ"),
    Corruptor("hamza-qat", re.compile(NB + "([وفبل]?)[أإ](?=[%s]{2,})" % L),
              lambda m: m.group(1) + "ا"),
    Corruptor("taa-haa", re.compile("(?<=[%s])ة" % L + NA), _const("ه")),
    Corruptor("alif-maqsura→ي", re.compile("(?<=[%s])ى" % L + NA), _const("ي")),
    Corruptor("ي→alif-maqsura", re.compile("(?<=[%s])ي" % L + NA), _const("ى")),
    Corruptor("persian-letter", re.compile("(?<=[%s])ك(?=[%s])" % (L, L)), _const("ک")),
    Corruptor("tatweel", re.compile("(?<=[بتثجحخسشصضطظعغفقكلمنهي])(?=[%s])" % L), _const("ـ")),
    Corruptor("digit-mix", re.compile(r"(?<![\d.,])[0-9]+(?![\d.,])"),
              lambda m: m.group().translate(_AR_DIGITS),
              lambda line: len(re.findall(r"\d+", line)) >= 2),
    Corruptor("jussive-nun", re.compile(
        NB + "((?:لم|لن|أن|كي|لكي) [يت][%s]+)وا" % L + NA),
        lambda m: m.group(1) + "ون"),
    Corruptor("sawfa-lan", re.compile(NB + "لن(?= [يتنأ])"), _const("سوف لن")),
    Corruptor("common-misspelling", re.compile(NB + "(هذا|لكن|ذلك)" + NA),
              lambda m: {"هذا": "هاذا", "لكن": "لاكن", "ذلك": "ذالك"}[m.group()]),
]


class Site(NamedTuple):
    line: str
    start: int
    end: int
    repl: str


def doc_lines(text: str) -> List[Tuple[str, str]]:
    """(line, masked line) pairs. The whole document is masked first, so a
    line inside a code fence is masked too."""
    return list(zip(text.split("\n"), mask(text).split("\n")))


def sites(lines: List[Tuple[str, str]], c: Corruptor) -> List[Site]:
    out = []
    for line, masked in lines:
        if not c.line_ok(line):
            continue
        for m in c.pattern.finditer(line):
            if masked[m.start():m.end()] != line[m.start():m.end()]:
                continue  # inside code, a URL or another skipped region
            repl = c.repl(m)
            if repl == m.group():
                continue  # no change (a number already in Arabic-Indic digits)
            out.append(Site(line, m.start(), m.end(), repl))
    return out


def corrupt(s: Site) -> str:
    return s.line[:s.start] + s.repl + s.line[s.end:]


def covering(text: str, a: int, b: int) -> List[str]:
    """Rules of non-info findings that overlap or touch [a, b]."""
    return [f.rule for f in check(text)
            if f.severity != "info" and f.start <= b and f.end >= a]


class Result(NamedTuple):
    detected: Optional[str]  # the rule that caught it, or None
    restored: bool  # --fix gives back the clean line (after its own fixes)


def evaluate(s: Site) -> Optional[Result]:
    """None if the clean line already has a finding at this spot."""
    a, b = s.start, s.start + len(s.repl)
    if covering(s.line, s.start, s.end):
        return None
    bad = corrupt(s)
    rules = covering(bad, a, b)
    return Result(rules[0] if rules else None, fix_text(bad) == fix_text(s.line))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("paths", nargs="+")
    p.add_argument("--sites", type=int, default=200, help="sites per error type")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--samples", type=int, default=3, help="missed examples to print")
    args = p.parse_args()
    lines = []
    for path in files(args.paths):
        with open(path, encoding="utf-8") as f:
            lines += [lm for lm in doc_lines(f.read()) if len(lm[0].split()) >= 5]
    rng = random.Random(args.seed)
    print("%-20s %6s %9s %8s %9s  %s" % ("error type", "sites", "detected", "recall",
                                       "restored", "caught by"))
    misses = {}
    for c in CORRUPTORS:
        cands = sites(lines, c)
        pick = rng.sample(cands, min(args.sites, len(cands)))
        results = [(s, r) for s in pick for r in [evaluate(s)] if r is not None]
        n = len(results)
        hit = [r for _, r in results if r.detected]
        by = Counter(r.detected for r in hit)
        restored = sum(r.restored for _, r in results)
        misses[c.name] = [s for s, r in results if not r.detected]
        print("%-20s %6d %9d %7.0f%% %8.0f%%  %s" % (
            c.name, n, len(hit), 100.0 * len(hit) / n if n else 0,
            100.0 * restored / n if n else 0,
            ", ".join("%s %d" % kv for kv in by.most_common(3))))
    for name, ms in misses.items():
        if ms and args.samples:
            print("\n## missed: %s" % name)
            for s in ms[:args.samples]:
                a, b = max(0, s.start - 25), s.start + len(s.repl) + 25
                bad = corrupt(s)
                print("  " + " ".join((bad[a:s.start] + "[[" + s.repl + "]]" +
                                       bad[s.start + len(s.repl):b]).split()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
