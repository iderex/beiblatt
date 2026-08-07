# The reproduction target

The target of the reproduction, and the public material its inputs will be
transcribed from, fixed before any transcription starts. Raised in issue #59.

Every statement below about something outside this repository carries the
command that produced it. The commands were run on 2026-08-07 and their output
is pasted as it came back.

## The target

The combination of top quark mass measurements from data collected by the ATLAS
and CMS experiments at centre-of-mass energies of 7 and 8 TeV, published in 2024.

    $ curl -sS "http://export.arxiv.org/api/query?id_list=2402.08713"

Title, as given there:

    Combination of measurements of the top quark mass from data collected
    by the ATLAS and CMS experiments at sqrt(s) = 7 and 8 TeV

Identifiers:

- preprint: arXiv:2402.08713, submitted 2024-02-13, revised 2024-08-07
- literature record: INSPIRE 2789110
- journal: Phys. Rev. Lett. 132 (2024) 261902
- publisher DOI: 10.1103/PhysRevLett.132.261902
- report numbers: CMS-TOP-22-001, ATLAS-TOPQ-2019-13, CERN-EP-2024-020

The record resolves and the identifiers above are read from it:

    $ curl -sS "https://inspirehep.net/api/literature/2789110?fields=titles,arxiv_eprints,publication_info,dois,control_number"

## The numbers to be reproduced

Quoted with the digits as published. From the abstract of the preprint:

    m_t = 172.52 +- 0.14 (stat) +- 0.30 (syst) GeV,
    with a total uncertainty of 0.33 GeV

The abstract also states that fifteen measurements are combined and that the
combination achieves an improvement in the total uncertainty of 31 percent
relative to the most precise input measurement. Both are things the reproduction
can be checked against, and the second one only if the input set is transcribed
correctly, which makes it a useful second target rather than a restatement of the
first.

Two further published values are available and are recorded here because they are
in the deposited data rather than only in the paper:

    ATLAS-only combination:  172.71, statistical uncertainty 0.25
    CMS-only combination:    172.52, statistical uncertainty 0.14

## The deposited data

There is a HEPData record for this paper.

    $ curl -sS "https://www.hepdata.net/record/ins2789110?format=json"

It is record 143309, version 1, last updated 2024-07-03, and it holds exactly one
table:

    Table 1, DOI 10.17182/hepdata.143309.v1/t1
    "Uncertainties on the m_t values extracted in the LHC, ATLAS, and CMS
     combinations arising from the categories described in the text, sorted in
     order of decreasing value of the combined LHC uncertainty."
    location: Data from Table 2

The table content was retrieved:

    $ curl -sS "https://www.hepdata.net/record/data/143309/1666165/1/"

It carries three rows, one per combination: LHC, ATLAS and CMS. Each row carries
the extracted mass value and a labelled per-category uncertainty, twenty-five
categories on the LHC row, each as a `symerror`. The categories are named, for
example `sys,LHCbJES`, `sys,b tagging`, `sys,ME generator`, `sys,QCD radiation`
and `sys,Color reconnection`.

The table is CC0:

    "name": "CC0",
    "url": "https://creativecommons.org/publicdomain/zero/1.0/"

which matters because it settles whether these numbers may be redistributed
inside this repository. They may.

### What the deposit does not carry

This is the finding of this issue and it is the reason it is written down before
transcription starts rather than discovered during it.

The deposit holds the uncertainty breakdown of the three combination **outputs**.
It does not hold the fifteen input measurements, it does not hold their
per-category uncertainty breakdowns, and it does not hold the correlation
strengths between the two experiments. Those are the material a budget and an
assumption set are made of, and none of it is in the machine-readable deposit.

    $ curl -sS "https://www.hepdata.net/record/ins2789110?format=json" \
        | python -c "import sys,json; print(len(json.load(sys.stdin)['data_tables']))"
    1

One table. So the reproduction inputs are transcribed from the paper, and the
deposit is usable only as a check on the answer rather than as a source for the
inputs.

That is not a complaint about this paper, which publishes more than most. It is a
statement about the state this project exists because of: the paper's own
correlation table is the disputed quantity the field negotiated over, and it is
published as a table in a document rather than as data anybody can consume.

## Where the inputs come from

From the preprint's HTML rendering, read at

    https://arxiv.org/html/2402.08713v2

- Table 1 of the paper gives the correlation strengths between ATLAS and CMS for
  each systematic uncertainty category, as used in the combination. That is the
  assumption set, and it is what #61 transcribes.
- Table 2 of the paper gives the uncertainties on the extracted values by
  category. That is the table deposited on HEPData, which the deposit itself
  confirms by recording its location as "Data from Table 2".
- The supplemental material carries the per-measurement results and systematic
  uncertainties for the ATLAS measurements and for the CMS measurements
  separately, and the BLUE weights and pulls of each input measurement. Those
  per-measurement tables are what #60 transcribes.

The supplemental tables are NOT numbered here. The rendering they were read from
returned an inconsistent numbering for them, so any number written here would be
a guess dressed as a citation. Establishing their numbering against the published
article is part of #60 and is not done by this document.

## What is confirmed, and what is not

Confirmed by fetching, with the commands above: the preprint record, the
literature record, the existence and contents of the HEPData record, its single
table, that table's licence, and the published combined value with its quoted
precision.

Not confirmed: the numerical contents of the paper's Table 1 and of the
supplemental per-measurement tables. They were not transcribed here and no number
from them appears in this document. Reading them out of the article is #60 and
#61, and a number in either of those has to carry its own source.

## One thing already visible in the deposited numbers

Summing the twenty-five deposited LHC categories in quadrature does not reproduce
the quoted systematic uncertainty exactly:

    $ curl -sS "https://www.hepdata.net/record/data/143309/1666165/1/" -o t1.json
    $ python -c "
    import json, math
    d = json.load(open('t1.json', encoding='utf-8'))
    for row in d['values']:
        name = row['x'][0]['value']
        errs = row['y'][0]['errors']
        sys = [float(e['symerror']) for e in errs if e['label'].startswith('sys')]
        stat = [float(e['symerror']) for e in errs if e['label'] == 'stat']
        q = math.sqrt(sum(v * v for v in sys))
        tot = math.sqrt(q * q + sum(v * v for v in stat))
        print('%-6s value=%s  n_sys=%2d  quadrature(sys)=%.4f  stat=%.2f  total=%.4f'
              % (name, row['y'][0]['value'], len(sys), q, stat[0], tot))
    "
    LHC    value=172.52  n_sys=25  quadrature(sys)=0.3056  stat=0.14  total=0.3362
    ATLAS  value=172.71  n_sys=22  quadrature(sys)=0.4147  stat=0.25  total=0.4843
    CMS    value=172.52  n_sys=24  quadrature(sys)=0.3918  stat=0.14  total=0.4161

The LHC row gives 0.3056 against a published 0.30, and a total of 0.3362 against
a published 0.33. Every deposited category is given to two decimal places, and
summing rounded numbers in quadrature is enough to explain a difference of this
size. It is recorded here because the quadrature check in #60 will hit it on the
first run, and a check that fires on a known rounding effect has to be expected
rather than investigated as a transcription error. It is also the first concrete
argument for the tolerance policy: a comparison against a published number that
demands exactness would fail here on arithmetic that is not wrong.

The ATLAS and CMS rows are not the same quantity as the LHC row and are not
checked against a published total here, because no published total for them is
quoted in this document.
