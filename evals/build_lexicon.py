#!/usr/bin/env python3
"""Build the frequency lexicons behind the hamza-missing and taa-haa warnings
from clean Arabic text (Arabic Wikipedia featured articles).

An entry says: in clean text, this word is written with a hamza (or ة)
almost always, and the bare (or ه) spelling is almost never seen. A text
that uses the bare spelling then probably has an error. Entries are
whole surface words with their prefixes (الاطفال, وايضا, بالطريقه).

Usage: python3 evals/build_lexicon.py [--min 5] [--ratio 0.01] DIR [DIR ...]
Writes skills/arabic-writing/scripts/data/lexicon_*.
"""
import argparse
import os
import re
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "skills", "arabic-writing", "scripts", "data")
sys.path.insert(0, _HERE)
from corpus_check import files  # noqa: E402

_DIAC = re.compile("[ً-ٰٟ]")
_WORD = re.compile("[ء-ي]+")
# Prefixes before the word's own first letter: و/ف, then ب/ل/ك, then ال (or لل).
_IMPERATIVE = re.compile("^[أإآ][^ا]{2,3}(?:وا|ي|ا|ن|وه|وها|وهم|يه|يها|يهم|ه|ها|هم|ني|نا)?$")
_PREFIXES = re.compile("^(?:[وف]?(?:[بلك]?ال|لل|[بلك])?)")
_IMPERFECT = re.compile("^[وف]?[يتنأ]")
_IMPERFECT_WAW = re.compile("^[وف]?[يتنأا]")  # also ادعو, a hamza slip for أدعو
_DEFINITE = re.compile("^(?:[وف]?(?:[بك]?ال|لل))")
_HAMZA_AT_STEM = re.compile("^((?:[وف])?(?:[بلك])?(?:ال)?|(?:[وف])?لل)([أإآ])(?=[ء-ي]{2})")


def count(paths):
    c = Counter()
    for path in files(paths):
        with open(path, encoding="utf-8") as f:
            c.update(_WORD.findall(_DIAC.sub("", f.read())))
    return c


def pairs(c, min_count, ratio):
    hamza, taa = [], []
    for w, n in c.items():
        if n < min_count:
            continue
        m = _HAMZA_AT_STEM.match(w)
        # Skip imperative shapes: the bare form is also a valid imperative
        # (انسَ، ادعُ، اجلس، اسأل، اقبل، واقسموا، اكتبيه).
        if m and not (m.group(1) in ("", "و", "ف") and _IMPERATIVE.match(w[len(m.group(1)):])):
            bare = m.group(1) + "ا" + w[m.end():]
            if c[bare] <= ratio * n:
                hamza.append((bare, w, n))
        # Only with ال: a definite word cannot take a pronoun suffix, while
        # هواه، قاده، مكتبه are real words ("his desire", "led him", "his office").
        # Without ال, only nisba adjectives (سلبية) that are common in clean text:
        # the يه spelling is then not a pronoun form in practice.
        # Not فاعية (باقية، ماضية): باقيه "the rest of it" and ماضيه "his past" are words.
        # 6+ letters: a 5-letter يه word may be a feminine imperative with a
        # pronoun (علِّميه "teach her"), and فاعية shapes (باقيه) are words.
        nisba = w.endswith("ية") and len(w) >= 6 and n >= 4 * min_count
        if w.endswith("ة") and (_DEFINITE.match(w) and len(w) >= 5 or nisba):
            haa = w[:-1] + "ه"
            if c[haa] <= ratio * n:
                taa.append((haa, w, n))
    return _best(hamza), _best(taa)


def endings(c, min_count, ratio):
    """Word-final spellings: ى for ي (المصرى), and a missing alif after the
    plural و (كانو)."""
    yaa, waw = [], []
    for w, n in c.items():
        if n < min_count or len(w) < 3:
            continue
        # Only ى written for a final ي (المصرى), in words of 5+ letters not
        # shaped like an imperfect verb: يُسمى/يسمي، تبقى/تُبقي، رمى/رمي are
        # all real words.
        # Definite words cannot be verbs; others need a long stem, so Form III
        # verbs (والى، نادى "called" vs نادي "club") stay out.
        stem = _PREFIXES.sub("", w)
        if w.endswith("ي") and (_DEFINITE.match(w) and len(stem) >= 3
                                or len(stem) >= 5 and not _IMPERFECT.match(w)):
            wrong = w[:-1] + "ى"
            if c[wrong] <= ratio * n:
                yaa.append((wrong, w, n))
        # Past-tense plurals only: an imperfect ending in و is a real verb
        # (أدعو، أبدو، يرجو).
        if w.endswith("وا") and len(w) >= 4 and not _IMPERFECT_WAW.match(w):
            wrong = w[:-1]
            if c[wrong] <= ratio * n:
                waw.append((wrong, w, n))
    return _best(yaa), _best(waw)


def merged(c, min_count):
    """Frequent words (for يا/لا/ما joined to the next word), and the attested
    words that start with يا/لا/ما, which are then left alone (ياسر، لاعب)."""
    frequent = sorted(w for w, n in c.items() if n >= min_count and len(w) >= 3)
    fset = set(frequent)
    attested = sorted(w for w in c if w[:2] in ("يا", "لا", "ما") and w[2:] in fset)
    return frequent, attested


def _best(rows):
    """One entry per wrong form: its most frequent correct form (واثر: وأثر, not وإثر)."""
    best = {}
    for wrong, right, n in rows:
        if wrong not in best or n > best[wrong][2]:
            best[wrong] = (wrong, right, n)
    return sorted(best.values(), key=lambda e: -e[2])


def write(name, rows, words, args):
    with open(os.path.join(_DATA, name), "w", encoding="utf-8") as f:
        f.write("# Generated by evals/build_lexicon.py from %d words of Arabic Wikipedia\n"
                "# featured articles (--min %d --ratio %g). Do not edit by hand: add\n"
                "# exceptions to lexicon_exceptions.txt and rebuild.\n"
                % (words, args.min, args.ratio))
        f.write("wrong\tright\tcount\n")
        for wrong, right, n in rows:
            f.write("%s\t%s\t%d\n" % (wrong, right, n))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dirs", nargs="+")
    p.add_argument("--min", type=int, default=5, help="minimum count of the correct form")
    p.add_argument("--ratio", type=float, default=0.01,
                   help="maximum count of the wrong form, as a share of the correct one")
    args = p.parse_args()
    c = count(args.dirs)
    with open(os.path.join(_DATA, "lexicon_exceptions.txt"), encoding="utf-8") as f:
        skip = {ln.strip() for ln in f if ln.strip() and not ln.startswith("#")}
    hamza, taa = pairs(c, args.min, args.ratio)
    hamza = [e for e in hamza if e[0] not in skip]
    taa = [e for e in taa if e[0] not in skip]
    yaa, waw = endings(c, args.min, args.ratio)
    yaa = [e for e in yaa if e[0] not in skip]
    waw = [e for e in waw if e[0] not in skip]
    words = sum(c.values())
    write("lexicon_hamza.tsv", hamza, words, args)
    write("lexicon_taa.tsv", taa, words, args)
    write("lexicon_yaa.tsv", yaa, words, args)
    write("lexicon_waw.tsv", waw, words, args)
    frequent, attested = merged(c, 6 * args.min)
    for name, rows in (("lexicon_frequent.txt", frequent), ("lexicon_merged_ok.txt", attested)):
        with open(os.path.join(_DATA, name), "w", encoding="utf-8") as f:
            f.write("# Generated by evals/build_lexicon.py; do not edit by hand.\n")
            f.write("\n".join(rows) + "\n")
    print("%d words; %d hamza, %d taa, %d yaa, %d waw entries; %d frequent words"
          % (words, len(hamza), len(taa), len(yaa), len(waw), len(frequent)))


if __name__ == "__main__":
    main()
