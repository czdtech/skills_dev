import argparse
import json
import os
import sys
import urllib.request
import urllib.error

def main():
    parser = argparse.ArgumentParser(description="Droid Executor Wrapper")
    parser.add_argument("objective", help="The objective of the task")
    parser.add_argument("--instructions", help="Detailed instructions")
    args = parser.parse_args()

    payload = {
        "objective": args.objective,
        "instructions": args.instructions or "",
        "context": {}
    }

    url = os.getenv("DROID_BRIDGE_URL", "http://localhost:3002/execute")
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except urllib.error.URLError as e:
        print(f"Error calling Droid Bridge: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
