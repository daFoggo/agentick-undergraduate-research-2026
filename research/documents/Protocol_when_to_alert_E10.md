# Protocol E10: khi nào báo thì hợp lý và có ích

Khóa ngày 2026-11-05, trước khi chạy. Không sửa tệp này sau khi chạy: sửa đổi đi vào tệp amendment riêng.

## Câu hỏi
Hiện cảnh báo chỉ chạy một lần ở mốc 50% sprint, lấy ⌈20%⌉ issue điểm cao nhất, không có ngưỡng, không xem lại. Với **cùng số cảnh báo mỗi sprint**, một chính sách xem lại nhiều mốc (0, 25, 50, 75%), không báo lặp, và chỉ báo khi issue "nhiều khả năng không xong" có cho nhiều cảnh báo đúng hơn và sớm hơn không?

## Dữ liệu
Giống E8, E9: dự đoán chéo dự án của `dynamic_catboost` tại bốn mốc (14 dự án chưa từng thấy lúc huấn luyện), `load(mốc)` của `research/alert_eval.py`. Issue đủ điều kiện tại mỗi mốc: chưa xong, chưa hủy (`flag_alerts`). Chỉ dùng sprint có đủ cả bốn mốc.

## Ngân sách chung
Mỗi sprint có ngân sách **K = ⌈20% × số issue đủ điều kiện tại mốc 50%⌉**, bằng đúng số cảnh báo của chính sách đang chạy. Mọi chính sách dưới đây dùng cùng K, nên so sánh là công bằng về khối lượng cảnh báo.

## Các chính sách
- **P0 (đang chạy):** top K theo điểm tại mốc 50%.
- **P1 (sớm):** top K theo điểm tại mốc 0%.
- **P2 (sổ nhiều mốc, có ngưỡng):** xem lại tại 0, 25, 50, 75%. Tại mốc thứ i (i = 0..3) được báo thêm tối đa ⌈K còn lại / (4 − i)⌉ issue chưa từng được báo, đủ điều kiện, có **điểm ≥ 0,5**, chọn theo điểm giảm dần (hòa: dòng đầu). Một issue chỉ được báo một lần mỗi sprint.
- **P3 (sổ nhiều mốc, không ngưỡng):** như P2 nhưng không có điều kiện điểm ≥ 0,5. Dùng để tách tác dụng của ngưỡng.
Không chính sách nào được dùng nhãn `y` để chọn.

## Chỉ số
Mỗi chính sách: số cảnh báo mỗi sprint; số cảnh báo đúng mỗi sprint (issue báo mà `y = 1`); precision; **độ sớm** = trung bình, trên các cảnh báo đúng, của (1 − mốc) tức phần sprint còn lại lúc báo.
**Chỉ số chính:** hiệu số cảnh báo đúng mỗi sprint của chính sách so với P0, bootstrap ghép cặp theo sprint (2000 lần, seed 20261105). Hiệu số độ sớm so với P0 bằng bootstrap theo sprint trên tỉ số gộp.

## Quy tắc kết luận (khóa trước)
- Một chính sách "tốt hơn P0" chỉ khi CI 95% của hiệu số cảnh báo đúng nằm hoàn toàn trên 0 **và** độ sớm trung bình không thấp hơn P0 (CI của hiệu số độ sớm không nằm hoàn toàn dưới 0).
- Tác dụng của ngưỡng: P2 so với P3 theo cùng quy tắc.
- Không đổi ngưỡng 0,5, cách chia ngân sách hay danh sách mốc sau khi xem kết quả; biến thể thêm phải ghi là thăm dò.

## Hạn chế đã biết
Thăm dò, dùng lại dữ liệu E1, `y = 1` gồm cả issue bị rút khỏi sprint. Replay không đo việc người phản ứng với cảnh báo; "sớm" chỉ là phần sprint còn lại. Cảnh báo xem lại ở mốc sau dùng điểm đã tính ở mốc đó, đúng như hệ thống chạy thật. Ngưỡng 0,5 do người làm đặt (xác suất "nhiều khả năng không xong"), không tối ưu hóa. Đây chưa phải hiệu chuẩn: điểm là điểm đã hiệu chuẩn nhưng chưa được kiểm độ khớp ở từng mốc.
