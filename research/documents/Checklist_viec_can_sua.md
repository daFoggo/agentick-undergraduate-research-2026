# Checklist việc cần sửa và quay lại

Ngày 2026-11-05, sau review chặng "cảnh báo rủi ro + Việc giống thế này trước đây". Đánh dấu `[x]` khi xong và kiểm bằng lệnh hoặc ảnh chụp thật. Mức: **P1** nên sửa trước khi demo hoặc commit, **P2** sửa sớm, **P3** khi rảnh hoặc khi mở rộng.

## P1. Sửa trước

- [x] **Race khi hai người cùng Duyệt**: đã sửa trong `agentick-backend/app/routers/alerts.py` bằng khóa dòng trong PostgreSQL (`SELECT ... FOR UPDATE`) và test hai luồng (`test_two_approvals_at_once_keep_the_real_previous_priority`). Đối chứng: bỏ khóa thì test đỏ 2/3 lần, có khóa thì xanh 3/3. Test không tất định khi thiếu khóa (lỗi theo xác suất).
- [x] **E6 không đếm query bị bỏ** (đã sửa: `predict_project` ghi `attrs['skipped']`, `summary.json` có `skipped_queries` và `skipped_total`; test `test_queries_without_enough_candidates_are_counted_not_lost`) (`research/research/estimate_cases.py`, dòng `continue` khi dưới 30 ứng viên): protocol hứa "đếm riêng". Sửa: đếm theo dự án, ghi vào `summary.json`.
- [x] **Manifest smoke thiếu tham số** (đã sửa: manifest ghi `subset` {top, cap, max_tokens} và hash của các tệp amendment; smoke đã chạy lại vào `artifacts/estimation_e6_smoke_rerun/`) (`estimate_cases.py`, `main`): chưa lưu `E6_TOP`, `E6_CAP`, `E6_MAXLEN` và hash của `Protocol_estimation_E6_amendment1.md`. Sửa: thêm vào manifest. Kết quả smoke trong `artifacts/estimation_e6_smoke/` hiện không có manifest đầy đủ.
- [x] **Bản ghi case sai dạng làm thẻ biến mất**: không còn xảy ra theo thiết kế, vì dữ liệu nằm trong bảng PostgreSQL có schema và Alembic (không còn file JSON tự do) và dịch vụ ghi qua đúng mô hình `SimilarCasesIn`. Web vẫn ẩn thẻ khi gặp bất kỳ lỗi nào (chưa đổi).
- [ ] **Commit**: chưa commit gì. Có hai repo: `plane/` (nhánh `feat/risk-service`) và repo ngoài (`research/scripts`, `research/documents`, `research/research`, `research/tests`). Chỉ làm khi người dùng bảo.

## Đã làm sau review (2026-11-05)

- [x] **Gộp backend**: lấy lại `agentick-backend/` từ commit `5bc771c`, bỏ JWT/users/items (Plane là hệ thống chính, backend là dịch vụ bên ngoài), chuyển cảnh báo và case vào đó, dữ liệu vào PostgreSQL, `plane/apps/risk` đã xóa (sao lưu ở scratchpad). 31 test qua (gồm fuzz hợp đồng OpenAPI), ruff sạch, migration upgrade-downgrade-upgrade chạy được. Đã nhập lại 95 cảnh báo và 497 bộ case. Đã kiểm trên Plane thật: thẻ hiện, Duyệt, Duyệt lần hai trả 409, Hoàn tác trả priority về `medium`.
- [x] **Lỗi tôi gây ra khi triển khai**: chạy `docker compose` trong shell có `DATABASE_URL` trỏ vào Postgres test làm `plane-api-1` bị tạo lại với địa chỉ sai (Plane API chết khoảng 4 phút). Đã tạo lại đúng; ghi cảnh báo vào README của backend.
- [x] **Giới hạn độ dài dòng thay đổi 300 ký tự do tôi tự đặt** từ chối dữ liệu thật (dòng dài 708); nâng lên 1000 và có test hồi quy.

- [x] **Cảnh báo cho issue đã hủy hoặc đã xong** (mục 5e): quy tắc chọn cảnh báo thành hàm có test, luồng đăng gỡ cảnh báo cũ, backend có `DELETE /alerts/{id}`; trên Plane thật 0 cảnh báo ở trạng thái Cancelled hoặc Done.

## P2. Sửa sớm

- [x] **Định dạng và lint Plane** (đã chạy `oxfmt@0.35.0` và `oxlint@1.51.0`, đúng phiên bản của Plane: hai tệp sai định dạng đã sửa, lint 0 lỗi 0 cảnh báo; kiểm kiểu TypeScript vẫn chưa chạy): `activity-comment-root.tsx` (Fragment chưa thụt lề, import chưa đúng thứ tự), `main-content.tsx`, `peek-overview/view.tsx`, `similar-cases.tsx`, `risk-decision.tsx`. Chưa chạy prettier và oxlint vì repo chưa có `node_modules`; build Docker không kiểm kiểu và định dạng. Cần một lần chạy thật.
- [x] **Chưa có test cho `publish_cases.py`** (đã thêm `research/tests/test_publish_cases.py`: cỡ theo thang dự án, trường hợp mọi điểm bằng nhau trả `medium`, và `history_paths` không tạo trùng case đã có): `size_of` (điểm bằng nhau, ngưỡng P33/P80), `history_paths` (chạy lại không tạo trùng). Cân nhắc tách `size_of` sang module có test.
- [ ] **Trang case trong dự án Past cases (PCA) chưa ghi cỡ và số ngày làm**: người bấm vào chỉ thấy mô tả. Sửa: thêm dòng đầu mô tả hoặc comment.
- [ ] **Số ngày chỉ có với khoảng một phần tư issue**: kiểm trong 20 case gần nhất bao nhiêu case có ngày, giá trị có hợp lý không; nếu quá ít thì bỏ dòng ngày.
- [ ] **Bấm link case từ trong peek view** chưa kiểm (chỉ kiểm ở trang đầy đủ).
- [ ] **Bố cục điện thoại sau thay đổi chữ cuối** chưa chụp lại bằng Plane thật (chỉ trên khung xem nhanh).
- [ ] **Chưa có test riêng cho `comment_id`** của cảnh báo (trường bắt buộc nên thiếu thì 422; chưa kiểm vòng gửi và đọc).

## P3. Khi rảnh hoặc khi mở rộng

- [ ] **Giới hạn tốc độ của web Caddy** (`apps/web/caddy/Caddyfile`, `events 5000`): vẫn dùng chung một nhóm vì khóa theo IP của proxy. Trước khi chia sẻ link ngrok rộng, khóa theo IP thật và hạ giới hạn.
- [x] **Phản hồi không phải JSON** (route `/risk` chưa triển khai): hai thẻ bỏ qua thay vì lỗi parse. Mỗi trang issue vẫn gọi `/risk` hai lần khi có dịch vụ (404 khi không có dữ liệu): giữ nguyên.
- [x] **Tổng cỡ bằng 0** (đã sửa cả hai phía: backend từ chối bản ghi tổng 0 với 422, test mới; thẻ web không hiển thị khi tổng bằng 0)
- [ ] **File `decisions.jsonl` đọc toàn bộ mỗi lần xem cảnh báo**: tăng dần, chưa vấn đề ở quy mô luận văn.
- [ ] **Hai lệnh `PUT` chạy song song**: giờ là `INSERT ... ON CONFLICT DO UPDATE` trong PostgreSQL nên an toàn; mục này có thể coi là xong.
- [ ] **Script cũ trong `research/research/*.py` mặc định cổng 5432** (đúng là 15990 theo `compose.override.yaml`); `estimate_cases.py` và `publish_cases.py` đã đúng.
- [ ] **Mật khẩu DB cục bộ nằm trong mã nguồn** (`tawos_local_dev`) ở các script; chuyển sang biến môi trường nếu repo công khai.
- [ ] **Môi trường anaconda hỏng** (metadata torch bị hỏng sau một lần nâng cấp pip bị ngắt; thư mục `~orch*` trong site-packages, thuộc tài khoản `ubuntu`). Hiện dùng venv trong scratchpad; cần sửa môi trường thật nếu muốn chạy GPU.

## Hạn chế khoa học cần nhắc khi viết luận văn

- [x] **E1 tính cả issue `invalid` và `won't fix`**: đã đo lại cho chính sách đang chạy ở E8 (mục 5f): lift 1,14 so với tỉ lệ nền 0,67. E1 gốc chưa tính lại. Mục gốc: **E1 tính cả issue `invalid` và `won't fix`** là trường dương (364, tức 3,6% số trường hợp dương, y = 1,00): các con số recall và precision có thể hơi lạc quan. Tính lại E1 sau khi loại chúng (cần protocol mới hoặc amendment).
- [ ] Kết quả E6 mới là **smoke 5 dự án** (MAE 1,61 so với 1,71, thắng 3/5 dự án, CI chứa 0, quy tắc go ≥4/5 không đạt); chưa chạy E6 đầy đủ 39 dự án. Cần GPU hoặc chạy nền lâu.
- [ ] Pool case giới hạn 1.000 mới nhất mỗi dự án, nên "toàn dự án" thực ra là pool; case cũ hơn không được xét.
- [ ] Ngưỡng nhỏ/vừa/lớn (P33/P80) và ngưỡng độ chắc (≥70%) do người làm đặt, chưa kiểm chứng.
- [ ] Mức độ chắc không có "cao" vì smoke chỉ cho thấy giảm sai số khoảng 6%.
- [ ] Thẻ chưa giải thích vì sao hai issue được coi là giống nhau.
- [ ] Nguồn ngoài: đã đọc toàn văn RAG story point (arXiv 2604.03443), CoGEE (2403.08430) và đọc một phần replication (2201.05401: tóm tắt, mở đầu, bảng; chưa đọc kỹ phương pháp và kết quả). Chưa đọc: Llama3SP (trả phí), 2505.01108, RAG4Tickets, ProactiveBench, PROBE. Chỉ trích những bài đã đọc.
- [ ] Các con số E1 và E3 (recall ~59%, precision ~77–80%, A0 100%, A1 và A2 98%) lấy từ tài liệu tiến độ, chưa đối chiếu với báo cáo gốc.
- [ ] Trùng lặp (duplicate) giữa các issue cùng dự án có thể làm kNN lạc quan; chưa kiểm soát.

- [x] **Brief và thẻ không còn nói "dự báo trễ"**: chữ nhẹ hơn, không nêu thống kê (người dùng không cần). Tỉ lệ nền 67% giữ trong tài liệu và luận văn (mục 5f).
- [x] **Ngôn ngữ đồng bộ với app**: brief bot viết tiếng Anh như giao diện Plane (trước đây tiếng Việt lẫn trong app tiếng Anh). Thẻ cảnh báo và thẻ case theo bộ dịch i18n của Plane. Brief cũ tiếng Việt sẽ bị thay khi đăng lại.

## Roadmap tiếp theo (chưa làm)

- [ ] **Năng lực 2: phân loại "kẹt thật hay chờ ngoài hệ thống"** (protocol E7): định nghĩa nhãn từ dữ liệu sau mốc, thêm tool đọc comment và liên kết vào `AgentContext`, so A0 đến A3. Khảo sát: 60,5% issue mở tại mốc 50% có ≥1 comment; link kiểu chặn phủ khoảng 15% (không có thời gian tạo).
  - Đã chạy cổng E7 không LLM (xem mục 5d của `Mo_rong_tro_ly_sprint.md`): qua theo quy tắc khóa trước (ΔAUC +0,016) nhưng chủ yếu nhờ số comment, không bền theo nhãn phụ (−0,073); chưa biện minh agent LLM đọc comment.
- [x] **Policy giới hạn cảnh báo mỗi sprint** nối vào luồng (mặc định ceil20 của issue đủ điều kiện, tùy chọn k1 đến k3 và floor20); chưa có giao diện chọn K.
- [ ] **Ledger chống báo lặp, snooze, dry-run** (Task 6 của kế hoạch agent).
  - E10 (mục 5i) và amendment 1: P2 (sổ 4 mốc) hơn P0 về phần vượt kỳ vọng ngẫu nhiên (+0,031 [+0,013; +0,048]) và báo sớm hơn; chọn P2 cho chạy thật. Code đã có trong `scripts/score_sprints.py`; còn đăng lên Plane (cần khóa API).
  - E9 (mục 5h): cảnh báo đáng báo từ mốc 0% (lift 1,23); nên xem lại ở 25, 50, 75%. Đây là cơ sở cho ledger theo thời gian.
- [ ] **Chọn hành động theo ngữ cảnh** thay vì chỉ nâng priority.
- [ ] **Chip "N cảnh báo" ở trang cycle.**
- [ ] **So với estimate của chính issue** và nút "Đặt estimate": cần biết Plane có bật trường estimate cho ISP và DCP không.
- [ ] **Nối agent LLM vào Plane** thành chế độ tùy chọn qua cùng `EvidenceVerifier` và thẻ Duyệt, Bỏ qua, Hoàn tác (chỉ nếu E7 cho thấy giá trị).
- [ ] E4 nghiên cứu với người và E5 can thiệp: cần người tham gia thật, chưa lên kế hoạch.
