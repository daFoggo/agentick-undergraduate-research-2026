# Protocol E6: ước lượng story point theo case tương tự (baseline không LLM)

Khóa ngày 2026-11-05, trước khi chạy. Không sửa tệp này sau khi chạy: sửa đổi đi vào tệp amendment riêng. Manifest của lần chạy ghi SHA-256 của tệp này.

## Câu hỏi
Trong cùng một dự án, các case đã xong trước đó có giúp ước lượng story point của một issue mới tốt hơn trung vị của cả dự án không? Có tạo ra khoảng dự báo có độ phủ đúng không?

Phạm vi: chỉ baseline không LLM (giai đoạn B). LLM đọc case (giai đoạn C) chỉ chạy nếu kết quả ở đây cho thấy truy xuất có ích; phải khóa protocol riêng.

## Dữ liệu
Bảng `tawos_raw.issue`. Một issue đủ điều kiện nếu: `story_point > 0`; `resolution_date` và `creation_date` khác NULL; `title_changed_after_estimation`, `description_changed_after_estimation` và `story_point_changed_after_estimation` đều bằng false (giữ văn bản và điểm gốc đúng thời điểm ước lượng; giá trị NULL bị loại); độ dài `description_text` > 50 ký tự. Văn bản là `title + " " + description_text`.

Dự án đưa vào: dự án có ≥ 500 issue đủ điều kiện (số này đếm khi chạy, không dùng để chọn dự án).

## Thiết kế
- **Query:** trong mỗi dự án, sắp issue theo `creation_date`; 30% cuối là query, phần còn lại không bị loại mà chỉ làm ứng viên theo quy tắc dưới.
- **Ứng viên của một query q:** issue cùng dự án, `resolution_date < q.creation_date`, khác q. Chặn rò rỉ tương lai: mọi ứng viên đã có kết quả tại thời điểm tạo q. Query có dưới 30 ứng viên bị bỏ và đếm riêng.
- **Biểu diễn:** embedding câu đóng băng `paraphrase-multilingual-MiniLM-L12-v2`, tối đa 128 token, chuẩn hóa L2, cosine. Mô hình chọn trước (đã dùng ở research dự báo), không chọn qua kết quả.
- **Không tinh chỉnh.** Mọi tham số cố định dưới đây; không có tập validation vì không có gì để chọn.

| Mã | Dự đoán điểm | Khoảng 80% |
|---|---|---|
| M0 | trung vị story point của mọi ứng viên | phân vị 10 và 90 của mọi ứng viên |
| M1 | trung bình của mọi ứng viên | phân vị 10 và 90 của mọi ứng viên |
| M2 | trung vị của k=20 ứng viên giống nhất | phân vị 10 và 90 của k=20 ứng viên đó |

## Chỉ số
Trên thang story point gốc: MAE, MdAE; độ phủ khoảng 80% (tỉ lệ query có điểm thật nằm trong [P10, P90], đích danh nghĩa 0,80); độ rộng trung bình khoảng.

- **Chỉ số chính:** MAE của M2 trừ MAE của M0, lấy trung bình macro theo dự án.
- **CI:** bootstrap theo dự án (2000 lần, seed 20261105) cho hiệu MAE theo dự án. Với 16 dự án trở xuống, CI rộng; báo cả số dự án mà M2 thắng M0.
- **Phụ:** MdAE và độ phủ khoảng, mô tả; không có kiểm định.

## Quy tắc kết luận (khóa trước)
- "Truy xuất có ích" chỉ khi CI 95% của hiệu MAE (M2 − M0) nằm hoàn toàn dưới 0. Nếu CI chứa 0, kết luận là không phân biệt được với trung vị, và giai đoạn C không được chạy.
- Khoảng dự báo được coi là hiệu chỉnh tạm chấp nhận nếu độ phủ nằm trong 0,75–0,85 ở mức tổng; ngoài khoảng này báo là không hiệu chỉnh.
- Mọi kết quả là thăm dò trên một lần chia thời gian duy nhất; không tuyên bố tổng quát ngoài 16 dự án này.

## Hạn chế đã biết
- Story point nhiễu và không so sánh được giữa các dự án, nên chỉ đánh giá trong từng dự án.
- Loại issue có văn bản/điểm bị sửa làm lệch mẫu về các issue ít thay đổi (research dự báo trước giữ 52,5%).
- Chỉ một lần chia thời gian, không lặp. Ứng viên trùng lặp (duplicate) trong cùng dự án có thể làm kNN lạc quan; chưa kiểm soát.
- Ước lượng điểm không phải thời gian làm thực tế; đích thời gian là giai đoạn sau.
