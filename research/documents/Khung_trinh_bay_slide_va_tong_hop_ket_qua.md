# TỔNG HỢP KẾT QUẢ NGHIÊN CỨU VÀ KHUNG TRÌNH BÀY SLIDE

**Đề tài:** Nghiên cứu mô hình đánh giá rủi ro trễ hạn công việc trong sprint và xây dựng agent hỗ trợ can thiệp sớm (04-SV-2026-RIPT)
**Ngày cập nhật:** 08/10/2026
**Bộ slide:** `slide-template/` (Beamer, build bằng `latexmk -xelatex main.tex`); lời nói từng slide: `slide-template/script.md`
**Thuyết minh đi kèm:** [Thuyet_minh_bao_cao_tien_do.md](Thuyet_minh_bao_cao_tien_do.md)

Tài liệu này tóm tắt các con số được dùng trong slide và liệt kê cấu trúc 20 slide. Khi slide, thuyết minh và tài liệu này khác nhau, số liệu gốc nằm trong `artifacts/results/` và `artifacts/agent_extension/`.

---

## PHẦN I: TỔNG HỢP KẾT QUẢ

Mọi kết quả định lượng lấy từ benchmark trên TAWOS v1.1. Mô hình và agent **chưa tích hợp vào Agentick**, nên chưa có dữ liệu sử dụng thật.

### 1. Kiến trúc hai tầng

```text
┌──────────────────────────────────────┬──────────────────────────────────────┐
│ TẦNG 1: MÔ HÌNH DỰ BÁO + CONTROLLER  │ TẦNG 2: AGENT LẬP BRIEF              │
│ (không dùng LLM)                     │                                      │
│ - CatBoost động, mốc 50% sprint      │ - LLM gemini-3.5-flash-lite          │
│ - Ngân sách ⌈0,2n⌉ cảnh báo/sprint   │ - Công cụ chỉ đọc: get_issue_evidence│
│ - Quyết định KHI NÀO và ISSUE NÀO    │   get_sprint_summary                 │
│                                      │ - Mỗi khẳng định trích event_id      │
│                                      │ - EvidenceVerifier chặn brief sai    │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

### 2. Tham số vận hành

- **Mốc dự báo 50%** là mốc của giả thuyết chính, đã đăng ký trước. Không phải mốc "tối ưu": mốc muộn hơn cho recall cao hơn nhưng lead time ngắn hơn (bảng ở mục 3.2).
- **Ngân sách chính** là ⌈0,2n⌉ cảnh báo cho sprint *n* issue. Do 207/397 sprint test có dưới 5 issue, tỷ lệ cảnh báo thực tế là 41,54% (macro) / 25,81% (micro), không phải 20%.
- **K = 2** (tổng cảnh báo cố định mỗi sprint, chỉ issue còn mở) là giá trị được khảo sát trong phân tích phân bổ cảnh báo E1 và dùng để sinh kịch bản agent. Đây **không** phải giá trị đã chứng minh là tối ưu.

### 3. Kết quả mô hình dự báo (giai đoạn 1–4)

#### 3.1. Giả thuyết chính tại mốc 50%

| Thiết kế | Recall tĩnh | Recall động | Chênh lệch | CI 95% |
|---|---:|---:|---:|---|
| Temporal (336 sprint) | 44,46% | 53,36% | +8,90 | [6,38; 11,70] |
| Cross-project (14 dự án) | 43,56% | 53,52% | +9,96 | [7,53; 12,82] |

Với cùng 850 cảnh báo (temporal): phát hiện 682 so với 605 issue trễ (trên 1.883); precision gộp 80,24% so với 71,18%; cảnh báo sai 0,42 so với 0,62 mỗi sprint.

#### 3.2. Theo mốc (temporal)

| Mốc | 0% | 25% | 50% | 75% |
|---|---:|---:|---:|---:|
| Recall động | 45,12% | 50,22% | 53,36% | 54,55% |
| Chênh lệch (điểm %) | +0,66 (CI chứa 0) | +5,76 | +8,90 | +10,09 |
| Lead time trung bình | ~12,6 ngày | ~9,5 ngày | ~6,3 ngày | ~3,1 ngày |

#### 3.3. Những điểm phải nói rõ

- Chỉ xét issue còn mở: chênh lệch còn +2,59 [0,68; 4,69] (temporal), +2,03 [0,73; 3,58] (cross-project). Phần lớn lợi thế đến từ việc nhận ra issue đã Done.
- So với quy tắc nghiệp vụ trên temporal: +2,13 [−0,33; 4,60], CI chứa 0, nên chưa chứng minh ML hơn quy tắc.
- Cross-project: hiệu chuẩn không cải thiện Brier (0,1374 → 0,1381); cần hiệu chuẩn lại trên dữ liệu Agentick.
- Lead time **8,30 ngày** thuộc về *cảnh báo tuần tự* (recall 51,56%, precision 77,67%), **không** đi kèm recall 53,36% của cảnh báo một lần ở mốc 50% (lead time ~6,3 ngày).
- Phân bổ cảnh báo (K = 2, temporal): quota sớm hơn ~1,9 ngày (8,18 so với 6,29) nhưng không tăng recall (−0,43 [−1,36; 0,55]).

### 4. Kết quả kỹ thuật của agent (Protocol E3 v2)

Bộ 50 kịch bản từ TAWOS (mốc 0,5; 3 sự kiện vàng mỗi kịch bản; 5 lớp probe × 10), 1 lần lặp, model `gemini-3.5-flash-lite`:

| Chỉ số | A0 Template (không LLM) | A1 Narrator | A2 Bounded Tool Agent |
|---|---:|---:|---:|
| Evidence Recall | 100,0% | 100,0% | 100,0% |
| Grounding Precision | 100,0% | 100,0% | 100,0% |
| Numeric Accuracy | 100,0% | 100,0% | 100,0% |
| Decision Accuracy | 100,0% | 98,0% | 98,0% |
| Tool calls trung bình | 0 | 0 | 1,0 |
| Độ trễ p50 / p95 | 0 / 0 s | 1,67 / 2,07 s | 2,67 / 17,34 s |

**Cách trình bày:** cả ba biến thể đạt trần về trích dẫn, nên kết quả xác nhận pipeline bằng chứng và verifier hoạt động đúng, kể cả với probe rò rỉ tương lai, truy cập dự án khác và prompt injection. Template A0 ngang hoặc hơn agent với chi phí bằng 0, nên **chưa có bằng chứng LLM agent tốt hơn template về độ chính xác**. A1 và A2 cùng cảnh báo thừa một kịch bản (MULE, kỳ vọng `abstain`). Không dùng các cụm "chống bịa đặt tuyệt đối" hay "chính xác tuyệt đối".

### 5. Kiểm thử tự động

68 test. Lần chạy 08/10/2026: 66 đạt, 2 lỗi `FileNotFoundError` do máy chạy không có tệp dữ liệu archival mà bước sinh kịch bản cần (lỗi môi trường, không phải lỗi logic).

---

## PHẦN II: CẤU TRÚC BỘ SLIDE (20 SLIDE)

| # | Slide | Tệp | Nội dung chính |
|---|---|---|---|
| 1 | Tiêu đề | `main.tex` | Tên đề tài, mã 04-SV-2026-RIPT, chủ trì, GVHD |
| 2 | Bối cảnh và bài toán | `01-setup.tex` | 47,21% cặp issue–sprint không hoàn thành; RQ1–RQ3; giả thuyết chính; hai phần mô hình + agent |
| 3 | Dữ liệu TAWOS và thiết kế đánh giá | `01-setup.tex` | 39 → 14 dự án, 18.322 cặp; nhãn; temporal (purge 128 cặp) và cross-project |
| 4 | Đặc trưng và mô hình | `02-method.tex` | 5 nhóm đặc trưng; 6 mô hình; cấu hình CatBoost |
| 5 | Cảnh báo theo ngân sách và cách đọc chỉ số | `02-method.tex` | ⌈0,2n⌉; paired bootstrap 2.000 lần; bảng ý nghĩa chỉ số |
| 6 | Kết quả chính | `03-results.tex` | +8,90 / +9,96 điểm, CI không chứa 0; cùng 850 cảnh báo |
| 7 | Chính xác hơn nhưng muộn hơn | `03-results.tex` | Recall và lead time theo 4 mốc |
| 8 | Kiểm tra độ vững | `03-results.tex` | Làm tròn xuống, chỉ issue còn mở, chỉ Closed; ba lưu ý |
| 9 | Chất lượng xác suất | `03-results.tex` | AP, Brier, intercept/slope; cross-project không cải thiện Brier |
| 10 | So với quy tắc và giữa các dự án | `03-results.tex` | Chưa chứng minh ML hơn quy tắc (temporal); dương ở cả 14 dự án |
| 11 | Phân bổ cảnh báo theo thời gian | `03-results.tex` | Quota và midpoint với K = 2; sớm hơn ~1,9 ngày, không tăng recall |
| 12 | Kiến trúc agent hai tầng | `04-agent.tex` | Sơ đồ tầng 1 / tầng 2; công cụ; verifier; cấu hình LLM |
| 13 | Agent làm được gì | `04-agent.tex` | Bảng khả năng; ràng buộc cài trong mã |
| 14 | Ví dụ: agent gọi công cụ | `04-agent.tex` | Trace thật issue 177929 (CONFSERVER) |
| 15 | Ví dụ: brief agent trả về | `04-agent.tex` | Quyết định `alert`, khẳng định đình trệ 7,0 ngày, 3 `event_id` |
| 16 | Giới hạn | `05-next.tex` | 7 giới hạn, đứng đầu là chưa triển khai trên Agentick |
| 17 | Tiến độ hiện tại | `05-next.tex` | Đã xong / đang chờ |
| 18 | Roadmap và kế hoạch | `05-next.tex` | 4 giai đoạn từ T0: tích hợp, kiểm tra agent, shadow mode, báo cáo cuối |
| 19 | Tóm tắt | `05-next.tex` | Bốn ý kết luận |
| 20 | Tài liệu tham khảo | `05-next.tex` | 6 nguồn chính |

Bộ slide hiện chưa có slide riêng cho bảng E3 v2 (mục I.4). Nếu hội đồng hỏi về đánh giá agent, trả lời theo bảng ở mục I.4 và nhấn mạnh: template ngang agent, kết quả chỉ xác nhận cơ chế kiểm tra bằng chứng.
