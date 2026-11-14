"""Run the complete offline verification suite for r20942097-hue/ad (legacy s).

Usage: python scripts/verify.py [--list] [--check PATTERN]
No network access or third-party packages are required.
"""
from __future__ import annotations

import argparse
import os
os.environ.pop('BASH_ENV', None)
os.environ['REMY_SHELL_EXPLICIT_CWD'] = '1'
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Filter regression tests", ("-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v")),
    ("Filter list validation", ("scripts/validate_lists.py",)),
    ("Generated list parity", ("scripts/generate_lists.py", "--check")),
    ("Subscription contract", ("scripts/check_subscription_contract.py", "--json")),
)


def run_check(command: tuple[str, ...]) -> bool:
    """Execute one verification command from repository root."""
    completed = subprocess.run([sys.executable, *command], cwd=ROOT, check=False)
    return completed.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list registered offline checks without running them")
    parser.add_argument("--check", action="append", metavar="PATTERN", help="run only checks whose name contains PATTERN (case-insensitive)")
    args = parser.parse_args(argv)

    selected = CHECKS
    if args.check:
        patterns = [p.casefold() for p in args.check]
        selected = tuple(item for item in CHECKS if any(p in item[0].casefold() for p in patterns))
        if not selected:
            print(f"No offline checks matched --check: {', '.join(args.check)}", file=sys.stderr)
            return 2

    if args.list:
        for index, (name, command) in enumerate(selected, 1):
            print(f"{index:2d}. {name}: python {' '.join(command)}")
        return 0

    if Path(ROOT).is_symlink():
        print("Could not run checks: repository root must not be a symlink", file=sys.stderr)
        return 1

    results: list[tuple[str, bool]] = []
    for name, command in selected:
        print(f"\n==> {name}", flush=True)
        try:
            passed = run_check(command)
        except OSError as exc:
            print(f"Could not start check: {exc}", file=sys.stderr)
            passed = False
        results.append((name, passed))

    print("\n==> Offline verification summary")
    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    passed_count = sum(passed for _, passed in results)
    print(f"{passed_count}/{len(results)} checks passed")
    return 0 if passed_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
