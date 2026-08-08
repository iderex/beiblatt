"""How a fixture whose bytes matter is carried.

    from fixtures import b64

    A_BUDGET_WITH_A_CARRIAGE_RETURN = b64("bmFtZTogYQ0KdmFsdWU6IDEK")

A fixture in this project is usually a document that is meant to be wrong in
one specific way. Where the wrongness is a byte rather than a word, that byte
is the first thing a normalisation setting removes: a carriage return, a
trailing space before a newline, a tab, a byte order mark. Checked in as a file
it goes through git's clean and smudge filters, and this repository's
.gitattributes stores and checks out LF, so the carriage return a fixture
exists to carry does not come back out. The test then feeds a clean document to
a validator that correctly accepts it, and the suite passes while proving the
opposite of what it claims.

Base64 is ASCII with no line ending in it, so a fixture written this way is the
same bytes in every clone on every platform, and no setting anywhere can reach
it. The cost is that the fixture is not readable at a glance, which is the
reason for the helper: `b64(...)` at the point of definition is one word saying
that these bytes are exact, and a fixture that skipped it is a raw literal
sitting where every other fixture has that word.

Where the bytes do not matter, a plain string literal is right and this helper
is noise. The line to draw is whether the test would still be testing what it
says if a byte changed on the way in.
"""

import base64

__all__ = ["b64"]


def b64(encoded: str) -> bytes:
    """The exact bytes of a fixture, from its base64 in source."""
    return base64.b64decode(encoded)
