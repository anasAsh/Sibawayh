"""Word-list rules. Every rule has the signature rule(text, masked, opts).

A word matches an entry when one of its stem candidates (the word, then the
word stripped of و/ف, ب/ل/ك/لل and ال) equals the entry. Stripped stems shorter
than 3 letters are not looked up, so وفى or واو never match فى or او.
hamza-missing and dialect-word match whole words only. Entries
with a space are matched as phrases. The suggestion keeps the word's prefixes.
"""
import re
from functools import lru_cache
from typing import Dict, List, Pattern, Tuple

from .data import load_list, load_tsv
from .model import Finding
from .text import ARABIC_LETTER, iter_words, stem_candidates

_DIAC = "ً-ٰٟ"
_DIAC_RE = re.compile("[" + _DIAC + "]")
_EDGE = "(?:" + ARABIC_LETTER + "|[" + _DIAC + "])"
_MIN_STRIPPED = 3

Table = Tuple[Dict[str, Tuple[str, str]], Tuple[Tuple[Pattern, str, str], ...]]


def _phrase_re(phrase: str) -> Pattern:
    body = "".join(
        r"\s+" if ch == " " else re.escape(ch) + "[" + _DIAC + "]*" for ch in phrase
    )
    return re.compile("(?<!" + _EDGE + ")" + body + "(?!" + _EDGE + ")")


@lru_cache(maxsize=None)
def _table(name: str, key: str, value: str) -> Table:
    words = {}
    phrases = []
    for row in load_tsv(name):
        wrong = _DIAC_RE.sub("", row[key]).strip()
        entry = (row[value], row.get("note", ""))
        if " " in wrong:
            phrases.append((_phrase_re(wrong), entry[0], entry[1]))
        else:
            words[wrong] = entry
    return words, tuple(phrases)


def _cut(word: str, n: int) -> int:
    """Index in word just after its first n letters (diacritics stay attached)."""
    count = 0
    for i, ch in enumerate(word):
        if not _DIAC_RE.match(ch):
            if count == n:
                return i
            count += 1
    return len(word)


def _candidates(word: str, whole: bool) -> List[Tuple[int, str, int]]:
    """(prefix letters, stem, letters to drop from the suggestion's start)."""
    plain = stem_candidates(word)
    full = plain[0]
    out = [(0, full, 0)]
    if whole:
        return out
    for stem in plain[1:]:
        p = len(full) - len(stem)
        if len(stem) >= _MIN_STRIPPED:
            out.append((p, stem, 0))
        if full[:p].endswith("لل"):
            # لل = لـ + الـ: look the stem up with its article, then
            # drop the article's ال from the suggestion (للمدرسه -> للمدرسة).
            out.append((p, "ال" + stem, 2))
    return out


def _scan(masked: str, rule: str, name: str, key: str, value: str,
          severity: str, message: str, whole: bool = False) -> List[Finding]:
    words, phrases = _table(name, key, value)
    out = []
    for start, end, word in iter_words(masked):
        if whole and start and masked[start - 1] == "ـ":
            continue  # a cited ending such as ـان, not a word
        for p, stem, drop in _candidates(word, whole):
            hit = words.get(stem)
            if hit is None:
                continue
            right, note = hit
            if drop and not right.startswith("ال"):
                drop = 0
            suggestion = word[:_cut(word, p)] + right[drop:]
            msg = message + (" (" + note + ")" if note else "")
            out.append(Finding(start, end, severity, rule, msg, suggestion=suggestion))
            break
    for pattern, right, note in phrases:
        for m in pattern.finditer(masked):
            msg = message + (" (" + note + ")" if note else "")
            out.append(Finding(m.start(), m.end(), severity, rule, msg, suggestion=right))
    return out


def misspelling(text, masked, opts):
    return _scan(masked, "misspelling", "misspellings.tsv", "wrong", "right",
                 "error", "Misspelling")


# Masdars of forms VII (انفعال), VIII (افتعال) and X (استفعال) by shape, for
# words not in wasl_words.tsv. Form IV masdars (إفعال: إنتاج، إنفاق) have one
# letter fewer, so they never match.
_C = "[بتثجحخدذرزسشصضطظعغفقكلمنهويءأإآؤئ]"
_WASL_MASDAR = re.compile(
    "إ(?:" + _C + "ت" + _C + "ا" + _C + "|ن" + _C + _C + "ا" + _C
    + "|ست" + _C + _C + "ا" + _C + ")(?:ة|ات|ي|ية|يا|يين|يات|ه|ها|هم|هما)?")
_WASL_FOREIGN = ("إسترات", "إسترال", "إنكشار")  # loanwords: إستراتيجية، إستراليا، الإنكشارية


def hamza_wasl(text, masked, opts):
    out = _scan(masked, "hamza-wasl", "wasl_words.tsv", "wrong", "right",
                "error", "Hamzat al-wasl: write a bare alif, not إ")
    listed = {f.start for f in out}
    for start, end, word in iter_words(masked):
        if start in listed:
            continue
        plain = stem_candidates(word)
        for stem in plain:
            if _WASL_MASDAR.fullmatch(stem) and not stem.startswith(_WASL_FOREIGN):
                p = len(plain[0]) - len(stem)
                i = _cut(word, p)
                out.append(Finding(start, end, "error", "hamza-wasl",
                                   "Hamzat al-wasl: write a bare alif, not إ "
                                   "(masdar of form VII, VIII or X)",
                                   suggestion=word[:i] + "ا" + word[i + 1:]))
                break
    return out


def _with_lexicon(found, masked, rule, lexicon, message):
    """Add warnings from a generated frequency lexicon (whole words) where
    the hand-made list found nothing."""
    seen = {f.start for f in found}
    extra = _scan(masked, rule, lexicon, "wrong", "right", "warn", message, whole=True)
    return found + [f for f in extra if f.start not in seen]


def hamza_missing(text, masked, opts):
    # Whole words only: stripped forms collide with real words (كانت -> انت).
    found = _scan(masked, "hamza-missing", "hamza_missing.tsv", "wrong", "right",
                  "warn", "Missing hamza", whole=True)
    found = _with_lexicon(found, masked, "hamza-missing", "lexicon_hamza.tsv",
                          "Missing hamza? Clean text almost always writes it")
    # A word inside a misspelled phrase has the phrase's fix instead:
    # انشاء الله is إن شاء الله, never إنشاء الله.
    _, phrases = _table("misspellings.tsv", "wrong", "right")
    spans = [m.span() for pattern, _, _ in phrases for m in pattern.finditer(masked)]
    return [f for f in found
            if not any(a <= f.start and f.end <= b for a, b in spans)]


def taa_haa(text, masked, opts):
    found = _scan(masked, "taa-haa", "taa_haa.tsv", "wrong", "right",
                  "warn", "Taa marbuta / haa confusion")
    return _with_lexicon(found, masked, "taa-haa", "lexicon_taa.tsv",
                         "ة written as ه? Clean text almost always writes ة here")


def alif_maqsura(text, masked, opts):
    found = _scan(masked, "alif-maqsura", "alif_maqsura.tsv", "wrong", "right",
                  "warn", "Alif maqsura / yaa confusion")
    return _with_lexicon(found, masked, "alif-maqsura", "lexicon_yaa.tsv",
                         "ى/ي at the end? Clean text almost always writes it the other way")


def alif_fariqa(text, masked, opts):
    return _scan(masked, "alif-fariqa", "lexicon_waw.tsv", "wrong", "right", "warn",
                 "Missing alif after the plural و? Clean text almost always writes it",
                 whole=True)


_PARTICLES = ("يا", "لا", "ما")
# لا joins nisba adjectives as a prefix: لاسلكي، لامركزية، لادينية.
_NISBA = re.compile("(?:ي|ية|يا|يًا|يات|يين)$")


def merged_particle(text, masked, opts):
    """يا، لا and ما are separate words: ياجزيرة -> يا جزيرة، لايوجد -> لا يوجد.
    Only when the rest is a frequent word of 4+ letters and the joined form
    is never seen in clean text (ياسر، لاعب، ماكين stay)."""
    frequent = load_list("lexicon_frequent.txt")
    attested = load_list("lexicon_merged_ok.txt")
    out = []
    for start, end, word in iter_words(masked):
        plain = _DIAC_RE.sub("", word)
        head, rest = plain[:2], plain[2:]
        if head in _PARTICLES and len(rest) >= 4 and rest in frequent \
                and plain not in attested and not (head == "لا" and _NISBA.search(rest)):
            out.append(Finding(start, end, "warn", "merged-particle",
                               head + " is a separate word", suggestion=head + " " + rest))
    return out


def dialect_word(text, masked, opts):
    # Whole words only: stripped forms collide with real words (كبدي -> بدي).
    return _scan(masked, "dialect-word", "dialect_words.tsv", "word", "msa",
                 "warn", "Dialect word in an MSA text", whole=True)


RULES = [misspelling, hamza_wasl, hamza_missing, taa_haa, alif_maqsura, alif_fariqa,
         merged_particle, dialect_word]
