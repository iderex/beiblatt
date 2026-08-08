"""A test that asks to run something with privilege.

The guard reads the name of the program being spawned and reads nothing after
it, so the argument here is the one that prints a usage message. That is
deliberate and it is the whole of the difference from what somebody would
really write: a spawn whose refusal never came would print help rather than ask
the person at the machine for anything. The path through the guard is the same
one `runas /user:... something` takes, because the name is all of what is
matched.
"""

import subprocess
import sys

from guarded import under_guard

under_guard()

tool = ["runas", "/?"] if sys.platform == "win32" else ["sudo", "-h"]
subprocess.run(tool, capture_output=True, timeout=30, check=False)

print("not refused: a privilege tool was spawned")
