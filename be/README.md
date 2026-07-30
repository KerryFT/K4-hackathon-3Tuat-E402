# VLearn backend

FastAPI backend cho trợ giảng có căn cứ từ slide. Code được chia theo trách
nhiệm: HTTP API, application services, agent orchestration, tools, retrieval và
các provider có thể thay thế.

Đây là runtime agent duy nhất của ứng dụng. Frontend gọi trực tiếp
`POST /api/v1/chat`; không cần chạy thêm service agent ở cổng khác.

Trước khi vào retrieval/LLM, chat pipeline xử lý cục bộ các intent xã giao như
`xin chào`, `cảm ơn`, `tạm biệt` và chặn các mẫu prompt injection nhằm ghi đè
chỉ dẫn hoặc lấy system prompt/secret. Câu hỏi kiến thức về chính chủ đề
“prompt injection” vẫn được phép đi qua pipeline có citation.

## Chạy local

```powershell
cd be
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Kiểm tra:

- `GET http://localhost:8000/api/v1/health`
- `GET http://localhost:8000/api/course/info`
- `POST http://localhost:8000/api/v1/chat`
- OpenAPI: `http://localhost:8000/docs`

Chat endpoint chạy chuỗi scope → retrieval → LLM → citation validation. Nếu
index hoặc API key chưa sẵn sàng, endpoint trả `not_configured` thay vì tạo câu
trả lời không có căn cứ.

## Ingest slide

Đặt PDF theo tên `d1-*.pdf`, `d2-*.pdf`, ... trong `fe/public/slides`, rồi chạy:

```powershell
cd be
python scripts/ingest_documents.py
```

Mặc định pipeline đọc text theo từng trang, chuẩn hóa, chia chunk tối đa 1.200
ký tự và ghi:

- `be/data/indexes/lecture_chunks.jsonl`: các chunk có `course_id`,
  `lecture_id`, `page` và nội dung;
- `be/data/indexes/lecture_chunks.manifest.json`: checksum và thống kê nguồn để
  kiểm tra index có khớp đúng phiên bản slide.

Có thể đổi đường dẫn và kích thước chunk:

```powershell
python scripts/ingest_documents.py `
  --slides-dir ../fe/public/slides `
  --output data/indexes/lecture_chunks.jsonl `
  --max-characters 1200
```

Chạy lại lệnh sẽ thay toàn bộ index một cách an toàn, tránh nhân đôi chunk. Kho
JSONL dùng lexical search offline ở môi trường phát triển; bước sau có thể thay
provider embeddings mà không đổi schema chunk.

## Cấu hình LLM thật cho CP3

Sao chép `be/.env.example` thành `be/.env`, sau đó điền:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-sol
OPENAI_REASONING_EFFORT=low
```

Không commit `be/.env` hoặc API key. Provider dùng OpenAI Responses API với
Structured Outputs. Model chỉ trả answer và danh sách `source_id`; backend dựng
citation từ index và chặn toàn bộ câu trả lời nếu citation không tồn tại.

Trình tự chạy local:

```powershell
cd be
python scripts/ingest_documents.py
uvicorn main:app --reload
```

Frontend gọi endpoint `POST /api/v1/chat`. Có thể kiểm tra nhanh tại
`http://localhost:8000/docs`.

Sau khi có API key, chạy một lượt thật qua toàn pipeline và lưu evidence CP3:

```powershell
python scripts/smoke_cp3.py
```

Lệnh chỉ pass khi response có trạng thái `answered`; kết quả được lưu tại
`artifacts/evaluation-runs/cp3-smoke.json`.

## Chạy test

```powershell
cd be
python -m unittest discover -s tests -p "test_*.py"
```
