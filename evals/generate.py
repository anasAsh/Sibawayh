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
    # Both modes get the same tools, so only the skill differs.
    cmd = ["claude", "-p", prompt, "--output-format", "text",
           *c.ISOLATE, "--allowedTools", c.ALLOWED_TOOLS]
    with c.workdir(with_skill) as d:
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True,
                           encoding="utf-8", timeout=c.TIMEOUT)
        files = written_files(d)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError("exit %s: %s" % (r.returncode, r.stderr.strip()))
    # A model may save the deliverable to a file and only summarise it; the
    # temp dir is deleted, so keep what it wrote.
    return r.stdout + "".join("\n\n--- file: %s ---\n%s" % f for f in files)


def written_files(d):
    """(relative path, text) of files the model wrote, outside .claude/ and /tmp."""
    out = []
    for root, dirs, names in os.walk(d):
        dirs[:] = sorted(x for x in dirs if x != ".claude")
        for n in sorted(names):
            path = os.path.join(root, n)
            try:
                with open(path, encoding="utf-8") as f:
                    out.append((os.path.relpath(path, d), f.read()))
            except (UnicodeDecodeError, OSError):
                continue
    return out


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
