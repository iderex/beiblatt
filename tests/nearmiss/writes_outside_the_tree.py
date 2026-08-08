"""A test that writes where it was not asked to.

A suite that writes outside the repository and the temporary directory leaves
things on the machine that ran it, and the person who finds them later has no
way to tell which run put them there. The guard refuses the open, so the file
is never created; the removal below is for the case where the refusal is
missing, so that proving the guard bites does not itself leave the mess.
"""

from pathlib import Path

from guarded import under_guard

under_guard()

target = Path.home() / ".beiblatt-a-near-miss-that-should-not-exist"
try:
    target.write_text("the guard did not refuse this\n", encoding="utf-8")
finally:
    if target.exists():
        target.unlink()

print("not refused: a file was written outside the tree")
