# Amendment 1 cho Protocol E11: chạy thử nhỏ trước, có trần chi phí

Khóa ngày 2026-11-05, trước lần chạy nào của E11 (lần chạy đầy đủ đầu tiên đã bị dừng giữa chừng vì quá tốn, không ghi kết quả).

Chạy theo hai bước, mỗi bước ghi vào thư mục riêng:
1. **Chạy thử:** 10 cảnh báo (mẫu ngẫu nhiên seed 20261105), một model `openai/gpt-oss-120b`, 1 lần lặp, kiểm tra chèn lệnh trên cả 10, trần chi 0,05 USD (`E11_BUDGET_USD`). Mục đích: xem đầu ra thật có hợp lý và hợp lệ không, ước chi phí.
2. Chỉ nếu chạy thử không lỗi thiết kế và tổng chi phí ước tính cho lần đầy đủ còn dưới 1 USD, mới chạy đầy đủ theo protocol gốc (110 cảnh báo, hai model, 3 lần lặp) hoặc một phần nhỏ hơn có ghi rõ.
Ngưỡng đạt và chỉ số giữ nguyên như protocol gốc; ở bước 1 chúng chỉ để tham khảo vì mẫu nhỏ.
