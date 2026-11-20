#!/usr/bin/env python3
"""Download Arabic Wikipedia featured articles as plain text, for the
over-correction check (corpus_check.py). Stdlib only; needs network.

Usage: python3 evals/fetch_wiki.py [--limit 50] [--out evals/corpus/wiki]
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

API = "https://ar.wikipedia.org/w/api.php"
CATEGORY = "تصنيف:مقالات_مختارة"
UA = "SibawayhEval/0.1 (https://github.com/anasAsh/Sibawayh)"
_HERE = os.path.dirname(os.path.abspath(__file__))


def api(**params):
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def featured(limit):
    """First `limit` featured articles, in category order."""
    out, cont = [], {}
    while len(out) < limit:
        data = api(action="query", list="categorymembers", cmtitle=CATEGORY,
                   cmnamespace=0, cmlimit=min(500, limit - len(out)), **cont)
        out += data["query"]["categorymembers"]
        if "continue" not in data:
            break
        cont = {"cmcontinue": data["continue"]["cmcontinue"]}
    return out[:limit]


def extract(pageid):
    data = api(action="query", prop="extracts", explaintext=1, pageids=pageid)
    return data["query"]["pages"][str(pageid)].get("extract", "")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--out", default=os.path.join(_HERE, "corpus", "wiki"))
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for page in featured(args.limit):
        path = os.path.join(args.out, "%d.txt" % page["pageid"])
        if os.path.exists(path):
            continue
        text = extract(page["pageid"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("ok   %s (%d chars)" % (page["title"], len(text)))
        time.sleep(0.5)


if __name__ == "__main__":
    main()
