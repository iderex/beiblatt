"""The coverage figure, the floor, and the two ways the pair can lie.

The figure is a signal. Nothing here treats it as saying the code is tested,
and the tests below are about the arithmetic and about the two refusals, not
about the number being high.

The two refusals are what stop the pair from being adjusted instead of earned.
A floor above the figure the configuration records as measured is a target
written down as though it were a measurement, and a figure below the floor is
the drop the whole leg exists to catch.
"""

import unittest

from gate.coverage import (
    BELOW_THE_FLOOR,
    CONFIGURATION,
    FLOOR_ABOVE_THE_MEASUREMENT,
    REPORT,
    Coverage,
    Floor,
    _ranges,
    judge,
    measurable_lines,
    measure,
    read_floor,
)
from gate.legs import legs
from gate.run import ROOT

A_FILE = "gate/example.py"

SOURCE = '''"""A docstring, which the compiler puts on a line of its own."""

CONSTANT = 1


def called(value):
    return value + 1


def never_called(value):
    return value - 1
'''


def coverage_of(measurable, executed):
    return Coverage(
        measurable={A_FILE: frozenset(measurable)},
        executed={A_FILE: frozenset(executed)},
    )


class TestWhatCountsAsAMeasurableLine(unittest.TestCase):
    def test_it_comes_from_the_compiled_code_rather_than_the_text(self):
        """Fails if the denominator is guessed at from the source.

        Deciding from the text which lines are statements means reimplementing
        part of the compiler and then disagreeing with it about continuation
        lines, decorators and comprehension bodies. The compiler's own table is
        the same one the interpreter reports line events from, so numerator and
        denominator come from one place.
        """
        lines = measurable_lines(SOURCE, A_FILE)
        self.assertIn(3, lines)
        self.assertIn(7, lines)
        self.assertIn(11, lines)
        self.assertNotIn(2, lines)
        self.assertNotIn(0, lines)

    def test_an_empty_file_has_no_measurable_lines_and_no_figure(self):
        """Fails if an empty scope divides by zero rather than saying nothing
        ran."""
        empty = Coverage(measurable={A_FILE: frozenset()}, executed={A_FILE: frozenset()})
        self.assertEqual(empty.figure(), 0.0)

    def test_the_tree_measures_as_more_than_nothing(self):
        found = measure(ROOT, set())
        self.assertGreater(sum(len(v) for v in found.measurable.values()), 0)
        self.assertEqual(found.figure(), 0.0)


class TestTheFigure(unittest.TestCase):
    def test_it_is_truncated_rather_than_rounded(self):
        """Fails if a figure can read higher than what was measured. A floor set
        from a rounded-up number is a floor nothing has ever reached."""
        self.assertEqual(coverage_of(range(1, 4), [1, 2]).figure(), 66.6)

    def test_the_summary_carries_both_sides_of_the_fraction(self):
        summary = coverage_of(range(1, 5), [1, 2]).summary()
        self.assertIn("2 of 4 measurable line(s)", summary)
        self.assertIn("50.0%", summary)

    def test_the_report_names_the_lines_that_did_not_run(self):
        """Fails if the report gives a percentage and nothing else. A figure
        with no list of what is missing tells somebody there is a problem and
        not where."""
        report = coverage_of([1, 2, 3, 7, 8, 20], [1, 2]).report()
        self.assertIn("2/6 lines", report)
        self.assertIn("not executed: 3, 7-8, 20", report)

    def test_consecutive_lines_are_written_as_a_range(self):
        self.assertEqual(_ranges([1]), "1")
        self.assertEqual(_ranges([1, 2, 3]), "1-3")
        self.assertEqual(_ranges([1, 3, 4, 9]), "1, 3-4, 9")


class TestTheConfigurationCarriesThreeThingsTogether(unittest.TestCase):
    def test_the_floor_the_measurement_and_the_command_are_read(self):
        parsed = read_floor(
            "[tool.beiblatt.coverage]\n"
            "floor = 70.5\n"
            "measured = 75.8\n"
            'measured-by = "python -m gate"\n'
        )
        self.assertEqual(parsed, Floor(70.5, 75.8, "python -m gate"))

    def test_a_configuration_with_no_section_reads_as_no_floor(self):
        self.assertEqual(read_floor("[project]\nname = 'x'\n"), Floor(0.0, 0.0, ""))

    def test_this_repository_records_all_three(self):
        """Fails if the floor is left in the tree with no measurement beside it
        and no command that produced it. A number on its own is the thing
        somebody edits."""
        parsed = read_floor((ROOT / CONFIGURATION).read_text(encoding="utf-8"))
        self.assertGreater(parsed.floor, 0.0)
        self.assertGreater(parsed.measured, 0.0)
        self.assertTrue(parsed.measured_by)


class TestAFigureBelowTheFloor(unittest.TestCase):
    def test_it_is_refused(self):
        """Fails if a drop can land. This is the whole reason for the leg: not
        that the figure is high, but that it stopped being what it was."""
        refusals = judge(coverage_of(range(1, 5), [1]), Floor(50.0, 60.0, "a command"))
        self.assertEqual([r.refusal for r in refusals], [BELOW_THE_FLOOR])
        self.assertEqual(refusals[0].subject, "25.0%")

    def test_a_figure_exactly_at_the_floor_is_clean(self):
        """Fails if the comparison is strict. A floor is a floor and standing on
        it is allowed, or the number would have to be raised on every change
        that touched nothing."""
        self.assertEqual(judge(coverage_of(range(1, 5), [1, 2]), Floor(50.0, 60.0, "a")), [])

    def test_a_figure_above_it_is_clean(self):
        self.assertEqual(judge(coverage_of(range(1, 5), [1, 2, 3]), Floor(50.0, 60.0, "a")), [])


class TestAFloorAboveWhatWasMeasured(unittest.TestCase):
    def test_it_is_refused(self):
        """Fails if a target can be written into the configuration as though it
        were a measurement.

        The pair exists so that lowering the floor is an edit beside the number
        it contradicts. Raising it past the measurement is the same move in the
        other direction: it makes the recorded figure stop being what the floor
        was derived from, and then neither number means anything.
        """
        refusals = judge(coverage_of(range(1, 5), [1, 2, 3, 4]), Floor(90.0, 60.0, "a"))
        self.assertEqual([r.refusal for r in refusals], [FLOOR_ABOVE_THE_MEASUREMENT])

    def test_both_refusals_can_arrive_together(self):
        refusals = judge(coverage_of(range(1, 5), [1]), Floor(90.0, 60.0, "a"))
        self.assertEqual(
            sorted(r.refusal for r in refusals),
            sorted([BELOW_THE_FLOOR, FLOOR_ABOVE_THE_MEASUREMENT]),
        )

    def test_a_floor_at_or_below_the_measurement_is_clean(self):
        self.assertEqual(judge(coverage_of(range(1, 5), [1, 2, 3, 4]), Floor(60.0, 60.0, "a")), [])


class TestTheLegIsInTheGate(unittest.TestCase):
    def test_coverage_is_a_declared_leg(self):
        self.assertIn("coverage", [leg.name for leg in legs()])

    def test_the_report_is_written_where_nothing_tracks_it(self):
        """Fails if the report would be committed. It is output of a run and
        changes on every run, so it belongs where the ignore file already
        sends build output."""
        self.assertEqual(REPORT.parts[0], "build")
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("build/", ignored)


if __name__ == "__main__":
    unittest.main()
