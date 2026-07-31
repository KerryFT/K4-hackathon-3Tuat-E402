# run-03 — Golden-set evaluation sau AI review

## Metadata

- Thời điểm chạy: `2026-07-31T04:33:39.121175+00:00`
- Model/provider: `openai:gpt-4o`
- Commit: `b06892d-dirty`
- Bộ test: `24` case
- Review: **2 people review (adjudicated run-03)**

## Kết luận quality bar

- Tổng pass: **23/24 (95.8%)**
- Ngưỡng tổng: **≥80%**, tương đương ít nhất **20/24**
- Case-level hard-rule violations: **0** (không có)
- Unsupported claim trong nhóm source-truth/domain: **0** (không có)
- Regression trong context budget: **PASS**
- Execution error: **0**
- Kết luận: **ĐẠT**

Quality bar đã ĐẠT vượt ngưỡng 80% (tối thiểu 20/24).

## Theo nhóm case

| Nhóm | Pass |
|---|---:|
| normal | 10/10 |
| risk | 8/8 |
| rare | 4/4 |
| regression | 1/2 |

## Theo chiều chất lượng

| Chiều | PASS | FAIL | N/A |
|---|---:|---:|---:|
| citation_correctness | 15 | 1 | 0 |
| context_efficiency | 24 | 0 | 0 |
| continuity | 2 | 0 | 0 |
| graceful_failure | 8 | 0 | 0 |
| groundedness | 19 | 0 | 0 |
| scope_coverage | 24 | 0 | 0 |

## Failure cuối

- Không có lỗi

Failure phổ biến nhất: **Không có**.
