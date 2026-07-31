# API draft

## `POST /api/v1/chat`

Request:

```json
{
  "message": "So sánh JTBD trong bài này với bài trước",
  "conversation_id": "demo-01",
  "context": {
    "course_id": "COMP2010",
    "current_lecture_id": "day-02",
    "current_page": 8,
    "selected_lecture_ids": ["day-01", "day-02"]
  }
}
```

Response:

```json
{
  "conversation_id": "demo-01",
  "answer": "...",
  "status": "answered",
  "scope": "selected_lectures",
  "citations": [
    {
      "source_id": "day-01:14:0",
      "lecture_id": "day-01",
      "lecture_title": "Day 01",
      "page": 14,
      "excerpt": "..."
    }
  ],
  "suggested_questions": []
}
```

`conversation_id` là tùy chọn trong request. Nếu client không gửi, backend sinh
UUID và trả lại trong response. Client nên gửi lại cùng ID ở các lượt sau để
nhóm các event vào một phiên audit.

Mỗi lượt gọi được append dưới dạng một dòng JSON vào
`artifacts/conversations/<sha256-conversation-id>.jsonl` khi
`CONVERSATION_LOG_ENABLED=true`. Event chứa request, response, citation, trace
retrieval và thời gian xử lý; không chứa tên, email, API key hoặc system prompt.
Lỗi ghi log không làm thay đổi response của API.

Các endpoint course cũ vẫn ở `/api/course/*` để frontend hiện tại tương thích.
