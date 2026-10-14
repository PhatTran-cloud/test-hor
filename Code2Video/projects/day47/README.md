# Ngày 47

Kịch bản gốc của người dùng → Edge TTS tiếng Việt → timeline đo theo PCM →
16 shot vẽ bằng JavaScript/SVG → animatic Remotion và bản Hyperframes cùng hình.
Lượt dựng này dài 92,5 giây / 5550 frame, 1920×1080, 60 fps.

Yêu cầu ngày 14/10/2026 chọn **Edge TTS và tranh code JS** cho phim này.
`src/script.mjs` ghi nguyên văn quyết định và kịch bản. Override chỉ áp dụng
`production_mode=day47-storyboard-js`; các phim khác giữ workflow V4.1 hiện có.
Không suy ra tuổi hoặc diện mạo từ giọng; nhân vật chỉ xuất hiện qua POV/găng tay.

## Clone và chạy

Cần Node.js 22+, FFmpeg/FFprobe trên PATH và Edge TTS 7.3.1:

```bash
git clone --depth 1 https://github.com/PhatTran-cloud/test-hor.git
cd test-hor/Code2Video/projects/day47
npm ci
python -m pip install edge-tts==7.3.1
npm run all
```

`all` tạo giọng, đo clock, xuất board/tranh, chuẩn bị Hyperframes và render
animatic bằng Remotion. Chrome được Remotion tải nếu chưa có. Nếu dùng browser
cài sẵn, đặt `CHROME_BIN` thành đường dẫn executable. Nếu `edge-tts` chưa có
trên PATH, đặt `EDGE_TTS_PYTHON` thành executable Python đã cài module.
Mọi tranh/timing/renderer đều viết bằng JavaScript; Python chỉ là client Edge TTS.

Entrypoint của repo cũng hỗ trợ các bước này:

```bash
cd ../..
python local_tools/production.py storyboard-js all
python local_tools/production.py storyboard-js audit
python local_tools/production.py storyboard-js check
python local_tools/production.py storyboard-js hyperframes
```

`hyperframes` lint rồi render bản MP4 thứ hai ở 60 fps. Có thể đặt
`HYPERFRAMES_BROWSER_PATH` khi dùng Chrome sẵn có. Các file video, giọng,
tranh, HTML xem storyboard và bản Hyperframes được xuất vào `outputs/day47/`
ở gốc repo, không commit node_modules hoặc media vào Git.

## Đọc và chỉnh

- [STORYBOARD.md](STORYBOARD.md): bảng thời gian, thông tin, hình và nối shot.
- [storyboard.json](storyboard.json): packet schema 4, `scene-shot/1`, IDs,
  trạng thái, ceiling, voice receipts và clock lần dựng đã đo. Clone không
  kèm giọng đã render; tạo lại giọng sẽ tự đo lại và cập nhật packet này.
- `src/board.mjs`: scene worlds, shot intent, canon IDs, sự kiện và các hold.
- `src/draw.mjs`: từng vật thể SVG rời và một hàm `renderFrame(board, frame)`.
- `src/script.mjs`: lời kể và khoảng nghỉ. Khi sửa lời, cập nhật `SCRIPT` và
  `CUES` cùng nhau rồi chạy lại `voice`; lệch nội dung sẽ bị từ chối.
- `tools/voice.mjs`: cache theo hash yêu cầu/MP3/boundaries, decode PCM48k,
  đệm tối đa dưới một frame để căn clock, không time stretch.

Một sự kiện blink nối hai góc nhìn. Ba HELLO có chung nguồn anten; phản hồi
đến đúng 240 frame sau lần gửi cuối. Co đá/đổi gaze có mốc biên tập trong
đoạn đọc thực tế; không gắn nhãn word alignment. Độ cong chỉ là hình minh hoạ,
không mô phỏng Einstein số. Mốc 600000 km cần giả định đáp tức thì và đường
truyền trực tiếp; “ngôi sao gần nhất” được hiểu là ngoài Mặt Trời gần hệ Mặt Trời.

`storyboard-js audit` kiểm tra cấu trúc scene/shot của packet override;
không thay cho các validator/phê duyệt phim đầy đủ của pipeline OmniVoice/Flow.
Giữ riêng kiểm tra kỹ thuật, kiểm tra khung hình và duyệt giọng bằng nghe.
Nhạc/SFX để trống có chủ ý; không có phụ đề cháy hoặc HUD trang trí.
Đây là storyboard/animatic để duyệt, không tự cấp FINAL PASS hoặc release.

```bash
npm run check
npm run voice
npm run board
npm run stills
npm run render
npm run hyperframes
```

Nếu Chrome không khởi chạy trong máy/môi trường hiện tại, `npm run raster-preview`
xuất bản xem có giọng bằng chính các SVG JavaScript qua Sharp + FFmpeg, giữ
nguyên từng frame/clock. File là `day47-animatic.mp4`. Đây là renderer cho bản
xem; không được ghi nhận là kiểm tra MP4 của hai adapter browser. Xem
[REVIEW.md](REVIEW.md) để biết lượt render nào đã chạy thực tế.
