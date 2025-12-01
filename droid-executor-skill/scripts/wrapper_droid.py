#!/usr/bin/env python3
"""Simple wrapper to call Droid Executor with auto-managed bridge."""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import subprocess
import time
import socket
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DEFAULT_PORT = 53002
BRIDGE_PORT = int(os.getenv("DROID_BRIDGE_PORT", str(DEFAULT_PORT)))
BRIDGE_URL = os.getenv("DROID_BRIDGE_URL", f"http://localhost:{BRIDGE_PORT}")
PM2_APP = os.getenv("DROID_BRIDGE_PM2_APP", "droid-bridge-skill")


def is_port_open(port, timeout=1):
    """Check if port is open (bridge is running)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False


def ensure_bridge():
    """Start bridge if not running. Return started_by_me flag."""
    if is_port_open(BRIDGE_PORT):
        return False

    print("Starting Droid Bridge...", file=sys.stderr)
    subprocess.run(
        ["npx", "pm2", "start", "ecosystem.config.cjs"],
        cwd=ROOT_DIR,
        capture_output=True
    )

    for _ in range(30):
        if is_port_open(BRIDGE_PORT):
            print("Bridge ready.", file=sys.stderr)
            return True
        time.sleep(1)

    print("Warning: Bridge may not be ready.", file=sys.stderr)
    return True


def stop_bridge():
    subprocess.run(
        ["npx", "pm2", "stop", PM2_APP],
        cwd=ROOT_DIR,
        capture_output=True
    )


def main():
    parser = argparse.ArgumentParser(description="Droid Executor")
    parser.add_argument("objective", help="The objective of the task")
    parser.add_argument("--instructions", default="", help="Detailed instructions")
    parser.add_argument("--context", default="{}", help="Context as JSON string")
    args = parser.parse_args()

    started_by_me = ensure_bridge()

    # Parse context JSON
    try:
        context = json.loads(args.context)
    except json.JSONDecodeError:
        context = {}

    payload = {
        "objective": args.objective,
        "instructions": args.instructions,
        "context": context
    }

    req = urllib.request.Request(
        f"{BRIDGE_URL}/execute",
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=650) as response:
            result = json.loads(response.read().decode())
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except urllib.error.URLError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if started_by_me:
            stop_bridge()


if __name__ == "__main__":
    main()
