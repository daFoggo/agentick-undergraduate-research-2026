# Checklist viết báo cáo (áp dụng khi viết và khi rà)

Nguồn: quy tắc của người dùng; petergyang/no-ai-slop; Wikipedia "Signs of AI writing". Hai nguồn sau viết cho tiếng Anh;
ở đây chuyển sang tiếng Việt.

## A. Quy tắc của người dùng (bắt buộc)

1. Không dùng dấu gạch dài (em dash, en dash). Chỉ dùng "-".
2. Viết đoạn văn liền mạch. Không biến mọi thứ thành gạch đầu dòng hay chuỗi câu cụt. Danh sách và bảng chỉ dùng khi nội
   dung thật sự là danh sách hay phép so sánh.
3. Không dài dòng, nhưng cũng không cộc lốc.
4. Từ thường, không dùng từ khó hay kêu. Thuật ngữ tiếng Anh chỉ giữ khi phổ biến (CatBoost, SQL, verifier, backtest,
   prompt, held-out...). Có từ Việt thông dụng thì dùng từ Việt. Không có thì giữ thuật ngữ và giải thích một lần ở lần
   dùng đầu tiên.
5. Chỉ giữ thông tin giúp người đọc hiểu, đánh giá hoặc làm lại được nghiên cứu.
6. Mỗi con số phải lần được về REPORT_BRIEF.md hoặc một file đã kiểm.
7. Mỗi nhận định về một bài báo phải đến từ phần bài đã đọc. Không trích số của bài chỉ đọc tóm tắt.
8. Không viết "đầu tiên", "SOTA", "chưa ai làm".
9. Không so sánh phương pháp khi không có thực nghiệm.
10. Một khái niệm một tên trong toàn bài (xem bảng thuật ngữ ở mục D).
11. Không bịa hình. Chỗ cần hình để "[HÌNH x.y: ...]" và ghi vào assets/NEEDED.md.

## B. Mẫu câu "giọng AI" phải tránh

| Mẫu | Ví dụ tiếng Việt cần bỏ |
|---|---|
| Câu mở đầu rào đón | "Có thể nói rằng...", "Điều đáng chú ý là...", "Trong bối cảnh hiện nay..." |
| Đối lập giả "không phải X mà là Y" | "Đây không chỉ là một công cụ mà là một người bạn đồng hành" |
| "Không chỉ... mà còn..." | dùng khi chỉ cần nói một ý |
| Liệt kê ba cho đủ bộ | "nhanh chóng, chính xác và hiệu quả" khi không có ba ý thật |
| Thổi phồng ý nghĩa | "đánh dấu bước ngoặt", "minh chứng cho", "đóng vai trò then chốt", "mang tính đột phá" |
| Phân tích hời hợt đuôi câu | "..., góp phần nâng cao hiệu quả quản lý dự án" |
| Quy về nguồn mơ hồ | "nhiều nghiên cứu cho thấy", "các chuyên gia đồng ý" (không có trích dẫn) |
| Mở màn kiểu tiết lộ | "Điểm mấu chốt: ...", "Điều ít ai để ý là..." |
| Câu cụt gây kịch tính | "Và đó là tất cả." |
| Đổi từ liên tục cho cùng một thứ | lúc "hệ thống", lúc "trợ lý", lúc "công cụ" cho cùng một vật |
| Kết luận rỗng / câu tóm tắt lặp đoạn | "Tóm lại, ... là rất quan trọng" lặp lại câu đầu đoạn |
| Mục "Thách thức" công thức | "Mặc dù còn những thách thức, ... vẫn ..." |
| Lạm dụng in đậm, gạch đầu dòng | in đậm cả câu, mọi đoạn thành bullet |
| Tránh động từ "là" | "đóng vai trò là", "đóng vai trò như" thay cho "là" |
| Độ dài câu đều đều | mọi câu cùng một nhịp |
| Chuyển ý rỗng | "Bên cạnh đó", "Ngoài ra", "Hơn nữa" đầu nhiều đoạn liên tiếp |

## C. Rà soát sau bản nháp

1. Tìm dấu gạch dài (U+2014, U+2013): phải là 0.
2. Tìm các cụm: "không chỉ", "mà còn", "đóng vai trò", "then chốt", "đột phá", "vượt trội", "toàn diện", "hiệu quả cao",
   "góp phần", "có thể nói", "đáng chú ý", "bên cạnh đó", "ngoài ra", "hơn nữa", "tóm lại", "nhìn chung", "minh chứng".
3. Đếm in đậm trong thân bài; chỉ giữ ở tên bảng/hình và nhãn bắt buộc.
4. Mỗi số: đánh dấu nguồn khi rà.
5. Mỗi câu về bài báo: bài đó có trong danh sách đã đọc không.
6. Mỗi mục: phủ M0-M17 nào, có lặp mô tả của mục khác không.
7. Thuật ngữ: đối chiếu bảng mục D.

## D. Bảng thuật ngữ (một tên cho một khái niệm)

| Khái niệm | Tên dùng trong báo cáo |
|---|---|
| issue thuộc một sprint | cặp issue-sprint |
| thời điểm cắt dữ liệu | mốc t (mốc 0/25/50/75% thời lượng sprint) |
| issue được mô hình chọn để báo | cảnh báo (alert) |
| giải thích nguyên nhân | chẩn đoán |
| một nguyên nhân mô hình nêu | giả thuyết |
| bản ghi do bộ thu thập trả về | sự kiện (mã sự kiện = event_id) |
| năm truy vấn SQL | bộ thu thập |
| bước kiểm bằng code | verifier |
| hiển thị trên Plane | thẻ cảnh báo |
| người dùng bấm | Duyệt / Bỏ qua / Hoàn tác |
| nhãn độc lập M13 | nhãn của người chấm |
| issue phải chuyển sprint | tập chuyển |
| số issue dự kiến không xong | số không xong dự kiến (sức chứa còn lại suy ra từ đó) |
| agent M16 | agent hỏi đáp |
| sổ M17 | sổ cảnh báo |
| mô hình ngôn ngữ lớn | LLM |
