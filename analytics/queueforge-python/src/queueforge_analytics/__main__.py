import argparse
from queueforge_analytics.health import build_health_status
def main() -> int:
    parser = argparse.ArgumentParser(prog="queueforge-analytics")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    args = parser.parse_args()
    if args.command == "health":
        print(build_health_status().to_json())
        return 0
    return 64
if __name__ == "__main__":
    raise SystemExit(main())
