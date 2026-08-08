# 0008 Source identifiers, the registry entry, and the append-only rule

Status: decided. Raised in issue #8.

[0002](0002-correlation-by-named-source.md) made a name the whole statement of a
correlation, and said in its own cost section that the names are worth exactly
what the agreement about them is worth. This is the decision that pays for that
sentence: what a name looks like, what has to be written down beside it, and
what may never happen to it afterwards.

## The decision

An external source is named by a namespaced identifier. A registry in this
repository holds every identifier this project mints, each entry carrying a
prose definition of the physical effect it covers, the date it entered force
and, where it is retired, what replaces it. A budget may name an identifier
from a namespace this project does not own, and then the budget says where that
namespace is defined.

### The identifier

An identifier has two parts, a namespace and a name, joined by one colon:

    <namespace>:<name>

Exactly one colon and therefore exactly two parts. Each part is built from the
lowercase ASCII letters `a` to `z`, the digits `0` to `9` and the hyphen. Each
part begins with a letter, ends with a letter or a digit, and carries no two
hyphens in a row. Each part is at most 64 characters, so an identifier is at
most 129 characters including the colon.

Only the lowercase spelling exists. An identifier carrying an uppercase letter
is refused rather than folded down to lowercase. Folding accepts two spellings
and stores one, so the person who wrote the other spelling never learns that
the document they wrote is not the document that will be read, and the two
spellings are exactly the near-miss this identifier exists to make impossible.
Refusal puts the failure in front of the author while they still have the file
open.

The character set is the smallest one that can carry a readable phrase. An
underscore and a dot are both left out for one reason: each is a second way to
write the same word, and a second way to write the same word is a name that
looks agreed and is not. There is one word separator and it is the hyphen.

Each part begins with a letter because a part that begins with a digit can stop
being a string before anything in this project sees it. Measured against the
YAML parser this repository pins:

    .venv/bin/python -c "import yaml; print(repr(yaml.safe_load('source: 2015-01-02')))"
    {'source': datetime.date(2015, 1, 2)}
    .venv/bin/python -c "import yaml; print(repr(yaml.safe_load('source: atlas:jes-1')))"
    {'source': 'atlas:jes-1'}

The first is a date and not the identifier somebody wrote. Requiring a leading
letter keeps every identifier out of that class rather than leaving it to be
caught later.

The colon survives both positions an identifier is written in, which was worth
checking rather than assuming, because a separator that has to be quoted in one
of them is a separator people will get wrong by hand:

    .venv/bin/python -c "import yaml; print(repr(yaml.safe_load('atlas:jes-1: 0.5')))"
    {'atlas:jes-1': 0.5}

All three were run in the environment the readme's install produces, against
PyYAML 6.0.3, on the Windows spelling of that interpreter path.

The maximum length is a choice and not a measurement. A bound has to exist,
because an identifier with no bound is an unbounded field in every document,
every error message and every table a reader prints; 64 characters per part is
long enough for a phrase in hyphen-separated words and short enough to retype
without losing your place.

What is not decided here is the namespace string this project publishes its own
identifiers under. That is entry 7 of issue #15 and it is open. The grammar
above admits whatever it turns out to be, so nothing in this decision has to
move when it is answered.

### The registry entry

Every identifier this project mints has an entry, and an entry carries four
things:

- the identifier itself
- a prose definition of the physical effect it covers
- the date it entered force
- where it is retired, the date of the retirement and the identifier that
  replaces it, or the statement that nothing does

The definition is the load-bearing field and the rest is bookkeeping around it.
An entry whose definition is empty is worse than no entry at all, because an
absent identifier is refused and an empty one looks like an agreement that
exists.

Nothing in the entry says how anybody estimated anything. That boundary is
[0014](0014-what-the-format-does-not-hold.md), which excludes the estimation
procedure from a budget and points here for the one part of it that matters to
a combination: whether two groups' components rest on the same underlying
effect.

### Append-only

An identifier is append-only. Once an entry has landed, its definition, its
identifier and its in-force date are never edited. A definition that changes
meaning is a new identifier and a retirement of the old one, with the
retirement naming what replaces it.

The only permitted edit to a landed entry is adding that retirement, and this
is deliberately absolute. A typographical error in a landed definition is not
repairable in place either, and the only route to correcting one is to retire
the identifier and mint its successor. That is expensive and it is the price of
the guarantee. The alternative is a rule with an exception for harmless edits,
and nothing can decide from the outside whether an edit was harmless: the
person making it is the person least able to see that a reader took the older
wording to mean something narrower.

Without the rule, every combination that ever used an identifier changes
meaning retroactively when its definition moves, and no reader of an older
result can tell that it did. That is the worst failure this format can have,
because it is silent and it is in the past.

### Foreign namespaces

A budget may name an identifier from a namespace this project does not own, and
then the budget carries a declaration saying where that namespace is defined.
The declaration is required rather than optional, and an identifier from a
foreign namespace without one is refused.

Foreign namespaces are permitted because this project does not get to own the
vocabulary of every group that might publish a budget, and a format that
required it to would be ignored. What can be checked about a declaration is
that it is there and that it names a location that resolves. Whether the
definition at that location says what the author of the budget believes it says
cannot be checked here, and nothing in this project's refusals will imply that
it was.

## Why

Correlation by name is worth exactly as much as the agreement about names, so
the definitions are the load-bearing part and the strings are not. Without a
definition attached, two groups writing the same string is a coincidence that a
tool will read as an agreement, and the arithmetic will confidently return a
wrong number.

Retirement matters for the same reason in the other direction. If a definition
changes silently, every combination that ever used it changes meaning
retroactively, and no reader of an old result can tell. An identifier is
therefore append-only: a changed meaning is a new identifier, and the old one
is retired with a pointer.

The syntax is narrow for the same reason again. The failure this format fails
at, if it fails, is two groups believing they have agreed when they have not,
and a near-miss identifier is the cheapest way for that to happen. Every rule
above removes a way of writing two strings that a reader would read as one
thing: one case, one separator, one colon, one character set. None of them is
there to make the identifiers tidy.

## The cost

The registry is a governance obligation and not a file. Somebody has to decide
what enters it, refuse a name that duplicates an existing one under a different
spelling, and hold the append-only line against the person who would rather fix
a word than mint a successor. That work does not stop, and it is not work a
check can do: a check can refuse an edit to a landed definition, and it cannot
tell whether two definitions describe one effect.

Who holds that obligation is not decided here. It is entry 2 of issue #15, and
that entry carries the part that makes it urgent rather than merely open: the
registry is cheap to move while it holds a handful of entries and expensive
once outside parties have contributed to it.

The narrow syntax costs every author who has an existing internal name that
does not fit, and there will be many. They write a mapping into this format's
spelling and keep their own, which is work this decision hands to them.

Permitting foreign namespaces costs the guarantee at exactly the point where
this project stops. Two budgets naming identifiers in two foreign namespaces
are correlated only if those namespaces agree with each other, and no reading
of either document establishes that. The format carries the declaration so a
reader can go and look; it does not carry the answer.
