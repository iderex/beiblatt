"""The container itself, checked.

This is the only thing there is to check while the package holds nothing else.
It uses the standard library test runner rather than a third-party one, so that
running it costs no dependency beyond the ones the project already declares.
"""

import unittest
from importlib.metadata import PackageNotFoundError, version

import beiblatt


class TestThePackageIsInstalled(unittest.TestCase):
    def test_the_distribution_and_the_package_agree_on_the_version(self):
        """Fails when the source tree was imported without being installed.

        importlib.metadata reads the installed distribution rather than the
        directory on sys.path, so this is the difference between an environment
        the documented install produced and a checkout somebody ran from. That
        is exactly what the install step in the readme claims to produce, and a
        claim wants something that goes red when it stops being true.
        """
        try:
            installed = version("beiblatt")
        except PackageNotFoundError:  # pragma: no cover - the failure message
            self.fail(
                "beiblatt is not installed in this environment. Run the "
                "install documented in README.md before running the tests."
            )
        self.assertEqual(installed, beiblatt.__version__)


class TestTheDeclaredDependenciesAreThere(unittest.TestCase):
    def test_each_declared_dependency_imports(self):
        """Fails when the lock file installed something other than the set
        pyproject.toml declares. Importing is the cheapest thing that
        distinguishes a package that resolved from one that only appeared in a
        resolution report."""
        for name in ("yaml", "jsonschema", "numpy"):
            with self.subTest(dependency=name):
                __import__(name)


if __name__ == "__main__":
    unittest.main()
