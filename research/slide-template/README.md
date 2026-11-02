# Báo cáo tiến độ: Dự báo sớm issue không hoàn thành trong sprint

Slide Beamer dùng `theme.tex` và các asset của template gốc.
Build bằng XeLaTeX (theme dùng `fontspec` với Times New Roman):

```bash
latexmk -xelatex main.tex
```

- Nội dung nằm trong `sections/`; lời nói cho từng slide nằm trong `script.md`.
- Hình kết quả được chép từ `artifacts/results/` sang `assets/results/`.
- Số liệu lấy từ `artifacts/results/` và `artifacts/agent_extension/`, là benchmark trên TAWOS v1.1. Chưa có dữ liệu từ Agentick.
- Thuyết minh đi kèm: `documents/Thuyet_minh_bao_cao_tien_do.md` (bản PDF cùng tên).
- `assets/demo/` và `annobot-experiment-result.pdf` là phần còn lại của template AnnoBot, slide hiện tại không dùng.
