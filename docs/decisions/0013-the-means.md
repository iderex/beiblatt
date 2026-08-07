# 0013 The means, checked against what this artefact has to carry

Status: decided. Raised in issue #13.

The means is chosen against what this artefact has to carry, not by habit. The
four questions and their answers are recorded here so that a later reader can
disagree with the answer rather than guess whether the question was asked.

## The four questions

### Can the means carry a refusable rule, an executed proof that the rule bites, and a claim that cites the command that produced it?

Yes, and all three by ordinary means. A validator that exits non-zero on a
document it refuses is a machine refusing a violation. A test suite proves a
refusal bites by feeding it the near-miss and asserting the refusal, and it runs
headless and unprivileged, with no display and no special hardware. A claim
about a number carries the command that produced it because the command is one
line.

### Is anything outside this repository forcing a means, and is that force real?

Yes, and the force is the audience. The people who have to write budgets, read
them and disagree with the arithmetic work in Python. A reference implementation
they cannot read is a reference implementation nobody checks, which leaves it
with the same problem as the PDF table it replaces.

The force applies to the reference implementation and not to the format. It is
held to that surface.

### Does it add a runtime or a dependency, and is the cost paid knowingly?

Yes to both, and the cost is stated below rather than absorbed. A Python runtime
has to be installed. Three third-party dependencies enter the tree, and the
numerical result depends on the linear algebra library underneath, which is why
the tolerance policy is a separate decision rather than an afterthought.
Dependency surface is held down by pinning every version and by a vulnerability
audit that runs in the gate.

### Would the artefact be testable by a suite that will actually exist, or does it need a parallel apparatus nobody will maintain?

By the suite that will exist. Everything the format needs tested is a function
from bytes to a verdict or from numbers to numbers, both of which an ordinary
test runner handles. No parallel apparatus is required and none is created.

## The decision

The schema itself is language neutral. A JSON Schema document plus a prose
specification, both of which a second implementation in any language can
consume.

The reference validator and the reference arithmetic are written in Python, with
a pinned dependency set of three: a YAML parser, a JSON Schema validator, and a
numerical linear algebra library. No compiled extension is written by this
project.

## What was decided against

A compiled language would give a single distributable binary and no runtime to
install. That is a genuine advantage for an operator and a genuine loss for the
reader, and the reader matters more here, because reading the arithmetic is the
point of a reference implementation.

Building on top of an existing physics analysis framework would inherit a
working combination implementation, and with it a heavy runtime the audience
cannot install everywhere. It would also make this project a plugin to that
framework rather than a format. Whether such a framework is used as an optional
cross-check, rather than as a dependency, is a maintainer decision and is not
settled here.

## The cost

A Python runtime, three third-party dependencies, and a numerical answer that is
reproducible under a stated tolerance rather than bit for bit.
