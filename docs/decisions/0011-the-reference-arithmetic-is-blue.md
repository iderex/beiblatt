# 0011 The reference arithmetic is BLUE, weights are reported, likelihood combination is out of scope

Status: decided. Raised in issue #11.

## The decision

The reference arithmetic is the best linear unbiased estimate over a covariance
matrix built from the budgets and the assumption set. Combination from full
likelihoods is out of scope for this project. The implementation reports the
weight it assigned to each input, including negative weights, and never hides
one.

## Why this method

The published combinations this project validates against used exactly this
method. Using it here makes the validation a test of whether the format carried
enough information, which is the question this project is asking.

A different method would make the validation a test of the method instead. If
the number came out different, it would be impossible to tell a format gap from
a method difference, and the interesting result would be unreadable.

## Why likelihood combination is out of scope

Combination from likelihoods needs the likelihoods, and those are the material
that is not published. A format whose use requires an input nobody publishes
solves a problem nobody has.

This is a statement about what this project builds, not a claim that the method
is worse. Where the full statistical model is available, it carries more than a
covariance matrix can.

## The reporting obligation for weights

The estimator does things that surprise people who have not met it. A weight can
come out negative, and the combined uncertainty can grow rather than shrink as
the assumed correlation increases. Both are properties of the estimator rather
than bugs.

So every result reports the weight assigned to each input, always, not only when
one is negative and not behind a verbosity flag. A tool that hides them will be
blamed for them the first time somebody notices.

## How the variant that ran is recorded

The method is unbiased only when the true uncertainties and correlations are
known. It is biased when estimates are substituted, which is always. An
iterative variant reduces that bias and changes the answer.

Which variant ran is therefore an input rather than a default: the assumption
set names it, and the result document repeats the name it was given back to the
reader. A result that does not name its variant is not reproducible, on the same
argument that makes a result name its assumption set in
[0003](0003-assumptions-are-separate-from-budgets.md).

## The cost

Recording the difference between the variants on the reproduction target is part
of the validation work rather than an optional extra, because the size of that
difference is the only honest statement about how much the choice matters.
