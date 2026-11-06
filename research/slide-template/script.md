# Kịch bản thuyết trình: Báo cáo tổng kết đề tài NCKH sinh viên (04-SV-2026-RIPT)

Thời lượng dự kiến: 15 - 20 phút cho 20 slide.
Toàn bộ số liệu đồng bộ với báo cáo tổng kết `Bao_cao_tong_ket_de_tai_v2.md`.

---

## Slide 1: Trang bìa
Kính chào các thầy cô trong Hội đồng. Em là Nguyễn Trường Giang, sinh viên lớp D23CCPM02, Viện Khoa học Kỹ thuật Bưu điện. Hôm nay em xin trình bày báo cáo tổng kết đề tài nghiên cứu khoa học "Nghiên cứu mô hình đánh giá rủi ro trễ hạn công việc trong sprint và xây dựng agent hỗ trợ can thiệp sớm", mã số 04-SV-2026-RIPT, dưới sự hướng dẫn của ThS. Trần Minh Hiếu.

## Slide 2: Bối cảnh thực tế và Bài toán nghiên cứu
Trong quản lý dự án theo Agile, đầu mỗi sprint nhóm phát triển cam kết hoàn thành một danh sách issue. Tuy nhiên, thống kê trên 18.322 cặp issue-sprint thuộc 14 dự án trong bộ dữ liệu Jira TAWOS cho thấy có tới 47,21% trường hợp kết thúc sprint khi issue vẫn chưa hoàn thành.
Dù các công cụ như Jira hay Plane lưu lại đầy đủ lịch sử thao tác, trưởng nhóm khó có thời gian đọc thủ công nhật ký của hàng chục issue mỗi ngày. Khi áp dụng học máy, chỉ đưa ra một con số xác suất trễ hạn là chưa đủ vì người quản lý cần biết vì sao issue gặp rủi ro và nên xử lý thế nào. Ở chiều ngược lại, thực nghiệm E6 của chúng tôi cho thấy việc ước lượng trực tiếp story point từ 20 issue tương tự không vượt qua mức trung vị của dự án (MAE 1,61 so với 1,71, khoảng tin cậy 95% chứa 0).
Vì vậy, đề tài giải quyết bài toán hỗ trợ quyết định tại các mốc 0%, 25%, 50% và 75% thời lượng sprint trên nền tảng Plane ở hai cấp độ: ở cấp từng issue là phát hiện theo ngân sách 20%, chẩn đoán nguyên nhân có bằng chứng sự kiện và đề xuất hành động chờ người dùng Duyệt, Bỏ qua hoặc Hoàn tác; ở cấp sprint là ước lượng số không xong dự kiến để lập tập chuyển sang sprint kế tiếp, đi kèm agent hỏi đáp chỉ đọc.

## Slide 3: Bốn câu hỏi nghiên cứu (RQ1 - RQ4) và Đóng góp thực nghiệm
Toàn bộ thực nghiệm được tổ chức xoay quanh bốn câu hỏi nghiên cứu tương ứng với bốn bước xử lý của hệ thống, kèm quy tắc kết luận khóa trước khi chạy:
- RQ1 kiểm tra điểm phát hiện sớm dưới ngân sách 20% số issue đang mở.
- RQ2 đo độ bám bằng chứng và độ đồng thuận giữa chẩn đoán của hệ thống với nhãn của người chấm độc lập trên 81 cảnh báo và 60 issue held-out.
- RQ3 đánh giá công thức lập kế hoạch cấp sprint bằng backtest trên 60 sprint lịch sử.
- RQ4 kiểm tra tính đúng phạm vi, chống tiêm lệnh và cô lập quyền xem của agent hỏi đáp trên bộ 25 câu hỏi kịch bản.

## Slide 4: Dữ liệu TAWOS v1.1 và Quy tắc cắt tại mốc t (Chống rò rỉ tương lai)
Chúng tôi nạp bộ dữ liệu TAWOS phiên bản 1.1 vào PostgreSQL gồm 39 dự án, 458 nghìn issue và hơn 9,25 triệu dòng nhật ký thay đổi. Sau các bước lọc cố định, tập đánh giá khối phát hiện gồm 14 dự án, 1.962 sprint và 18.322 cặp issue-sprint. Khối chẩn đoán, kế hoạch sprint và giao diện Plane được triển khai và đo đạc trên dự án IS (Indy SDK của Hyperledger, nhập vào Plane dưới mã ISP).
Một điểm kỹ thuật quan trọng là trên bảng issue của Jira/TAWOS, các cột trạng thái, mức ưu tiên, người phụ trách và sprint đều lưu giá trị cuối cùng sau khi issue đã đóng. Để tránh rò rỉ thông tin tương lai, hệ thống tái dựng trạng thái tại mốc t hoàn toàn từ bảng nhật ký thay đổi change_log, chỉ lấy các sự kiện xảy ra trước hoặc đúng tại mốc t.

## Slide 5: Kiến trúc tổng thể 6 khối chức năng và 7 bất biến an toàn
Hệ thống gồm 6 khối chức năng với luồng dữ liệu một chiều. Khối 2 (chẩn đoán) và Khối 3 (kế hoạch sprint) chạy nền theo lô; Khối 4 là dịch vụ risk viết bằng FastAPI tách riêng cơ sở dữ liệu với Plane. Như mũi tên đỏ trên sơ đồ thể hiện, LLM hoàn toàn không có quyền ghi: dịch vụ risk chỉ gọi API sửa dữ liệu trên Plane khi người dùng bấm nút Duyệt hoặc Hoàn tác dưới phiên đăng nhập của chính họ. Toàn bộ hệ thống tuân thủ 7 bất biến an toàn được kiểm tra bằng code và có unit test tự động.

## Slide 6: Phương pháp Khối 1 - Phát hiện sớm rủi ro theo ngân sách (RQ1)
Ở Khối 1, mỗi cặp issue-sprint tại mốc t được biểu diễn bằng 5 nhóm đặc trưng. Mô hình tĩnh chỉ dùng thông tin ở đầu sprint (t = 0%), còn mô hình động kết hợp thêm trạng thái thực thi (như số ngày liên tiếp ngừng hoạt động), cường độ hoạt động trước mốc t và bối cảnh sprint. Cả hai dùng CatBoost với bộ siêu tham số khóa trước và hiệu chuẩn xác suất bằng hàm logistic trên tập validation.
Thay vì dùng ngưỡng xác suất cố định, mỗi sprint có n issue đủ điều kiện chỉ nhận tối đa K = trần của 0,2n cảnh báo. Khi đánh giá qua các mốc t, chúng tôi đối chiếu Precision với tỉ lệ nền pi thông qua chỉ số Lift, vì càng về cuối sprint các issue dễ đã hoàn thành trước làm tỉ lệ nền pi tự tăng cao.

## Slide 7: Phương pháp Khối 2 - Bộ thu thập SQL, Chẩn đoán LLM và Verifier (RQ2)
Với mỗi cảnh báo, bộ thu thập chạy 5 truy vấn SQL cố định để lấy các sự kiện không muộn hơn mốc t từ 5 nguồn: bình luận thảo luận, hoạt động của người phụ trách trên các issue khác trong 7 ngày gần nhất, chuỗi chặn đến độ sâu 2, tình trạng sprint và lịch sử thay đổi của issue.
Tiếp theo, hệ thống gọi LLM một lần trên dữ liệu đã bọc thẻ untrusted để sinh tối đa 3 giả thuyết thuộc tập đóng 6 nhãn nguyên nhân. Ngay sau LLM, bước hậu kiểm Verifier bằng code loại bỏ mọi giả thuyết trích dẫn mã sự kiện không tồn tại hoặc sai loại sự kiện quy định cho từng nhãn, đồng thời đẩy nhãn carry_over xuống cuối thẻ nếu đã có một nguyên nhân cụ thể hơn đi kèm.

## Slide 8: Phương pháp Khối 3 & 4 - Kế hoạch Sprint, Duyệt/Hoàn tác và Agent hỏi đáp
Ở cấp sprint (module M14), thuật toán tính tỉ lệ không hoàn thành lịch sử r từ các sprint đã kết thúc trước đó của cùng dự án tại cùng mốc t, nhân với số issue đang mở O(t) để ước lượng số không xong dự kiến b. Sau khi lấy b issue có điểm rủi ro cao nhất, thuật toán đóng bắc cầu theo quan hệ chờ-nhau để đưa thêm các issue phụ thuộc vào tập chuyển.
Mọi thao tác Duyệt đơn lẻ hay theo lô (module M15) chỉ đi qua 3 hành động đóng và lưu giá trị cũ trước khi gọi API Plane để hỗ trợ Hoàn tác. Sổ cảnh báo (module M17) tự mở lại cảnh báo đã bỏ qua nếu điểm rủi ro ở lần chạy sau tăng thêm từ 0,15 trở lên. Agent hỏi đáp (module M16) sử dụng 5 công cụ chỉ đọc có lọc quyền xem dự án ngay trong SQL và quét đầu ra để chặn mọi câu trả lời bịa mã issue.

## Slide 9: Minh họa thực tế - Luồng xử lý 5 bước trên cảnh báo ISP-401 (IS-1119)
Slide này minh họa luồng xử lý thực tế trên issue IS-1119 (mã trên Plane là ISP-401). Ở mốc 25% sprint, issue đang ở trạng thái Code Review và ngừng hoạt động 3,3 ngày; CatBoost chấm điểm 0,759 (xếp thứ 2/7) nên đưa vào diện cảnh báo. Bộ thu thập SQL lấy ra 12 sự kiện trước mốc t, bao gồm bình luận c-550736 chờ 3 thành viên review và lịch sử h-carry-203241 ghi nhận 7 lần dồn sprint. LLM nêu hai giả thuyết waiting_person và carry_over kèm câu nhắc hỏi tiến độ review; Verifier xác nhận cả hai mã sự kiện hợp lệ và đăng thẻ lên Plane. Kết quả này trùng khớp hoàn toàn với nhãn của người chấm độc lập ở module M13.

## Slide 10: Giao diện trên Plane (1/2) - Thẻ cảnh báo Issue và Bảng điều khiển
Trên giao diện Plane, hình bên trái là thẻ cảnh báo hiển thị ngay trong trang chi tiết của issue ISP-401, gồm dòng trạng thái từ sổ cảnh báo M17, danh sách giả thuyết gắn mã sự kiện, câu nhắc dự kiến và hai nút Approve / Dismiss. Hình bên phải là bảng điều khiển Delivery risk trong mục Analytics, tổng hợp 81 cảnh báo của dự án, chi phí vận hành 0,0103 USD và tỉ lệ bám bằng chứng đạt 80/81 thẻ.

## Slide 11: Giao diện trên Plane (2/2) - Kế hoạch Sprint, Duyệt theo lô và Hỏi đáp
Ở nửa trái là thẻ kế hoạch của sprint "LibINDY 18.04 Revocation" tại mốc 50%: từ 13 issue đang mở và tỉ lệ lịch sử 45%, thuật toán ước lượng 6 issue không xong và lập tập chuyển. Khi bỏ chọn dòng IS-546 và bấm duyệt theo lô 5 dòng còn lại, cả 5 issue chuyển sang sprint sau và có thể bấm Undo để hoàn tác cả lô. Ở nửa phải là khung hỏi đáp Ask: trả lời câu hỏi tự nhiên kèm mã issue và hiển thị rõ các công cụ đã gọi ở dòng Looked up.

## Slide 12: Kết quả RQ1 (1/2) - So sánh mô hình động và tĩnh qua các mốc thời gian
Bước sang kết quả thực nghiệm, ở RQ1, bảng và biểu đồ so sánh Recall dưới ngân sách 20% cho thấy tại mốc 0%, mô hình động và tĩnh ngang nhau, xác nhận không có rò rỉ dữ liệu tương lai. Từ mốc 25% trở đi, tiến độ thực thi giúp mô hình động tăng Recall có ý nghĩa thống kê ở cả kịch bản chia theo thời gian (+7,1 điểm % ở mốc 50%) và chia theo dự án (+7,5 điểm % ở mốc 50%). Do trung bình có 57% issue không xong nhưng ngân sách chỉ báo 20%, mức Recall tối đa lý thuyết là 0,598; mức 0,533 của mô hình động ở mốc 50% đã đạt 89% mức tối đa lý thuyết đó.

## Slide 13: Kết quả RQ1 (2/2) - Chất lượng cảnh báo trên tập issue còn mở (E8, E9)
Khi đo trực tiếp trên tập các issue còn đang mở tại mốc t qua 14 dự án chưa từng xuất hiện khi huấn luyện (thực nghiệm E8, E9), ở mốc 50% cảnh báo của mô hình đạt Precision 76,3% so với tỉ lệ nền 67,0%, tương ứng Lift = 1,14. Ở cả bốn mốc thời gian, mô hình động đều vượt quy tắc sắp xếp đơn giản có ý nghĩa thống kê. Thực nghiệm phụ E7 cũng chỉ ra rằng việc đưa cờ từ khóa bình luận vào CatBoost chỉ tăng AUC thêm 0,016, giải thích vì sao văn bản bình luận được giữ cho bước chẩn đoán bằng LLM.

## Slide 14: Kết quả RQ2 (1/2) - Độ bám bằng chứng và Độ đồng thuận chẩn đoán (M13)
Ở RQ2, cả 81 cảnh báo đều trả về JSON hợp lệ và Verifier loại bỏ 3 giả thuyết thiếu căn cứ, bảo đảm 0 giả thuyết bịa sự kiện lọt lên thẻ với chi phí chỉ 0,0001 USD mỗi cảnh báo. Khi đối chiếu với người chấm độc lập M13, tỉ lệ khớp nguyên nhân đứng đầu đạt 61,7% (kappa = 0,496) ở lượt 1 và tăng lên 68,3% (kappa = 0,571) trên tập 60 issue held-out sau khi sửa quy tắc thứ tự. Đặc biệt, khi cả hai bên cùng nêu nguyên nhân, nhãn của người chấm đã nằm sẵn trong danh sách giả thuyết của thẻ ở 96,9% và 97,7% số trường hợp.

## Slide 15: Kết quả RQ2 (2/2) - Ma trận nhầm lẫn và Phân tích theo từng nguyên nhân
Ma trận nhầm lẫn lý giải vì sao có sự chênh lệch trên: ở lượt 1, LLM xếp nhãn carry_over lên đầu ở 41/81 thẻ, lấn át các nguyên nhân cụ thể hơn như pulled_away hay waiting_person nằm ở vị trí thứ hai. Vì nhật ký thực sự có sự kiện dồn sprint nên Verifier (vốn chỉ kiểm tra cấu trúc) không tự nhận ra đây là dấu hiệu bề mặt; việc thêm quy tắc đẩy carry_over xuống cuối thẻ giải quyết trực tiếp điểm này. Ngược lại, hạn chế lớn nhất của hệ thống nằm ở nhãn unclear_scope (khớp 0/13 trường hợp) khi phạm vi chưa rõ nằm ẩn trong câu chữ thảo luận.

## Slide 16: Kết quả RQ3 - Đánh giá kế hoạch cấp Sprint bằng Backtest trên 60 Sprint (M14)
Ở RQ3, kết quả backtest trên 60 sprint lịch sử của dự án IS tại mốc 50% cho thấy sự khác biệt rõ rệt giữa hai bước. Ở bước ước lượng quy mô tồn đọng của cả sprint, công thức thống kê lịch sử đạt độ chính xác cao với sai số tuyệt đối trung bình MAE = 1,76 issue/sprint và độ chệch Bias = -0,05, tốt hơn nhiều so với việc cộng trực tiếp xác suất của mô hình. Tuy nhiên, ở bước chọn đích danh từng issue vào tập chuyển khi phải lấy sâu tới gần nửa sprint, Precision chỉ đạt 52,8% so với 48,8% chọn ngẫu nhiên. Vì vậy, thẻ kế hoạch hữu ích trước hết ở con số cảnh báo sức chứa của sprint, còn danh sách bên dưới là gợi ý để trưởng nhóm chọn lại và duyệt theo lô.

## Slide 17: Kết quả RQ4 - Kiểm thử Agent hỏi đáp (M16) và Hiệu năng toàn hệ thống
Ở RQ4, trên 25 câu hỏi kịch bản, agent hỏi đáp trả lời đúng cả 17 câu trong phạm vi, từ chối 3 câu ngoài phạm vi, từ chối 2 yêu cầu ghi dữ liệu và chặn hoàn toàn 3 câu tấn công tiêm lệnh, không bịa mã issue nào ngoài kết quả công cụ với thời gian phản hồi trung vị 3,2 giây. Toàn bộ hệ thống có 92 unit test khối nghiên cứu và 89 unit test khối backend đều vượt qua 100%.

## Slide 18: Thảo luận tổng hợp và Các mối đe dọa tính hợp lệ (Threats to Validity)
Nhìn chung, các bước dựa trên thống kê cấp tập hợp và kiểm tra cấu trúc bằng code đạt độ tin cậy cao hơn những bước đòi hỏi phân biệt từng issue ở giữa bảng xếp hạng hoặc suy luận ngữ nghĩa ẩn. Chúng tôi cũng phân tích rõ bốn nhóm mối đe dọa tính hợp lệ: người chấm M13 là một LLM độc lập nên có thể chia sẻ thiên lệch đọc văn bản; phần chẩn đoán và kế hoạch sprint mới đo trên 1 dự án mã nguồn mở (IS); bảng liên kết chặn trong TAWOS thiếu dấu thời gian tạo liên kết; và nghiên cứu chưa có thử nghiệm đối chứng trực tiếp với người quản lý dự án thật.

## Slide 19: Kết luận và Hướng phát triển tiếp theo
Từ bốn kết quả thực nghiệm chính và các giới hạn đã phân tích, ba hướng phát triển tiếp theo của đề tài gồm: thứ nhất, mời người quản lý dự án thực tế chấm độc lập một mẫu cảnh báo và mở rộng thực nghiệm sang các dự án khác trong TAWOS; thứ hai, bổ sung lịch sử chỉnh sửa mô tả issue vào bộ thu thập để nhận diện tốt hơn nguyên nhân unclear_scope và hiệu chuẩn lại xác suất theo từng mốc t; thứ ba, triển khai chạy thử nghiệm ngầm (shadow mode) trên một đội phát triển thực tế.

## Slide 20: Tài liệu tham khảo
Trên đây là phần trình bày báo cáo tổng kết đề tài của em. Em xin trân trọng cảm ơn các thầy cô trong Hội đồng đã lắng nghe và rất mong nhận được ý kiến đóng góp của thầy cô ạ.
