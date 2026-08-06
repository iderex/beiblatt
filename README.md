# beiblatt

Every publication carries its systematic uncertainties as running text in a PDF with no correlation information, which makes combining results from different groups practically impossible and has ATLAS and CMS negotiating for months over which systematics are correlated. The schema holds source, magnitude, distributional assumption and correlation to named external sources, plus a reference implementation of the combination arithmetic. The correlations are the point; a budget without them is the PDF table in another syntax. It does not fail on the mathematics but on nobody having defined the format, so the deliverable is reproducing a published combination from two budgets rather than the schema itself.

Planning happens on the issue tracker first. Every decision that shapes
the architecture is written down there with its reasons before the code
that depends on it exists.

See [NOTICE.md](NOTICE.md) for the intended-use notice.
