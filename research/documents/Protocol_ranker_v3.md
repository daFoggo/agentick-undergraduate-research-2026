# Protocol bổ sung v3: xếp hạng theo nhóm sprint (`dynamic_catboost_rank`)

Ngày 2026-11-03. Đây là bổ sung ngoài protocol gốc, chưa phải kết quả xác nhận cuối cùng.

## Lý do

Metric chính (Recall@ceil(20%) trong từng sprint) chỉ phụ thuộc thứ tự xếp hạng bên trong một sprint. `dynamic_catboost` là bộ phân loại trộn mọi sprint vào một bảng nên phải học cả mức rủi ro chung của sprint. Đo trên landmark 0, trung bình 31% phương sai nhãn nằm giữa các sprint (từ 12% ở DM đến 43% ở CONFSERVER; tỉ lệ SSB/SST theo project), phần này không giúp xếp hạng trong sprint.

## Mô hình

- `dynamic_catboost_rank`: `CatBoostRanker`, loss `YetiRank`, `group_id = sprint_id`, **cùng feature và cùng siêu tham số** với `dynamic_catboost`. Không tune thêm.
- Điểm số được đưa qua sigmoid (đơn điệu, không đổi thứ tự) để dùng chung bước hiệu chỉnh xác suất. Metric xếp hạng không phụ thuộc bước này.
- Cài đặt: `fit_model`, `predict_scores`, `is_ranker` trong `research/train.py`; test trong `tests/test_rank_model.py`.

## Quy trình đã theo (pilot trước, full sau)

1. Pilot 3 seed, landmark 0, trên tập đặc biệt: temporal DM, CONFSERVER, XD, APIKIT, TISTUD; cross-project DM, XD.
2. Tiêu chí đi tiếp được chốt trước khi xem kết quả: phải ≥ mốc so sánh ở đa số tập, không tập nào tụt vượt nhiễu giữa seed. Nhiễu đo từ độ lệch giữa các seed, không đặt ngưỡng tự do.
3. Chỉ biến thể qua pilot mới vào benchmark full.

## Kết quả âm của các pilot (không vào benchmark full)

| Ý tưởng | Kết quả pilot | Kết luận |
|---|---|---|
| Feature cấu trúc issue thô (link, component, nhãn, epic, rank, bình luận, độ dài mô tả) | CONFSERVER −0,062 (0/10 sprint tốt hơn), TISTUD −0,028, DM ≈ 0, cross-project ≈ 0 | Loại. Nguyên nhân: feature trôi theo thời gian (CONFSERVER: tỉ lệ có epic 33% → 82%, bình luận trung bình 3,4 → 12,2 giữa train và test). Ép số âm về 0 kèm cờ không cứu được |
| Feature tương đối trong sprint (phần trăm thứ hạng trong cùng sprint, cùng landmark), kèm hoặc không kèm feature cấu trúc | Không vượt `rank` ở đa số tập; temporal tụt ở CONFSERVER, XD, APIKIT; cross-project hơn `rank` +0,003 (DM) và +0,013 (XD) | Loại |
| TabPFN | Không chạy | Đã loại trong `Quyet_dinh_lua_chon_phuong_phap_du_bao_v1.md` dựa trên tài liệu |

Số âm trong `n_components` (1.552 dòng), `n_fix_versions` (772), `n_attachments` (56) xuất hiện khi lịch sử thiếu sự kiện "thêm". Ghi nhận là hạn chế của nhóm feature cấu trúc, nhóm này không được dùng tiếp.

## Kết quả benchmark full

3 seed (20261008–10), 14 project đủ điều kiện, 4 landmark, mỗi seed đổi cả cách chia cross-project lẫn seed mô hình. Recall@ceil(20%) trung bình theo sprint, trung bình qua 3 seed.

| Thí nghiệm | Landmark | static | dynamic | **rank** | rule | oracle | rank − dynamic | sd giữa seed | seed rank tốt hơn |
|---|---|---|---|---|---|---|---|---|---|
| temporal | 0 | .461 | .456 | **.477** | .405 | .598 | +.021 | .003 | 3/3 |
| temporal | .25 | .462 | .503 | **.521** | .451 | .598 | +.019 | .008 | 3/3 |
| temporal | .5 | .462 | .533 | **.546** | .481 | .598 | +.014 | .015 | 2/3 |
| temporal | .75 | .462 | .543 | **.568** | .525 | .598 | +.025 | .006 | 3/3 |
| cross-project | 0 | .447 | .447 | **.453** | .367 | .637 | +.006 | .001 | 3/3 |
| cross-project | .25 | .448 | .487 | **.491** | .419 | .637 | +.004 | .002 | 3/3 |
| cross-project | .5 | .448 | .523 | **.530** | .466 | .637 | +.007 | .002 | 3/3 |
| cross-project | .75 | .448 | .574 | **.577** | .535 | .637 | +.003 | .003 | 3/3 |

- Điểm ước lượng của ranker cao hơn `dynamic_catboost` ở cả 8 ô, nhưng khoảng tin cậy chỉ loại trừ 0 ở 3 ô (xem mục bootstrap bên dưới). Ở temporal landmark 0.5, chênh lệch (+0,014) cùng cỡ với độ lệch giữa seed (0,015).
- Cross-project: hiệu ứng nhỏ (+0,003 đến +0,007). Temporal: lớn hơn (+0,014 đến +0,025).
- Đầu sprint vẫn còn khoảng cách tới trần: ở landmark 0, rank đạt 0,80 (temporal) và 0,71 (cross-project) của oracle.

## Bootstrap theo sprint và giả thuyết H1

Mô hình `static_catboost_rank` (cùng ranker, chỉ feature tĩnh) được huấn luyện thêm để H1 vẫn so sánh cùng thuật toán. Mỗi sprint được lấy trung bình recall qua 3 seed, rồi `paired_bootstrap` của dự án (đơn vị sprint, 2000 lần, khoảng tin cậy 95%). Số sprint: 397 (temporal), 1.962 (cross-project). Giá trị là chênh lệch Recall@20% và khoảng tin cậy.

| Thí nghiệm | Landmark | H1 gốc: dynamic − static | H1 mới: rank_dyn − rank_static | Ranker: rank − dynamic |
|---|---|---|---|---|
| temporal | 0 | −.006 [−.014, +.003] | −.004 [−.011, +.001] | +.020 [−.002, +.044] |
| temporal | .25 | **+.041** [+.022, +.061] | **+.040** [+.020, +.060] | **+.018** [+.002, +.034] |
| temporal | .5 | **+.071** [+.050, +.093] | **+.065** [+.044, +.089] | +.014 [−.003, +.029] |
| temporal | .75 | **+.081** [+.056, +.107] | **+.087** [+.062, +.114] | **+.025** [+.010, +.042] |
| cross-project | 0 | −.001 [−.005, +.003] | +.000 [−.002, +.003] | +.007 [−.000, +.014] |
| cross-project | .25 | **+.039** [+.031, +.048] | **+.037** [+.029, +.046] | +.004 [−.003, +.011] |
| cross-project | .5 | **+.075** [+.065, +.085] | **+.076** [+.066, +.087] | **+.007** [+.002, +.013] |
| cross-project | .75 | **+.126** [+.114, +.139] | **+.124** [+.111, +.136] | +.004 [−.000, +.008] |

(In đậm = khoảng tin cậy không chứa 0.)

- **H1 được ủng hộ ở landmark .25, .5, .75 cho cả hai thuật toán** và hai chênh lệch gần như bằng nhau. Kết luận H1 không phụ thuộc việc dùng bộ phân loại hay ranker. Ở landmark 0 không có chênh lệch, đúng như kỳ vọng vì chưa có lịch sử thực thi.
- **Tác dụng riêng của ranker nhỏ và chỉ có ý nghĩa ở 3/8 ô** (temporal .25 và .75, cross-project .5). Với phía static, ranker cũng cho điểm ước lượng dương nhưng không có ý nghĩa (temporal +.019 [−.004, +.042], cross-project +.006 [−.000, +.013]).
- Khoảng tin cậy coi các sprint là độc lập. Sprint trong cùng một project có thể tương quan nên khoảng này có thể hẹp hơn thực tế.

## Kiểm tra tái lập

Mô hình đối chứng (`static_catboost`, `dynamic_catboost`) khớp từng bit với lần rerun sạch trước: temporal 168/168 tệp ở mỗi mô hình và mỗi seed; cross-project seed 0 khớp. Cross-project seed 1 và 2 khác vì lần rerun trước dùng lại cách chia của seed 0 cho mọi seed (chỉ đổi seed CatBoost), còn lần này đổi cả cách chia theo seed. So sánh rank với dynamic luôn là so sánh cặp trong cùng một workspace nên không bị ảnh hưởng.

## Hạn chế

- Mới có 3 seed. Bootstrap theo sprint chưa tính tương quan giữa các sprint cùng project (chưa bootstrap theo project).
- Chưa thử ranker với loss khác (PairLogit, QueryCrossEntropy) và chưa tune; chọn YetiRank trước khi xem kết quả.
- Pilot chỉ chạy landmark 0 trên vài project; quyết định đưa vào full dựa trên các tập đó.
- Thư mục kết quả `artifacts/rerun_v3_rank/` nằm cục bộ vì `.gitignore` chặn `artifacts/*`.
