# 0001 One budget file is one estimate of one observable

Status: decided. Raised in issue #1.

## The decision

One budget file describes exactly one estimate of one observable by one group.
It carries the observable it estimates, the central value, the statistical
uncertainty, and a list of named systematic components. Fifteen estimates are
fifteen files. Nothing in a budget file refers to another estimate.

## Why

The published combinations this project has to reproduce take one row per
estimate, so a file per estimate is the shape the source material already has.
No transformation stands between the table in the paper and the artefact.

Provenance, licence and version attach to the thing that was actually
published, which is the estimate. An update to one estimate does not rewrite
bytes belonging to another group.

A container holding many estimates would have to decide whose artefact it is,
and for a cross-experiment combination the answer is nobody in particular.

## The cost

Combining needs something that names the files and says how they relate. That
is the assumption set, decided separately in
[0003](0003-assumptions-are-separate-from-budgets.md). It is a cost this
decision creates rather than one it avoids: a reader who has a budget in hand
still cannot combine anything with it until a second artefact exists.
