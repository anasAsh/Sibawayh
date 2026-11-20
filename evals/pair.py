#!/usr/bin/env python3
"""Blind A/B pairs for an AI judge (see ai_judge.md).

For every prompt with both a baseline and a skill output, writes
OUT/pairs/pair-NN.md (the prompt, then Response A and Response B in random
order) and KEY (pair,id,a,b). Keep KEY outside OUT so the judge never sees it.

Usage: python3 evals/pair.py [--seed 7] OUT KEY
"""
import argparse
import csv
import hashlib
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _common as c  # noqa: E402


def sha1(text):
    """Of the stripped text, as judge_report.py checks it."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("out")
    p.add_argument("key")
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args(argv)
    rng = random.Random(a.seed)
    prompts = c.read_tsv(os.path.join(HERE, "prompts.tsv"))
    os.makedirs(os.path.join(a.out, "pairs"), exist_ok=True)
    rows = []
    for pr in prompts:
        texts = {}
        for mode in ("baseline", "skill"):
            path = os.path.join(HERE, "outputs", mode, pr["id"] + ".txt")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    texts[mode] = f.read().strip()
        if len(texts) < 2:
            continue
        order = ["baseline", "skill"]
        rng.shuffle(order)
        n = len(rows) + 1
        with open(os.path.join(a.out, "pairs", "pair-%02d.md" % n), "w", encoding="utf-8") as f:
            f.write("# Pair %02d\n\n## Prompt\n\n%s\n\n## Response A\n\n%s\n\n## Response B\n\n%s\n"
                    % (n, pr["prompt"], texts[order[0]], texts[order[1]]))
        rows.append({"pair": "%02d" % n, "id": pr["id"], "a": order[0], "b": order[1],
                     "a_sha1": sha1(texts[order[0]]), "b_sha1": sha1(texts[order[1]])})
    with open(a.key, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["pair", "id", "a", "b", "a_sha1", "b_sha1"])
        w.writeheader()
        w.writerows(rows)
    print("%d pairs in %s; key in %s" % (len(rows), a.out, a.key))
    return 0


if __name__ == "__main__":
    sys.exit(main())
