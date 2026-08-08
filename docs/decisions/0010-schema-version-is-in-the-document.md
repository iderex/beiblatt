# 0010 The schema version is in the document, and an unknown version is refused

Status: decided. Raised in issue #10.

## The decision

Every document carries the version of the schema it is written against. A
validator that does not implement that version refuses the document and says so,
rather than validating against the version it does implement.

The version is a required element of the document, not a filename convention
and not a directory it sits in. A document separated from its surroundings still
says what it is.

## The refusal behaviour

A document whose declared version the running tool does not implement is
refused. The refusal names the version the document declared and the versions
the tool implements, and it exits by the same path as every other refusal, so a
caller cannot distinguish it from any other failure by exit code alone and does
not have to.

The version is read before anything else is checked. A document declaring an
unimplemented version is not partially validated, and no other finding about it
is reported, because every other finding would be an assertion about rules that
document was not written against.

A missing version element is a separate refusal from an unknown one. The two
have different repairs, and collapsing them would tell somebody who forgot a
field to go and read a compatibility policy.

## Why

This format exists to combine artefacts published years apart, so documents
older than the running tool are the normal case and not an edge one. A tool that
silently applies today's meaning to an older document produces a number that
looks like a combination and is not one.

Refusing is preferable to a best-effort read because the failure it prevents is
invisible. A rejected document sends somebody to look; a quietly reinterpreted
one does not.

Refusing forward is the same argument in the other direction and is the case
that will happen first. A document written against a newer version than the tool
implements contains elements the tool has no rules for, and a validator that
ignores what it does not recognise reports success on a document it did not
read.

## The compatibility policy

Versions are declared and dropped, never silently redefined. A change to what an
existing element means is a new version, and the previous version keeps the
meaning it had on the day it was published.

The set of versions a release implements is stated in that release. Support for
a version ends by removing it from that set in a release that says so, and a
tool that has dropped a version refuses documents declaring it by the refusal
above, naming the last release that implemented it.

The answer to when an old version stops being supported is not never. Carrying
every version forever means one validator holding every rule set ever written,
which is the cost this policy exists to bound. What retires a version is that
the material written against it has been migrated or has stopped being
combined, and the release notes are where that is argued rather than here.

A dropped version does not become invalid. The documents written against it are
still correct documents, and a tool that once implemented it is still the way to
read them. What is lost is the ability to combine them with current material
without migrating them first, and migration is a conversion of the document
rather than a flag on the validator.

## The cost

Supporting several versions means several validators or one validator carrying
several rule sets, and that cost grows with every version that is kept.

The policy above moves the cost rather than removing it. Bounding the supported
set means somebody has to decide when a version leaves it, and that decision
strands whoever had not migrated. Refusing forward means a document written
against a newer version cannot be read by an older tool even where every element
it uses is one the older tool understands, which will look like obstruction the
first time somebody meets it.
