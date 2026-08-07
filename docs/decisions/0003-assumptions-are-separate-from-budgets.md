# 0003 Correlation assumptions live in a separate artefact from the budget

Status: decided. Raised in issue #3.

## The decision

How strongly two named sources are correlated is declared in a separate
document, an assumption set, which names the budgets it applies to. Budget
files carry no correlation strengths at all. A budget says what the uncertainty
is; an assumption set says how two budgets relate.

## Why

In the published ATLAS and CMS top quark mass combination the correlation
strength for each category is the disputed quantity. It takes values agreed
between the groups rather than measured, and the paper reports what changes when
an alternative assumption is taken.

If that number lives inside a budget, then disagreeing with it means editing an
artefact somebody else published. Nobody will do that and nobody should.

Separating the two means two groups publish their budgets once and a third party
can publish a competing assumption set beside them and show exactly what moves.
A sensitivity scan over correlation assumptions becomes an operation the format
supports rather than a script somebody wrote once.

## The cost

A combination now needs two inputs rather than one. A result quoted without
naming its assumption set is not reproducible, so every output the reference
implementation produces has to name the assumption set it used. That obligation
falls on the result document rather than on the reader remembering.
