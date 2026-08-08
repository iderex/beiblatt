# 0012 Determinism, and how a tolerance against a published number is justified

Status: decided. Raised in issue #12.

## The decision

The arithmetic is deterministic for a given input on a given platform, and every
comparison against a published number states a tolerance and where that
tolerance came from. No test asserts equality against a number taken out of a
paper.

## Why

Published central values are quoted to a stated number of digits, so agreement
with one is a statement about digits and not about equality. A test asserting
equality against a rounded value either passes by luck or fails for a reason
that has nothing to do with the format, and both outcomes destroy the evidence
the test was written to produce.

Determinism is separate and is what makes a regression readable. If the same
input can produce two answers on two runs, a changed answer proves nothing.

## What determinism means here

Same input, same machine, same installed dependency set, same answer, every
time. Nothing in the arithmetic draws a random number, iterates to a
convergence criterion seeded by wall-clock time, or depends on the order in
which a set was enumerated. Where an ordering could reach the linear algebra,
it is fixed by the document rather than by a hash table, so that two runs
assemble the same matrix in the same order and not merely an equivalent one.

The dependency set is pinned to exact versions for this reason as much as for
the supply chain, which is what issue #16 lays down. An unpinned numerical
library makes the sentence above untestable, because the machine changes
underneath a run that nobody touched.

## How a tolerance is justified

A tolerance has two sources and is the larger of them. Both are written into
the test beside the number, not into a shared constant somewhere else, because
a tolerance justified in one place and used in five is a tolerance nobody can
check.

The first source is the published number itself. A value quoted to a given
number of digits carries a rounding half-interval in its last quoted digit, and
no comparison against it can be tighter than that interval without asserting
something the paper did not say. This part of the tolerance is read off the
paper and the digits are quoted in the test.

The second source is the arithmetic's own spread across the platforms and
library versions the project supports. That is a measured figure, produced by
running the same input across those environments and recording the range, and
the command that produced it is cited beside the number in the same way every
other measured claim in this repository cites its command. Until such a run has
happened, this part of the tolerance is not a number and the test says so
rather than carrying a placeholder that reads as measured.

A tolerance is justified before the test is green, never after. Widening one to
make a failing comparison pass is a finding about the arithmetic or about the
transcription, and it is written up as one. Where a tolerance genuinely has to
move, the movement is a change with its own reason recorded, and the previous
value is visible in the history rather than quietly replaced.

## What this project does not promise

Bit-identical results across platforms and library versions are not promised,
because the linear algebra underneath does not promise them. The reference
arithmetic is a best linear unbiased estimate over a covariance matrix,
[0011](0011-the-reference-arithmetic-is-blue.md), and the solve it rests on is
performed by the numerical library the means decision brings in,
[0013](0013-the-means.md). That library is free to choose a different order of
operations on a different processor, and floating point addition is not
associative, so the last digits may differ. Nothing this project can do inside
its own source changes that.

So a result is reproducible under a stated tolerance rather than byte for byte.
A reader comparing two runs on two machines should expect agreement to the
tolerance and should not read a difference in the last digits as a defect.

## The cost

The tolerance has to be wide enough to survive a library upgrade and narrow
enough to catch a real change, and the value has to be justified in the test
rather than tuned until the suite goes green. Those two requirements pull in
opposite directions, and the policy above does not make them compatible; it
only makes the pull visible.

Where they genuinely conflict, the conflict is written down instead of resolved
by widening. A comparison whose honest tolerance is too wide to catch anything
is not evidence, and saying so is more useful than a green test that proves
nothing.

The second cost is that the measured half of every tolerance is a claim about a
run across several environments, and this project's gate runs in one. Until the
spread has actually been measured, the tolerances carry only the half that comes
off the paper, and every test using one says which half it has.
