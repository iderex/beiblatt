"""`python -m gate`.

The whole of this file is turning the entry point's return value into an exit
code. Keeping the work in `gate.cli.main` is what lets the tests call it
directly and read what it printed.
"""

import sys

from gate.cli import main

sys.exit(main())
