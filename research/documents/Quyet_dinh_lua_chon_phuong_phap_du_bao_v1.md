# Quyết định lựa chọn phương pháp mô hình dự báo (không tính agent) v1

Ngày: 2026-11-03. Phạm vi: định hướng nghiên cứu tiếp theo cho **tầng dự báo rủi ro** (đề cương mục 5), không bao gồm agent/controller cảnh báo (mục 7). Không sửa protocol/model/kết quả giai đoạn 1–4 đã khóa (`Protocol_v1.md`, `artifacts/protocol/config.json`, `lock.json`). Đây là quyết định định hướng, **chưa chạy thực nghiệm xác nhận (confirmatory)** trên dữ liệu TAWOS thật của đề tài — xem mục Giới hạn.

## Quyết định

Giữ **CatBoost (gradient boosted trees)** làm họ mô hình chính cho tầng dự báo. Không chuyển sang sequence model (LSTM/Transformer học trực tiếp trên raw changelog), không chuyển sang tabular foundation model (TabPFN) làm mô hình chính. Hướng cải tiến được chọn cho v2: mở rộng feature set động đưa vào CatBoost, giữ nguyên khung protocol snapshot 4 mốc (0/25/50/75%) đã khóa.

## Căn cứ

### 1. Quy mô dữ liệu nằm trong vùng tree-based model được benchmark thực nghiệm cho là vẫn SOTA

Cohort đánh giá chính (đã khóa, `Data_card_TAWOS.md`): 18.322 instance, 1.962 sprint, 14 project, 88.588 dòng snapshot. Grinsztajn, Oyallon, Varoquaux, "Why do tree-based models still outperform deep learning on tabular data?" (NeurIPS 2022, [arXiv:2207.08815](https://arxiv.org/abs/2207.08815)) — benchmark 45 dataset, 20.000 giờ compute tuning — kết luận tree ensemble vẫn SOTA ở quy mô dữ liệu trung bình (~10K sample) kể cả khi bỏ qua ưu thế tốc độ huấn luyện. Cohort của đề tài nằm trong vùng quy mô này.

### 2. Per-project minority class nhỏ tới ngưỡng tối thiểu đã tự định nghĩa trong protocol

`artifacts/protocol/config.json` (đã khóa): `min_class_instances=30`, `min_train_class=10`, `min_validation_class=5`, `min_test_class=5`. Train deep sequence model với tối thiểu 10 sample lớp thiểu số/project có rủi ro overfit cao, không đủ gradient signal để học representation có ý nghĩa — đây là ngưỡng do chính nhóm nghiên cứu gốc định nghĩa, không phải suy diễn thêm.

### 3. So sánh tabular foundation model (TabPFN) với GBDT đã tune cho bằng chứng trái chiều

- **TabArena** ([arXiv:2506.16791](https://arxiv.org/abs/2506.16791), đã verify trực tiếp abstract qua WebFetch — không phải chỉ qua tóm tắt vendor như lần trích đầu tiên): kết luận thật **khác** với claim vendor ban đầu — "gradient-boosted trees vẫn là đối thủ mạnh trên dataset tabular thực tế"; deep learning chỉ bắt kịp khi có budget thời gian lớn **và** ensembling; foundation model "excel trên dataset nhỏ" (điều kiện, không phải ưu thế tuyệt đối); TabPFN v2 đứng riêng (không ensemble) **không** được xác nhận thắng tree đã tune trong abstract.
- Phân tích finetuning gradient-based trên TabPFN v2 so với GBDT và mô hình SOTA khác ([arXiv:2506.08982](https://arxiv.org/html/2506.08982v1)): kiểm tra lại ưu thế in-context learning của TabPFN v2 đã công bố trước đó — nguồn này trùng với mục tham khảo [3] bên dưới, không phải nguồn mới.
- Benchmark độc lập ([arXiv:2512.00888](https://arxiv.org/pdf/2512.00888v2)): gain tuyệt đối dưới 1 điểm % so với GBDT đã tune kỹ (so với TabPFN-1.0/TabICL-base, không phải v2).

Bằng chứng không đủ nhất quán để đổi model chính dựa trên literature; cần test trực tiếp trên dữ liệu đề tài mới có thể kết luận (chưa làm — xem mục Giới hạn).

### 4. Sequence model chỉ được literature ghi nhận thắng tabular trên log LỚN

"Revisiting Predictive Process Monitoring in the Age of Foundation Models: A Comparative Study of Sequence, Tabular, and LLM Approaches" ([arXiv:2607.27797](https://arxiv.org/html/2607.27797)) — qua tóm tắt tìm được: sequence model dẫn đầu về next-activity accuracy nói chung; tabular model "trailed the Transformer on a large log". Hàm ý ngược lại (tabular không thua) có thể đúng trên log không lớn như TAWOS cohort, nhưng **đây mới chỉ là suy luận từ motivation/abstract qua công cụ search, chưa đọc được số liệu thực nghiệm đầy đủ của paper** — không trích số liệu cụ thể từ nguồn này cho báo cáo chính thức trước khi đọc lại full text.

### 5. Chuỗi event per-issue ngắn, vocabulary trạng thái nhỏ

Changelog toàn nguồn TAWOS: 9.253.419 dòng / 458.232 issue ≈ 20 event/issue tính trung bình — con số này gộp **mọi** loại field thay đổi (priority, assignee, v.v.), không riêng status transition liên quan trực tiếp đến bài toán. Vocabulary trạng thái Jira hữu hạn, thường dưới 10 loại mỗi dự án. Không gian pattern thứ tự cho sequence model khai thác tương đối hẹp so với lợi thế cần có để vượt feature đã nén thủ công (số lần đổi trạng thái, thời gian ở trạng thái hiện tại — đã có trong feature set hiện tại).

## Phương án bị loại và lý do ngắn

| Phương án | Lý do không chọn làm model chính |
|---|---|
| TabPFN v2/2.5 | Gain so với GBDT tune kỹ trái chiều giữa nguồn (mục 3); chưa test trên dữ liệu thật của đề tài |
| Sequence model (LSTM/Transformer trên raw changelog) | Cỡ mẫu tổng và per-project nhỏ hơn vùng literature cho thấy deep model cần để vượt GBDT (mục 1, 2); sequence per-issue ngắn, vocabulary nhỏ (mục 5) |
| Self-supervised (SiamSA-PPM, [arXiv:2507.18293](https://arxiv.org/abs/2507.18293v1)) | Chỉ validate trên benchmark process-mining khác domain (ví dụ BPIC12/Sepsis theo một aggregator bên thứ ba, **chưa xác nhận trực tiếp từ bài gốc**), chưa có bằng chứng transfer sang issue-tracker; rủi ro adaptation cao |
| Survival/discrete-time hazard model | Đã nằm trong "hướng mở rộng" mục 10 đề cương gốc — không phải điều kiện hoàn thành đề tài chính; cải thiện format output (một đường xác suất liên tục thay 4 mốc rời rạc), không có cơ sở cho rằng sẽ cải thiện accuracy |

## Hướng cải tiến v2 — ĐÃ CHẠY THỰC NGHIỆM, KẾT QUẢ TIÊU CỰC (cập nhật 2026-11-03)

Đã test momentum/rolling-window (`status_changes_3d/7d`, `events_3d/7d`) theo `Protocol_feature_v2_momentum.md` trên dữ liệu TAWOS thật (migrate lại, parity-verified byte-for-byte với split gốc). Kết quả: **không cải thiện** — Δrecall@20% ≈ 0 (CI chứa 0 cả temporal và cross-project), AP/Brier xấu hơn nhẹ. Xem chi tiết số liệu trong `Protocol_feature_v2_momentum.md` mục Kết quả.

**Feature quan hệ từ `tawos_raw.issue_link`** — loại khỏi scope: bảng không có cột timestamp, không thể tính as-of an toàn, có rủi ro leakage nếu dùng trạng thái link hiện tại.

Hướng "mở rộng feature trong khung tabular hiện tại" do đó **chưa tìm được cải tiến nào vượt baseline CatBoost hiện tại** sau khi test cụ thể hướng dễ nhất (momentum). Quyết định giữ CatBoost ở mục trên vẫn đúng; chỉ riêng đề xuất cải tiến feature cụ thể này bị bác bỏ bằng thực nghiệm, không còn là "đề xuất chưa test".

**Cập nhật sau rà soát (2026-11-03)**: kết quả v2 ở trên được tạo trước khi sửa hai lỗi (baseline tĩnh nhiễm feature momentum; story points luôn rỗng). Chạy lại sạch với 3 seed cho cùng kết luận: v2 − dynamic nằm trong ±0,004, trong dao động giữa các seed. Chi tiết và số liệu: `Protocol_feature_v2_momentum.md` mục "Bổ sung 2026-11-03". Hệ quả cho các hướng tiếp theo:

- Metric Recall@20% có trần thấp (oracle 0,598 temporal; 0,637 cross-project do ~57% issue rủi ro so với ngân sách 20%), và cuối sprint mô hình đã đạt 0,89–0,91 của trần. Cải tiến tiếp theo nên báo cáo thêm recall/oracle và đường recall theo ngân sách, và đặt `Rule` (luật đơn giản theo `is_done`) làm baseline ở mọi landmark.
- Dư địa nằm ở **đầu sprint** (landmark 0: dynamic ≈ static, 0,70–0,76 của oracle). Các hướng thêm feature nhắm vào giai đoạn này đã được thử và không thắng (xem mục "Chốt phương pháp" bên dưới).
- Các ý tưởng đã thử nhanh và không cho tín hiệu: carry-over (trùng feature hiện có), lịch sử đội (hằng số trong sprint), tỉ lệ tải (không tín hiệu), trộn mô hình pooled/local (0,4952 so với 0,4922 ở landmark 0; 0,5879 so với 0,5878 ở landmark 0,5). Các kết quả này là thăm dò, chưa lặp seed.

## Chốt phương pháp (2026-11-03)

**Mô hình chính: `dynamic_catboost`** (CatBoost phân loại, feature lịch sử as-of; baseline gồm `static_catboost` và `Rule` theo `is_done`). Số liệu và quy trình: `Protocol_feature_v2_momentum.md`, `Protocol_ranker_v3.md`.

**Kết luận H1 (lịch sử thực thi có giá trị):** được ủng hộ ở landmark .25, .5, .75 trên cả test và validation, cho cả bộ phân loại lẫn ranker (+3 đến +13 điểm Recall@20%, khoảng tin cậy 95% không chứa 0). Ở landmark 0 không có chênh lệch, vì chưa có lịch sử.

**Đã thử và loại (kèm bằng chứng):**

| Hướng | Kết quả |
|---|---|
| Feature momentum v2 | v2 − dynamic trong ±0,004 (3 seed, baseline sạch) |
| Feature cấu trúc issue thô | Tụt ở CONFSERVER (−0,062) và TISTUD (−0,028); nguyên nhân là dữ liệu trôi theo thời gian |
| Feature tương đối trong sprint | Không vượt ranker ở đa số tập pilot |
| Văn bản issue (TF-IDF + LR) | Validation: C − B = −0,0004 [−0,011, +0,010] |
| Ranker theo nhóm sprint | Giữ làm mô hình bổ sung: cross-project +0,3 đến +0,6 điểm (tái lập trên validation), temporal không tái lập |
| TabPFN | Loại từ tài liệu (mục 3), chưa chạy |

**Cách báo cáo:** nêu Recall@20% cùng recall/oracle và khoảng tin cậy bootstrap; báo cáo đường ngân sách bên dưới thay vì chỉ một mốc 20%; không nêu lợi ích temporal của ranker; mọi biến thể mới phải chọn bằng validation, không bằng test (bài học từ rủi ro chọn biến thể ở `Protocol_ranker_v3.md`).

**Đường ngân sách của `dynamic_catboost`** (temporal, test, trung bình 3 seed; mô tả, không dùng để chọn mô hình). Ngân sách thực tế cao hơn mức danh nghĩa (17,3% / 25,8% / 35,9%) vì làm tròn lên ở các sprint nhỏ. Tỉ lệ issue rủi ro là 57%.

| Landmark | Ngân sách | Precision | Precision oracle | Recall |
|---|---|---|---|---|
| 0 | 10% | .696 | .841 | .387 |
| 0 | 20% | .674 | .826 | .456 |
| 0 | 30% | .657 | .802 | .549 |
| .25 | 20% | .715 | .826 | .503 |
| .5 | 20% | .752 | .826 | .533 |
| .75 | 10% / 20% / 30% | .778 / .765 / .746 | .841 / .826 / .802 | .452 / .543 / .649 |

Precision gần như phẳng theo ngân sách: ở landmark 0, tăng ngân sách từ 20% lên 30% làm recall tăng 9,3 điểm trong khi precision giảm 1,7 điểm. Bảng đầy đủ: `artifacts/rerun_v3_rank/budget_table.csv` (cục bộ).

**Khuyến nghị vận hành (không phải kết luận thực nghiệm):** lịch sử chỉ có giá trị từ landmark .25, nên cảnh báo ở đầu sprint chỉ nên coi là thứ tự ưu tiên thô (dynamic ≈ static). Mốc ngân sách phụ thuộc năng lực xử lý cảnh báo của đội; protocol không chứng minh một mốc tối ưu.

**Chưa làm, để mở:** (1) ngân sách thích ứng theo sprint, vì 31% phương sai nhãn nằm giữa các sprint; hướng này đổi định nghĩa bài toán nên cần quyết định và sửa protocol trước; (2) embedding văn bản mạnh hơn TF-IDF; thăm dò đơn giản không cho tín hiệu nên ưu tiên thấp.

**Giới hạn:** 3 seed; bootstrap theo sprint chưa tính tương quan giữa các sprint cùng project; dữ liệu TAWOS, chưa kiểm chứng trên dữ liệu Agentick thực.

## Điều kiện revisit quyết định này

Không coi đây là quyết định vĩnh viễn. Revisit khi: (a) dữ liệu sản xuất thật từ Agentick vượt đáng kể quy mô ~10K instance đã dẫn ở mục 1, hoặc (b) xuất hiện loại dữ liệu không thể nén hợp lý thành feature tabular (ví dụ ảnh, audio, log hệ thống phi cấu trúc lớn). Không thiết kế trước cho dữ liệu giả định chưa tồn tại.

## Giới hạn của chính quyết định này

- Đây là quyết định **định hướng** dựa trên literature benchmark tổng quát (Grinsztajn et al. áp dụng cho 45 dataset nói chung, không phải benchmark riêng cho bài toán sprint-risk) kết hợp số liệu quy mô của chính cohort — **không phải kết quả thực nghiệm so sánh trực tiếp CatBoost vs sequence/TabPFN trên TAWOS**. Nếu cần trình bày là kết luận thực nghiệm, phải chạy so sánh thật trước (yêu cầu build lại `data/processed/` + train — việc nặng, chưa thực hiện).
- Nguồn mục 4 ([arXiv:2607.27797](https://arxiv.org/html/2607.27797)) chỉ đọc được qua tóm tắt công cụ search tại 2026-11-03, chưa đọc full text/số liệu — không trích số liệu cụ thể từ nguồn này nếu đưa vào báo cáo/luận văn chính thức trước khi đọc lại trực tiếp.
- Momentum/rolling-window **đã chạy thật** (2026-11-03), kết quả tiêu cực — xem `Protocol_feature_v2_momentum.md`. Đây là 1 lần chạy duy nhất (không lặp seed/bootstrap train nhiều lần như phase 4 làm cho H1 chính), nên chỉ coi là tín hiệu đủ mạnh để bác bỏ hướng này (effect gần 0, chiều nhất quán xấu đi ở mọi metric phụ), không phải mức rigor đầy đủ của nghiên cứu chính. `issue_link` vẫn chưa test (bị loại do thiếu timestamp, không phải do kết quả xấu).
- TabPFN v2 cụ thể (bản mới nhất) chưa được test trực tiếp trên dữ liệu đề tài; bằng chứng mục 3 đến từ dataset khác.
- Chi tiết dataset benchmark của SiamSA-PPM (BPIC12/Sepsis, mục "Phương án bị loại") đến từ một aggregator bên thứ ba, chưa xác nhận trực tiếp từ bài gốc.

## Tài liệu tham khảo

1. Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). *Why do tree-based models still outperform deep learning on tabular data?* NeurIPS 2022. [arXiv:2207.08815](https://arxiv.org/abs/2207.08815)
2. *Revisiting Predictive Process Monitoring in the Age of Foundation Models: A Comparative Study of Sequence, Tabular, and LLM Approaches.* [arXiv:2607.27797](https://arxiv.org/html/2607.27797) — chỉ đọc qua tóm tắt, xem Giới hạn.
3. *On Finetuning Tabular Foundation Models.* [arXiv:2506.08982](https://arxiv.org/html/2506.08982v1) — trích ở mục Căn cứ 3.
4. Independent hardware-cost benchmark, tuned GBDT vs TabPFN-1.0/TabICL-base. [arXiv:2512.00888](https://arxiv.org/pdf/2512.00888v2)
5. van Straten, S., Padella, A., & Hassani, M. (2025). *Leveraging Data Augmentation and Siamese Learning for Predictive Process Monitoring* (SiamSA-PPM). CoopIS 2025. [arXiv:2507.18293](https://arxiv.org/abs/2507.18293v1)
5b. *TabArena: A Living Benchmark for Machine Learning on Tabular Data.* [arXiv:2506.16791](https://arxiv.org/abs/2506.16791) — trích ở mục Căn cứ 3; abstract đã verify qua WebFetch 2026-11-03, chưa đọc full text/bảng số liệu.
6. `Data_card_TAWOS.md` (nội bộ, đã khóa 2026-10-08) — số liệu cohort.
7. `artifacts/protocol/config.json` (nội bộ, đã khóa) — ngưỡng `min_class_instances`/`min_train_class`/`min_validation_class`/`min_test_class`.
8. `De_cuong_du_bao_som_rui_ro_sprint.md` mục 4.3, 5.1, 10 (nội bộ) — nguyên tắc as-of, danh sách mô hình so sánh đã đăng ký, hướng mở rộng ngoài scope v1.
