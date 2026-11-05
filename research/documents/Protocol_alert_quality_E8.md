# Protocol E8: chất lượng cảnh báo như đang vận hành

Khóa ngày 2026-11-05, trước khi chạy. Không sửa tệp này sau khi chạy: sửa đổi đi vào tệp amendment riêng.

## Câu hỏi
Với đúng quy tắc đang chạy trên Plane (chỉ issue chưa xong và chưa bị hủy, mỗi sprint tối đa ceil(20%) số issue đủ điều kiện, mốc 50% sprint), (1) trong số cảnh báo được đưa ra, bao nhiêu phần thật sự không hoàn thành? (2) mô hình có hơn một quy tắc đơn giản không?

Đây cũng là cách tính lại E1 sau khi loại các issue đã hủy (`invalid`, `won't fix`: 3,6% số trường hợp dương của E1, y = 1,00), nhưng chỉ cho mốc 50% và chính sách đang chạy, không thay thế E1.

## Dữ liệu và chính sách
- Dự đoán: `artifacts/_archive_v2_momentum/predictions/cross_project__<P>__0.5__<model>.parquet`, 14 dự án mà mô hình **chưa từng thấy lúc huấn luyện**. Trạng thái issue (`dynamic_status`) lấy từ `data/processed/snapshots.parquet` (landmark 0,5).
- Chọn cảnh báo: `research/alert_selection.py::flag_alerts` (ceil20 mặc định; nhạy cảm: k2). Mọi mô hình dùng **cùng tập issue đủ điều kiện và cùng số cảnh báo mỗi sprint**.
- So sánh: `dynamic_catboost` (đang chạy trên Plane), `business_rule` (quy tắc đơn giản), và mốc **tỉ lệ nền** (tỉ lệ y = 1 trong các issue đủ điều kiện, tương đương chọn ngẫu nhiên). `frequency` cho điểm hằng nên không xếp hạng được, không dùng.

## Chỉ số
Gộp trên mọi sprint (micro) và theo dự án: số cảnh báo; **precision** (tỉ lệ y = 1 trong cảnh báo); tỉ lệ nền; **lift** = precision / tỉ lệ nền; recall trên các trường hợp dương đủ điều kiện.

**Chỉ số chính:** hiệu số precision giữa `dynamic_catboost` và `business_rule` ở ceil20, bằng hiệu số số cảnh báo đúng trung bình mỗi sprint (cùng số cảnh báo). CI 95% bằng bootstrap ghép cặp **theo sprint** (2000 lần, seed 20261105).

## Quy tắc kết luận (khóa trước)
- "Mô hình hơn quy tắc đơn giản" chỉ khi CI 95% của hiệu số nằm hoàn toàn trên 0. Nếu CI chứa 0 thì báo là không phân biệt được.
- "Cảnh báo có giá trị" chỉ nếu lift > 1 và CI bootstrap theo sprint của lift (so với tỉ lệ nền) không chứa 1.
- Không đổi chính sách hay ngưỡng sau khi xem kết quả; biến thể thêm phải ghi là thăm dò.

## Hạn chế đã biết
Thăm dò, dùng lại dữ liệu E1, một lần chia theo dự án. Nhãn `y = 1` gồm cả issue bị rút khỏi sprint, không chỉ "không làm xong". Số sprint nhỏ mỗi dự án nên chỉ báo cáo gộp và theo dự án mô tả, không kiểm định từng dự án. `p` là điểm đã hiệu chỉnh; điểm hiệu chỉnh có thể hòa, khi đó thứ tự theo hàng đầu tiên (xác định, không phụ thuộc nhãn).
