# 0014 What the format deliberately does not hold

Status: decided. Raised in issue #14.

This is the decision about what the format refuses to hold, which is as load
bearing as the rest and is usually left implicit. It is written here so that the
boundary is something a reader finds in one place rather than something they
infer from an absence.

## The decision

The format does not hold any of the following, and the specification says so in
the text rather than leaving the absence to be discovered.

### Bin-to-bin statistical correlations within one measurement

A budget describes an estimate of a scalar observable, not a differential
distribution. Serving both would make every field conditional on which case it
is, and the second case has existing partial solutions while the first has none.

A differential measurement needs a correlation structure across bins as well as
across sources, and the two are different objects. Carrying both in one document
means a reader can never tell from the schema alone which shape a given file is
in, and every element has to be read twice.

### Full likelihoods

Covered by [0011](0011-the-reference-arithmetic-is-blue.md), which puts
combination from likelihoods out of scope, and repeated here because a reader
looking for the boundary should find it in one place. The reason given there is
that the likelihoods are the material nobody publishes, and a format whose use
requires an input nobody publishes solves a problem nobody has.

### Detector-level or event-level data

A budget refers to a published result and never carries the data behind it. The
artefact is a description of an estimate somebody else made, and the estimate is
the thing being combined.

### The procedure by which a systematic was estimated

A budget carries what the uncertainty is and what it is correlated with, not how
somebody arrived at it. That is a long argument in prose, it does not have a
schema, and pretending otherwise would produce a required free-text field that
everybody fills with a sentence nothing can use.

The one thing about the procedure that does matter to a combination is whether
two groups' procedures rest on the same underlying effect, and that question is
answered by the source name and the registry definition behind it,
[0002](0002-correlation-by-named-source.md), rather than by a description of
either procedure.

## Why the boundary is written down

Each of these is something a reader will reasonably expect and will otherwise
assume is coming. Writing the boundary down is what lets somebody decide the
format is unsuitable for their case quickly, which is a service, and it is what
stops the schema growing a field per request.

An absence that is not written down is read as an oversight, and the repair
offered for an oversight is a new field. Four exclusions stated in the
specification turn four future arguments about fields into one argument about
scope, which is the argument worth having.

## The cost

The format cannot be used for a differential measurement without an extension
that does not exist, and it cannot answer a question about how an uncertainty
was derived. Both restrictions are visible from the specification instead of
discovered during use.

The differential case is the expensive one. It is a large share of what gets
published, and a group whose result is differential gets nothing from this
format at all. That is a deliberate narrowing to the case with no existing
solution, and it is a bet that the narrow case is worth solving properly rather
than a claim that the other case does not matter.

Excluding the estimation procedure has a cost that lands on the registry. A
reader who wants to know whether two groups mean the same thing by a source name
has only the registry definition to go on, so that definition has to carry
weight the budget is not allowed to carry, and issue #8 is where that obligation
was taken on.
