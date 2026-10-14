# Nghiên cứu video: 180 giây, 1 ảnh/giây

Đọc [trạng thái ngày 14/10](research/2026-10-14_reference_study.md) trước khi gọi
nhận xét nào là quan sát khung hình. Phiên này không tải/phát được media:
**540 ảnh OverSimplified chưa được lấy**. Công cụ đã được kiểm tra bằng video
giả lập; test đó không phải bằng chứng nghiên cứu kênh.

## Chạy từ bản clone

Cần Python, Pillow, FFmpeg và FFprobe trên PATH. Riêng lấy mẫu không cần GPU,
Flow, OmniVoice, Small-SFX, cookies, API key hoặc môi trường Manim.
Đặt video thật vào `inputs/reference-videos/` tại root theo tên trong
[manifest](../examples/reference-windows.json), hoặc sửa `file` tới video local.
`source_url` ghi xuất xứ; công cụ không tự tải URL. Chạy từ `Code2Video`:

```powershell
python -m pip install Pillow
python local_tools/production.py reference-study examples/reference-windows.json --output ../outputs/reference-study
```

Manifest dùng `schema_version=reference-study/1`. Mỗi video có `id`, `file`,
`source_url`, `start_second`, `duration_seconds` (mặc định 180), `sample_width`
(mặc định 960). `video_start_second` ánh xạ giây 0 của file đã cắt sang clock
nguồn. File chứa đoạn gốc 60–240s dùng start=0, offset=60, duration=180.
Video đầy đủ dùng offset=0. Tăng kích thước ảnh không tăng chi tiết nguồn.

Khoảng nửa mở `[0,180)` có đúng **180 mẫu: 0, 1, …, 179**, không thêm ảnh 180.
Chọn frame giải mã đầu tiên tại/sau mỗi mốc. Receipt ghi cả mốc yêu cầu, PTS
thực và độ trễ. Clock local đưa frame đầu về 0 rồi cộng offset đã khai. Không
gọi caption time hay target 0.3s là PTS thật nếu frame được giải mã tại 0.5s.

Video thiếu/ngắn, HTML giả dạng video, thiếu frame hoặc khoảng trống giải mã
không đáp ứng giây lấy mẫu làm lệnh lỗi; không chèn thumbnail hay ảnh giả cho
đủ số. Chọn output mới; không ghi đè mẫu/review cũ. Chỉ xuất receipt cuối khi
tất cả video có đủ mẫu.

## Đầu ra và review

- `study.json`: hash nguồn/manifest, phiên bản FFmpeg, mốc nguồn, PTS, kích thước
  và hash từng ảnh, tổng số mẫu; review ban đầu `UNVERIFIED`.
- Mỗi video: 180 JPEG, sáu contact sheet 30 ảnh và `annotations.csv` để ghi
  scene/shot, anchors, FG/MG/BG, attention, action, camera, knowledge delta,
  cut trigger, carried state và nhận xét thực.

Đọc tất cả sheet theo thứ tự, mở ảnh lớn ở cảnh khó, ghi ID/vùng ảnh đã kiểm
tra. 180 mẫu không đồng nghĩa 180 shot/panel. Phân biệt biểu cảm/zoom trong
cùng shot, cut trong cùng scene, đổi nơi/thời gian, insert và return. Ghi
start/action/end và carry/delta. Với 1 Hz, cut chỉ được khoanh trong khoảng
giữa hai mẫu; xem lại frame rate gốc để xác định ranh giới chính xác. Chi tiết
không đủ rõ và chuyển động giữa hai ảnh giữ `UNVERIFIED`.

Đánh dấu sponsor/merch nằm trong cửa sổ và loại khỏi kết luận về storytelling;
không sửa clock để giấu chúng. Audio phải nghe riêng; caption không chứng minh
mix, gain hay lip-sync. Video/ảnh giữ local ở `inputs/reference-videos/` và
`outputs/`; commit ghi chú nguyên gốc, URL, cửa sổ, hash và giới hạn, không
chép video/phụ đề toàn tập/ảnh bên khác vào source repo.

Áp dụng vào [scene/shot grammar](SCENE_SHOT_GRAMMAR.md). Video hoàn thiện không
chứng minh storyboard, rig hay công cụ nội bộ của tác giả.
