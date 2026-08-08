# 0002 Correlation is carried by named external sources, not by a pairwise matrix

Status: decided. Raised in issue #2.

## The decision

A systematic component declares the external source it derives from, by name.
Two components in two different budgets that name the same source are
correlated through that source. Budget files carry no pairwise correlation
matrix and no reference to another budget.

## Why

A pairwise matrix grows with the square of the number of results and has to be
renegotiated every time a new result appears. That renegotiation is the months
of argument the problem statement describes, and a format that encodes its
outcome rather than its inputs preserves the problem. Names compose to any
number of results without renegotiation: a sixteenth estimate declaring the
same calibration source is correlated with the other fifteen by construction.

Names are also the level at which the disagreement actually lives. Two groups
rarely disagree about a number in the abstract; they disagree about whether
their two calibrations are the same underlying thing. A format that makes that
question explicit describes the argument instead of hiding it.

The decision that one budget file is one estimate,
[0001](0001-one-budget-is-one-estimate.md), is what makes this the only
available shape. A budget that may not refer to another budget has nowhere to
put a pairwise coefficient, so the relation has to live in something both
budgets can point at independently, which is a name.

## Prior art

The mechanism is not new. Analysis likelihood specifications already treat a
shared modifier name as a fully correlated parameter across channels and
samples within one analysis. Two samples that declare the same nuisance
parameter move together, and no coefficient is written anywhere; the name is
the whole statement.

What is new here is applying it across published results by different groups,
which is the case nobody has a format for. Inside one analysis the names come
from one team and mean one thing by construction. Across groups they do not,
and that difference is the cost below rather than a detail.

## The cost

Correlation by name is worth exactly as much as the agreement about names.
Without a definition attached to each name, two groups writing one string is a
coincidence and not an agreement, and the arithmetic will read it as an
agreement and return a number with no warning attached.

That cost is paid by the source registry, decided separately in issue #8, and
it is the largest obligation this decision creates. It is a governance
obligation and not a file: somebody has to write the definition each name
stands for and refuse a name that duplicates an existing one under a different
spelling.

The decision also gives up the one thing a pairwise matrix does well. Where two
groups have genuinely agreed a coefficient between their two results, and that
agreement does not decompose into shared sources, this format cannot carry it.
Such an agreement has to be expressed as a source both budgets name, which is a
worse fit for how it was reached, or it cannot be expressed at all.
