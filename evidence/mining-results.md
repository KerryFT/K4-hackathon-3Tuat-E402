# Kết quả mining

**Trạng thái:** đã audit sơ bộ, số liệu chính thức bên dưới.

| Chỉ số | Kết quả chính thức | Ghi chú |
|---|---:|---|
| Tổng student turns trong data pack | 1.261 | Đơn vị đếm: student turn |
| Candidate yêu cầu tóm tắt/tổng hợp | 91 turn / 72 user / 83 conversation | Lọc keyword + audit tay |
| Candidate có citation rỗng | 57/91 (62,6%) | Tutor không cite được nguồn |
| Candidate có ngôn ngữ giới hạn/thiếu nguồn | 44/91 (48,4%) | Tutor nói thiếu ngữ cảnh/phạm vi |
| False positive sau audit | 8/91 (8,8%) | Ví dụ: hỏi giải thích 1 đoạn cụ thể, không phải tổng hợp |
| Candidate hợp lệ sau audit | 83/91 (91,2%) | Giữ lại làm evidence |
| Input token trung bình từ turn 6+ | ~13.120 token | Cao hơn ~23% so với turn đầu |

## Ví dụ kiểm chứng

| # | Mã conversation / turn | Nhãn | Trích đoạn tối thiểu | Lý do phân loại |
|---|---|---|---|---|
| 1 | `conv-0142 / turn-3` | `WHOLE_LESSON` | "Tóm tắt lại toàn bộ buổi học hôm nay cho em" | User yêu cầu tổng hợp toàn bài, tutor trả lời thiếu citation cho nhiều phần |
| 2 | `conv-0087 / turn-5` | `CROSS_DAY` | "Hôm trước thầy có nói về attention, hôm nay liên hệ thế nào với problem statement?" | Câu hỏi cần nguồn Day 1 (attention) trong khi đang ở Day 2; tutor trả lời không có citation Day 1 |
| 3 | `conv-0215 / turn-2` | `CONTEXT_BREAK` | "Em hỏi lại lần nữa, ý em là slide trước đó chứ không phải slide này" | User phải nhắc lại phạm vi vì tutor hiểu sai "slide này" |
| 4 | `conv-0301 / turn-8` | `LONG_CONTEXT_RISK` | "Quay lại câu hỏi đầu tiên của em về context window" | Hội thoại ≥8 turn, user muốn quay lại chủ đề đầu; input token tăng rõ rệt |
| 5 | `conv-0178 / turn-4` | `WHOLE_LESSON` | "Cho em một bản tóm tắt các điểm chính của bài giảng" | User yêu cầu tóm tắt điểm chính; tutor trả lời citation rỗng và nói "không đủ ngữ cảnh" |
| 6 | `conv-0056 / turn-6` | `CROSS_DAY` | "So sánh cách giảng viên giải thích token ở Day 1 với cách dùng token trong bài Day 2" | Cần trích cả hai ngày; tutor chỉ cite Day 2 |
| 7 | `conv-0410 / turn-3` | `CONTEXT_BREAK` | "Không phải trang đó, em đang hỏi về trang có sơ đồ Diamond" | User sửa lại phạm vi khi tutor cite sai trang |
