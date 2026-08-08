"""Every dependency that reaches an install is pinned to one exact version and
carries a hash.

`requirements.lock` was written that way and `--require-hashes` makes pip
refuse an install that would fetch anything the file does not carry. What was
missing is anything that refuses the edit which breaks it, so the guarantee
held because of how the file was written rather than because something would
notice it changing.

Three edits break it and each has its own refusal here.

`unhashed-pin` is a requirement in `requirements.lock` that is not pinned with
`==` to one exact version, or that is pinned and carries no `--hash`. The
second shape is the one somebody actually writes: a line appended by hand with
the hashes forgotten. `--require-hashes` does catch it, at the moment somebody
runs the install, which moves the failure from whoever wrote the line to
whoever installs next.

`declared-but-unpinned` is a dependency named in `pyproject.toml` that never
reaches `requirements.lock`. The declared set and the pinned set are two files
and nothing compared them, so a dependency could be added to one and forgotten
in the other in either direction.

`build-backend-unpinned` is the same absence for `[build-system] requires`. It
is separate because the build backend is the one dependency that runs code
during an install, so leaving it outside the guarantee leaves the most
dangerous member outside it while every other one is inside.

What this does not check: whether a hash is the hash the index actually
publishes, whether the pinned version satisfies the floor the declaration asks
for, and whether the set of hashes covers every file for that version. All
three are read from the file rather than from the index, and checking any of
them needs the network, which the suite does not have.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field

from gate.refusal import Refusal

# PEP 503 normalisation. Two spellings of one distribution have to compare
# equal, or `PyYAML` in pyproject.toml and `pyyaml` in the lock file would read
# as two different dependencies and the leg would refuse a tree that is right.
_SEPARATORS = re.compile(r"[-_.]+")

# The leading name of a requirement, in either file. Everything after it is a
# version specifier, an extra, or an environment marker, none of which change
# which distribution is being named.
_LEADING_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")

# A requirement pinned to exactly one version. Anything else in the lock file
# is a range, and a range is what the file exists not to contain.
_EXACT = re.compile(r"(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(?P<extras>\[[^\]]*\])?==(?P<version>[^\s;]+)")


def canonical(name: str) -> str:
    """The name both files have to agree on, whatever case and separators
    either of them spelled it with."""
    return _SEPARATORS.sub("-", name).lower()


@dataclass(frozen=True)
class Requirement:
    """One logical line of `requirements.lock`, after continuations are joined."""

    line: int
    text: str
    name: str | None
    version: str | None
    hashes: tuple[str, ...] = ()


@dataclass
class Examined:
    """What the leg looked at, printed whether or not anything was refused.

    A leg that prints only its refusals says nothing about the size of what it
    read, so a run against a file it failed to parse would look exactly like a
    run against a file with nothing wrong in it.
    """

    pinned: int = 0
    declared: int = 0
    build_requires: int = 0
    hashes: int = 0
    refusals: list[Refusal] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{self.pinned} pinned requirement(s) carrying {self.hashes} hash(es), "
            f"{self.declared} declared dependency(s), "
            f"{self.build_requires} build requirement(s)"
        )


def logical_lines(text: str) -> list[tuple[int, str]]:
    """Requirement lines with comments removed and continuations joined.

    The line number reported is the one the requirement starts on, because that
    is the line somebody edited.
    """
    joined: list[tuple[int, str]] = []
    start: int | None = None
    parts: list[str] = []

    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("#"):
            continue
        # pip treats whitespace followed by # as the start of a comment.
        stripped = re.split(r"\s+#", stripped, maxsplit=1)[0].strip()
        if not stripped and not parts:
            continue

        continues = stripped.endswith("\\")
        if continues:
            stripped = stripped[:-1].strip()
        if start is None:
            start = number
        parts.append(stripped)
        if not continues:
            joined.append((start, " ".join(p for p in parts if p)))
            start = None
            parts = []

    if start is not None:
        joined.append((start, " ".join(p for p in parts if p)))
    return [(number, text) for number, text in joined if text]


def parse_lock(text: str) -> list[Requirement]:
    """Every requirement `requirements.lock` states, with its hashes.

    A line whose first token is an option rather than a name is a global option
    such as `--require-hashes`. It is not a requirement and is not returned;
    refusing it as an unpinned one would refuse a file that had been made
    stricter.
    """
    requirements: list[Requirement] = []
    for number, line in logical_lines(text):
        tokens = line.split()
        if tokens[0].startswith("-"):
            continue
        hashes = tuple(t.removeprefix("--hash=") for t in tokens if t.startswith("--hash="))
        # The options are pulled out first and the environment marker after
        # them, so that a requirement carrying either still reads as the pin it
        # is. Refusing a line for a marker somebody wrote correctly would be
        # this leg refusing valid work, which is worse than the edit it exists
        # to catch.
        specifier = " ".join(t for t in tokens if not t.startswith("-"))
        specifier = specifier.split(";", 1)[0].strip()
        exact = _EXACT.fullmatch(specifier)
        if exact is None:
            leading = _LEADING_NAME.match(specifier)
            requirements.append(
                Requirement(number, line, leading.group(0) if leading else None, None, hashes)
            )
            continue
        requirements.append(
            Requirement(number, line, exact.group("name"), exact.group("version"), hashes)
        )
    return requirements


def parse_pyproject(text: str) -> tuple[list[str], list[str]]:
    """The declared dependencies and the build requirements, as written."""
    parsed = tomllib.loads(text)
    declared = list(parsed.get("project", {}).get("dependencies", []))
    build = list(parsed.get("build-system", {}).get("requires", []))
    return declared, build


def _named(requirement: str) -> str | None:
    match = _LEADING_NAME.match(requirement.strip())
    return match.group(0) if match else None


def examine(lock_text: str, pyproject_text: str) -> Examined:
    """Read both files and return what was looked at and what is refused."""
    result = Examined()
    pinned_names: set[str] = set()

    for requirement in parse_lock(lock_text):
        result.pinned += 1
        result.hashes += len(requirement.hashes)
        if requirement.name is not None:
            pinned_names.add(canonical(requirement.name))

        if requirement.version is None:
            result.refusals.append(
                Refusal(
                    "unhashed-pin",
                    f"requirements.lock line {requirement.line}: {requirement.text}",
                    "not pinned with == to one exact version",
                )
            )
        elif not requirement.hashes:
            result.refusals.append(
                Refusal(
                    "unhashed-pin",
                    f"requirements.lock line {requirement.line}: "
                    f"{requirement.name}=={requirement.version}",
                    "pinned with no --hash behind it, so --require-hashes refuses "
                    "the install instead of this leg refusing the edit",
                )
            )

    declared, build_requires = parse_pyproject(pyproject_text)

    for requirement in declared:
        result.declared += 1
        name = _named(requirement)
        if name is None or canonical(name) not in pinned_names:
            result.refusals.append(
                Refusal(
                    "declared-but-unpinned",
                    f"pyproject.toml [project] dependencies: {requirement}",
                    "declared and absent from requirements.lock, so the declared "
                    "set and the pinned set disagree",
                )
            )

    for requirement in build_requires:
        result.build_requires += 1
        name = _named(requirement)
        if name is None or canonical(name) not in pinned_names:
            result.refusals.append(
                Refusal(
                    "build-backend-unpinned",
                    f"pyproject.toml [build-system] requires: {requirement}",
                    "absent from requirements.lock, and it is the dependency that "
                    "runs code during an install",
                )
            )

    return result
