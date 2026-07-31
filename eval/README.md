# Evaluation

Thư mục này chứa bộ đánh giá có thể phúc khảo của VLearn Context Tutor.

## Artifact

- `golden-set.csv`: 24 case đã khóa ID, gồm 10 thường, 8 risk, 4 hiếm và
  2 regression; 12 case phát triển từ chatlog ẩn danh.
- `scoring-guide.md`: định nghĩa `PASS`/`FAIL`/`N/A`, sáu chiều chất lượng,
  hard rules và quy trình hai người chấm.
- `results-cp3.md`: smoke test một case; không thay cho full golden-set run.
- `run-01.csv`: output và điểm của toàn bộ 24 case, kể cả fail/execution error.
- `run-01-summary.md`: tỷ lệ, quality bar, phân bố lỗi và bước tiếp theo.
- `run-02.csv`: lượt OpenAI thật trên index 760 chunks; giữ đủ 24 case.
- `run-02-review.md`: hai lượt AI review (claim-by-claim và behavior-first),
  có bằng chứng từng case và audit 41 source ID duy nhất.
- `run-02-summary.md`: kết quả sau adjudication mang nhãn

## Quality bar đã khóa

Đạt khi có ít nhất 20/24 case pass, không có unsupported factual claim trong
nhóm nguồn-sự-thật/domain, và cả hai regression không vượt context budget.
Không thay đổi quality bar sau Run 01.

## Lệnh

Chạy từ thư mục `be/`:

```powershell
python scripts/validate_eval_set.py
python scripts/run_evaluation.py --validate-only
python scripts/run_evaluation.py
```

Runner luôn giữ đủ 24 dòng. Thiếu index/API key hoặc exception được ghi thành
`EXECUTION_ERROR`, không bị bỏ khỏi mẫu số.

Run 02 đã được 2 người review độc lập; có thể tái áp
