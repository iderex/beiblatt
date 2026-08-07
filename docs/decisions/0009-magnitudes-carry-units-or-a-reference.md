# 0009 Magnitudes carry a unit or an explicit reference, never a bare number

Status: decided. Raised in issue #9.

## The decision

Every magnitude is either an absolute quantity carrying a unit, or a relative
quantity carrying an explicit statement of what it is relative to. There is no
default and no bare number.

## The failure class this removes

Mixing absolute and relative magnitudes is the ordinary way a transcription of a
published table goes wrong, and it goes wrong quietly. A number that is wrong by
a factor of the central value is still a plausible-looking number, so it
survives review and shows up as a disagreement much later, in a combined result,
where it is attributed to something else.

Neither a schema nor a reader can recover the intent afterwards. A component
reading 0.15 next to a central value of 172.5 could be either reading, and
nothing in the file settles it. Requiring the statement costs one field and
removes the whole class from everything downstream, because a document that does
not say which it is does not validate.

Units are required for the same reason and for one more, which is the next
section.

## Two budgets quoting in different units

A combination across two groups quoting in different units is exactly the case
this format exists to serve, so the format does not refuse it. It converts.

The conversion happens in the implementation, once, at the point where the
covariance matrix is assembled, and never in a person reading a paper. The
result document states the unit it reports in. A unit the implementation cannot
convert is refused by name rather than assumed to be compatible, which is the
same posture as the distributional assumption in
[0005](0005-distributional-assumption-is-declared-and-enforced.md).

A relative magnitude has no unit to convert. It is resolved against the value it
declares itself relative to, and that resolution happens before the conversion,
so a budget may mix the two forms freely.

## The cost

Every component gets one more required field, and hand-writing a budget is
slightly more work. Refusing a bare number will annoy the first authors. That
annoyance is the price of not having to audit for this class later, and there is
no version of the format that both accepts a bare number and can tell what it
means.
