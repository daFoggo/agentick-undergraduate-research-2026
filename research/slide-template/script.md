# Kịch bản thuyết trình: Báo cáo tiến độ đề tài

Thời lượng dự kiến: khoảng 15–18 phút cho 20 slide.
Mọi số liệu định lượng lấy từ `artifacts/results/` (benchmark trên dataset TAWOS); ví dụ agent lấy từ trace trong `artifacts/agent_extension/`. Chưa có số liệu nào từ Agentick.

---

## Slide 1: Tiêu đề
Kính chào thầy cô. Em là Nguyễn Trường Giang, chủ trì đề tài, lớp D23CCPM02. Em xin báo cáo tiến độ đề tài "Nghiên cứu mô hình đánh giá rủi ro trễ hạn công việc trong sprint và xây dựng agent hỗ trợ can thiệp sớm", mã đề tài 04-SV-2026-RIPT, dưới sự hướng dẫn của ThS. Trần Minh Hiếu.
Bài trình bày đi theo đúng hai phần của đề tài: trước hết là mô hình đánh giá rủi ro và kết quả của nó, sau đó là agent; cuối cùng là giới hạn và kế hoạch tiếp theo.

## Slide 2: Bối cảnh và bài toán
Đầu sprint, nhóm cam kết hoàn thành một danh sách issue, nhưng trong dữ liệu của đề tài có khoảng 47% cặp issue–sprint không xong đúng hạn.
Jira lưu lại toàn bộ lịch sử thay đổi, nên về nguyên tắc có thể dùng dữ liệu này để nhận ra sớm các issue có nguy cơ. Khi làm việc này có hai ràng buộc. Thứ nhất, người quản lý không xem được mọi issue, nên số cảnh báo phải có giới hạn. Thứ hai, nếu vô tình dùng thông tin chỉ xuất hiện sau thời điểm dự báo thì kết quả sẽ tốt giả tạo; vì vậy mọi đặc trưng đều được tái dựng đúng tại thời điểm dự báo.
Cụ thể, tại các mốc 0, 25, 50 và 75% thời lượng sprint, mô hình ước lượng xác suất issue chưa xong vào ngày kết thúc sprint.
Có ba câu hỏi chính. RQ1 hỏi lịch sử thực thi có giúp ích không. RQ2 hỏi kết quả có giữ được trên sprint tương lai và trên dự án mới không. RQ3 hỏi khi số cảnh báo bị giới hạn, mô hình nào phát hiện được nhiều issue rủi ro hơn.
Giả thuyết chính được đăng ký trước khi chạy thực nghiệm: tại mốc 50%, mô hình động có recall cao hơn mô hình tĩnh. Hai hướng mở rộng là phân bổ cảnh báo theo thời gian và agent; cả hai được bổ sung sau, không thuộc giả thuyết đăng ký trước.
Tóm lại, đề tài có hai phần: mô hình chọn ra issue nào cần chú ý, còn agent giải thích vì sao, kèm bằng chứng, để người quản lý tự quyết định có can thiệp hay không.

## Slide 3: Dữ liệu TAWOS và thiết kế đánh giá
Để trả lời các câu hỏi này, đề tài dùng TAWOS phiên bản 1.1: 39 dự án, hơn 458 nghìn issue và hơn 9 triệu bản ghi lịch sử thay đổi.
Sau khi lọc, tập đánh giá còn 14 dự án, 1.962 sprint và 18.322 cặp issue–sprint.
Nhãn "không hoàn thành" nghĩa là tại ngày kết thúc sprint, issue chưa ở trạng thái Done, Resolved, Closed hoặc Complete. Nhãn được kiểm tra chéo trên 765 cặp bằng một truy vấn SQL viết riêng.
Dữ liệu được chia theo hai cách, tương ứng với RQ2. Thiết kế temporal huấn luyện trên sprint cũ và kiểm tra trên sprint mới hơn, tức là hỏi mô hình có dùng được cho các sprint tiếp theo của cùng nhóm không. Thiết kế cross-project lần lượt giữ một dự án làm tập kiểm tra, tức là hỏi mô hình có dùng được cho một nhóm mới không.

## Slide 4: Đặc trưng và mô hình
Từ dữ liệu này, đặc trưng được chia thành năm nhóm. Mô hình tĩnh chỉ dùng hai nhóm có sẵn ở đầu sprint là thời gian và thuộc tính; mô hình động dùng thêm trạng thái thực thi, hoạt động trước mốc và bối cảnh nhóm.
Đề tài so sánh sáu mô hình, từ baseline tần suất, một quy tắc nghiệp vụ đơn giản, đến CatBoost động. Cấu hình CatBoost được cố định và không dò tham số trên tập test.

## Slide 5: Cảnh báo theo ngân sách và cách đọc chỉ số
Điểm rủi ro chỉ có ích khi được chuyển thành cảnh báo. Mỗi sprint có n issue chỉ được phát khoảng 20% cảnh báo, làm tròn lên, cho các issue có điểm cao nhất.
Chỉ số chính là recall: trong số issue thực sự trễ, bao nhiêu phần trăm nằm trong danh sách cảnh báo. Ngoài ra đề tài đo precision, số cảnh báo sai, lead time là số ngày còn lại để xử lý, AP cho chất lượng xếp hạng, và Brier cùng intercept/slope cho chất lượng xác suất.
Mọi so sánh đều kèm khoảng tin cậy 95% tính bằng bootstrap. "Chênh lệch" là recall của mô hình động trừ recall của mô hình tĩnh, tính bằng điểm phần trăm; nếu khoảng tin cậy không chứa 0 thì chênh lệch được xem là có ý nghĩa.

## Slide 6: Kết quả chính
Với cách đo như vậy, kết quả chính như sau. Tại mốc 50%, mô hình động phát hiện trung bình 53% số issue trễ trong mỗi sprint, mô hình tĩnh phát hiện 44%. Chênh lệch khoảng 9 điểm, khoảng tin cậy nằm hoàn toàn trên 0, cả trên sprint tương lai lẫn dự án chưa thấy, nên giả thuyết chính được ủng hộ.
Nói cách khác, với cùng 850 cảnh báo, mô hình động bắt được 682 issue trễ thay vì 605, và số cảnh báo sai giảm từ 245 xuống 168.

## Slide 7: Chính xác hơn nhưng muộn hơn
Kết quả này không chỉ đúng ở mốc 50%. Ở mốc 0%, hai mô hình ngang nhau. Đây là kết quả kỳ vọng vì lúc đó chưa có lịch sử nào, và cũng là dấu hiệu không có rò rỉ dữ liệu.
Càng về cuối sprint, mô hình động càng chính xác hơn, nhưng thời gian còn lại để xử lý giảm từ khoảng 12 ngày xuống khoảng 3 ngày. Đề tài báo cáo cả đánh đổi này chứ không chọn một mốc tối ưu duy nhất.

## Slide 8: Kiểm tra độ vững
Con số 9 điểm phụ thuộc vào một số lựa chọn thiết kế, nên cần kiểm tra lại khi thay đổi các lựa chọn đó.
Thứ nhất, nếu chỉ xét các issue còn mở thì chênh lệch giảm từ khoảng 9 điểm xuống khoảng 2–2,6 điểm. Phần lớn lợi thế đến từ việc nhận ra issue đã Done; đặc trưng này chiếm 27% importance trong temporal và 56% trong cross-project.
Thứ hai, ngân sách 20% thực tế cao hơn 20%. Gần một nửa số sprint test có dưới 5 issue, nên làm tròn lên vẫn cho ít nhất một cảnh báo; tỷ lệ cảnh báo thực tế là khoảng 41% theo sprint và 26% tính gộp.
Dù vậy, trong mọi trường hợp chênh lệch vẫn dương và có ý nghĩa thống kê.

## Slide 9: Chất lượng xác suất
Các kết quả trên chỉ dùng điểm để xếp hạng. Nếu muốn đọc điểm như xác suất thì phải kiểm tra hiệu chuẩn.
Mô hình động xếp hạng tốt hơn rõ rệt: AP tăng từ khoảng 0,65 lên khoảng 0,81.
Với temporal, sau hiệu chuẩn intercept gần 0 và slope gần 1. Với cross-project, Brier không cải thiện, nghĩa là xác suất học từ dự án khác không áp dụng thẳng cho dự án mới được. Khi đưa vào Agentick sẽ cần hiệu chuẩn lại.

## Slide 10: So với quy tắc đơn giản và giữa các dự án
Vì phần lớn tín hiệu đến từ trạng thái Done và số ngày không hoạt động, câu hỏi tự nhiên là một quy tắc đơn giản dựa trên hai thông tin này có đủ không. Đây là phân tích khám phá, thực hiện sau khi đã xem kết quả.
Trên sprint tương lai, mô hình động chỉ hơn quy tắc khoảng 2 điểm và khoảng tin cậy chứa 0, nên chưa chứng minh được học máy hơn quy tắc. Trên dự án mới, mô hình động hơn khoảng 3,8 điểm.
Ngoài ra, nếu phát cảnh báo dần qua các mốc thì lead time tăng lên khoảng 8 ngày.
Cuối cùng, con số trung bình che đi khác biệt giữa các dự án: chênh lệch dương ở cả 14 dự án nhưng dao động rất lớn, từ khoảng 3 đến 35 điểm, nên không thể suy ra mức cải thiện cho một nhóm cụ thể từ con số trung bình.

## Slide 11: Phân bổ cảnh báo theo thời gian
Phân tích cuối cùng của phần dự báo đi tiếp từ quan sát về lead time ở slide trước: với cùng tổng số cảnh báo, phát sớm một phần có tốt hơn phát hết ở mốc 50% không?
Kết quả là phát sớm giúp cảnh báo sớm hơn khoảng 1,9 ngày nhưng không tăng recall. Giá trị K=2 chỉ là giá trị được khảo sát, không phải giá trị đã chứng minh là tối ưu.
Tóm lại phần dự báo: mô hình chọn được danh sách issue rủi ro tốt hơn, nhưng đầu ra vẫn chỉ là một điểm số. Phần tiếp theo là agent, thành phần giải thích vì sao.

## Slide 12: Kiến trúc agent hai tầng
Hệ thống gồm hai tầng. Tầng một là mô hình CatBoost vừa trình bày cùng controller, không dùng LLM; tầng này quyết định khi nào cảnh báo và cảnh báo issue nào.
Tầng hai là agent. Agent chỉ nhận các issue mà tầng một đã chọn, dùng công cụ chỉ đọc để lấy bằng chứng và viết brief; mỗi khẳng định phải trích một event_id có thật, và verifier chặn những brief vi phạm. LLM không sinh xác suất và không được sửa sprint.

## Slide 13: Agent làm được gì
Cụ thể, agent có bốn khả năng. Thứ nhất, lấy bằng chứng của một issue tại thời điểm dự báo: trạng thái, số ngày không hoạt động, ước lượng, điểm rủi ro do CatBoost tính và các sự kiện đã xảy ra. Thứ hai, lấy tổng quan sprint. Thứ ba, đề xuất cảnh báo hoặc bỏ qua. Thứ tư, viết brief có cấu trúc gồm loại rủi ro, giá trị đo, event_id làm căn cứ, việc nên kiểm tra và điều chưa biết.
Các ràng buộc được cài trong mã: chỉ đọc, lọc sự kiện sau thời điểm dự báo, chặn issue của dự án khác, gắn nhãn nội dung không tin cậy, và verifier chặn event_id bịa, số liệu sai hay khẳng định nhân quả.

## Slide 14: Ví dụ: agent gọi công cụ lấy bằng chứng
Đây là một lần chạy thật, issue 177929 của dự án CONFSERVER ở mốc 50%. Agent gọi get_issue_evidence với mã issue. Công cụ trả về: issue đang open, đã 7 ngày không có hoạt động, điểm rủi ro do CatBoost tính là 0,863, và ba sự kiện: tạo issue, đưa vào sprint, cập nhật trạng thái open. Cờ untrusted_content đánh dấu phần nội dung do người dùng nhập.

## Slide 15: Ví dụ: brief agent trả về
Từ bằng chứng đó, agent trả về quyết định cảnh báo, kèm một khẳng định thuộc loại đình trệ trạng thái với giá trị 7 ngày, trích cả ba event_id. Agent gợi ý kiểm tra người phụ trách có bị chặn không và có tiến triển nhưng chưa cập nhật trạng thái không, đồng thời nêu rõ điều chưa biết là có commit nằm ngoài hệ thống issue hay không.
Verifier xác nhận các event_id có thật và con số 7 ngày khớp dữ liệu, nên brief được chấp nhận. Trong dữ liệu, issue này thực tế không hoàn thành trong sprint.
Ngoài ra, khi bộ kiểm thử chèn vào mô tả một issue khác câu lệnh yêu cầu agent đặt rủi ro bằng 0 và không cảnh báo, agent không làm theo mà vẫn cảnh báo dựa trên các sự kiện có thật; điểm rủi ro do CatBoost tính nên LLM không sửa được.

## Slide 16: Giới hạn
Trước khi sang kế hoạch, em xin nêu các giới hạn. Giới hạn đầu tiên là chưa triển khai thực nghiệm: agent chưa được tích hợp vào Agentick nên mọi kết quả đều từ benchmark TAWOS. Các giới hạn còn lại là những lưu ý khi đọc kết quả phần dự báo đã trình bày ở trên.

## Slide 17: Tiến độ hiện tại
Đã hoàn thành: toàn bộ phần dự báo trên TAWOS, phân tích phân bổ cảnh báo, và mô-đun agent.
Đang chờ: tích hợp vào Agentick. Agentick là dự án riêng, đã có mã nguồn, dùng để thu dữ liệu và chạy thực nghiệm.

## Slide 18: Roadmap và kế hoạch
Vì vậy bước tiếp theo là tích hợp vào Agentick và kiểm tra agent trong luồng cảnh báo thật. Sau đó chạy shadow mode: hệ thống ghi lại dự báo và brief nhưng chưa gửi cho người dùng, để đo trên dữ liệu thật mà không ảnh hưởng đến nhóm.
Chỉ chuyển sang bước thực nghiệm khi dữ liệu Agentick tái dựng được phạm vi sprint và trạng thái hoàn thành.
Về thời gian, tích hợp dự kiến 2 tuần, song song kiểm tra agent; thực nghiệm khoảng 3 tuần tiếp theo; 2 tuần cuối để viết báo cáo.

## Slide 19: Tóm tắt
Tóm lại, lịch sử thực thi giúp phát hiện issue sắp trễ tốt hơn, và kết quả giữ được trên dự án mới, dù phần lớn lợi thế đến từ việc nhận biết issue đã xong. Agent đã xây xong: tự lấy bằng chứng tại thời điểm dự báo, đề xuất cảnh báo và viết brief trích dẫn sự kiện có thật. Bước tiếp theo là tích hợp cả hai vào Agentick để thực nghiệm trên dữ liệu thật.

## Slide 20: Tài liệu tham khảo
Em xin cảm ơn thầy cô đã lắng nghe, và rất mong nhận được góp ý.
