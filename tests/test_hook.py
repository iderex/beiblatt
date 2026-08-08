"""The hook runs the gate and nothing else, and git will actually run it.

Two things go wrong with a hook and neither of them is the script being wrong.
The first is a second procedure growing inside it, a step somebody added here
and nowhere else, which then runs before a push and never anywhere again. The
second is a hook that is not executable, which on the platforms that check the
bit is a file git skips in silence: the push succeeds, the gate never ran, and
nothing said so.
"""

import subprocess
import unittest

from gate.run import ROOT

HOOK = ROOT / ".githooks" / "pre-push"


class TestTheHookRunsTheGateAndNothingElse(unittest.TestCase):
    def test_it_hands_over_to_the_gate(self):
        body = HOOK.read_text(encoding="utf-8")
        self.assertIn("-m gate", body)

    def test_it_starts_no_second_procedure(self):
        """Fails if the hook grows a step of its own.

        The gate is one verb precisely so that what runs before a push and what
        runs anywhere else cannot differ. A step added here would run in one
        place only, and the two would go on passing while they drifted.
        """
        body = HOOK.read_text(encoding="utf-8")
        code = [
            line.strip()
            for line in body.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        handovers = [line for line in code if line.startswith("exec ")]
        self.assertEqual(handovers, ["exec \"$candidate\" -m gate"])
        for line in code:
            with self.subTest(line=line):
                self.assertNotIn("-m unittest", line)
                self.assertNotIn("-m pip", line)


class TestGitWillRunIt(unittest.TestCase):
    def test_the_executable_bit_is_set_in_the_index(self):
        """Fails if the hook is committed without the bit.

        Windows does not carry the bit in the working tree, so it has to be set
        in the index deliberately, and it is the kind of thing a later edit
        loses. Where the bit is missing git skips the hook without a word,
        which is the worst shape this failure could take.
        """
        listed = subprocess.run(
            ["git", "ls-files", "-s", "--", ".githooks/pre-push"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertTrue(listed.stdout.strip(), "the hook is not tracked")
        self.assertEqual(listed.stdout.split()[0], "100755")

    def test_the_hooks_directory_holds_only_hooks_git_knows(self):
        """Fails if something that is not a hook is put in the directory a
        clone is told to point core.hooksPath at."""
        names = sorted(path.name for path in (ROOT / ".githooks").iterdir())
        self.assertEqual(names, ["pre-push"])


if __name__ == "__main__":
    unittest.main()
