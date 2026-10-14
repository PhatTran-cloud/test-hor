# Nghiên cứu tham chiếu và cập nhật repo — 14/10/2026

Yêu cầu: vài video, mỗi video 3 phút, 1 ảnh/giây; phân tích bên trong shot và
liên kết shot/scene rồi cập nhật repo. Chọn ba nguồn OverSimplified theo hướng
đã có, cửa sổ gốc `[00:00,03:00)`: mục tiêu **540 ảnh**.

**Trạng thái thực: 0/540 frame giải mã, 0/540 frame đã kiểm tra.** Đã lấy và đọc
metadata/phụ đề gốc của cả ba. Tải media trả HTML “Site Unavailable”; FFmpeg
không giải mã được. Browser mở được trang nhưng player vẫn 0:00, readyState=0,
videoWidth/videoHeight=0. Preview sheet cũng không trả ảnh hợp lệ. Không gọi
đây là nghiên cứu hình 1 Hz, không bổ sung nhận xét visual giả từ phụ đề.

| Video nguồn | Cửa sổ | Bằng chứng hiện có | Mẫu hình |
| --- | --- | --- | --- |
| [French Revolution Part 1](https://www.youtube.com/watch?v=8qRZcXIODNU) | 0–180s | metadata + caption | BLOCKED, 0 |
| [The Pig War](https://www.youtube.com/watch?v=QLq6GEiHqR8) | 0–180s | metadata + caption | BLOCKED, 0 |
| [Prohibition](https://www.youtube.com/watch?v=AAGIi62-sAU) | 0–180s | metadata + caption | BLOCKED, 0 |

Xuất xứ, hash nguồn phụ đề/metadata, phạm vi và số cue ở
[receipt](2026-10-14_reference_evidence.json). Không commit video hay phụ đề toàn
tập. Metadata ghi cùng channel ID `UCNIuvl7V8zACPpTmmNIqP2A`.

## CAPTION: cấu trúc kể chuyện có thể phân tích

Mốc dưới đây là **timestamp caption**, không phải ranh giới shot đã quan sát.
Các mô tả nói về nội dung của video; không dùng làm xác nhận lịch sử. Sponsor
và merch đầu video được tách khỏi nhận xét storytelling.

| Nguồn / mốc caption | Nhận xét giới hạn ở lời và stage note |
| --- | --- |
| French, 21.160–43.040 | Trò chuyện đặt áp lực lên nhân vật; thông tin tài chính nối với trách nhiệm. |
| French, 43.040–69.320 | Nghi lễ chuyển tới phòng ngủ; lời/stage note giữ cùng nhân vật và tình thế. |
| French, 70.440–99.040 | Các lời đã xuất hiện quay lại, tích lũy áp lực trước phản ứng. |
| French, 103.620–175.100 | Giải thích xã hội quay về đối thoại và đạo cụ lặp, làm bất bình đẳng cụ thể. |
| Pig War, 23.687–56.470 | Mong muốn mở rộng gặp phản bác; phản ứng kéo cùng mục tiêu qua thoại. |
| Pig War, 56.470–87.510 | Thuyết minh chuyển tới thương lượng; lãnh thổ giữ vấn đề trung tâm. |
| Pig War, 87.510–141.650 | Giải pháp biên giới được đặt rồi bị thông tin địa lý mới bác bỏ. |
| Pig War, 147.550–179.540 | Thương lượng lặp sau xung đột; motif giải pháp cũ nhận thêm ngữ cảnh. |
| Prohibition, 12.932–46.455 | Sinh hoạt ăn uống nối tới công việc nguy hiểm và hậu quả; crash chỉ là cue caption. |
| Prohibition, 50.758–94.370 | Narrator gom các ví dụ quanh một thói quen xã hội chung. |
| Prohibition, 95.813–129.670 | Đối thoại nơi làm việc và nhóm hỗ trợ cụ thể hóa chuẩn mực đảo ngược. |
| Prohibition, 129.670–180.000 | Phản bác chuyển sang hậu quả gia đình/công việc; giữ chủ đề qua đối thoại. |

Các caption không xác nhận kích thước shot, số cut, layout, màu/ánh sáng, lớp
ảnh, hướng nhìn hay kiểu zoom. Chưa nghe audio nên chưa đánh giá gain/mix,
voice acting, J/L cut, lip-sync hoặc timing của hiệu ứng bằng tai.

## PROPOSED: đưa vào tác giả và công cụ

- Khóa scene world/anchors; shot đổi framing và thông tin trên cùng world.
  Phân biệt lived-in background với insert giản lược bằng chức năng của cảnh.
- Card ghi function/attention, FG/MG/BG, start/action/end, knowledge/reveal.
  Diễn xuất và đạo cụ có mục đích; deliberate hold hợp lệ.
- Edge ghi cut trigger, relation, carry state/channel và next information delta.
  Giữ motif/vết dấu/ownership và kiểm tra state khi quay lại một world.
- Dùng schema 4 hiện hành; contract `scene-shot/1` là phần tác giả opt-in,
  không đổi thành schema của plugin ngoài và không tự art/audio PASS.

Đã thêm `production.py reference-study` để giải mã video local ở 1 Hz, ghi PTS,
hash, sheet và CSV ghi chú trống. Đã thêm `storyboard-audit` và kiểm tra opt-in
trước production check/prompt export; execution context giữ card của shot liền
kề. [Scene/shot grammar](../SCENE_SHOT_GRAMMAR.md) và skill Horror Asset Director
hướng dẫn cùng contract. [Cách lấy mẫu](../REFERENCE_STUDY.md) có manifest ba video.

Test FFmpeg dùng clip giả lập 180s xác nhận đúng 180 JPEG và clock 0–179; test
đó chỉ kiểm tra công cụ. Không biến fixture thành bằng chứng OverSimplified.

## Phần còn thiếu và điểm dừng

Cần video local hợp lệ để chạy manifest, inspect đủ 540 ảnh và bổ sung bảng shot/
scene dựa trên pixel, sau đó xem lại những ranh giới khó ở frame rate gốc.
Chưa tạo artwork, TTS/SFX, animatic hoặc render phim. Không thay đổi kịch bản,
cast, thời đại và các lựa chọn đã duyệt. Bản update này là công cụ/tác giả và
nghiên cứu caption có giới hạn; nghiên cứu hình 1 Hz vẫn chưa hoàn thành.
