# Mở rộng: trợ lý sprint chủ động

Ngày 2026-11-05. Tổng kết sau đợt research bổ sung. Chưa có kết quả thực nghiệm mới trong tài liệu này; mọi trạng thái "chưa làm" đều chưa chạy. Nguồn ngoài chỉ đọc qua tóm tắt tìm kiếm, cần đọc toàn văn trước khi trích dẫn.

## 1. Bài toán

Một trợ lý sprint chủ động, người luôn quyết định (duyệt, bỏ qua, hoàn tác). Ba năng lực và một lớp chung.

| # | Năng lực | Đầu ra | Trạng thái |
|---|---|---|---|
| 1 | Dự báo rủi ro sprint | Điểm và hạng rủi ro của issue tại mốc 50% sprint | Xong, đã đo (E1, theo tài liệu: recall sớm ~59%, precision ~77–80%) |
| 2 | Giải thích ca im lặng | "Kẹt thật" hay "chờ ngoài hệ thống / xong ngầm", kèm bằng chứng từ comment và liên kết | Chưa làm |
| 3 | Tư vấn ước lượng theo case | Thời gian hoặc khối lượng dự kiến dạng khoảng, kèm các case tương tự | Chưa làm |

Lớp chung: policy giới hạn K cảnh báo mỗi sprint và quyền im lặng (đã đo, chưa nối Plane); `EvidenceVerifier` (xong); Duyệt/Bỏ qua/Hoàn tác trong Plane (xong); chọn hành động theo ngữ cảnh và ledger chống báo lặp (làm sau).

Ràng buộc từ kết quả cũ: trên bài toán hiện tại mẫu câu A0 ngang hoặc hơn LLM (E3 v2, ceiling effect). Mỗi năng lực mới phải thắng baseline đơn giản (median, kNN, mẫu câu) thì mới đáng dùng LLM; kết quả âm vẫn được báo.

## 2. Thông tin cần truy xuất

Nguồn: PostgreSQL schema `tawos_raw`. Mọi truy xuất phải **as-of**: chỉ dùng bản ghi có thời gian không sau mốc dự báo của issue hỏi.

| Bảng | Trường dùng | Cho năng lực | Ghi chú |
|---|---|---|---|
| `issue` | `title`, `description_text`, `type`, `priority`, `status`, `project_id`, `sprint_id`, `creation_date` | 1, 2, 3 | Văn bản có thể bị sửa sau thời điểm ước lượng: cờ `title_changed_after_estimation`, `description_changed_after_estimation` cho biết văn bản gốc còn đúng hay không (research cũ chỉ dùng 52,5% issue "chưa sửa") |
| `issue` | `story_point`, `story_point_changed_after_estimation`, `estimation_date` | 3 | Đích ước lượng loại 1. Điểm nhiễu, khó so sánh giữa dự án |
| `issue` | `resolution_date`, `resolution_time_minutes`, `in_progress_minutes`, `total_effort_minutes`, `timespent` | 3 | Đích ước lượng loại 2 (thời gian). Cần kiểm tra chất lượng, độ phủ và giá trị âm/bất thường |
| `issue` | `resolution`, `status`, `resolution_date` | 2 | Nhãn kết quả sau mốc để định nghĩa "kẹt thật" so với "xong ngầm" |
| `sprint` | `start_date`, `end_date`, `activated_date`, `complete_date`, `state` | 1, 2, 3 | Mốc 50%, cắt as-of, chia theo thời gian |
| `change_log` | `field`, `from_string`, `to_string`, `creation_date`, `issue_id` | 1, 2 | Dùng `*_string`, không dùng `*_value` (luôn NULL). Trường hiểu được: status, Sprint, Story Points, priority, resolution, assignee |
| `comment` | `comment_text`, `creation_date`, `author_id`, `issue_id` | 2, 3 | 1.518.327 dòng. `comment_code` tách phần mã. Phải lọc theo `creation_date <= mốc`. Có thể chứa prompt injection |
| `issue_link` | `name`, `direction`, `target_issue_id` | 2 | 246.587 dòng. Tên trùng nghĩa cần gộp: Blocks, Blockers, Depends, Dependency (khoảng 33 nghìn); Duplicate, Relates, Reference, Cloners là loại khác. Không có thời gian tạo link: cần quy ước as-of riêng |

Số liệu khảo sát sơ bộ (toàn bộ dữ liệu, chưa cắt theo mốc 50%):
- 43.475 issue có sprint; 30.410 có sprint và story point; 37.826 có mô tả trên 50 ký tự.
- 33.197 issue trong sprint có ít nhất 1 comment; 15.508 có ít nhất 1 liên kết.
- Chưa đo: số comment và link **trước mốc 50%** cho nhóm issue rủi ro cao. Đây là điều kiện sống còn của năng lực 2.

### Truy xuất theo năng lực

1. **Năng lực 1** (đã có): `AgentContext` as-of; changelog, trạng thái, số ngày không hoạt động, hạng và điểm rủi ro.
2. **Năng lực 2:** thêm hai tool chỉ đọc cho agent: đọc comment đến mốc, đọc liên kết của issue và trạng thái issue đích tại mốc. Nội dung comment luôn xử lý như dữ liệu không tin cậy.
3. **Năng lực 3:** (a) văn bản của issue hỏi; (b) tập case ứng viên: issue đã **xong trước ngày của issue hỏi**, cùng dự án (chính) hoặc khác dự án (kiểm tra chuyển dự án); (c) đích của từng case; (d) embedding câu của văn bản case.

## 3. Rủi ro dữ liệu và phương pháp

- Văn bản không giúp dự báo rủi ro (đã đo, khoảng tin cậy chứa 0). Giá trị của văn bản chỉ được giả định ở phần giải thích và tư vấn ước lượng, chưa được chứng minh.
- Story point nhiễu; replication của GPT2SP cho thấy baseline trung vị khó thắng, nhất là khi chuyển dự án. Nếu kNN không hơn median thì thông điệp là "cho xem case và khoảng", không phải "dự đoán chính xác hơn".
- Rò rỉ tương lai ở truy xuất case: case phải xong trước ngày hỏi; link không có thời gian nên phải nêu quy ước (dùng link nếu issue được tạo trước mốc, hoặc chỉ dùng loại liên kết thường tạo ngay khi lập issue) và báo là hạn chế.
- Nhãn "kẹt thật" phải tự định nghĩa từ dữ liệu sau mốc, có thể nhiễu; phải ghi định nghĩa và kiểm tay một mẫu.
- Ít comment trước mốc 50% sẽ làm năng lực 2 không khả thi. Nếu vậy chuyển sang năng lực "chọn khi nào im lặng".

## 4. Kế hoạch triển khai

| Giai đoạn | Việc | Đầu ra | Điều kiện qua |
|---|---|---|---|
| 0 | Khảo sát dữ liệu cắt theo mốc (độ phủ comment, link, đích ước lượng) | Số liệu trong tài liệu này, mục 5 | Đủ độ phủ để tiếp tục |
| A | Protocol E6 ước lượng theo case: đích, chia thời gian, baseline, chỉ số, khóa trước | `Protocol_estimation_E6.md` có hash | Khóa trước khi chạy |
| B | Baseline không LLM: median, mean, kNN embedding, khoảng dự báo; đo MAE, MdAE, độ phủ khoảng | Báo cáo B | kNN so với median |
| C | LLM đọc case truy xuất (RAG), so với kNN thuần, ≥3 lần chạy | Báo cáo C | Chỉ tiếp nếu thắng kNN |
| D | Panel "Case tương tự" ở trang issue Plane, thêm vào dịch vụ risk | Playwright | Hiển thị đúng, có link case |
| E | Protocol E7 phân loại kẹt; mở rộng `AgentContext`; so A0–A3 | Báo cáo E | Có kết quả dù âm |
| F | Chọn hành động theo ngữ cảnh, policy K, ledger | Báo cáo F | Làm sau cùng |

Quy ước E-number: E1 policy replay, E2 serving, E3 agent kỹ thuật, E4 nghiên cứu với người, E5 can thiệp (đã dùng); E6 ước lượng theo case, E7 phân loại kẹt (mới).

## 5. Khảo sát dữ liệu giai đoạn 0

Chạy 2026-11-05, chỉ đọc, trên `tawos_raw` và `data/processed/snapshots.parquet` (landmark 0,5; 22.147 cặp sprint-issue; `y=1` là kết thúc không hoàn thành; "mở" là `dynamic_is_done=0`). Truy vấn chạy tay, chưa là script lưu trong repo.

**Năng lực 2: độ phủ comment và liên kết tại mốc 50%**

| Nhóm | Số cặp | Có ≥1 comment trước mốc | Có link kiểu chặn* | Có link bất kỳ* |
|---|---|---|---|---|
| Mở tại mốc | 15.153 | 60,5% | 13,6% | 50,3% |
| Mở và cuối cùng không xong (`y=1`) | 10.125 | 62,7% | 15,5% | 54,2% |
| Mở và cuối cùng xong (`y=0`) | 5.028 | 56,0% | 9,8% | 42,3% |

Trung vị 1 comment/issue; trong số issue có comment, trung vị 479 ký tự tổng. *Link không có thời gian tạo nên chưa cắt as-of; phải coi là hạn chế. Kết luận: comment đủ phủ để làm năng lực 2 (khoảng 6 trên 10 issue rủi ro có comment trước mốc); link kiểu chặn chỉ phủ khoảng 15%, nên là bằng chứng bổ sung chứ không là nguồn chính.

**Năng lực 3: đích ước lượng**

| Đại lượng | Kết quả |
|---|---|
| Issue đã giải quyết | 352.632 (trong sprint: 40.902) |
| `resolution_time_minutes` | đủ cho mọi issue đã giải quyết, không âm, khớp `resolution_date − creation_date` (0 trường hợp lệch trên 1 ngày); phân vị 10/50/90 là 0,47 / 37,3 / 1.322 ngày |
| `in_progress_minutes` > 0 | 88.070 issue |
| `total_effort_minutes` > 0 | 151.254 issue |
| `timespent` > 0 | 10.226 issue |
| Story point > 0, đã giải quyết, mô tả > 50 ký tự | 49.121 issue; 16 dự án có ≥ 500 issue như vậy |
| Phân bố story point (top) | 1: 14.068; 2: 11.984; 3: 8.885; 5: 7.503; 8: 5.232; 4: 4.226; 0,5: 1.502; 13: 1.327 |

Nhận xét: thời gian từ lúc tạo đến lúc giải quyết có đuôi rất dài (phân vị 90 hơn 3,6 năm) vì bao gồm thời gian nằm trong backlog, nên **không phải đích hợp lý cho "deadline"**. Đích nên là thời gian làm thực tế (`in_progress_minutes`, hoặc thời gian từ lúc vào sprint đến lúc xong) hoặc story point. Chưa biết `total_effort_minutes` được tính thế nào trong TAWOS; cần đọc tài liệu bộ dữ liệu trước khi dùng. Chưa kiểm: tỉ lệ story point bị sửa sau ước lượng (truy vấn lỗi kiểu dữ liệu, chưa chạy lại).

**Quyết định rút ra:** cả hai hướng mở rộng đều đủ dữ liệu để tiếp tục. Hướng 3 dùng story point trong từng dự án làm đích chính, thời gian làm thực tế làm đích phụ sau khi xác nhận ý nghĩa `in_progress_minutes`.

## 5b. Kết quả E6 smoke (2026-11-05)

Theo [Amendment 1](Protocol_estimation_E6_amendment1.md): 5 dự án lớn nhất (chọn theo kích thước), 1.500 issue mới nhất mỗi dự án, văn bản cắt 64 token, 2.250 query, k=20 cố định, chạy một lần, không tinh chỉnh. Output: `artifacts/estimation_e6_smoke/`.

| | MAE | MdAE | Độ phủ khoảng 80% | Độ rộng |
|---|---|---|---|---|
| M0 trung vị dự án | 1,71 | 1,0 | 0,92 | 5,5 |
| M1 trung bình dự án | 1,98 | 1,93 | 0,92 | 5,5 |
| M2 kNN k=20 | 1,61 | 1,0 | 0,88 | 5,0 |

**Tái lập:** chạy lại ngày 2026-11-05 vào `artifacts/estimation_e6_smoke_rerun/` cho đúng từng chữ số của bảng trên, 0 query bị bỏ (mọi query có ≥30 ứng viên); manifest mới ghi tập con (5 dự án, 1.500 issue, 64 token) và hash amendment.

M2 − M0: −0,10 [−0,24; +0,01], thắng ở 3/5 dự án (dự án 12, 28, 36 thắng; 13 và 43 hòa hoặc thua nhẹ). M2 − M1: −0,37 [−0,78; −0,02], thắng 4/5. Quy tắc go (≥4/5 so với M0) **không đạt**; khoảng phủ 0,88–0,92 nằm ngoài 0,75–0,85 nên khoảng bị rộng (điểm rời rạc làm phân vị phủ dư). Hệ quả: tính năng hiển thị case và khoảng, **không đưa ước lượng điểm**. Đây là smoke 5 dự án, CI rất rộng; chưa phải kết luận về E6 đầy đủ (chưa chạy).

## 5c. Tính năng "Việc giống thế này trước đây" trong Plane

Thiết kế theo người dùng (không dùng thuật ngữ nghiên cứu): một dòng kết luận ("Thường là việc nhỏ"), thanh chia nhỏ/vừa/lớn của 20 việc giống nhất, 3 ví dụ giống nhất kèm cỡ và số ngày đã làm, độ chắc bằng lời. Nhỏ/vừa/lớn tính theo thang story point của chính dự án (≤ P33, ≤ P80, còn lại). Độ chắc: ≥70% cùng cỡ thì "vừa", ngược lại "thấp"; ngưỡng cố định do người làm đặt, chưa kiểm chứng, và không có mức "cao" vì smoke E6 chỉ cho thấy giảm sai số ~6%.

- Job offline `research/scripts/publish_cases.py`: tính 20 case gần nhất (cùng dự án, đã xong trước ngày tạo issue, có story point), nhập 3 case hiển thị vào dự án Plane "Past cases" (PCA) để bấm vào là mở trang trong Plane, rồi đăng lên dịch vụ risk (`PUT /api/v1/cases`). Lần chạy 2026-11-05: 497/545 work item có thẻ, 350 case nhập vào PCA.
- Dịch vụ risk: `GET /api/v1/cases/{work_item_id}` theo session Plane. Đường dẫn case chỉ chấp nhận dạng `/<workspace>/browse/<mã>/` nên liên kết không rời Plane.
- Web: thẻ dưới mô tả issue ở trang đầy đủ và peek view.
- Hạn chế: pool 1.000 case mới nhất mỗi dự án; số ngày chỉ có với khoảng một phần tư issue; trang case trong PCA mới có mô tả, chưa ghi cỡ và số ngày; chưa giải thích vì sao hai issue được coi là giống nhau; không ước lượng điểm.

## 5d. Kết quả cổng E7 (2026-11-05): comment và liên kết có giúp phân biệt "kẹt thật" không?

Protocol khóa trước ở [Protocol_stuck_E7_gate.md](Protocol_stuck_E7_gate.md); mã `research/research/stuck_gate.py`, 5 test. Dùng điểm rủi ro của 14 dự án mà mô hình chưa từng thấy, 10.454 issue "im lặng" tại mốc 50% (chưa xong, không hoạt động ≥3 ngày), bỏ-một-dự-án-ra, không LLM. 62,5% có ít nhất một comment trước mốc; 14,2% có liên kết kiểu chặn; 70,8% cuối cùng không hoàn thành (`y=1`).

| | AUC chỉ điểm rủi ro | AUC thêm comment và liên kết | ΔAUC [CI 95%] | Dự án thắng |
|---|---|---|---|---|
| Chính (`y`) | 0,684 | 0,700 | **+0,016 [+0,005; +0,025]** | 11/14 |
| Phụ (`y_closed_only`) | | | **−0,073 [−0,140; −0,021]** | 2/10 |

**Theo quy tắc đã khóa, cổng qua** (CI chính nằm hẳn trên 0). **Nhưng kết luận thực chất yếu và không bền:**
- Mức tăng là 1,6 điểm AUC.
- Với nhãn phụ, thêm đặc trưng làm **kém đi** có ý nghĩa thống kê: lợi ích phụ thuộc vào định nghĩa nhãn.
- Phân tích sau khi xem kết quả (không nằm trong protocol, chỉ thăm dò): hệ số chuẩn hóa lớn nhất là **số comment** (+2,20); các cờ từ khóa (chờ, bị chặn, review, câu hỏi) đều nhỏ (|hệ số| ≤ 0,25). Tức tín hiệu chủ yếu là mức độ thảo luận, không phải ý nghĩa "đang chờ" hay "bị chặn". Issue có liên kết kiểu chặn có tỉ lệ không hoàn thành cao hơn (78,5% so với 69,5%), nhưng chỉ khoảng 14% issue có liên kết và liên kết không cắt theo thời gian.

**Hệ quả:** chưa có bằng chứng rằng đọc ngữ nghĩa comment giúp phân loại "kẹt thật"; cổng qua chủ yếu nhờ số lượng comment. Agent LLM đọc comment (A1/A2) **chưa được biện minh** bởi kết quả này; nếu thử thì phải so với baseline đếm comment, không phải với baseline không có comment. Hạn chế: `y=1` gồm cả issue bị rút khỏi sprint; dùng lại dữ liệu E1; từ khóa tiếng Anh; liên kết không cắt as-of.

## 5e. Sửa luồng cảnh báo: không báo cho issue đã hủy hoặc đã xong (2026-11-05)

Khi định nối policy giới hạn K vào luồng, đo thực trạng cho thấy vấn đề thật không phải con số K mà là **tính đủ điều kiện**:
- Luồng cũ xếp hạng mọi issue của sprint rồi lấy top ceil(20%), không loại issue đã xong hay đã hủy. Trong 95 cảnh báo đang chạy có 7 cảnh báo cho issue `invalid` (Plane hiểu là Cancelled) và 1 cho issue `complete`. Policy E1 thì loại issue đã xong (`dynamic_is_done`).
- Trên toàn bộ 15.153 issue đang mở tại mốc 50%, hai trạng thái `invalid` (210) và `won't fix` (154) cộng 364 issue, **100% cuối cùng không hoàn thành**: điểm cao cho chúng là đúng một cách tầm thường và cảnh báo là nhiễu.
- Sửa: `research/research/alert_selection.py` (5 test, có đối chứng) chỉ xếp hạng và gắn cờ issue chưa xong và chưa bị hủy, giới hạn số cảnh báo tính trên số issue đủ điều kiện (mặc định ceil20 như cũ; có thể đặt `k1`, `k2`, `k3`, `floor20` theo E1). `score_sprints.py` dùng hàm này; `post_briefs.py` gỡ nhãn, comment của bot và bản ghi cảnh báo của issue không còn được gắn cờ (backend có `DELETE /alerts/{id}` bằng token ingest, từ chối nếu đã có quyết định của người).
- Kết quả trên Plane thật (IS): 107 work item xử lý, 83 cảnh báo được đăng, 24 gỡ, 0 cảnh báo nằm trên issue Cancelled hoặc Done; 2 cảnh báo mỗi sprint (trung vị), tối đa 5.

**Hệ quả cho nghiên cứu (chưa tính lại):** E1 và các chỉ số recall dùng nhãn `y` trên mọi issue chưa xong, gồm cả các issue `invalid` và `won't fix`: 3,6% số trường hợp dương (364 trên 10.125) là các issue đã bị hủy mà y = 1 gần như theo định nghĩa. Các con số E1 (recall, precision) có thể hơi lạc quan; chưa tách riêng và chưa tính lại.

## 6. Nguồn ngoài (chỉ đọc tóm tắt, cần đọc toàn văn)

- [Agile Story-Point Estimation: Is RAG a Better Way to Go?](https://arxiv.org/html/2604.03443v1)
- [Search-based Optimisation of LLM Learning Shots for Story Point Estimation (CoGEE)](https://arxiv.org/pdf/2403.08430)
- [Agile Effort Estimation: Have We Solved the Problem Yet? (replication GPT2SP)](https://arxiv.org/pdf/2201.05401)
- [Llama3SP](https://www.sciencedirect.com/science/article/pii/S2949719125000652)
- [Towards an Interpretable Analysis for Estimating the Resolution Time of Software Issues](https://arxiv.org/html/2505.01108)
- [RAG4Tickets](https://arxiv.org/pdf/2510.08667)
- [ProactiveBench](https://arxiv.org/pdf/2410.12361), [PROBE](https://www.arxiv.org/pdf/2510.19771)
- Tawosi, Sarro: LHC-SE, trong [luận án Vali Tawosi](https://discovery.ucl.ac.uk/id/eprint/10175111/1/Vali_PhD_Thesis.pdf)
- Sản phẩm thương mại (tự quảng cáo, chưa có đánh giá độc lập): Wrike, Monday.com, Atlassian Rovo, Asana.
