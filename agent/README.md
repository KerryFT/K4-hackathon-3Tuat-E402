# Transcript Agent

LangGraph agent tóm tắt và hỏi đáp trên transcript của Day 1 hoặc Day 2.
Agent chỉ đọc một trong hai thư mục cố định:

- `data/transcript/day_1`
- `data/transcript/day_2`

Slide và chatlog không được index.

## Cài đặt

Từ thư mục `agent`:

```powershell
uv sync --extra test
```

Điền tối thiểu hai biến sau trong file `.env` ở repository root:

```dotenv
OPENAI_API_KEY=...
OPENAI_MODEL=...
```

`OPENAI_EMBEDDING_MODEL` mặc định là `text-embedding-3-small`.

## Khởi chạy

```powershell
uv run uvicorn app.main:app --reload --port 8001
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health
```

## Gọi API

Tóm tắt Day 1:

```powershell
$body = @{
    day_id = "day_1"
    mode = "summary"
    query = $null
} | ConvertTo-Json

Invoke-WebRequest `
    -Method Post `
    -Uri http://127.0.0.1:8001/internal/v1/agent-runs/stream `
    -ContentType "application/json" `
    -Body $body
```

Hỏi đáp trên Day 2:

```powershell
$body = @{
    day_id = "day_2"
    mode = "qa"
    query = "Automation và augmentation khác nhau thế nào?"
} | ConvertTo-Json

Invoke-WebRequest `
    -Method Post `
    -Uri http://127.0.0.1:8001/internal/v1/agent-runs/stream `
    -ContentType "application/json" `
    -Body $body
```

Endpoint trả các SSE event `status`, `token`, `sources`, `done` hoặc `error`.

## Gọi LangGraph trực tiếp

```python
from app.runtime import create_runtime

runtime = create_runtime()
result = await runtime.graph.ainvoke(
    {
        "day_id": "day_1",
        "mode": "qa",
        "query": "Attention trong transformer hoạt động như thế nào?",
    }
)
print(result["answer"])
```

## Cache và kiểm thử

- Chroma index: `agent/.cache/chroma`
- Summary cache: `agent/.cache/summaries`
- Thay đổi transcript sẽ tự làm mất hiệu lực cache của đúng Day tương ứng.

Chạy test offline:

```powershell
uv run pytest
```

Chạy thêm integration test với OpenAI thật:

```powershell
$env:RUN_OPENAI_INTEGRATION = "1"
uv run pytest -m integration
```
