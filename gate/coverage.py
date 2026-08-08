"""Line coverage, as a signal and not as evidence.

A line executed by a test that asserts nothing counts here exactly the same as
a line whose behaviour is checked, so a high figure means very little on its
own. What a figure is good for is its second derivative: a sharp drop says
somebody added code and no tests, and that is worth catching on the day it
happens rather than in a review three changes later. This repository's real
coverage obligation is the `proof` leg, which asks the harder question of
whether each refusal has been seen to bite.

The measurement uses the interpreter rather than a coverage dependency. What
counts as a measurable line is read out of the compiled code objects, which is
the same table the interpreter reports line events from, so the denominator is
derived rather than guessed at from the source text. The numerator comes from
the recorder in `gate/proof.py`, which is already run against the same scope.

The floor is a number the suite actually achieved, written down beside the
figure it was derived from and the command that produced it. That is what makes
a later change lowering it visible as a change rather than as a tuning: the two
numbers sit next to each other and one of them has to be edited.

A floor above the recorded measurement is refused. It would be a number nobody
produced, which is the shape a target takes when it is written down as though
it were a measurement.
"""

from __future__ import annotations

import tomllib
import types
from dataclasses import dataclass, field
from pathlib import Path

from gate.proof import scope_files
from gate.refusal import Refusal

CONFIGURATION = "pyproject.toml"
REPORT = Path("build") / "coverage.txt"

BELOW_THE_FLOOR = "coverage-below-the-floor"
FLOOR_ABOVE_THE_MEASUREMENT = "coverage-floor-above-the-measurement"


@dataclass(frozen=True)
class Floor:
    """What the configuration says, as it says it."""

    floor: float
    measured: float
    measured_by: str


@dataclass
class Coverage:
    """The measurement, per file and in total."""

    measurable: dict[str, frozenset[int]] = field(default_factory=dict)
    executed: dict[str, frozenset[int]] = field(default_factory=dict)

    def totals(self) -> tuple[int, int]:
        measurable = sum(len(lines) for lines in self.measurable.values())
        executed = sum(len(lines) for lines in self.executed.values())
        return measurable, executed

    def figure(self) -> float:
        measurable, executed = self.totals()
        if measurable == 0:
            return 0.0
        # Truncated rather than rounded, so a figure never reads higher than
        # what was measured. A floor set from a rounded-up number is a floor
        # nothing has ever reached.
        return int(1000 * executed / measurable) / 10

    def summary(self) -> str:
        measurable, executed = self.totals()
        return (
            f"{executed} of {measurable} measurable line(s) in "
            f"{len(self.measurable)} file(s), {self.figure():.1f}%"
        )

    def report(self) -> str:
        lines = [self.summary(), ""]
        for path in sorted(self.measurable):
            total = self.measurable[path]
            ran = self.executed.get(path, frozenset())
            share = int(1000 * len(ran) / len(total)) / 10 if total else 0.0
            lines.append(f"{path}: {len(ran)}/{len(total)} lines, {share:.1f}%")
            missing = sorted(total - ran)
            if missing:
                lines.append(f"    not executed: {_ranges(missing)}")
        return "\n".join(lines) + "\n"


def _ranges(numbers: list[int]) -> str:
    """Line numbers as ranges, because a report is read by a person."""
    spans: list[str] = []
    start = previous = numbers[0]
    for number in numbers[1:]:
        if number == previous + 1:
            previous = number
            continue
        spans.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = number
    spans.append(str(start) if start == previous else f"{start}-{previous}")
    return ", ".join(spans)


def measurable_lines(source: str, path: str) -> frozenset[int]:
    """Every line the interpreter can report as executed in one file.

    Read out of the compiled code objects rather than out of the source text.
    Deciding from the text which lines are statements means reimplementing a
    part of the compiler and disagreeing with it about continuation lines,
    decorators and the bodies of comprehensions.
    """
    lines: set[int] = set()
    stack = [compile(source, path, "exec")]
    while stack:
        code = stack.pop()
        for _, _, number in code.co_lines():
            if number:
                lines.add(number)
        stack.extend(
            constant for constant in code.co_consts if isinstance(constant, types.CodeType)
        )
    return frozenset(lines)


def measure(root: Path, reached: set[tuple[str, int]]) -> Coverage:
    """What was measurable and what ran, over the same scope the proof leg uses."""
    result = Coverage()
    for path in scope_files(root):
        relative = path.relative_to(root).as_posix()
        total = measurable_lines(path.read_text(encoding="utf-8"), relative)
        result.measurable[relative] = total
        result.executed[relative] = frozenset(
            number for number in total if (relative, number) in reached
        )
    return result


def read_floor(configuration: str) -> Floor:
    """The three numbers the configuration has to carry together."""
    parsed = tomllib.loads(configuration)
    section = parsed.get("tool", {}).get("beiblatt", {}).get("coverage", {})
    return Floor(
        floor=float(section.get("floor", 0.0)),
        measured=float(section.get("measured", 0.0)),
        measured_by=str(section.get("measured-by", "")),
    )


def judge(coverage: Coverage, floor: Floor) -> list[Refusal]:
    """Compare what ran against what the configuration claims."""
    refusals: list[Refusal] = []
    figure = coverage.figure()

    if floor.floor > floor.measured:
        refusals.append(
            Refusal(
                FLOOR_ABOVE_THE_MEASUREMENT,
                f"{CONFIGURATION} [tool.beiblatt.coverage]",
                f"sets a floor of {floor.floor:.1f}% above the {floor.measured:.1f}% "
                f"it records as measured, which is a target written down as though "
                f"it were a measurement",
            )
        )

    if figure < floor.floor:
        refusals.append(
            Refusal(
                BELOW_THE_FLOOR,
                f"{figure:.1f}%",
                f"is below the floor of {floor.floor:.1f}% that "
                f"{CONFIGURATION} sets, which was derived from {floor.measured:.1f}% "
                f"measured by {floor.measured_by}",
            )
        )

    return refusals
