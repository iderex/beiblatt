"""Put the guard on this interpreter, and go no further without it.

Every script beside this one attempts something the suite must never do. Each
attempt is safe only because the guard refuses it before the interpreter acts,
so the attempt is made only where the guard is demonstrably present. install()
raises rather than returns when it cannot hold, and the check below is the
second half of the same statement.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gate.headless import install, installed  # noqa: E402  the path comes first


def under_guard() -> None:
    install()
    if not installed():
        raise SystemExit("the guard is not on this interpreter; nothing is attempted")
