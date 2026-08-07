# Security policy

## Supported versions

None yet. Nothing has been released and no version is tagged, so there is no
released version to support and no supported-version table that would say
anything true. The default branch is the only thing that exists.

When a first release is made this section is replaced with the versions that
receive fixes and the ones that do not.

## Reporting a vulnerability

Report privately through this repository's security advisory page, under the
Security tab, using "Report a vulnerability". Private vulnerability reporting is
enabled, so the form is there and a report through it is not public.

Do not open a public issue for a vulnerability, and do not send a proof of
concept to a public tracker.

If you have already published the finding somewhere, say so in the report. It
changes nothing about whether the report is welcome and it changes a great deal
about what can usefully be done next.

## What a reporter can expect

An acknowledgement that the report arrived, an assessment of whether it is in
scope, and, where it is, a fix or a written statement of why it is not being
fixed. Where a report is declined, the reason is given rather than the report
being left unanswered.

The intent is to acknowledge within a week and to reach an assessment within a
month. Those are intentions and not a guarantee. This project has no staffed
security response and cannot promise a time it might not keep, and a policy that
promised one would be making a claim it has no way to hold. If a report has gone
unanswered past those intentions, sending a reminder through the same private
route is the right thing to do rather than an imposition.

There is no bounty, no payment and no swag.

Credit is offered to a reporter who wants it, and withheld from a reporter who
does not. Say which in the report.

## Scope

This project is a document format, a validator for it, and an implementation of
the combination arithmetic. Its attack surface is not the usual one for an
application, so scope is written out here rather than assumed.

In scope:

- The validator parsing a document it did not write. A budget or an assumption
  set arriving from another group is untrusted input by definition, which is the
  point of the format: it exists so that documents travel between groups. A
  crash, an unbounded allocation, an unbounded run time, a file read outside the
  document, a network request, or any execution of content from the document
  itself, all reached by a document that a user was willing to validate, is a
  vulnerability in this project.
- The combination tool reading budgets that were fetched from a repository. The
  same argument, one step further along: the documents were not written here, the
  operator who fetched them did not read every byte, and the tool has to survive
  the ones that are hostile rather than merely wrong.
- The specification and the schema themselves. If the schema permits a construct
  that makes a conforming implementation consume unbounded memory or unbounded
  time, that is a defect in the specification and it is in scope here, even where
  no implementation in this repository is affected. A format defines what every
  implementation of it must accept, so a specification that requires a dangerous
  construct to be accepted has put the defect into implementations this project
  will never see. This is unusual enough as a scope statement that it is written
  down rather than left to be inferred.
- The dependencies this project pins, where a version pinned here carries a known
  vulnerability that reaches a user of this project.
- The workflow files in this repository, which run with a token and are the only
  thing here that does.

Out of scope:

- A document that is merely invalid. A validator refusing a wrong document is the
  validator working. A report has to show that a document does something worse
  than being refused.
- A result that is numerically wrong. That is a correctness defect and belongs on
  the issue tracker in the open, where it can be argued about, not in a private
  advisory.
- Anything about a service this project operates, because it operates none. There
  is no hosted validator and no hosted registry.
- Findings from an automated scanner pasted without a statement of what an
  attacker gains. A report has to say what the impact is.

## The state this policy is written in

There is no parser and no arithmetic in this repository yet:

    git ls-files | grep -vE '\.(md|yml)$'

returns nothing at the commit this file landed on. The scope section above is
therefore a statement about what will be in scope as those parts arrive, and
today the only in-scope surface that actually exists is the last item, the
workflow files. Saying so here is the honest version; a scope section describing
a validator that does not exist would read as though one did.
