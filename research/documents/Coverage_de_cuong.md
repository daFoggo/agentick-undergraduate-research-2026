# Đối chiếu đề cương và module với báo cáo v2

Nguồn: đề cương 1 (`De_cuong_du_bao_som_rui_ro_sprint.md`) và đề cương 2 (`De_cuong_v2_tro_ly_canh_bao_tre_sprint.md`),
lấy bằng `git show becbdd2^:research/documents/<tên>`; module M0-M17 theo `intent.md`. Mục là mục của
`Bao_cao_tong_ket_de_tai_v2.md`. Trạng thái: **xong** (đã làm, mô tả trong báo cáo), **đã đo** (có số trong báo cáo),
**chờ** (đang xây, báo cáo có chỗ giữ), **không có kết quả** (không làm hoặc không trích được, nêu lý do).

## Đề cương 1

| Nhiệm vụ / câu hỏi | Mục báo cáo | Trạng thái |
|---|---|---|
| Mục tiêu 1: tái dựng dữ liệu tại nhiều mốc, không rò rỉ | 3.1, 3.2, 3.3 | xong (765 cặp kiểm SQL độc lập) |
| Mục tiêu 2: baseline và mô hình từ thông tin tĩnh và lịch sử | 4.1 | xong |
| Mục tiêu 3: đánh giá theo thời gian, theo dự án, theo ngân sách | 7.1, bảng 7.1, 7.2 | đã đo (chạy lại sau khi sửa lỗi; E8, E9) |
| Mục tiêu 3 (phần hiệu chuẩn: Brier, slope, intercept) | 4.1 (chỉ nêu cách hiệu chỉnh), 7.3 (điểm chưa hiệu chỉnh để cộng) | không có kết quả: số hiệu chuẩn chỉ có ở lần chạy trước khi sửa lỗi, không trích |
| Mục tiêu 4: policy phân bổ cảnh báo (controller ngoài LLM, E1) | 2.2, 7.1 (đoạn cuối) | đã đo nhưng không trích số: E1 chạy trước khi sửa lỗi, thăm dò |
| Mục tiêu 5: agent công cụ chỉ đọc, bằng chứng as-of, verifier; so A0/A1/A2 | 4.2-4.4, 8 (nhắc E3) | xong phần xây; so sánh A0/A1/A2 lặp 3 lần không có kết quả (E3 v2 chỉ 1 lần, thuộc hướng cũ) |
| Mục tiêu 6: tích hợp vào ứng dụng, ledger phản hồi | 5, 4.10 (M17) | xong trên Plane (thay Agentick); sổ cảnh báo xong, phản hồi chưa đo |
| Mục tiêu 7: công bố giới hạn | 9 | xong |
| RQ1 (lịch sử có cải thiện so với đầu sprint) | 7.1, bảng 7.1 | đã đo |
| RQ2 (sprint tương lai, dự án chưa thấy) | 7.1, bảng 7.1, 7.2 | đã đo |
| RQ3 (ngân sách cảnh báo, độ sớm) | 7.1, bảng 7.2 | đã đo (E9) |
| RQ-A (phân bổ capacity theo thời gian) | 7.1 (E1) | đã đo, không trích số (thăm dò, trước khi sửa lỗi) |
| RQ-B (agent so với template, LLM một lượt) | 8 | không có kết quả trong giai đoạn này; không so sánh phương pháp |
| RQ-C (verifier, ledger giảm khẳng định không căn cứ) | 7.2 (3 giả thuyết bị bỏ, 0 lỗi schema), 4.10 | đã đo phần verifier; sổ cảnh báo xong nhưng chưa đo báo lặp; không có negative control riêng |
| WP-A1 serving parity (E2) | - | không có kết quả: không thuộc phạm vi mới |
| WP-A4 / E4 nghiên cứu với người | 1.3, 9.4, 10.2 | không có kết quả: cần người tham gia |
| Gửi email/Telegram, dry-run, shadow mode | 10.2 (chạy bóng là hướng tiếp) | không có kết quả: email/Telegram bị cắt khỏi phạm vi; chạy bóng chưa làm |
| Sản phẩm: danh sách issue cần chú ý, brief có bằng chứng | 5.2, 5.3 | xong |

## Đề cương 2

| Nhiệm vụ / câu hỏi | Mục báo cáo | Trạng thái |
|---|---|---|
| RQ1 dự báo ở dự án chưa thấy, so với quy tắc | 7.1 | đã đo |
| RQ2 độ sớm, mốc sớm nhất đáng báo | 7.1, bảng 7.2 | đã đo (mốc 0% đạt cả hai điều kiện) |
| RQ3 ngân sách, so với tỉ lệ nền và quy tắc | 7.1, bảng 7.2 | đã đo |
| RQ4 agent chọn hành động hợp lý hơn mẫu câu (người chấm, rubric khóa trước) | 4.6 | không có kết quả: hành động không được chấm; M13 chỉ chấm nguyên nhân |
| RQ5 an toàn và vòng đời (khẳng định không căn cứ, báo lặp, chèn lệnh) | 4.3, 4.4, 7.2, 7.4, 4.10 | một phần: verifier đã đo; chèn lệnh đã thử trong 3 câu của M16; báo lặp chưa đo |
| A Phát hiện | 4.1, 7.1 | xong, đã đo |
| B Sức khỏe sprint | 4.5 (ghi chú quá tải), 4.7 (kế hoạch) | xong một phần; ghi chú quá tải chưa xuất hiện trên cảnh báo thật |
| C Giải thích có bằng chứng | 4.2-4.4, 5.3, 7.2 | xong, đã đo |
| D Hành động qua Plane, có hoàn tác | 4.6, 5.3 | xong |
| E Vòng đời / sổ cảnh báo | 4.10 | xong một phần: đếm lần thấy, điểm trước, mở lại; chưa đo hồi phục |
| F Đánh giá: replay, agent lặp >= 3, chạy bóng/thử với người | 6, 7, 9.4 | replay xong; lặp agent và thử với người không có kết quả |
| Kế hoạch giai đoạn 1-3 (hành động, sổ, sức khỏe sprint) | 4.6, 4.10, 4.7 | 1 xong; 2 xong (M17); 3 chuyển thành M14, xong |
| Kế hoạch giai đoạn 4-5 (agent A2 chọn hành động, đánh giá E3 v3) | - | không có kết quả: hướng thay bằng một lần gọi LLM + verifier |
| Kế hoạch giai đoạn 6 (chạy bóng / thử với người) | 10.2 | không có kết quả |

## Module M0-M17

| Module | Phương pháp | Hệ thống | Kết quả | Trạng thái |
|---|---|---|---|---|
| M0 Intent, dọn dẹp | - | 5.1 (bảng 5.1) | - | xong |
| M1 Trạng thái tại t, ánh xạ chặn | 3.3, 4.2 | bảng 5.1 | 9.3 (5-7% lệch) | xong |
| M2 Năm bộ thu thập | 4.2 | bảng 5.1, 5.3 | 5.3 | xong |
| M3 Chẩn đoán, verifier, mẫu câu | 4.3, 4.4 | bảng 5.1, 5.3 | 7.2 | xong, đã đo |
| M4 Backend, lọc quyền xem | 4.11 | bảng 5.1 | 5.4 (test) | xong |
| M5 Job đăng cảnh báo | 4.6 | bảng 5.1 | 7.5 | xong |
| M6 Thẻ Plane | 4.6 | 5.2, hình 5.2 | - | xong |
| M7 Chạy đầu cuối | - | bảng 5.1, 5.4 | 5.4 | xong |
| M8 Hai ghi chú | 4.5 | bảng 5.1 | 9.2, 9.3 | xong (chưa kích hoạt trên cảnh báo thật) |
| M9 Insights endpoints | 4.11 | bảng 5.1 | 7.5 | xong |
| M10 Tab Delivery risk | - | 5.2, hình 5.3 | - | xong |
| M11 Widget Home | - | 5.2, hình 5.4 | - | xong |
| M12 Your work, view | - | 5.2, hình 5.5 | 9.2 | xong (trống vì ẩn danh) |
| M13 Bộ nhãn, đo chẩn đoán | 6 | bảng 5.1 | 7.2, bảng 7.3, 7.4 | đã đo |
| M14 Kế hoạch sprint | 4.7 | bảng 5.1, hình 5.6 | 7.3, bảng 7.5, 5.2 | xong, đã đo backtest; demo phát lại sprint cũ |
| M15 Duyệt theo lô | 4.8 | bảng 5.1, hình 5.7 | 5.2, 7.5 | xong, kiểm trong trình duyệt |
| M16 Agent hỏi đáp | 4.9 | bảng 5.1, hình 5.8 | 7.4, bảng 7.6 | xong, đã đo 25 câu (người làm code chấm) |
| M17 Sổ cảnh báo | 4.10 | bảng 5.1, hình 5.2 | 7.5 | xong; mở lại và hồi phục chưa đo |
