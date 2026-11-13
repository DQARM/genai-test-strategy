#!/usr/bin/env python3
"""Offline teaching fixture only; never a rule or verification of a user's product."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version="counter-demo 1.0")
    parser.add_argument("--count", type=int, required=True)
    parser.add_argument("--record", type=Path, required=True)
    args = parser.parse_args()
    if not 0 <= args.count <= 100:
        parser.error("This teaching fixture accepts integers from 0 to 100.")
    observed = {"demo": True, "fixture_version": "counter-demo 1.0", "count": args.count,
                "alarm": args.count >= 50, "observed_at": datetime.now(timezone.utc).isoformat()}
    content = json.dumps(observed, ensure_ascii=False, indent=2) + "\n"
    try:
        with args.record.open("x", encoding="utf-8") as stream:
            stream.write(content)
    except OSError as exc:
        parser.error(str(exc))
    print(content, end="")


if __name__ == "__main__":
    main()
