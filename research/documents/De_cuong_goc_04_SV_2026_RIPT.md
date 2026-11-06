# ĐỀ CƯƠNG NGHIÊN CỨU KHOA HỌC CỦA SINH VIÊN (BẢN GỐC)

- **Đơn vị:** Học viện Công nghệ Bưu chính Viễn thông - Viện Khoa học Kỹ thuật Bưu điện
- **Ngày lập:** Hà Nội, ngày 07 tháng 05 năm 2026

## 1. Tên đề tài
- **Tên đề tài trong thuyết minh gốc:** Agentick - Hệ thống quản lý công việc tích hợp AI Agent (Nghiên cứu mô hình đánh giá rủi ro trễ hạn công việc trong sprint và xây dựng agent hỗ trợ can thiệp sớm)
- **Mã số:** `04-SV-2026-RIPT`

## 2. Thuộc lĩnh vực
Công nghệ thông tin

## 3. Mục tiêu, nội dung và kết quả đề tài

### a/ Mục tiêu
Xây dựng hệ thống có khả năng theo dõi quá trình thực thi công việc theo thời gian thực, đánh giá rủi ro trễ deadline sớm và hỗ trợ can thiệp dựa trên dữ liệu, thay vì chỉ phản ứng khi vấn đề đã xảy ra.

### b/ Nội dung
- **Giảm rủi ro trễ deadline:** Phát hiện sớm các nguy cơ quá tải, trì hoãn hoặc lập kế hoạch không khả thi, giúp doanh nghiệp can thiệp kịp thời trước khi deadline bị vi phạm.
- **Nâng cao khả năng thực thi kế hoạch:** Hỗ trợ lập kế hoạch và phân bổ thời gian dựa trên dữ liệu hành vi làm việc thực tế, thay vì chỉ dựa vào ước lượng chủ quan.
- **Tăng hiệu quả quản lý dự án:** Cung cấp cho quản lý và team lead cái nhìn rõ ràng về tính khả thi của deadline, điểm nghẽn tiến độ và mức độ quá tải của đội nhóm để ra quyết định điều phối chính xác hơn.
- **Giảm chi phí quản lý và xử lý sự cố:** Chuyển từ xử lý bị động khi trễ hạn sang can thiệp sớm, giúp hạn chế tăng ca, điều chỉnh gấp và các chi phí phát sinh do quản lý tiến độ kém hiệu quả.
- **Minh bạch hóa quá trình làm việc:** Dữ liệu tiến độ, hành vi làm việc và các can thiệp của AI Agent được ghi nhận và đánh giá rõ ràng, giảm phụ thuộc vào báo cáo thủ công và đánh giá cảm tính.
- **Nền tảng cho cải tiến dài hạn:** Thông qua cơ chế observability & evaluation với Opik, hệ thống tạo tiền đề cho việc cải thiện liên tục hiệu quả của AI Agent và tối ưu quy trình làm việc theo thời gian.

### c/ Kết quả
- Báo cáo kết quả đề tài
- Hệ thống phần mềm dạng ứng dụng web hoàn chỉnh được triển khai và vận hành thực tế.

## 4. Chủ trì đề tài
Nguyễn Trường Giang, MSV B23DCCC055, Lớp D23CCPM02, CCCD 001205056637, SĐT 0988169513

## 5. Những người tham gia thực hiện
Nguyễn Trường Giang, MSV B23DCCC055, Lớp D23CCPM02, CCCD 001205056637, SĐT 0988169513

## 6. Giảng viên hướng dẫn
ThS. Trần Minh Hiếu

## 7. Sơ lược tình hình nghiên cứu, điều tra trong nước, ngoài nước

### Trong nước
Tình hình tại Việt Nam: Trễ deadline là vấn đề phổ biến và dai dẳng trong môi trường làm việc theo dự án tại Việt Nam. Thực trạng này xuất phát từ hai nguyên nhân cốt lõi được ghi nhận rộng rãi trong thực tiễn doanh nghiệp: deadline được đặt ra dựa trên cảm tính thay vì dữ liệu thực thi, và các dấu hiệu rủi ro tích lũy trong quá trình thực hiện không được theo dõi liên tục. Ngay cả các quản lý dự án có kinh nghiệm cũng thừa nhận tình trạng đánh giá thấp thời gian cần thiết, dẫn đến việc một dự án ước tính 4 tháng thực tế mất 6 tháng [1], kéo theo ngân sách vượt mức và ảnh hưởng hàng loạt dự án tiếp theo. Công tác quản trị dự án tại doanh nghiệp Việt Nam vẫn còn nhiều rào cản, cần có công cụ hỗ trợ để chuẩn hóa và tối ưu hóa quy trình.

Về mặt công cụ, các doanh nghiệp công nghệ Việt Nam hiện chủ yếu sử dụng các nền tảng quốc tế như Jira, Trello, Notion để quản lý công việc. Tuy nhiên, các công cụ này tiếp cận deadline như một mốc ghi nhận trạng thái, nghĩa là chỉ phản ánh công việc đang ở trạng thái nào, không dự báo được khả năng hoàn thành đúng hạn hay không. Trong khi đó, phần lớn doanh nghiệp vừa và nhỏ vẫn vận hành song song bằng Excel, email và các kênh chat như Slack hay Zalo, dẫn đến dữ liệu tiến độ phân tán và thiếu nhất quán. Chưa có sản phẩm thương mại lẫn công trình nghiên cứu học thuật nào trong nước tiếp cận bài toán quản lý dự án theo hướng AI Agent chủ động, tức là liên tục phân tích dữ liệu thực thi, phát hiện nguy cơ trễ hạn từ sớm và tự động can thiệp mà không cần chờ báo cáo thủ công từ người dùng.

### Ngoài nước
Trên thế giới, bài toán trễ deadline trong dự án phần mềm đã được ghi nhận ở mức độ nghiêm trọng. Theo PMI's Pulse of the Profession 2023, 43% dự án bỏ lỡ deadline hơn 25% so với kế hoạch ban đầu [2], trong khi nguyên nhân cốt lõi được xác định là ước lượng effort thiếu cơ sở dữ liệu và thiếu cơ chế phát hiện rủi ro sớm trong quá trình thực thi.

Hướng ứng dụng LLM và agentic AI vào quản lý dự án đang nhận được sự quan tâm nghiên cứu ngày càng lớn. Các nghiên cứu gần đây đã chứng minh LLM có thể vượt trội so với phương pháp truyền thống trong bài toán ước lượng thời gian và chi phí dự án nhờ khả năng hiểu ngữ nghĩa của mô tả công việc [3]. Theo hướng multi-agent, một số framework đề xuất các agent phối hợp với nhau và với developer để đạt đồng thuận trong ước lượng effort [4], cho kết quả vượt trội trên dataset thực tế. Tuy nhiên, phần lớn các nghiên cứu này tập trung vào giai đoạn lập kế hoạch đầu kỳ, chưa giải quyết bài toán giám sát rủi ro liên tục trong suốt quá trình thực thi dự án.

### Kết luận
Đề tài "Agentick - Hệ thống quản lý công việc tích hợp AI Agent" được thực hiện trong bối cảnh bài toán trễ deadline vẫn là thách thức dai dẳng tại hầu hết các tổ chức làm việc theo dự án, đặc biệt trong lĩnh vực phần mềm. Trong khi các nghiên cứu quốc tế đang chứng minh tiềm năng của LLM và agentic AI trong quản lý dự án, và tại Việt Nam, ứng dụng AI trong lĩnh vực này còn rất hạn chế, đề tài hướng đến giải quyết một khoảng trống cụ thể: xây dựng một hệ thống agent chủ động theo dõi quá trình thực thi, phát hiện sớm nguy cơ trễ hạn và cải thiện khả năng dự báo theo thời gian, phù hợp với đặc thù làm việc nhóm tại các doanh nghiệp công nghệ Việt Nam.

## 8. Sản phẩm giao nộp của đề tài
- **Dạng sản phẩm III:** Chương trình máy tính (đánh dấu X)

### a. Kết quả, sản phẩm

| STT | Tên sản phẩm | Đ.vị tính | Số lượng | Chú thích |
|---|---|---|---|---|
| 1 | Hệ thống phần mềm dạng ứng dụng web hoàn chỉnh được triển khai và vận hành thực tế. | Hệ thống | 01 | |
| 2 | Báo cáo kết quả của đề tài | Quyển | 02 | |

### c. Yêu cầu khoa học, kinh tế xã hội đối với sản phẩm (dạng II, III)

| STT | Tên sản phẩm | Yêu cầu cụ thể cần đạt | Chú thích |
|---|---|---|---|
| 1 | Báo cáo kết quả đề tài | Khoa học và đủ nội dung | |
| 2 | USB chứa nội dung báo cáo, bài báo và sản phẩm phần mềm (nếu có) | - file nội dung báo cáo có trang bìa như bản cứng; - file bài báo là bản cuối cùng đã sửa theo ý kiến của hội đồng khoa học Viện; - Sản phẩm phần mềm được thuyết minh mô tả không quá 02 trang A4 | |

## 11. Tiến độ thực hiện các nội dung

| STT | Nội dung từng bước | Thời gian thực hiện | Kết quả cần đạt |
|---|---|---|---|
| 1 | Tổng quan tài liệu: nghiên cứu các công trình liên quan về AI trong quản lý dự án, agentic AI, LLM-based effort estimation, case-based reasoning | 05/2026 | Bản tổng quan tài liệu, xác định khoảng trống nghiên cứu và hướng tiếp cận của đề tài |
| 2 | Phân tích yêu cầu, đề xuất mô hình hệ thống, thiết kế kiến trúc agent và cơ sở dữ liệu | 06/2026 | Tài liệu đặc tả yêu cầu, sơ đồ kiến trúc hệ thống, schema database, thiết kế luồng hoạt động của agent |
| 3 | Xây dựng module quản lý công việc, lịch làm việc và time tracking | 07-08/2026 | API hoàn chỉnh cho Task, Phase, Project, WorkSchedule, TimeLog; giao diện người dùng cơ bản |
| 4 | Xây dựng AI Agent: phân tích rủi ro, dự báo deadline, cơ chế cảnh báo chủ động qua email và Telegram | 09/2026 | Agent hoạt động end-to-end: tính risk score, gửi cảnh báo, tạo báo cáo tự động theo lịch |
| 5 | Viết báo cáo kết quả nghiên cứu | 10/2026 | Đầy đủ nội dung |
| 6 | Nghiệm thu | 11/2026 | Được hội đồng thông qua |

## Tài liệu tham khảo (trong đề cương gốc)
1. Hoàng Công Chính, "Lí do nào khiến nhóm cứ mãi trễ deadline công việc?", CareerLink, 2023.
2. Project Management Institute, *Pulse of the Profession 2023*, PMI, 2023.
3. S. Ahmed, M. Danilova, và M. Torchiano, "Leveraging Large Language Models for Predicting Cost and Duration in Software Engineering Projects", arXiv preprint arXiv:2409.09617, 2024.
4. T. Nguyen et al., "An LLM-based Multi-Agent Framework for Agile Effort Estimation", arXiv preprint arXiv:2509.14483, 2025.
