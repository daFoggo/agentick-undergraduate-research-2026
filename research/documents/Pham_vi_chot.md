# Phạm vi chốt: trợ lý cảnh báo trễ sprint trên Plane

Ngày 2026-11-05. Nguyên tắc: một tính năng chỉ ở lại nếu nó giúp **phát hiện sớm hoặc tránh được trễ deadline và rủi ro** cho người quản lý. Còn lại cắt, dù đang thịnh hành.

## Mục tiêu
Giúp đội biết sớm sprint và issue nào có nguy cơ trễ, hiểu vì sao, làm gì được, và không bị làm phiền bằng cảnh báo vô ích. Người quyết định, hệ thống chỉ đề xuất và có thể hoàn tác.

## Sản phẩm gồm 6 phần
| # | Phần | Người dùng thấy gì | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| A | Phát hiện | Vài issue có rủi ro cao hơn, ở mốc 0/25/50/75% sprint, tối đa vài cảnh báo mỗi sprint | Xong (mốc 50%) | E8 lift 1,14; E9 lift 1,23 ở mốc 0% |
| B | Sức khỏe sprint | Ở trang cycle: bao nhiêu issue đang cảnh báo; sprint nhận nhiều hơn mức đội thường xong bao nhiêu (so lịch sử đội) | Chưa làm | Mô hình không hơn lịch sử đội ở cấp sprint, nên chỉ hiển thị thống kê, không dự báo |
| C | Giải thích | Brief có bằng chứng: trạng thái, bao ngày im lặng, thay đổi gần nhất | Xong (mẫu câu) | E3 |
| D | Hành động | Mỗi cảnh báo kèm một hành động cụ thể từ tập nhỏ gắn với nguyên nhân trễ (nhắc người phụ trách, gán người, tách nhỏ, chuyển sprint sau, tăng ưu tiên); bấm Duyệt thì Plane thực hiện, có hoàn tác | Xong phần thực thi: 3 hành động chạy trong Plane và hoàn tác được (tăng ưu tiên, nhắc người phụ trách bằng comment, chuyển sang cycle kế: kiểm trên Plane thật, Plane từ chối cycle đã kết thúc); gán người và tách nhỏ là gợi ý. Baseline mẫu câu chọn hành động; agent chưa nối |
| E | Vòng đời cảnh báo | Không báo lặp, xem lại ở mốc kế, thấy "đã ổn" hoặc "xấu đi", ghi kết cục (cuối sprint xong chưa) | Chưa làm | Cần để đo giá trị thật |
| F | Đánh giá | Replay trên TAWOS, đánh giá agent, chạy bóng hoặc thử với người | Replay xong; còn lại chưa | E8, E9, E3 |

## LLM dùng ở đâu
Chỉ ở phần C và D: viết brief dễ đọc và soạn nội dung hành động (ví dụ lời nhắc gửi người phụ trách). Xác suất, chọn cảnh báo và quyền ghi **không** do LLM quyết. Giá trị LLM so với mẫu câu chưa được chứng minh (E3: mẫu câu ngang LLM), nên LLM là chế độ tùy chọn và phải đo so với mẫu câu.

## Cắt khỏi phạm vi (không liên quan trực tiếp đến giảm trễ, hoặc bằng chứng không ủng hộ)
- Agent đa vai, đội agent, agent "bộ nhớ tự tiến hóa": đắt, chưa có bằng chứng cho bài toán này.
- Ước lượng story point chính xác: kNN chỉ hơn trung vị ~6%, không giúp tránh trễ; giữ thẻ "việc giống nhau" như thông tin phụ, không đầu tư thêm.
- Đọc ngữ nghĩa comment bằng LLM: E7 cho thấy tín hiệu chủ yếu là số comment.
- Phát hiện issue trùng lặp: tiện ích chung, không đúng mục tiêu trễ deadline.
- Dự báo "sprint trễ khi nào" ở cấp sprint bằng mô hình: không hơn lịch sử đội.
- Huấn luyện lại từ phản hồi bấm Duyệt/Bỏ qua: chưa đủ dữ liệu, rủi ro nhiễu.

## Việc cần làm theo thứ tự
1. **D (hành động):** chốt tập hành động nhỏ; hành động ghi vào Plane chỉ qua Duyệt, có hoàn tác. Quan trọng nhất vì cảnh báo không kèm việc làm được thì ít giúp tránh trễ.
2. **E (vòng đời):** ledger, xem lại ở các mốc, ghi kết cục.
3. **B (sức khỏe sprint):** chip và thống kê ở trang cycle.
4. **Agent (LLM) cho C và D** trong chế độ tùy chọn, đo so với mẫu câu, báo chi phí.
5. **F:** đánh giá agent lặp ≥3 lần, thử chèn lệnh qua comment, chạy bóng hoặc thử với người.
