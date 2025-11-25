import argparse
import json
import os
import sys
import urllib.request
import urllib.error

def main():
    parser = argparse.ArgumentParser(description="Codex Advisor Wrapper")
    parser.add_argument("problem", help="The technical problem to analyze")
    parser.add_argument("--context", help="Background context")
    parser.add_argument("--focus-areas", help="Comma-separated focus areas")
    args = parser.parse_args()

    payload = {
        "problem": args.problem,
        "context": args.context or "",
        "focus_areas": args.focus_areas.split(",") if args.focus_areas else []
    }

    url = os.getenv("CODEX_BRIDGE_URL", "http://localhost:3001/analyze")
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
        print(f"Error calling Codex Bridge: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
