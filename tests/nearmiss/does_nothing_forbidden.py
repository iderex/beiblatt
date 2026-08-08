"""The valid neighbour of the four beside it.

Everything an ordinary test does, under the same guard: import from the
standard library, write into the temporary directory, and spawn a program that
is not a privilege tool. If this one is refused, the guard is refusing the work
rather than the mistake, which is the failure that would get it turned off.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from guarded import under_guard

under_guard()

import json  # noqa: E402,F401  an ordinary import

with tempfile.TemporaryDirectory() as temporary:
    (Path(temporary) / "written").write_text("ordinary\n", encoding="utf-8")

subprocess.run([sys.executable, "-c", "pass"], capture_output=True, timeout=60, check=True)

print("nothing refused")
