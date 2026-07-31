"""Validate and run eval/golden-set.csv through the tutor pipeline."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.agents.tutor_agent import TutorAgent, build_tutor_agent
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, LearningContext


DEFAULT_GOLDEN_SET = REPO_DIR / "eval" / "golden-set.csv"
DEFAULT_OUTPUT = REPO_DIR / "eval" / "run-01.csv"
DEFAULT_SUMMARY = REPO_DIR / "eval" / "run-01-summary.md"

GOLDEN_COLUMNS = [
    "case_id",
    "case_group",
    "risk_class",
    "origin",
    "source_ref",
    "input_turns_json",
    "expected_status",
    "expected_scope",
    "required_lecture_ids",
    "required_pages",
    "expected_behavior",
    "prohibited_behavior",
    "hard_rule",
    "dimensions",
]

RUN_COLUMNS = [
    "run_id",
    "run_at",
    "model",
    "commit_sha",
    "case_id",
    "response_status",
    "response_scope",
    "answer",
    "citation_source_ids",
    "citation_pages",
    "latency_ms",
    "context_chars",
    "groundedness",
    "citation_correctness",
    "scope_coverage",
    "continuity",
    "graceful_failure",
    "context_efficiency",
    "judge_1",
    "judge_2",
    "adjudicated_result",
    "overall_pass",
    "failure_code",
    "notes",
]

DIMENSIONS = {
    "groundedness",
    "citation_correctness",
    "scope_coverage",
    "continuity",
    "graceful_failure",
    "context_efficiency",
}
CASE_GROUPS = {"normal", "risk", "rare", "regression"}
RISK_CLASSES = {"normal", "source_truth", "ambiguity", "authority", "domain"}
ORIGINS = {"chatlog", "synthetic", "self_use", "regression"}
STATUSES = {
    "answered",
    "needs_clarification",
    "not_grounded",
    "not_configured",
    "out_of_scope",
}
SCOPES = {
    "current_page",
    "current_lecture",
    "selected_lectures",
    "all_lectures",
    "small_talk",
    "prompt_injection",
}
FAILURE_CODES = {
    "UNSUPPORTED_CLAIM",
    "INVALID_CITATION",
    "WRONG_SCOPE",
    "MISSED_CLARIFICATION",
    "AUTHORITY_BREACH",
    "OVER_REFUSAL",
    "CONTEXT_LOSS",
    "BUDGET_EXCEEDED",
    "EXECUTION_ERROR",
}


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    case_group: str
    risk_class: str
    origin: str
    source_ref: str
    turns: list[dict[str, Any]]
    expected_status: str
    expected_scope: str
    required_lecture_ids: tuple[str, ...]
    required_pages: tuple[int, ...]
    expected_behavior: str
    prohibited_behavior: str
    hard_rule: str
    dimensions: tuple[str, ...]


def _split_pipe(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split("|") if part.strip())


def load_cases(path: Path) -> tuple[list[EvalCase], list[str]]:
    errors: list[str] = []
    cases: list[EvalCase] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        actual_columns = reader.fieldnames or []
        if actual_columns != GOLDEN_COLUMNS:
            errors.append(
                "Golden-set columns do not match the required schema. "
                f"Expected {GOLDEN_COLUMNS}; got {actual_columns}."
            )
        for row_number, row in enumerate(reader, start=2):
            try:
                turns = json.loads(row.get("input_turns_json", ""))
                if not isinstance(turns, list):
                    raise ValueError("input_turns_json must be a JSON array")
                required_pages = tuple(
                    int(page) for page in _split_pipe(row.get("required_pages", ""))
                )
                cases.append(
                    EvalCase(
                        case_id=row.get("case_id", "").strip(),
                        case_group=row.get("case_group", "").strip(),
                        risk_class=row.get("risk_class", "").strip(),
                        origin=row.get("origin", "").strip(),
                        source_ref=row.get("source_ref", "").strip(),
                        turns=turns,
                        expected_status=row.get("expected_status", "").strip(),
                        expected_scope=row.get("expected_scope", "").strip(),
                        required_lecture_ids=_split_pipe(
                            row.get("required_lecture_ids", "")
                        ),
                        required_pages=required_pages,
                        expected_behavior=row.get("expected_behavior", "").strip(),
                        prohibited_behavior=row.get(
                            "prohibited_behavior", ""
                        ).strip(),
                        hard_rule=row.get("hard_rule", "").strip(),
                        dimensions=_split_pipe(row.get("dimensions", "")),
                    )
                )
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                errors.append(f"Row {row_number}: {exc}")
    return cases, errors


def validate_cases(cases: list[EvalCase]) -> list[str]:
    errors: list[str] = []
    if len(cases) != 24:
        errors.append(f"Expected 24 cases; found {len(cases)}.")

    expected_ids = {f"GS-{number:03d}" for number in range(1, 25)}
    case_ids = [case.case_id for case in cases]
    if len(case_ids) != len(set(case_ids)):
        errors.append("case_id values must be unique.")
    missing_ids = expected_ids - set(case_ids)
    extra_ids = set(case_ids) - expected_ids
    if missing_ids or extra_ids:
        errors.append(
            f"case_id range must be GS-001..GS-024; "
            f"missing={sorted(missing_ids)}, extra={sorted(extra_ids)}."
        )

    group_counts = Counter(case.case_group for case in cases)
    expected_groups = {"normal": 10, "risk": 8, "rare": 4, "regression": 2}
    if dict(group_counts) != expected_groups:
        errors.append(
            f"Case-group distribution must be {expected_groups}; "
            f"found {dict(group_counts)}."
        )

    risk_counts = Counter(
        case.risk_class for case in cases if case.case_group == "risk"
    )
    expected_risks = {
        "source_truth": 2,
        "ambiguity": 2,
        "authority": 2,
        "domain": 2,
    }
    if dict(risk_counts) != expected_risks:
        errors.append(
            f"Risk distribution must be {expected_risks}; "
            f"found {dict(risk_counts)}."
        )

    chatlog_count = sum(case.origin == "chatlog" for case in cases)
    if chatlog_count < 10:
        errors.append(f"At least 10 chatlog-derived cases are required; found {chatlog_count}.")

    for case in cases:
        prefix = case.case_id or "<missing case_id>"
        if case.case_group not in CASE_GROUPS:
            errors.append(f"{prefix}: invalid case_group={case.case_group!r}.")
        if case.risk_class not in RISK_CLASSES:
            errors.append(f"{prefix}: invalid risk_class={case.risk_class!r}.")
        if case.origin not in ORIGINS:
            errors.append(f"{prefix}: invalid origin={case.origin!r}.")
        if case.expected_status not in STATUSES:
            errors.append(
                f"{prefix}: invalid expected_status={case.expected_status!r}."
            )
        if case.expected_scope not in SCOPES:
            errors.append(f"{prefix}: invalid expected_scope={case.expected_scope!r}.")
        unknown_dimensions = set(case.dimensions) - DIMENSIONS
        if unknown_dimensions or not case.dimensions:
            errors.append(
                f"{prefix}: dimensions must be non-empty and known; "
                f"unknown={sorted(unknown_dimensions)}."
            )
        if not case.turns:
            errors.append(f"{prefix}: input_turns_json must contain at least one turn.")
        for turn_index, turn in enumerate(case.turns, start=1):
            if not isinstance(turn, dict) or not str(turn.get("message", "")).strip():
                errors.append(f"{prefix}: turn {turn_index} must contain a message.")
            context = turn.get("context", {})
            if context is not None and not isinstance(context, dict):
                errors.append(f"{prefix}: turn {turn_index} context must be an object.")
        if not case.expected_behavior:
            errors.append(f"{prefix}: expected_behavior is required.")
        if not case.prohibited_behavior:
            errors.append(f"{prefix}: prohibited_behavior is required.")
        serialized = json.dumps(case.__dict__, ensure_ascii=False, default=list)
        if "TBD" in serialized.upper():
            errors.append(f"{prefix}: TBD is not allowed in the committed golden set.")
        if case.origin == "chatlog" and not re.fullmatch(
            r"C\d{4}:T\d{4}", case.source_ref
        ):
            errors.append(
                f"{prefix}: chatlog source_ref must look like C0001:T0001."
            )
    return errors


def _git_commit_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        revision = result.stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        return f"{revision}-dirty" if dirty.stdout.strip() else revision
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _score_scope(
    response: ChatResponse,
    case: EvalCase,
) -> str:
    if response.scope != case.expected_scope:
        return "FAIL"
    if case.required_lecture_ids:
        cited_lectures = {citation.lecture_id for citation in response.citations}
        if not set(case.required_lecture_ids).issubset(cited_lectures):
            return "FAIL"
    return "PASS"


def _score_citations(response: ChatResponse, case: EvalCase) -> str:
    if response.status != "answered":
        return "N/A"
    if not response.citations:
        return "FAIL"
    cited_lectures = {citation.lecture_id for citation in response.citations}
    if case.required_lecture_ids and not set(case.required_lecture_ids).issubset(
        cited_lectures
    ):
        return "FAIL"
    cited_pages = {citation.page for citation in response.citations if citation.page}
    if case.required_pages and not set(case.required_pages).issubset(cited_pages):
        return "FAIL"
    return "PASS"


def _initial_dimension_scores(
    case: EvalCase,
    response: ChatResponse | None,
    *,
    execution_error: bool,
    context_chars: int,
    context_budget: int,
) -> dict[str, str]:
    scores = {dimension: "N/A" for dimension in DIMENSIONS}
    if execution_error or response is None:
        for dimension in case.dimensions:
            scores[dimension] = "FAIL"
        return scores

    if "scope_coverage" in case.dimensions:
        scores["scope_coverage"] = _score_scope(response, case)
    if "citation_correctness" in case.dimensions:
        scores["citation_correctness"] = _score_citations(response, case)
    if "groundedness" in case.dimensions:
        if response.status != "answered":
            scores["groundedness"] = (
                "PASS"
                if response.status == case.expected_status and not response.citations
                else "FAIL"
            )
        else:
            # Semantic claim-to-source support requires human review.
            scores["groundedness"] = "N/A"
    if "graceful_failure" in case.dimensions:
        scores["graceful_failure"] = (
            "PASS"
            if response.status == case.expected_status
            and response.status != "answered"
            and not response.citations
            else "FAIL"
        )
    if "continuity" in case.dimensions:
        # A human must confirm that the correction and learning goal survived.
        scores["continuity"] = "N/A"
    if "context_efficiency" in case.dimensions:
        scores["context_efficiency"] = (
            "PASS" if context_chars <= context_budget else "FAIL"
        )
    return scores


def _failure_code(
    case: EvalCase,
    response: ChatResponse | None,
    scores: dict[str, str],
    *,
    execution_error: bool,
) -> str:
    if execution_error or response is None:
        return "EXECUTION_ERROR"
    if response.status != case.expected_status:
        if case.expected_status == "needs_clarification":
            return "MISSED_CLARIFICATION"
        if case.risk_class == "authority":
            return "AUTHORITY_BREACH"
        if response.status == "out_of_scope" and case.expected_status == "answered":
            return "OVER_REFUSAL"
    if scores["scope_coverage"] == "FAIL":
        return "WRONG_SCOPE"
    if scores["citation_correctness"] == "FAIL":
        return "INVALID_CITATION"
    if scores["context_efficiency"] == "FAIL":
        return "BUDGET_EXCEEDED"
    if scores["groundedness"] == "FAIL":
        return "UNSUPPORTED_CLAIM"
    if scores["continuity"] == "FAIL":
        return "CONTEXT_LOSS"
    return ""


def evaluate_case(
    case: EvalCase,
    agent: TutorAgent,
    *,
    run_id: str,
    run_at: str,
    model: str,
    commit_sha: str,
) -> dict[str, str]:
    started = time.perf_counter()
    response: ChatResponse | None = None
    execution_error = False
    error_note = ""
    max_context_chars = 0
    context_budget = agent.context_character_budget

    try:
        for turn in case.turns:
            context = LearningContext(**(turn.get("context") or {}))
            request = ChatRequest(
                message=str(turn["message"]),
                conversation_id=str(
                    turn.get("conversation_id") or f"{run_id}:{case.case_id}"
                ),
                context=context,
            )
            response = agent.run(request)
            max_context_chars = max(
                max_context_chars,
                agent.last_trace.context_chars,
            )
        if response is not None and response.status == "not_configured":
            execution_error = True
            error_note = "Pipeline is not configured: index and/or real LLM unavailable."
    except Exception as exc:  # Keep the full run auditable even when one case crashes.
        execution_error = True
        error_note = f"{type(exc).__name__}: {exc}"

    latency_ms = round((time.perf_counter() - started) * 1000)
    scores = _initial_dimension_scores(
        case,
        response,
        execution_error=execution_error,
        context_chars=max_context_chars,
        context_budget=context_budget,
    )
    applicable_scores = [scores[dimension] for dimension in case.dimensions]
    overall_pass = bool(applicable_scores) and all(
        score == "PASS" for score in applicable_scores
    )
    failure_code = _failure_code(
        case,
        response,
        scores,
        execution_error=execution_error,
    )
    if failure_code and failure_code not in FAILURE_CODES:
        raise ValueError(f"Unexpected failure code: {failure_code}")

    citations = response.citations if response else []
    notes = [f"context_budget={context_budget}"]
    if error_note:
        notes.append(error_note)
    pending = [
        dimension
        for dimension in case.dimensions
        if scores[dimension] == "N/A"
    ]
    if pending and not execution_error:
        notes.append(f"pending_human_review={'|'.join(pending)}")

    return {
        "run_id": run_id,
        "run_at": run_at,
        "model": model,
        "commit_sha": commit_sha,
        "case_id": case.case_id,
        "response_status": response.status if response else "EXECUTION_ERROR",
        "response_scope": response.scope if response else "",
        "answer": response.answer if response else "",
        "citation_source_ids": "|".join(citation.source_id for citation in citations),
        "citation_pages": "|".join(
            str(citation.page) for citation in citations if citation.page is not None
        ),
        "latency_ms": str(latency_ms),
        "context_chars": str(max_context_chars),
        **scores,
        "judge_1": "N/A",
        "judge_2": "N/A",
        "adjudicated_result": "N/A",
        "overall_pass": "PASS" if overall_pass else "FAIL",
        "failure_code": failure_code,
        "notes": "; ".join(notes),
    }


def run_cases(
    cases: list[EvalCase],
    agent: TutorAgent,
    *,
    run_id: str,
    run_at: str | None = None,
    model: str | None = None,
    commit_sha: str | None = None,
) -> list[dict[str, str]]:
    timestamp = run_at or datetime.now(timezone.utc).isoformat()
    model_name = model or f"{settings.llm_provider}:{settings.openai_model}"
    revision = commit_sha or _git_commit_sha()
    return [
        evaluate_case(
            case,
            agent,
            run_id=run_id,
            run_at=timestamp,
            model=model_name,
            commit_sha=revision,
        )
        for case in cases
    ]


def write_results(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _dimension_counts(
    cases_by_id: dict[str, EvalCase],
    rows: list[dict[str, str]],
    dimension: str,
) -> Counter[str]:
    return Counter(
        row[dimension]
        for row in rows
        if dimension in cases_by_id[row["case_id"]].dimensions
    )


def _hard_violation_count(
    cases_by_id: dict[str, EvalCase],
    rows: list[dict[str, str]],
) -> int:
    count = 0
    for row in rows:
        if row["failure_code"] == "EXECUTION_ERROR":
            continue
        rule = cases_by_id[row["case_id"]].hard_rule
        if rule == "ZERO_UNSUPPORTED_CLAIMS" and row["groundedness"] == "FAIL":
            count += 1
        elif rule == "NO_INVALID_CITATION" and row["citation_correctness"] == "FAIL":
            count += 1
        elif rule == "NO_AUTHORITY_BREACH" and row["graceful_failure"] == "FAIL":
            count += 1
        elif rule == "STAY_WITHIN_CONTEXT_BUDGET" and row["context_efficiency"] == "FAIL":
            count += 1
    return count


def build_summary(cases: list[EvalCase], rows: list[dict[str, str]]) -> str:
    cases_by_id = {case.case_id: case for case in cases}
    total = len(rows)
    passed = sum(row["overall_pass"] == "PASS" for row in rows)
    pass_rate = (passed / total * 100) if total else 0.0
    hard_violations = _hard_violation_count(cases_by_id, rows)
    regression_rows = [
        row for row in rows if cases_by_id[row["case_id"]].case_group == "regression"
    ]
    regression_budget_ok = bool(regression_rows) and all(
        row["context_efficiency"] == "PASS" for row in regression_rows
    )
    required_passes = math.ceil(total * 0.80)
    meets_bar = (
        passed >= required_passes
        and hard_violations == 0
        and regression_budget_ok
    )

    group_lines: list[str] = []
    for group in ("normal", "risk", "rare", "regression"):
        group_rows = [
            row for row in rows if cases_by_id[row["case_id"]].case_group == group
        ]
        group_passes = sum(row["overall_pass"] == "PASS" for row in group_rows)
        group_lines.append(f"| {group} | {group_passes}/{len(group_rows)} |")

    dimension_lines: list[str] = []
    for dimension in sorted(DIMENSIONS):
        counts = _dimension_counts(cases_by_id, rows, dimension)
        dimension_lines.append(
            f"| {dimension} | {counts['PASS']} | {counts['FAIL']} | {counts['N/A']} |"
        )

    failures = Counter(
        row["failure_code"] for row in rows if row["failure_code"]
    )
    top_failures = failures.most_common(3)
    failure_lines = (
        "\n".join(f"- `{code}`: {count} case" for code, count in top_failures)
        if top_failures
        else "- Không có failure code."
    )
    worst_failure = top_failures[0][0] if top_failures else "Không có"
    run_id = rows[0]["run_id"] if rows else "unknown"
    run_at = rows[0]["run_at"] if rows else "unknown"
    model = rows[0]["model"] if rows else "unknown"
    commit_sha = rows[0]["commit_sha"] if rows else "unknown"

    return f"""# {run_id} — Golden-set evaluation

## Metadata

- Thời điểm: `{run_at}`
- Model/provider: `{model}`
- Commit: `{commit_sha}`
- Bộ test: `{total}` case
- Human review: các ô `N/A` ở chiều áp dụng vẫn được coi là chưa đạt cho tới khi adjudicate.

## Kết luận quality bar

- Tổng pass: **{passed}/{total} ({pass_rate:.1f}%)**
- Ngưỡng tổng: **≥80%**, tương đương ít nhất **{required_passes}/{total}**
- Hard-rule violations đã quan sát: **{hard_violations}**
- Regression trong context budget: **{'PASS' if regression_budget_ok else 'FAIL'}**
- Kết luận: **{'ĐẠT' if meets_bar else 'CHƯA ĐẠT'}**

Quality bar được giữ nguyên; kết quả thấp hoặc execution error không làm thay đổi chuẩn.

## Theo nhóm case

| Nhóm | Pass |
|---|---:|
{chr(10).join(group_lines)}

## Theo chiều chất lượng

| Chiều | PASS | FAIL | N/A |
|---|---:|---:|---:|
{chr(10).join(dimension_lines)}

## Failure nổi bật

{failure_lines}

Failure nghiêm trọng nhất theo tần suất: **{worst_failure}**.

## Bước tiếp theo

1. Khắc phục execution/configuration error trước nếu có.
2. Hai người chấm độc lập năm case hiệu chuẩn theo `scoring-guide.md`.
3. Adjudicate các chiều ngữ nghĩa còn `N/A`, sau đó tính lại summary.
4. Chọn một failure nghiêm trọng để sửa; nếu sản phẩm thay đổi, chạy lại toàn bộ thành Run 02 và không ghi đè Run 01.
"""


def write_summary(
    path: Path,
    cases: list[EvalCase],
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_summary(cases, rows), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and run the VLearn 24-case golden set."
    )
    parser.add_argument("--golden-set", type=Path, default=DEFAULT_GOLDEN_SET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--run-id", default="run-01")
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases, load_errors = load_cases(args.golden_set)
    errors = [*load_errors, *validate_cases(cases)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

    print(
        "Golden set valid: "
        f"{len(cases)} cases, "
        f"{sum(case.origin == 'chatlog' for case in cases)} chatlog-derived."
    )
    if args.validate_only:
        return

    agent = build_tutor_agent()
    rows = run_cases(cases, agent, run_id=args.run_id)
    write_results(args.output, rows)
    write_summary(args.summary, cases, rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    print(f"Wrote summary to {args.summary}")


if __name__ == "__main__":
    main()
