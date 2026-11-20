#!/usr/bin/env python3
"""Unblind an AI judge's scores and check the success bar.

SCORES is a CSV with one row per pair and response:
  pair,response,grammar,spelling,translationese,register,formatting,over_corrections
(response is A or B), plus optional rows with response=pref and the
preferred response (A, B or tie) in the grammar column. KEY comes from
pair.py; when it carries a_sha1/b_sha1, the outputs must be the ones judged. Word counts come from evals/outputs.

Usage: python3 evals/judge_report.py SCORES KEY
"""
import csv
import hashlib
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "skills", "arabic-writing", "scripts"))
from archeck.text import iter_words, mask  # noqa: E402

CATS = ["grammar", "spelling", "translationese", "register", "formatting"]


def digest(mode, pid):
    with open(os.path.join(HERE, "outputs", mode, pid + ".txt"), "rb") as f:
        return hashlib.sha1(f.read().strip()).hexdigest()


def words(mode, pid):
    with open(os.path.join(HERE, "outputs", mode, pid + ".txt"), encoding="utf-8") as f:
        return sum(1 for _ in iter_words(mask(f.read())))


def main(argv=None) -> int:
    scores_path, key_path = (argv or sys.argv[1:])[:2]
    with open(key_path, encoding="utf-8") as f:
        key = {r["pair"]: r for r in csv.DictReader(f)}
    errors = {m: Counter() for m in ("baseline", "skill")}
    nwords = Counter()
    over = 0
    prefs = Counter()
    by_type = defaultdict(lambda: {m: Counter() for m in ("baseline", "skill")})
    seen = set()
    with open(scores_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = key[r["pair"].zfill(2)]
            if r["response"] == "pref":
                v = r["grammar"].strip()
                prefs[k[v.lower()] if v in ("A", "B") else "tie"] += 1
                continue
            mode = k[r["response"].lower()]
            if (k["pair"], mode) in seen:
                sys.exit("duplicate row for pair %s %s" % (k["pair"], r["response"]))
            seen.add((k["pair"], mode))
            sha = k.get(r["response"].lower() + "_sha1")
            if sha and sha != digest(mode, k["id"]):
                sys.exit("outputs/%s/%s.txt changed since pair.py made the pairs the judge saw"
                         % (mode, k["id"]))
            nwords[mode] += words(mode, k["id"])
            task = k["id"].rsplit("-", 1)[0]
            for cat in CATS:
                n = int(r[cat] or 0)
                errors[mode][cat] += n
                by_type[task][mode][cat] += n
            if mode == "skill":
                over += int(r.get("over_corrections") or 0)
    pairs = Counter(p for p, _ in seen)
    incomplete = sorted(p for p, n in pairs.items() if n != 2)
    if incomplete:
        sys.exit("pairs without both an A and a B row: %s" % ", ".join(incomplete))
    per100 = {m: {c: 100.0 * errors[m][c] / nwords[m] for c in CATS} for m in errors}
    tot = {m: sum(per100[m].values()) for m in errors}
    print("Pairs scored: %d   words: baseline %d, skill %d\n" % (len(seen) // 2, nwords["baseline"], nwords["skill"]))
    print("%-15s %9s %9s %8s" % ("errors/100w", "baseline", "skill", "change"))
    for cat in CATS + ["TOTAL"]:
        b = tot["baseline"] if cat == "TOTAL" else per100["baseline"][cat]
        s = tot["skill"] if cat == "TOTAL" else per100["skill"][cat]
        ch = "%+.0f%%" % (100 * (s - b) / b) if b else ("-" if not s else "new")
        print("%-15s %9.2f %9.2f %8s" % (cat, b, s, ch))
    print("\nRaw counts: baseline %s\n            skill    %s" % (
        dict(errors["baseline"]), dict(errors["skill"])))
    print("\nBy task (total errors, baseline → skill):")
    for task in sorted(by_type):
        t = by_type[task]
        print("  %-14s %3d → %3d" % (task, sum(t["baseline"].values()), sum(t["skill"].values())))
    if prefs:
        print("\nPreferred: skill %d, baseline %d, tie %d" % (prefs["skill"], prefs["baseline"], prefs["tie"]))
    worse = [c for c in CATS if per100["skill"][c] > per100["baseline"][c]]
    ok = (over == 0 and tot["skill"] <= 0.5 * tot["baseline"] and not worse)
    print("\nOver-corrections in skill outputs: %d" % over)
    print("Bar (0 over-corrections, skill <= 50%% of baseline, no category worse): %s%s"
          % ("PASS" if ok else "FAIL", "" if not worse else "  (worse: %s)" % ", ".join(worse)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
