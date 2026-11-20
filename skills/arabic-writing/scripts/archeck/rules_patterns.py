"""Consistency and pattern rules. Every rule has the signature rule(text, masked, opts).

None of these rules is `fix` severity, so none sets `replacement`; the corrected
form, when there is one, is in `suggestion`. All rules scan `masked`, so code,
URLs, paths and Qur'an quotes are never looked at.
"""
import re
from typing import Dict, Iterator, List, Tuple

from .data import load_list, load_tsv
from .model import Finding
from .text import ARABIC_LETTER, has_arabic, iter_words

_DIAC = "ً-ٰٟ"
_DIAC_RE = re.compile("[" + _DIAC + "]")
_EDGE = "(?:" + ARABIC_LETTER + "|[" + _DIAC + "])"
_NB = "(?<!" + _EDGE + ")"  # no Arabic letter or mark before
_NA = "(?!" + _EDGE + ")"  # no Arabic letter or mark after
_WORD = ARABIC_LETTER + "(?:" + ARABIC_LETTER + "|[" + _DIAC + "])*"
_TANWEEN = "ًٌٍ"
_SHADDA = "ّ"

Opts = Dict[str, str]


def _plain(word: str) -> str:
    return _DIAC_RE.sub("", word)


def _lines(masked: str) -> Iterator[Tuple[int, str]]:
    """(offset, line) for each line, without the line break."""
    pos = 0
    for line in masked.split("\n"):
        yield pos, line.rstrip("\r")
        pos += len(line) + 1


# --- digit-mix ---------------------------------------------------------------

_DIGIT_RUN = re.compile("[0-9]+|[٠-٩]+")
_LATIN = re.compile("[A-Za-z]")


def _in_latin_token(line: str, a: int, b: int) -> bool:
    """Digits glued to, or right after, a Latin word belong to it (not prose)."""
    before = line[a - 1] if a > 0 else ""
    after = line[b] if b < len(line) else ""
    if _LATIN.match(before) or _LATIN.match(after):
        return True
    # COVID-19, Python 3, Windows 11: a number tied to a Latin word.
    return a >= 2 and before in "-_ " and _LATIN.match(line[a - 2]) is not None


def digit_mix(text: str, masked: str, opts: Opts) -> List[Finding]:
    runs = []
    for off, line in _lines(masked):
        if not has_arabic(line):
            continue
        for m in _DIGIT_RUN.finditer(line):
            if _in_latin_token(line, m.start(), m.end()):
                continue
            system = "western" if m.group()[0] <= "9" else "arabic"
            runs.append((off + m.start(), off + m.end(), m.group(), system))
    mode = opts.get("digits", "auto")
    if mode not in ("western", "arabic"):
        ar = sum(1 for r in runs if r[3] == "arabic")
        mode = "arabic" if ar > len(runs) - ar else "western"
    out = []
    for a, b, run, system in runs:
        if system == mode:
            continue
        if mode == "western":
            conv = "".join(chr(ord(c) - 0x0660 + ord("0")) for c in run)
            name = "Western (0-9)"
        else:
            conv = "".join(chr(ord(c) - ord("0") + 0x0660) for c in run)
            name = "Arabic-Indic (٠-٩)"
        out.append(Finding(a, b, "warn", "digit-mix",
                           "Mixed digit systems; this text uses " + name + " digits",
                           suggestion=conv))
    return out


# --- tanween-mixed -------------------------------------------------------------

_ALIF_FIRST = "اً"  # اً
_TANWEEN_FIRST = "ًا"  # ًا


def tanween_mixed(text: str, masked: str, opts: Opts) -> List[Finding]:
    if _ALIF_FIRST not in masked or _TANWEEN_FIRST not in masked:
        return []
    out = []
    for a, b, w in iter_words(masked):
        if _ALIF_FIRST in w:
            out.append(Finding(a, b, "info", "tanween-mixed",
                               "Tanween is written both ways; the convention is ـًا "
                               "(tanween on the letter before the alif)",
                               suggestion=w.replace(_ALIF_FIRST, _TANWEEN_FIRST)))
    return out


# --- spelling-mixed ------------------------------------------------------------

_SPELLINGS = (
    ("مسئول", "مسؤول", "Convention: مسؤول (hamza on waw), not مسئول"),
    ("مائة", "مئة", "Convention: مئة, not مائة"),
    ("مائت", "مئت", "Convention: مئتان/مئتين, not مائتان/مائتين"),
)


def spelling_mixed(text: str, masked: str, opts: Opts) -> List[Finding]:
    out = []
    for a, b, w in iter_words(masked):
        plain = _plain(w)
        for wrong, right, msg in _SPELLINGS:
            if wrong in plain:
                out.append(Finding(a, b, "info", "spelling-mixed", msg,
                                   suggestion=plain.replace(wrong, right)))
                break
    return out


# --- stray-english / rtl-line-start ----------------------------------------------

# Latin tokens; ones with digits (mp3, IPv6) are identifiers and skipped below.
_LATIN_WORD = re.compile("(?<![A-Za-z0-9])[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*")
_PARENS = re.compile(r"\([^()]*\)")


def stray_english(text: str, masked: str, opts: Opts) -> List[Finding]:
    acronyms = {a.lower() for a in load_list("acronyms.txt")}
    out = []
    for off, line in _lines(masked):
        if not has_arabic(line):
            continue
        inside = [(m.start(), m.end()) for m in _PARENS.finditer(line)]
        for m in _LATIN_WORD.finditer(line):
            tok = m.group()
            if len(tok) < 2 or re.search("[0-9]", tok) or tok.lower() in acronyms:
                continue
            if tok[0].isupper():
                continue  # a name or product (Docker, Google Analytics, UFW): keep it
            if any(s < m.start() and m.end() < e for s, e in inside):
                continue
            out.append(Finding(off + m.start(), off + m.end(), "info", "stray-english",
                               "English word in Arabic text; use the Arabic term, or "
                               "give the English in parentheses after it"))
    return out


_ARABIC_WORD = re.compile(ARABIC_LETTER + "+")


def english_line(text: str, masked: str, opts: Opts) -> List[Finding]:
    """A whole English prose line inside a mostly-Arabic document.

    Catches the agent switching to English for notes or caveats. Lines with
    any Arabic are left to stray-english; code is already masked.
    """
    arabic = len(_ARABIC_WORD.findall(masked))
    if arabic <= len(_LATIN_WORD.findall(masked)):
        return []
    out = []
    for off, line in _lines(masked):
        if has_arabic(line) or len(_LATIN_WORD.findall(line)) < 4:
            continue
        start = len(line) - len(line.lstrip())
        out.append(Finding(off + start, off + len(line.rstrip()), "warn", "english-line",
                           "English sentence in an Arabic answer; write notes and "
                           "caveats in Arabic too"))
    return out


_LEAD = re.compile(r"(?:[#>*+\-\s]+|\d+[.)](?=\s))*")


_TOKEN = re.compile("[A-Za-z0-9._-]*")


def rtl_line_start(text: str, masked: str, opts: Opts) -> List[Finding]:
    out = []
    for off, line in _lines(masked):
        if not has_arabic(line):
            continue
        i = _LEAD.match(line).end()
        # Only Latin letters and Western digits. Arabic-Indic digits (٠-٩) are
        # not flagged: they belong with Arabic text and are not used in code.
        if i < len(line) and re.match("[A-Za-z0-9]", line[i]):
            j = _TOKEN.match(line, i).end()
            while j > i + 1 and line[j - 1] in "._-":
                j -= 1
            what = "a Western digit" if line[i].isdigit() else "a Latin word"
            out.append(Finding(off + i, off + j, "warn", "rtl-line-start",
                               "Arabic line starts with " + what + "; it may render "
                               "left-to-right. Start the line with an Arabic word"))
    return out


# --- sawfa-lan -----------------------------------------------------------------

_SAWFA_LAN = re.compile(_NB + "سوف[" + _DIAC + r"]*\s+لن[" + _DIAC + "]*" + _NA)


def sawfa_lan(text: str, masked: str, opts: Opts) -> List[Finding]:
    return [
        Finding(m.start(), m.end(), "warn", "sawfa-lan",
                "سوف is not used with لن; لن alone negates the future",
                suggestion="لن")
        for m in _SAWFA_LAN.finditer(masked)
    ]


# --- jussive-nun -----------------------------------------------------------------

_JUSSIVE = frozenset(("لم", "ولم", "فلم"))
_SUBJUNCTIVE = frozenset(("لن", "ولن", "فلن", "أن", "وأن", "بأن", "وبأن", "كي", "لكي", "ولكي"))
_NUN_EXCEPT = frozenset(("يعنون", "تعنون", "تلفزيون"))


def _five_verbs_fix(verb: str, jussive: bool) -> str:
    """The verb with its ن dropped, or "" if it is not clearly one of الأفعال الخمسة.

    Only the plural ون (يذهبون) and, after لم, the feminine تـ...ين (تذهبين) are
    handled. Verbs whose own root ends in ون/ين (يكون، يتكون، يتعاون، يبيّن،
    تتبين، تستعين) are skipped: the part between the prefix and the ending is
    1 letter, or 2 letters starting with ت, or ends in ا, or is ست + 1 letter.
    """
    if verb in _NUN_EXCEPT or verb[:1] not in ("ي", "ت"):
        return ""
    if verb.endswith("ون"):
        new = verb[:-1] + "ا"
    elif jussive and verb.startswith("ت") and verb.endswith("ين"):
        new = verb[:-1]
    else:
        return ""
    mid = verb[1:-2]
    if len(mid) < 2 or (len(mid) == 2 and mid[0] == "ت") or mid.endswith("ا"):
        return ""
    if len(mid) == 3 and mid.startswith("ست"):
        return ""
    return new


_KASRA_LAM = "ل\u0650"
_CLAUSE_END = re.compile("[.،,!\n؟?]")


def _is_question(masked: str, pos: int) -> bool:
    """True if the clause from pos ends with a question mark."""
    m = _CLAUSE_END.search(masked, pos)
    return m is not None and m.group() in "؟?"


def jussive_nun(text: str, masked: str, opts: Opts) -> List[Finding]:
    words = list(iter_words(masked))
    out = []
    for (a1, b1, w1), (a2, b2, w2) in zip(words, words[1:]):
        if _SHADDA in w1 or masked[b1:a2].strip():
            continue
        p1 = _plain(w1)
        jussive = p1 in _JUSSIVE
        if not jussive and p1 not in _SUBJUNCTIVE:
            continue
        if jussive and (_KASRA_LAM in w1 or _is_question(masked, b2)):
            continue  # لِمَ "why" takes the indicative
        new = _five_verbs_fix(_plain(w2), jussive)
        if new:
            mood = "jussive (مجزوم)" if jussive else "subjunctive (منصوب)"
            out.append(Finding(a2, b2, "warn", "jussive-nun",
                               "After " + p1 + " the verb is " + mood + " and drops its ن",
                               suggestion=new))
    return out


# --- relative-after-indefinite -----------------------------------------------------

_RELATIVES = frozenset(("الذي", "التي", "الذين"))
_SUFFIXES = ("ه", "ها", "هم", "هن", "هما", "كم", "كن", "كما", "نا", "ي", "ك")
# Words that are definite, are not nouns, or are commonly in iḍāfa to a relative.
_DEFINITE = frozenset("""
هذا هذه هذان هذين هاتان هاتين هؤلاء ذلك تلك ذاك أولئك هنا هناك هنالك
هو هي هم هن هما أنا نحن أنت أنتم أنتن أنتما إياه إياها إياهم
من ما ماذا متى أين كيف لماذا أي أيها أيتها يا
في على عن إلى الى مع منذ مذ حتى لدى لدي عند حول ضد نحو عبر بين دون بدون
قبل بعد خلال أثناء طوال تجاه أمام خلف وراء فوق تحت ضمن حسب بحسب سوى إلا
غير مثل كل بعض جميع كافة معظم أغلب غالبية أغلبية أكثر أقل كثير قليل عدد نسبة
مجموع مجمل نصف ثلث ربع بقية باقي سائر أحد إحدى نفس ذات عين ذو ذي ذوي أولو أولي
إن أن لأن كأن لكن ليت لعل بل ثم أو أم لا لم لن قد لقد هل كي لكي إذ إذا لو لولا
كما مما عما فيما بما ربما إنما أما إما حيث خاصة سيما لاسيما فقط أيضا كذلك
كان يكون كانت ليس ليست ليسوا أصبح صار ظل بات قال جاء رأى عرف وجد فعل أحب شكر
فاز نجح حضر ذهب خرج دخل سأل حصل اختار شارك رفض بقي عاد ترك يعني تعني
خذ اختر اقرأ احترم ساعد اتبع اسأل اشكر
مصر لبنان سوريا تونس ليبيا فلسطين قطر عمان اليمن محمد أحمد علي عمر
""".split())


def _maybe_definite(word: str) -> bool:
    if any(ch in _TANWEEN for ch in word):
        return False
    plain = _plain(word)
    stems = [plain]
    if plain[:1] in ("و", "ف") and len(plain) > 2:
        stems.append(plain[1:])
    for s in list(stems):
        if s[:1] in ("ب", "ك") and len(s) > 2:
            stems.append(s[1:])
    for s in stems:
        if s.startswith("ال") or s.startswith("لل") or s in _DEFINITE:
            return True
    core = stems[1] if len(stems) > 1 and plain[:1] in ("و", "ف") else plain
    if core.endswith(_SUFFIXES):
        return True
    # Likely verbs: present tense, plural past, past with ت.
    if core.startswith("ي") and len(core) >= 3 and core not in ("يوم", "يد"):
        return True
    if core.endswith("وا"):
        return True
    if core.endswith("ت") and not core.endswith("ات"):
        return True
    if core[:2] in ("سي", "سن", "سأ", "ست") and not core.endswith(("ة", "ات")):
        return True
    return False


def relative_after_indefinite(text: str, masked: str, opts: Opts) -> List[Finding]:
    words = list(iter_words(masked))
    out = []
    for (a1, b1, w1), (a2, b2, w2) in zip(words, words[1:]):
        rel = _plain(w2)
        if rel not in _RELATIVES or masked[b1:a2].strip(" \t") or _maybe_definite(w1):
            continue
        noun = _plain(w1)
        out.append(Finding(a1, b2, "info", "relative-after-indefinite",
                           "Approximate check: " + rel + " after an indefinite noun. "
                           "Make the noun definite, or drop " + rel + " (an indefinite "
                           "noun takes a clause without a relative pronoun). Ignore if "
                           "the word is a proper name or a verb",
                           suggestion="ال" + noun + " " + rel))
    return out


# --- translationese-density ----------------------------------------------------------

_W = "[" + _DIAC + "]*"
_TAMMA = re.compile(_NB + "[وف]?" + "(?:يتم|تمت|تم)" + _W + _NA + r"[ \t]+" + _WORD)
_QAMA = re.compile(_NB + "[وف]?" + "(?:يقوم|قامت|قام)" + _W + _NA + r"[ \t]+" + "ب" + _WORD)
_MIN_QIBAL = re.compile(_NB + "من" + _W + r"[ \t]+" + "قبل" + _W + _NA + r"(?=[ \t]+(" + _WORD + "))")
_BISHAKL = re.compile(_NB + "[وف]?" + "بشكل" + _W + _NA + r"[ \t]+" + _WORD)
_NOT_AGENT = frozenset("""
في على عن إلى الى مع لم لا ما أن إن ولم ولا وما ثم حتى كما أو قد لقد وقد بل لكن ولكن
""".split())
_RATE = 3.0
_MIN_MATCHES = 2


def translationese_density(text: str, masked: str, opts: Opts) -> List[Finding]:
    n_words = sum(1 for _ in iter_words(masked))
    if not n_words:
        return []
    qibal = [m for m in _MIN_QIBAL.finditer(masked)
             if _plain(m.group(1)) not in _NOT_AGENT]
    groups = (
        ("تم/يتم", list(_TAMMA.finditer(masked))),
        ("قام/يقوم بـ", list(_QAMA.finditer(masked))),
        ("من قبل", qibal),
        ("بشكل", list(_BISHAKL.finditer(masked))),
    )
    total = sum(len(ms) for _, ms in groups)
    rate = total * 100.0 / n_words
    if total < _MIN_MATCHES or rate <= _RATE:
        return []
    first = min((m for _, ms in groups for m in ms), key=lambda m: m.start())
    counts = ", ".join(name + ": " + str(len(ms)) for name, ms in groups if ms)
    return [Finding(first.start(), first.end(), "info", "translationese-density",
                    "Translationese density %.1f per 100 words (%s); prefer direct "
                    "verbs (أُنشئ / أنشأ الفريق) over تم + masdar, قام بـ, من قبل, بشكل"
                    % (rate, counts))]


# --- maqsura-medial -------------------------------------------------------------

# ى only ends a word. Inside one it is a typo for ئ (وساىل) or ي, or a missing
# space (علىمقاومة).
_MEDIAL_YAA = re.compile("ى[\u064b-\u0652]*(?=" + ARABIC_LETTER + ")")


def maqsura_medial(text: str, masked: str, opts: Opts) -> List[Finding]:
    return [Finding(m.start(), m.start() + 1, "error", "maqsura-medial",
                    "ى only ends a word: inside a word write ئ or ي, or add the missing space",
                    suggestion="ئ or ي")
            for m in _MEDIAL_YAA.finditer(masked)]


# --- number-gender ----------------------------------------------------------------

# 3–10 (and بضع) take the opposite gender of the counted noun's singular.
# Each form, and the form of the other gender.
_NUM_SWAP = {
    "ثلاثة": "ثلاث", "أربعة": "أربع", "خمسة": "خمس", "ستة": "ست", "سبعة": "سبع",
    "ثمانية": "ثماني", "تسعة": "تسع", "عشرة": "عشر", "بضعة": "بضع",
}
_NUM_SWAP.update({f: m for m, f in list(_NUM_SWAP.items())})
_NUM_SWAP["ثمان"] = "ثمانية"
_NUM_PREFIX = re.compile("^(?:[وفبلك]|[وف][بلك])?(?:ال)?")


def number_gender(text: str, masked: str, opts: Opts) -> List[Finding]:
    nouns = {r["plural"]: (r["gender"], r["singular"]) for r in load_tsv("number_nouns.tsv")}
    words = list(iter_words(masked))
    out = []
    for (a1, b1, w1), (a2, b2, w2) in zip(words, words[1:]):
        if masked[b1:a2].strip() or "\u064f" in w1:
            continue  # not adjacent, or خُمس/عُشر "a fifth/tenth"
        noun = nouns.get(_plain(w2))
        plain = _plain(w1)
        # The whole word first, so بضعة is not read as بـ + ضعة.
        cut = 0 if plain in _NUM_SWAP else _NUM_PREFIX.match(plain).end()
        prefix, form = plain[:cut], plain[cut:]
        if noun is None or form not in _NUM_SWAP:
            continue
        gender, singular = noun
        if (gender == "m") != form.endswith("ة"):  # ثلاثة/ثمانية suit a masculine singular
            out.append(Finding(a1, b2, "error", "number-gender",
                               "3–10 take the opposite gender of the singular (%s is %s)"
                               % (singular, "masculine" if gender == "m" else "feminine"),
                               suggestion=prefix + _NUM_SWAP[form] + " " + _plain(w2)))
    return out


RULES = [
    maqsura_medial,
    number_gender,
    digit_mix,
    tanween_mixed,
    spelling_mixed,
    stray_english,
    english_line,
    rtl_line_start,
    sawfa_lan,
    jussive_nun,
    relative_after_indefinite,
    translationese_density,
]
