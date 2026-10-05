"""Emit an escaped JSON summary without rendering untrusted report strings."""
import argparse
import json
import sys
from .report import analyze_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report')
    args = parser.parse_args()
    try:
        result = analyze_report(args.report)
    except (ValueError, OSError) as exc:
        print(f'Report rejected: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
