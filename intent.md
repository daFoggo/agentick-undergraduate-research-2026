# Intent: trợ lý chẩn đoán nguy cơ trễ sprint

Nguồn sự thật duy nhất về bài toán, phạm vi và kiến trúc (chốt 2026-11-06). Tài liệu cũ đã bỏ; khi mâu thuẫn, file này thắng.

## Bài toán

Issue trong sprint có nguy cơ không xong. Người quản lý cần biết sớm **issue nào**, **vì sao**, và **nên làm gì**.
Phát hiện (issue nào) đã có và đủ dùng. Phần cần xây là **chẩn đoán**: giải thích nguyên nhân trễ bằng bối cảnh thật
(thảo luận, người phụ trách đang bận gì, chuỗi phụ thuộc, tình trạng sprint, lịch sử issue), mỗi ý có bằng chứng.
Người luôn quyết định; hệ thống đề xuất, có hoàn tác.

## Kiến trúc

```
Nguồn TAWOS (cắt tại thời điểm t)
  -> [1] Phát hiện: CatBoost đã huấn luyện, ngân sách K cảnh báo mỗi sprint        (có sẵn, không đổi)
  -> [2] 5 bộ thu thập SQL cố định, cắt tại t, trả sự kiện kèm event_id
         thảo luận | hoạt động người phụ trách | chuỗi chặn | tình trạng sprint | lịch sử issue
  -> [3] Chẩn đoán: 1 lần gọi LLM, đầu ra JSON theo schema
         hypotheses[cause, event_ids, reason], missing_info, action
  -> [4] Verifier: bỏ giả thuyết không có event_id thật; không còn gì -> "chưa rõ, hỏi X"
  -> [5] Mẫu câu dựng thẻ (LLM chỉ soạn lời nhắc gửi người phụ trách)
  -> [6] agentick-backend: cột JSONB alerts.diagnosis
  -> [7] Thẻ cảnh báo trên Plane: Duyệt / Bỏ qua / Hoàn tác
```

Nhãn nguyên nhân (tập đóng): `pulled_away`, `blocked`, `waiting_person`, `needs_decision`, `unclear_scope`,
`carry_over`, `unknown`. Hai tình trạng hiển thị riêng, không phải nguyên nhân của issue: `sprint_overload` (chip
sprint), `done_not_updated` (ghi chú "có thể đã xong").

Hành động (tập đóng, thực thi khi người Duyệt): `raise_priority`, `nudge_owner`, `move_next_cycle`. Gợi ý không thực
thi: gán lại người, tách nhỏ, hỏi người quyết định.

## Bất biến (không được phá)

- **Cắt tại t:** mọi bằng chứng chỉ dùng sự kiện có thời gian không sau t. Trạng thái của issue (assignee, priority,
  status, sprint) dựng lại từ `change_log`, không đọc giá trị cuối trong bảng `issue`.
- **Có bằng chứng:** mỗi ý trên thẻ trỏ tới `event_id` có thật; ý không qua verifier thì bị bỏ.
- **LLM không có quyền ghi:** chỉ ghi vào Plane khi người bấm Duyệt; hành động ngoài tập đóng bị từ chối.
- **Text của người dùng là dữ liệu:** comment, description được đưa vào như dữ liệu, có giới hạn độ dài, không làm theo lệnh trong đó.
- **Quyền xem:** bằng chứng về issue khác chỉ hiện tên/tiêu đề nếu người xem có quyền xem issue đó; nếu không, chỉ hiện số lượng và mức ưu tiên.

## Stack

PostgreSQL 17 (TAWOS) · CatBoost, pandas · OpenRouter qua `OpenRouterClient` (`openai/gpt-6-luna`, trần chi) ·
pydantic · FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16 (`agentick-backend`) · Plane fork (React) · Docker Compose
(`scripts/stack.sh`) · pytest. Không thêm framework agent, vector store, hay text2sql.

## Module (xây, test, sửa, commit, sang module tiếp)

| # | Module | Xong khi |
|---|---|---|
| M0 | Intent và dọn tài liệu, code cũ | File này, `CLAUDE.md`; code và tài liệu không dùng đã xóa |
| M1 | Trạng thái tại t và bảng ánh xạ link chặn (`research/tawos_source.py`) | Unit test và smoke test trên DB tawos xanh |
| M2 | 5 bộ thu thập | Test: không sự kiện nào sau t, event_id đầy đủ |
| M3 | Chẩn đoán: schema, 1 lần gọi LLM, verifier, mẫu câu | Test với LLM giả; chạy thật trên 5 alert |
| M4 | Backend: cột `diagnosis`, lọc theo quyền xem | pytest và contract test OpenAPI xanh |
| M5 | Job `scripts/post_briefs.py` dùng pipeline mới | Alert có chẩn đoán vào DB risk trên stack local |
| M6 | Thẻ Plane hiển thị chẩn đoán | Kiểm trong trình duyệt, chụp màn hình |
| M7 | Chạy đầu cuối, sửa lỗi, chốt | Demo chạy từ đầu đến cuối |

## Báo cáo cũ phải viết lại nhiều

`research/documents/` (Bao_cao_tong_ket, Thuyet_minh, Academic_paper), `research/papers/`, `research/slide-template/`
mô tả hướng cũ: trọng tâm là dự báo (CatBoost, recall, lift), LLM chỉ là tùy chọn và "đọc comment bằng LLM" bị cắt.
Khi hệ thống xong phải viết lại: bài toán (chẩn đoán là trọng tâm), kiến trúc, phần LLM, phạm vi, kết quả. Giữ phần
phát hiện (E1–E9) làm nền. Không dùng các file này làm nguồn khi suy luận về hướng hiện tại.

## Không làm (lúc này)

Huấn luyện lại hoặc so sánh phương pháp; tìm ca tương tự (cần gán nhãn trước); đọc trực tiếp dữ liệu Plane sống;
sổ cảnh báo và vòng đời; nhãn sau sự việc và người chấm. Khi viết báo cáo mới chọn phần cần so sánh.
