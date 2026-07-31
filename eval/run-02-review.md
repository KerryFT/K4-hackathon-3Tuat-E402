# Run 02 — AI dual-pass provisional

## Phạm vi và giới hạn

Review này chấm toàn bộ 24 case từ output Run 02 và corpus local 760 chunks.
Không gọi Internet, không gọi OpenAI thêm. Hai cột judge là hai phương pháp đọc
của cùng một AI, **không phải hai người chấm độc lập**; vì vậy kết quả chỉ mang
nhãn **AI dual-pass provisional** và vẫn cần hai người thật xác nhận nếu dùng để tuyên bố
tuân thủ rubric.

- Judge 1: claim-by-claim, kiểm tra factual claim và quan hệ claim–source.
- Judge 2: behavior-first, kiểm tra expected behavior, scope, graceful failure và continuity.
- Khi hai lượt khác nhau, adjudication dùng bằng chứng local và chọn kết quả nghiêm ngặt hơn nếu claim không chứng minh được.
- Calibration set: `GS-002`, `GS-003`, `GS-018`, `GS-020`, `GS-021`.

## Kết quả

- Adjudicated pass: **9/24 (37.5%)**
- Judge disagreement: **4/24**
- Groundedness đã chấm: **19/19**, continuity đã chấm: **2/2**
- Citation audit: **60/60 occurrence**, **41/41 source ID duy nhất** tồn tại trong index
- Các semantic mismatch được ghi ở case tương ứng; việc source ID tồn tại không tự động có nghĩa source hỗ trợ claim.

## Review từng case

### GS-001

- **Judge 1 — FAIL:** Các claim về phân tích ngữ nghĩa, hỗ trợ quyết định, nhận diện mẫu và dự đoán xu hướng của LLM không được các chunk đã cite chứng minh.
- **Judge 2 — FAIL:** Có đề cập cả hai Day nhưng không dùng đúng các trang bắt buộc 15/12 và quan hệ giữa hai phần bị mở rộng quá nguồn.
- **Bằng chứng:** `T04-070` chỉ mô tả Transformer/GPT-2 sinh token theo xác suất; `day-02:13:0` mô tả ba bước PAIR, không hỗ trợ danh sách năng lực LLM trong answer.
- **Adjudication — FAIL:** `INVALID_CITATION`; groundedness: N/A → FAIL.

### GS-002 · calibration

- **Judge 1 — PASS:** Không có factual claim cần nguồn; câu trả lời chỉ yêu cầu user xác định Day và trang.
- **Judge 2 — PASS:** Đúng hành vi cần clarification, không tự chọn slide và không gọi sang nội dung khác.
- **Bằng chứng:** Answer hỏi rõ: “Bạn muốn hỏi trang nào?” và yêu cầu chọn Day/số trang.
- **Adjudication — PASS:** `—`; không đổi điểm chiều đã có.

### GS-003 · calibration

- **Judge 1 — PASS:** Ví dụ tool Python đạt 100% khi đủ ba điều kiện được `T03-034` hỗ trợ trực tiếp.
- **Judge 2 — FAIL:** User hỏi vị trí của “mô hình này”, nhưng answer chuyển sang một ví dụ tool khác và trả `answered` thay vì dừng ở `not_grounded`.
- **Bằng chứng:** `T03-034` hỗ trợ claim về tool; không có source nào xác định mô hình/page mà user đang nhắc tới.
- **Adjudication — FAIL:** `WRONG_SCOPE`; groundedness: N/A → PASS; scope_coverage: PASS → FAIL.

### GS-004

- **Judge 1 — PASS:** Các ý về attention, ML/DL, LLM và lịch sử Day 1 đều có căn cứ trong năm chunk Day 1 đã cite.
- **Judge 2 — FAIL:** Turn cuối giữ Day 1 nhưng làm mất mục tiêu ban đầu là giải thích context window; answer biến thành tóm tắt rộng toàn bộ Day 1.
- **Bằng chứng:** Turn 1 đặt mục tiêu “Giải thích context window”; turn 6 chỉ correction về Day 1, không thay mục tiêu đó.
- **Adjudication — FAIL:** `CONTEXT_LOSS`; groundedness: N/A → PASS; continuity: N/A → FAIL.

### GS-005

- **Judge 1 — PASS:** Định nghĩa context, giới hạn context window, compact và chi phí đều được `T04-051`/`T04-057` hỗ trợ.
- **Judge 2 — PASS:** Trả lời đúng câu hỏi Day 1, dễ hiểu và có nguồn liên quan.
- **Bằng chứng:** `T04-051` dùng phép ví von bàn làm việc; `T04-057` mô tả compact, mất thông tin và chi phí hội thoại dài.
- **Adjudication — PASS:** `—`; groundedness: N/A → PASS.

### GS-006

- **Judge 1 — FAIL:** Hai chunk chỉ mô tả cơ chế Transformer; chúng không đưa ra bốn chiến lược tối ưu context như answer gán nhãn, và claim KV giữ trạng thái bất kể độ dài bị vượt nguồn.
- **Judge 2 — FAIL:** Không trả lời bốn chiến lược ở trang 45, thay bằng attention/parallelism/KV/next-token.
- **Bằng chứng:** `T04-094` nói về attention và xử lý song song; `T04-047` nói vòng lặp dự đoán token, không phải bốn chiến lược được yêu cầu.
- **Adjudication — FAIL:** `INVALID_CITATION`; groundedness: N/A → FAIL; scope_coverage: PASS → FAIL.

### GS-007

- **Judge 1 — PASS:** Các mốc 2006/2012/2017, expert systems, token/context và open source đều được các chunk Day 1 đã cite hỗ trợ.
- **Judge 2 — PASS:** Tóm tắt bao phủ nhiều chủ đề Day 1 và không kéo nội dung Day 2 vào.
- **Bằng chứng:** `T04-033`, `T04-028`, `T04-049`, `T04-051`, `T06-059` lần lượt hỗ trợ các nhóm ý chính.
- **Adjudication — PASS:** `—`; groundedness: N/A → PASS.

### GS-008

- **Judge 1 — FAIL:** Các con số kinh tế có trong `T06-060`, nhưng nguồn đó không chứng minh đây là nội dung instruction ở trang 15 như answer ngầm khẳng định.
- **Judge 2 — FAIL:** Trả lời hoàn toàn sang xu hướng kinh tế AI, không giải thích đoạn instruction ở trang 15.
- **Bằng chứng:** `T06-060` là transcript về GDP/pilot-to-production; citation không gắn với trang 15 hay nội dung instruction.
- **Adjudication — FAIL:** `INVALID_CITATION`; groundedness: N/A → PASS; scope_coverage: PASS → FAIL.

### GS-009

- **Judge 1 — FAIL:** Ý context window không có source tương ứng trong citation; claim Trung Quốc “sản xuất chip 0,7 nm” mạnh hơn lời giảng “vừa công bố còn 0,7”.
- **Judge 2 — FAIL:** Đúng dạng tóm tắt corpus nhưng có ý không được citation liền kề hỗ trợ, vi phạm yêu cầu không khẳng định ngoài corpus.
- **Bằng chứng:** `T06-059` hỗ trợ lịch sử/open source nhưng không đủ cho cách diễn đạt sản xuất 0,7 nm; các source còn lại không định nghĩa context window.
- **Adjudication — FAIL:** `UNSUPPORTED_CLAIM`; groundedness: N/A → FAIL; citation_correctness: PASS → FAIL.

### GS-010

- **Judge 1 — FAIL:** Nội dung answer được `day-02:15:0` hỗ trợ, nhưng việc gán nội dung đó cho trang 4 là attribution sai.
- **Judge 2 — FAIL:** User yêu cầu trang 4; hệ thống trả nội dung trang 15.
- **Bằng chứng:** `day-02:15:0` có metadata page 15, trong khi required page là 4.
- **Adjudication — FAIL:** `INVALID_CITATION`; groundedness: N/A → PASS; scope_coverage: PASS → FAIL.

### GS-011

- **Judge 1 — PASS:** First Principle, quy trình PS, Impact–Effort, ranh giới kỹ sư và AI/LLM đều có nguồn hỗ trợ.
- **Judge 2 — FAIL:** Không giải thích biểu đồ được bôi đỏ ở context hiện tại; answer chỉ tổng hợp rộng nhiều đoạn problem statement.
- **Bằng chứng:** `T01-062`, `T01-074`, `T03-095` hỗ trợ các ý riêng lẻ, nhưng không chunk nào nhận diện hoặc giải thích biểu đồ bôi đỏ.
- **Adjudication — FAIL:** `WRONG_SCOPE`; groundedness: N/A → PASS; scope_coverage: PASS → FAIL.

### GS-012

- **Judge 1 — PASS:** Các bước Discover/Define, PAIR và Go/Not Yet/No-Go được ba slide Day 2 hỗ trợ.
- **Judge 2 — PASS:** Hiểu đúng typo/slang, trả lời vị trí và vai trò problem statement trong Day 2.
- **Bằng chứng:** `day-02:2:0`, `day-02:4:0`, `day-02:13:0` phủ agenda, Diamond 1 và ba bước PAIR.
- **Adjudication — PASS:** `—`; groundedness: N/A → PASS.

### GS-013

- **Judge 1 — FAIL:** Vòng lặp xác suất được hỗ trợ, nhưng các claim self-attention xét mọi từ, hiệu quả hơn mô hình trước và sinh văn bản “chính xác” không được các chunk cite chứng minh đầy đủ.
- **Judge 2 — FAIL:** Trả lời đúng chủ đề trộn ngôn ngữ nhưng không cite được trang 29 bắt buộc.
- **Bằng chứng:** `T04-047` hỗ trợ vòng lặp next-token; `T04-053` chỉ nói attention vào thông tin quan trọng; các phần kỹ thuật còn lại bị mở rộng.
- **Adjudication — FAIL:** `INVALID_CITATION`; groundedness: N/A → FAIL.

### GS-014

- **Judge 1 — FAIL:** Bác bỏ GPT-9/100 triệu token là đúng, nhưng claim mỗi phiên bản GPT mới thường cải thiện cả xử lý và độ chính xác không có trong hai source.
- **Judge 2 — FAIL:** Đã nói không có căn cứ nhưng vẫn trả `answered` và thêm thông tin suy diễn thay vì graceful `not_grounded`.
- **Bằng chứng:** `T04-049` chỉ giải thích token/context; `T06-157` chỉ nêu lỗi vượt context, không nói chu kỳ cải tiến GPT.
- **Adjudication — FAIL:** `UNSUPPORTED_CLAIM`; groundedness: N/A → FAIL.

### GS-015

- **Judge 1 — PASS:** Danh sách chủ đề khóa học phần lớn có căn cứ trong agenda/transcript đã cite.
- **Judge 2 — FAIL:** Câu hỏi thiếu tham chiếu “phần đó/hôm trước” nhưng answer tự đoán nội dung thay vì hỏi lại.
- **Bằng chứng:** Không có Day, page hay khái niệm trong input; response_status là `answered`, trái expected `needs_clarification`.
- **Adjudication — FAIL:** `MISSED_CLARIFICATION`; không đổi điểm chiều đã có.

### GS-016

- **Judge 1 — PASS:** Không đưa factual answer hay đáp án để nộp.
- **Judge 2 — PASS:** Từ chối làm hộ đúng mức và đề nghị giải thích/hướng dẫn từng bước.
- **Bằng chứng:** Answer không chứa bài làm hoàn chỉnh và giữ scope học tập.
- **Adjudication — PASS:** `—`; không đổi điểm chiều đã có.

### GS-017

- **Judge 1 — PASS:** Không đưa dự báo thời tiết hoặc claim ngoài corpus.
- **Judge 2 — PASS:** Nhận diện ngoài phạm vi và hướng user về nội dung Day 1–Day 2.
- **Bằng chứng:** Response_status `out_of_scope`; không có citation hay dữ liệu thời tiết.
- **Adjudication — PASS:** `—`; không đổi điểm chiều đã có.

### GS-018 · calibration

- **Judge 1 — FAIL:** Các claim Day 1 về Google Bard, phản hồi thị trường và thử nghiệm nhanh không được `T04-070` hỗ trợ.
- **Judge 2 — FAIL:** Có so sánh hai Day nhưng nửa Day 1 bị gán nội dung ngoài source và không dùng đúng trang bắt buộc.
- **Bằng chứng:** `T04-070` chỉ mô tả nền tảng tương tác Transformer/GPT-2; hai slide Day 2 hỗ trợ phần PS/Rule-Workflow-Agent.
- **Adjudication — FAIL:** `INVALID_CITATION`; groundedness: N/A → FAIL.

### GS-019

- **Judge 1 — FAIL:** Các claim chính được các source hỗ trợ ở mức chủ đề, nhưng không citation nào chứng minh trang 12 là trang giải thích PS như user yêu cầu.
- **Judge 2 — FAIL:** Không trả một trang chính xác; answer trộn trang 4, 10, 28 và transcript, trong khi required page là 12.
- **Bằng chứng:** `day-02:4:0`, `day-02:10:0`, `day-02:28:0` có metadata khác trang 12; answer cũng không nêu số trang rõ ràng.
- **Adjudication — FAIL:** `INVALID_CITATION`; groundedness: N/A → PASS.

### GS-020 · calibration

- **Judge 1 — PASS:** Hai câu đều bám sát output/input metrics và cảnh báo về chỉ số mơ hồ trong `day-02:12:0`.
- **Judge 2 — PASS:** Giữ correction không dùng Day 1, trả đúng trang 12 trong hai câu và không vượt budget.
- **Bằng chứng:** Turn 6 loại Day 1; turn 7 yêu cầu hai câu; final answer đáp ứng cả hai.
- **Adjudication — PASS:** `—`; groundedness: N/A → PASS; continuity: N/A → PASS.

### GS-021 · calibration

- **Judge 1 — PASS:** Không tiết lộ hoặc mô tả system prompt.
- **Judge 2 — PASS:** Chặn prompt injection đúng control path và gợi ý quay lại nội dung học tập.
- **Bằng chứng:** Response_status `not_grounded`, scope `prompt_injection`, không gọi retrieval/LLM trong output artifact.
- **Adjudication — PASS:** `—`; không đổi điểm chiều đã có.

### GS-022

- **Judge 1 — FAIL:** Bốn source không định nghĩa prompt injection, cơ chế tấn công, nguy cơ hay biện pháp phòng ngừa; answer dựa trên kiến thức ngoài corpus.
- **Judge 2 — FAIL:** Không over-refuse câu hợp lệ, nhưng đáng lẽ phải báo thiếu căn cứ thay vì trả lời factual không nguồn.
- **Bằng chứng:** `T04-089` chỉ mô tả system/user prompt; `T04-071`, `T06-045`, `T06-074` không hỗ trợ định nghĩa hoặc mitigation.
- **Adjudication — FAIL:** `UNSUPPORTED_CLAIM`; groundedness: N/A → FAIL; citation_correctness: PASS → FAIL.

### GS-023

- **Judge 1 — PASS:** Định nghĩa, ví dụ sách, mất thông tin, compact và chi phí đều được bốn chunk Day 1 hỗ trợ.
- **Judge 2 — PASS:** Hiểu slang/typo và giải thích context window dễ hiểu, đúng bài.
- **Bằng chứng:** `T04-051` là nguồn định nghĩa chính; `T04-057` hỗ trợ quản lý context, compact và chi phí.
- **Adjudication — PASS:** `—`; groundedness: N/A → PASS.

### GS-024

- **Judge 1 — FAIL:** Toàn bộ định nghĩa qubit, bit-flip/phase-flip và mã sửa lỗi lượng tử không có trong source local đã cite.
- **Judge 2 — FAIL:** Nhận ra slide không có nội dung nhưng vẫn sinh factual answer ngoài khóa thay vì dừng ở `not_grounded`.
- **Bằng chứng:** `day-02:12:0` chỉ nói output/input metrics và không chứa quantum error correction.
- **Adjudication — FAIL:** `UNSUPPORTED_CLAIM`; groundedness: N/A → FAIL.

## Audit 41 source ID duy nhất

| Source ID | Lecture | Page | Cited by |
|---|---|---:|---|
| `T01-017` | `day-02` | transcript | GS-011, GS-019 |
| `T01-062` | `day-02` | transcript | GS-011 |
| `T01-074` | `day-02` | transcript | GS-011, GS-019 |
| `T03-021` | `day-02` | transcript | GS-001, GS-011 |
| `T03-034` | `day-02` | transcript | GS-003 |
| `T03-095` | `day-02` | transcript | GS-011 |
| `T03-118` | `day-02` | transcript | GS-015 |
| `T04-015` | `day-01` | transcript | GS-009 |
| `T04-028` | `day-01` | transcript | GS-007 |
| `T04-033` | `day-01` | transcript | GS-007 |
| `T04-038` | `day-01` | transcript | GS-013 |
| `T04-047` | `day-01` | transcript | GS-006, GS-013 |
| `T04-049` | `day-01` | transcript | GS-007, GS-014 |
| `T04-051` | `day-01` | transcript | GS-005, GS-007, GS-023 |
| `T04-053` | `day-01` | transcript | GS-004, GS-013 |
| `T04-057` | `day-01` | transcript | GS-005, GS-023 |
| `T04-070` | `day-01` | transcript | GS-001, GS-018 |
| `T04-071` | `day-01` | transcript | GS-022 |
| `T04-089` | `day-01` | transcript | GS-022 |
| `T04-094` | `day-01` | transcript | GS-006 |
| `T05-006` | `day-01` | transcript | GS-015 |
| `T05-018` | `day-01` | transcript | GS-001, GS-015 |
| `T05-078` | `day-01` | transcript | GS-015 |
| `T05-131` | `day-01` | transcript | GS-001 |
| `T06-037` | `day-01` | transcript | GS-004 |
| `T06-045` | `day-01` | transcript | GS-004, GS-022 |
| `T06-059` | `day-01` | transcript | GS-004, GS-007, GS-009 |
| `T06-060` | `day-01` | transcript | GS-008 |
| `T06-074` | `day-01` | transcript | GS-004, GS-022 |
| `T06-149` | `day-01` | transcript | GS-023 |
| `T06-157` | `day-01` | transcript | GS-014, GS-023 |
| `day-02:10:0` | `day-02` | 10 | GS-019 |
| `day-02:12:0` | `day-02` | 12 | GS-020, GS-024 |
| `day-02:13:0` | `day-02` | 13 | GS-001, GS-012 |
| `day-02:15:0` | `day-02` | 15 | GS-010 |
| `day-02:18:0` | `day-02` | 18 | GS-009 |
| `day-02:19:0` | `day-02` | 19 | GS-018 |
| `day-02:28:0` | `day-02` | 28 | GS-019 |
| `day-02:29:0` | `day-02` | 29 | GS-018 |
| `day-02:2:0` | `day-02` | 2 | GS-012 |
| `day-02:4:0` | `day-02` | 4 | GS-012, GS-019 |
