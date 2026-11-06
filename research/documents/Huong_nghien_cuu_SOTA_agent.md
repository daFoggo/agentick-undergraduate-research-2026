# Hướng nghiên cứu agent (SOTA) cho bài toán cảnh báo rủi ro sprint

Ngày 2026-11-05. Bài toán đề cương (rủi ro sprint, người duyệt, Plane) giữ nguyên; tài liệu này tìm công nghệ mới để áp vào. **Mức đọc:** chỉ đọc tóm tắt (abstract) và kết quả tìm kiếm của các bài dưới đây, chưa đọc toàn văn; đọc toàn văn trước khi trích.

## Phát hiện từ tài liệu
| Hướng | Nguồn | Ý chính | Áp vào bài toán |
|---|---|---|---|
| Proactive agent: khi nào can thiệp | PRISM (arXiv 2602.01532), ProAgentBench (2602.04482), ProactiveBench (2410.12361) | Cổng quyết định theo chi phí: ước lượng xác suất người dùng chấp nhận, chỉ can thiệp khi vượt ngưỡng suy từ chi phí bỏ sót và báo nhầm; chỉ chạy suy luận chậm gần ngưỡng. PRISM báo giảm báo nhầm 22,78%, tăng F1 20,14% trên ProactiveBench | Thay luật "ceil20 mỗi sprint" bằng cổng chi phí có hiệu chuẩn; LLM chỉ chạy gần ngưỡng |
| Bộ nhớ ý định tương lai | Pro-Memory (2611.05731) | Lưu "ý định chờ" kèm bằng chứng, kiểm lại khi có quan sát mới, cập nhật trạng thái | Cảnh báo là một ý định có điều kiện kích hoạt; chính là ledger, snooze, "nhắc lại khi có thay đổi" chưa làm |
| Bộ nhớ theo ca (CBR) cho agent | Memento (2508.16153), Hatalis và cộng sự (2504.06943) | Agent dùng kho ca cũ, LLM đóng băng; Memento báo +4,7 đến 9,6 điểm ngoài phân phối | Thẻ "việc giống nhau" trở thành bộ nhớ ca của agent: ca kẹt cũ, việc đã làm, kết cục |
| Hiệu chuẩn độ chắc của agent | UQ cho LLM agent (2609.07395) | Độ chắc tự báo của agent không luôn hơn baseline đơn giản; lỗi trung bình che quá tự tin ở các bước sau | Giữ xác suất từ mô hình số (CatBoost), LLM chỉ giải thích và chọn hành động; báo hiệu chuẩn theo mốc 25/50/75% sprint |
| Nhiều agent | Scaling agent systems (2512.08296), SEEAgent (2509.14483), CogniSim (2508.16678) | Đa agent giảm 39–70% ở tác vụ tuần tự, tăng ~81% ở tác vụ song song có điều phối trung tâm; SEEAgent: đa agent ước lượng effort có tương tác với người | Chỉ dùng điều phối trung tâm + worker song song cho từng issue; phải đo so với một agent |
| Khoảng trống | tìm kiếm | Không thấy benchmark proactive riêng cho Jira/issue tracker; TheAgentCompany có một task sprint trên Plane | Có thể đóng góp benchmark proactive cho sprint từ TAWOS (có đáp án kết cục) |
| Duyệt và hoàn tác | Magentic-UI (2507.22358) và bài blog thực hành | Cổng theo mức đảo ngược và phạm vi ảnh hưởng; hành động đảo ngược được thì cần duyệt nhẹ | Duyệt, Bỏ qua, Hoàn tác đã đúng mô hình này |

## Ghi chú về LLM rẻ (OpenRouter, số liệu từ trang collection tool-calling, chưa kiểm lại)
Giá mỗi triệu token (vào/ra): DeepSeek V4.1 Flash 0,006/0,50; GLM 5.3 Flash 0,0285/0,0923; MiniMax M3.1 Flash 0,1125/0,45; Claude Haiku 5.5 0,10/0,50; Hy3 0,132/0,528 (trang nêu riêng tool calling ổn định); Nemotron 3 Ultra miễn phí; Claude Opus 5.5 4/20. Trang không xếp hạng chất lượng tool calling. Cần một thăm dò độ tin cậy gọi tool trước khi chọn. Một brief khoảng 3k token vào, 0,5k ra: dưới 0,001 USD với mô hình rẻ.

## Hướng A (đã chọn, ghi nhận 2026-11-05): chọn hành động theo ngữ cảnh
Bot đề xuất hành động hợp tình huống, người duyệt thì Plane thực hiện và có thể hoàn tác (thay vì chỉ nâng priority):
- không có người phụ trách: gợi ý gán người;
- im lặng nhiều ngày: soạn comment hỏi tiến độ gửi người phụ trách;
- quá lớn so với các ca giống nhau (thẻ case): đề xuất tách nhỏ;
- sprint quá tải: đề xuất chuyển sang sprint sau.
Kiểm chứng: lịch sử TAWOS cho biết hành động nào xảy ra trước khi issue kẹt hồi phục (chỉ là quan hệ, không phải nhân quả); so với baseline "luôn nâng priority"; người dùng thật (E4) mới chứng minh hữu ích.
Ghép với các hướng trên: cổng chi phí (PRISM) quyết định có đề xuất hay im lặng; bộ nhớ ca (Memento, CBR) cung cấp ca kẹt cũ và việc đã làm; ledger kiểu Pro-Memory giữ ý định và kích hoạt lại; LLM rẻ soạn comment và giải thích, qua `EvidenceVerifier`; mô hình số giữ xác suất. Điều phối trung tâm, worker song song cho từng issue, so với một agent.
Việc tiếp theo: viết protocol hướng A (danh sách hành động, nhãn từ lịch sử, baseline), rồi thăm dò tool calling trên OpenRouter, rồi nối vào `post_briefs.py` chế độ `--agent`.

## Model đã chọn (2026-11-05)
- **Thật (chạy kết quả báo cáo):** `openai/gpt-6-luna` (0,10 / 0,50 USD mỗi triệu token).
- **Thử nghiệm và phát triển:** `openai/gpt-oss-120b` (0,024 / 0,089), reasoning luôn bật nên client không gửi `reasoning.enabled=false` cho model này.
- Client `app/services/openrouter_client.py`: model trả phí phải nằm trong `PAID_MODELS`, mỗi request kèm trần giá, dừng khi chi tiêu chạm `OPENROUTER_BUDGET_USD` (mặc định 2). Có test.
- Thăm dò tool calling (3 tình huống x 2 lần, một tool `set_priority`): cả hai 6/6 đúng, tổng chi khoảng 0,0002 USD. Mẫu nhỏ, chỉ cho biết gọi tool cơ bản chạy được.
- Lỗi đã gặp: `require_parameters` cộng với `seed`, `top_p` làm gpt-6-luna trả 404 (không endpoint nào đủ tham số); với model trả phí chỉ gửi `max_price`.

## Khảo sát thị trường và học thuật (báo cáo do người dùng cung cấp, 2026-11-05; chưa kiểm chứng độc lập)
Nguồn: báo cáo dán vào phiên làm việc (repo, sản phẩm thương mại, bài báo). Mình chưa mở lại các liên kết; số sao, ngày phát hành và số liệu bài báo phải kiểm lại trước khi trích.
Điểm chính báo cáo nêu:
- Mẫu đang nổi: orchestrator/manager + worker, trạng thái ngoài ngữ cảnh (ticket, SQLite, tệp), ngân sách và cổng duyệt; nền tảng ticket (Linear, Jira, Asana, Notion, ClickUp, Planner) coi agent là người được giao việc.
- Phần "thông minh" của PM (dự báo, sprint planning, sổ rủi ro) có bằng chứng mỏng nhất: không thấy benchmark có nhãn cho sprint planning hoặc backlog; không thấy bài nào kết hợp agent LLM với dữ liệu dự án thật để dự báo rủi ro sớm rồi kiểm với độ trễ thực.
- Jira Delivery agent (7/2026) gắn cờ rủi ro theo luật (quá hạn, bị chặn, thiếu story point), không có số độ chính xác, không mô tả cổng duyệt.
- Đa agent: chi phí khoảng 1,65 lần (TheBotCompany) đến 15 lần (Anthropic) token; hợp tác vụ song song, kém ở tác vụ có phụ thuộc.
- Ticket là nội dung không đáng tin: có PoC tiêm lệnh gián tiếp qua ticket Jira với agent MCP.

Hệ quả cho đề tài (suy luận của mình):
1. **Chỗ đứng:** dự báo rủi ro đo bằng kết cục sprint thật (E8 trên TAWOS, có baseline luật `business_rule` lift 1,03 và đối chứng cùng chi phí) là phần mà khảo sát cho là trống. Đây là đóng góp nên nhấn mạnh; cần kiểm lại bằng tìm kiếm có mục tiêu trước khi viết "chưa ai làm".
2. **Baseline cạnh tranh:** gắn cờ theo luật như Jira Delivery agent chính là `business_rule` của ta; báo kết quả mô hình so với luật.
3. **Sổ cảnh báo (ledger):** theo mẫu `project-risk-agent`: mỗi cảnh báo có bằng chứng, likelihood, impact, urgency, confidence và trạng thái thay đổi giữa các lần chạy (mới, dai dẳng, xấu đi, đã giải quyết).
4. **Tách tất định khỏi LLM:** giữ đúng thiết kế hiện tại (mô hình số cho xác suất, LLM soạn nội dung).
5. **An toàn:** agent đọc comment và mô tả issue phải coi đó là dữ liệu không tin cậy: LLM chỉ có tool đọc và tool đề xuất, mọi thao tác ghi đi qua thẻ Duyệt; nội dung ticket không được quyết định lời gọi tool. Đưa vào protocol hướng A thành một kiểm tra (chèn lệnh trong comment thử nghiệm không được tạo hành động).
6. **Chi phí:** báo token và USD mỗi cảnh báo; một agent điều phối cộng worker song song cho từng issue chỉ nếu thắng một agent đơn ở chi phí so sánh được.

## Kế hoạch hợp nhất (2026-11-05): đặt các hướng SOTA vào khung đề cương đã nộp
Khung đề cương (De_cuong_du_bao_som_rui_ro_sprint.md): tầng 1 mô hình + controller ngoài LLM; tầng 2 agent chỉ đọc lập brief có bằng chứng, verifier, ledger; RQ-A (phân bổ cảnh báo theo thời gian), RQ-B (agent so với template và LLM một lượt), RQ-C (verifier và ledger). Multi-agent, RL, semantic features nằm ngoài v1 (chỉ là mở rộng).

| Gói | Nội dung | Hướng SOTA dùng | Câu hỏi nghiên cứu | Đo bằng |
|---|---|---|---|---|
| P0 | Ghi E9 là thăm dò (mốc 50% vẫn là mốc khóa trước); sửa tài liệu cho khớp đề cương | | | |
| P1 | E10: controller theo chi phí và hiệu chuẩn theo mốc, thay K cố định | PRISM (cổng chi phí, suy luận chậm chỉ gần ngưỡng), UQ cho agent (hiệu chuẩn theo mốc) | RQ-A, RQ3 | recall và lift ở cùng số cảnh báo, Brier và độ dốc hiệu chuẩn mỗi mốc 0/25/50/75, so với ceil20 và K cố định |
| P2 | Nối agent A2 vào Plane (tầng 2, dry-run): tool đọc bằng chứng + tool ca giống nhau (E6), qua `EvidenceVerifier`; `gpt-6-luna` chạy thật, `gpt-oss-120b` để dev | Memento/CBR (kho ca làm bộ nhớ), tách xác suất (số) khỏi nội dung (LLM) | RQ-B | brief bám bằng chứng, chi phí USD mỗi cảnh báo |
| P3 | E3 v3: lặp ≥3 lần, A0 so với A1 so với A2, tool ca giống nhau bật/tắt, tiêm lệnh qua comment thật, negative control cho verifier | AgentDojo, ProAgentBench (đề cương), bài học bảo mật từ khảo sát | RQ-B, RQ-C | độ bám, số liệu, quyết định, an toàn, chi phí, độ lệch giữa các lần |
| P4 | Ledger theo thời gian, snooze, shadow mode | Pro-Memory (ý định chờ kèm điều kiện kích hoạt lại) | RQ-C | trạng thái mới/dai dẳng/xấu đi/đã giải quyết; cảnh báo lặp bị chặn |
| P5 | E4 người thật hoặc shadow có người xem | | tác động | cần người tham gia |
| Mở rộng sau v1 | Chọn hành động theo ngữ cảnh (hướng A), agent đa vai (điều phối + worker song song), khớp ngữ nghĩa comment | Scaling agent systems, SEEAgent | ngoài đề cương | so sánh có kiểm soát chi phí |

Đóng góp có thể nhấn mạnh (kiểm lại tài liệu trước khi viết "chưa ai làm"): dự báo rủi ro sprint đo bằng kết cục thật, baseline luật cùng chi phí, bộ đánh giá agent tái lập được trên TAWOS.
