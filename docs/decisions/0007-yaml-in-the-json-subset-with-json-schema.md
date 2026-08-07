# 0007 YAML restricted to the JSON data model, with JSON Schema as the normative definition

Status: decided. Raised in issue #7.

## The decision

Budgets and assumption sets are YAML documents restricted to the JSON data
model. A JSON Schema is the normative machine-readable definition of the format.
Every valid document must survive a round trip through JSON without loss of
meaning.

## Why

The people expected to write these files by hand already write YAML for data
submissions. A format that starts by asking them to learn a new syntax spends
its first credit on nothing.

JSON Schema has a validator in every language that matters here, which keeps a
second, independent implementation cheap. A format with only one implementation
is a program rather than a standard.

The restriction to the JSON data model exists because YAML has corners that turn
a correct-looking file into a wrong one without an error. None of them is needed
by anything this format describes.

## What is excluded

- Anchors, aliases and merge keys. They make a document non-local to read, so
  the value at a given path cannot be established by looking at that path.
- Non-string mapping keys, including numbers, booleans, dates, sequences and
  mappings used as keys. JSON has string keys only, so any other key loses its
  type on the round trip.
- Tags, both the standard ones and application-specific ones, which carry a type
  the JSON data model has no place for.
- Multiple documents in one stream. One file is one document.
- The types outside the JSON data model: timestamps, sexagesimals, binary, the
  set and ordered-map collections, and the unbounded integer that no longer fits
  a double.
- The implicit typing that reads an unquoted `NO` as a boolean, reads `y` and
  `on` the same way, and treats a version-like `1.2.3` as a string only by
  accident.

## Which artefact is the authority

Where the prose specification and the schema disagree, the schema is the
authority. The specification states this in its own text rather than leaving a
reader to work it out, and a disagreement found between the two is a defect in
the specification until somebody argues otherwise.

## The cost

Two artefacts have to agree, and keeping them in agreement is continuing work
rather than a one-off. A check that refuses the YAML features listed above is
owed, because a rule with nothing to refuse it is a suggestion. Issue #38 holds
it. Until it lands, the exclusion list above is prose and a document using an
anchor will validate.
