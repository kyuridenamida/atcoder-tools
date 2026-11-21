import os
import socket
import unittest

# Tests must not depend on atcoder.jp or PyPI being reachable, so the network is disabled by default.
# The tests which need the real network are marked with @requires_network and run only with
# ATCODERTOOLS_TEST_NETWORK=1.
NETWORK_ENABLED = os.environ.get("ATCODERTOOLS_TEST_NETWORK") == "1"
requires_network = unittest.skipUnless(
    NETWORK_ENABLED, "set ATCODERTOOLS_TEST_NETWORK=1 to run")

# The tests which compile programs in every supported language need all of the compilers (see
# .github/workflows/tests.yml), so they run only with ATCODERTOOLS_TEST_COMPILERS=1.
requires_compilers = unittest.skipUnless(
    os.environ.get("ATCODERTOOLS_TEST_COMPILERS") == "1", "set ATCODERTOOLS_TEST_COMPILERS=1 to run")

if not NETWORK_ENABLED:
    def _refuse_network(*args, **kwargs):
        raise OSError(
            "The network is disabled in tests. Mock it, or mark the test with @tests.requires_network.")

    socket.socket.connect = _refuse_network
    socket.getaddrinfo = _refuse_network
