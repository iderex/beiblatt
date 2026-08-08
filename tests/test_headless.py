"""The near-misses, kept.

Each script under tests/nearmiss does one of the things this project says a
test may never do. They are run here rather than deleted after somebody watched
them work once, so the day a refusal stops biting is the day the suite says so
rather than a year later on somebody else's machine.

None of them is dangerous to run, and that is a property of the guard rather
than of the scripts. Every refusal happens at the moment the interpreter
reports the attempt, so no window is drawn, no process is created, no socket
exists and no file is written. Each script asks whether the guard is on the
interpreter before it attempts anything and stops if it is not.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

from gate.headless import (
    ACQUIRED_PRIVILEGE,
    DISPLAY_VARIABLES,
    OPENED_A_SOCKET,
    OPENED_A_WINDOW,
    REFUSALS,
    SOCKET_EVENTS,
    WROTE_OUTSIDE_THE_TREE,
    asserted,
    check_environment,
    judge,
    roots,
)
from gate.refusal import Refusal
from gate.legs import legs
from gate.run import ROOT

NEAR_MISS = ROOT / "tests" / "nearmiss"

ATTEMPTS = (
    (("opens_a_window.py",), OPENED_A_WINDOW),
    (("requests_elevation.py",), ACQUIRED_PRIVILEGE),
    (("writes_outside_the_tree.py",), WROTE_OUTSIDE_THE_TREE),
    # One route per entry in the guard's socket set. connect is the shape
    # somebody writes; the other three exist because each is the only route
    # that reaches its entry, and an entry no fixture drives is a name rather
    # than a check.
    (("opens_a_socket.py", "connect"), OPENED_A_SOCKET),
    (("opens_a_socket.py", "socket"), OPENED_A_SOCKET),
    (("opens_a_socket.py", "resolve"), OPENED_A_SOCKET),
    (("opens_a_socket.py", "name"), OPENED_A_SOCKET),
)


def under_guard(script, *arguments, display=None):
    """Run one script in its own interpreter, with no display in the
    environment, and give back what it did.

    `display` puts one back, which is the only way to reach the check that
    refuses a run whose environment said a screen was available. Setting the
    variable draws nothing; it is a claim about the machine and the guard
    refuses to proceed on it.
    """
    environment = dict(os.environ)
    for name in DISPLAY_VARIABLES:
        environment.pop(name, None)
    if display is not None:
        environment[display[0]] = display[1]
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", str(NEAR_MISS / script), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=environment,
        timeout=180,
        check=False,
    )


class TestEachNearMissIsRefused(unittest.TestCase):
    def test_the_attempt_fails_and_says_which_refusal_caught_it(self):
        """Fails if any attempt goes through.

        The refusal identifier is asserted rather than only the exit code,
        because a script that crashed for an unrelated reason also exits
        non-zero and would otherwise read as a guard that bit.
        """
        for invocation, refusal in ATTEMPTS:
            with self.subTest(attempt=" ".join(invocation)):
                completed = under_guard(*invocation)
                self.assertNotEqual(completed.returncode, 0, completed.stdout)
                self.assertIn(refusal, completed.stderr)
                self.assertNotIn("not refused", completed.stdout)

    def test_every_refusal_this_guard_declares_has_a_near_miss(self):
        """Fails when a refusal is added to the guard with nothing that reaches
        it. A refusal nobody has seen bite is a claim."""
        self.assertEqual(sorted({refusal for _, refusal in ATTEMPTS}), sorted(REFUSALS))

    def test_every_socket_event_the_guard_watches_has_a_route_to_it(self):
        """Fails if an event name is added to the socket set with no fixture
        that reaches it.

        The set was four entries longer once. connect, bind and sendto all need
        a socket object and socket.__new__ refuses one first, so no fixture
        could ever have driven them, and their presence read as three more
        things being checked than were.
        """
        routes = {
            invocation[1] for invocation, _ in ATTEMPTS if invocation[0] == "opens_a_socket.py"
        }
        self.assertEqual(len(SOCKET_EVENTS), 3)
        self.assertEqual(routes, {"connect", "socket", "resolve", "name"})

    def test_the_scripts_the_table_names_are_all_there(self):
        for invocation, _ in ATTEMPTS:
            with self.subTest(attempt=invocation[0]):
                self.assertTrue((NEAR_MISS / invocation[0]).is_file())


class TestEachRefusalInThisInterpreter(unittest.TestCase):
    """Every site, reached here rather than in a child, asserting which refusal
    came back.

    The near-misses above prove the guard end to end, through a real interpreter
    doing a real thing. What they cannot do is show that a particular refusal
    site was the one that fired, because a child process reports an exit code
    and a message and both would look the same if two sites emitted the same
    identifier. These reach each site directly and are what the proof leg sees.
    """

    def refusal_from(self, call, *arguments):
        with self.assertRaises(Refusal) as raised:
            call(*arguments)
        return raised.exception

    def test_a_windowing_import_is_refused(self):
        refusal = self.refusal_from(judge, "import", ("tkinter.ttk",), roots())
        self.assertEqual(refusal.refusal, OPENED_A_WINDOW)
        self.assertEqual(refusal.subject, "tkinter.ttk")

    def test_an_ordinary_import_is_not(self):
        self.assertIsNone(judge("import", ("json",), roots()))

    def test_a_spawn_naming_a_privilege_tool_is_refused(self):
        refusal = self.refusal_from(
            judge, "subprocess.Popen", ("runas", ["runas", "/user:Administrator", "cmd"], None, None), roots()
        )
        self.assertEqual(refusal.refusal, ACQUIRED_PRIVILEGE)
        self.assertIn("runas", refusal.subject)

    def test_a_spawn_asking_for_the_elevation_verb_is_refused(self):
        """Fails if the second spelling stops being caught.

        This is the site the subprocess near-miss cannot reach: it names an
        ordinary program and puts the request in an argument, so the tool-name
        check walks past it. Two sites in one function are indistinguishable to
        a test that only reads the exit code, which is why this one is here and
        not in a child.
        """
        refusal = self.refusal_from(
            judge,
            "subprocess.Popen",
            ("powershell", ["powershell", "-Verb", "RunAs", "-FilePath", "cmd"], None, None),
            roots(),
        )
        self.assertEqual(refusal.refusal, ACQUIRED_PRIVILEGE)
        self.assertIn("-Verb", refusal.subject)

    def test_an_ordinary_spawn_is_not_refused(self):
        self.assertIsNone(
            judge("subprocess.Popen", ("git", ["git", "status"], None, None), roots())
        )

    def test_a_privilege_tool_named_only_in_an_argument_is_not_refused(self):
        """Fails if the guard reads the whole argument list again.

        A commit message mentioning one of these programs is not a request to
        run it, and refusing that is the kind of false positive that gets a
        guard turned off. It is also what made the verb site unreachable, since
        the verb and one of the tool names are the same word.
        """
        self.assertIsNone(
            judge(
                "subprocess.Popen",
                ("git", ["git", "commit", "-m", "sudo this later"], None, None),
                roots(),
            )
        )

    def test_os_system_goes_through_the_same_check(self):
        refusal = self.refusal_from(judge, "os.system", ("sudo make install",), roots())
        self.assertEqual(refusal.refusal, ACQUIRED_PRIVILEGE)

    def test_every_socket_event_is_refused_by_name(self):
        for event in sorted(SOCKET_EVENTS):
            with self.subTest(event=event):
                refusal = self.refusal_from(judge, event, (), roots())
                self.assertEqual(refusal.refusal, OPENED_A_SOCKET)
                self.assertEqual(refusal.subject, event)

    def test_a_write_outside_the_tree_is_refused(self):
        outside = str(Path.home() / "a-file-this-test-never-creates")
        refusal = self.refusal_from(judge, "open", (outside, "w", 0), roots())
        self.assertEqual(refusal.refusal, WROTE_OUTSIDE_THE_TREE)
        self.assertEqual(refusal.subject, outside)

    def test_a_write_inside_the_tree_and_a_read_outside_it_are_not(self):
        """Fails if the guard refuses work it is supposed to allow. Reading is
        not writing, and the repository and the temporary directory are where a
        test is meant to put things."""
        self.assertIsNone(judge("open", (str(ROOT / "build" / "x"), "w", 0), roots()))
        self.assertIsNone(judge("open", (str(Path.home() / "anything"), "r", 0), roots()))
        self.assertIsNone(judge("open", (3, "w", 0), roots()))

    def test_an_environment_offering_a_screen_is_refused(self):
        for variable in DISPLAY_VARIABLES:
            with self.subTest(variable=variable):
                refusal = self.refusal_from(check_environment, {variable: ":0"})
                self.assertEqual(refusal.refusal, OPENED_A_WINDOW)
                self.assertEqual(refusal.subject, variable)

    def test_an_environment_with_no_screen_is_accepted(self):
        self.assertIsNone(check_environment({"PATH": "/usr/bin"}))
        self.assertIsNone(check_environment({name: "" for name in DISPLAY_VARIABLES}))


class TestTheGuardDoesNotRefuseOrdinaryWork(unittest.TestCase):
    def test_the_valid_neighbour_runs_clean(self):
        """Fails if the guard refuses what a test is supposed to do.

        This is the failure that gets a guard turned off rather than fixed, so
        it is checked every run alongside the attempts. The neighbour
        imports from the standard library, writes into the temporary directory
        and spawns a program that is not a privilege tool.
        """
        completed = under_guard("does_nothing_forbidden.py")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("nothing refused", completed.stdout)


class TestARunThatHadADisplayIsNotReportedAsOneThatDidNot(unittest.TestCase):
    def test_the_guard_refuses_to_start_where_the_environment_offers_a_screen(self):
        """Fails if the guard would install on a machine with a display and let
        the run be reported as headless.

        The vehicle is the script that does nothing forbidden, which is the
        point: the refusal is about the environment the run was given and not
        about anything the test did. Without this the guard could pass a run
        that had a screen available throughout, and the leg's first sentence
        would be an assertion nothing made.
        """
        for variable in DISPLAY_VARIABLES:
            with self.subTest(variable=variable):
                completed = under_guard(
                    "does_nothing_forbidden.py", display=(variable, ":0")
                )
                self.assertNotEqual(completed.returncode, 0, completed.stdout)
                self.assertIn(OPENED_A_WINDOW, completed.stderr)
                self.assertIn(variable, completed.stderr)


class TestTheLegSaysWhatItAsserted(unittest.TestCase):
    def test_headless_is_a_declared_leg(self):
        self.assertIn("headless", [leg.name for leg in legs()])

    def test_there_is_a_sentence_for_each_thing_asserted(self):
        """Fails if the guard grows a refusal and the run stops saying what it
        covered. What was asserted has to be in the output, or a reader has to
        open this file to find out what a green run meant."""
        sentences = asserted()
        self.assertEqual(len(sentences), len(REFUSALS))
        for sentence in sentences:
            self.assertTrue(sentence.strip())


class TestTheNearMissesAreNotRunByDiscovery(unittest.TestCase):
    def test_the_directory_is_not_a_package(self):
        """Fails if tests/nearmiss becomes importable.

        Discovery recurses into a directory only when it holds __init__.py.
        These scripts do their attempt at module scope, so the day this
        directory becomes a package is the day the ordinary suite starts making
        the attempts itself, outside any guard.
        """
        self.assertFalse((NEAR_MISS / "__init__.py").exists())

    def test_no_script_here_matches_the_discovery_pattern(self):
        for script in NEAR_MISS.glob("*.py"):
            with self.subTest(script=script.name):
                self.assertFalse(script.name.startswith("test"))


if __name__ == "__main__":
    unittest.main()
