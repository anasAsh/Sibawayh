import os
import sys

_SCRIPTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "arabic-writing", "scripts",
)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
