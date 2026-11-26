"""Loaders for the data files in scripts/data."""
import os
from functools import lru_cache
from typing import Dict, FrozenSet, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _lines(name: str) -> List[str]:
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return [ln.rstrip("\r\n") for ln in f]


def _is_data(line: str) -> bool:
    return bool(line.strip()) and not line.startswith("#")


@lru_cache(maxsize=None)
def load_tsv(name: str) -> List[Dict[str, str]]:
    lines = [ln for ln in _lines(name) if _is_data(ln)]
    if not lines:
        return []
    header = lines[0].split("\t")
    return [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]


@lru_cache(maxsize=None)
def load_list(name: str) -> FrozenSet[str]:
    return frozenset(ln.strip() for ln in _lines(name) if _is_data(ln))
