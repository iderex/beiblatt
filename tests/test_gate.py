"""The gate, checked against the four things this repository claims about it.

The claims are that the legs run in the declared order, that the walk stops at
the first failure, that the exit code follows the verdict, and that every
declared leg is named in the output whatever happened to it. Each test below
is written so that removing the line in `gate/run.py` that holds the claim
turns it red.

The walk is exercised with legs made here rather than with the repository's
own. A test that ran the real `tests` leg would run this file, which would run
the real `tests` leg. It also means these tests say nothing about whether the
declared set is the right set, which is what the review is for.
"""

import io
import subprocess
import sys
import unittest

from gate.cli import main
from gate.legs import legs
from gate.run import ROOT, Leg, Outcome, walk


def passing(name, marker=None):
    """A leg that passes and records that it ran."""

    def run():
        if marker is not None:
            marker.append(name)
        return Outcome(True, f"{name} was reached")

    return Leg(name=name, decides=f"{name} decides nothing, it is a fixture", run=run)


def failing(name, marker=None):
    def run():
        if marker is not None:
            marker.append(name)
        return Outcome(False, f"{name} was reached and refused")

    return Leg(name=name, decides=f"{name} decides nothing, it is a fixture", run=run)


def unasked(name):
    return Leg(
        name=name,
        decides=f"{name} decides nothing, it is a fixture",
        cost="asking for it would cost the thing this sentence exists to name",
    )


class TestTheWalkStopsAtTheFirstFailure(unittest.TestCase):
    def test_no_leg_after_a_failure_runs(self):
        """Fails if the walk keeps going past a red leg.

        The whole reason the gate is one ordered verb rather than a set of
        independent checks is that the first failure is the one worth reading.
        A walk that continued would also spend the time of every later leg on
        a tree that is already refused.
        """
        reached = []
        code, reports = walk(
            [
                passing("first", reached),
                failing("second", reached),
                passing("third", reached),
            ],
            io.StringIO(),
        )
        self.assertEqual(reached, ["first", "second"])
        self.assertEqual(code, 1)
        self.assertEqual([r.state for r in reports], ["passed", "failed", "not run"])

    def test_a_leg_that_did_not_run_is_not_reported_as_one_that_passed(self):
        """Fails if a leg skipped after a failure is reported with a state that
        a reader could take for a verdict. Not run, not asked for and passed
        are three different states and collapsing any two of them is the defect
        the summary exists against."""
        _, reports = walk([failing("first"), passing("second")], io.StringIO())
        after = reports[1]
        self.assertEqual(after.state, "not run")
        self.assertNotEqual(after.state, "passed")
        self.assertNotEqual(after.state, "not asked for")


class TestTheExitCodeFollowsTheVerdict(unittest.TestCase):
    def test_a_walk_with_nothing_failing_exits_zero(self):
        code, _ = walk([passing("first"), unasked("second")], io.StringIO())
        self.assertEqual(code, 0)

    def test_a_walk_of_legs_none_of_which_ran_still_exits_zero(self):
        """Fails if a run that asked for nothing reported a failure. It has to
        exit zero, which is exactly why the output has to say the legs were not
        asked for: the exit code alone cannot carry that."""
        code, _ = walk([unasked("first"), unasked("second")], io.StringIO())
        self.assertEqual(code, 0)

    def test_one_failing_leg_anywhere_in_the_order_exits_non_zero(self):
        for position in range(3):
            with self.subTest(position=position):
                declared = [passing(f"leg{i}") for i in range(3)]
                declared[position] = failing(f"leg{position}")
                code, _ = walk(declared, io.StringIO())
                self.assertEqual(code, 1)


class TestEveryDeclaredLegIsNamedInTheOutput(unittest.TestCase):
    def test_the_summary_names_a_leg_that_ran_one_that_failed_and_one_that_did_not(
        self,
    ):
        """Fails if any declared leg is missing from the printed summary.

        This is what stops the gate from being read as covering what it printed
        rather than what it declared. The count in the summary comes from the
        same list, so a leg cannot be dropped from the print and left in the
        count.
        """
        out = io.StringIO()
        walk([passing("alpha"), failing("beta"), passing("gamma")], out)
        printed = out.getvalue()
        for name in ("alpha", "beta", "gamma"):
            self.assertIn(name, printed)
        self.assertIn("3 leg(s) declared", printed)

    def test_a_leg_that_was_not_asked_for_prints_what_asking_would_cost(self):
        """Fails if a leg nobody asked for is silently absent, or present with
        no cost. The point of the sentence is that a run covering less than the
        whole set cannot be read as a run that covered it and found nothing."""
        out = io.StringIO()
        leg = unasked("delta")
        _, reports = walk([leg], out)
        self.assertEqual(reports[0].state, "not asked for")
        self.assertIn("not asked for", out.getvalue())
        self.assertIn(leg.cost, out.getvalue())


class TestALegSaysEitherWhatItDoesOrWhatItWouldCost(unittest.TestCase):
    def test_a_leg_with_work_and_a_cost_is_refused(self):
        """Fails if the two fields can drift apart. A leg carrying both would
        print a cost for something it went on to run, which is a sentence the
        reader has no way to place."""
        with self.assertRaises(ValueError):
            Leg(name="both", decides="x", run=lambda: Outcome(True, ""), cost="y")

    def test_a_leg_with_neither_is_refused(self):
        """Fails if a leg can be declared that does nothing and explains
        nothing, which is the silent skip in its purest form."""
        with self.assertRaises(ValueError):
            Leg(name="neither", decides="x")


class TestTheDeclaredSetOfThisRepository(unittest.TestCase):
    def test_every_leg_that_cannot_run_carries_a_cost(self):
        """Fails the moment somebody adds a leg to gate/legs.py that neither
        runs nor says why. The constructor refuses it, so this test is the
        record that the real set is subject to that refusal and not only the
        fixtures above."""
        for leg in legs():
            with self.subTest(leg=leg.name):
                self.assertTrue(leg.run is not None or leg.cost)

    def test_the_names_are_unique(self):
        names = [leg.name for leg in legs()]
        self.assertEqual(sorted(names), sorted(set(names)))

    def test_listing_runs_nothing_and_names_every_leg(self):
        out = io.StringIO()
        code = main(["--list"], out)
        self.assertEqual(code, 0)
        for leg in legs():
            self.assertIn(leg.name, out.getvalue())
            self.assertIn(leg.decides, out.getvalue())

    def test_an_unrecognised_argument_is_refused_rather_than_ignored(self):
        """Fails if a mistyped flag runs the gate anyway. A gate that ran when
        it was asked for something else is a gate whose output does not answer
        the question that was put to it."""
        out = io.StringIO()
        self.assertEqual(main(["--lsit"], out), 2)
        self.assertIn("unrecognised", out.getvalue())


class TestTheCommandIsOneLine(unittest.TestCase):
    def test_python_m_gate_list_runs_from_a_clean_invocation(self):
        """Fails if the package cannot be invoked as the one line this
        repository documents.

        This is the only test here that spawns the gate as a process. It uses
        --list so that it costs one interpreter start and cannot re-enter the
        suite that is running it.
        """
        completed = subprocess.run(
            [sys.executable, "-m", "gate", "--list"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        for leg in legs():
            self.assertIn(leg.name, completed.stdout)


if __name__ == "__main__":
    unittest.main()
