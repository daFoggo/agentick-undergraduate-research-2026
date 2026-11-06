# Bản mô tả cho người viết báo cáo

Cập nhật 2026-11-06. File này do người làm code giữ và cập nhật khi mỗi module xong. Nguồn duy nhất về bài toán và kiến
trúc vẫn là [intent.md](intent.md); giới hạn ở [BACKLOG.md](BACKLOG.md). Quy ước: **[ĐÃ ĐO]** là số đã chạy và có thể
chạy lại; **[SẼ ĐO Mxx]** là số sẽ có khi module xong, chưa được viết thành số trong báo cáo; **[CHƯA ĐỌC TOÀN VĂN]** là
nguồn ngoài mới đọc tóm tắt, phải đọc trước khi trích.

## 1. Câu chuyện của đề tài (một đoạn)

Trong một sprint, nhiều issue trễ mà không ai biết sớm. Phần phát hiện (CatBoost, E1 đến E9) cho biết issue nào có nguy
cơ trễ. Đề tài này làm bước kế tiếp: **giải thích vì sao issue có nguy cơ, kèm bằng chứng kiểm chứng được, rồi đề xuất
hành động ở cấp issue và cấp sprint; con người luôn là người quyết định trong Plane.** AI không có quyền ghi.

## 2. Hệ thống làm những gì (chức năng)

| Chức năng | Mô tả cho người dùng | Module | Trạng thái |
|---|---|---|---|
| Phát hiện | Chấm điểm nguy cơ trễ mỗi issue tại mốc t trong sprint | nền (E1 đến E9) | xong |
| Chẩn đoán | Thẻ trên issue: nguyên nhân (6 loại), bằng chứng trích dẫn, hành động đề xuất, hai ghi chú | M1 đến M8 | xong, [ĐÃ ĐO] trên 81 alert |
| Duyệt / Bỏ qua / Hoàn tác | Người bấm thì Plane mới thay đổi (đổi ưu tiên, nhắc người phụ trách, chuyển sprint sau) | M4 đến M7 | xong |
| Thống kê giám sát | Tab Analytics "Delivery risk", widget Home, danh sách Your work, view đã lưu | M9 đến M12 | xong |
| Đo chất lượng chẩn đoán | Bộ nhãn độc lập, độ đồng thuận với chẩn đoán của mô hình | M13 | đang làm |
| Kế hoạch sprint | Đề xuất chuyển nhiều issue cùng lúc dựa trên sức chứa suy từ lịch sử và tình trạng cả sprint | M14 | chưa |
| Duyệt theo lô | Chọn từng dòng của kế hoạch, duyệt một lần, hoàn tác cả lô | M15 | chưa |
| Hỏi đáp về rủi ro | Hỏi bằng ngôn ngữ tự nhiên; agent gọi công cụ chỉ đọc, trả lời kèm mã issue | M16 | chưa |
| Sổ cảnh báo tối thiểu | Trạng thái giữa các lần chạy, tạm hoãn, ghi nhận hồi phục sau khi duyệt | M17 | chưa |

## 3. Stack

PostgreSQL 17 (TAWOS, schema `tawos_raw`) · Python, pandas, CatBoost · OpenRouter qua `OpenRouterClient`
(`openai/gpt-6-luna`; trần giá mỗi request; ngân sách `OPENROUTER_BUDGET_USD`) · pydantic · FastAPI, SQLAlchemy 2,
Alembic, PostgreSQL 16 (`agentick-backend`) · Plane (fork, React/MobX) · Docker Compose (`scripts/stack.sh`) · pytest,
ruff, Spectral (lint OpenAPI), `tsc`. **Không dùng:** framework agent, vector store, text2sql.

## 4. Phương pháp theo từng phần (để viết mục Phương pháp)

1. **Dựng trạng thái tại t.** `issue.assignee_id/priority/status/sprint_id` trong TAWOS là giá trị cuối; trạng thái tại t
   được dựng lại từ `change_log` (tên trường khác hoa thường nên dùng `lower(field)`). Mọi bằng chứng cắt tại t.
2. **Năm bộ thu thập (collector).** Truy vấn SQL viết sẵn, không phải kỹ thuật AI: thảo luận; việc người phụ trách làm
   trong 7 ngày trước; chuỗi chặn (chờ-nhau, sâu 2); tình trạng sprint; lịch sử issue. Mỗi dòng có mã sự kiện.
3. **Chẩn đoán.** Một lần gọi LLM, đầu ra pydantic theo tập nguyên nhân đóng (`pulled_away`, `blocked`,
   `waiting_person`, `needs_decision`, `unclear_scope`, `carry_over`), tối đa 3 giả thuyết, mỗi giả thuyết trích mã sự kiện.
4. **Verifier (code).** Bỏ giả thuyết có mã sự kiện không tồn tại hoặc sai loại; kiểm câu nhắc không nêu issue của
   project khác. Comment của người dùng đi vào khối `<untrusted>`.
5. **Hai ghi chú luật.** `sprint_overload` (đã trôi >= 50%, >= 60% còn mở, >= 5 issue) và `done_not_updated` (từ khóa
   trong comment 3 ngày gần nhất mà trạng thái chưa done). Ngưỡng chọn bằng mắt, ghi ở hạn chế.
6. **Quyền xem.** Nội dung của project người xem không thấy bị che; thống kê chỉ đếm project Plane liệt kê cho người xem.
7. **Kế hoạch sprint (M14).** *Sức chứa* = số issue dự kiến xong trong phần thời gian còn lại, lấy từ tỉ lệ hoàn thành
   của các sprint trước cùng dự án tại cùng mốc thời gian (kinh nghiệm, không huấn luyện). *Chọn tập chuyển* = xếp theo
   điểm rủi ro, chỉ chuyển đủ số vượt sức chứa, và nếu A chờ B mà B bị chuyển thì A cũng bị chuyển (đóng dưới quan hệ
   chờ-nhau). **Không có lời gọi mô hình mới**: lý do cho từng issue lấy từ chẩn đoán đã qua verifier, phần tóm tắt là mẫu
   câu do code điền số. Cơ sở: policy có giới hạn nguồn lực và dễ kiểm toán hơn là để LLM tự quyết (When to Intervene;
   WB-PrPM) [CHƯA ĐỌC TOÀN VĂN]. Mã: `research/research/sprint_plan.py`, `research/scripts/backtest_plan.py`.
8. **Duyệt theo lô (M15).** Mỗi dòng đi qua đúng hành động đóng đã có; ghi kết quả từng dòng; hoàn tác theo giá trị cũ
   đã lưu. Lỗi một dòng không làm hỏng các dòng khác.
9. **Agent hỏi đáp (M16).** Vòng gọi công cụ tự viết; công cụ có tham số, chỉ đọc, đã lọc theo quyền xem ngay trong công
   cụ (không dựa vào lời nhắc). Mọi mã issue trong câu trả lời phải có trong kết quả công cụ. Từ chối câu ngoài phạm vi.
   Thiết kế công cụ sẽ theo tài liệu hướng dẫn mà người dùng cung cấp [CHỜ TÀI LIỆU].
10. **Sổ cảnh báo (M17).** Mỗi lần chạy so điểm và trạng thái với lần trước để gán mới / dai dẳng / xấu đi / đã giải
    quyết; Bỏ qua kèm hạn tạm hoãn; ghi nhận issue về done sau khi Duyệt (chỉ là quan hệ, không là nhân quả).

## 5. Bất biến (nên có một mục riêng trong báo cáo)

Cắt tại t; có bằng chứng; AI không có quyền ghi; text người dùng là dữ liệu; theo quyền xem; số do code tính; lô cũng là
hành động đóng. Chi tiết ở `intent.md`.

## 6. Số liệu đã đo (chỉ dùng những số này)

- Chẩn đoán trên project ISP: 81 alert, 0 lần gọi mô hình lỗi, 3 alert có một giả thuyết bị verifier bỏ. Chi phí khoảng
  0,0001 USD mỗi alert, toàn bộ một lần chạy khoảng 0,01 USD. [ĐÃ ĐO]
- 43 trong 81 alert có "carry_over" là lý do đứng đầu (tín hiệu yếu một mình). [ĐÃ ĐO]
- Kiểm thử: research 86, backend 56 test xanh; `tsc` 0 lỗi; Spectral 0 lỗi. [ĐÃ ĐO]
- Phát hiện (E1 đến E9): lấy từ `research/artifacts` và tài liệu gốc của giai đoạn đó, **kiểm lại trước khi trích**; người
  làm code không nhắc lại số ở đây để tránh sai lệch.
- **M13, đồng thuận của chẩn đoán với nhãn độc lập** [ĐÃ ĐO, 2026-11-06]. Người chấm là một mô hình (Claude Opus chạy
  như agent riêng), không thấy kết luận của hệ thống, chấm một lượt theo `research/eval/RUBRIC.md` (khóa trước khi
  chấm). Nhãn nghĩa là "nguyên nhân mà sự kiện thu được hỗ trợ", không phải nguyên nhân thật (TAWOS không có). Kết quả
  ở `research/artifacts/eval/results.json` và `research/artifacts/eval_heldout/results.json`.

  | | Lần 1: 81 alert của ISP | Held-out: 60 ca, sau khi sửa thứ tự |
  |---|---|---|
  | Khớp nguyên nhân đứng đầu | 0,617 | 0,683 |
  | Khớp khi cả hai đều nêu một nguyên nhân | 0,656 | 0,682 |
  | Nguyên nhân đúng nằm trong danh sách (khi cả hai nêu) | 0,969 | 0,977 |
  | Kappa | 0,496 | 0,571 |
  | Hệ thống nói "không rõ" / người chấm gắn `none` | 16 / 9 | 15 / 12 |
  | Tỉ lệ nhãn phổ biến nhất (đa số) | 0,383 (`pulled_away`) | 0,317 (`pulled_away`) |
  | `carry_over`: hệ thống nêu đầu / người chấm / trùng | 41 / 20 / 20 | 20 / 17 / 12 |
  | `pulled_away`: hệ thống nêu đầu / người chấm / trùng | 19 / 31 / 18 | 22 / 19 / 15 |
  | `unclear_scope`: hệ thống nêu đầu / người chấm / trùng | 1 / 8 / 0 | 0 / 5 / 0 |
  | `waiting_person`: hệ thống nêu đầu / người chấm / trùng | 2 / 8 / 2 | 1 / 3 / 1 |

  Phát hiện: ở lần 1 hệ thống đặt `carry_over` (bị dồn từ sprint trước) lên đầu ở 41 trên 81 thẻ dù có nguyên nhân mạnh
  hơn; verifier được sửa để xếp `carry_over` cuối (có test). Held-out là **tập khác** (issue xếp hạng nhưng không bị
  cảnh báo, không trùng lần 1, sinh bằng mã đã sửa), nên không thể nói chắc bản sửa gây ra mức tăng. Hệ thống gần như
  không bắt được `unclear_scope` (0 trên 13 ca người chấm gắn nhãn). Giới hạn: người chấm là mô hình; quy tắc 2 của
  rubric ("carry_over là tín hiệu yếu") được viết sau khi đã thấy 43/81 alert có `carry_over` đứng đầu; chưa có người
  chấm lại một mẫu. Chi phí 60 ca held-out: 0,007 USD.
- **M14, backtest kế hoạch sprint** [ĐÃ ĐO, ISP, mốc 50%, `research/artifacts/eval/backtest_plan.json`]: 60 sprint được
  chạy lại (59 có kế hoạch), 412 issue mở, 201 không xong (tỉ lệ nền 0,488). Số issue không xong dự kiến so với thực tế
  (từ lịch sử các sprint đã kết thúc trước đó): sai lệch tuyệt đối trung bình 1,76 issue mỗi sprint, thiên lệch -0,05.
  Issue được chọn theo rủi ro: 0,528 thật sự không xong (so với 0,488 nếu chọn bừa), phủ 0,532 số issue không xong; 2 issue
  "đi cùng" (đều không xong). 25 trên 60 sprint chuyển nhiều hơn số issue thật sự không xong. Diễn giải đúng: **đếm số
  issue không xong thì chuẩn, chọn đúng issue thì yếu** ở độ sâu này. Phân tích tạm (chưa lưu thành script): precision
  trong top 20% mỗi sprint là 0,582 (110 issue), top 33% là 0,537, nền 0,49 (429 issue); tổng điểm rủi ro trung bình
  mỗi sprint (4,22) cao hơn số issue không xong thật (3,33), tức điểm chưa hiệu chuẩn ở mốc này. **Số "precision 77 đến
  80%" trong báo cáo cũ không khớp** với ISP ở mốc này: kiểm lại trước khi trích.
- Kiểm thử: research 92, backend 64 test xanh (sau M13 và backend M14). [ĐÃ ĐO]
- Bộ câu hỏi của agent hỏi đáp: [SẼ ĐO M16]. Duyệt theo lô: [SẼ ĐO M15]. Sổ cảnh báo: [SẼ ĐO M17].

## 7. Hạn chế phải nêu trung thực

Xem mục "Hạn chế nghiên cứu hiện tại" trong `intent.md` và `BACKLOG.md` (23 mục, trong đó 15 mục là hạn chế nghiên cứu).
Nhấn mạnh: chưa có nhãn người cho chẩn đoán (sẽ có một phần nhờ M13, người chấm là một mô hình khác và cần người kiểm
mẫu); thử trên một project; ngưỡng ghi chú chọn bằng mắt; assignee TAWOS đã ẩn danh nên Your work trống; không có kết quả
nhân quả về việc cảnh báo giúp issue hồi phục.

## 8. Không được viết

- Không viết "chưa ai làm" hay "SOTA" (tài liệu nghiên cứu cũ ghi rõ chỉ là targeted review, không phải systematic review).
- Không viết số cải thiện của bài ngoài nếu chưa đọc toàn văn bài đó (PRISM, Memento, ProAgentBench, Pro-Memory...).
- Không viết là hệ thống ước lượng deadline hay story point: E6 cho thấy kNN theo case không phân biệt được với trung vị
  (smoke 5 dự án: MAE 1,61 so với 1,71, khoảng tin cậy chứa 0). Kế hoạch sprint dựa trên sức chứa cấp sprint, không phải
  ước lượng từng issue.
- Không so sánh phương pháp nếu chưa có thực nghiệm; báo cáo mô tả và báo số đo, nếu muốn so sánh phải hỏi người làm code.

## 9. Nguồn ngoài đã có trong dự án (đều [CHƯA ĐỌC TOÀN VĂN] trừ khi ghi khác)

Tawosi và cộng sự (TAWOS, MSR 2022); Tu và cộng sự (FSE 2018, dùng sai thời gian trong dữ liệu issue); Teinemaa và cộng
sự (TKDD 2019, outcome-oriented predictive monitoring); Prokhorenkova và cộng sự (CatBoost, NeurIPS 2018); replication
estimation của Tawosi (TSE); *Fire now, fire later*; *When to Intervene?*; WB-PrPM; ProAgentBench; PRISM; Pro-Memory;
Memento; bài tiêm lệnh gián tiếp qua ticket Jira. Danh sách và liên kết gốc nằm trong lịch sử git (commit `becbdd2^`,
thư mục `research/documents/`: `Deep_research_AI_agent_canh_bao_som.md`, `Literature_and_methods.md`,
`Huong_nghien_cuu_SOTA_agent.md`, `Mo_rong_tro_ly_sprint.md`, `Protocol_estimation_E6.md`). Lấy bằng
`git show becbdd2^:research/documents/<tên>`.

## 10. Hình minh họa nên có

Sơ đồ ba khối (job ngoại tuyến, dịch vụ risk, Plane), và một ví dụ đi qua từng bước với một alert thật (ví dụ ISP-449),
vì sơ đồ trừu tượng khó hiểu. Ảnh chụp trình duyệt: thẻ chẩn đoán, tab Delivery risk, (sau này) thẻ kế hoạch sprint và
panel hỏi đáp.
