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

## 5f. Chất lượng cảnh báo như đang vận hành (E8, 2026-11-05)

Protocol khóa trước ở [Protocol_alert_quality_E8.md](Protocol_alert_quality_E8.md); mã `research/research/alert_eval.py`, 2 test. Replay đúng chính sách đang chạy trên Plane (chỉ issue chưa xong và chưa bị hủy, tối đa ceil(20%) số issue đủ điều kiện mỗi sprint, mốc 50%), 14 dự án mà mô hình chưa từng thấy, 1.962 sprint, 3.339 cảnh báo (1,7 cảnh báo mỗi sprint).

| | Precision | Tỉ lệ nền | Lift [CI 95% theo sprint] | Recall |
|---|---|---|---|---|
| Mô hình đang dùng (`dynamic_catboost`) | 0,763 | 0,670 | **1,14 [1,12; 1,16]** | 0,308 |
| Quy tắc đơn giản (`business_rule`) | 0,693 | 0,670 | 1,03 [1,01; 1,05] | 0,280 |

Mô hình trừ quy tắc đơn giản: **+0,119 cảnh báo đúng mỗi sprint [+0,091; +0,148]** (cùng số cảnh báo); theo quy tắc khóa trước, mô hình hơn quy tắc. Với chính sách chặt hơn (k2) kết quả tương tự: lift 1,10, mô hình hơn quy tắc +0,102 [+0,078; +0,127]. Mô hình có precision cao hơn tỉ lệ nền ở cả 14 dự án (mô tả, không kiểm định từng dự án).

**Điều cần nói thẳng:** trong các issue chưa xong tại mốc 50%, **67% cuối cùng không hoàn thành** (tỉ lệ nền). Một cảnh báo đúng 76% so với mức chung 67%: lift 1,14, chỉ hơn chọn ngẫu nhiên 14%. Mô hình có giá trị thống kê thật nhưng độ phân biệt trong thực tế khiêm tốn, và quy tắc đơn giản gần như bằng chọn ngẫu nhiên (lift 1,03). Hệ quả cho sản phẩm: thẻ không nên ngụ ý "issue này sẽ trễ"; nên nêu mức chung ("khoảng hai phần ba issue chưa xong ở giữa sprint kết thúc không hoàn thành"). Hệ quả cho luận văn: chỉ số chính nên là lift so với tỉ lệ nền, không phải precision đơn thuần.

Hạn chế: thăm dò, dùng lại dữ liệu E1, `y = 1` gồm cả issue bị rút khỏi sprint, `business_rule` là một quy tắc đơn giản duy nhất nên "hơn quy tắc đơn giản" chỉ nói về quy tắc đó. Sự cải thiện của quy tắc chọn so với E1 (loại issue đã hủy) chưa được tách riêng.

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

## 5g. Đối chiếu với tài liệu đã đọc toàn văn (2026-11-05)
- RAG story point (Maha, Rahman, Roy, ICPC 2026): cùng dữ liệu TAWOS, cắt theo thời gian 80/20, truy xuất 2–4 ca bằng embedding rồi Llama-3.2-3B sinh điểm; MAE khoảng 1,6–2,0, không khác biệt có ý nghĩa so với các phương pháp cũ; kết luận dùng làm công cụ hỗ trợ bằng cách cho xem ca giống nhau. E6 của ta là phần truy xuất không có LLM, kết quả cùng mức (MAE 1,61 so với 1,71), tự làm độc lập.
- CoGEE (Tawosi và cộng sự): GPT-4 không ví dụ kém mean/median; có tìm kiếm ví dụ thì tốt hơn nhưng 3 dự án, 30 issue test, hàm mục tiêu tính trên tập test (đọc từ mô tả phương pháp).
- Replication Deep-SE: chỉ đọc tóm tắt, mở đầu và bảng; Deep-SE hơn median có ý nghĩa ở 8/42 trường hợp.

## 5h. E9: cảnh báo sớm đến đâu thì còn đáng báo (2026-11-05)
Protocol `Protocol_lead_time_E9.md` (khóa trước), `research/research/lead_time.py`, một lần chạy; kết quả ở `artifacts/lead_time_e9/` (không commit theo chính sách). Cùng 1.962 sprint, 14 dự án mô hình chưa từng thấy, chính sách ceil20 như E8.

| Mốc sprint | Cảnh báo | Precision | Tỉ lệ nền | Lift [CI 95%] | Recall | Mô hình trừ quy tắc (cảnh báo đúng mỗi sprint) |
|---|---|---|---|---|---|---|
| 0% | 4.263 | 0,612 | 0,496 | 1,23 [1,21; 1,26] | 0,312 | +0,236 [+0,197; +0,277] |
| 25% | 3.741 | 0,694 | 0,583 | 1,19 [1,17; 1,21] | 0,312 | +0,180 [+0,146; +0,214] |
| 50% | 3.339 | 0,763 | 0,670 | 1,14 [1,12; 1,16] | 0,308 | +0,119 [+0,091; +0,148] |
| 75% | 2.976 | 0,850 | 0,784 | 1,08 [1,07; 1,10] | 0,307 | +0,066 [+0,045; +0,088] |

**Mốc sớm nhất đáng báo theo quy tắc khóa trước: 0%** (lúc lập kế hoạch sprint). Lift cao nhất và mô hình hơn quy tắc nhiều nhất ở mốc sớm nhất; tỉ lệ nền tăng theo thời gian (mọi issue chưa xong ở cuối sprint đều gần như chắc không xong) nên lift giảm dù precision thô tăng. Không so precision thô giữa các mốc.
Hệ quả: cảnh báo nên chạy từ lúc lập kế hoạch và được xem lại ở các mốc sau (nền tảng của sổ cảnh báo theo thời gian), thay vì chỉ một lần ở 50%.
Hạn chế: giống E8 (dùng lại dữ liệu E1, `y=1` gồm cả issue bị rút khỏi sprint); ở mốc 0% chưa kiểm xem đặc trưng "động" có thật sự chỉ gồm thông tin trước lúc bắt đầu sprint (cần đối chiếu với định nghĩa đặc trưng trong E1 trước khi tuyên bố).

## 5i. E10: khi nào báo (2026-11-05)
Protocol `Protocol_when_to_alert_E10.md` (khóa trước), `research/research/when_to_alert.py`, 6 test, một lần chạy; kết quả ở `artifacts/when_to_alert_e10/`. Cùng ngân sách K mỗi sprint (bằng số cảnh báo của chính sách đang chạy, 1,70 cảnh báo mỗi sprint), 1.962 sprint, 14 dự án mô hình chưa từng thấy.

| Chính sách | Cảnh báo đúng mỗi sprint | Precision | Độ sớm (phần sprint còn lại) |
|---|---|---|---|
| P0 đang chạy (top K ở 50%) | 1,298 | 0,763 | 0,50 |
| P1 (top K ở 0%) | 1,138 | 0,669 | 1,00 |
| P2 (sổ 4 mốc, không báo lặp, ngưỡng điểm ≥ 0,5) | 1,203 | 0,713 | 0,79 |
| P3 (sổ 4 mốc, không ngưỡng) | 1,194 | 0,702 | 0,82 |

So với P0: P1 −0,160 [−0,182; −0,138], P2 −0,095 [−0,113; −0,076], P3 −0,103 [−0,123; −0,085] cảnh báo đúng mỗi sprint; độ sớm P1 +0,50, P2 +0,29 [+0,28; +0,30], P3 +0,32. P2 so với P3: +0,009 [+0,002; +0,016] cảnh báo đúng, độ sớm −0,032 [−0,037; −0,027].

**Theo quy tắc khóa trước:** không chính sách nào "tốt hơn P0" (cảnh báo đúng thấp hơn có ý nghĩa), và ngưỡng 0,5 không "tốt hơn" không ngưỡng (lợi cảnh báo đúng +0,009 nhưng mất độ sớm). Kết luận: **báo sớm hơn phải đánh đổi độ đúng**: ở cùng ngân sách, mỗi lần dời cảnh báo sớm hơn làm precision giảm (0,763 → 0,669 khi dời từ mốc 50% về 0%). Không có chính sách thống trị; đây là một đường đánh đổi.
**Đọc cho sản phẩm (đánh giá thiết kế, không phải kết quả đã khóa):** sổ nhiều mốc P2 đổi khoảng 7% cảnh báo đúng (1,298 → 1,203) lấy thêm khoảng 0,29 phần sprint thời gian để hành động (từ 0,50 lên 0,79), và cho phép bắt issue "nổi lên" ở mốc sau. Lựa chọn giữa P0 và P2 là quyết định về mức giá trị của thời gian để hành động, chưa thể rút ra từ replay vì chưa đo người phản ứng thế nào với cảnh báo sớm.
Hạn chế: giống E8, E9; ngưỡng 0,5 và cách chia ngân sách do người làm đặt, không tối ưu; "độ sớm" chỉ là phần sprint còn lại, không phải thời gian người thật cần để sửa.

**Bổ sung thăm dò cho 5i (2026-11-05, sau khi chạy; chưa có CI, chưa có protocol):** chỉ số chính khóa trước của E10 (số cảnh báo đúng mỗi sprint) bất lợi cho cảnh báo sớm vì tỉ lệ nền tăng theo thời gian: ở mốc muộn gần như mọi issue còn mở đều không xong nên cảnh báo nào cũng "đúng". Tính phần **vượt kỳ vọng ngẫu nhiên** (đúng trừ số đúng mong đợi khi chọn ngẫu nhiên trong các issue đủ điều kiện cùng sprint và cùng mốc): P0 0,150; P1 0,194; P2 0,181; P3 0,179 cảnh báo mỗi sprint. Theo cách đo này cảnh báo sớm không kém, thậm chí hơn. Muốn kết luận phải viết amendment khóa trước (chỉ số vượt kỳ vọng ngẫu nhiên, CI bootstrap theo sprint) rồi chạy lại. Chọn chỉ số chính "số đúng" trong E10 là một lựa chọn chưa tốt của người làm.

## 5j. Định nghĩa nhãn giữ nguyên (2026-11-05)
Nhãn `y = 1` giữ như đề cương: issue cam kết trong sprint mà đến hết sprint chưa xong, gồm cả làm dở lẫn bị rút khỏi sprint (sprint kết thúc theo ngày, issue dở dang trôi sang sprint sau hoặc về backlog). Tỉ lệ issue bị rút trong số không xong ở mốc 75%: XD 57%, TISTUD 42%, MULE 37%, ... CONFSERVER 10%. Tỉ lệ nền ở 75% khác nhau theo dự án từ 0,55 đến 0,94, nên so sánh giữa dự án dùng lift và phần vượt kỳ vọng ngẫu nhiên, không dùng precision thô. Phân tích phụ cần báo: tỉ lệ bị rút theo dự án. "Chuyển sang cycle kế" là hành động khớp với định nghĩa này.

**Amendment 1 của E10 (khóa trước, chạy lại cùng dữ liệu, `artifacts/when_to_alert_e10_amendment1/`)** với chỉ số phần vượt kỳ vọng ngẫu nhiên mỗi sprint:

| Chính sách | Vượt kỳ vọng ngẫu nhiên | So với P0 [CI 95%] | Độ sớm |
|---|---|---|---|
| P0 (báo ở 50%) | 0,150 | | 0,50 |
| P1 (báo ở 0%) | 0,194 | +0,044 [+0,022; +0,064] | 1,00 |
| **P2 (sổ 4 mốc, ngưỡng 0,5)** | 0,181 | **+0,031 [+0,013; +0,048]** | 0,79 |
| P3 (sổ 4 mốc, không ngưỡng) | 0,179 | +0,029 [+0,011; +0,046] | 0,82 |

Theo quy tắc của amendment: P1, P2, P3 đều **tốt hơn P0** (CI nằm hoàn toàn trên 0), đồng thời báo sớm hơn. Chỉ số cũ (số đúng thô) vẫn ngược chiều vì tỉ lệ nền tăng theo thời gian; hai chỉ số được báo cùng nhau. **Quyết định thiết kế: chạy thật dùng P2** (sổ nhiều mốc, không báo lặp), vì nó hơn P0 về phần vượt kỳ vọng ngẫu nhiên, báo sớm hơn nhiều, và cho phép bắt issue nổi lên ở mốc sau. P1 có phần vượt cao nhất nhưng không cho xem lại. Hạn chế như E8, E9.

## 5k. E11: agent chọn và soạn hành động, chạy thử nhỏ (2026-11-05)
Protocol `Protocol_action_agent_E11.md` và amendment 1 (chạy thử nhỏ trước vì lần đầy đủ đầu tiên bị dừng do quá tốn, không ghi kết quả). Mã `app/services/action_agent.py`, `research/agent_action_eval.py`, 7 test. Chạy thử 10 cảnh báo của dự án IS (chính sách P2), `gpt-oss-120b`, 1 lần lặp, kèm 10 lần chèn lệnh trong comment; tổng chi khoảng 0,0005 USD.
- **Lần 1:** đầu ra hợp lệ 10/10, bộ kiểm tra chặn 4/4 đầu ra xấu cố định, chèn lệnh lọt vào thẻ 0 lần, 0,00005 USD và khoảng 5 giây mỗi cảnh báo. Đọc đầu ra thấy lỗi: nhắc "đang kẹt gì" cho issue vừa hoạt động 0,0 đến 0,9 ngày; ghi "status: unknown"; một lần chọn "giao người phụ trách" dựa trên dữ kiện không được cung cấp.
- **Sửa:** chỉ cho nhắc khi im lặng ≥ 2 ngày; agent chỉ được chọn tăng ưu tiên, nhắc, chuyển cycle (bỏ giao người và tách nhỏ vì thiếu dữ kiện); dặn bỏ trạng thái khi không rõ.
- **Lần 2 (sau sửa, cùng 10 cảnh báo):** hành động agent **trùng quy tắc ở cả 10**; 4 lần agent đề xuất nhắc cho issue vừa hoạt động bị bộ kiểm tra từ chối và quay về quy tắc (tỉ lệ hợp lệ 0,6, dưới ngưỡng 90% của protocol gốc; sau đó prompt được dặn thêm điều kiện ≥ 2 ngày để giảm bị từ chối, chưa đo lại). Chèn lệnh lọt 0.
**Đọc:** trên mẫu nhỏ này agent chưa chọn hành động tốt hơn quy tắc; giá trị còn lại là lời nhắc viết tự nhiên và (chưa kiểm) khả năng đọc comment. Muốn kết luận chất lượng cần người chấm (bảng chấm nằm trong thư mục kết quả), không phải đo thêm bằng máy.

## 5l. Agent chẩn đoán nguyên nhân kẹt (2026-11-05)
Nhiệm vụ mới của agent (thay cho "chọn hành động", vốn trùng quy tắc ở 10/10 trong 5k): đọc comment, mô tả và liên kết chặn trước mốc rồi trả lời **vì sao issue có vẻ kẹt** trong tập (chờ người, bị issue khác chặn, cần quyết định, phạm vi chưa rõ, chưa bắt đầu, không đủ thông tin), **trích nguyên văn** một câu bằng chứng, nêu issue đang chặn nếu có, và soạn lời nhắc nhắm đúng chỗ. Mã `app/services/stuck_diagnosis.py` (6 test). Mã kiểm tra từng phần: câu trích phải có thật trong văn bản (so sánh không phân biệt hoa thường và khoảng trắng), issue chặn phải là liên kết đang mở, lời nhắc không có link, mention, thẻ HTML, phải nhắc đúng khóa issue và số ngày; hỏng thì thành `no_signal` và quy tắc quyết định. Backend lưu `cause` và `evidence_quote`; thẻ Plane hiện "Why it looks stuck" cùng câu trích; brief có cùng dòng đó.
**Chạy thử nhỏ** (`research/research/stuck_diagnosis_pilot.py`): 30 cảnh báo của dự án IS có comment, `gpt-6-luna`, một lần, tốn 0,002 USD. Agent trả "không đủ thông tin" ở 20/30, có nguyên nhân ở 10/30 (cần quyết định 5, chờ người 3, phạm vi chưa rõ 1, bị chặn 1); bộ từ khóa của E7 có nguyên nhân ở 17/30. Câu trích bịa: 0/9. Trùng nguyên nhân với bộ từ khóa: 43%. Đọc từng dòng (người đọc là tác giả, không độc lập): từ khóa gán sai nhiều trường hợp ("Dependencies of packages" thành bị chặn, "Done in PR" thành chờ), agent thận trọng hơn và có ca đúng rõ (IS-736 bị IS-867 chặn nhờ liên kết và comment, IS-1119 chờ review, IS-1500 chờ người báo lỗi cung cấp thông tin); agent bỏ sót một số ca (IS-1211, IS-712). Bảng 30 dòng `artifacts/stuck_diagnosis_pilot/rating_sheet.csv` có hai cột trống cho người chấm. **Chưa kết luận** agent chẩn đoán đúng hơn bộ từ khóa cho đến khi có người chấm độc lập.

## 5m. Agent chẩn đoán có công cụ (2026-11-05)
Sau khi đối chiếu với các tài liệu thiết kế (Protocol_agent_E3_v2, tài liệu Anthropic về kiến trúc agent): bản "một lần gọi" (5l) là workflow chứ chưa phải agent. Bản mới `app/services/stuck_agent.py` là agent có công cụ thật: vòng lặp tối đa 4 bước, công cụ chỉ đọc `get_comments` (chỉ issue được cảnh báo) và `get_linked_issue` (chỉ issue có liên kết với nó), kết thúc bằng `submit_diagnosis`. Dữ liệu công cụ cắt tại thời điểm cảnh báo (`research/tawos_source.py`), kết quả công cụ bị cắt tối đa 3.000 ký tự, quote phải có thật trong kết quả công cụ, issue chặn phải là liên kết đang mở, lời nhắc qua cùng bộ kiểm tra; chạy dở, bị từ chối hoặc lỗi thì `no_signal` và quy tắc quyết định. Mỗi bước ghi vào `meta['trace']` (công cụ, tham số, kích thước, chi phí). 7 test (đọc comment rồi trả lời, theo issue chặn, công cụ ngoài phạm vi bị từ chối, quote bịa bị loại, vòng lặp có giới hạn, kết quả công cụ bị cắt, lỗi thì quay về quy tắc).
**Chạy thử nhỏ** (cùng 30 cảnh báo của dự án IS như 5l, `gpt-6-luna`, tốn 0,0043 USD, `artifacts/stuck_agent_pilot/`): có nguyên nhân 13/30 (một lần gọi: 10/30; bộ từ khóa: 17/30); 30/30 gọi `get_comments`, 4 lần gọi `get_linked_issue` (đúng các issue có liên kết), không lần nào chạy dở; một câu trả lời bị bộ kiểm tra từ chối (blocker không phải liên kết đang mở). Cùng nguyên nhân với bản một lần gọi ở 18/30. Ví dụ: IS-736 bị IS-867 chặn (tìm được qua liên kết), IS-582 bị IS-574 chặn, IS-1121 có hai liên kết đều đã xong nên kết luận không đủ thông tin. Hạn chế: chỉ 30 mẫu, người đọc kết quả là tác giả, chưa có người chấm; lời nhắc của agent đôi khi không mở đầu lịch sự; bộ kiểm tra số ngày chỉ so với issue được cảnh báo nên lời nhắc nêu số ngày của issue chặn bị từ chối.
Nhãn trên thẻ và brief đổi thành "Theo các comment: ..." để không thành khẳng định nhân quả (cổng an toàn nhân quả của E3).
