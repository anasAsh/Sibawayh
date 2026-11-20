#!/usr/bin/env python3
"""Score the checker on essays that people corrected by hand (ZAEBUC, in
ARETA's token-aligned format: source word, corrected word, error tag).

Recall: share of erroneous tokens that a finding covers, per ARETA tag.
False alarms: findings on tokens the annotators left unchanged. Some of these
are errors the annotators missed, so they are listed for review.

Usage: python3 evals/gec_eval.py [--samples 5] FILE.areta.txt [...]

Get the files (CC BY-NC-SA 4.0, keep them local):
  https://github.com/CAMeL-Lab/arabic-gec/tree/master/data/areta_tags/wo_camelira/zaebuc
"""
import argparse
import os
import sys
from collections import Counter, defaultdict
from typing import List, NamedTuple, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "skills", "arabic-writing", "scripts"))
from archeck.engine import check  # noqa: E402

# Tokenized text has a space before every punctuation mark; that is not the
# writer's error, so punct-space findings are not scored.
_SKIP_RULES = {"punct-space"}

TAGS = {
    "OH": "hamza", "OT": "ة/ه", "OA": "ى/ي", "OW": "alif fariqa", "ON": "nun/tanween",
    "OG": "lengthened vowel", "OS": "shortened vowel", "OC": "letter order",
    "OR": "wrong letter", "OD": "extra letter", "OM": "missing letter",
    "MI": "inflection", "MT": "tense", "XC": "case", "XF": "definiteness",
    "XG": "gender", "XN": "number", "XT": "extra word", "XM": "missing word",
    "SW": "word choice", "SF": "conjunction", "PC": "punct. confusion",
    "PT": "extra punct.", "PM": "missing punct.", "SP": "wrongly split",
    "MG": "wrongly merged",
}


class Token(NamedTuple):
    src: str
    tgt: str
    tag: str


def read(path: str) -> List[List[Token]]:
    """Essays (blank-line separated) of aligned tokens."""
    essays, cur = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    essays.append(cur)
                cur = []
                continue
            src, tgt, tag = (line.split("\t") + ["", ""])[:3]
            cur.append(Token(src, tgt, tag or "UNK"))
    if cur:
        essays.append(cur)
    return essays


def layout(tokens: List[Token]) -> Tuple[str, List[Tuple[int, int]]]:
    """Text of the source tokens joined by spaces, and each token's span.
    An inserted token (empty source) gets the empty span at its position."""
    parts, spans, pos = [], [], 0
    for t in tokens:
        if t.src:
            if parts:
                pos += 1
            spans.append((pos, pos + len(t.src)))
            parts.append(t.src)
            pos += len(t.src)
        else:
            spans.append((pos, pos))
    return " ".join(parts), spans


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("files", nargs="+")
    p.add_argument("--samples", type=int, default=5)
    args = p.parse_args()
    total, hit = Counter(), Counter()
    false_by_rule, samples = Counter(), defaultdict(list)
    exact = suggested = 0
    words = 0
    for path in args.files:
        for tokens in read(path):
            text, spans = layout(tokens)
            found = [f for f in check(text)
                     if f.severity != "info" and f.rule not in _SKIP_RULES]
            words += sum(1 for t in tokens if t.src)
            covered = defaultdict(list)
            for f in found:
                for i, (a, b) in enumerate(spans):
                    if a < f.end and f.start < b:
                        covered[i].append(f)
            for i, t in enumerate(tokens):
                if not t.src:
                    continue  # insertions cannot be flagged on a token
                fs = covered.get(i, [])
                for tag in t.tag.split("+"):
                    if tag in ("UC", "UNK"):
                        continue
                    total[tag] += 1
                    hit[tag] += bool(fs)
                if t.tag != "UC" and fs:
                    a, b = spans[i]
                    for f in fs:
                        # Only one-word findings on exactly this token compare.
                        if (f.start, f.end) == (a, b) and f.suggestion \
                                and " or " not in f.suggestion:
                            suggested += 1
                            exact += f.suggestion == t.tgt
                            break
                if t.tag == "UC":
                    for f in fs:
                        false_by_rule[f.rule] += 1
                        a, b = spans[i]
                        samples[f.rule].append(" ".join(
                            text[max(0, a - 25):b + 25].split()).replace(
                                t.src, "[[" + t.src + "]]", 1))
    print("%d source words\n" % words)
    print("%-6s %-18s %6s %6s %7s" % ("tag", "error", "tokens", "caught", "recall"))
    for tag, n in total.most_common():
        if n >= 5:
            print("%-6s %-18s %6d %6d %6.0f%%" % (tag, TAGS.get(tag, "?"), n, hit[tag],
                                                100.0 * hit[tag] / n))
    n, h = sum(total.values()), sum(hit.values())
    print("%-6s %-18s %6d %6d %6.0f%%" % ("all", "", n, h, 100.0 * h / n if n else 0))
    if suggested:
        print("\nSuggestions on caught errors: %d of %d match the annotators' correction"
              % (exact, suggested))
    print("\nFlags on tokens the annotators left unchanged: %d" % sum(false_by_rule.values()))
    for rule, k in false_by_rule.most_common():
        print("  %-24s %d" % (rule, k))
        for s in samples[rule][:args.samples]:
            print("      " + s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
