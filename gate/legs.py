"""The legs this repository declares, in the order the gate runs them.

Order is cheapest first, so that a run that is going to fail usually fails
before it has spent much. The set grows as the milestones create the things
each leg checks, and the issue that adds a leg adds it here.

A leg that cannot run yet is declared anyway, with what asking for it would
cost. Leaving it out instead would mean a run printing four legs and passing,
which reads as a repository that has four things to check rather than as one
that has more and is not checking them.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from gate.headless import DISPLAY_VARIABLES, asserted
from gate.pins import examine
from gate.proof import DESTINATION, judge, reached_from, sites, waivers
from gate.run import ROOT, Leg, Outcome, python

# What the three tooling legs have in common. The documented install reads
# requirements.lock with --require-hashes, so a tool that is not in that file
# is not on the machine, and adding one is not a line in a config file: it is a
# pin plus the hashes of every file the index serves for that version, for the
# tool and for everything it drags in.
_PINNED_INSTALL = (
    "no such tool is in requirements.lock, and the documented install reads "
    "that file with --require-hashes. Asking costs the tool and its transitive "
    "set pinned to exact versions with the hash of every file the index serves"
)


def _pins() -> Outcome:
    """Every dependency that reaches an install is pinned and hashed.

    What was examined is printed whether or not anything was refused, because a
    run against a file this leg failed to read would otherwise be
    indistinguishable from a run against a file with nothing wrong in it.
    """
    examined = examine(
        (ROOT / "requirements.lock").read_text(encoding="utf-8"),
        (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
    )
    print(f"gate: pins: examined {examined.summary()}", flush=True)
    for refusal in examined.refusals:
        print(f"gate: pins: refused {refusal}", flush=True)
    if examined.refusals:
        return Outcome(
            False,
            f"{len(examined.refusals)} refusal(s) over {examined.summary()}",
        )
    return Outcome(True, f"nothing refused over {examined.summary()}")


def _unit_tests() -> Outcome:
    """The suite, through the standard library runner.

    The command is the one the readme already documents, character for
    character, so that following the readme and running the gate are the same
    run rather than two that could disagree. It is run from the repository
    root, which `python -m` puts on the import path, so a test can import
    `gate` as well as the installed package.
    """
    return python(["-m", "unittest", "discover", "-s", "tests", "-v"])


# The suite, started inside an interpreter that has the guard on it before any
# test is imported. A wrapper script would be a second file saying the same
# thing; this is the same discovery the tests leg runs, with one line in front.
_GUARDED_SUITE = (
    "import unittest;"
    "from gate.headless import install;"
    "install();"
    "unittest.main(module=None, argv=['gate', 'discover', '-s', 'tests', '-v'])"
)


def _headless() -> Outcome:
    """The suite again, with no display, no privilege, no network and no write
    outside the tree.

    It is a second run of the same tests rather than a replacement for the
    first, and it costs what the suite costs. What it buys is a distinction the
    single run cannot make: whether a red is the tests failing or the tests
    needing something this project says they may not need.
    """
    environment = dict(os.environ)
    for name in DISPLAY_VARIABLES:
        environment.pop(name, None)
    # An interactive backend chosen from the environment is the other way a
    # suite acquires a display, so it is pinned rather than left unset.
    environment["MPLBACKEND"] = "Agg"
    # No bytecode, so the run writes nothing beside the interpreter it borrowed
    # and the write refusal has no false positive to explain away.
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    for sentence in asserted():
        print(f"gate: headless: asserts {sentence}", flush=True)
    return python(["-B", "-c", _GUARDED_SUITE], env=environment)


# The suite again, this time inside an interpreter recording which lines of the
# scope it executed. A third run of the same tests, and it costs what the suite
# costs; what it buys is the only question a coverage figure cannot answer,
# which is whether each individual refusal has ever been seen to bite.
_RECORDED_SUITE = (
    "import unittest;"
    "from gate.proof import watch;"
    "watch();"
    "unittest.main(module=None, argv=['gate', 'discover', '-s', 'tests'])"
)


def _proof() -> Outcome:
    """Every refusal site in the source was reached by a test, or is waived."""
    with tempfile.TemporaryDirectory() as temporary:
        destination = Path(temporary) / "executed.json"
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment[DESTINATION] = str(destination)

        recorded = python(["-B", "-c", _RECORDED_SUITE], env=environment)
        if not recorded.passed:
            return Outcome(
                False,
                "the suite did not pass under the recorder, so what it reached "
                f"says nothing yet: {recorded.detail}",
            )
        reached = reached_from(destination)

    result = judge(sites(ROOT), reached, waivers(ROOT))
    print(f"gate: proof: examined {result.summary()}", flush=True)
    for refusal in result.refusals:
        print(f"gate: proof: refused {refusal}", flush=True)
    if result.refusals:
        return Outcome(False, f"{len(result.refusals)} refusal(s) over {result.summary()}")
    return Outcome(True, f"nothing refused over {result.summary()}")


def legs() -> list[Leg]:
    """The declared set, rebuilt on each call so that nothing shares state
    between runs."""
    return [
        Leg(
            name="format",
            decides="source, documentation and example documents are formatted",
            cost=f"{_PINNED_INSTALL}. The formatter and this leg are issue #30",
        ),
        Leg(
            name="lint",
            decides="the linter finds nothing, and every suppression carries a reason",
            cost=f"{_PINNED_INSTALL}. The linter and this leg are issue #27",
        ),
        Leg(
            name="types",
            decides="the type checker finds nothing under its strict setting",
            cost=f"{_PINNED_INSTALL}. The type checker and this leg are issue #27",
        ),
        Leg(
            name="pins",
            decides=(
                "every dependency that reaches an install is pinned to one "
                "exact version and carries a hash"
            ),
            run=_pins,
        ),
        Leg(
            name="tests",
            decides="the unit suite passes",
            run=_unit_tests,
        ),
        Leg(
            name="proof",
            decides=(
                "every place in the source that can refuse something was "
                "reached by a test, or is waived with what retires the waiver"
            ),
            run=_proof,
        ),
        Leg(
            name="headless",
            decides=(
                "the suite passes with no display, no privilege, no network "
                "and no write outside the tree"
            ),
            run=_headless,
        ),
    ]
