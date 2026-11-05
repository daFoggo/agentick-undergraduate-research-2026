# Tích hợp mô hình dự báo và agent vào Plane

Tài liệu kỹ thuật làm nền cho phần báo cáo. Trạng thái: 2026-11-05. Mã: `agentick-backend/` (backend FastAPI + PostgreSQL, ở gốc repo), phần giao diện và cấu hình ghép trong `plane/` (bản fork `daFoggo/plane`, nhánh `feat/risk-service`), và `research/scripts/`.

## 1. Mục tiêu

Có một giao diện quản lý dự án mã nguồn mở (Plane) để (a) hiển thị dữ liệu công khai TAWOS ở dạng sprint/issue, làm chỗ thu thập và đối chiếu minh chứng, (b) gắn dự báo rủi ro sprint, (c) cho agent đề xuất hành động và người duyệt.

## 2. Kiến trúc

Ba lớp. **Nghiên cứu (offline)** chấm điểm và dựng brief từ `tawos_raw`. **Plane** là nơi hiển thị và là bảng điều khiển của người dùng. **Backend `agentick-backend`** (dịch vụ bên ngoài, Plane là hệ thống chính) lưu cảnh báo trong PostgreSQL, thực hiện hành động khi người dùng bấm nút Duyệt / Bỏ qua / Hoàn tác trên trang issue, và ghi nhật ký quyết định. Service chỉ nói chuyện với Plane qua REST, không đọc DB của Plane; quyền xem do Plane quyết định (chuyển tiếp cookie phiên của người dùng). Luồng chi tiết và cấu hình: `plane/apps/risk/README.md`.

## 3. Các quyết định thiết kế

| Quyết định | Lý do | Phương án đã bỏ |
|---|---|---|
| Dùng Plane làm giao diện, không tự viết frontend | Plane có sẵn sprint (cycle), issue, board; tự viết là chi phí lớn mà không thêm giá trị nghiên cứu | Taiga, OpenProject (khác stack, Taiga chậm phát triển) |
| Backend FastAPI riêng (`agentick-backend`), không nhúng vào Django của Plane, không có tài khoản riêng (người dùng là chủ phiên Plane) | Dependency nặng (catboost) không đụng vào Plane; fork Plane chỉ còn phần web, merge upstream ít xung đột; Plane vẫn là nguồn sự thật về người dùng và quyền | Nhúng vào `apps/api`; để backend tự quản JWT |
| Chấm điểm offline, chưa chạy model trong service | Chưa có dữ liệu live; tính đặc trưng live là việc nghiên cứu riêng | Đưa `score_bundle` vào service |
| Brief theo mẫu cố định, kiểm bằng `EvidenceVerifier`, không gọi LLM | Thực nghiệm E3 cho thấy mẫu không LLM đạt ngang LLM trên các metric dẫn chứng | Agent nhiều bước |
| Nút Duyệt / Bỏ qua / Hoàn tác ngay dưới comment của bot (sửa giao diện web của fork) | Tương tác thấy ngay, một cú bấm, hoàn tác được; quyền kiểm bằng phiên Plane nên không có đăng nhập riêng | Duyệt bằng nhãn Plane (bước kém trực quan, đã bỏ); bấm nút trong comment (Plane không cho) |
| Brief và mô tả issue đọc được (tiếng Việt, dẫn chứng bằng chữ, không mã) | Người đọc không phải tự dịch mã; mô tả TAWOS mất xuống dòng và nhân đôi dấu nháy nên được dựng lại (`research/scripts/tawos_text.py`) | Giữ nguyên văn thô; link sang Jira (bỏ, xem ngay trong Plane) |
| Một hành động duy nhất: nâng priority lên High | Đảo ngược được, rủi ro thấp; đủ chứng minh luồng đề xuất → duyệt → thực hiện | Chuyển sprint, đổi người phụ trách |
| Tài khoản bot riêng (`agentick-bot`, quyền member) | Người dùng phân biệt agent với người; bot không có quyền admin | Dùng khóa của admin |

## 4. Phát hiện kỹ thuật (từ spike P0 và P3)

1. Plane **khóa cycle đã kết thúc** (`CYCLE_COMPLETED`): không thêm issue, không sửa. Cách vòng: tạo cycle ngày tương lai, gắn issue, rồi sửa ngày về quá khứ.
2. Một work item chỉ thuộc **một cycle**. Issue chuyển tiếp qua nhiều sprint chỉ giữ điểm của sprint cuối.
3. Plane không nhận lịch sử changelog (9,2 triệu dòng) và `created_at` là giờ nạp. Dẫn chứng `event_id` vẫn lấy từ `tawos_raw`.
4. Luồng webhook + nhãn đã bị thay bằng nút trên giao diện (webhook phải tự dựng chống lặp vì chính ghi của bot sinh thêm webhook).
5. Container web của Plane giới hạn 300 request/phút mỗi IP; một lần tải trang cần hàng trăm chunk nên qua tunnel bị HTTP 429. Đã nâng lên 5000.
6. Tên project Plane không được có ký tự đặc biệt (kể cả dấu gạch nối).
7. Bản self-host này **không có** OAuth app và agent @mention (không có bảng/mã tương ứng); điểm mở rộng thật là webhook, REST API và MCP server.

## 5. Kết quả thử nghiệm (project IS, held-out)

| Mục | Giá trị |
|---|---|
| Model | `cross_project__IS__0.5__dynamic_catboost` (IS không có trong tập huấn luyện); `run_hash` khớp file kết quả gốc, 643 dòng test |
| Sprint / work item trong Plane | 65 cycle / 475 work item |
| Cảnh báo (top `ceil(20%)` mỗi sprint) | 159 dòng theo sprint; 95 work item mang nhãn sau khi gộp issue chuyển tiếp |
| Recall trung bình theo sprint, ngân sách 20% | 0,396 (chỉ IS; con số 53% trong báo cáo là của 14 project) |
| Brief đã đăng | 95/95 qua `EvidenceVerifier`, 0 bị chặn |
| Kiểm thử luồng duyệt | Thử tay trên giao diện: Duyệt → priority High + comment bot; Hoàn tác → trả lại medium; Duyệt lại được. 17 test tự động cho service (auth, trạng thái, hoàn tác). Chưa thử tay Bỏ qua; giao diện chưa có test tự động |

## 6. Giới hạn và mối đe dọa tới tính hợp lệ

- Màn hình Plane chỉ là snapshot; số liệu nghiên cứu theo membership từng thời điểm vẫn nằm ở file điểm (mục 4.2).
- Trạng thái trong Plane là trạng thái **tại mốc 50%**; nhãn kết quả `y` không được đưa lên Plane.
- Chưa có chấm điểm live: đặc trưng phải dựng lại từ lịch sử hoạt động của Plane, chưa kiểm chứng.
- Nhật ký quyết định mới chỉ có cấu trúc; chưa có đủ dữ liệu để đánh giá tỷ lệ duyệt.
- Brief mẫu ngắn: chỉ nêu trạng thái, số ngày không hoạt động và 3 sự kiện gần nhất.

## 7. Tái lập

```bash
cd research
PYTHONPATH=. python scripts/score_sprints.py IS scores.csv
PLANE_API_KEY=... TAWOS_PG_PASSWORD=... python scripts/import_to_plane.py scores.csv "IS heldout pilot" ISP
PYTHONPATH=. PLANE_API_KEY=... PLANE_BOT_KEY=... TAWOS_PG_PASSWORD=... python scripts/post_briefs.py scores.csv ISP
```

Yêu cầu: Plane chạy (compose của Plane + `docker-compose.risk.yml`), tài khoản bot (README của `agentick-backend`), và build ảnh web của fork (`plane-web-risk:dev`).
