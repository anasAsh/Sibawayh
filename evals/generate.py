#!/usr/bin/env python3
"""Generate responses with Claude Code headless.

  python3 evals/generate.py --mode baseline|skill [--only ID]

Writes evals/outputs/<mode>/<id>.txt (existing files are skipped). A failure
is recorded in evals/outputs/<mode>/<id>.error and the run continues.
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402


def run_one(prompt: str, with_skill: bool) -> str:
    # Prompt comes first: --allowedTools is variadic and would swallow it.
    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if with_skill:
        cmd += ["--allowedTools", c.ALLOWED_TOOLS]
    with c.workdir(with_skill) as d:
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True,
                           encoding="utf-8", timeout=c.TIMEOUT)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError("exit %s: %s" % (r.returncode, r.stderr.strip()))
    return r.stdout


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["baseline", "skill"])
    ap.add_argument("--only")
    a = ap.parse_args(argv)
    c.refuse_if_globally_installed()

    prompts = c.read_tsv(os.path.join(c.HERE, "prompts.tsv"))
    if a.only:
        prompts = [p for p in prompts if p["id"] == a.only]
        if not prompts:
            sys.exit("no such id: %s" % a.only)
    out_dir = os.path.join(c.HERE, "outputs", a.mode)
    os.makedirs(out_dir, exist_ok=True)

    for p in prompts:
        out = os.path.join(out_dir, p["id"] + ".txt")
        err = os.path.join(out_dir, p["id"] + ".error")
        if os.path.exists(out):
            print("skip  %s (exists)" % p["id"])
            continue
        try:
            text = run_one(p["prompt"], a.mode == "skill")
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
            if os.path.exists(err):
                os.remove(err)
            print("ok    %s" % p["id"])
        except Exception as e:  # includes TimeoutExpired
            with open(err, "w", encoding="utf-8") as f:
                f.write("%s: %s\n" % (type(e).__name__, e))
            print("FAIL  %s (%s)" % (p["id"], type(e).__name__))
    return 0


if __name__ == "__main__":
    sys.exit(main())
