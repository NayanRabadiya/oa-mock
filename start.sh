#!/usr/bin/env bash
# Start the OA mock. Stop it with Ctrl+C (Ctrl+Z only pauses it and keeps the port busy).
cd "$(dirname "$0")"
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && exec "$c" run.py "$@"; done
echo "Python 3 not found. Run ./setup.sh first."; exit 1
