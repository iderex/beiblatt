# 0004 Impacts are signed, and an undetermined sign says so

Status: decided. Raised in issue #4.

## The decision

A systematic component carries the sign of its impact on the central value, not
only a magnitude. Where a category is the sum of several sources whose combined
sign is not determined, the budget records that the sign is undetermined
instead of inventing one, and the assumption set chooses.

The undetermined value is a third state and not a missing field. A budget that
leaves the sign out is refused; a budget that says the sign is undetermined is
accepted and cannot be combined until an assumption set supplies the choice.

## Why

The published combination builds the correlation coefficient between two
measurements for a category as the product of the agreed correlation strength
and the signs of the impacts of that category on each measurement. Categories
that push the two measurements in the same direction get a positive
correlation, and opposite directions get a negative one. A budget carrying
magnitudes only cannot produce that coefficient, so it cannot reproduce the
published result, and reproducing a published result is this project's
deliverable rather than a nice property.

Putting the choice in the assumption set rather than in the budget follows
[0003](0003-assumptions-are-separate-from-budgets.md) for the same reason it
was decided there. The sign of one component inside one estimate belongs to
whoever published that estimate; what to do about a component whose sign nobody
determined is a position taken by whoever is combining, and two people
combining the same budgets are allowed to disagree about it and to say so.

## The undetermined case

The undetermined case is not hypothetical. The published combination met it,
assumed a positive sign, and reported the effect of the opposite assumption on
both the central value and the uncertainty. A format that cannot say that a
sign is a choice forces the choice to be silent.

Silent is the specific failure being prevented. If the budget must write a sign
it does not have, the number it writes is indistinguishable from one that was
measured, and the sensitivity study the published combination performed becomes
impossible to reconstruct from the artefacts. Carrying the third state is what
lets the same pair of budgets be combined twice, under opposite assumptions,
and both results reported.

## The cost

Signs are extra work at transcription time and are the field most likely to be
wrong, because a sign error is not visually implausible. A magnitude entered
with a digit missing looks wrong on the page; a sign entered the wrong way
round looks exactly like the right one.

No validator can catch it. Nothing in the document, and nothing available to a
tool reading the document, distinguishes a correct sign from its opposite. The
reproduction test in M7 is what catches it, which is one more reason that
milestone is the deliverable and not a demonstration.

The third state also costs the arithmetic a refusal it would not otherwise
need. A combination whose assumption set does not resolve every undetermined
sign it meets has to stop rather than pick, and that refusal is a thing that
has to be written, proven and explained.
