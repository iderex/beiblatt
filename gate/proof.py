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


# The prelude the recorded run starts with. It is a string rather than a
# function because of what it has to happen before: every line of this
# repository that runs at import time, including the lines of this file. A
# function here would be reached only after importing the module holding it,
# and everything imported on the way would be reported as never executed. It
# records every line it sees and the filtering to the scope happens at the end,
# which is the only order that leaves nothing out.
RECORDER = (
    "import sys;"
    "_m=sys.monitoring;"
    "_m.use_tool_id(_m.COVERAGE_ID,'beiblatt-line-recorder');"
    "_seen=set();"
    "_m.register_callback("
    "_m.COVERAGE_ID,_m.events.LINE,"
    "lambda code,number:(_seen.add((code.co_filename,number)),_m.DISABLE)[1]);"
    "_m.set_events(_m.COVERAGE_ID,_m.events.LINE);"
    "from gate.proof import record;"
    "record(_seen);"
)


def record(seen: set[tuple[str, int]]) -> None:
    """Write what the prelude saw, filtered to the scope, when the run ends.

    Filtering here rather than in the callback is what lets the recording start
    before this file is imported. The set the prelude fills holds every line the
    interpreter executed anywhere, which is large and costs one entry per
    location because each one is disabled after its first report.
    """
    destination = os.environ[DESTINATION]
    watched = {
        os.path.normcase(str(path)): path.relative_to(ROOT).as_posix()
        for path in scope_files(ROOT)
    }

    def write() -> None:
        # Stop recording before reading, or the iteration below executes lines
        # that the callback is still adding to the set it is iterating.
        monitoring = sys.monitoring
        monitoring.set_events(monitoring.COVERAGE_ID, monitoring.events.NO_EVENTS)
        inside = {
            f"{watched[name]}:{number}"
            for name, number in ((os.path.normcase(f), n) for f, n in seen)
            if name in watched
        }
        Path(destination).write_text(json.dumps(sorted(inside)), encoding="utf-8")

    atexit.register(write)


def reached_from(destination: Path) -> set[tuple[str, int]]:
    """What the recorder wrote, back as pairs."""
    recorded = json.loads(destination.read_text(encoding="utf-8"))
    pairs = set()
    for entry in recorded:
        path, _, number = entry.rpartition(":")
        pairs.add((path, int(number)))
    return pairs
