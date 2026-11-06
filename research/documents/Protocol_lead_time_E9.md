# Protocol E9: cảnh báo sớm đến mức nào thì còn đáng báo?

Khóa ngày 2026-11-05, trước khi chạy. Không sửa tệp này sau khi chạy: sửa đổi đi vào tệp amendment riêng.

## Câu hỏi
Đề tài là cảnh báo **sớm**. E8 chỉ đo ở mốc 50% sprint. Nếu cảnh báo ở mốc 0%, 25%, 50%, 75% thì chất lượng thay đổi ra sao, và mốc sớm nhất mà cảnh báo còn có giá trị (hơn tỉ lệ nền và hơn quy tắc đơn giản) là mốc nào?

## Dữ liệu và chính sách
Giống E8 (documents/Protocol_alert_quality_E8.md): dự đoán chéo dự án `artifacts/_archive_v2_momentum/predictions/cross_project__<P>__<mốc>__<model>.parquet` cho mốc 0, 0.25, 0.5, 0.75; trạng thái issue từ `data/processed/snapshots.parquet` tại đúng mốc; chọn cảnh báo bằng `flag_alerts` mặc định ceil20; so `dynamic_catboost`, `business_rule` và tỉ lệ nền. Cùng tập issue đủ điều kiện và cùng số cảnh báo cho mọi mô hình. Sprint nào không có đủ cả bốn mốc vẫn được tính ở các mốc có mặt; số sprint mỗi mốc được báo cáo.

## Chỉ số (mỗi mốc)
Số cảnh báo mỗi sprint, precision, tỉ lệ nền, lift và CI bootstrap theo sprint, recall, và hiệu số số cảnh báo đúng mỗi sprint giữa mô hình và quy tắc (CI bootstrap ghép cặp theo sprint, 2000 lần, seed 20261105). Cùng hàm với E8 (`research/alert_eval.py`).

## Quy tắc kết luận (khóa trước)
- Mốc "có giá trị": CI 95% của lift nằm hoàn toàn trên 1.
- Mốc "mô hình hơn quy tắc": CI 95% của hiệu số nằm hoàn toàn trên 0.
- **Mốc sớm nhất đáng báo** là mốc sớm nhất thỏa cả hai. Nếu không mốc nào thỏa cả hai thì báo "không xác định được mốc đáng báo".
- Không đổi mốc, chính sách hay ngưỡng sau khi xem kết quả; biến thể thêm phải ghi là thăm dò.

## Hạn chế đã biết
Giống E8. Thêm: ở mốc sớm số issue "đang mở" gần bằng toàn bộ sprint nên tỉ lệ nền khác mốc 50%; lift chỉ so sánh được trong cùng một mốc, không so precision thô giữa các mốc.
