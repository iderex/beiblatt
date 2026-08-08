"""A test file that imports a windowing toolkit at module scope.

This is the shape the failure actually arrives in: one import added to one test
file by somebody whose machine has a screen. It is refused at the import rather
than at the window, so nothing is ever drawn, and importing tkinter opens
nothing even where the refusal is missing.
"""

from guarded import under_guard

under_guard()

import tkinter  # noqa: E402,F401  the attempt is the point

print("not refused: a windowing toolkit was imported")
