"""Auto-fix rules. Every rule has the signature rule(text, masked, opts)."""
import re
import unicodedata
from typing import Dict, List

from .model import Finding
from .text import ARABIC_LETTER

_AR = re.compile(ARABIC_LETTER)
_DIACRITICS = frozenset(chr(c) for c in range(0x064B, 0x0660)) | {"ٰ"}
_SPACES = " \t"
_TATWEEL = "ـ"


def _is_ar(ch: str) -> bool:
    return bool(ch) and _AR.match(ch) is not None


def _blank(text: str, masked: str, i: int) -> bool:
    """True if position i is a real space or tab (not a masked region)."""
    return text[i] in _SPACES and masked[i] == text[i]


def _left_letter(text: str, masked: str, i: int, skip_close: bool = False) -> int:
    """Index of the Arabic letter just left of i (skipping real blanks and
    diacritics), or -1. With skip_close, one closing ) or » after Arabic is
    looked through."""
    j = i - 1
    while j >= 0 and _blank(text, masked, j):
        j -= 1
    if skip_close and j >= 0 and masked[j] in ")»":
        j -= 1
        while j >= 0 and masked[j] in _DIACRITICS:
            j -= 1
        return j if j >= 0 and _is_ar(masked[j]) else -1
    while j >= 0 and masked[j] in _DIACRITICS:
        j -= 1
    return j if j >= 0 and _is_ar(masked[j]) else -1


def _right_index(text: str, masked: str, i: int) -> int:
    """Index of the nearest non-blank char right of i, or len(text) at the end
    of the text (also returned at a newline)."""
    j = i + 1
    while j < len(text) and _blank(text, masked, j):
        j += 1
    return j


def punct_latin(text: str, masked: str, opts: Dict[str, str]) -> List[Finding]:
    table = {",": "،", ";": "؛", "?": "؟"}
    out = []
    for m in re.finditer(r"[,;?]", masked):
        i = m.start()
        if _left_letter(text, masked, i, skip_close=True) < 0:
            continue
        j = _right_index(text, masked, i)
        ch = masked[i]
        at_eol = j >= len(text) or masked[j] in "\r\n"
        if (j < len(text) and _is_ar(masked[j])) or (ch == "?" and at_eol):
            out.append(
                Finding(i, i + 1, "fix", "punct-latin",
                        "Latin punctuation between Arabic words",
                        suggestion=table[ch], replacement=table[ch])
            )
    return out


def punct_space(text: str, masked: str, opts: Dict[str, str]) -> List[Finding]:
    out = []
    for m in re.finditer("[،؛؟.:!]", masked):
        i = m.start()
        if _left_letter(text, masked, i) < 0:
            continue
        s = i
        while s > 0 and _blank(text, masked, s - 1):
            s -= 1
        nxt = masked[i + 1] if i + 1 < len(masked) else ""
        if masked[i] == ".":
            # Dots are abbreviations, runs, or paths far too often: only
            # tidy a lone sentence-ending dot (space before it).
            prv = masked[i - 1] if i > 0 else ""
            if prv in ".…" or nxt in ".…" or (nxt and not nxt.isspace()):
                continue
            need_after = False
        else:
            need_after = _is_ar(nxt)
        if s == i and not need_after:
            continue
        rep = masked[i] + (" " if need_after else "")
        out.append(
            Finding(s, i + 1, "fix", "punct-space",
                    "No space before, one space after Arabic punctuation",
                    suggestion=rep, replacement=rep)
        )
    return out


# Persian/Urdu look-alikes with one unambiguous Arabic counterpart.
# A word-final ی is not here: it may stand for ي or ى, so it is reported as a
# separate ``persian-letter-final`` warn with no replacement.
_PERSIAN = {"ی": "ي", "ک": "ك", "ہ": "ه"}
_FARSI_YEH = "ی"
# Letters that exist only in Persian/Urdu: a token with one is quoted Persian,
# not misspelled Arabic, so it is left alone.
_PERSIAN_ONLY = frozenset("پچژگ")
_TOKEN = re.compile("[ء-ۓ]+")
_LATIN_WORD = re.compile(r"[A-Za-z0-9_]")


def persian_letter(text: str, masked: str, opts: Dict[str, str]) -> List[Finding]:
    out = []
    for m in _TOKEN.finditer(masked):
        a, b = m.start(), m.end()
        if (a > 0 and _LATIN_WORD.match(masked[a - 1])) or (
            b < len(masked) and _LATIN_WORD.match(masked[b])
        ):
            continue
        tok = m.group()
        if not all(
            c in _PERSIAN or c in _DIACRITICS or c == _TATWEEL or _is_ar(c)
            for c in tok
        ):
            continue
        if any(c in _PERSIAN_ONLY for c in tok):
            continue
        letters = [k for k, c in enumerate(tok) if _is_ar(c)]
        if len(letters) == 1:
            continue  # a letter cited on its own, not a word
        last = letters[-1] if letters else -1
        for k, c in enumerate(tok):
            if c == _FARSI_YEH and k == last:
                out.append(
                    Finding(a + k, a + k + 1, "warn", "persian-letter-final",
                            "Persian yeh at the end of a word: Arabic ي or ى?",
                            suggestion="ي or ى")
                )
            elif c in _PERSIAN:
                out.append(
                    Finding(a + k, a + k + 1, "fix", "persian-letter",
                            "Persian/Urdu letter form in Arabic text",
                            suggestion=_PERSIAN[c], replacement=_PERSIAN[c])
                )
    return out


# U+FDF0-U+FDFF are word ligatures (ﷲ ﷺ …) and the Rial sign ﷼: they are
# written on purpose, so only letter presentation forms are expanded.
_PRESENTATION = re.compile("[\ufb50-\ufdcf\ufe70-\ufeff]")


def presentation_form(text: str, masked: str, opts: Dict[str, str]) -> List[Finding]:
    out = []
    for m in _PRESENTATION.finditer(masked):
        ch = m.group()
        rep = unicodedata.normalize("NFKC", ch)
        if rep != ch:
            out.append(
                Finding(m.start(), m.end(), "fix", "presentation-form",
                        "Arabic presentation form; use the base letters",
                        suggestion=rep, replacement=rep)
            )
    return out


def tatweel(text: str, masked: str, opts: Dict[str, str]) -> List[Finding]:
    out = []
    for m in re.finditer(_TATWEEL + "+", masked):
        a, b = m.start(), m.end()
        j = a - 1
        while j >= 0 and masked[j] in _DIACRITICS:
            j -= 1
        k = b
        while k < len(masked) and masked[k] in _DIACRITICS:
            k += 1
        if j >= 0 and _is_ar(masked[j]) and k < len(masked) and _is_ar(masked[k]):
            out.append(
                Finding(a, b, "fix", "tatweel", "Remove tatweel",
                        suggestion="", replacement="")
            )
    return out


def persian_digit(text: str, masked: str, opts: Dict[str, str]) -> List[Finding]:
    found = list(re.finditer("[۰-۹]", masked))
    if not found:
        return []
    mode = opts.get("digits", "auto")
    if mode == "auto":
        ar = len(re.findall("[٠-٩]", masked))
        we = len(re.findall("[0-9]", masked))
        mode = "arabic" if ar > we else "western"
    base = 0x0660 if mode == "arabic" else ord("0")
    out = []
    for m in found:
        rep = chr(base + ord(m.group()) - 0x06F0)
        out.append(
            Finding(m.start(), m.end(), "fix", "persian-digit",
                    "Persian digit; use the document's digit style",
                    suggestion=rep, replacement=rep)
        )
    return out


RULES = [
    punct_latin,
    punct_space,
    persian_letter,
    presentation_form,
    tatweel,
    persian_digit,
]
