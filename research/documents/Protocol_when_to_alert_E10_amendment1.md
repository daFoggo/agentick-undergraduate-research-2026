# Amendment 1 cho Protocol E10: chỉ số vượt kỳ vọng ngẫu nhiên

Khóa ngày 2026-11-05, sau khi đã chạy E10 một lần với chỉ số chính "số cảnh báo đúng mỗi sprint" (kết quả ở `Mo_rong_tro_ly_sprint.md` mục 5i). Amendment này **không thay thế** kết quả đó; nó thêm một chỉ số khóa trước và chạy lại **cùng dữ liệu, cùng chính sách**, ghi vào thư mục riêng.

## Lý do
Tỉ lệ nền tăng theo thời gian (0,50 ở mốc 0% đến 0,78 ở 75%): cảnh báo muộn gần như luôn "đúng" dù không dùng mô hình, nên số đúng thô phạt cảnh báo sớm. Chỉ số chính cũ chọn chưa tốt.

## Chỉ số mới
**Phần vượt kỳ vọng ngẫu nhiên** của một cảnh báo ở mốc m trong sprint s = `y` của issue − tỉ lệ y = 1 trong các issue đủ điều kiện của sprint s tại mốc m (kỳ vọng nếu chọn ngẫu nhiên). Tổng theo sprint, rồi trung bình mỗi sprint.

## Kết luận (khóa trước)
Chính sách X "tốt hơn" P0 về phần vượt kỳ vọng ngẫu nhiên chỉ khi CI 95% bootstrap ghép cặp theo sprint (2000 lần, seed 20261105) của hiệu số nằm hoàn toàn trên 0. Không đổi ngưỡng, chính sách, mốc. Chỉ số cũ vẫn được báo; hai chỉ số được trình bày cùng nhau, không chọn chỉ số theo kết quả.
