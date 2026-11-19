"""Core data model for the Arabic checker."""
from dataclasses import dataclass
from typing import Optional

SEVERITIES = ("fix", "error", "warn", "info")


@dataclass(frozen=True)
class Finding:
    """One issue. start/end are offsets into the full text.

    replacement is set only for ``fix`` findings.
    """

    start: int
    end: int
    severity: str
    rule: str
    message: str
    suggestion: Optional[str] = None
    replacement: Optional[str] = None
