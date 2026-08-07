# The landscape

What already exists in this space, what each of those things does and does not
do, and what this project should take from them rather than invent. Raised in
issue #73.

Every claim about something outside this repository names the document or the
record it came from. Where a source is summarised rather than quoted, that is
said in the sentence, because a paraphrase presented as a quotation is a claim
about somebody else's words.

## The repository for published measurement data

HEPData is where the material this project transcribes is deposited, and it is
where a budget would eventually live rather than beside it.

What it does. Its submission format carries uncertainties per data point in two
forms. A symmetric uncertainty is one number, written `symerror`. An asymmetric
one carries both signs explicitly, written `asymerror: {plus: 0.4, minus: -0.3}`,
and a one-sided uncertainty is expressed by leaving one side an empty string.
That is more than a table in a PDF carries and more than this project's readme
implies: the asymmetry of a single component survives the deposit.

It also carries correlation and covariance information. The submission
documentation describes a matrix as a table with two independent variables giving
the bins and one dependent variable giving the value.

Source: the HEPData submission documentation, `data_yaml` page, sections on
uncertainties and on correlation/covariance matrices,
https://hepdata-submission.readthedocs.io/en/latest/data_yaml.html

What it does not do. Three things, and all three are in the record rather than
inferred.

The matrix is a separate table from the measurement it describes, with no link
between the two. HEPData's own issue for this proposes adding a
`related_to_table_doi` key to the submission so that links can be made from one
table to the other, which is a statement that no such link exists today.

The same table structure encodes a covariance matrix and a correlation matrix.
The documentation describes one shape for both and does not carry a field saying
which one a given table is, so a consumer needs a convention that the format does
not supply.

There is no standard for correlation between measurements in different records.
The same issue proposes a YAML block naming an experiment, a source name, a
correlation level such as `fully-correlated`, and the list of table DOIs it
applies to. It is a proposal in an issue and not a format.

That issue is open and it is long-standing:

    gh api repos/HEPData/hepdata/issues/140 \
      --jq '{number, title, state, created_at, updated_at, comments}'
    {"comments":0,"created_at":"2018-04-20T16:48:32Z","number":140,
     "state":"open","title":"Improve support for error correlations etc.",
     "updated_at":"2021-02-04T09:31:05Z"}

Opened in April 2018, last touched in February 2021, still open, and with no
comment on it. Its body records that better support for correlation information,
both within one record and between records, was requested at the 2017 HEPData
advisory board meeting.

A further limit belongs to the matrix rather than to HEPData. A covariance or
correlation matrix holds one number per pair, so an asymmetric component has
nowhere to put its asymmetry once it reaches the matrix, whatever the deposit
carried per point. That is a property of the construction and not a defect of
this repository, and any format that ends in a covariance matrix inherits it,
including this one.

What would change the answer. If the proposal in that issue lands, so that a
record can declare a named correlated source across table DOIs and a matrix can
declare what it is and what measurement it belongs to, then most of what this
project defines would exist there and this project would be a validator and an
arithmetic rather than a format. That is the outcome to hope for rather than to
guard against, and this page is where somebody should look first before writing
more schema.

## The analysis likelihood specifications

The published statistical model of an analysis, in the HistFactory shape that
`pyhf` reads and writes.

What it does. It encodes systematic effects as modifiers that carry a name, and
a name is what makes two of them the same thing. The `pyhf` documentation states
that modifiers with the same name share parameter sets, so a systematic declared
in two channels or on two samples under one name is one parameter and is
correlated by construction rather than by a matrix somebody assembled. The
specification is a JSON workspace with a JSON Schema published beside it.

Source: the `pyhf` likelihood specification page,
https://pyhf.readthedocs.io/en/stable/likelihood.html

The debt is visible and belongs here. Correlation by shared name is where this
project's central design idea comes from. This project did not invent it; it
takes the mechanism out of one analysis and puts it between analyses published by
different groups, which is the part the model cannot reach.

What it does not do. It needs the full statistical model. That model is the
material that is usually not published, which is the case the field has had to
argue for in its own right: a 2021 paper makes the scientific case for
systematically publishing full statistical models and describes the technical
developments that make it practical, which is an argument nobody has to make
about something already routine.

Source: Cranmer et al., "Publishing statistical models: Getting the most out of
particle physics experiments", arXiv:2109.04981, SciPost Phys. 12, 037 (2022).

What would change the answer. If publishing the full model became the norm across
the groups whose results this project wants to combine, then combining from
likelihoods would beat combining from budgets, and the honest response would be to
say so. Decision
[0011](decisions/0011-the-reference-arithmetic-is-blue.md) puts likelihood
combination out of scope on exactly the ground that the input is not published,
so the condition that would reopen it is written down rather than implied.

## The implementations of the combination arithmetic

The best linear unbiased estimate has a mature implementation and a literature,
and this project's own arithmetic is measured against them rather than proposed
against them.

What they do. The BLUE software combines m correlated estimates of n observables
as a C++ class used inside the ROOT analysis package. Its abstract describes what
it offers: disabling specific estimates or uncertainty sources, investigating
different correlation assumptions, and combining according to the importance of
the estimates, all from within the software and, in its own words, without
touching the input.

Source: Nisius, "BLUE: combining correlated estimates of physics observables
within ROOT using the Best Linear Unbiased Estimate method", arXiv:2001.10310,
SoftwareX 11 (2020) 100468. The method paper behind it is Nisius, "On the
combination of correlated estimates of a physics observable", arXiv:1402.4016,
Eur. Phys. J. C (2014) 74:3004.

The iterative variant, and its bias, are established results rather than a
discovery this project would make. Lista, "The bias of the unbiased estimator: a
study of the iterative application of the BLUE method", arXiv:1405.3425,
Nucl. Instrum. Meth. A764 (2014) 82-93 with a corrigendum in A773 (2015) 87-96,
states in its abstract that the method is unbiased by construction when the true
uncertainties and correlations are known and may exhibit a bias when estimated
uncertainties are used in place of the true ones, particularly when those
estimates depend on the measured values.

What they do not do. They are not a format. What they take is the estimates, the
uncertainty sources and the correlation assumptions, handed to the class by the
program that calls it. Nothing in them reads a published budget, and no
interchange definition is offered for the input, so where those numbers come from
is outside the software. The phrase "without touching the input" in the abstract
is the point: varying an assumption is cheap once the input exists, and building
the input is the expensive part. That is the work this project is trying to make
unnecessary.

What would change the answer. If one of these implementations grew a documented
input format that other groups published against, the format problem would be
solved there and this project would be redundant. Nothing in the sources above
suggests that is happening.

## The community recommendations on publishing correlated uncertainties

The LHC Reinterpretation Forum has published recommendations on how results
should be presented, and correlation is one of the things they address.

Source: Abdallah et al., "Reinterpretation of LHC Results for New Physics: Status
and Recommendations after Run 2", arXiv:2003.07868, SciPost Phys. 9, 022 (2020).
The statements below are summarised from that paper rather than quoted.

What they do. For searches, the paper recommends publishing covariance or
error-source information between signal regions in a stated order of preference:
first a decomposition into orthogonal error sources given as part of the primary
dataset, then a separate covariance matrix, and last a separate correlation
matrix. For measurements, it records that a breakdown of systematic uncertainties
into correlated components is increasingly available on HEPData and asks for
statistical covariance matrices and signed systematic shifts by uncertainty
source to be released systematically. For Higgs measurements it asks for
channel-by-channel correlation or covariance matrices given separately for
experimental, theoretical and total uncertainties.

What they do not do. They stop at what should be published and do not specify a
document that carries it. There is no schema, no validator, and no identifier for
a named systematic source, so two groups can both follow the recommendation and
still produce material that cannot be combined without a person reconciling the
names.

What would change the answer. If a schema were attached to those recommendations
by the forum or by the data repository, this project should adopt it rather than
compete with it, and this page is where that has to be noticed.

## What to adopt instead of inventing

Four things, each with the issue it changes.

The order of preference for correlation information is already stated by the
reinterpretation forum, and its first preference is a decomposition into named
orthogonal error sources. That is the shape of a budget in this project. The
specification should cite the recommendation as the reason for the shape rather
than argue it from first principles, which changes #35 and gives #2 an external
support it currently lacks.

The asymmetric uncertainty encoding is already fixed by HEPData, including the
one-sided case expressed by an empty side. Inventing a second spelling for the
same thing would cost every transcription a conversion and every reader a
lookup. This changes #6 and #36.

Correlation by shared name is `pyhf`'s mechanism, and this project should credit
it in the specification rather than present it as new. This changes #35 and #2.

The identity of a transcribed measurement already exists as a HEPData table DOI,
which is minted, resolvable and not this project's to invent. A budget
transcribed from a deposited record should carry that DOI as its provenance
rather than a locally invented reference. This changes #35 and #59, and it is
separate from the source identifier registry in #8, which names systematic
sources rather than measurements.

## What this page does not settle

Whether this project should exist at all is decided by the first section rather
than by this one. The answer today is that the linking, the covariance-versus-
correlation declaration and the cross-record correlation block are proposals in
an issue that has been open since 2018 and has attracted no comment, and a
proposal is not a format. If that changes, the argument for this project changes
with it.
