"""The one line the gate is invoked as.

    .venv/bin/python -m gate

There is nothing else to learn. `--list` prints the declared legs and runs
none of them, which is what a reader wants when the question is what the gate
covers rather than whether this tree passes it.
"""

from __future__ import annotations

import sys
from typing import IO

from gate.legs import legs
from gate.run import Leg, walk

USAGE = """usage: python -m gate [--list]

Runs every leg in order and stops at the first failure. Exits 0 when nothing
failed and 1 when something did.

  --list   print the declared legs and what each one decides, run nothing
"""


def _list(declared: list[Leg], out: IO[str]) -> int:
    width = max((len(leg.name) for leg in declared), default=0)
    print(f"gate: {len(declared)} leg(s) declared, none run", file=out)
    for leg in declared:
        print(f"  {leg.name.ljust(width)}  {leg.decides}", file=out)
        if leg.run is None:
            print(f"  {' ' * width}  not asked for: {leg.cost}", file=out)
    return 0


def main(argv: list[str] | None = None, out: IO[str] | None = None) -> int:
    """The entry point, returning the exit code rather than raising SystemExit,
    so a test can call it without a subprocess and read what it printed."""
    argv = sys.argv[1:] if argv is None else argv
    out = sys.stdout if out is None else out

    if argv in (["--help"], ["-h"]):
        print(USAGE, file=out)
        return 0
    if argv == ["--list"]:
        return _list(legs(), out)
    if argv:
        print(USAGE, file=out)
        print(f"gate: unrecognised argument(s): {' '.join(argv)}", file=out)
        return 2

    code, _ = walk(legs(), out)
    return code
