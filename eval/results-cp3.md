# CP3 smoke test — grounded cross-lecture answer

- Thời điểm chạy: 30/07/2026
- Model: `gpt-4o`
- Pipeline: Chat API → scope router → JSONL retrieval → OpenAI Responses API →
  citation validator
- Câu hỏi: “Problem statement liên hệ thế nào với nền tảng AI và LLM giữa Day
  1 và Day 2?”
- Kết quả: **PASS**
- Status: `answered`
- Scope: `selected_lectures`
- Citation hợp lệ:
  - `day-01:15:0` — Day 1, trang 15
  - `day-02:12:0` — Day 2, trang 12
  - `day-02:13:0` — Day 2, trang 13

## Điều đã xác minh

1. API key được đọc từ biến môi trường và không xuất hiện trong output.
2. Router nhận ra yêu cầu xuyên Day 1–Day 2.
3. Retrieval đưa nguồn từ cả hai lecture vào context.
4. Một lời gọi LLM thật trả Structured Output.
5. Backend chỉ dựng citation từ `source_id` tồn tại trong retrieved context.
6. Coverage guardrail xác nhận citation phủ cả Day 1 và Day 2.

JSON chi tiết của lượt chạy được sinh bởi `be/scripts/smoke_cp3.py` tại
`artifacts/evaluation-runs/cp3-smoke.json`. Artifact runtime này bị Git bỏ qua
theo chính sách dữ liệu; file hiện tại là bản kết quả đã rà soát để nộp.

## Giới hạn

Đây là smoke test một case để xác minh CP3, chưa phải kết quả quality bar trên
toàn bộ golden set 24 case. Lượt đánh giá tiếp theo phải chạy toàn bộ
`eval/golden-set.csv`.
