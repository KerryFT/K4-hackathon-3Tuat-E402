# AI Chat Assistant — Three-Tier Framework

Khung monorepo ban đầu cho một trợ lý chat AI phục vụ demo/hackathon. Repository hiện chỉ định nghĩa cấu trúc và ranh giới kiến trúc; chưa chứa mã nguồn, manifest, dependency hay dịch vụ có thể chạy.

## Kiến trúc

Luồng giao tiếp dự kiến:

```text
Frontend (Next.js) → Backend (FastAPI) → Agent (FastAPI/Python) → OpenAI
```

- **Frontend** chịu trách nhiệm giao diện đăng nhập demo, giao diện chat và hiển thị dữ liệu streaming. Frontend chỉ gọi backend, không truy cập trực tiếp agent hoặc OpenAI.
- **Backend** là API công khai, xử lý đăng nhập demo, nhận yêu cầu chat và chuyển tiếp yêu cầu đến agent qua HTTP nội bộ.
- **Agent** sở hữu prompt, OpenAI adapter, tool registry và vòng lặp tool-calling.
- Dữ liệu phản hồi chat dự kiến được truyền bằng Server-Sent Events (SSE).

## Cổng local dự kiến

| Service | Công nghệ | Cổng |
| --- | --- | ---: |
| Frontend | Next.js + TypeScript | `3000` |
| Backend | FastAPI + Python | `8000` |
| Agent | FastAPI + Python | `8001` |

## Endpoint dự kiến

Các endpoint dưới đây mới là quy ước kiến trúc, chưa được triển khai.

### Backend công khai

- `GET /health` — kiểm tra trạng thái backend.
- `POST /api/v1/auth/demo-login` — đăng nhập demo, không có người dùng thật hoặc phiên bền vững.
- `POST /api/v1/chat/stream` — chuyển yêu cầu chat tới agent và stream phản hồi bằng SSE.

### Agent nội bộ

- `GET /health` — kiểm tra trạng thái agent.
- `POST /internal/v1/agent-runs/stream` — chạy agent, gọi OpenAI/tool khi cần và stream sự kiện về backend.

## Cấu trúc repository

```text
.
├── frontend/   # UI, auth demo và chat
├── backend/    # API công khai và client gọi agent
├── agent/      # Agent runtime, prompts, tools và OpenAI adapter
└── docs/       # Tài liệu kiến trúc mở rộng trong tương lai
```

Mỗi service có vùng `app` hoặc `src` riêng và thư mục kiểm thử độc lập. Các thư mục rỗng được giữ trong Git bằng `.gitkeep`.

## Giới hạn hiện tại

- Chưa có source code hoặc package manifest.
- Chưa cài dependency và chưa có lệnh khởi chạy.
- Không có database, agent memory hoặc lịch sử chat phía server.
- Đăng nhập chỉ phục vụ demo và không lưu phiên bền vững.
- Chưa có Docker, CI/CD hoặc cấu hình cloud.

## Cấu hình môi trường

Sao chép `.env.example` thành `.env` khi bắt đầu triển khai. Không commit API key hoặc thông tin đăng nhập thật vào repository.
