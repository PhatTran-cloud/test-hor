# OverSimplified: trạng thái khảo sát video ngày 13/10/2026

**Chưa hoàn tất khảo sát video. 0/540 ảnh được trích và xem.**
Không có kết luận mới từ frame, số lượng cut, thời lượng shot, biểu cảm thực hay
liên kết được quan sát trong ba đoạn. Các sửa staging trong repo là đề xuất từ
yêu cầu của người dùng và ví dụ horror hiện có, không phải kết quả 540 ảnh.

## Phạm vi đã chọn

| Video nguồn chính thức | Đoạn dự kiến | Ảnh yêu cầu | Ảnh thực có |
| --- | --- | --- | --- |
| [The French Revolution – Part 1](https://www.youtube.com/watch?v=8qRZcXIODNU) | 00:00–03:00 | 180 | 0 |
| [Prohibition](https://www.youtube.com/watch?v=AAGIi62-sAU) | 00:00–03:00 | 180 | 0 |
| [The Pig War](https://www.youtube.com/watch?v=QLq6GEiHqR8) | 17:00–20:00 | 180 | 0 |

Các mốc này là phạm vi dự kiến, chưa được xác nhận là phần dựng cảnh phù hợp nhất
vì video không phát được. Có thể chọn lại sau khi nhận được file nguồn thật.
Metadata lấy được: lần lượt 1.074, 2.023 và 2.323 giây; không thay thế việc xem.
Trang tuyển dụng chính thức https://www.oversimplified.tv/create phân biệt
animation, asset creation và research/writing; nêu After Effects và Photoshop.
Trang đó không công bố shot list, quota layer hoặc số pose cho nhân vật chính.

## Thử truy cập và kết quả thực

1. Xác minh các URL bằng tìm kiếm/trang YouTube; một lần mở web French nhận 429.
2. yt-dlp 2026.8.19 lấy được title/duration và metadata các nguồn. Client mặc
   định không có stream dùng được; web/android có metadata MP4 itag 18.
3. Tải đoạn bằng FFmpeg thất bại: endpoint media trả HTML thay vì MP4. Thử tải
   trực tiếp French nhận HTTP 200 nhưng Content-Type=text/html và file 195 byte
   có tiêu đề Site Unavailable. File này bị loại, không được coi là video.
4. Player French trong trình duyệt mở được trang/title/duration, đóng cookie và
   thử phát; currentTime=0, readyState=0, videoWidth=0, videoHeight=0. Không có
   frame video thật. Không suy ra YouTube ngừng hoạt động hoặc người dùng bị chặn.
5. Preview storyboard chính thức là khoảng 9,9 giây/ảnh, vốn không đạt 1 Hz.
   Kiểm tra các sheet trong ba cửa sổ cũng trả HTML lỗi; không có ảnh để phân tích.

Không dùng thumbnail, transcript hoặc ảnh AI để thay thế 540 frame. Không lưu
signed media URLs/IP/tokens, video hay preview gốc vào source công khai.

## Phần repo đã làm được

- Thêm `reference-sample` để lấy 180 ảnh thật từ file local dài đủ 3 phút, kèm
  contact sheets, timestamp danh nghĩa, hash nguồn/ảnh và metadata FFmpeg.
- Thêm `reference-check` để kiểm tra file/hash/timestamp và độ phủ ghi chú. Nó
  không tự ghi rằng người phân tích đã xem ảnh hoặc tự PASS chất lượng.
- Thêm staging dùng chung trong scene, named shot views, chi tiết nền tĩnh có ý
  nghĩa và loại liên kết giữa shot; giữ storyboard nhẹ, không quota metaphor/layer.
- Giữ ensemble 9/4/1 người, trạng thái/gaze và asset coverage; prompt nền và brief
  motion cùng nhận được geography/static detail/story link. Mọi art vẫn chưa tạo.

Muốn hoàn tất phần khảo sát, cần ba file video hoặc ba clip 3 phút truy cập được.
Quy trình tiếp tục: [REFERENCE_VIDEO_STUDY.md](../REFERENCE_VIDEO_STUDY.md).
Sau khi có file, trích đủ 540 ảnh, xem/ghi chú từng nhóm shot, kiểm tra chỗ nối
và cập nhật lại đề xuất theo bằng chứng. Không đổi status trước khi thực sự làm.

## Kiểm tra triển khai source

- 134 unittest qua; TypeScript `npm run check` qua; skill metadata hợp lệ.
- Chạy CLI trên video kỹ thuật tự tạo dài 180 giây: đúng 180 JPEG/9 contact
  sheets, hash và timestamp danh nghĩa hợp lệ. Đối chiếu mẫu với frame lấy trực
  tiếp từ source; dùng round=up để giữ mốc giây, tránh lệch nửa giây của round=near.
- Công cụ từ chối file HTML 195 byte đã tải nhầm đuôi MP4; không tạo cache giả.
- Xuất lại ensemble: 8 asset/12 prompt/3 shot, 9→4→1 người; hai brief cùng hash
  plan. Còn 4 thiết kế nhân vật và 1 setting proposal cần chốt cho một phim thật.
- Forward-use skill phát hiện thiếu setting ở motion và câu plug insert mơ hồ;
  đã đưa brief setting vào handoff, cảnh báo setting chưa chọn, sửa lời event và
  bỏ body/hatch khỏi visible inventory ở shot cuối, giữ event/source ngoài khung.
- Lượt forward-use mới xác nhận handoff; phát hiện wording attendant held worry
  trái với ordinary checking concentration trước gõ. Đã thống nhất về tập trung
  bình thường trong design/state của prompt, không tạo phản ứng sợ sớm.

Các test/smoke/forward-use này kiểm tra source/handoff, **không** phải 180 hay
540 frame OverSimplified, art/motion/VFX/audio PASS hoặc kiểm chứng độ kinh dị.
