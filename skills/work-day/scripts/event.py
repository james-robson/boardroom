#!/usr/bin/env python3
"""Append one Boardroom event to a day's events.jsonl.

Usage: event.py <events.jsonl> <type> [key=value ...]

Values that parse as JSON (numbers, lists, true/false) are stored as such;
anything else is stored as a string. Adds the current UTC time as "t".
"""
import json
import sys
from datetime import datetime, timezone

if len(sys.argv) < 3:
    sys.exit(__doc__)
path, typ, *pairs = sys.argv[1:]
event = {"t": datetime.now(timezone.utc).isoformat(timespec="seconds"), "type": typ}
for pair in pairs:
    key, sep, value = pair.partition("=")
    if not sep:
        sys.exit(f"not key=value: {pair!r}")
    try:
        event[key] = json.loads(value)
    except ValueError:
        event[key] = value
with open(path, "a") as f:
    f.write(json.dumps(event) + "\n")
