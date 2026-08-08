"""A suppression without a reason, refused, and every near-miss kept.

The fixtures are source text handed to the reader, paired with the neighbour
they are one word away from. Each pair is the same suppression twice, once with
a reason and once without, so a test cannot pass because the fixture was broken
in some other way as well.

The markers below live inside string literals, which is the case the reader has
to get right: this file would otherwise refuse the tree for its own fixtures,
and the obvious repair for that is to stop scanning tests, which is where the
awkward suppressions live.
"""

import unittest

from gate.legs import legs
from gate.run import ROOT
from gate.suppressions import (
    SHORTEST_REASON,
    WITHOUT_A_REASON,
    examine,
    judge,
    suppressions_in,
)

A_FILE = "gate/example.py"

BARE = 'import tkinter  # noqa\n'
WITH_CODES = 'import tkinter  # noqa: F401\n'
WITH_A_REASON = 'import tkinter  # noqa: F401  the attempt is the point\n'

IGNORE_BARE = 'value = thing()  # type: ignore\n'
IGNORE_WITH_A_REASON = 'value = thing()  # type: ignore[no-any-return]  the stub lies\n'

PRAGMA_BARE = 'if never():  # pragma: no cover\n    pass\n'
PRAGMA_WITH_A_REASON = 'if never():  # pragma: no cover - the failure message\n    pass\n'


def refused(source):
    return [refusal.refusal for refusal in judge(suppressions_in(source, A_FILE))]


class TestASuppressionWithNoReason(unittest.TestCase):
    def test_a_bare_marker_is_refused(self):
        """Fails if a suppression can be written with nothing said about it.

        Six months later a decision with no reason recorded cannot be told from
        a mistake, and the only safe thing to do with one is leave it alone,
        which is how a tree fills up with suppressions nobody can remove.
        """
        self.assertEqual(refused(BARE), [WITHOUT_A_REASON])

    def test_the_codes_are_not_the_reason(self):
        """Fails if a code list satisfies the requirement.

        This is the near-miss somebody actually writes. `noqa: F401` looks like
        it explains something and says only which check was turned off, which
        is the one thing already obvious from the line it is on.
        """
        self.assertEqual(refused(WITH_CODES), [WITHOUT_A_REASON])

    def test_the_same_line_with_a_reason_is_clean(self):
        self.assertEqual(refused(WITH_A_REASON), [])

    def test_a_reason_shorter_than_the_floor_is_refused(self):
        stub = f'import tkinter  # noqa: F401  {"x" * (SHORTEST_REASON - 1)}\n'
        self.assertEqual(refused(stub), [WITHOUT_A_REASON])


class TestEveryMarkerIsCovered(unittest.TestCase):
    def test_a_type_checker_suppression_needs_one_too(self):
        self.assertEqual(refused(IGNORE_BARE), [WITHOUT_A_REASON])
        self.assertEqual(refused(IGNORE_WITH_A_REASON), [])

    def test_a_coverage_suppression_needs_one_too(self):
        self.assertEqual(refused(PRAGMA_BARE), [WITHOUT_A_REASON])
        self.assertEqual(refused(PRAGMA_WITH_A_REASON), [])

    def test_a_security_scanner_suppression_needs_one_too(self):
        self.assertEqual(refused("run(command)  # nosec\n"), [WITHOUT_A_REASON])
        self.assertEqual(refused("run(command)  # nosec B602  the input is a literal\n"), [])

    def test_the_refusal_names_the_marker_that_was_turned_off(self):
        refusal = judge(suppressions_in(IGNORE_BARE, A_FILE))[0]
        self.assertIn("type: ignore", refusal.detail)
        self.assertEqual(refusal.subject, f"{A_FILE}:1")


class TestWhatIsNotASuppression(unittest.TestCase):
    def test_a_marker_inside_a_string_is_not_one(self):
        """Fails if the reader scans lines rather than comments.

        The file most likely to hold a marker in a string is the one testing
        this check, so a line scan refuses the tree for its own fixtures, and
        the obvious repair for that is to stop reading tests.
        """
        self.assertEqual(suppressions_in('MARKER = "# noqa"\n', A_FILE), [])
        self.assertEqual(suppressions_in("HELP = '''\n# type: ignore\n'''\n", A_FILE), [])

    def test_an_ordinary_comment_is_not_one(self):
        self.assertEqual(suppressions_in("# this comment mentions nothing\n", A_FILE), [])

    def test_a_docstring_naming_a_marker_is_not_one(self):
        self.assertEqual(suppressions_in('"""Explains what noqa means."""\n', A_FILE), [])

    def test_the_line_number_is_the_line_the_comment_is_on(self):
        source = "a = 1\nb = 2\nc = 3  # noqa: F841  kept for the next change\n"
        self.assertEqual(str(suppressions_in(source, A_FILE)[0]), f"{A_FILE}:3")


class TestTheTreeAsItStands(unittest.TestCase):
    def test_nothing_is_refused(self):
        examined = examine(ROOT)
        self.assertEqual(examined.refusals, [], examined.summary())

    def test_the_suppressions_it_found_all_carry_a_reason(self):
        """Fails if the reader stopped finding the ones that are there.

        A check that read nothing refuses nothing and looks exactly like a
        clean tree, so the count is asserted rather than only the verdict.
        """
        examined = examine(ROOT)
        self.assertGreater(len(examined.suppressions), 0)
        for suppression in examined.suppressions:
            with self.subTest(suppression=str(suppression)):
                self.assertGreaterEqual(len(suppression.reason), SHORTEST_REASON)

    def test_it_read_the_tests_as_well_as_the_source(self):
        examined = examine(ROOT)
        self.assertTrue(any(s.path.startswith("tests/") for s in examined.suppressions))


class TestTheLegIsInTheGate(unittest.TestCase):
    def test_suppressions_is_a_declared_leg(self):
        self.assertIn("suppressions", [leg.name for leg in legs()])


if __name__ == "__main__":
    unittest.main()
