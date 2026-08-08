"""A fixture's bytes survive version control, and a raw one does not.

The second half is the point. It would be easy to assert that base64 decodes to
what it encodes, which is true of base64 and says nothing about git. What is
asserted here is the difference: the same bytes, in the same scratch
repository, under this repository's own .gitattributes, come back intact when
they were carried encoded in source and come back changed when they were
checked in raw.

The scratch repository is built in a temporary directory and gets its
.gitattributes by copying this repository's, so the test measures the file the
tree actually has rather than a copy of it written here that could drift.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from fixtures import b64
from gate.run import ROOT

# "budget: a\r\nvalue: 1\r\n". A document whose only defect is a carriage
# return: the shape where the wrongness a fixture exists to carry is one byte,
# and the byte is the first thing a normalisation setting removes.
A_DOCUMENT_WITH_CARRIAGE_RETURNS = "YnVkZ2V0OiBhDQp2YWx1ZTogMQ0K"

# What a test file carrying that fixture looks like. It is ASCII with no
# carriage return anywhere in it, which is why no setting can reach the bytes
# it stands for.
ENCODED_SOURCE = f'from fixtures import b64\n\nDOCUMENT = b64("{A_DOCUMENT_WITH_CARRIAGE_RETURNS}")\n'


def git(*args, cwd, autocrlf=None):
    """git, with the working-tree conversion setting forced where one is given.

    Passing core.autocrlf explicitly is how the test stands in for the platform
    it is not running on. A contributor on the other default is the case the
    convention exists for, and asserting it here beats asserting it on one
    machine and assuming the other.
    """
    settings = [] if autocrlf is None else ["-c", f"core.autocrlf={autocrlf}"]
    return subprocess.run(
        ["git", *settings, *args],
        cwd=cwd,
        capture_output=True,
        text=False,
        check=True,
    )


class TestTheHelperCarriesExactBytes(unittest.TestCase):
    def test_the_carriage_return_is_in_what_it_decodes_to(self):
        self.assertIn(b"\r\n", b64(A_DOCUMENT_WITH_CARRIAGE_RETURNS))
        self.assertEqual(b64(A_DOCUMENT_WITH_CARRIAGE_RETURNS), b"budget: a\r\nvalue: 1\r\n")

    def test_the_encoded_form_carries_no_line_ending_of_its_own(self):
        """Fails if the base64 in source could itself be rewritten. That is the
        whole reason the convention works, so it is asserted rather than
        assumed."""
        self.assertNotIn("\r", A_DOCUMENT_WITH_CARRIAGE_RETURNS)
        self.assertNotIn("\n", A_DOCUMENT_WITH_CARRIAGE_RETURNS)
        self.assertTrue(A_DOCUMENT_WITH_CARRIAGE_RETURNS.isascii())


class TestARoundTripThroughVersionControl(unittest.TestCase):
    """The bytes are put through git's clean and smudge filters, under this
    repository's .gitattributes, on each of the three settings a contributor's
    platform might have installed.

    The trip is working tree to object store to working tree, which is the trip
    that rewrites a file. It is done without a commit, so the suite needs no
    signing key on the machine running it; a clone would run the same two
    filters over the same attributes and is what the pull request records by
    hand.
    """

    def round_trip(self, autocrlf):
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            checkout = Path(temporary) / "checkout"
            repository.mkdir()
            checkout.mkdir()

            attributes = ROOT / ".gitattributes"
            self.assertTrue(
                attributes.is_file(),
                "there is no .gitattributes, so nothing in this tree decides "
                "what git does to a file and every fixture is at the mercy of "
                "whoever cloned it",
            )

            git("init", "-q", str(repository), cwd=temporary, autocrlf=autocrlf)
            shutil.copyfile(attributes, repository / ".gitattributes")

            # The same document twice: once checked in as itself, once carried
            # encoded inside a source file.
            (repository / "raw.yaml").write_bytes(b64(A_DOCUMENT_WITH_CARRIAGE_RETURNS))
            (repository / "encoded.py").write_text(ENCODED_SOURCE, encoding="ascii", newline="")

            git("add", "-A", cwd=repository, autocrlf=autocrlf)
            git(
                "checkout-index",
                "--all",
                "--force",
                f"--prefix={checkout.as_posix()}/",
                cwd=repository,
                autocrlf=autocrlf,
            )

            raw = (checkout / "raw.yaml").read_bytes()
            source = (checkout / "encoded.py").read_text(encoding="ascii")
            encoded = source.split('b64("')[1].split('")')[0]
            return raw, b64(encoded)

    def test_the_encoded_fixture_still_carries_its_carriage_return(self):
        """Fails if the byte is gone. This is the assertion the whole convention
        is for, and it is made on the bytes that came back out of git rather
        than on the ones that went in."""
        for autocrlf in ("true", "false", "input"):
            with self.subTest(autocrlf=autocrlf):
                _, decoded = self.round_trip(autocrlf)
                self.assertIn(b"\r\n", decoded)
                self.assertEqual(decoded, b"budget: a\r\nvalue: 1\r\n")

    def test_the_same_document_checked_in_raw_loses_it(self):
        """Fails if a raw fixture would have been fine after all.

        Without this the convention is a rule nobody can see the reason for,
        and a rule whose reason cannot be seen is one somebody drops. It also
        pins the reason to this repository's .gitattributes: change that file
        so it stops normalising and this test is the one that says so.
        """
        for autocrlf in ("true", "false", "input"):
            with self.subTest(autocrlf=autocrlf):
                raw, _ = self.round_trip(autocrlf)
                self.assertNotIn(b"\r", raw)
                self.assertEqual(raw, b"budget: a\nvalue: 1\n")


class TestEveryTrackedFileIsCovered(unittest.TestCase):
    def test_git_reports_a_fixed_line_ending_for_every_tracked_path(self):
        """Fails if any tracked file's treatment is left to the platform.

        The set of paths comes from git rather than from a list here, so a file
        type this repository has not held yet is covered on the day it arrives
        instead of on the day somebody remembers to add it.
        """
        listed = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
        paths = [p for p in listed.stdout.decode("utf-8").split("\0") if p]
        self.assertGreater(len(paths), 0)

        attributes = subprocess.run(
            ["git", "check-attr", "--stdin", "-z", "text", "eol"],
            cwd=ROOT,
            input="\0".join(paths).encode("utf-8"),
            capture_output=True,
            check=True,
        )
        # -z gives path, attribute, value repeated with no line endings, which
        # is the only form that survives a path containing one.
        fields = attributes.stdout.decode("utf-8").split("\0")
        reported = {}
        for index in range(0, len(fields) - 2, 3):
            reported.setdefault(fields[index], {})[fields[index + 1]] = fields[index + 2]

        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(reported[path].get("eol"), "lf")
                self.assertIn(reported[path].get("text"), ("auto", "set"))


if __name__ == "__main__":
    unittest.main()
