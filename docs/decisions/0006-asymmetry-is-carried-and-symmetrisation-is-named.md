# 0006 Asymmetric uncertainties are carried, and symmetrisation is named in the output

Status: decided. Raised in issue #6.

## The decision

A component may carry different up and down magnitudes. Any symmetrisation is
performed by the arithmetic, never by the author of the budget, the rule used is
chosen in the assumption set, and the output names which rule ran.

A budget therefore records what was published. Where a published component is
asymmetric, the budget is asymmetric, and no step between the paper and the
artefact averages anything.

## Why

Covariance-based combination is symmetric by construction, so an asymmetry is
lost somewhere between the budget and the answer. The reference arithmetic is
fixed as a best linear unbiased estimate over a covariance matrix in
[0011](0011-the-reference-arithmetic-is-blue.md), and that matrix has one
number per pair. The question is not whether the asymmetry survives. It is only
where it is destroyed and whether anybody can see it happen.

The recorded complaint about existing published data is precisely that the loss
happens implicitly, inside a symmetric Gaussian construction, with nothing
recording that it happened.

Making the rule an input moves the loss to a place a reader can see and a second
party can disagree with. It also lets the same pair of budgets be combined under
two symmetrisation rules to show whether the choice matters, which is the only
honest way to report a case where it does.

The rule belongs in the assumption set rather than in the budget for the reason
[0003](0003-assumptions-are-separate-from-budgets.md) gives: it is a position
taken by whoever is combining, and disagreeing with it must not require editing
an artefact somebody else published.

## Where this sits against the distributional assumption

[0005](0005-distributional-assumption-is-declared-and-enforced.md) refuses a
component whose distribution the arithmetic cannot consume. An asymmetric
Gaussian component is not that case. It is a component the arithmetic can
consume once a stated rule has reduced it, and the rule is what this decision
makes visible. A one-sided or log-normal component is still refused, and
symmetrisation is not a route around that refusal.

## The cost

One more required element in the assumption set, and an output format that has
to carry a note about a transformation the reader did not ask for.

The note is not optional and cannot be suppressed. An output that ran a
symmetrisation and does not say so is the failure this decision exists to
prevent, so the naming is part of the result document rather than a verbosity
setting.

There is a second cost the arithmetic pays rather than the author. Two rules
applied to the same pair of budgets give two different answers, both correct
under their own rule, and neither is the answer. A reader who wants one number
has to be told which rule produced it, every time, which makes every quoted
result longer.
