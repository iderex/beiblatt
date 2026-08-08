"""One refusal, and the only way this repository makes one.

Every place that refuses something builds a `Refusal` here. That is not tidiness:
the leg in `gate/proof.py` finds the refusal sites by looking for this
constructor in the source, so a second way of refusing would be a set of sites
nothing enumerates and nothing requires a test for.

It is an exception as well as a value because refusals arrive both ways. A
checker that reads two files collects every refusal it finds and reports them
together; a guard watching one interpreter has to stop the thing happening, so
it raises. Two classes would mean two constructors and two enumerations, and
the choice between collecting and raising would silently decide whether a site
was counted.
"""

from __future__ import annotations


class Refusal(Exception):
    """One refused subject, under the identifier of the property that refused it.

    The identifier comes first in the printed form because that is what a run
    quotes and what a test matches on. The subject says which line, path or
    name was refused, so a refusal does not send anybody looking. The detail
    says what is wrong with it.
    """

    def __init__(self, refusal: str, subject: str, detail: str) -> None:
        super().__init__(f"{refusal}: {subject}: {detail}")
        self.refusal = refusal
        self.subject = subject
        self.detail = detail

    def __str__(self) -> str:
        return f"{self.refusal}: {self.subject}: {self.detail}"
