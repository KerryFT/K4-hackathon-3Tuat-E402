"""Validate the committed golden set without running the tutor."""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.run_evaluation import DEFAULT_GOLDEN_SET, load_cases, validate_cases


def main(path: Path = DEFAULT_GOLDEN_SET) -> None:
    cases, load_errors = load_cases(path)
    errors = [*load_errors, *validate_cases(cases)]
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print(
        f"PASS: {len(cases)} cases; "
        f"{sum(case.origin == 'chatlog' for case in cases)} chatlog-derived."
    )


if __name__ == "__main__":
    main()
