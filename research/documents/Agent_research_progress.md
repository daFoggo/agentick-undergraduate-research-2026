# Tiến độ nghiên cứu agent cảnh báo chủ động

Ngày 2026-10-08. Tiếp nối phase 4 nhưng không sửa study frozen. Người dùng yêu cầu deep research theo SOTA nhất có thể, tạo lộ trình và thực hiện đánh giá theo quy trình trước.

Format mỗi batch: mục tiêu; protocol/version/hash; trạng thái; commands; evidence/metrics; limitations; quyết định; next step. DONE chỉ khi có verification.

- [x] Research nhiều vòng và tổng hợp 15 nguồn chính, đánh dấu mức đọc và giới hạn.
- [x] Thiết kế ba lớp model/controller/tool agent, baselines/ablation và human study.
- [x] Protocol E1 và lộ trình triển khai được viết trước metric mới.
- [x] E1 policy replay, CI, audit và báo cáo (post-hoc exploratory).
- [ ] E2 validation/serving parity và chọn calibration cho deployment (serving adapter parity đã PASS 18 bundles).
- [x] E3 technical agent benchmark — **đã chạy Protocol E3 v2 trên bộ Full 50 kịch bản (1 lần lặp, 150 lượt chạy)**. `ClaimGrader` chấm độc lập trên đầu ra thô, không vá đầu ra bằng ground-truth; kịch bản đa sự kiện (`agent_scenarios_v2.py`). Cả A0/A1/A2 đạt 100% evidence recall, grounding precision và numeric accuracy; decision accuracy A0 100%, A1/A2 98%. Template A0 ngang hoặc hơn agent, nên chưa có bằng chứng LLM agent tăng độ chính xác. Chưa lặp ≥3 lần. Chi tiết: `artifacts/agent_extension/agent_v2/eval_report_full.md`.
- [ ] E4 human decision study / opt-in pilot.
- [ ] Manuscript extension bằng kết quả mới.

## Checkpoint hiện tại

E1 đã kết thúc exit 0 bằng `.venv/Scripts/python.exe -m research.agent_policy_experiment`. 252 input files, 96 cells, 24 CI contrasts, 113.232 sprint metric rows và 180.638 alert rows. Đã đọc kết quả sau run và viết `Phan_tich_policy_agent_E1.md`.

E2 phục vụ: `app/services/risk_inference.py` tái dùng prepare/logit từ research code, `research.validate_serving_parity` pass 18 trusted local bundles / 180 snapshots (atol=1e-12).

E3 Technical Agent Evaluation — **HOÀN THÀNH TRÊN FULL SUITE (50 KỊCH BẢN, 2026-10-08 theo Protocol E3 v2)**:
- Đã khắc phục triệt để các hạn chế của v1: `ClaimGrader` chấm độc lập trên đầu ra thô, `parse_claim_strict` không tự ý vá ground-truth, `GeminiClient` đưa key vào header + generationConfig + tự động retry 5 lần (429 rate limit resilience).
- Bộ kịch bản đa sự kiện (`research/agent_scenarios_v2.py`) có đủ 5 lớp probe với 10 kịch bản mỗi lớp (tổng cộng 50 kịch bản): rò rỉ tương lai (10), xuyên dự án (10), prompt injection (10), nhiệm vụ bình thường (10) và nhiệm vụ hoàn thành / an toàn (10).
- Kết quả benchmark (`artifacts/agent_extension/agent_v2/eval_report_full.md`, model `gemini-3.5-flash-lite`):
  * **Evidence Recall / Grounding Precision / Numeric Accuracy:** 100,0% ở cả A0, A1, A2 (hiệu ứng trần: mỗi kịch bản chỉ có 3 sự kiện vàng, mốc 0,5).
  * **Decision Accuracy:** A0 100,0%; A1 98,0%; A2 98,0%. A1 và A2 cùng cảnh báo thừa ở kịch bản `SCEN-V2-NORMAL_STAGNATION-MULE-4438-389943` (kỳ vọng `abstain`, điểm rủi ro 0,35, issue thực tế hoàn thành).
  * **Tool calls:** A2 trung bình 1,0 lượt (`get_issue_evidence`). Độ trễ p50/p95: A1 1,67/2,07 s; A2 2,67/17,34 s.
  * **Diễn giải:** pipeline bằng chứng + verifier hoạt động đúng trên 5 lớp probe; template A0 (không LLM, chi phí 0) là mức sàn khó vượt. Không được trình bày là "agent chống bịa đặt tuyệt đối".
  * **Test suite:** 68 test. Lần chạy 08/10/2026 trên máy không có tệp dữ liệu archival: 66 đạt, 2 lỗi `FileNotFoundError` ở `test_agent_evaluation.py::test_evaluate_single_run_a0` và `test_agent_scenarios.py::test_load_dev_scenarios` (lỗi môi trường, không phải lỗi logic).

Kết quả E1 dynamic/K2 temporal: quota early macro recall 58,77%, midpoint 59,20%; delta -0,43 pp CI [-1,36; 0,55]. Quota lead days conditional 8,18 vs 6,29, precision micro 77,31% vs 79,70%. Không kết luận superior/causal; cohort/cap khác H1 cũ. Decision A10: giữ midpoint/rule và quyền abstain làm đối chứng cho policy mới; không tune bằng E1. CSV lớn giữ local, manifest SHA và summary/CI/audit tracking Git. Lưu ý sau review: metric chính early-recall thiên lệch cấu trúc về midpoint dồn toàn cap (delta −12,7 pp ở K=3 phần lớn là cơ học); “independent audit” là audit thứ cấp cùng toolchain.

Next safe step (cập nhật 08/10/2026 sau báo cáo tiến độ): tích hợp mô hình dự báo và agent vào Agentick (endpoint dự báo, ledger/outbox, bảng cảnh báo, dry-run), rồi shadow mode; xem roadmap trong [Thuyet_minh_bao_cao_tien_do.md](Thuyet_minh_bao_cao_tien_do.md) mục 9. Checklist cũ: thực hiện checklist trong [Danh_gia_va_checklist_chinh_sua.md](Danh_gia_va_checklist_chinh_sua.md) theo thứ tự T0 → T6 trước khi gọi LLM thật. E2 (validation scores mới, registry), ledger/outbox và E4 (người tham gia/consent) chưa thực hiện, không được báo DONE.

Quy ước E-number chuẩn: E1 policy replay; E2 serving/validation; E3 agent kỹ thuật; E4 nghiên cứu với người; E5 can thiệp.

Decision A07: E1 dùng raw ranking/fixed policies, mọi kết quả exploratory trên frozen test cũ, không tune/chọn champion. A08: evidence mới chỉ về policy replay, không agent hoặc causal improvement. A09: provider/human dependency được báo trạng thái NOT RUN, không thay bằng lời hứa tự hoàn thành.
Decision A11 (review 2026-10-08): kết quả `agent_v1` không được trích dẫn ở bất kỳ báo cáo/paper nào; chỉ benchmark được khóa trước và có negative control mới được dùng. A12: không sửa `Protocol_agent_extension_v1.md` (validator E1 kiểm hash); amendment đi vào `Protocol_agent_E3_v2.md`.

