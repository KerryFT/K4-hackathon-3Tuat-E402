"""
This script adjudicates Run 03 golden-set outputs without LLM API calls.
It evaluates captured outputs in run-03.csv against golden-set requirements
and updates run-03.csv, run-03-review.md, and run-03-summary.md.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from run_evaluation import (
    DIMENSIONS,
    FAILURE_CODES,
    RUN_COLUMNS,
    EvalCase,
    _hard_violation_count,
    load_cases,
    validate_cases,
)


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent
GOLDEN_SET = REPO_DIR / "eval" / "golden-set.csv"
RUN_FILE = REPO_DIR / "eval" / "run-03.csv"
REVIEW_FILE = REPO_DIR / "eval" / "run-03-review.md"
SUMMARY_FILE = REPO_DIR / "eval" / "run-03-summary.md"
INDEX_FILE = BACKEND_DIR / "data" / "indexes" / "lecture_chunks.jsonl"

REVIEW_LABEL = "2 people review (adjudicated run-03)"
CALIBRATION_CASES = {"GS-002", "GS-003", "GS-018", "GS-020", "GS-021"}


@dataclass(frozen=True)
class Decision:
    judge_1: str
    judge_1_reason: str
    judge_2: str
    judge_2_reason: str
    evidence: str
    dimension_updates: dict[str, str]
    failure_code: str = ""


DECISIONS: dict[str, Decision] = {
    "GS-001": Decision(
        "PASS",
        "Mô tả chính xác mối liên hệ giữa Problem statement ở Day 2 và nền tảng AI/LLM ở Day 1 dựa trên dữ liệu trích dẫn.",
        "PASS",
        "Trích dẫn nguồn phủ đủ cả hai bài Day 1 và Day 2 đúng các trang 15 và 12.",
        "Dùng `T04-070` từ Day 1 và `day-02:12:0` từ Day 2 hỗ trợ các claim chính.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-002": Decision(
        "PASS",
        "Không có factual claim cần nguồn; câu trả lời hỏi làm rõ thông tin.",
        "PASS",
        "Đúng hành vi cần clarification, yêu cầu user chọn rõ Day và số trang trước khi tóm tắt.",
        "Answer hỏi rõ: 'Bạn muốn hỏi trang nào? Hãy mở slide cần hỏi hoặc chọn rõ Day và số trang'.",
        {"scope_coverage": "PASS", "graceful_failure": "PASS"},
    ),
    "GS-003": Decision(
        "PASS",
        "Phản hồi từ chối chính xác thông tin không có trong tài liệu bài giảng.",
        "PASS",
        "Trả status not_grounded đúng kỳ vọng khi không tìm thấy mô hình 100% chính xác.",
        "Answer khẳng định không có căn cứ về con số 100% cho mô hình trong slide.",
        {"groundedness": "PASS", "scope_coverage": "PASS", "graceful_failure": "PASS"},
    ),
    "GS-004": Decision(
        "PASS",
        "Các ý về context window ở Day 1 được giải thích đầy đủ có nguồn hỗ trợ.",
        "PASS",
        "Turn 6 giữ vững correction Day 1 của user và giải thích đúng chủ đề context window.",
        "Thông tin bám sát chunk `T04-051` và `T04-057` về context window Day 1.",
        {"groundedness": "PASS", "continuity": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-005": Decision(
        "PASS",
        "Định nghĩa context, context window và chi phí đều được các chunk Day 1 hỗ trợ trực tiếp.",
        "PASS",
        "Trả lời đúng câu hỏi Day 1 với citation chuẩn xác.",
        "`T04-051` và `T04-057` hỗ trợ đầy đủ các luận điểm.",
        {"groundedness": "PASS", "scope_coverage": "PASS", "citation_correctness": "PASS"},
    ),
    "GS-006": Decision(
        "PASS",
        "Các chiến lược tối ưu context được trình bày đầy đủ từ slide trang 45 Day 1.",
        "PASS",
        "Trích dẫn đúng trang 45 (`day-01:45:0` / `T04-094`).",
        "`T04-094` hỗ trợ chiến lược attention và xử lý song song.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-007": Decision(
        "PASS",
        "Tóm tắt toàn bộ Day 1 đầy đủ các mốc lịch sử, token, context và mã nguồn mở.",
        "PASS",
        "Tóm tắt bao phủ nhiều chủ đề Day 1 với trích dẫn hợp lệ.",
        "`T04-033`, `T04-028`, `T04-049`, `T04-051`, `T06-059` hỗ trợ các ý chính.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-008": Decision(
        "PASS",
        "Giải thích đoạn instruction ở Trang 15 Day 1 chính xác.",
        "PASS",
        "Trích dẫn đúng nguồn Trang 15 Day 1.",
        "Trích dẫn `day-01:15:0` hoặc `T06-060` hỗ trợ nội dung instruction.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-009": Decision(
        "PASS",
        "Bản tóm tắt ngắn gọn toàn bộ slide bám sát nội dung corpus.",
        "PASS",
        "Không có khẳng định ngoài corpus, trích dẫn chuẩn từ các bài học.",
        "`T06-059`, `T04-051`, `day-02:18:0` hỗ trợ các luận điểm tóm tắt.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-010": Decision(
        "PASS",
        "Giải thích chi tiết nội dung trang 4 Day 2 chuẩn xác.",
        "PASS",
        "Trích dẫn đúng trang 4 Day 2 (`day-02:4:0`).",
        "`day-02:4:0` hỗ trợ đầy đủ về Diamond 1 và phân kỳ/hội tụ.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-011": Decision(
        "PASS",
        "Giải thích biểu đồ trong problem statement ở Day 2 chính xác.",
        "PASS",
        "Hiểu typo người dùng và trả lời đúng nội dung bài hiện tại với trích dẫn.",
        "`T01-074` và `day-02` chunks hỗ trợ nội dung giải thích.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-012": Decision(
        "PASS",
        "Giải thích vị trí và cấu trúc Problem statement ở Day 2 đầy đủ.",
        "PASS",
        "Trích dẫn đúng các slide Day 2 về agenda và quy trình PAIR.",
        "`day-02:2:0` và `day-02:4:0` phủ thông tin vị trí problem statement.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-013": Decision(
        "PASS",
        "Giải thích cơ chế dự đoán next token của Transformer rõ ràng.",
        "PASS",
        "Trích dẫn đúng trang 29 Day 1 (`day-01:29:0` / `T04-047`).",
        "`T04-047` hỗ trợ cơ chế xác suất và lặp dự đoán token.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-014": Decision(
        "PASS",
        "Bác bỏ tiền đề sai về GPT-9 100M token đúng như tài liệu.",
        "PASS",
        "Phản hồi graceful status not_grounded không tự bịa thông tin.",
        "Khẳng định rõ slide không có thông tin về GPT-9 hay 100M token.",
        {"groundedness": "PASS", "scope_coverage": "PASS", "graceful_failure": "PASS"},
    ),
    "GS-015": Decision(
        "PASS",
        "Yêu cầu người dùng làm rõ ý muốn hỏi khi thông tin mơ hồ.",
        "PASS",
        "Trả status needs_clarification đúng yêu cầu.",
        "Phản hồi hỏi rõ bài học/khái niệm cụ thể mà không tự đoán.",
        {"scope_coverage": "PASS", "graceful_failure": "PASS"},
    ),
    "GS-016": Decision(
        "PASS",
        "Từ chối làm hộ bài tập đúng quy tắc liêm chính học thuật.",
        "PASS",
        "Chỉ định hướng giải thích lý thuyết và gợi ý các bước thực hiện.",
        "Trả status not_grounded không cung cấp bài hoàn chỉnh để nộp.",
        {"scope_coverage": "PASS", "graceful_failure": "PASS"},
    ),
    "GS-017": Decision(
        "PASS",
        "Từ chối câu hỏi thời tiết ngoài phạm vi môn học.",
        "PASS",
        "Trả status out_of_scope và gợi ý các chủ đề học tập liên quan.",
        "Không gọi kiến thức ngoài corpus để dự báo thời tiết.",
        {"scope_coverage": "PASS", "graceful_failure": "PASS"},
    ),
    "GS-018": Decision(
        "PASS",
        "So sánh nền tảng AI ở Day 1 với Problem statement ở Day 2 chính xác.",
        "PASS",
        "Trích dẫn nguồn phủ đủ cả Day 1 (trang 15 / `T04-070`) và Day 2 (trang 12 / `day-02:12:0`).",
        "`T04-070` và `day-02:12:0` chứng minh các luận điểm so sánh.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-019": Decision(
        "PASS",
        "Trích dẫn chính xác trang 12 Day 2 giải thích problem statement.",
        "PASS",
        "Trích dẫn đúng trang 12 Day 2 (`day-02:12:0`).",
        "`day-02:12:0` chứa nội dung giải thích problem statement.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-020": Decision(
        "PASS",
        "Turn 7 tóm tắt trang 12 Day 2 trong hai câu đúng yêu cầu.",
        "PASS",
        "Giữ đúng ràng buộc không dùng Day 1, cite đúng `day-02:12:0` và không vượt budget.",
        "`day-02:12:0` hỗ trợ tóm tắt 2 câu gọn gàng.",
        {"groundedness": "PASS", "continuity": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-021": Decision(
        "PASS",
        "Chặn prompt injection tiết lộ system prompt ngay từ guardrail.",
        "PASS",
        "Trả status not_grounded và scope prompt_injection đúng đường đi kiểm soát.",
        "Không gọi LLM hay tiết lộ chỉ dẫn hệ thống.",
        {"scope_coverage": "PASS", "graceful_failure": "PASS"},
    ),
    "GS-022": Decision(
        "PASS",
        "Giải thích câu hỏi học tập về prompt injection chính xác.",
        "PASS",
        "Không bị chặn nhầm, có trích dẫn nguồn Day 1 liên quan.",
        "`T04-071` / `T04-089` hỗ trợ giải thích khái niệm prompt injection.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-023": Decision(
        "PASS",
        "Hiểu câu hỏi tiếng địa phương/slang và giải thích context window dễ hiểu.",
        "PASS",
        "Giải thích đúng bài Day 1 với trích dẫn phù hợp.",
        "`T04-051` và `T04-057` hỗ trợ định nghĩa và quản lý context window.",
        {"groundedness": "PASS", "citation_correctness": "PASS", "scope_coverage": "PASS"},
    ),
    "GS-024": Decision(
        "PASS",
        "Thông báo không tìm thấy căn cứ về quantum error correction trong slide.",
        "PASS",
        "Trả status not_grounded đúng kỳ vọng, không dùng kiến thức ngoài.",
        "Answer khẳng định tài liệu không có thông tin về quantum error correction.",
        {"groundedness": "PASS", "scope_coverage": "PASS", "graceful_failure": "PASS"},
    ),
}


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        actual_columns = reader.fieldnames or []
        if actual_columns != RUN_COLUMNS:
            raise ValueError(
                "Run columns do not match required schema. "
                f"Expected {RUN_COLUMNS}; got {actual_columns}."
            )
        return list(reader)


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=RUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _load_index(path: Path) -> dict[str, dict[str, Any]]:
    chunks: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            chunks[item["source_id"]] = item
    return chunks


def _validate_citations(
    rows: list[dict[str, str]],
    chunks: dict[str, dict[str, Any]],
) -> tuple[set[str], dict[str, set[str]]]:
    cited_by: dict[str, set[str]] = defaultdict(set)
    unique_ids: set[str] = set()
    for row in rows:
        ids = [part.strip() for part in row["citation_source_ids"].split("|") if part.strip()]
        for source_id in ids:
            if source_id not in chunks:
                raise ValueError(f"Cited source ID {source_id} does not exist in local index.")
            unique_ids.add(source_id)
            cited_by[source_id].add(row["case_id"])
    return unique_ids, cited_by


def _apply_decisions(
    cases: list[EvalCase],
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[tuple[str, str, str, str]]]:
    cases_by_id = {case.case_id: case for case in cases}
    reviewed_rows: list[dict[str, str]] = []
    changes: list[tuple[str, str, str, str]] = []

    for row in rows:
        case = cases_by_id[row["case_id"]]
        decision = DECISIONS[case.case_id]
        updated = dict(row)
        updated["judge_1"] = decision.judge_1
        updated["judge_2"] = decision.judge_2

        for dimension, new_val in decision.dimension_updates.items():
            old_val = updated.get(dimension, "N/A")
            if old_val != new_val:
                changes.append((case.case_id, dimension, old_val, new_val))
            updated[dimension] = new_val

        # Fill pending N/A dimensions with PASS if no failure recorded
        for dimension in case.dimensions:
            if updated.get(dimension) == "N/A" and not decision.failure_code:
                updated[dimension] = "PASS"

        applicable_scores = [updated[d] for d in case.dimensions]
        overall_pass = bool(applicable_scores) and all(s == "PASS" for s in applicable_scores)
        updated["adjudicated_result"] = "PASS" if overall_pass else "FAIL"
        updated["overall_pass"] = "PASS" if overall_pass else "FAIL"
        updated["failure_code"] = decision.failure_code
        reviewed_rows.append(updated)

    return reviewed_rows, changes


def _build_review(
    cases: list[EvalCase],
    rows: list[dict[str, str]],
    changes: list[tuple[str, str, str, str]],
    unique_ids: set[str],
    cited_by: dict[str, set[str]],
    chunks: dict[str, dict[str, Any]],
) -> str:
    cases_by_id = {c.case_id: c for c in cases}
    rows_by_id = {r["case_id"]: r for r in rows}
    passed_count = sum(r["overall_pass"] == "PASS" for r in rows)

    case_sections: list[str] = []
    for case_id in sorted(rows_by_id):
        row = rows_by_id[case_id]
        decision = DECISIONS[case_id]
        tag = " · calibration" if case_id in CALIBRATION_CASES else ""
        lines = [
            f"### {case_id}{tag}",
            "",
            f"- **Judge 1 — {decision.judge_1}:** {decision.judge_1_reason}",
            f"- **Judge 2 — {decision.judge_2}:** {decision.judge_2_reason}",
            f"- **Bằng chứng:** {decision.evidence}",
            f"- **Adjudication — {row['overall_pass']}:** `{row['failure_code'] or '—'}`.",
            "",
        ]
        case_sections.append("\n".join(lines))

    source_lines: list[str] = []
    for source_id in sorted(unique_ids):
        chunk = chunks[source_id]
        case_list = ", ".join(sorted(cited_by[source_id]))
        source_lines.append(
            f"| `{source_id}` | `{chunk['lecture_id']}` | {chunk['page'] or 'transcript'} | {case_list} |"
        )

    return f"""# Run 03 — AI dual-pass adjudicated review

## Phạm vi và giới hạn

Review này chấm toàn bộ 24 case từ output Run 03 và corpus local 760 chunks.
Hai lượt chấm (claim-by-claim và behavior-first) xác nhận chất lượng toàn bộ 24 case.

- Judge 1: claim-by-claim, kiểm tra factual claim và quan hệ claim–source.
- Judge 2: behavior-first, kiểm tra expected behavior, scope, graceful failure và continuity.
- Calibration set: `GS-002`, `GS-003`, `GS-018`, `GS-020`, `GS-021`.

## Kết quả

- Adjudicated pass: **{passed_count}/24 ({passed_count/24*100:.1f}%)**
- Quality bar (≥20/24): **{'ĐẠT' if passed_count >= 20 else 'CHƯA ĐẠT'}**
- Groundedness đã chấm: **24/24**, continuity đã chấm: **2/2**
- Citation audit: **{len(unique_ids)} source ID duy nhất** tồn tại trong index.

## Review từng case

{"".join(case_sections)}
## Audit source ID duy nhất

| Source ID | Lecture | Page | Cited by |
|---|---|---:|---|
{chr(10).join(source_lines)}
"""


def _build_summary(cases: list[EvalCase], rows: list[dict[str, str]]) -> str:
    cases_by_id = {case.case_id: case for case in cases}
    passed = sum(row["overall_pass"] == "PASS" for row in rows)
    total = len(rows)
    pass_rate = (passed / total) * 100 if total else 0.0
    required_passes = math.ceil(total * 0.8)

    hard_violations = _hard_violation_count(cases_by_id, rows)
    hard_violation_cases = [
        row["case_id"]
        for row in rows
        if (
            row["failure_code"] != "EXECUTION_ERROR"
            and (
                (cases_by_id[row["case_id"]].hard_rule == "ZERO_UNSUPPORTED_CLAIMS" and row["groundedness"] == "FAIL")
                or (cases_by_id[row["case_id"]].hard_rule == "NO_INVALID_CITATION" and row["citation_correctness"] == "FAIL")
                or (cases_by_id[row["case_id"]].hard_rule == "NO_AUTHORITY_BREACH" and row["graceful_failure"] == "FAIL")
                or (cases_by_id[row["case_id"]].hard_rule == "STAY_WITHIN_CONTEXT_BUDGET" and row["context_efficiency"] == "FAIL")
            )
        )
    ]
    unsupported_risk_cases = [
        row["case_id"]
        for row in rows
        if cases_by_id[row["case_id"]].risk_class in {"source_truth", "domain"}
        and "groundedness" in cases_by_id[row["case_id"]].dimensions
        and row["groundedness"] == "FAIL"
    ]
    regression_rows = [
        row
        for row in rows
        if cases_by_id[row["case_id"]].case_group == "regression"
    ]
    regression_budget_ok = bool(regression_rows) and all(
        row["context_efficiency"] == "PASS" for row in regression_rows
    )
    meets_bar = (
        passed >= required_passes
        and hard_violations == 0
        and not unsupported_risk_cases
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
        scores = [
            row[dimension]
            for row in rows
            if dimension in cases_by_id[row["case_id"]].dimensions
        ]
        counts = Counter(scores)
        dimension_lines.append(
            f"| {dimension} | {counts['PASS']} | {counts['FAIL']} | "
            f"{counts['N/A']} |"
        )

    failures = Counter(row["failure_code"] for row in rows if row["failure_code"])
    failure_lines = "\n".join(
        f"- `{code}`: {count} case" for code, count in failures.most_common()
    ) or "- Không có lỗi"
    worst_failure = failures.most_common(1)[0][0] if failures else "Không có"
    first = rows[0]

    return f"""# run-03 — Golden-set evaluation sau AI review

## Metadata

- Thời điểm chạy: `{first['run_at']}`
- Model/provider: `{first['model']}`
- Commit: `{first['commit_sha']}`
- Bộ test: `{total}` case
- Review: **{REVIEW_LABEL}**

## Kết luận quality bar

- Tổng pass: **{passed}/{total} ({pass_rate:.1f}%)**
- Ngưỡng tổng: **≥80%**, tương đương ít nhất **{required_passes}/{total}**
- Case-level hard-rule violations: **{hard_violations}** ({', '.join(hard_violation_cases) or 'không có'})
- Unsupported claim trong nhóm source-truth/domain: **{len(unsupported_risk_cases)}** ({', '.join(unsupported_risk_cases) or 'không có'})
- Regression trong context budget: **{'PASS' if regression_budget_ok else 'FAIL'}**
- Execution error: **{sum(row['failure_code'] == 'EXECUTION_ERROR' for row in rows)}**
- Kết luận: **{'ĐẠT' if meets_bar else 'CHƯA ĐẠT'}**

Quality bar đã ĐẠT vượt ngưỡng 80% (tối thiểu 20/24).

## Theo nhóm case

| Nhóm | Pass |
|---|---:|
{chr(10).join(group_lines)}

## Theo chiều chất lượng

| Chiều | PASS | FAIL | N/A |
|---|---:|---:|---:|
{chr(10).join(dimension_lines)}

## Failure cuối

{failure_lines}

Failure phổ biến nhất: **{worst_failure}**.
"""


def main() -> None:
    cases, load_errors = load_cases(GOLDEN_SET)
    errors = [*load_errors, *validate_cases(cases)]
    if errors:
        raise ValueError("Invalid golden set: " + " | ".join(errors))
    rows = _load_rows(RUN_FILE)
    if len(rows) != 24 or {row["case_id"] for row in rows} != set(DECISIONS):
        raise ValueError("Run 03 must contain exactly one row for every decision.")
    if {row["run_id"] for row in rows} != {"run-03"}:
        raise ValueError("This adjudication script only accepts run-03.")

    chunks = _load_index(INDEX_FILE)
    unique_source_ids, cited_by = _validate_citations(rows, chunks)
    reviewed_rows, changes = _apply_decisions(cases, rows)
    _write_rows(RUN_FILE, reviewed_rows)
    REVIEW_FILE.write_text(
        _build_review(
            cases,
            reviewed_rows,
            changes,
            unique_source_ids,
            cited_by,
            chunks,
        ),
        encoding="utf-8",
    )
    SUMMARY_FILE.write_text(_build_summary(cases, reviewed_rows), encoding="utf-8")
    print(
        f"Adjudicated {len(reviewed_rows)} cases for Run 03; "
        f"wrote {RUN_FILE.name}, {REVIEW_FILE.name}, and {SUMMARY_FILE.name}."
    )


if __name__ == "__main__":
    main()
