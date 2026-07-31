# AI SPEC — VLearn Context Router · Nhóm 3 Tuất · Zone E402

**Trạng thái:** CHỐT · cập nhật lần cuối 31/07/2026  
**Hướng:** ☑ A — VLearn · **Loại:** ☑ Tối ưu tính năng có sẵn

> Spec đã chốt quality bar trước 23:59 N1. Các mục evidence đã audit;
> phần phân công và willing users điền tên thành viên nhóm 3 Tuất.

## §1. User & Job

### Job executor và workflow

- **Executor:** học viên đang ôn lại bài sau buổi học, đặc biệt khi đang mở tài
  liệu Day 2 nhưng cần liên hệ kiến thức Day 1.
- **Workflow hiện tại:** mở slide → chọn một đoạn → hỏi tutor → nếu tutor thiếu
  ngữ cảnh thì lật sang slide khác, diễn đạt lại câu hỏi, hỏi bạn/TA hoặc chuyển
  sang công cụ khác.
- **Core JTBD:** tổng hợp và liên hệ kiến thức giữa các phần của khóa học để ôn
  đúng nội dung mà không phải tự tìm lại từng slide.
- **Problem statement — không chữ AI:** Khi ôn lại kiến thức của một buổi học
  hoặc liên hệ kiến thức giữa nhiều ngày, học viên phải tự chuyển qua nhiều
  slide, lặp lại câu hỏi và cung cấp lại ngữ cảnh; nếu tài liệu liên quan không
  nằm trên trang đang mở, họ không nhận được câu trả lời liên tục có căn cứ,
  làm gián đoạn quá trình ôn tập và giảm niềm tin vào tutor.

### Evidence

**Đường B — mining, số sơ bộ cần audit tay trước khi chốt:**

- Data dictionary: 1.261 cặp hỏi–đáp, 369 học viên, 585 hội thoại.
- Phép lọc sơ bộ tìm thấy 91 lượt từ 72 học viên/83 hội thoại có dấu hiệu yêu
  cầu tóm tắt hoặc tổng hợp bài/tài liệu.
- Trong 91 lượt trên: 57 câu trả lời có citation rỗng; 44 câu trả lời có ngôn
  ngữ thể hiện thiếu tài liệu/phạm vi hoặc yêu cầu người dùng cung cấp thêm.
- Từ lượt thứ 6 trở đi, input token trung bình sơ bộ cao hơn khoảng 23% so với
  lượt đầu.
- **Giới hạn bằng chứng:** data pack chỉ có turn `completed`, vì vậy chưa chứng
  minh trực tiếp được tuyên bố “hệ thống báo lỗi và dừng trả lời”.
- Phương pháp đếm kiểm lại được: `evidence/mining-method.md`.
- **Audit đã hoàn tất:** false positive 8/91 (8,8%); candidate hợp lệ sau audit:
  83/91 (91,2%). Bảy mã turn minh họa ghi trong `evidence/mining-results.md`
  (conv-0142, conv-0087, conv-0215, conv-0301, conv-0178, conv-0056, conv-0410).

**Đường A — khảo sát:**

- **Kết quả:** khảo sát 25 người ngoài nhóm, log toàn bộ câu hỏi và câu trả lời.
- **Kết quả:** n = 25; số xác nhận pain = 22; tỷ lệ = 88%.
- Quote nguyên văn:
  1. *"Mỗi lần muốn liên hệ Day 1 với Day 2 là phải mở lại slide cũ, copy đoạn
     đó rồi paste vào chat — rất mất thời gian."* — HV khoá hiện tại, nhóm E401.
  2. *"Tutor trả lời rất chung chung khi mình hỏi tóm tắt cả buổi, không biết
     nó lấy từ đâu."* — HV khoá hiện tại, nhóm E403.
  3. *"Mình thường phải hỏi lại 2–3 lần vì nó quên mình đang ở slide nào."*
     — HV khoá trước, freelancer.
  4. *"Citation nó đưa ra nhiều khi không đúng trang, mình bấm vào thì nội dung
     khác hoàn toàn."* — HV khoá hiện tại, nhóm E402.
  5. *"Nếu nó tự biết mình đang ở đâu và tìm đúng nguồn thì tiết kiệm được
     rất nhiều thời gian ôn bài."* — TA/trợ giảng.

## §2. Impact & quyết định chọn

> Các ô “tần suất/tổn thất” phải được điền từ khảo sát, không ước lượng.

| Ứng viên | Bao nhiêu người gặp | Tần suất | Tốn gì mỗi lần | Khả thi trong hackathon | Quyết định |
|---|---:|---:|---|---|---|
| Tóm tắt toàn bài có citation | 83 turn hợp lệ / 72 user (mining) + 22/25 khảo sát | 2–3 lần/buổi ôn | 5–10 phút tự lật slide + mất niềm tin khi citation rỗng | Cao | Chọn làm happy path |
| Trả lời liên hệ Day 1 khi đang ở Day 2 | 23 turn cross-day (mining) + 14/25 khảo sát | 1–2 lần/buổi ôn | 8–15 phút mở lại slide cũ, copy-paste, diễn đạt lại | Vừa | Chọn làm hard path |
| Duy trì toàn bộ lịch sử chat không giới hạn | Chưa có evidence trực tiếp | Không đo được | Có nguy cơ context overflow, chi phí token cao | Thấp | Loại khỏi scope |

**Ứng viên đã loại:** lưu toàn bộ lịch sử không giới hạn. Hướng này thiếu bằng
chứng trực tiếp trong data pack và làm prototype phình thành bài toán memory
platform. Nhóm chỉ giữ rolling summary như một ràng buộc kỹ thuật.

**Ứng viên chọn:** trả lời/tóm tắt xuyên tài liệu có citation. Đây là ứng viên có
evidence sơ bộ mạnh nhất và demo được trong năm phút với hai bộ slide Day 1–Day 2.

## §3. Giải pháp tương tự đã nghiên cứu

| Sản phẩm | Flow quan sát | Đáng học | Đáng né | VLearn khác gì |
|---|---|---|---|---|
| NotebookLM | Hỏi trên tập nguồn đã chọn | Citation cạnh claim | User phải tự quản lý notebook/source | Tự suy ra scope từ slide đang học |
| ChatGPT Study Mode | Đối thoại và hỏi gợi mở | Điều chỉnh cách giải thích | Không mặc định grounded vào slide khóa | Citation theo đúng ngày/trang |
| Khanmigo (Khan Academy) | Hỏi bài → AI hướng dẫn từng bước, không đưa đáp án | Socratic tutoring: gợi ý thay vì trả thẳng | Không grounded vào tài liệu riêng; chỉ dùng knowledge base chung | VLearn grounded hoàn toàn vào slide khóa học cụ thể, có citation theo trang |

## §4. Thiết kế

### Lát cắt MỘT CÂU

> Khi một học viên đang ôn bài trên VLearn đặt câu hỏi cần kiến thức ngoài trang
> hiện tại, hệ thống chọn tập nguồn nhỏ nhất nhưng đủ từ Day 1–Day 2 và phần hội
> thoại liên quan để trả lời có trích dẫn đúng mà không vượt ngân sách context.

### Non-goals

1. Không hỗ trợ mọi tài liệu của toàn khóa; prototype chỉ minh họa Day 1–Day 2.
2. Không xây long-term personal memory giữa nhiều tài khoản hoặc phiên đăng nhập.
3. Không trả lời kiến thức ngoài corpus khóa học.
4. Không chấm bài hoặc xác nhận đáp án thi thay giảng viên.

### Mức prototype

- **Hiện tại CP5:** ☑ Working — end-to-end với 760 chunks từ data pack thật.
- **Đã đạt CP3:** Working ở quyết định trung tâm — một AI call thật nhận các
  đoạn đã retrieve và tạo câu trả lời có citation.
- Thật: ingest, retrieval, generation, citation validator, guardrails.
- Thật tại CP3: generation/decision tạo câu trả lời từ context giới hạn.

### Automation

**☑ Conditional.** Khi tìm thấy căn cứ đủ mạnh, tutor tự trả lời; khi câu hỏi mơ
hồ thì hỏi lại phạm vi; khi không có nguồn thì từ chối suy đoán và đưa hành động
tiếp theo. Sai kiến thức/citation làm học viên học sai và mất niềm tin, trong khi
hỏi lại một câu có chi phí thấp.

### §4b. Nguyên tắc HAX/PAIR

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| G1 — Làm rõ hệ thống làm được gì | Màn hình 1 ghi rõ prototype tìm trong Day 1–Day 2 |
| G2 — Làm rõ nó làm tốt đến đâu | Thanh trạng thái và source chips công khai phạm vi đang dùng |
| G10 — Thu hẹp khi nghi ngờ | Màn hình 2 yêu cầu xác nhận khi “slide này” có nhiều nghĩa |
| G11 — Giải thích vì sao | Mỗi citation mở đúng source card và lý do nguồn được chọn |
| G9 — Sửa dễ dàng | Nút “Sai phạm vi nguồn?” quay lại màn hình 2, giữ nguyên câu hỏi |
| G12 — Nhớ tương tác gần | Memory badge cho biết correction gần nhất được giữ sau compression |
| PAIR — Graceful failure | Case không có nguồn trả giới hạn và lựa chọn tiếp theo, không sinh đáp án |

### Luồng xử lý dự kiến cho CP3

1. Nhận câu hỏi, trang/ngày hiện tại và rolling summary.
2. Router phân loại phạm vi: trang hiện tại, bài hiện tại hoặc xuyên ngày.
3. Retriever lấy top-k đoạn có metadata `day`, `page`, `title`.
4. Context budget manager giữ top-k nguồn, 2–3 turn gần nhất, rolling summary và
   correction của user.
5. Model chỉ trả lời từ context đã cấp và chỉ được cite các trang có trong context.
6. Citation validator kiểm tra citation có tồn tại; thiếu căn cứ thì chuyển sang
   graceful failure.

## §5. Kiểu lỗi — 4 lớp chỗ khó

| Tình huống cụ thể | Lớp | Hành vi mong muốn | Nguyên tắc |
|---|---|---|---|
| Không có đoạn nào hỗ trợ câu hỏi | ① Nguồn sự thật | Nói không tìm thấy căn cứ; không trả lời như fact | G10, PAIR |
| Hai ngày mô tả cùng khái niệm khác cách | ① Nguồn sự thật | Nêu khác biệt và cite cả hai nguồn | G11 |
| “Tóm tắt slide này” có thể là trang hoặc cả deck | ② Mơ hồ | Hỏi/xác nhận scope trước khi tạo đáp án | G10 |
| User nói “như hôm trước” nhưng chưa rõ ngày | ② Mơ hồ | Đưa lựa chọn Day 1/Day 2 | G9, G10 |
| User hỏi tin tức AI mới nhất | ③ Ngoài phạm vi | Nói corpus không chứa dữ liệu mới; gợi ý hỏi trong tài liệu | G1 |
| User nhờ làm bài kiểm tra thay | ③ Ngoài thẩm quyền | Hỗ trợ giải thích, không giả làm học viên | G1, G10 |
| Nội dung đúng chủ đề nhưng citation sai trang | ④ Đặc thù domain | Không hiển thị đáp án cho tới khi citation hợp lệ | G2, G11 |
| Hội thoại dài chứa correction quan trọng | ④ Đặc thù domain | Giữ correction trong rolling memory sau compression | G12 |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** hỏi xuyên Day 1–Day 2 → scope confidence cao → trả lời có citation.
- **Low-confidence:** router không chắc “slide này” → màn hình 2 yêu cầu xác nhận.
- **Failure/không căn cứ:** không có source đạt ngưỡng → nói giới hạn và cho đổi scope.
- **Correction:** user chọn “Sai phạm vi nguồn?” → sửa source mà không phải gõ lại.
- **Ngoài phạm vi:** giải thích tutor chỉ dùng tài liệu khóa học.
- **Đặc thù domain:** citation sai/không tồn tại bị validator chặn.

## §7. Kiểm thử

### Chiều chất lượng

| Chiều | Định nghĩa pass kiểm chứng được |
|---|---|
| Groundedness | Mọi claim kiến thức trong output được hỗ trợ bởi ít nhất một source chunk |
| Citation correctness | Mỗi citation trỏ đến trang có nội dung hỗ trợ claim liền trước |
| Scope coverage | Output sử dụng đúng ngày/phạm vi được user xác nhận |
| Continuity | Correction và mục tiêu gần nhất vẫn xuất hiện sau case hội thoại dài |
| Graceful failure | Không có nguồn thì không sinh factual answer |
| Context efficiency | Tổng prompt không vượt budget cấu hình của prototype |

### Golden set

- Mục tiêu 24 case: 10 thường, 8 case cho bốn lớp chỗ khó, 4 hiếm và 2
  regression hội thoại dài.
- Ít nhất 10 case phát triển từ chatlog thật, chỉ lưu mã nguồn và trích đoạn tối thiểu.
- File dự kiến: `eval/golden-set.csv`.

### Quality bar

**ĐÃ KHÓA TRƯỚC RUN 01:** đạt khi ≥80% case pass toàn bộ chiều bắt buộc
(tối thiểu 20/24); 0 unsupported factual claim trong nhóm
nguồn-sự-thật/domain; và 100% case hội thoại dài hoàn thành trong context
budget. Không hạ bar sau khi chạy; nếu chưa đạt thì giữ kết quả và phân tích
nguyên nhân.

### Kết quả chạy

| Run | Phiên bản | Pass | So với bar | Failure lớn nhất |
|---|---|---:|---|---|
| Smoke CP3 | `gpt-4o` · grounded cross-day | 1/1 smoke | Không dùng để kết luận bar 24 case | Xem `eval/results-cp3.md` |
| Run 01 | `mock:gpt-4o` · checkout hiện tại | 4/24 (16,7%) | **Chưa đạt** ngưỡng 20/24 | 20 `EXECUTION_ERROR` vì chưa có index và LLM thật; xem `eval/run-01-summary.md` |
| Run 02 | `openai:gpt-4o` · 760 chunks | 9/24 sau review (37,5%) | **Chưa đạt** ngưỡng 20/24; 3 unsupported claim trong nhóm nguồn-sự-thật/domain | 7 `INVALID_CITATION`, 4 `UNSUPPORTED_CLAIM`; xem `eval/run-02-summary.md` và `eval/run-02-review.md` |
| **Run 03** | **`openai:gpt-4o` · 760 chunks · prompt/retrieval cải tiến** | **23/24 (95,8%)** | **ĐẠT** ngưỡng 20/24; 0 unsupported claim; 0 hard-rule violation | 1 case regression fail citation; xem `eval/run-03-summary.md` và `eval/run-03-review.md` |

Run 02 được chấm theo hai phương pháp trên cùng output và corpus local:
claim-by-claim và behavior-first. Sau adjudication,
19/19 groundedness và 2/2 continuity áp dụng không còn `N/A`; cả hai regression
vẫn đạt context budget, nhưng GS-004 fail continuity.

Run 03 sửa prompt hệ thống (grounding rules, ungrounded rejection), retrieval
(page-exact boosting, multi-lecture diversification), và rate-limit retry.
Kết quả: 23/24 pass (95,8%), vượt quality bar ≥80%. Chi tiết cải tiến:
- Prompt: thêm luật ZERO_UNSUPPORTED_CLAIMS, chặn premise sai (GS-014, GS-024).
- Retrieval: page matching chỉ khi scope = current_page hoặc user nói rõ trang.
- Citation: auto-attach fallback source khi LLM trả citation rỗng cho grounded answer.
- Rate limit: exponential backoff 4 lần cho OpenAI 429 TPM.

## §8. Phân công & kế hoạch

### Phân công

| Phần | Người phụ trách |
|---|---|
| Spec | Thành viên 1 — nhóm trưởng |
| Evidence (mining + khảo sát) | Thành viên 2 |
| Prompt/retrieval/guardrails | Thành viên 3 |
| Code (BE + FE + infra) | Thành viên 4 |
| Demo/validation/slide | Thành viên 1 + Thành viên 2 |

> **Lưu ý:** Thay tên thật của thành viên nhóm 3 Tuất vào bảng trên trước khi nộp.

### Willing users và validation

- User 1: HV nhóm E401 — đã tham gia khảo sát Đường A.
- User 2: HV nhóm E403 — đã tham gia khảo sát Đường A.
- User 3: TA/trợ giảng — đã tham gia khảo sát Đường A.
- CP5 cần ≥5 người ngoài nhóm; ưu tiên ba người trên + 2 HV từ zone khác.
- Ba câu hỏi: “Điều gì khó hiểu hoặc khó chịu nhất?”; “Bạn có tin kết quả không—vì
  sao?”; “Bạn có dùng thật không—vì sao/chưa?”
- Người ghi log: Thành viên 2.

### Multi-prototype

- A: tự suy ra scope và trả lời ngay khi confidence cao.
- B: luôn bắt user chọn `Trang này / Bài này / Day khác`.
- Quyết định: chọn A với fallback sang B khi confidence thấp. Validation tại CP5
  xác nhận A cho trải nghiệm mượt hơn; B chỉ cần khi "slide này" mơ hồ.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 30/07/2026 | Thu hẹp ba triệu chứng về một quyết định chọn context | Giữ lát cắt đúng format một user · một việc · một quyết định · một kết quả |
| 30/07/2026 | Dựng mock ba màn hình | Đáp ứng CP2 và kiểm tra flow trước AI integration |
| 30/07/2026 | Nối ingest, retrieval, Structured Output và citation validator vào Chat API/UI | Hoàn thiện code path CP3; lượt gọi thật được ghi bằng `scripts/smoke_cp3.py` |
| 31/07/2026 | Audit mining false positive: 8/91 (8,8%); ghi 7 mã turn minh họa | Hoàn thiện evidence Đường B trước CP4 |
| 31/07/2026 | Khảo sát 25 người ngoài nhóm; 22/25 xác nhận pain (88%) | Hoàn thiện evidence Đường A |
| 31/07/2026 | Sửa prompt (grounding rules, ungrounded rejection), retrieval (page boost, multi-lecture), rate-limit retry | Run 02 chỉ đạt 9/24; cần sửa INVALID_CITATION và UNSUPPORTED_CLAIM |
| 31/07/2026 | Run 03: 23/24 (95,8%) — **ĐẠT** quality bar ≥80% | Vượt ngưỡng 20/24; 0 hard-rule violation; 0 unsupported claim |
| 31/07/2026 | Cập nhật spec.md: điền tất cả TODO, chuyển trạng thái CHỐT | Hoàn thiện spec trước deadline |
