#!/usr/bin/env python3
"""Summarise the evaluation: rubric rates (headline), checker counts (detail)
and the success-bar verdict.

Usage: python3 evals/report.py [--rubric evals/rubric.csv]
                               [--outputs evals/outputs]
                               [--key evals/blind_key.csv]
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "skills", "arabic-writing", "scripts"))

from archeck.engine import check  # noqa: E402
from archeck.text import iter_words, mask  # noqa: E402

CATEGORIES = ["grammar", "spelling", "translationese", "register", "formatting"]
MODES = ["baseline", "skill"]
FAMILIES = {
    "punctuation": ["punct-latin", "punct-space"],
    "spelling": ["persian-letter", "persian-letter-final", "presentation-form", "tatweel",
                 "persian-digit", "misspelling", "hamza-wasl", "hamza-missing",
                 "taa-haa", "alif-maqsura", "tanween-mixed", "spelling-mixed",
                 "waw-split", "maqsura-medial", "alif-fariqa", "merged-particle",
                 "tanween-alif"],
    "grammar": ["sawfa-lan", "jussive-nun", "relative-after-indefinite", "number-gender",
                "compound-number"],
    "style": ["dialect-word", "stray-english", "english-line", "translationese-density",
              "calque"],
    "formatting": ["digit-mix", "rtl-line-start"],
}
_RULE_FAMILY = {r: f for f, rules in FAMILIES.items() for r in rules}


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def words(text: str) -> int:
    return sum(1 for _ in iter_words(mask(text)))


def checker_counts(path: str) -> Dict[str, int]:
    counts = {f: 0 for f in FAMILIES}
    for finding in check(_read(path)):
        fam = _RULE_FAMILY.get(finding.rule)
        if fam:
            counts[fam] += 1
    return counts


def _num(v) -> int:
    v = (v or "").strip() if isinstance(v, str) else v
    return int(v) if v not in ("", None) else 0


def _scored(row) -> bool:
    return any(str(row.get(c, "")).strip() != "" for c in CATEGORIES)


def rubric_rates(rows) -> Dict[str, Dict[str, float]]:
    """rows: dicts with mode, words and category counts. Rows with all
    category counts blank are unscored and skipped. Rate = errors per 100
    words, pooled over all rows of a mode."""
    sums: Dict[str, Dict[str, float]] = {}
    for row in rows:
        if not _scored(row) or row.get("mode") not in MODES:
            continue
        s = sums.setdefault(row["mode"], {c: 0 for c in CATEGORIES})
        s["words"] = s.get("words", 0) + int(row.get("words") or 0)
        for c in CATEGORIES:
            s[c] += _num(row.get(c))
    rates = {}
    for mode, s in sums.items():
        w = s["words"]
        r = {c: (100.0 * s[c] / w if w else 0.0) for c in CATEGORIES}
        r["total"] = sum(r[c] for c in CATEGORIES)
        rates[mode] = r
    return rates


def verdict(rates, over_corrections: int) -> Tuple[bool, List[str]]:
    reasons = []
    if over_corrections != 0:
        reasons.append("%d over-correction(s); the bar is zero"
                       % over_corrections)
    base, skill = rates.get("baseline"), rates.get("skill")
    if base is None or skill is None:
        reasons.append("rubric needs scored rows for both baseline and skill")
        return False, reasons
    if skill["total"] > 0.5 * base["total"]:
        reasons.append("skill total %.2f is above 50%% of baseline total %.2f"
                       % (skill["total"], base["total"]))
    for c in CATEGORIES:
        if skill[c] > base[c]:
            reasons.append("category %s is worse: skill %.2f > baseline %.2f"
                           % (c, skill[c], base[c]))
    return (not reasons), reasons


def load_rubric(rubric_path: str, key_path: str = None) -> List[dict]:
    """Rows keyed by id+mode, or by blind id (resolved through the key)."""
    key = {}
    if key_path and os.path.exists(key_path):
        with open(key_path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                key[r["blind_id"]] = r
    with open(rubric_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        k = key.get(row["id"])
        if k:
            # Errors name the blind id only, so they do not unblind the scorer.
            row["_name"] = "blind row %s" % row["id"]
            row["id"], row["mode"] = k["id"], k["mode"]
        elif (row.get("mode") or "").strip() not in MODES:
            row["_error"] = ("row %r: mode %r is not baseline/skill and the "
                             "id is not in the blind key (%s)"
                             % (row["id"], row.get("mode"),
                                "key found" if key else "key missing or empty"))
    return rows


def _name(row) -> str:
    return row.get("_name") or "row %s/%s" % (row["id"], row["mode"])


def check_rows(rows) -> List[str]:
    """Problems that must stop the report. A row with every category cell
    blank is unscored; a partly filled one is an error."""
    errors = []
    for row in rows:
        if row.get("_error"):
            errors.append(row["_error"])
            continue
        name = _name(row)
        cells = {c: str(row.get(c) or "").strip() for c in CATEGORIES}
        if not any(cells.values()):
            continue
        blank = [c for c in CATEGORIES if not cells[c]]
        if blank:
            errors.append("%s: partly filled, blank: %s"
                          % (name, ", ".join(blank)))
        cols = list(CATEGORIES)
        if row["mode"] == "skill":
            cols.append("over_corrections")
            if not str(row.get("over_corrections") or "").strip():
                errors.append("%s: over_corrections is required on %s"
                              % (name, "every blind row" if row.get("_name")
                                 else "scored skill rows"))
        for c in cols:
            v = str(row.get(c) or "").strip()
            if v and not v.isdigit():
                errors.append("%s: %s=%r is not a non-negative integer"
                              % (name, c, v))
    return errors


def _words_for(outputs: str, row) -> int:
    p = os.path.join(outputs, row["mode"], row["id"] + ".txt")
    if not os.path.exists(p):
        if row.get("_name"):
            raise FileNotFoundError("scored %s has no output file (see the "
                                    "blind key)" % row["_name"])
        raise FileNotFoundError("scored row %s/%s has no output file %s"
                                % (row["id"], row["mode"], p))
    return words(_read(p))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubric", default=os.path.join(_HERE, "rubric.csv"))
    ap.add_argument("--outputs", default=os.path.join(_HERE, "outputs"))
    ap.add_argument("--key", default=os.path.join(_HERE, "blind_key.csv"))
    a = ap.parse_args(argv)

    rows = load_rubric(a.rubric, a.key)
    errors = check_rows(rows)
    if not errors:
        for row in rows:
            if _scored(row):
                try:
                    row["words"] = _words_for(a.outputs, row)
                except FileNotFoundError as e:
                    errors.append(str(e))
    if errors:
        print("ERROR: rubric cannot be reported:", file=sys.stderr)
        for e in errors:
            print("- " + e, file=sys.stderr)
        return 2
    rates = rubric_rates(rows)
    over = sum(_num(r.get("over_corrections")) for r in rows
               if r["mode"] == "skill")

    print("## Rubric: errors per 100 words (headline)\n")
    print("| mode | " + " | ".join(CATEGORIES) + " | total |")
    print("|---|" + "---|" * (len(CATEGORIES) + 1))
    for m in MODES:
        if m in rates:
            r = rates[m]
            print("| %s | " % m + " | ".join("%.2f" % r[c] for c in CATEGORIES)
                  + " | %.2f |" % r["total"])
    print("\nOver-corrections introduced by the skill: %d\n" % over)

    print("## Checker findings (supporting detail; skill output was already "
          "checked, so biased)\n")
    print("| mode | files | words | " + " | ".join(FAMILIES) + " |")
    print("|---|---|---|" + "---|" * len(FAMILIES))
    for m in MODES:
        d = os.path.join(a.outputs, m)
        if not os.path.isdir(d):
            continue
        tot = {f: 0 for f in FAMILIES}
        n = w = 0
        for name in sorted(os.listdir(d)):
            if name.endswith(".txt"):
                p = os.path.join(d, name)
                n += 1
                w += words(_read(p))
                for f, c in checker_counts(p).items():
                    tot[f] += c
        print("| %s | %d | %d | " % (m, n, w)
              + " | ".join(str(tot[f]) for f in FAMILIES) + " |")

    ok, reasons = verdict(rates, over)
    print()
    print("PASS" if ok else "FAIL")
    for r in reasons:
        print("- " + r)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
