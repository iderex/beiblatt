"""The gate: one command, its legs in a fixed order, stopping at the first
failure.

Everything that decides whether a change may land runs behind this package, so
that a local run and a run on a server are the same procedure rather than two
that drift. The legs are declared in `gate.legs` and the runner that walks them
is `gate.run`.

This package sits outside `src/` on purpose. `pyproject.toml` packages only
what is under `src/`, so the gate is present in a clone and absent from an
install: somebody who installs the library gets the format and the arithmetic
and none of the machinery that judges this repository.
"""

__all__ = ["main"]

from gate.cli import main
