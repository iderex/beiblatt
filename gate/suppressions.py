"""Every suppression comment carries a written reason on the same line.

A suppression is a decision. Six months later a decision with no reason
recorded is indistinguishable from a mistake, and the only safe thing to do
with it is leave it alone, which is how a tree accumulates suppressions nobody
can remove. The reason is what makes one of them reviewable and, eventually,
deletable.

The markers are the ones a Python tree carries: `noqa` for a linter,
`type: ignore` for a type checker, `pragma: no cover` for a coverage tool and
`nosec` for a security scanner. They are listed by name rather than matched
loosely, because a rule that guessed at what looked like a suppression would
refuse ordinary prose in a comment.

A reason is text after the marker and after whatever codes it carries. What
counts is length rather than content: nothing here can judge whether a reason
is a good one, and nothing pretends to. The review is where a bad reason is
caught, and a bad reason is at least something to argue with.

This does not enforce that the suppression was necessary, that its codes are
the right ones, or that the tool it addresses is even in this tree. Two of
those become checkable when the linter and the type checker land, and neither
is checkable now.
"""

from __future__ import annotations

import io
import re
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

from gate.refusal import Refusal

# Where a suppression can be written. Wider than the refusal-site scope,
# because a suppression in a test is exactly as unreviewable as one in the
# source and the tests are where the awkward ones live.
SCOPE = ("gate", "src", "tests")

WITHOUT_A_REASON = "suppression-without-a-reason"

# How much text after the codes counts as a reason. Three characters refuses
# the empty case and the single stray letter without pretending to judge what
# a good reason looks like.
SHORTEST_REASON = 3

# Each marker, with the codes it may carry, as one expression. The codes are
# part of the match so that a reason is measured from after them: `noqa: E402`
# on its own is a suppression with no reason, not a suppression whose reason is
# `E402`.
MARKERS = (
    ("noqa", re.compile(r"#\s*noqa(?::\s*[A-Za-z]+[0-9]*(?:\s*,\s*[A-Za-z]+[0-9]*)*)?")),
    ("type: ignore", re.compile(r"#\s*type:\s*ignore(?:\[[^\]]*\])?")),
    ("pragma: no cover", re.compile(r"#\s*pragma:\s*no\s+cover")),
    ("nosec", re.compile(r"#\s*nosec(?::?\s*[A-Za-z0-9_]+(?:\s*,\s*[A-Za-z0-9_]+)*)?")),
)


@dataclass(frozen=True)
class Suppression:
    """One marker found in one line, with whatever followed it."""

    path: str
    line: int
    marker: str
    reason: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}"


@dataclass
class Examined:
    """What was read and what is refused, printed either way."""

    files: int = 0
    suppressions: list[Suppression] = field(default_factory=list)
    refusals: list[Refusal] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{len(self.suppressions)} suppression(s) in {self.files} file(s) "
            f"under {'/, '.join(SCOPE)}/"
        )


def _reason(text: str) -> str:
    """Whatever is left once the punctuation somebody separates with is gone."""
    return text.strip().lstrip("-:;,").strip()


def suppressions_in(source: str, path: str) -> list[Suppression]:
    """Every suppression in one file, with the reason it carries.

    Comment tokens rather than a scan of the lines. A marker inside a string
    literal is not a suppression, and the file most likely to hold one is the
    file testing this check, so a line scan would refuse the tree for its own
    fixtures.
    """
    found: list[Suppression] = []
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        for marker, expression in MARKERS:
            match = expression.search(token.string)
            if match is None:
                continue
            found.append(
                Suppression(path, token.start[0], marker, _reason(token.string[match.end() :]))
            )
    return found


def scope_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for directory in SCOPE:
        files.extend(sorted((root / directory).rglob("*.py")))
    return files


def examine(root: Path) -> Examined:
    result = Examined()
    for path in scope_files(root):
        result.files += 1
        relative = path.relative_to(root).as_posix()
        result.suppressions.extend(
            suppressions_in(path.read_text(encoding="utf-8"), relative)
        )
    result.refusals.extend(judge(result.suppressions))
    return result


def judge(found: list[Suppression]) -> list[Refusal]:
    refusals = []
    for suppression in found:
        if len(suppression.reason) < SHORTEST_REASON:
            refusals.append(
                Refusal(
                    WITHOUT_A_REASON,
                    str(suppression),
                    f"turns off {suppression.marker} and says nothing about why, "
                    f"so nobody after today can tell the decision from a mistake",
                )
            )
    return refusals
