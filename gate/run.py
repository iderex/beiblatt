"""What a leg is, and the walk that runs them.

The walk is a plain function over a list rather than a script, because the
properties this repository claims about the gate are then things a test can
assert directly: that the legs run in the declared order, that the walk stops
at the first failure, that a leg nobody asked for is reported as not asked for
instead of silently skipped, and that every declared leg is named in the
output whatever happened to it.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import IO

# The repository root, derived from this file rather than from the working
# directory, so the gate behaves the same whichever directory it was invoked
# from. gate/run.py -> gate/ -> the root.
ROOT = Path(__file__).resolve().parent.parent

PASSED = "passed"
FAILED = "failed"
NOT_ASKED_FOR = "not asked for"


@dataclass(frozen=True)
class Outcome:
    """What a leg reports back: whether it passed, and the one line a reader
    gets. The detail carries the command where there was one, because a verdict
    without the command that produced it is a claim."""

    passed: bool
    detail: str


@dataclass(frozen=True)
class Leg:
    """One decision the gate makes.

    `decides` is the single line saying what the leg is for, printed whether or
    not the leg runs, so a listing is readable without opening this file.

    `run` is the work. Where it is None the leg is declared but not asked for,
    and `cost` says what asking would cost. Those two fields move together: a
    leg with no work has to say what it would take to have some, which is what
    keeps a run that covered less than the whole set from reading like a run
    that covered it and found nothing.
    """

    name: str
    decides: str
    run: Callable[[], Outcome] | None = None
    cost: str | None = None

    def __post_init__(self) -> None:
        if (self.run is None) == (self.cost is None):
            raise ValueError(
                f"leg {self.name!r}: a leg either does work or says what "
                f"asking for it would cost, and never both or neither"
            )


@dataclass(frozen=True)
class Report:
    """The state of one leg after the walk, in declaration order."""

    name: str
    state: str
    detail: str


def command(
    argv: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None
) -> Outcome:
    """Run a subprocess and turn its exit code into an outcome.

    The command is echoed into the detail whichever way it went, so the reader
    of a passing run can re-run exactly what passed and the reader of a failing
    one is not left reconstructing it.
    """
    shown = " ".join(argv)
    completed = subprocess.run(argv, cwd=cwd, env=env)
    if completed.returncode == 0:
        return Outcome(True, f"{shown}")
    return Outcome(False, f"{shown} exited {completed.returncode}")


def python(
    args: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None
) -> Outcome:
    """`command` for a leg that runs this interpreter.

    sys.executable rather than "python", so a leg runs in the environment the
    gate was started in and not in whatever the PATH resolves to.
    """
    return command([sys.executable, *args], cwd=cwd, env=env)


def walk(legs: list[Leg], out: IO[str]) -> tuple[int, list[Report]]:
    """Run the legs in order, stop at the first failure, report every leg.

    Returns the exit code and one report per declared leg. A leg after the
    failure is reported as not run, which is a different word from passing and
    a different word from not being asked for.
    """
    reports: list[Report] = []
    failed = False

    for leg in legs:
        if failed:
            reports.append(Report(leg.name, "not run", "a leg before it failed"))
            continue

        if leg.run is None:
            assert leg.cost is not None  # __post_init__ refuses the other case
            reports.append(Report(leg.name, NOT_ASKED_FOR, leg.cost))
            continue

        print(f"gate: {leg.name}: {leg.decides}", file=out, flush=True)
        outcome = leg.run()
        state = PASSED if outcome.passed else FAILED
        reports.append(Report(leg.name, state, outcome.detail))
        if not outcome.passed:
            failed = True

    _summarise(reports, out)
    return (1 if failed else 0), reports


def _summarise(reports: list[Report], out: IO[str]) -> None:
    """Print every declared leg with what became of it.

    Every leg appears here whatever happened to it. That is the whole point of
    the summary: the reader learns the size of the set from the run itself
    rather than from a list in a document that drifts against it.
    """
    width = max((len(r.name) for r in reports), default=0)
    print("", file=out)
    print(f"gate: {len(reports)} leg(s) declared", file=out)
    for report in reports:
        print(f"  {report.name.ljust(width)}  {report.state}: {report.detail}", file=out)

    counts: dict[str, int] = {}
    for report in reports:
        counts[report.state] = counts.get(report.state, 0) + 1
    tally = ", ".join(f"{counts[state]} {state}" for state in sorted(counts))
    print(f"gate: {tally}", file=out, flush=True)
