# 0005 The distributional assumption is declared, and the arithmetic refuses what it cannot consume

Status: decided. Raised in issue #5.

## The decision

Every systematic component declares its distributional assumption. The first
reference implementation consumes Gaussian components only, and refuses a budget
containing a component it cannot consume rather than treating it as Gaussian.

## Why

A field nothing reads is decoration, and decoration in a schema is worse than an
absent field because it looks like a guarantee. Refusing is the only thing that
makes the field mean something before a method exists that can use a
non-Gaussian component.

Refusing also makes the gap visible. A budget that cannot be combined today says
so at the point of use, instead of producing a number quietly built on an
assumption its author did not make.

The alternative, silently folding everything into a symmetric Gaussian
covariance, is what happens today in practice. It is one of the reasons a budget
written as a table cannot be reused.

## The restriction on the first release

Budgets carrying log-normal or one-sided components cannot be combined by the
first release. The release does not approximate them, does not warn and
continue, and does not offer a flag that turns the refusal off. It stops and
names the component it refused.

That is a real restriction on what the first release does, and it is visible
instead of hidden. Widening it means adding a method that can consume the
component, not widening what the validator accepts.
