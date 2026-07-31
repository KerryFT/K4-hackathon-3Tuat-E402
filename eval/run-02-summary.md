# run-02 — Golden-set evaluation sau AI review

## Metadata

- Thời điểm chạy: `2026-07-31T03:25:31.589286+00:00`
- Model/provider: `openai:gpt-4o`
- Commit: `a3abfdd-dirty`
- Bộ test: `24` case
- Review: 2 người chấm độc lập — hai phương pháp chấm của cùng một AI, không phải hai người độc lập.
- Semantic dimensions: không còn `N/A` ở 19 groundedness và 2 continuity áp dụng.

## Kết luận quality bar

- Tổng pass: **9/24 (37.5%)**
- Ngưỡng tổng: **≥80%**, tương đương ít nhất **20/24**
- Case-level hard-rule violations: **4** (GS-014, GS-018, GS-019, GS-024)
- Unsupported claim trong nhóm source-truth/domain: **3** (GS-014, GS-018, GS-024)
- Regression trong context budget: **PASS**
- Execution error: **0**
- Kết luận tạm thời: **CHƯA ĐẠT**

Quality bar được giữ nguyên. Kết quả này phục vụ phân tích prototype; kết luận tuân
thủ rubric cuối cùng vẫn cần hai người thật xác nhận.

## Theo nhóm case

| Nhóm | Pass |
|---|---:|
| normal | 3/10 |
| risk | 3/8 |
| rare | 2/4 |
| regression | 1/2 |

## Theo chiều chất lượng

| Chiều | PASS | FAIL | N/A |
|---|---:|---:|---:|
| citation_correctness | 7 | 9 | 0 |
| context_efficiency | 24 | 0 | 0 |
| continuity | 1 | 1 | 0 |
| graceful_failure | 4 | 4 | 0 |
| groundedness | 11 | 8 | 0 |
| scope_coverage | 19 | 5 | 0 |

## Failure cuối

- `INVALID_CITATION`: 7 case
- `UNSUPPORTED_CLAIM`: 4 case
- `WRONG_SCOPE`: 2 case
- `CONTEXT_LOSS`: 1 case
- `MISSED_CLARIFICATION`: 1 case

Failure phổ biến nhất: **INVALID_CITATION**.

## Nguyên nhân chính

1. Citation tồn tại nhưng sai trang hoặc không hỗ trợ nội dung user yêu cầu.
2. Answer mở rộng factual claim vượt phần được retrieved source chứng minh.
3. Một số control behavior trả `answered` khi phải clarification/not-grounded.

Chi tiết claim/source/turn và hai judgment nằm trong `eval/run-02-review.md`.
Nếu sửa prompt, retrieval hoặc guardrail, phải chạy lại toàn bộ thành Run 03;
không ghi đè output hay judgment của Run 01/02.
