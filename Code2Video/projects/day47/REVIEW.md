# Kiểm tra bản storyboard Ngày 47

Bản giao là **animatic để duyệt**, 16 shot, 92,500 giây, 1920×1080 / 60 fps.
Giữ nguyên 20 đoạn của kịch bản; giọng Edge TTS vi-VN-NamMinhNeural.

| Hạng mục | Kết quả thực tế |
| --- | --- |
| Giọng và clock | 20 take Edge TTS thật; PCM48k có 4.440.000 sample, 5550 frame; không time stretch |
| Chờ phản hồi | HELLO cuối f1650 / 27,500s; RX f1890 / 31,500s; đúng 240 frame |
| Cấu trúc | `scene-shot/1` STRUCTURE_CHECKED; 4 scene world, 16 shot, các state change và time jump có khai báo |
| Mã | 7 kiểm tra JS và 92 regression test của repo đạt |
| MP4 bản xem | JS/SVG → Sharp → FFmpeg; H.264 + AAC; hai track bắt đầu 0 và dài 92,500s; video đủ 5550 frame |
| Khung hình | Lấy mẫu 80 frame từ MP4 ở start/end shot, các pha event và panel; xem 4 sheet gồm 20 frame/sheet |
| Đồng bộ audio | 4 cửa sổ kiểm tra AAC so với PCM có lag 0 sample; tương quan >0,9996; peak PCM −3,71 dBFS, RMS −21,32 dBFS |
| Remotion | Composition/bundle đã build; render browser chưa kiểm tra được: Chrome thoát mã 133 trong môi trường này |
| Hyperframes | HTML/GSAP đã build và lint không có error; 1 warning về độ dài HTML được biên dịch. MP4 browser chưa xuất được |
| Nghe và duyệt diễn xuất | UNVERIFIED; số đo/boundary dịch vụ không thay cho việc nghe giọng |
| Release phim | Không yêu cầu; không tự cấp FINAL PASS |

Kiểm tra hình tập trung vào TX trống/RX có tín hiệu, phía sau trạm chưa lộ mắt,
nguồn ba wavefront gắn đầu anten, đá co đồng loạt trước khi lộ iris, vùng cong chỉ
đổi gaze cuối câu, cùng một blink nối POV với cửa kính trạm, và găng xanh/cổ tay
hổ phách xuất hiện ngoài cửa ở cuối. Găng người nhận không trở lại nút REPLY.
Cửa vẫn khoá và dấu tiếp xúc tồn tại trong hold cuối.

Đây là kiểm tra theo mẫu khung hình, không là chứng nhận mọi frame hoặc mức độ
gây sợ. Hình tối/các hold có chủ ý; nhạc và SFX để trống, không có phụ đề cháy
hay HUD trang trí. Chưa xem/nghe toàn bộ video theo thời gian thực.

Hai adapter dùng cùng `renderFrame(board, frame)` và có mã/lệnh trong repo.
`raster-preview` là bản xuất riêng có nhãn rõ, không được tính là render thành
công bằng Remotion/Hyperframes. Không đổi provider giọng hoặc thay giọng bằng
silence khi renderer bị lỗi. Mốc lens/gaze trong đoạn đọc là nhịp biên tập;
không khai là word alignment.

`outputs/day47/` giữ voice receipts/hashes, `structure-audit.json`,
`preview-probe.json`, `hyperframes-lint.json`, `audio-timing-check.json`,
và ảnh/index frame review. Media và thư viện cài đặt được loại khỏi Git để
repo vẫn nhẹ; clone tạo lại bằng các lệnh trong README.
