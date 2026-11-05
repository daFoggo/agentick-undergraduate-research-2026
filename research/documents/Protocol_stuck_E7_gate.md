# Protocol E7 (cổng): comment và liên kết có giúp phân biệt "kẹt thật" với "ổn" không?

Khóa ngày 2026-11-05, trước khi chạy. Không sửa tệp này sau khi chạy: sửa đổi đi vào tệp amendment riêng. Manifest của lần chạy ghi SHA-256 của tệp này.

## Mục đích và giới hạn
Đây là **cổng rẻ trước khi gọi LLM**: dùng các tín hiệu từ khóa đơn giản, không LLM. Nếu ngay cả tín hiệu thô từ comment và liên kết cũng không thêm gì so với điểm rủi ro hiện có thì chưa có lý do dùng agent đọc comment cho bài toán này; nếu có thêm thì LLM đáng thử (protocol riêng). Cổng qua **không** chứng minh LLM tốt hơn, và cổng không qua **không** chứng minh LLM kém hơn (LLM có thể hiểu ngữ nghĩa mà từ khóa bỏ sót). Kết quả thăm dò trên dữ liệu đã dùng cho E1.

## Dữ liệu
- Điểm: `artifacts/_archive_v2_momentum/predictions/cross_project__<P>__0.5__dynamic_catboost.parquet`, 14 dự án, mô hình **chưa từng thấy dự án đó khi huấn luyện** (cột `p`, nhãn `y`). Mốc 50% sprint.
- "Im lặng": issue chưa xong tại mốc (`dynamic_is_done = 0`) và `dynamic_inactive_days ≥ 3` (cùng ngưỡng mà `post_briefs.py` dùng để gọi là `status_stagnation`). Cột `dynamic_inactive_days` lấy từ `data/processed/snapshots.parquet` theo (sprint, issue, landmark).
- Nhãn "kẹt thật": `y = 1` (không hoàn thành trong sprint). "Ổn": `y = 0`. Phụ: `y_closed_only`.
- Comment: `tawos_raw.comment` với `creation_date ≤ prediction_at` của dòng đó. Liên kết: `tawos_raw.issue_link` kiểu chặn (Blocks, Blockers, Depends, Dependency) của issue, **không có thời gian tạo nên không cắt as-of; báo là hạn chế**.

## Đặc trưng (cố định, không tinh chỉnh)
Từ comment trước mốc: `n_comments`, `days_since_last_comment` (NaN nếu không có comment), cờ nhị phân theo từ khóa trong **comment cuối** và trong **mọi comment**: `waiting` (waiting, wait for, pending, on hold), `blocked` (blocked, blocker, depends on, dependency), `review` (review, reviewing, pull request, PR, merged), `question` (dấu `?` hoặc how, why, can you). Từ liên kết: `has_block_link`. Từ khóa tiếng Anh, không phân biệt hoa thường, khớp theo ranh giới từ.

## Mô hình và đánh giá
- Cơ sở B: hồi quy logistic (C=1, chuẩn hóa) trên `logit(p)` duy nhất.
- Có đặc trưng T: hồi quy logistic (C=1, chuẩn hóa) trên `logit(p)` cộng toàn bộ đặc trưng trên (NaN thay bằng 0 và thêm cờ `has_comment`).
- Đánh giá: **bỏ-một-dự-án-ra (leave-one-project-out)**: huấn luyện trên 13 dự án, chấm AUC trên dự án còn lại, trong tập "im lặng". Chỉ tính dự án có ≥ 30 issue im lặng và cả hai lớp.
- **Chỉ số chính:** ΔAUC = AUC(T) − AUC(B), trung bình macro theo dự án. CI 95% bằng bootstrap theo dự án (2000 lần, seed 20261105). Báo thêm số dự án mà T thắng B và hệ số của từng đặc trưng (chuẩn hóa) trên mô hình huấn luyện toàn bộ.

## Quy tắc kết luận (khóa trước)
- **Cổng qua** chỉ khi CI 95% của ΔAUC nằm hoàn toàn trên 0. Khi đó mới viết protocol riêng cho agent LLM đọc comment (A1, A2) so với baseline từ khóa này.
- Nếu CI chứa 0: không có bằng chứng tín hiệu từ khóa bổ sung; agent đọc comment cho bài toán "kẹt thật" chưa được biện minh, và ưu tiên chuyển sang hướng khác (chọn khi nào im lặng, chọn hành động).
- Không đổi đặc trưng, ngưỡng, hay danh sách từ khóa sau khi xem kết quả. Mọi biến thể thử thêm phải ghi là thăm dò.

## Hạn chế đã biết
- Link không cắt as-of: có thể rò rỉ nhẹ (link tạo sau mốc).
- `y = 1` gồm cả issue bị rút khỏi sprint (`removed`), không chỉ "không làm xong"; chưa tách.
- Dùng lại dữ liệu E1; chỉ một lần chia theo dự án; số dự án ít (≤ 14) nên CI rộng.
- Từ khóa tiếng Anh; comment không phải tiếng Anh bị bỏ sót.
