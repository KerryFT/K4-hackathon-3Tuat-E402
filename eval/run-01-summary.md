# run-01 — Golden-set evaluation

## Metadata

- Thời điểm: `2026-07-31T03:17:59.196974+00:00`
- Model/provider: `mock:gpt-4o`
- Commit: `a3abfdd-dirty`
- Bộ test: `24` case
- Human review: các ô `N/A` ở chiều áp dụng vẫn được coi là chưa đạt cho tới khi adjudicate.

## Kết luận quality bar

- Tổng pass: **4/24 (16.7%)**
- Ngưỡng tổng: **≥80%**, tương đương ít nhất **20/24**
- Hard-rule violations đã quan sát: **0**
- Regression trong context budget: **FAIL**
- Kết luận: **CHƯA ĐẠT**

Quality bar được giữ nguyên; kết quả thấp hoặc execution error không làm thay đổi chuẩn.

## Theo nhóm case

| Nhóm | Pass |
|---|---:|
| normal | 0/10 |
| risk | 3/8 |
| rare | 1/4 |
| regression | 0/2 |

## Theo chiều chất lượng

| Chiều | PASS | FAIL | N/A |
|---|---:|---:|---:|
| citation_correctness | 0 | 16 | 0 |
| context_efficiency | 4 | 20 | 0 |
| continuity | 0 | 2 | 0 |
| graceful_failure | 4 | 4 | 0 |
| groundedness | 0 | 19 | 0 |
| scope_coverage | 4 | 20 | 0 |

## Failure nổi bật

- `EXECUTION_ERROR`: 20 case

Failure nghiêm trọng nhất theo tần suất: **EXECUTION_ERROR**.

## Bước tiếp theo

1. Khắc phục execution/configuration error trước nếu có.
2. Hai người chấm độc lập năm case hiệu chuẩn theo `scoring-guide.md`.
3. Adjudicate các chiều ngữ nghĩa còn `N/A`, sau đó tính lại summary.
4. Chọn một failure nghiêm trọng để sửa; nếu sản phẩm thay đổi, chạy lại toàn bộ thành Run 02 và không ghi đè Run 01.
