"""The three edits that break the pinning guarantee, each refused by name.

Every near-miss below is the real tree with one thing changed, and each is
paired with the tree it was changed from. That pairing is what stops a test
from passing because the fixture was wrong in some other way as well: the
neighbour has to come out clean under the same code path.

The near-misses are the edits somebody actually makes. A pin appended by hand
with the hashes forgotten is the first one, because that is what happens when a
dependency is added in a hurry and the hashes are looked up afterwards.
"""

import unittest
from pathlib import Path

from gate.pins import Refusal, canonical, examine, parse_lock
from gate.run import ROOT

LOCK = (ROOT / "requirements.lock").read_text(encoding="utf-8")
PYPROJECT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

# A sha256 is 64 hex characters. These are not any real file's digest and are
# not meant to be: this leg reads the file and never the index, which is stated
# in gate/pins.py as one of the things it does not check.
A_HASH = "sha256:" + "ab" * 32
ANOTHER_HASH = "sha256:" + "cd" * 32


def identifiers(refusals):
    return sorted(r.refusal for r in refusals)


class TestTheTreeAsItStandsIsClean(unittest.TestCase):
    """The valid neighbour every near-miss below is one edit away from."""

    def test_nothing_is_refused(self):
        examined = examine(LOCK, PYPROJECT)
        self.assertEqual(examined.refusals, [], examined.summary())

    def test_what_it_examined_is_the_whole_of_both_files(self):
        """Fails if the parser quietly stopped reading part of either file.

        A leg that read three of eight pins would refuse nothing and look
        exactly like one that read all eight, which is why the count is
        printed and asserted rather than only the verdict.
        """
        examined = examine(LOCK, PYPROJECT)
        self.assertEqual(examined.pinned, 8)
        self.assertEqual(examined.declared, 3)
        self.assertEqual(examined.build_requires, 1)
        self.assertEqual(examined.hashes, 243)

    def test_the_header_comments_are_not_read_as_requirements(self):
        """Fails if a commented example command in the lock file's header is
        parsed as a pin. The header contains install commands and a version
        number, which is exactly the shape a careless parser picks up."""
        names = {r.name for r in parse_lock(LOCK)}
        self.assertEqual(
            names,
            {
                "attrs",
                "jsonschema",
                "jsonschema-specifications",
                "numpy",
                "PyYAML",
                "referencing",
                "rpds-py",
                "setuptools",
            },
        )


class TestAPinAppendedWithTheHashesForgotten(unittest.TestCase):
    def test_it_is_refused_as_unhashed_pin(self):
        """Fails if a hand-written pin with no hash behind it passes the gate.

        Without this, the file still refuses the install, but it refuses it on
        the machine of whoever installs next rather than in front of whoever
        wrote the line.
        """
        near_miss = LOCK + "chardet==5.2.0\n"
        refusals = examine(near_miss, PYPROJECT).refusals
        self.assertEqual(identifiers(refusals), ["unhashed-pin"])
        self.assertIn("chardet==5.2.0", refusals[0].subject)

    def test_the_same_pin_with_a_hash_is_clean(self):
        neighbour = LOCK + f"chardet==5.2.0 \\\n    --hash={A_HASH}\n"
        self.assertEqual(examine(neighbour, PYPROJECT).refusals, [])

    def test_the_line_number_names_where_the_edit_is(self):
        """Fails if the refusal sends the reader to the wrong line. The lock
        file is 280 lines of hashes and a refusal that does not say where is a
        refusal somebody has to search for."""
        near_miss = LOCK + "chardet==5.2.0\n"
        expected = len(LOCK.splitlines()) + 1
        refusals = examine(near_miss, PYPROJECT).refusals
        self.assertIn(f"line {expected}", refusals[0].subject)


class TestAPinThatIsARangeRatherThanAVersion(unittest.TestCase):
    def test_a_range_in_the_lock_file_is_refused(self):
        """Fails if a requirement that is not pinned to one exact version
        passes. A range in this file resolves to whatever the index serves on
        the day of the install, which is the property the file exists to
        remove."""
        near_miss = LOCK + f"chardet>=5.2.0 \\\n    --hash={A_HASH}\n"
        refusals = examine(near_miss, PYPROJECT).refusals
        self.assertEqual(identifiers(refusals), ["unhashed-pin"])
        self.assertIn("not pinned with ==", refusals[0].detail)


class TestADeclaredDependencyThatNeverReachesTheLock(unittest.TestCase):
    def test_it_is_refused_as_declared_but_unpinned(self):
        """Fails if the declared set and the pinned set can disagree.

        They are two files and nothing compared them, so a dependency added to
        pyproject.toml and forgotten in requirements.lock installed from
        whatever the resolver found, outside the hash guarantee the other seven
        are inside.
        """
        near_miss = PYPROJECT.replace(
            '    "numpy>=2.5.1",\n',
            '    "numpy>=2.5.1",\n    "requests>=2.32.0",\n',
        )
        self.assertNotEqual(near_miss, PYPROJECT)
        refusals = examine(LOCK, near_miss).refusals
        self.assertEqual(identifiers(refusals), ["declared-but-unpinned"])
        self.assertIn("requests>=2.32.0", refusals[0].subject)

    def test_a_dependency_that_does_reach_the_lock_is_clean(self):
        neighbour = PYPROJECT.replace(
            '    "numpy>=2.5.1",\n',
            '    "numpy>=2.5.1",\n    "attrs>=26.1.0",\n',
        )
        self.assertNotEqual(neighbour, PYPROJECT)
        self.assertEqual(examine(LOCK, neighbour).refusals, [])


class TestTheBuildBackendLeftOutOfTheLock(unittest.TestCase):
    def test_it_is_refused_under_its_own_identifier(self):
        """Fails if the one dependency that runs code during an install can sit
        outside the guarantee every other one is inside.

        It is a separate refusal from the declared set rather than a case of
        it, because the reason is different: a build backend executes, so its
        absence from the lock file costs more than a runtime dependency's.
        """
        near_miss = PYPROJECT.replace(
            'requires = ["setuptools==83.0.0"]',
            'requires = ["hatchling==1.28.0"]',
        )
        self.assertNotEqual(near_miss, PYPROJECT)
        refusals = examine(LOCK, near_miss).refusals
        self.assertEqual(identifiers(refusals), ["build-backend-unpinned"])
        self.assertIn("hatchling==1.28.0", refusals[0].subject)

    def test_the_backend_this_tree_declares_is_in_the_lock(self):
        examined = examine(LOCK, PYPROJECT)
        under_this_refusal = [
            r for r in examined.refusals if r.refusal == "build-backend-unpinned"
        ]
        self.assertEqual(under_this_refusal, [])


class TestTwoSpellingsOfOneNameAreOneDependency(unittest.TestCase):
    def test_case_and_separators_do_not_make_a_second_dependency(self):
        """Fails if the leg refuses a tree that is right.

        pyproject.toml writes PyYAML and the lock file writes PyYAML; the index
        and other tools write pyyaml, and rpds-py is also written rpds_py. A
        comparison that took any of those for two distributions would refuse
        the correct file, which is a worse failure than the one this leg is
        for.
        """
        self.assertEqual(canonical("PyYAML"), canonical("pyyaml"))
        self.assertEqual(canonical("rpds-py"), canonical("rpds_py"))
        self.assertEqual(canonical("jsonschema_specifications"), "jsonschema-specifications")

        renamed = PYPROJECT.replace('"PyYAML>=6.0.3"', '"pyyaml >= 6.0.3"')
        self.assertNotEqual(renamed, PYPROJECT)
        self.assertEqual(examine(LOCK, renamed).refusals, [])


class TestTheParserReadsThePipFormatRatherThanAGuess(unittest.TestCase):
    def test_a_global_option_line_is_not_a_requirement(self):
        """Fails if making the file stricter makes the leg refuse it.
        `--require-hashes` in the file is not a dependency and a leg that read
        it as one would punish exactly the edit it wants."""
        stricter = "--require-hashes\n" + LOCK
        examined = examine(stricter, PYPROJECT)
        self.assertEqual(examined.refusals, [])
        self.assertEqual(examined.pinned, 8)

    def test_an_environment_marker_does_not_make_a_pin_unreadable(self):
        """Fails if a correctly written marker is refused. The tree carries no
        marker today, and the first one somebody adds should not red the
        gate."""
        with_marker = (
            LOCK + f'chardet==5.2.0 ; python_version < "3.15" \\\n    --hash={A_HASH}\n'
        )
        self.assertEqual(examine(with_marker, PYPROJECT).refusals, [])

    def test_several_hashes_on_one_pin_are_all_counted(self):
        counted = examine(
            f"chardet==5.2.0 \\\n    --hash={A_HASH} \\\n    --hash={ANOTHER_HASH}\n",
            PYPROJECT,
        )
        self.assertEqual(counted.hashes, 2)


class TestTheLegIsNamedInTheGateOutput(unittest.TestCase):
    def test_pins_is_a_declared_leg(self):
        """Fails if the refusal exists and the gate does not run it. A property
        that is not dispatched is a rule the repository declares and does not
        apply."""
        from gate.legs import legs

        self.assertIn("pins", [leg.name for leg in legs()])

    def test_the_leg_reads_the_files_this_repository_actually_has(self):
        for name in ("requirements.lock", "pyproject.toml"):
            with self.subTest(path=name):
                self.assertTrue(Path(ROOT / name).is_file())


class TestARefusalCarriesWhatAReaderQuotes(unittest.TestCase):
    def test_the_printed_form_names_the_identifier_first(self):
        printed = str(Refusal("unhashed-pin", "a subject", "a reason"))
        self.assertTrue(printed.startswith("unhashed-pin: "))


if __name__ == "__main__":
    unittest.main()
