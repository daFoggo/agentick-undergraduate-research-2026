# Protocol feature v2 — momentum/rolling-window

Ngày: 2026-11-03. Khóa specification trước khi build/train. Không sửa `research/build.py`/`research/replay.py` phần feature đã khóa (static_*, dynamic_* hiện có) — chỉ **thêm** cột mới, không đổi/xóa cột cũ. Không chạy trên artifact phase 1–4 gốc (không tồn tại trên máy này) — đây là **run mới, độc lập**, trên data đã migrate lại từ TAWOS gốc (checksum khớp, xem migration log 2026-11-02/03).

## Phạm vi

Chỉ thử nghiệm feature **momentum/rolling-window** từ `change_log` (đã có timestamp, an toàn as-of). **Loại bỏ** feature quan hệ từ `tawos_raw.issue_link` khỏi v2: bảng này không có cột timestamp (`\d tawos_raw.issue_link` xác nhận), không thể biết link được tạo trước hay sau mốc dự báo — nguy cơ leakage, không build.

## Feature mới (thêm vào `Timeline.features`, giữ nguyên feature cũ)

Tính tại `at` (mốc dự báo), chỉ dùng `self.before(at)` — không khác nguyên tắc as-of hiện có:

- `dynamic_status_changes_3d`: số status-change event trong `[at-3 ngày, at]`.
- `dynamic_status_changes_7d`: số status-change event trong `[at-7 ngày, at]`.
- `dynamic_events_3d`: số event (mọi field quan sát) trong `[at-3 ngày, at]`.
- `dynamic_events_7d`: số event trong `[at-7 ngày, at]`.

Không thêm feature nào dùng dữ liệu sau `at`.

## Model variant mới

Thêm `dynamic_catboost_v2` vào `feature_columns()` (train.py): = cột của `dynamic_catboost` (baseline, không đổi) **cộng thêm** 4 cột trên. `dynamic_catboost` (baseline) giữ nguyên cột như cũ — không tự động nhận cột mới, để số liệu baseline reproduce đúng, so sánh công bằng.

## Thiết kế so sánh

- Dùng đúng CatBoost config đã khóa (`iterations=400, depth=5, lr=.05, l2=5`), đúng landmark {0, .25, .5, .75}, đúng split temporal (60/20/20 theo thời gian) và cross-project (leave-one-project-out) — không đổi protocol split/eligibility.
- Primary contrast: `dynamic_catboost_v2` vs `dynamic_catboost` tại landmark 0.5, metric PR-AUC + Recall@budget 20% (ceil), test set, cùng cách đã dùng ở phase 4 (`research/evaluate.py`).
- Đây là **run mới trên data mới migrate**, không phải kết quả phase 1–4 gốc — số liệu baseline (`dynamic_catboost`) ở run này dùng để **sanity-check parity** với số đã công bố (recall ~53.36% temporal tại landmark 0.5, budget 20%), không dùng để thay thế kết quả gốc đã khóa.
- Không chọn feature/model theo test. Train trên train, chọn/calibrate trên validation, chỉ xem test sau khi toàn bộ train/validation đã cố định.

## Điều kiện kết luận

"v2 tốt hơn" chỉ được báo cáo nếu: (a) parity check baseline khớp số đã công bố trong khoảng hợp lý (cho thấy pipeline/migration đúng), và (b) `dynamic_catboost_v2` thắng `dynamic_catboost` trên test với chênh lệch có ý nghĩa (không chỉ do nhiễu seed đơn — đây là 1 lần chạy, không bootstrap CI đầy đủ như phase 4, phải ghi rõ là exploratory single-run, không phải confirmatory).

## Kết quả (2026-11-03, đã chạy thật)

Parity check trước khi tin kết quả: build lại từ Postgres cho đúng 88.588 snapshot / 22.147 instance / 2.555 sprint (khớp `Data_card_TAWOS.md`); `eligibility.csv`/`temporal_split_manifest.csv`/`cross_project_split_manifest.csv` **giống byte-for-byte** bản đã tracked trong git. Baseline `dynamic_catboost` vs `static_catboost` tái lập được chiều và độ lớn hiệu ứng đã công bố (temporal +7.69pp CI[5.26,10.33] so với công bố +8.90pp CI[6.38,11.70]; cross-project +9.45pp CI[6.97,12.30] so với công bố +9.96pp CI[7.53,12.82] — sai khác nhỏ do CatBoost không hoàn toàn deterministic giữa hai lần train, không phải lỗi pipeline).

**Primary contrast `dynamic_catboost_v2` vs `dynamic_catboost`, landmark 0.5, test, budget ceil(20%)**:

| Experiment | Δ Recall@20% | CI 95% | n_units |
|---|---:|---|---:|
| Temporal | −0.0009 | [−0.0155, 0.0142] | 336 sprint |
| Cross-project | −0.0016 | [−0.0050, 0.0018] | 14 project |

Probability metrics (raw score, landmark 0.5): AP và Brier đều **xấu hơn nhẹ** ở `dynamic_catboost_v2` so với baseline, cả temporal và cross-project (AP 0.8810 vs 0.8867 temporal; 0.8336 vs 0.8366 cross-project; Brier 0.1272 vs 0.1239 temporal; 0.1382 vs 0.1378 cross-project).

**Kết luận**: momentum/rolling-window feature **không cải thiện** dự báo — CI chứa 0 ở cả hai experiment, và chiều hiệu ứng (nếu có) là tiêu cực nhẹ trên mọi metric. Không đạt điều kiện "v2 tốt hơn" đã đặt ra trước khi chạy. Đây là **kết quả hợp lệ** (phủ định giả thuyết cải tiến), không phải thất bại pipeline — khớp với lập luận mục 5 của `Quyet_dinh_lua_chon_phuong_phap_du_bao_v1.md` (chuỗi event ngắn, feature cũ đã nắm được phần lớn tín hiệu).

## Giới hạn đã biết trước khi chạy

- 1 lần chạy, không lặp/bootstrap CI như phase 4 → kết luận chỉ là tín hiệu ban đầu, không phải bằng chứng thống kê chặt.
- issue_link bị loại hoàn toàn khỏi scope v2 (lý do: thiếu timestamp).
- Dữ liệu được migrate lại từ TAWOS gốc (không phải data/processed gốc đã mất trên máy này) — cohort/exclusion log sẽ được tạo lại, cần so khớp số lượng (project/sprint/instance) với `Data_card_TAWOS.md` trước khi tin tưởng kết quả.
