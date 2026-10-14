# NGÀY 47 — Storyboard có lời đọc

5550 frame, 92.500 giây, 1920×1080 / 60 fps. 16 shot; Edge TTS vi-VN-NamMinhNeural, rate -8%, pitch -6 Hz. Không kéo giãn âm thanh.

Giữ nguyên kịch bản người dùng. Nhân vật chỉ lộ găng tay và POV; không suy ra tuổi/diện mạo từ giọng. Tranh SVG gốc vẽ bằng JavaScript; Remotion và Hyperframes dùng cùng hàm renderFrame.

| Shot | Giây | Chức năng | Hình / hành động | Trần tiết lộ |
| --- | --- | --- | --- | --- |
| s01_receive | 0.00–10.98 | Câu trả lời đến trước câu hỏi | Opening already holds three RX marks beside empty TX; range appears at the second measured VO passage | Only a nearby answer; no eye, creature or outside hand |
| s02_behind | 10.98–15.63 | Ngay sau lưng trạm | Hold station right of a large dark rear region; reveal nothing in that region | Absence and proximity only; no organic ring |
| s03_listen | 15.63–23.92 | Nín thở | Blue glove stays off the key; empty window and frozen radio hold against the VO | Space seems attentive; no physical monster |
| s04_send | 23.92–31.50 | Ba HELLO / bốn giây chờ | Three discrete radio wavefronts leave antenna toward Jupiter; then digital silence for four seconds after the last send | Only the outbound test; no return at Jupiter |
| s05_answer | 31.50–35.25 | Phản hồi | RX waveform arrives exactly 240 frames after last HELLO; blue hand arrests above the keys | Incoming response only; do not identify the responder |
| s06_distance | 35.25–44.73 | 600.000 km | Same CRT compares outbound/return trace; range readout is inferred, not a measured angular position | Range is roughly 600000 km under prompt-response assumption; Sun excluded from nearest-other-star claim |
| s07_stone | 44.73–47.98 | Tưởng là đá | A chipped rock fills foreground; other rocks are cropped into an irregular arc | Stone silhouettes only; no full eye outline |
| s08_contract | 47.98–53.20 | Cả vành đai co lại | All stones contract toward one center together, preserving their order; no gravity/impact excuse | One coordinated ring; eye identity and pupil withheld until next shot |
| s09_eye | 53.20–57.62 | Bay trong mắt nó | The contracted annulus becomes readable as iris; tiny station remains inside, never jumps outside | Eye geometry allowed; full creature body and narrator transformation remain hidden |
| s10_lens | 57.62–63.65 | Ánh sáng cong | Stable star pair bends only around the field visible through the same rear window | Known eye plus bent starlight; no gaze shift yet |
| s11_look | 63.65–70.90 | Nó nhìn lại | Long locked hold; the dark center changes alignment toward the viewer late in the measured line | Returned gaze allowed; no external glove or infection reveal |
| s12_blink | 70.90–73.00 | Tôi chớp mắt | POV closes from top and bottom at the shared absolute blink event; aperture stays closed at the cut | Narrator POV blink only; no face needed |
| s13_station_blink | 73.00–77.33 | Trạm cũng chớp mắt | Begin with station aperture closed; reopen on the same global blink envelope; preserve the enclosing iris | Station/observer coupling; no narrator outside yet |
| s14_warning | 77.33–82.08 | Đừng trả lời | A different glove stops short of REPLY; closed door holds beside it | A new listener hears warning; narrator identity still withheld |
| s15_memory | 82.08–86.63 | 47 ngày trước | Return to DAY 00 log and the same blue wrist stripe near transmit control | Previous listener was narrator; outside hand remains hidden |
| s16_knock | 86.63–92.50 | Tao đang gõ cửa | Same blue glove rises outside glass and makes one knuckle contact; receiver glove remains out of frame; door stays locked | Narrator is now the arriving thing; body and cosmic cause remain unseen |

## Các nối cảnh quan trọng

- Mở DAY 47, sau đó lùi về lần thử đầu DAY 00; không thêm lời kể.
- HELLO thứ ba tại frame 1650; RX tại frame 1890: chênh đúng 240 frame / 4.000 giây.
- Đá → co đồng loạt → mắt: cùng belt_01, giữ thứ tự góc và vị trí trạm ở bên trong.
- Hai góc nhìn chớp mắt dùng một sự kiện frame 4366–4416; cắt trong lúc đóng, mở lại ở ngoài trạm.
- Găng xanh/cổ tay hổ phách ở đầu trở thành găng bên ngoài cửa ở cuối; găng người nhận màu đất để tránh nhầm. REPLY không được bấm.

## Giới hạn khoa học và kiểm tra

4 giây là thời gian đi và về. D = c × 4 / 2 = 599584.916 km, làm tròn 600000 km nếu thứ trả lời đáp ngay; nếu có độ trễ xử lý, đây là cận trên theo giả định đường truyền trực tiếp. “Ngôi sao gần nhất” được hiểu là ngoài Mặt Trời ở gần hệ Mặt Trời, không là khẳng định ở mọi vị trí trạm. Vành đai/mắt/chớp mắt là hư cấu, không mô phỏng hấp dẫn số.

Nguồn: [NIST](https://physics.nist.gov/cuu/Constants/Value/c.html), [NASA](https://science.nasa.gov/mission/hubble/science/science-behind-the-discoveries/time-travel-observing-cosmic-history/), [Edge TTS](https://github.com/rany2/edge-tts), [Remotion](https://www.remotion.dev/docs/the-fundamentals), [Hyperframes](https://hyperframes.app/docs/2-concepts/3-frame-adapters).

Mốc nội bộ co vành đai/đổi gaze là nhịp biên tập trong đoạn đo, không gắn nhãn word alignment. Boundary Edge là metadata dịch vụ, không là kiểm tra bằng nghe. Nhạc và SFX để trống có chủ ý. Không có phụ đề cháy hoặc HUD trang trí. Kiểm tra cấu trúc, khung hình render và nghe giọng ghi riêng trong REVIEW.md; đây là storyboard để duyệt, chưa phải phim đã release.
