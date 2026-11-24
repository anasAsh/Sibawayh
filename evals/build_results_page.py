#!/usr/bin/env python3
"""Build the full-results pages for GitHub Pages from one judged run.

RUN is a folder under evals/results/ with baseline/ and skill/ answers and
one key-N.csv (from pair.py) and scores-N.csv (from the judge) per judging.
Writes docs/results/index.html, docs/ar/results/index.html and
docs/results/results.csv (every score, unblinded).

Usage: python3 evals/build_results_page.py evals/results/2026-11-23
"""
import csv
import glob
import hashlib
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "skills", "arabic-writing", "scripts"))
from archeck.text import iter_words, mask  # noqa: E402

CATS = ["grammar", "spelling", "translationese", "register", "formatting"]
MODES = ["baseline", "skill"]
TASKS = ["email", "docs", "social", "tech_explain", "translate"]
REPO = "https://github.com/anasAsh/Sibawayh"
SITE = "https://anasash.github.io/Sibawayh/"

STRINGS = {
    "en": {
        "dir": "ltr", "out": "results", "up": "../", "other": "../ar/results/",
        "other_label": "العربية", "other_lang": "ar",
        "repo": "Sibawayh on GitHub",
        "back": "How it is tested",
        "title": "Full test results",
        "desc": "All 100 requests of the Sibawayh blind comparison, both answers to each, and the errors the judge counted in every answer.",
        "lede": "All 100 requests, both answers to each one, and the errors the judge counted in every answer in each of the three judgings.",
        "ran": "The test ran on %s. Claude Code answered each request twice, once as it is and once with Sibawayh. GPT then counted the errors in both answers without knowing which was which, three times. <a href=\"%s\">How the test works</a>.",
        "h_summary": "Summary",
        "cap_summary": "The three judgings",
        "per100": "Errors per 100 words",
        "pref_head": "Answer the judge preferred",
        "change": "Change", "tie": "Tie", "mean": "Mean",
        "words_note": "%s pairs, %s words without the skill and %s with it.",
        "h_all": "The %d requests",
        "read1": "Open a request to read both answers and the judge's counts. The answers are shown as plain text, as the judge read them. Each line takes its direction from its first letter, as most apps do, so a line that starts with a Latin word is aligned to the left.",
        "read2": "These are an AI judge's counts, not a native reader's. If you disagree with a count, <a href=\"%s/issues\">open an issue</a> and name the request.",
        "all": "All",
        "f_skill": "Only requests where the judge counted an error in the answer with the skill",
        "f_base": "Only requests where the judge preferred the answer without the skill",
        "showing": "Showing %s of %s",
        "col_req": "Request", "col_err": "Errors, mean of 3 judgings",
        "baseline": "Without the skill", "skill": "With Sibawayh",
        "baseline_short": "Without", "skill_short": "With",
        "words": "%s words",
        "judging": ["Judging 1", "Judging 2", "Judging 3"],
        "cats": {"grammar": "Grammar", "spelling": "Spelling", "translationese": "Translationese",
                 "register": "Register", "formatting": "Formatting"},
        "total": "Total", "over": "Over-corrections",
        "cap_scores": "Errors the judge counted",
        "preferred": "Preferred",
        "tasks": {"email": "Emails", "docs": "Documentation", "social": "Social posts",
                  "tech_explain": "Technical explanations", "translate": "Translation"},
        "h_files": "The files",
        "files": "<a href=\"%s\">Every score in one CSV file</a>, with the labels already matched to the answers. The original files are in the repository: <a href=\"%s\">the answers, the keys that record which answer was shown as A and which as B, and the judge's score files</a>, and <a href=\"%s\">the instructions the judge received</a>.",
        "footer": "Sibawayh is open source under the MIT licence.",
    },
    "ar": {
        "dir": "rtl", "out": os.path.join("ar", "results"), "up": "../", "other": "../../results/",
        "other_label": "English", "other_lang": "en",
        "repo": "«سيبويه» على GitHub",
        "back": "كيف نختبر «سيبويه»؟",
        "title": "نتائج الاختبار كاملة",
        "desc": "الطلبات المئة كلها في اختبار «سيبويه»، وإجابتا كل طلب، والأخطاء التي أحصاها المحكّم في كل إجابة.",
        "lede": "في هذه الصفحة الطلبات المئة كلها، وإجابتا كل طلب، والأخطاء التي أحصاها المحكّم في كل إجابة في جولات التحكيم الثلاث.",
        "ran": "أُجري الاختبار في %s. أجاب Claude Code عن كل طلب مرتين: مرة كما هو، ومرة مع «سيبويه». ثم أحصى GPT أخطاء الإجابتين ثلاث مرات، دون أن يعرف أيهما كُتبت بالمهارة. <a href=\"%s\">شرح طريقة الاختبار</a>.",
        "h_summary": "ملخص النتائج",
        "cap_summary": "جولات التحكيم الثلاث",
        "per100": "الأخطاء في كل 100 كلمة",
        "pref_head": "الإجابة التي فضّلها المحكّم",
        "change": "التغيّر", "tie": "تعادل", "mean": "المتوسط",
        "words_note": "عدد الأزواج %s، وفيها %s كلمة دون المهارة و%s كلمة معها.",
        "h_all": "الطلبات المئة",
        "read1": "افتح أي طلب لتقرأ إجابتيه وما أحصاه المحكّم فيهما. تُعرض الإجابات نصًّا خامًا كما قرأها المحكّم. ويأخذ كل سطر اتجاهه من أول حرف فيه، كما في أغلب التطبيقات، فالسطر الذي يبدأ بكلمة لاتينية يظهر محاذيًا لليسار.",
        "read2": "هذه الأعداد أحصاها نموذج ذكاء اصطناعي وليس قارئًا من أهل العربية. وإن خالفتَ المحكّم في عدد منها <a href=\"%s/issues\">فافتح تذكرة (issue) في المستودع</a> واذكر معرّف الطلب.",
        "all": "الكل",
        "f_skill": "أظهر فقط الطلبات التي أحصى المحكّم خطأً في إجابة المهارة عنها",
        "f_base": "أظهر فقط الطلبات التي فضّل المحكّم فيها الإجابة التي دون المهارة",
        "showing": "المعروض: %s من %s",
        "col_req": "الطلب", "col_err": "متوسط عدد الأخطاء في الجولات الثلاث",
        "baseline": "دون المهارة", "skill": "مع «سيبويه»",
        "baseline_short": "دونها", "skill_short": "معها",
        "words": "عدد الكلمات: %s",
        "judging": ["الجولة الأولى", "الجولة الثانية", "الجولة الثالثة"],
        "cats": {"grammar": "النحو", "spelling": "الإملاء", "translationese": "الترجمة الحرفية",
                 "register": "المستوى اللغوي", "formatting": "التنسيق"},
        "total": "المجموع", "over": "التصحيح الزائد",
        "cap_scores": "الأخطاء التي أحصاها المحكّم",
        "preferred": "الإجابة المفضّلة",
        "tasks": {"email": "رسائل البريد الإلكتروني", "docs": "التوثيق", "social": "منشورات التواصل الاجتماعي",
                  "tech_explain": "الشروح التقنية", "translate": "الترجمة"},
        "h_files": "الملفات",
        "files": "<a href=\"%s\">الدرجات كلها في ملف واحد</a> بصيغة القيم المفصولة بفواصل (CSV)، وقد قُرنت فيه كل درجة بإجابتها. والملفات الأصلية في المستودع: <a href=\"%s\">الإجابات، ومفاتيح الترتيب التي تبيّن أي الإجابتين عُرضت أولًا، وملفات درجات المحكّم</a>، ثم <a href=\"%s\">التعليمات التي تلقّاها المحكّم</a> (بالإنجليزية).",
        "footer": "«سيبويه» مفتوح المصدر برخصة MIT.",
    },
}
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"]
MONTHS_AR = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس",
             "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def load(run):
    """Return (prompts, judgings); each judging maps id -> scores and preference."""
    with open(os.path.join(HERE, "prompts.tsv"), encoding="utf-8") as f:
        prompts = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    for p in prompts:
        p["text"], p["words"] = {}, {}
        for m in MODES:
            with open(os.path.join(run, m, p["id"] + ".txt"), encoding="utf-8") as f:
                p["text"][m] = f.read().strip()
            p["words"][m] = sum(1 for _ in iter_words(mask(p["text"][m])))
    judgings = []
    for key_path in sorted(glob.glob(os.path.join(run, "key-*.csv"))):
        with open(key_path, encoding="utf-8") as f:
            key = {r["pair"]: r for r in csv.DictReader(f)}
        texts = {p["id"]: p["text"] for p in prompts}
        j = {}
        with open(key_path.replace("key-", "scores-"), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                k = key[r["pair"].zfill(2)]
                e = j.setdefault(k["id"], {"pref": "tie", "over": 0})
                if r["response"] == "pref":
                    v = r["grammar"].strip()
                    e["pref"] = k[v.lower()] if v in ("A", "B") else "tie"
                    continue
                mode = k[r["response"].lower()]
                sha = k.get(r["response"].lower() + "_sha1")
                if sha and sha != hashlib.sha1(texts[k["id"]][mode].encode("utf-8")).hexdigest():
                    sys.exit("%s/%s.txt is not the answer the judge saw" % (mode, k["id"]))
                e[mode] = {c: int(r[c] or 0) for c in CATS}
                if mode == "skill":
                    e["over"] = int(r.get("over_corrections") or 0)
        missing = [p["id"] for p in prompts if not all(m in j.get(p["id"], {}) for m in MODES)]
        if missing:
            sys.exit("%s: no scores for %s" % (key_path, ", ".join(missing)))
        judgings.append(j)
    return prompts, judgings


def num(x):
    return "%.1f" % x if x else "0"


def answer_html(text):
    """Plain text, one block per line; fenced code stays left-to-right."""
    out, code = [], None
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            if code is None:
                code = []
            else:
                out.append('<pre dir="ltr">%s</pre>' % html.escape("\n".join(code)))
                code = None
        elif code is not None:
            code.append(line)
        elif line.strip():
            out.append('<p dir="auto">%s</p>' % html.escape(line))
        else:
            out.append('<p class="gap"></p>')
    if code:
        out.append('<pre dir="ltr">%s</pre>' % html.escape("\n".join(code)))
    return "\n".join(out)


def ltr(s):
    return '<span dir="ltr">%s</span>' % s


def item_html(p, judgings, s):
    pid = p["id"]
    js = [j[pid] for j in judgings]
    mean = {m: sum(sum(e[m].values()) for e in js) / len(js) for m in MODES}
    pref_base = any(e["pref"] == "baseline" for e in js)
    cols = []
    for m in MODES:
        rows = "".join(
            "<tr%s><th>%s</th>%s</tr>" % (
                "" if c in CATS else ' class="total"', s["cats"].get(c, s["total"]),
                "".join('<td class="n">%d</td>' % (e[m][c] if c in CATS else sum(e[m].values())) for e in js))
            for c in CATS + ["total"])
        head = "".join('<th class="n">%s</th>' % x for x in s["judging"])
        cols.append(
            '<div class="resp">\n<h3>%s <span class="who">%s</span></h3>\n'
            '<div class="scroll"><table class="scores"><caption>%s</caption>'
            '<thead><tr><th></th>%s</tr></thead><tbody>%s</tbody></table></div>\n'
            '<div class="ans" lang="ar" dir="rtl">\n%s\n</div>\n</div>' % (
                s[m], s["words"] % ltr(p["words"][m]), s["cap_scores"], head, rows,
                answer_html(p["text"][m])))
    names = {"baseline": s["baseline"], "skill": s["skill"], "tie": s["tie"]}
    verdict = "<dl class=\"verdict\"><dt>%s</dt><dd>%s</dd><dt>%s</dt><dd>%s</dd></dl>" % (
        s["preferred"], " · ".join(names[e["pref"]] for e in js),
        s["over"], ltr(" · ".join(str(e["over"]) for e in js)))
    return (
        '<details class="item" id="%s" data-task="%s"%s%s>\n'
        '<summary><code>%s</code><span class="q" dir="auto" lang="%s">%s</span>'
        '<span class="n b">%s</span><span class="n s">%s</span></summary>\n'
        '<div class="pair-cols">\n%s\n</div>\n%s\n</details>' % (
            pid, p["task_type"],
            " data-skill-err" if mean["skill"] else "", " data-pref-base" if pref_base else "",
            pid, "ar" if any("؀" <= ch <= "ۿ" for ch in p["prompt"][:40]) else "en",
            html.escape(p["prompt"]), num(mean["baseline"]), num(mean["skill"]),
            "\n".join(cols), verdict))


def summary_html(prompts, judgings, s):
    words = {m: sum(p["words"][m] for p in prompts) for m in MODES}
    rows, rates = [], {m: [] for m in MODES}
    for i, j in enumerate(judgings):
        r = {m: 100.0 * sum(sum(e[m].values()) for e in j.values()) / words[m] for m in MODES}
        for m in MODES:
            rates[m].append(r[m])
        prefs = [e["pref"] for e in j.values()]
        rows.append(
            "<tr><th>%s</th><td class=\"n\">%.2f</td><td class=\"n\">%.2f</td><td class=\"n\">%s</td>"
            "<td class=\"n\">%d</td><td class=\"n\">%d</td><td class=\"n\">%d</td><td class=\"n\">%d</td></tr>" % (
                s["judging"][i], r["baseline"], r["skill"],
                "−%.0f%%" % (100 * (1 - r["skill"] / r["baseline"])),
                prefs.count("baseline"), prefs.count("skill"), prefs.count("tie"),
                sum(e["over"] for e in j.values())))
    b, k = (sum(rates[m]) / len(judgings) for m in MODES)
    rows.append(
        "<tr class=\"total\"><th>%s</th><td class=\"n\">%.2f</td><td class=\"n\">%.2f</td><td class=\"n\">%s</td>"
        "<td></td><td></td><td></td><td></td></tr>" % (s["mean"], b, k, "−%.0f%%" % (100 * (1 - k / b))))
    return (
        '<div class="scroll"><table><caption>%s</caption>\n<thead>'
        '<tr><th rowspan="2"></th><th colspan="3" class="grp">%s</th><th colspan="3" class="grp">%s</th>'
        '<th rowspan="2" class="n">%s</th></tr>\n'
        '<tr><th class="n">%s</th><th class="n">%s</th><th class="n">%s</th>'
        '<th class="n">%s</th><th class="n">%s</th><th class="n">%s</th></tr></thead>\n'
        "<tbody>%s</tbody></table></div>\n<p class=\"note\">%s</p>" % (
            s["cap_summary"], s["per100"], s["pref_head"], s["over"],
            s["baseline"], s["skill"], s["change"], s["baseline"], s["skill"], s["tie"],
            "\n".join(rows),
            s["words_note"] % (ltr(len(prompts)), ltr("{:,}".format(words["baseline"])),
                               ltr("{:,}".format(words["skill"])))))


SCRIPT = """<script>
(function () {
  var items = [].slice.call(document.querySelectorAll('details.item'));
  var tasks = [].slice.call(document.querySelectorAll('.filters button'));
  var fs = document.getElementById('f-skill'), fb = document.getElementById('f-base');
  var count = document.getElementById('count'), task = '';
  function apply() {
    var n = 0;
    items.forEach(function (d) {
      var show = (!task || d.dataset.task === task) &&
        (!fs.checked || d.hasAttribute('data-skill-err')) &&
        (!fb.checked || d.hasAttribute('data-pref-base'));
      d.hidden = !show;
      if (show) n++;
    });
    count.textContent = count.dataset.t.replace('%s', n).replace('%s', items.length);
  }
  tasks.forEach(function (b) {
    b.addEventListener('click', function () {
      task = b.dataset.task;
      tasks.forEach(function (o) { o.setAttribute('aria-pressed', o === b); });
      apply();
    });
  });
  fs.addEventListener('change', apply);
  fb.addEventListener('change', apply);
  document.getElementById('filters').hidden = false;
  apply();
  function fromHash() {
    var d = location.hash && document.getElementById(location.hash.slice(1));
    if (d && d.tagName === 'DETAILS') { d.hidden = false; d.open = true; d.scrollIntoView(); }
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
</script>"""


def page_html(lang, prompts, judgings, date):
    s = STRINGS[lang]
    y, mo, d = (int(x) for x in date.split("-"))
    when = "%d %s %d" % (d, (MONTHS_EN if lang == "en" else MONTHS_AR)[mo - 1], y)
    root = "../" if lang == "en" else "../../"
    url = SITE + ("results/" if lang == "en" else "ar/results/")
    alt = SITE + ("ar/results/" if lang == "en" else "results/")
    run_url = "%s/tree/main/evals/results/%s" % (REPO, date)
    buttons = '<button type="button" data-task="" aria-pressed="true">%s</button>' % s["all"] + "".join(
        '<button type="button" data-task="%s" aria-pressed="false">%s</button>' % (t, s["tasks"][t]) for t in TASKS)
    return """<!doctype html>
<html lang="{lang}" dir="{dir}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}assets/social-preview.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;600&family=Readex+Pro:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css">
<link rel="alternate" hreflang="{lang}" href="{url}">
<link rel="alternate" hreflang="{other_lang}" href="{alt}">
</head>
<body>
<!-- Generated by evals/build_results_page.py; edit that script, not this file. -->
<div class="wrap">

<header class="top">
  <p class="repo"><span><a href="{up}">{back}</a> · <a href="{repo_url}">{repo}</a></span> <a href="{other}" lang="{other_lang}" hreflang="{other_lang}">{other_label}</a></p>
  <h1>{title}</h1>
  <div class="text">
    <p class="lede">{lede}</p>
    <p>{ran}</p>
  </div>
</header>

<section id="summary">
  <h2>{h_summary}</h2>
  {summary}
</section>

<section id="requests">
  <div class="text">
    <h2>{h_all}</h2>
    <p>{read1}</p>
    <p class="note">{read2}</p>
  </div>
  <div class="filters" id="filters" hidden>
    <div class="tasks">{buttons}</div>
    <label><input type="checkbox" id="f-skill"> {f_skill}</label>
    <label><input type="checkbox" id="f-base"> {f_base}</label>
    <p class="note" id="count" data-t="{showing}" aria-live="polite"></p>
  </div>
  <div class="items-head" aria-hidden="true"><span>{col_req}</span><span class="e">{col_err}</span><span class="n b">{baseline_short}</span><span class="n s">{skill_short}</span></div>
{items}
</section>

<section id="files">
  <div class="text">
    <h2>{h_files}</h2>
    <p>{files}</p>
  </div>
</section>

<footer>
  <p>{footer}</p>
</footer>

</div>
{script}
</body>
</html>
""".format(
        lang=lang, dir=s["dir"], title=s["title"], desc=html.escape(s["desc"], quote=True), site=SITE,
        root=root, url=url, alt=alt, other_lang=s["other_lang"], up=s["up"], back=s["back"],
        repo_url=REPO, repo=s["repo"], other=s["other"], other_label=s["other_label"],
        lede=s["lede"], ran=s["ran"] % (when, s["up"] + "#blind"),
        h_summary=s["h_summary"], summary=summary_html(prompts, judgings, s),
        h_all=s["h_all"] % len(prompts) if "%d" in s["h_all"] else s["h_all"],
        read1=s["read1"], read2=s["read2"] % REPO, buttons=buttons,
        f_skill=s["f_skill"], f_base=s["f_base"], showing=s["showing"],
        col_req=s["col_req"], col_err=s["col_err"],
        baseline_short=s["baseline_short"], skill_short=s["skill_short"],
        items="\n".join(item_html(p, judgings, s) for p in prompts),
        h_files=s["h_files"],
        files=s["files"] % (root + "results/results.csv", run_url, REPO + "/blob/main/evals/ai_judge.md"),
        footer=s["footer"], script=SCRIPT)


def write_csv(path, prompts, judgings):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "task_type", "judging", "answer", "words"] + CATS + ["over_corrections", "preferred"])
        for p in prompts:
            for i, j in enumerate(judgings, 1):
                e = j[p["id"]]
                for m in MODES:
                    w.writerow([p["id"], p["task_type"], i, m, p["words"][m]] + [e[m][c] for c in CATS]
                               + [e["over"] if m == "skill" else "", e["pref"]])


def main(argv=None) -> int:
    args = argv or sys.argv[1:]
    if len(args) != 1:
        sys.exit(__doc__)
    run = os.path.abspath(args[0])
    prompts, judgings = load(run)
    date = os.path.basename(run)
    for lang, s in STRINGS.items():
        out = os.path.join(ROOT, "docs", s["out"])
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html(lang, prompts, judgings, date))
    write_csv(os.path.join(ROOT, "docs", "results", "results.csv"), prompts, judgings)
    print("Wrote docs/results/index.html, docs/ar/results/index.html and docs/results/results.csv "
          "(%d requests, %d judgings)" % (len(prompts), len(judgings)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
