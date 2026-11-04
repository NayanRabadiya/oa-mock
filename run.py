#!/usr/bin/env python3
"""Start the OA mock. Needs Python 3.8+ and nothing else.

    python3 run.py              # opens http://127.0.0.1:8765
    python3 run.py --port 9000 --no-browser
"""
import sys

if sys.version_info < (3, 8):
    sys.exit("OA Mock needs Python 3.8 or newer (this is %s)." % sys.version.split()[0])

from oa_mock.__main__ import main

main()
