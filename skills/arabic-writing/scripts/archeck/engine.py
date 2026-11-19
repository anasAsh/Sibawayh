"""Run the rules and apply fixes."""
from typing import List

from . import rules_fix, rules_lists, rules_patterns
from .data import load_list
from .model import Finding
from .text import iter_words, mask, stem_candidates

_MAX_ROUNDS = 5


def _approved(span: str) -> bool:
    """True if span is exactly one Arabic word that is an approved form."""
    words = list(iter_words(span))
    if len(words) != 1 or words[0][0] != 0 or words[0][1] != len(span):
        return False
    approved = load_list("approved_forms.txt")
    return any(c in approved for c in stem_candidates(span))


def check(text: str, digits: str = "auto") -> List[Finding]:
    masked = mask(text)
    opts = {"digits": digits}
    found = []
    for rule in rules_fix.RULES + rules_lists.RULES + rules_patterns.RULES:
        found.extend(rule(text, masked, opts))
    kept = [f for f in found if not _approved(text[f.start:f.end])]
    return sorted(kept, key=lambda f: (f.start, f.rule))


def apply_fixes(text: str, findings: List[Finding]) -> str:
    cands = sorted(
        (f for f in findings if f.severity == "fix" and f.replacement is not None),
        key=lambda f: (f.start, f.end),
    )
    chosen = []
    last_end = -1
    for f in cands:
        if f.start >= last_end:
            chosen.append(f)
            last_end = f.end
    for f in reversed(chosen):
        text = text[:f.start] + f.replacement + text[f.end:]
    return text


def fix_text(text: str, digits: str = "auto") -> str:
    for _ in range(_MAX_ROUNDS):
        new = apply_fixes(text, check(text, digits))
        if new == text:
            break
        text = new
    return text
