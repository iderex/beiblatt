"""A test that reaches the network, by each of the routes the guard watches.

A test that opens a socket is not headless in any useful sense: it fails on a
machine with no route out, which is the same failure mode as a display
dependency and is why it belongs to the same guard.

The route is chosen by the argument, because one script that always takes the
first route would leave the other entries in the guard unreached, and a name in
a guard that no fixture can drive reads as one more thing being checked. Every
address here is loopback or the local machine's own name, so an attempt that
was not refused reaches nothing.
"""

import socket
import sys

from guarded import under_guard

under_guard()

route = sys.argv[1] if len(sys.argv) > 1 else "connect"

if route == "connect":
    # What somebody actually writes: a test that fetches something.
    try:
        socket.create_connection(("127.0.0.1", 9), timeout=1)
    except OSError:
        pass
elif route == "socket":
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).close()
elif route == "resolve":
    socket.getaddrinfo("localhost", 9)
elif route == "name":
    socket.gethostbyname("localhost")
else:
    raise SystemExit(f"no such route: {route}")

print(f"not refused: the network was reached by {route}")
