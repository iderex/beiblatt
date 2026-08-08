"""The proof leg, and the three edits its done-condition names.

Every near-miss here is a fixture handed to the judgement, paired with the
neighbour it is one change away from. That pairing is what keeps a test from
passing because the fixture was broken in some other way as well: the
neighbour has to come out clean through the same code.

The register's four refusals are the reason the leg can be trusted in both
directions. Without them a waiver would be a way of turning the leg off, which
is exactly what somebody reaches for when it goes red at an inconvenient time.
"""

import unittest
from pathlib import Path

from gate.legs import legs
from gate.proof import (
    CONSTRUCTOR,
    REGISTER,
    REGISTER_README,
    UNPROVEN,
    WAIVER_NAMES_NO_SITE,
    WAIVER_ON_A_REACHED_SITE,
    WAIVER_WITHOUT_A_RETIREMENT,
    Waiver,
    judge,
    parse_waiver,
    scope_files,
    sites,
    sites_in,
    waivers,
)
from gate.refusal import Refusal
from gate.run import ROOT

A_FILE = "gate/example.py"

# Two refusal sites in one function, which is the case the whole leg exists
# for: a test that checks only that something failed cannot tell them apart,
# and one of them can be deleted with the suite still green.
TWO_SITES = '''"""A file with two refusal sites in one function."""

from gate.refusal import Refusal


def check(value):
    if value < 0:
        raise Refusal(
            "negative",
            str(value),
            "is below zero",
        )
    if value > 10:
        raise Refusal("too-large", str(value), "is above ten")
'''


def identifiers(refusals):
    return sorted(refusal.refusal for refusal in refusals)


class TestTheEnumerationComesFromTheSource(unittest.TestCase):
    def test_both_sites_in_one_function_are_found_separately(self):
        """Fails if the enumeration counts functions, files or rules rather
        than sites. Per site is the whole point: two arms of one function are
        one line of coverage and two things that can rot."""
        found = sites_in(TWO_SITES, A_FILE)
        self.assertEqual([str(site) for site in found], [f"{A_FILE}:8", f"{A_FILE}:14"])

    def test_a_call_written_over_several_lines_carries_all_of_them(self):
        """Fails if a site is pinned to one line. Which line of a multi-line
        call the interpreter reports as executed is an implementation detail,
        and a proof that depended on it would break on an upgrade rather than
        on a change to this repository."""
        first, second = sites_in(TWO_SITES, A_FILE)
        self.assertEqual(sorted(first.lines), [8, 9, 10, 11, 12])
        self.assertEqual(sorted(second.lines), [14])

    def test_a_file_with_no_refusal_has_no_sites(self):
        self.assertEqual(sites_in("x = 1\n", A_FILE), [])

    def test_the_constructor_it_looks_for_is_the_one_that_exists(self):
        """Fails if the name here and the class in gate/refusal.py drift apart.

        That drift is the quiet failure this leg is most exposed to: nothing
        would be enumerated, every site would be reported proved, and the run
        would be green with a smaller number in it that nobody reads.
        """
        import gate.refusal

        self.assertTrue(hasattr(gate.refusal, CONSTRUCTOR))

    def test_the_tree_has_sites_and_they_are_in_the_declared_scope(self):
        found = sites(ROOT)
        self.assertGreater(len(found), 0)
        for site in found:
            with self.subTest(site=str(site)):
                self.assertTrue(site.path.startswith(("gate/", "src/")))

    def test_the_scope_is_read_from_the_disk_rather_than_listed(self):
        listed = {path.relative_to(ROOT).as_posix() for path in scope_files(ROOT)}
        self.assertIn("gate/proof.py", listed)
        self.assertIn("src/beiblatt/__init__.py", listed)
        self.assertNotIn("tests/test_proof.py", listed)


class TestASiteNoTestReaches(unittest.TestCase):
    def test_it_is_refused_as_unproven(self):
        """Fails if a refusal site can ship with nothing that has seen it bite."""
        found = sites_in(TWO_SITES, A_FILE)
        result = judge(found, {(A_FILE, 8)}, [])
        self.assertEqual(identifiers(result.refusals), [UNPROVEN])
        self.assertEqual(result.refusals[0].subject, f"{A_FILE}:14")
        self.assertEqual([str(site) for site in result.proved], [f"{A_FILE}:8"])

    def test_the_neighbour_where_both_are_reached_is_clean(self):
        found = sites_in(TWO_SITES, A_FILE)
        result = judge(found, {(A_FILE, 10), (A_FILE, 14)}, [])
        self.assertEqual(result.refusals, [])
        self.assertEqual(len(result.proved), 2)

    def test_any_line_of_a_multi_line_call_counts_as_reaching_it(self):
        found = sites_in(TWO_SITES, A_FILE)
        for line in (8, 9, 10, 11, 12):
            with self.subTest(line=line):
                result = judge(found[:1], {(A_FILE, line)}, [])
                self.assertEqual(result.refusals, [])


class TestAWaiverWithNoRetirementCondition(unittest.TestCase):
    def test_it_is_refused(self):
        """Fails if a waiver can be written that never has to be repaid. A debt
        with no repayment is a permission, and a permission is what somebody
        reaches for when the leg goes red at an inconvenient moment."""
        found = sites_in(TWO_SITES, A_FILE)
        waiver = Waiver(f"{REGISTER}/second.md", f"{A_FILE}:14", None)
        result = judge(found, {(A_FILE, 8)}, [waiver])
        self.assertEqual(
            identifiers(result.refusals), sorted([UNPROVEN, WAIVER_WITHOUT_A_RETIREMENT])
        )

    def test_the_same_waiver_with_one_is_clean(self):
        found = sites_in(TWO_SITES, A_FILE)
        waiver = Waiver(
            f"{REGISTER}/second.md",
            f"{A_FILE}:14",
            "the arithmetic milestone gives this branch an input that reaches it",
        )
        result = judge(found, {(A_FILE, 8)}, [waiver])
        self.assertEqual(result.refusals, [])
        self.assertEqual([str(site) for site in result.waived], [f"{A_FILE}:14"])


class TestAWaiverNamingASiteNotInTheTree(unittest.TestCase):
    def test_it_is_refused_as_dangling(self):
        """Fails if a waiver can outlive the site it was written for.

        This is the direction that rots without anybody touching it: the code
        above a site changes, the line moves, and a waiver nobody edited now
        admits a debt that nothing owes while reading as though it covered
        something.
        """
        found = sites_in(TWO_SITES, A_FILE)
        waiver = Waiver(f"{REGISTER}/gone.md", f"{A_FILE}:99", "when the parser lands")
        result = judge(found, {(A_FILE, 8), (A_FILE, 14)}, [waiver])
        self.assertEqual(identifiers(result.refusals), [WAIVER_NAMES_NO_SITE])
        self.assertIn(f"{A_FILE}:99", result.refusals[0].subject)

    def test_a_waiver_with_no_site_line_at_all_is_refused_the_same_way(self):
        found = sites_in(TWO_SITES, A_FILE)
        waiver = Waiver(f"{REGISTER}/empty.md", None, "when the parser lands")
        result = judge(found, {(A_FILE, 8), (A_FILE, 14)}, [waiver])
        self.assertEqual(identifiers(result.refusals), [WAIVER_NAMES_NO_SITE])


class TestAWaiverOnASiteThatIsNowReached(unittest.TestCase):
    def test_it_is_refused_as_stale(self):
        """Fails if the register can go on claiming a debt that was paid.

        Without this the leg fails closed in one direction only: a waiver
        written once would suppress its site for ever, including after somebody
        wrote the test that made it unnecessary.
        """
        found = sites_in(TWO_SITES, A_FILE)
        waiver = Waiver(f"{REGISTER}/paid.md", f"{A_FILE}:14", "when the parser lands")
        result = judge(found, {(A_FILE, 8), (A_FILE, 14)}, [waiver])
        self.assertEqual(identifiers(result.refusals), [WAIVER_ON_A_REACHED_SITE])


class TestTheRegisterAsItStands(unittest.TestCase):
    def test_the_readme_is_not_read_as_a_waiver(self):
        """Fails if the file explaining the register is judged as an entry in
        it, which would red the gate for a document."""
        self.assertTrue((ROOT / REGISTER / REGISTER_README).is_file())
        self.assertEqual([w.path for w in waivers(ROOT) if REGISTER_README in w.path], [])

    def test_every_waiver_in_the_tree_parses_into_its_two_fields(self):
        for waiver in waivers(ROOT):
            with self.subTest(waiver=waiver.path):
                self.assertIsNotNone(waiver.site)
                self.assertTrue(waiver.retires)

    def test_a_waiver_is_read_as_its_two_lines(self):
        parsed = parse_waiver(
            "Site: gate/pins.py:210\nRetired-when: when the schema lands\n\nWhy.\n",
            f"{REGISTER}/one.md",
        )
        self.assertEqual(parsed.site, "gate/pins.py:210")
        self.assertEqual(parsed.retires, "when the schema lands")

    def test_a_field_present_but_empty_is_the_same_as_absent(self):
        parsed = parse_waiver("Site:\nRetired-when:   \n", f"{REGISTER}/one.md")
        self.assertIsNone(parsed.site)
        self.assertIsNone(parsed.retires)


class TestTheLegIsInTheGate(unittest.TestCase):
    def test_proof_is_a_declared_leg(self):
        self.assertIn("proof", [leg.name for leg in legs()])

    def test_the_summary_carries_both_numbers(self):
        """Fails if the run stops printing how many sites there are and how
        many were proved. One number without the other cannot be read."""
        result = judge(sites_in(TWO_SITES, A_FILE), {(A_FILE, 8), (A_FILE, 14)}, [])
        summary = result.summary()
        self.assertIn("2 refusal site(s)", summary)
        self.assertIn("2 proved", summary)
        self.assertIn("0 waived", summary)
        self.assertIn("0 waiver(s) read", summary)

    def test_the_register_directory_is_where_the_leg_looks(self):
        self.assertTrue((ROOT / REGISTER).is_dir())
        self.assertIsInstance(Refusal("a", "b", "c").refusal, str)
        self.assertTrue(Path(ROOT / REGISTER / REGISTER_README).is_file())


if __name__ == "__main__":
    unittest.main()
