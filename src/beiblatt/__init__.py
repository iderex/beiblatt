"""beiblatt: a format for published systematic uncertainty budgets.

This package is the container. It holds no schema, no validator and no
arithmetic; those arrive with the later milestones, and the decisions they are
built on are recorded under docs/decisions/.

The version here is the software version and is deliberately not the schema
version. A document carries the version of the schema it is written against,
which is decided in docs/decisions/0010-schema-version-is-in-the-document.md,
and the two are versioned separately.
"""

__all__ = ["__version__"]

__version__ = "0.0.0"
