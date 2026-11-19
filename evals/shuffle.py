#!/usr/bin/env python3
"""Blind the outputs for scoring.

Copies evals/outputs/<mode>/<id>.txt to evals/blind/<random-id>.txt and
writes evals/blind_key.csv (blind_id,id,mode). Score the files in blind/,
put the blind id in rubric.csv's `id` column (leave `mode` empty), and
report.py resolves it through the key. Do not open blind_key.csv until done.
"""
import csv
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    out_root = os.path.join(HERE, "outputs")
    blind = os.path.join(HERE, "blind")
    items = []
    for mode in ("baseline", "skill"):
        d = os.path.join(out_root, mode)
        if os.path.isdir(d):
            items += [(f[:-4], mode) for f in sorted(os.listdir(d))
                      if f.endswith(".txt")]
    if not items:
        sys.exit("no outputs found")
    rng = random.SystemRandom()
    ids = ["%06x" % n for n in rng.sample(range(1 << 24), len(items))]
    os.makedirs(blind, exist_ok=True)
    with open(os.path.join(HERE, "blind_key.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["blind_id", "id", "mode"])
        for b, (i, m) in zip(ids, items):
            shutil.copyfile(os.path.join(out_root, m, i + ".txt"),
                            os.path.join(blind, b + ".txt"))
            w.writerow([b, i, m])
    print("%d files in evals/blind/, key in evals/blind_key.csv" % len(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
