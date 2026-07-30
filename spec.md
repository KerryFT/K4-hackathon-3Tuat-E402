# AI SPEC — VLearn Context Router · Nhóm 3 Tuất · Zone E402

**Trạng thái:** DRAFT cho CP1–CP2 · cập nhật lần cuối 30/07/2026  
**Hướng:** ☑ A — VLearn · **Loại:** ☑ Tối ưu tính năng có sẵn

> Các mục có nhãn **TODO** cần được thay bằng bằng chứng/tên thật trước checkpoint
> tương ứng. Nhóm không tự điền số hoặc quote chưa được xác minh.

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
- **TODO:** audit false positive, ghi số chính thức và ít nhất 5 mã turn minh
  họa ngắn trong `evidence/mining-results.md`.

**Đường A — khảo sát:**

- **TODO:** khảo sát ≥20 người ngoài nhóm, log toàn bộ câu hỏi và câu trả lời.
- **TODO:** n = ___; số xác nhận pain = ___; tỷ lệ = ___%.
- **TODO:** ≥5 quote nguyên văn và tên/vai người trả lời trong log nội bộ phù
  hợp quy định dữ liệu.

## §2. Impact & quyết định chọn

> Các ô “tần suất/tổn thất” phải được điền từ khảo sát, không ước lượng.

| Ứng viên | Bao nhiêu người gặp | Tần suất | Tốn gì mỗi lần | Khả thi trong hackathon | Quyết định |
|---|---:|---:|---|---|---|
| Tóm tắt toàn bài có citation | 72 user sơ bộ từ mining | TODO | TODO phút/niềm tin | Cao | Chọn làm happy path |
| Trả lời liên hệ Day 1 khi đang ở Day 2 | TODO sau audit | TODO | TODO | Vừa | Chọn làm hard path |
| Duy trì toàn bộ lịch sử chat không giới hạn | Chưa có evidence trực tiếp | TODO | Có nguy cơ context overflow | Thấp | Loại khỏi scope |

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
| TODO: sản phẩm thứ ba | TODO | TODO | TODO | TODO |

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

- **Hiện tại CP2:** ☑ Mock — UI và bốn đường trải nghiệm dùng dữ liệu giả.
- **Mục tiêu CP3:** Working ở quyết định trung tâm — một AI call thật nhận các
  đoạn đã retrieve và tạo câu trả lời có citation.
- Mock: nội dung slide, retrieval ranking và citation validator.
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

**DRAFT — phải pilot và chốt trước hạn 23:59:** đạt khi ≥80% case pass toàn bộ
chiều bắt buộc; 0 unsupported factual claim trong nhóm nguồn-sự-thật/domain; và
100% case hội thoại dài hoàn thành trong context budget. Sau khi chốt, không hạ bar.

### Kết quả chạy

| Run | Phiên bản | Pass | So với bar | Failure lớn nhất |
|---|---|---:|---|---|
| Run 01 | CP3 · `gpt-4o` · grounded cross-day | 1/1 smoke | Chưa kết luận bar 24 case | Chưa ghi nhận trong smoke; xem `eval/results-cp3.md` |

## §8. Phân công & kế hoạch

### Phân công

| Phần | Người phụ trách |
|---|---|
| Spec | TODO tên + mã HV |
| Evidence | TODO tên + mã HV |
| Prompt/retrieval | TODO tên + mã HV |
| Code | TODO tên + mã HV |
| Demo/validation | TODO tên + mã HV |

### Willing users và validation

- User 1: TODO tên/vai.
- User 2: TODO tên/vai.
- User 3: TODO tên/vai.
- CP5 cần ≥5 người ngoài nhóm; ưu tiên ba người trên.
- Ba câu hỏi: “Điều gì khó hiểu/khó chịu nhất?”; “Bạn có tin kết quả không—vì
  sao?”; “Bạn có dùng thật không—vì sao/chưa?”
- Người ghi log: TODO.

### Multi-prototype

- A: tự suy ra scope và trả lời ngay khi confidence cao.
- B: luôn bắt user chọn `Trang này / Bài này / Day khác`.
- Quyết định dự kiến: A với fallback sang B khi confidence thấp; cần validation
  trước khi chốt.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 30/07/2026 | Thu hẹp ba triệu chứng về một quyết định chọn context | Giữ lát cắt đúng format một user · một việc · một quyết định · một kết quả |
| 30/07/2026 | Dựng mock ba màn hình | Đáp ứng CP2 và kiểm tra flow trước AI integration |
| 30/07/2026 | Nối ingest, retrieval, Structured Output và citation validator vào Chat API/UI | Hoàn thiện code path CP3; lượt gọi thật được ghi bằng `scripts/smoke_cp3.py` |

