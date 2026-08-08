# beiblatt

Every publication carries its systematic uncertainties as running text in a PDF with no correlation information, which makes combining results from different groups practically impossible and has ATLAS and CMS negotiating for months over which systematics are correlated. The schema holds source, magnitude, distributional assumption and correlation to named external sources, plus a reference implementation of the combination arithmetic. The correlations are the point; a budget without them is the PDF table in another syntax. It does not fail on the mathematics but on nobody having defined the format, so the deliverable is reproducing a published combination from two budgets rather than the schema itself.

Planning happens on the issue tracker first. Every decision that shapes
the architecture is written down there with its reasons before the code
that depends on it exists.

## Installing

Python 3.12 or newer has to be on the machine. Nothing else does. From a clean
clone:

    python -m venv .venv
    .venv/bin/python -m pip install --require-hashes -r requirements.lock
    .venv/bin/python -m pip install --no-build-isolation --no-deps -e .

On Windows the interpreter inside the environment is `.venv/Scripts/python.exe`
and the three lines are otherwise the same.

Every version installed comes from `requirements.lock`, which pins each direct
and transitive dependency to one version and to the hashes of every file the
index serves for it. `--require-hashes` makes pip refuse anything else rather
than fetch it, so two installs a month apart get the same bytes.
`--no-build-isolation` is what keeps the build backend inside that guarantee,
and what it carries there is the hash rather than the version. With build
isolation pip installs the backend in a step of its own that never reads
`requirements.lock`: the exact version in `pyproject.toml` still applies, and
nothing compares the bytes against a hash. Running the second line as
`pip install --no-deps -e . -vv` shows that step reporting `Given no hashes to
check` for the backend. The documented order installs the backend from the
hash-checked file first and then builds against what is already in the
environment.

Nothing is installed outside the environment and no step needs administrative
rights.

The package holds no schema, no validator and no arithmetic yet. What the
install produces at this point is an environment the later milestones build in,
and the check that it worked is:

    .venv/bin/python -m unittest discover -s tests

## The gate

    .venv/bin/python -m gate

That is the whole of it. It runs its legs in a fixed order, stops at the first
failure, and exits non-zero if anything failed. A local run and a run anywhere
else are the same command, so there is one procedure rather than two that
agree on the day they are written and drift afterwards.

What the legs are is not written here. The run prints them, and

    .venv/bin/python -m gate --list

prints them without running any. A list in this file would be a second place
that has to be corrected every time a leg is added, and the version that stops
being corrected is this one. A leg that cannot run yet is printed too, together
with what asking for it would cost, so a run that covered less than the whole
set cannot be read as a run that covered it and found nothing.

The gate is not what stands behind a merge. It is a command that can be skipped
by not running it, and whether anybody ran it before pushing is not a fact this
repository holds.

### Running it before a push

Once per clone:

    git config core.hooksPath .githooks

That points git at the tracked hook, which runs the gate command and nothing
else. It shortens the feedback loop and it is not the enforcement. It is absent
from a fresh clone, one flag on the push skips it, and whether any given clone
ran the line above is a fact of that clone's local git configuration which
nothing in this repository can read. Nothing here is going to notice that you
did not.

See [NOTICE.md](NOTICE.md) for the intended-use notice.
