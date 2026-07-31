# Runtime artifacts

Đầu ra có thể kiểm tra lại của chatbot. Không dùng thư mục này cho source code.

- `conversations`: audit log JSONL theo phiên chat. Mỗi dòng là một lượt
  user–bot gồm request, response, citation, retrieval trace và thời gian xử lý.
- `evaluation-runs`: kết quả chạy golden set theo phiên bản.
- `traces`: trace router, retrieval, context budget và tool calls.
- `exports`: file xuất phục vụ demo.

Mặc định dữ liệu runtime trong các thư mục con không commit để tránh lộ nội dung
người dùng. Chỉ đưa bản đã ẩn danh vào Git khi cần làm evidence.

Tên file hội thoại là SHA-256 của `conversation_id`; ID gốc vẫn nằm trong từng
event JSON. Không ghi tên, email, API key hoặc system prompt. Có thể tắt hoàn
toàn bằng `CONVERSATION_LOG_ENABLED=false`.
