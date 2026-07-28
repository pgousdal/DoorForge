#!/usr/bin/env python3
"""Host-only M0 reference door.

This does not communicate with ABBS. It demonstrates the BBS-neutral session
shape that later adapters must populate.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from doorforge import Session


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="Test User")
    parser.add_argument("--user-id", type=int, default=None)
    parser.add_argument("--node", type=int, default=0)
    parser.add_argument("--security", type=int, default=None)
    parser.add_argument("--sysop", action="store_true")
    parser.add_argument("--minutes", type=int, default=30)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    session = Session(
        node_number=args.node,
        display_name=args.user,
        is_local=args.local,
        minutes_remaining=args.minutes,
        is_sysop=args.sysop,
        user_id=args.user_id,
        security_level=args.security,
    )
    session.validate()

    print("DoorForge Hello Door")
    print(f"Welcome, {session.display_name}!")
    print(f"Node: {session.node_number}")
    if session.security_level is not None:
        print(f"Security: {session.security_level}")
    if session.user_id is not None:
        print(f"User ID: {session.user_id}")
    print(f"Sysop: {session.is_sysop}")
    print(f"Minutes remaining: {session.minutes_remaining}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
