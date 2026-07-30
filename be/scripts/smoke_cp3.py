"""Run one real grounded chat turn and save the CP3 smoke-test evidence."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.agents.tutor_agent import build_tutor_agent
from app.core.config import settings
from app.schemas.chat import ChatRequest, LearningContext


DEFAULT_OUTPUT = REPO_DIR / "artifacts" / "evaluation-runs" / "cp3-smoke.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call the configured real LLM once through the full CP3 pipeline."
    )
    parser.add_argument(
        "--question",
        default=(
            "Problem statement liên hệ thế nào với nền tảng AI và LLM "
            "giữa Day 1 và Day 2?"
        ),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if settings.llm_provider != "openai" or not settings.openai_api_key:
        raise SystemExit(
            "Configure LLM_PROVIDER=openai and OPENAI_API_KEY in be/.env first."
        )

    response = build_tutor_agent().run(
        ChatRequest(
            message=args.question,
            context=LearningContext(course_id="comp2010-phase-1"),
        )
    )
    evidence = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "model": settings.openai_model,
        "question": args.question,
        "response": response.model_dump(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    if response.status != "answered":
        raise SystemExit(f"CP3 smoke test did not pass: {response.status}")
    print(f"Saved CP3 evidence to {args.output}")


if __name__ == "__main__":
    main()
