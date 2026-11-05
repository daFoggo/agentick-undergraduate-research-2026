# Amendment 1 cho Protocol E6: chạy nhanh (smoke)

Ngày 2026-11-05, viết trước khi chạy. Không sửa `Protocol_estimation_E6.md`.

Lý do: lần chạy đầy đủ (34.676 issue, 39 dự án) quá lâu trên CPU. Mục đích của lần chạy này chỉ là quyết định go/no-go xây tính năng "Case tương tự", không phải kết quả để công bố.

Thay đổi duy nhất so với protocol: tập con và độ dài văn bản. Mọi thứ khác (điều kiện đủ, chặn rò rỉ, M0/M1/M2, k=20, chỉ số, quy tắc kết luận, seed) giữ nguyên.

- Dự án: 5 dự án có nhiều issue đủ điều kiện nhất (chọn theo kích thước, không theo kết quả).
- Mỗi dự án: 1.500 issue mới nhất theo `creation_date` (cửa sổ liền theo thời gian; 30% cuối của cửa sổ là query).
- Văn bản cắt ở 64 token.
- Chống overfitting: không có tham số nào được tinh chỉnh, k cố định trước, chạy đúng một lần, không chọn lại tập sau khi xem kết quả. Số dự án ít (5) nên CI theo dự án rất rộng; kết quả chỉ được dùng để loại trừ trường hợp rõ ràng xấu.
- Quy tắc go: M2 có MAE macro theo dự án thấp hơn M0 ở ít nhất 4/5 dự án. Không đạt thì tính năng chỉ hiển thị case và khoảng, không gắn ước lượng điểm.
- Output: `artifacts/estimation_e6_smoke/`.
