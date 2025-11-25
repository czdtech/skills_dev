import argparse
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_pm2(action: str) -> bool:
    if action in {"start", "stop", "restart", "delete"}:
        cmd = ["npx", "pm2", action, "ecosystem.config.js"]
    elif action == "status":
        cmd = ["npx", "pm2", "status", "codex-bridge"]
    else:
        print(f"Unsupported action: {action}", file=sys.stderr)
        return False

    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"pm2 command failed: {exc.stderr}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Manage codex bridge via pm2")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"], help="Action to perform")
    args = parser.parse_args()
    success = run_pm2(args.action)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
