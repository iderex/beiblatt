"""Every place that can refuse something has a test that reaches it.

A coverage figure does not answer this. Coverage counts executed lines, and a
refusal reached by a test that only checks that something failed executes the
line and proves nothing about which refusal it got. Worse, two refusal sites
inside one function are indistinguishable to such a test, so one of them can be
deleted and the suite stays green. The obligation is therefore per site rather
than per rule or per file.

The enumeration is derived from the source. `gate/refusal.py` is the only way
this repository makes a refusal, so every site is a call to that constructor,
and finding them is a parse rather than a list somebody maintains. A
hand-maintained list is the thing that goes stale first, and it goes stale
while looking correct.

A site that genuinely cannot be reached yet is waived in
`unproven-refusal-site/`, which is a debt carrying what retires it rather than
a dispensation. The register fails closed in both directions: a waiver on a
site that is reached again is stale and refused, and a waiver naming a site
that is not in the tree is dangling and refused. A waiver that says nothing
about what would retire it is refused as well, because a debt with no
repayment date is a permission.

What this does not decide is whether the test that reached a site asserted the
right thing. Nothing here reads an assertion. A test that reaches a refusal has
to assert which refusal it got, and that is what the review is for.
"""

from __future__ import annotations

import ast
import atexit
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from gate.refusal import Refusal
from gate.run import ROOT

# The directories whose refusal sites are enumerated. Tests are outside it: a
# fixture constructing a refusal is not a site that ships, and requiring a test
# for it would ask for a test of a test.
SCOPE = ("gate", "src")

# The name of the one constructor. Changing it here without changing
# gate/refusal.py would enumerate nothing and report every site proved, so a
# test asserts the two agree.
CONSTRUCTOR = "Refusal"

REGISTER = "unproven-refusal-site"

# The file in the register that explains the register. It is not a waiver.
REGISTER_README = "README.md"

# Where the recorder is told to write what it saw.
DESTINATION = "BEIBLATT_REFUSAL_PROOF_OUT"

UNPROVEN = "unproven-refusal-site"
WAIVER_NAMES_NO_SITE = "waiver-names-no-site"
WAIVER_ON_A_REACHED_SITE = "waiver-on-a-reached-site"
WAIVER_WITHOUT_A_RETIREMENT = "waiver-without-a-retirement"


@dataclass(frozen=True)
class Site:
    """One place in the source that can refuse something.

    `lines` is the whole span of the constructor call and not only its first
    line. A call written across several lines is executed across several, and
    which of them the interpreter reports is an implementation detail this
    should not depend on.
    """

    path: str
    line: int
    lines: frozenset[int]

    def __str__(self) -> str:
        return f"{self.path}:{self.line}"


@dataclass(frozen=True)
class Waiver:
    """One site admitted to be unreached, with what would retire the admission."""

    path: str
    site: str | None
    retires: str | None


@dataclass
class Proved:
    """What the leg looked at and what it concluded."""

    sites: list[Site] = field(default_factory=list)
    proved: list[Site] = field(default_factory=list)
    waived: list[Site] = field(default_factory=list)
    waivers: list[Waiver] = field(default_factory=list)
    refusals: list[Refusal] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{len(self.sites)} refusal site(s) under {'/, '.join(SCOPE)}/, "
            f"{len(self.proved)} proved, {len(self.waived)} waived, "
            f"{len(self.waivers)} waiver(s) read"
        )


def sites_in(source: str, path: str) -> list[Site]:
    """Every refusal site in one file, from its parse tree."""
    found: list[Site] = []
    for node in ast.walk(ast.parse(source, filename=path)):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        name = getattr(function, "id", None) or getattr(function, "attr", None)
        if name != CONSTRUCTOR:
            continue
        end = node.end_lineno or node.lineno
        found.append(
            Site(path, node.lineno, frozenset(range(node.lineno, end + 1)))
        )
    return sorted(found, key=lambda site: (site.path, site.line))


def scope_files(root: Path) -> list[Path]:
    """Every source file the enumeration reads, in a fixed order."""
    files: list[Path] = []
    for directory in SCOPE:
        files.extend(sorted((root / directory).rglob("*.py")))
    return files


def sites(root: Path) -> list[Site]:
    found: list[Site] = []
    for path in scope_files(root):
        relative = path.relative_to(root).as_posix()
        found.extend(sites_in(path.read_text(encoding="utf-8"), relative))
    return found


def parse_waiver(text: str, path: str) -> Waiver:
    """One waiver, read as the two fields it has to carry."""
    site = None
    retires = None
    for line in text.splitlines():
        if line.startswith("Site:"):
            site = line[len("Site:") :].strip() or None
        elif line.startswith("Retired-when:"):
            retires = line[len("Retired-when:") :].strip() or None
    return Waiver(path, site, retires)


def waivers(root: Path) -> list[Waiver]:
    register = root / REGISTER
    if not register.is_dir():
        return []
    found = []
    for path in sorted(register.iterdir()):
        if not path.is_file() or path.name == REGISTER_README:
            continue
        relative = path.relative_to(root).as_posix()
        found.append(parse_waiver(path.read_text(encoding="utf-8"), relative))
    return found


def judge(found: list[Site], reached: set[tuple[str, int]], waived: list[Waiver]) -> Proved:
    """Compare the sites against what ran and against what is admitted."""
    result = Proved(sites=list(found), waivers=list(waived))

    executed = {site for site in found if any((site.path, line) in reached for line in site.lines)}
    by_name = {str(site): site for site in found}
    waived_names = set()

    for waiver in waived:
        if waiver.site is None or waiver.site not in by_name:
            result.refusals.append(
                Refusal(
                    WAIVER_NAMES_NO_SITE,
                    f"{waiver.path}: {waiver.site or 'no Site: line'}",
                    "names no refusal site in the tree, so it admits a debt that "
                    "nothing owes and would outlive whatever it was written for",
                )
            )
            continue
        if not waiver.retires:
            result.refusals.append(
                Refusal(
                    WAIVER_WITHOUT_A_RETIREMENT,
                    f"{waiver.path}: {waiver.site}",
                    "carries no Retired-when: line, and a debt with nothing that "
                    "repays it is a permission",
                )
            )
            continue
        if by_name[waiver.site] in executed:
            result.refusals.append(
                Refusal(
                    WAIVER_ON_A_REACHED_SITE,
                    f"{waiver.path}: {waiver.site}",
                    "waives a site a test now reaches, so the register is claiming "
                    "a debt that has already been paid",
                )
            )
            continue
        waived_names.add(waiver.site)

    for site in found:
        if site in executed:
            result.proved.append(site)
        elif str(site) in waived_names:
            result.waived.append(site)
        else:
            result.refusals.append(
                Refusal(
                    UNPROVEN,
                    str(site),
                    "can refuse something and no test reached it, so nobody has "
                    "seen it bite",
                )
            )

    return result


def watch() -> None:
    """Record which lines in the scope this interpreter executes.

    Uses the interpreter's own monitoring rather than a coverage dependency,
    because the question is narrow: was this line ever executed. Each location
    is disabled after its first report, so the recording costs one callback per
    line rather than one per execution.
    """
    destination = os.environ[DESTINATION]
    monitoring = sys.monitoring
    tool = monitoring.COVERAGE_ID
    monitoring.use_tool_id(tool, "beiblatt-refusal-proof")

    watched = {
        os.path.normcase(str(path)): path.relative_to(ROOT).as_posix()
        for path in scope_files(ROOT)
    }
    seen: set[tuple[str, int]] = set()

    def line(code, number):
        relative = watched.get(os.path.normcase(code.co_filename))
        if relative is not None:
            seen.add((relative, number))
        return monitoring.DISABLE

    monitoring.register_callback(tool, monitoring.events.LINE, line)
    monitoring.set_events(tool, monitoring.events.LINE)

    def write() -> None:
        Path(destination).write_text(
            json.dumps(sorted(f"{path}:{number}" for path, number in seen)),
            encoding="utf-8",
        )

    atexit.register(write)


def reached_from(destination: Path) -> set[tuple[str, int]]:
    """What the recorder wrote, back as pairs."""
    recorded = json.loads(destination.read_text(encoding="utf-8"))
    pairs = set()
    for entry in recorded:
        path, _, number = entry.rpartition(":")
        pairs.add((path, int(number)))
    return pairs
