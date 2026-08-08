"""The suite runs with no display, no privilege, no network and no write
outside the tree, and something refuses each of those rather than a document
asking for them.

The rule is easy to hold while there is nothing to test and easy to break in a
year by importing a plotting library at the top of one test file. Nobody
notices, because the machine that runs it has a display. The failure surfaces
on somebody else's machine or in a container, and it surfaces as a suite that
cannot start rather than as a test that fails, which is the hardest kind to
place.

The mechanism is an audit hook. Every refusal below happens at the moment the
interpreter reports the attempt and before the thing is done: no window is
opened, no process is created, no socket exists and no file is written. That
ordering is what makes the near-misses safe to keep in the suite, and it is the
reason a hook was chosen over watching for side effects afterwards.

Four refusals, each named.

`opened-a-window` is an import of a toolkit whose purpose is to put something
on a screen. It refuses the import rather than the window, because an import at
module scope is the shape this actually arrives in, and by the time a window
exists the test has already needed a display to get there.

`acquired-privilege` is a process spawn naming a privilege-acquisition tool.

`opened-a-socket` is any socket, refused when one is made, plus the two ways of
resolving a name that need no socket. A test that reaches the network is not
headless in any useful sense: it fails on a machine with no route out, and that
is the same failure mode as a display dependency.

`wrote-outside-the-tree` is opening a file for writing anywhere but the
repository and the temporary directory.

What this does not catch, stated because a guard read as covering more than it
does is worse than no guard. The privilege check reads the name of the program
being spawned, so a program that calls the elevation interface directly through
a foreign function call is not caught. Deletion, renaming and directory
creation are not covered; only opening for writing is. And an audit hook lives
in one interpreter, so a test that spawns a second interpreter without
installing the guard in it has left what the guard can see.
"""

from __future__ import annotations

import os
import sys
import tempfile

from gate.refusal import Refusal

OPENED_A_WINDOW = "opened-a-window"
ACQUIRED_PRIVILEGE = "acquired-privilege"
OPENED_A_SOCKET = "opened-a-socket"
WROTE_OUTSIDE_THE_TREE = "wrote-outside-the-tree"

REFUSALS = (OPENED_A_WINDOW, ACQUIRED_PRIVILEGE, OPENED_A_SOCKET, WROTE_OUTSIDE_THE_TREE)

# The environment variables that say a display is available, and the one that
# chooses a drawing backend. The leg unsets the first two and pins the third,
# and install() refuses to run if the first two came through anyway, so a
# guarded run cannot quietly have had a screen to draw on.
DISPLAY_VARIABLES = ("DISPLAY", "WAYLAND_DISPLAY")

# Top-level packages whose reason to exist is a window. matplotlib is not here:
# it is usable without a display and the backend variable is what decides that,
# so refusing the import would refuse work this project will want.
WINDOWING = frozenset(
    {"tkinter", "turtle", "PyQt5", "PyQt6", "PySide2", "PySide6", "wx", "gi", "pygame"}
)

# Programs whose job is to run something as somebody else. Matched on the file
# name with any extension removed, so runas and runas.exe are one entry.
PRIVILEGE_TOOLS = frozenset({"runas", "sudo", "doas", "su", "pkexec", "gsudo", "elevate"})

# The PowerShell spelling, which is a verb passed to an ordinary program rather
# than a program of its own.
PRIVILEGE_VERB = "runas"

# Three events and not the six that exist. connect, bind and sendto all need a
# socket object, and socket.__new__ is raised when one is made, so those three
# cannot be reached while this set holds the first entry. Listing them anyway
# would put names in a guard that no fixture can drive, which reads as three
# more things being checked. Name resolution is the one route to the network
# that needs no socket, so both of its events stay.
SOCKET_EVENTS = frozenset({"socket.__new__", "socket.getaddrinfo", "socket.gethostbyname"})

_installed = False


def installed() -> bool:
    """Whether this interpreter has the guard.

    A near-miss asks before it attempts anything, so the attempt is only ever
    made where the thing that refuses it is present.
    """
    return _installed


def asserted() -> tuple[str, ...]:
    """The sentences a run prints, so that what was asserted is in the output
    rather than in this file only."""
    return (
        f"no display: {' and '.join(DISPLAY_VARIABLES)} unset, "
        f"and an import of {len(WINDOWING)} windowing toolkit(s) is refused",
        f"no privilege: a spawn naming {len(PRIVILEGE_TOOLS)} privilege tool(s) "
        f"or the {PRIVILEGE_VERB} verb is refused",
        "no network: a socket is refused at creation, and so is name "
        "resolution by either of the two routes that need no socket",
        "no write outside the repository and the temporary directory",
    )


def roots() -> tuple[str, ...]:
    """Where a test may write. The repository, because that is the tree under
    test, and the temporary directory, because that is where a test puts what
    it makes."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return tuple(os.path.normcase(os.path.abspath(p)) for p in (here, tempfile.gettempdir()))


def _inside(path: str, roots: tuple[str, ...]) -> bool:
    # abspath and normcase rather than resolve, because the hook must not touch
    # the filesystem: an audit hook that opens a file to decide about opening a
    # file does not return.
    candidate = os.path.normcase(os.path.abspath(path))
    return any(candidate == root or candidate.startswith(root + os.sep) for root in roots)


def _top_level(module: str) -> str:
    return module.split(".", 1)[0]


def _basename(word: str) -> str:
    return os.path.splitext(os.path.basename(word))[0].lower()


def _words(command) -> list[str]:
    if isinstance(command, (bytes, bytearray)):
        return command.decode("utf-8", "replace").split()
    if isinstance(command, str):
        return command.split()
    if isinstance(command, (list, tuple)):
        return [w.decode("utf-8", "replace") if isinstance(w, bytes) else str(w) for w in command]
    return [str(command)]


def refuse_privilege(executable, argv=()) -> None:
    """Refuse a command that acquires privilege.

    Two sites, because the two spellings are different things. The first is the
    program being launched: a privilege tool named as the executable or as the
    first word of the command. The second is an ordinary program handed the
    verb that asks the system to elevate it, which the first cannot see because
    the program it names is innocent.

    The first site reads only what is being launched and not the whole argument
    list. Scanning every word refused `git commit -m "sudo this"`, and a guard
    that refuses valid work is one somebody turns off. It also made the second
    site unreachable, because the verb and one of the tool names are the same
    word, and an unreachable site is a rule this repository would have gone on
    claiming.
    """
    words = _words(argv)
    launched = _words(executable)[:1] + words[:1]
    for word in launched:
        if _basename(word) in PRIVILEGE_TOOLS:
            raise Refusal(
                ACQUIRED_PRIVILEGE,
                " ".join(launched),
                "launches a program whose job is to run something with privilege",
            )

    lowered = [word.lower() for word in words]
    for index, word in enumerate(lowered):
        if not word.startswith("-verb"):
            continue
        if PRIVILEGE_VERB in word or PRIVILEGE_VERB in lowered[index + 1 : index + 2]:
            raise Refusal(
                ACQUIRED_PRIVILEGE,
                " ".join(words),
                f"asks for the {PRIVILEGE_VERB} verb, which is the other spelling "
                f"of the same request",
            )


def check_environment(environment) -> None:
    """Refuse a run whose environment says a screen was available.

    Separate from the hook, and called before it is installed, because this is
    a fact about the run rather than about anything a test did. Without it a
    guarded run on a machine with a display would pass and be reported as
    headless.
    """
    present = [name for name in DISPLAY_VARIABLES if environment.get(name)]
    if present:
        raise Refusal(
            OPENED_A_WINDOW,
            ", ".join(present),
            "is set, so this run had a display available and cannot be reported "
            "as one that did not",
        )


def judge(event: str, arguments: tuple, roots: tuple[str, ...]) -> None:
    """Decide one audited event.

    A function rather than a closure inside install(), so that every refusal
    below is reachable from a test in this same interpreter. A site that can
    only be reached by starting a second process is a site the proof leg cannot
    see, and a site nothing can see is one that gets deleted quietly.
    """
    if event == "import":
        if _top_level(arguments[0]) in WINDOWING:
            raise Refusal(
                OPENED_A_WINDOW,
                arguments[0],
                "is a windowing toolkit, and importing one needs a screen to draw on",
            )
    elif event in ("subprocess.Popen", "os.exec", "os.posix_spawn"):
        refuse_privilege(arguments[0], arguments[1])
    elif event == "os.system":
        refuse_privilege(arguments[0])
    elif event in SOCKET_EVENTS:
        raise Refusal(
            OPENED_A_SOCKET,
            event,
            "reaches the network, so the suite fails on a machine with no route out",
        )
    elif event == "open":
        path, mode = arguments[0], arguments[1]
        if path is None or isinstance(path, int) or not isinstance(mode, str):
            return
        if not any(letter in mode for letter in "wxa+"):
            return
        if not _inside(os.fspath(path), roots):
            raise Refusal(
                WROTE_OUTSIDE_THE_TREE,
                os.fspath(path),
                "was opened for writing and is neither in the repository nor in "
                "the temporary directory",
            )


def install() -> None:
    """Put the guard on this interpreter.

    An audit hook cannot be removed once added, which is the property wanted: a
    test cannot turn the guard off for itself and leave the run looking like one
    that was guarded throughout.
    """
    global _installed
    if _installed:
        return

    check_environment(os.environ)
    permitted = roots()
    sys.addaudithook(lambda event, arguments: judge(event, arguments, permitted))
    _installed = True
