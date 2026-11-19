"""Text masking and word utilities."""
import re
from typing import Iterator, List, Tuple

ARABIC_LETTER = "[ء-غف-يٱ-ۓ]"
_DIACRITICS = "\u064b-\u065f\u0670"  # U+064B-U+065F, U+0670

_WORD_RE = re.compile(
    ARABIC_LETTER + "(?:" + ARABIC_LETTER + "|[" + _DIACRITICS + "])*"
)
_DIACRITIC_RE = re.compile("[" + _DIACRITICS + "]")
_ANY_ARABIC_RE = re.compile(ARABIC_LETTER)

_SKIP_RE = re.compile(
    "|".join(
        [
            r"\A---[ \t]*\r?\n.*?^---[ \t]*\r?$",  # YAML front matter
            r"<!-- arabic-check: off -->.*?(?:<!-- arabic-check: on -->|\Z)",
            r"^[ \t]*(```|~~~).*?(?:^[ \t]*\1[^\n]*$|\Z)",
            r"`[^`\n]+`",
            r"https?://\S+",
            r"www\.\S+",
            r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
            r"[^\s\u0600-\u06FF]*/[^\s\u0600-\u06FF]+\.[A-Za-z0-9]+",
            r"~/\S+",
            r"﴿[^﴾]*﴾",
        ]
    ),
    re.DOTALL | re.MULTILINE,
)


def has_arabic(s: str) -> bool:
    return _ANY_ARABIC_RE.search(s) is not None


def mask(text: str) -> str:
    """Return text of the same length with skipped regions blanked.

    Every char in a skipped region becomes a space except newlines. Skipped:
    a YAML front-matter block (--- at the very start through the next ---),
    off/on markers, fenced and inline code, URLs, emails, paths, ﴿…﴾.
    """
    out = list(text)
    for m in _SKIP_RE.finditer(text):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def iter_words(masked: str) -> Iterator[Tuple[int, int, str]]:
    for m in _WORD_RE.finditer(masked):
        yield m.start(), m.end(), m.group()


def stem_candidates(word: str) -> List[str]:
    """Word without diacritics, then progressively stripped of clitics.

    Order: و/ف, then ب/ل/ك, then ال (لل gives the stem). Most-stripped last,
    no duplicates, nothing shorter than 2 letters.
    """
    cur = _DIACRITIC_RE.sub("", word)
    out = [cur]

    def step(new: str) -> str:
        if len(new) < 2:
            return cur
        if new not in out:
            out.append(new)
        return new

    if cur[:1] in ("و", "ف"):
        cur = step(cur[1:])
    if cur.startswith("لل"):
        cur = step(cur[2:])
    elif cur[:1] in ("ب", "ل", "ك"):
        cur = step(cur[1:])
    if cur.startswith("ال"):
        cur = step(cur[2:])
    return out


def line_col(text: str, offset: int) -> Tuple[int, int]:
    """1-based (line, column) of offset."""
    line = text.count("\n", 0, offset) + 1
    col = offset - (text.rfind("\n", 0, offset) + 1) + 1
    return line, col
