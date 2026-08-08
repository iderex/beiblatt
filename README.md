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
`--no-build-isolation` is what keeps the build backend inside that guarantee:
without it pip fetches the backend separately and the pin does not reach it.

Nothing is installed outside the environment and no step needs administrative
rights.

The package holds no schema, no validator and no arithmetic yet. What the
install produces at this point is an environment the later milestones build in,
and the check that it worked is:

    .venv/bin/python -m unittest discover -s tests

See [NOTICE.md](NOTICE.md) for the intended-use notice.
