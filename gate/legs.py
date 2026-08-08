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

from gate.run import Leg, Outcome, python

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


def _unit_tests() -> Outcome:
    """The suite, through the standard library runner.

    The command is the one the readme already documents, character for
    character, so that following the readme and running the gate are the same
    run rather than two that could disagree. It is run from the repository
    root, which `python -m` puts on the import path, so a test can import
    `gate` as well as the installed package.
    """
    return python(["-m", "unittest", "discover", "-s", "tests", "-v"])


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
            name="tests",
            decides="the unit suite passes",
            run=_unit_tests,
        ),
    ]
