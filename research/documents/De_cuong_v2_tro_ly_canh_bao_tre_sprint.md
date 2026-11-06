# Đề cương (bản 2)

## Trợ lý cảnh báo sớm trễ sprint: dự báo rủi ro từ lịch sử issue và agent hỗ trợ người quản lý hành động

**Tên tiếng Anh:** *Early Warning of Sprint Slippage and Human-Approved Corrective Actions in an Issue Tracker*

Ngày 2026-11-05. Thay thế phạm vi của đề cương cũ (De_cuong_du_bao_som_rui_ro_sprint.md) bằng phạm vi hẹp hơn, mọi thành phần đều phục vụ một mục tiêu: **giảm khả năng trễ deadline và rủi ro trong sprint**. Kết quả cũ (E1 đến E9) được giữ làm bằng chứng nền; chỗ nào là thăm dò thì ghi rõ.

## 1. Vấn đề
Đội phần mềm cam kết một tập issue cho mỗi sprint, nhưng phần lớn không kịp hoàn thành (trong dữ liệu TAWOS, 50% issue cam kết cuối cùng không xong tính ở đầu sprint; 67% issue còn mở ở giữa sprint không xong). Người quản lý thường chỉ biết khi đã quá muộn, và công cụ hiện có (gắn cờ theo luật như quá hạn, thiếu estimate) không cho biết ưu tiên xem gì, vì sao, và làm gì.

## 2. Bài toán
**Đơn vị:** một issue trong một sprint. **Thời điểm t:** các mốc 0, 25, 50, 75% thời lượng sprint. **Dự báo:** xác suất issue chưa hoàn thành đến hết sprint, chỉ dùng dữ liệu đã có đến t. **Nhãn:** issue thuộc sprint lúc chốt cam kết mà chưa đạt trạng thái hoàn thành khi sprint kết thúc; issue đã hủy (`invalid`, `won't fix`) không được cảnh báo và không tính khi đánh giá. **Cảnh báo bị giới hạn:** mỗi sprint tối đa ⌈20% số issue đủ điều kiện⌉ cảnh báo.

Từ cảnh báo đến hành động: với mỗi issue được cảnh báo, hệ thống đề xuất **một hành động sửa cụ thể** thuộc một tập nhỏ; người duyệt thì thực hiện; có hoàn tác.

## 3. Câu hỏi nghiên cứu
- **RQ1 (dự báo).** Lịch sử thực thi của issue có cải thiện dự báo so với thông tin tại thời điểm bắt đầu và so với quy tắc đơn giản không, ở dự án chưa từng thấy?
- **RQ2 (độ sớm).** Chất lượng cảnh báo thay đổi thế nào theo mốc 0/25/50/75%, và mốc sớm nhất nào còn đáng báo?
- **RQ3 (ngân sách).** Ở cùng số cảnh báo mỗi sprint, mô hình bắt được bao nhiêu issue không xong hơn tỉ lệ nền và hơn quy tắc?
- **RQ4 (hành động).** Với cảnh báo đã chọn, agent có công cụ đọc có chọn và soạn hành động hợp lý hơn quy tắc mẫu câu không (do người chấm theo rubric khóa trước), với chi phí và sai sót nào?
- **RQ5 (an toàn và vòng đời).** Verifier bằng chứng, giới hạn quyền ghi và sổ cảnh báo giảm được bao nhiêu khẳng định không có căn cứ, cảnh báo lặp và hành động trái phép (kể cả khi comment của issue chứa lệnh chèn)?

## 4. Phạm vi sản phẩm (trợ lý trên Plane)
| # | Phần | Mô tả |
|---|---|---|
| A | Phát hiện | Mô hình CatBoost chấm điểm; controller (không LLM) chọn cảnh báo theo ngân sách ở từng mốc |
| B | Sức khỏe sprint | Trang cycle: số issue đang cảnh báo; sprint nhận nhiều hơn mức đội thường xong bao nhiêu (thống kê lịch sử đội, không dự báo bằng mô hình) |
| C | Giải thích | Brief có bằng chứng: trạng thái, số ngày im lặng, thay đổi gần nhất; mỗi khẳng định gắn sự kiện nguồn, qua verifier |
| D | Hành động | Mỗi cảnh báo kèm một hành động. Thực thi được qua Plane: nhắc người phụ trách (comment), tăng ưu tiên, chuyển sang cycle kế. Chỉ gợi ý (không tự thực thi): gán người, tách nhỏ |
| E | Vòng đời | Sổ cảnh báo: không báo lặp, xem lại ở mốc kế, trạng thái mới/dai dẳng/xấu đi/đã giải quyết, ghi kết cục cuối sprint |
| F | Đánh giá | Replay trên TAWOS; đánh giá agent lặp ≥3 lần; chạy bóng hoặc thử với người nếu có người tham gia |

**Vai trò agent (LLM):** chỉ ở C và D, với quyền **chỉ đọc**: đọc lịch sử, comment, liên kết, tóm tắt sprint rồi chọn hành động trong tập cố định và soạn nội dung. Xác suất, chọn cảnh báo và mọi thao tác ghi do mã phía máy chủ kiểm soát; ghi chỉ xảy ra khi người bấm Duyệt. Nội dung issue được coi là dữ liệu không đáng tin. Mẫu câu theo quy tắc là baseline bắt buộc và là chế độ mặc định; agent là chế độ tùy chọn.

**Cắt khỏi phạm vi** (không phục vụ trực tiếp giảm trễ, hoặc bằng chứng không ủng hộ): đội nhiều agent, bộ nhớ agent tự tiến hóa, ước lượng story point chính xác, phát hiện trùng lặp, đọc ngữ nghĩa comment làm tín hiệu dự báo, dự báo "sprint trễ khi nào" ở cấp sprint, huấn luyện lại từ phản hồi Duyệt/Bỏ qua. Lý do và bằng chứng xem `Pham_vi_chot.md`.

## 5. Dữ liệu
TAWOS (Jira công khai, 39 dự án, ~458 nghìn issue), nhập vào PostgreSQL; 36 dự án có sprint dùng được; 14 dự án giữ ngoài huấn luyện để đo chuyển giao; snapshot theo mốc 0/25/50/75%. Không dùng thông tin xuất hiện sau mốc t. Plane tự chủ (self-host) làm giao diện; dữ liệu TAWOS nhập vào Plane để trình diễn.

## 6. Phương pháp và đánh giá
- **Dự báo:** baseline tần suất, quy tắc nghiệp vụ, mô hình tĩnh, mô hình động (CatBoost). Chia theo thời gian và theo dự án. Chỉ số: PR-AUC, Brier, độ dốc hiệu chuẩn.
- **Cảnh báo:** precision, **lift so với tỉ lệ nền**, recall, hiệu số cảnh báo đúng mỗi sprint giữa mô hình và quy tắc; bootstrap theo sprint; mọi so sánh dùng cùng tập issue đủ điều kiện và cùng số cảnh báo. Protocol khóa trước, một lần chạy.
- **Agent (RQ4, RQ5):** bộ kịch bản khóa trước, nhiều lớp (bình thường, không cần hành động, dữ liệu dự án khác, rò rỉ tương lai, chèn lệnh trong comment); A0 mẫu câu, A1 LLM một lượt, A2 agent có công cụ; lặp ≥3 lần; báo độ bám bằng chứng, độ đúng quyết định, an toàn, độ trễ, USD mỗi cảnh báo; negative control cho từng cơ chế an toàn. Chất lượng hành động do người chấm hoặc thử nghiệm với người (không dùng LLM thay người).
- **Mô hình LLM:** `openai/gpt-6-luna` (chạy báo cáo), `openai/gpt-oss-120b` (phát triển); trần giá và ngân sách chi tiêu trong client.

## 7. Kết quả đã có (thăm dò, dùng lại dữ liệu E1 cho E8, E9)
- E8 (mốc 50%, chính sách đang chạy): precision 0,763 so với tỉ lệ nền 0,670, lift 1,14 [1,12; 1,16]; mô hình hơn quy tắc đơn giản +0,119 cảnh báo đúng mỗi sprint [+0,091; +0,148]; 1.962 sprint, 14 dự án.
- E9 (độ sớm): lift 1,23 / 1,19 / 1,14 / 1,08 ở mốc 0/25/50/75%; mô hình hơn quy tắc ở mọi mốc; mốc sớm nhất đáng báo theo quy tắc khóa trước là 0%.
- Cấp sprint: mô hình cộng dồn không hơn lịch sử đội (MAE 0,197 so với 0,194) nên không đưa dự báo cấp sprint vào sản phẩm.
- E3 (brief): mẫu câu ngang agent về bám bằng chứng; chưa đo chất lượng hành động.
- E6, E7: truy xuất ca giống nhau chỉ hơn trung vị khoảng 6%; tín hiệu comment chủ yếu là số comment.
- Hệ thống tích hợp Plane đã chạy: thẻ cảnh báo Duyệt/Bỏ qua/Hoàn tác, backend FastAPI + PostgreSQL, kiểm quyền bằng phiên Plane.

## 8. Đóng góp dự kiến
1. Giao thức tái lập để đo cảnh báo sprint theo mốc, ngân sách và tỉ lệ nền (không chỉ precision thô).
2. Bằng chứng về giá trị thật của mô hình ở dự án chưa thấy (lift khiêm tốn nhưng ổn định) so với quy tắc đơn giản.
3. Một thiết kế agent hỗ trợ hành động có kiểm soát (chỉ đọc, bằng chứng, người duyệt, hoàn tác) và bộ đánh giá tái lập được, báo cả kết quả âm (ví dụ nếu mẫu câu ngang agent).
4. Hệ thống chạy trong Plane để trình diễn.

## 9. Giới hạn
- Lift 1,14 ở mốc 50% là khiêm tốn: cảnh báo giúp chọn nơi xem trước, không phải kết luận issue sẽ trễ.
- Replay lịch sử không chứng minh cảnh báo giảm trễ; tác động chỉ kết luận được sau thử nghiệm với người hoặc chạy bóng.
- Nhãn gồm cả issue bị rút khỏi sprint; kết quả E8, E9 dùng lại dữ liệu E1 nên là thăm dò; mô hình trên các mốc chưa được kiểm lại độ rò rỉ đặc trưng ở mốc 0%.
- TAWOS là dự án mã nguồn mở, không tự khái quát cho doanh nghiệp; dữ liệu người phụ trách đã ẩn danh.
- LLM chưa được chứng minh tốt hơn mẫu câu ở phần brief.

## 10. Kế hoạch
| Giai đoạn | Việc | Sản phẩm |
|---|---|---|
| 1 | Hành động có thực thi và hoàn tác trong backend và Plane (D) | API, thẻ cảnh báo hiển thị hành động và nội dung soạn sẵn, test |
| 2 | Sổ cảnh báo theo mốc (E) và đăng cảnh báo cho mốc 0/25/50/75% | Ledger, chống báo lặp, ghi kết cục |
| 3 | Trang sức khỏe sprint (B) | Chip và thống kê ở trang cycle |
| 4 | Agent A2 chọn hành động và soạn nội dung (C, D), dry-run | Chế độ `--agent`, verifier, ngân sách chi |
| 5 | Đánh giá agent (RQ4, RQ5): kịch bản khóa trước, lặp ≥3, chèn lệnh, chi phí | Báo cáo E3 v3 |
| 6 | Chạy bóng hoặc thử với người (nếu có người tham gia) | Báo cáo E4 |
| 7 | Viết báo cáo, hoàn thiện tài liệu | Luận văn |

## 11. Nguồn đã đọc (mức đọc ghi rõ)
- Toàn văn: Maha, Rahman, Roy (2026), RAG cho ước lượng story point (arXiv 2604.03443); Tawosi, Alamir, Liu (2024), CoGEE cho LLM learning shots (arXiv 2403.08430).
- Một phần (tóm tắt, mở đầu, bảng): Tawosi, Moussa, Sarro, replication Deep-SE (arXiv 2201.05401).
- Chỉ tóm tắt (abstract): PRISM (2602.01532), Pro-Memory (2611.05731), Memento (2508.16153), UQ cho agent (2609.07395), Scaling agent systems (2512.08296), SEEAgent (2509.14483), ProAgentBench (2602.04482).
- Báo cáo khảo sát do người dùng cung cấp về repo, sản phẩm và bài báo agent quản lý dự án: chưa kiểm chứng độc lập.
- Nền: Tawosi và cộng sự (2022), TAWOS (arXiv 2202.00979); Tu và cộng sự (2018), lỗi dùng thông tin theo thời gian trong issue tracker; Verenich và cộng sự (2019), dự báo thời gian còn lại trong giám sát quy trình.
Chưa đọc toàn văn: các nguồn "chỉ tóm tắt" phải đọc kỹ trước khi trích số liệu.
