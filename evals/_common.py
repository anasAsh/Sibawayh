"""Shared helpers for generate.py and run_triggers.py (stdlib only)."""
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL_DIR = os.path.join(ROOT, "skills", "arabic-writing")
TIMEOUT = 300
ALLOWED_TOOLS = "Bash(python3:*),Read,Write"


def refuse_if_globally_installed():
    """Only checks; never creates or removes anything under ~/.claude."""
    p = os.path.expanduser("~/.claude/skills/arabic-writing")
    if os.path.lexists(p):
        sys.exit("Refusing to run: %s exists and would contaminate the "
                 "baseline. Unlink it yourself, run the evals, then relink."
                 % p)


@contextmanager
def workdir(with_skill: bool):
    """Fresh temp dir; with_skill links the skill at .claude/skills/."""
    d = tempfile.mkdtemp(prefix="arabic-eval-")
    try:
        if with_skill:
            os.makedirs(os.path.join(d, ".claude", "skills"))
            os.symlink(SKILL_DIR,
                       os.path.join(d, ".claude", "skills", "arabic-writing"))
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    head = lines[0].split("\t")
    return [dict(zip(head, l.split("\t", len(head) - 1)))
            for l in lines[1:] if l.strip()]
