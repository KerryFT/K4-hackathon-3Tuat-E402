import unittest
from pathlib import Path
from types import SimpleNamespace

from app.schemas.chat import ChatResponse
from scripts.run_evaluation import (
    DEFAULT_GOLDEN_SET,
    EvalCase,
    load_cases,
    run_cases,
    validate_cases,
)


def make_case(
    case_id: str,
    messages: list[str],
    *,
    dimensions: tuple[str, ...] = ("context_efficiency",),
) -> EvalCase:
    return EvalCase(
        case_id=case_id,
        case_group="normal",
        risk_class="normal",
        origin="synthetic",
        source_ref="SYNTHETIC",
        turns=[
            {
                "message": message,
                "context": {"course_id": "comp2010-phase-1"},
            }
            for message in messages
        ],
        expected_status="answered",
        expected_scope="all_lectures",
        required_lecture_ids=(),
        required_pages=(),
        expected_behavior="Answer",
        prohibited_behavior="Crash",
        hard_rule="NONE",
        dimensions=dimensions,
    )


class FakeEvaluationAgent:
    context_character_budget = 100

    def __init__(self, failing_messages: set[str] | None = None) -> None:
        self.failing_messages = failing_messages or set()
        self.messages: list[str] = []
        self.last_trace = SimpleNamespace(context_chars=0)

    def run(self, request):
        self.messages.append(request.message)
        if request.message in self.failing_messages:
            raise RuntimeError("synthetic failure")
        self.last_trace = SimpleNamespace(context_chars=len(request.message))
        return ChatResponse(
            answer=f"Answer: {request.message}",
            status="answered",
            scope="all_lectures",
        )


class EvaluationRunnerTests(unittest.TestCase):
    def test_committed_golden_set_passes_structural_validation(self) -> None:
        cases, load_errors = load_cases(Path(DEFAULT_GOLDEN_SET))

        self.assertEqual(load_errors, [])
        self.assertEqual(validate_cases(cases), [])
        self.assertEqual(len(cases), 24)
        self.assertGreaterEqual(
            sum(case.origin == "chatlog" for case in cases),
            10,
        )

    def test_multi_turn_case_runs_every_turn_and_keeps_max_context(self) -> None:
        agent = FakeEvaluationAgent()
        case = make_case("GS-900", ["first", "a longer final turn"])

        rows = run_cases(
            [case],
            agent,
            run_id="test-run",
            run_at="2026-07-31T00:00:00+00:00",
            model="fake",
            commit_sha="test",
        )

        self.assertEqual(agent.messages, ["first", "a longer final turn"])
        self.assertEqual(rows[0]["context_chars"], str(len("a longer final turn")))
        self.assertEqual(rows[0]["overall_pass"], "PASS")

    def test_case_exception_is_recorded_and_later_case_still_runs(self) -> None:
        agent = FakeEvaluationAgent({"boom"})
        cases = [
            make_case("GS-901", ["boom"]),
            make_case("GS-902", ["works"]),
        ]

        rows = run_cases(
            cases,
            agent,
            run_id="test-run",
            run_at="2026-07-31T00:00:00+00:00",
            model="fake",
            commit_sha="test",
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["failure_code"], "EXECUTION_ERROR")
        self.assertEqual(rows[0]["overall_pass"], "FAIL")
        self.assertEqual(rows[1]["response_status"], "answered")


if __name__ == "__main__":
    unittest.main()
