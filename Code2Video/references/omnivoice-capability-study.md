# OmniVoice Docker — khả năng voice instruction cho V4.1 horror

Nghiên cứu tiếp theo đã đối chiếu upstream mới, V4 mixer và nguồn SFX; xem [thiết kế audio tích hợp và lịch chạy tuần tự](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/audio-capability-and-integration.md). Reference style có thể thắng instruct; không coi clone + whisper là bảo đảm chuyển mood.

Ngày 11/10/2026. Đầu vào: người dùng có OmniVoice, đã mở Docker, yêu cầu nghiên cứu dùng voice instruction/cảm xúc. Phạm vi: kiểm tra dịch vụ, API, source runtime và tài liệu; chưa synthesize, chưa nghe audio, chưa sửa V4 hoặc Docker.

## Kết luận

**Có voice instruction, nhưng bản hiện tại không nhận chỉ dẫn cảm xúc tự do.** `whisper` được hỗ trợ. `scared`, `angry`, `sad` và “terrified but trying to remain calm” bị parser từ chối. Có voice cloning, voice design và non-verbal tags, nên OmniVoice là ứng viên đáng thử cho cast narrator/character; chưa đủ chứng minh đáp ứng diễn xuất toàn bộ mood horror.

Điểm quan trọng của máy người dùng: runtime có trường Instruct ngay trong Voice Clone và truyền cùng reference vào model. Đường này dùng cùng parser thuộc tính giới hạn, không phải một API emotion riêng.

## Dịch vụ và bằng chứng local

| Mục | Đã xác minh |
|---|---|
| Container | `omnivoice-demo`, image `omnivoice:latest`, healthy tại lúc kiểm tra |
| URL | `http://127.0.0.1:8001` |
| Package runtime | `omnivoice` 0.2.0 |
| UI | Gradio 6.20.0, OmniVoice Demo, API prefix `/gradio_api` |
| API | `/_clone_fn`, `/_design_fn`, metadata lấy từ GET `/gradio_api/info` |
| Image ID | `sha256:d739b902c8f14e41bff7860a9ed595976dfb602321f3bfc5f30c6f4d69a4032f` |
| Reference có sẵn | `C:/Users/thebl/Downloads/jameson.mp3` tồn tại; chưa nghe/đánh giá trong bước này |
| Service khác | `docker ps` lúc kiểm tra chỉ có OmniVoice; chưa xác nhận Whisper running |

Không suy ra model checkpoint/revision chính xác từ package version hoặc tên image `latest`. Không chạy synthesis nên healthy/API đọc được chưa chứng minh GPU inference thành công hay chất lượng audio.

Source chép trực tiếp từ container vào [omnivoice-runtime](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-runtime/demo.py). Đây là snapshot nghiên cứu, không sửa bản đang chạy. Model hash `156510d8f2ea37e40766e53a3d3aa0d5769e51121fe924488def2bdb198d1eba`.

**Không lấy API từ working copy local một cách mặc định:** `D:/omnivoice/omnivoice` có HEAD `b2dcccaa9f68fe0255326ce675d24b6d112b685a`; source demo local không có Instruct trong clone, runtime có. Hash source cũng khác. Do đó metadata/source runtime là căn cứ cho cách gọi dịch vụ đang chạy. Chưa xác định nguyên nhân hoặc lịch sử khác biệt đó.

## Instruction: đọc source và kiểm tra thực sự

Nguồn chính thức: [Voice Design](https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md), [README](https://github.com/k2-fsa/OmniVoice). Voice design có nhóm gender, age, pitch, style `whisper`, English accent và Chinese dialect; mỗi nhóm chọn tối đa một thuộc tính. Instruction dùng tiếng Anh/Trung, không phải văn xuôi diễn xuất tùy ý.

Source runtime: [thuộc tính hợp lệ](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-runtime/voice_design.py), [parser](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-runtime/model.py:1364). Preprocess gọi parser cho instruction ở cả đường có reference; không chỉ kiểm tra dropdown UI.

Đã chạy riêng parser gốc trích bằng AST từ snapshot cùng constants gốc; không import/tạo model, không gọi TTS và không dùng GPU. [Script nghiên cứu](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-runtime/check_instruction_contract.py) · [kết quả JSON](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-runtime/instruction-check.json).

| Input | Kết quả parser |
|---|---|
| `whisper` | Chấp nhận |
| `male, elderly, low pitch, whisper` | Chấp nhận |
| `scared` | ValueError: unsupported |
| `angry` | ValueError: unsupported |
| `sad` | ValueError: unsupported |
| `terrified but trying to remain calm` | ValueError: unsupported |

Đây là kiểm tra syntax/contract, không phải listening test. Chấp nhận `whisper` chưa chứng minh whisper tự nhiên hoặc giữ đúng speaker. Không sửa parser để nhận arbitrary text rồi coi model có khả năng emotion đã được huấn luyện.

## API chạy trên máy này

[API summary đã lưu](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-runtime/api-summary.json).

`/_clone_fn` có thứ tự tham số:

```text
text, lang, ref_aud, ref_text, instruct,
ns, gs, dn, sp, du, pp, po
```

`ns` inference steps; `gs` CFG; `dn` denoise; `sp` speed; `du` duration; `pp` preprocess; `po` postprocess. Hàm trả output audio và status. Reference audio cần được gửi theo cơ chế Gradio file; không giả là đường host tự tồn tại trong container.

`/_design_fn` nhận text/language/settings và các lựa chọn gender/age/pitch/style/accent/dialect. Không có reference speaker như clone. Chỉ một request với instruction chung có thể tạo nhiều take, nhưng giữ speaker identity xuyên các request là việc cần nghe/kiểm chứng; không coi tuổi/pitch là speaker ID.

Đề xuất khi triển khai sau: design/cast một giọng, duyệt một canonical reference rồi thử clone cho các câu tiếp theo. Cách này có căn cứ từ chức năng cloning, nhưng stability và đổi delivery cần thử. Không khẳng định đổi reference mood vẫn giữ người nếu chưa nghe.

## Biểu cảm, nhiều nhân vật và timing

| Nhu cầu horror | Khả năng / giới hạn đã thấy | Cần kiểm chứng tiếp |
|---|---|---|
| Narrator ổn định | Clone từ reference + transcript | Identity, phát âm, nhịp và consistency qua passage |
| Nhiều nhân vật | Có thể gọi riêng từng utterance với reference riêng | Cast phân biệt, giữ identity, hợp vai; chưa có track multi-speaker của V4 |
| Thì thầm | `whisper` hợp lệ; runtime clone cũng nhận instruction | Whisper có thực sự hiệu quả cùng reference, intelligibility và giữ timbre |
| Thở dài/cười/âm phản ứng | README có `[sigh]`, `[laughter]`, `[surprise-ah]`, `[surprise-oh]`, các tag khác | Audio thực có tag đúng vị trí, không đọc tag thành chữ; không coi tag là emotion của cả câu |
| Sợ/giận/buồn/panic | Không có thuộc tính instruction tương ứng trong parser hiện tại | Reference diễn xuất cùng speaker, text/prosody và take selection có thể giúp; đó là giả thuyết thử nghiệm, chưa capability đã chứng minh |
| Pace | `speed`; `duration` ưu tiên hơn speed | Không dùng fixed duration để ép cảnh; chọn take rồi đo thời lượng thật |
| Long form | Chunking và preprocess/postprocess được tài liệu hóa | Chỗ nối, silence, mood/identity continuity; không coi chunk duration là beat quota |
| Word/phoneme sync | API demo trả audio/status, không trả alignment theo từ/phoneme | Đo WAV và phương pháp alignment riêng; SRT không tự chứng minh lip-sync chính xác |

Tài liệu tham số: [Generation Parameters](https://github.com/k2-fsa/OmniVoice/blob/master/docs/generation-parameters.md). Bản local snapshot: [generation-parameters.md](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-runtime/generation-parameters.md).

Thời lượng take và timestamp phải theo audio sau preprocessing/postprocessing cuối cùng. SFX annotations không gửi vào lời đọc; non-verbal tags là một loại khác, cần phân biệt với cue môi trường. Diễn xuất “sợ nhưng cố trấn an” vẫn là direction cần lưu trong storyboard, dù provider không nhận nguyên câu direction đó.

## Tái sử dụng và khoảng thiếu của V4

[D:/hand-draw/voice_srt.py](D:/hand-draw/voice_srt.py) đã có Gradio cloning, reference Jameson, cache chunks và Whisper transcription. Lời gọi clone có 13 tham số, với Instruct hiện để `None`, khớp API runtime đang chạy. Nó không hiện thực thoại nhiều nhân vật theo mood. Có thể học cách kết nối/cache/hash, không chạy toàn bộ pipeline đó cho V4.

Skill horror-video-pipeline bắt buộc đọc workspace guide và stage audio: đã đọc đầy đủ AGENTS.md, PIPELINE_GUIDE.md và docs/pipeline/02-kokoro-voice-srt.md. Chỉ áp dụng phần khám phá provider/audio code. Quy tắc ba truyện, full-frame giấy cũ, stream-drawing, intro hoặc pinned voice cho project hand-draw không trở thành yêu cầu artwork/cast của V4.1. Lựa chọn 3D horror cartoon + Kage của người dùng vẫn giữ nguyên.

V4 hiện có speech contract am_michael và Kokoro receipts. Việc dùng OmniVoice cho production cần thay đổi provider routing và recording receipt/validator tương ứng qua route hiện có, giữ measured timing, cache identity, script/reference/instruction/take hashes và QA nghe. Không dùng custom runner hoặc bỏ validation để né ràng buộc. Bước nghiên cứu này chưa thay provider, schema hoặc AGENTS.

## Đã thực hiện / chưa thực hiện

- Đọc lại D:/manim/Code2Video/AGENTS.md và START_HERE.md; thực hiện nghiên cứu rồi dừng.
- horror-video-pipeline dùng để tìm hướng dẫn và kết nối OmniVoice có sẵn, không nhập architecture hand-draw vào V4.
- script-to-visual-director dùng phân biệt voice identity, intention/mood và sound relationship; technical/API acceptance không thay thế nghe diễn xuất.
- Thao tác: docker ps/inspect chọn thông tin cần thiết; GET metadata; đọc/snapshot source runtime; web đối chiếu nguồn chính thức; chạy parser riêng. Không đọc secrets hoặc đổi trạng thái service.
- Chưa synthesize hoặc nghe audio; chưa đo performance; chưa thử identity qua whisper; chưa kiểm tra reference chất lượng, tags, full multi-cast dialogue hoặc alignment. Kết quả không là audio PASS.

## Bước tiếp theo — đề xuất, chưa chạy

**Công việc:** thử ngắn trên OmniVoice runtime với cùng reference Jameson: cùng câu tiếng Anh theo clone neutral, clone + whisper và clone + `[sigh]`; có thể thêm take lặp để xem identity drift. Đây là phép thử delivery/reference, chưa là cast toàn phim hay chứng minh đủ mood sợ/giận/buồn.

**Rule/file:** START_HERE.md — chỉ bước audio mẫu được giao, trình và dừng; V4_AUTHORING_GUIDE.md — timing đo audio thật, không time-stretch, QA nghe độc lập. Dùng source runtime/API đã xác minh và tài liệu OmniVoice, không tự thay toàn bộ provider V4 trong bước test.

**Skill/reference:** horror-video-pipeline + stage 02/voice_srt.py để gọi đúng Gradio clone và lưu provenance; script-to-visual-director để giữ cùng intention/text và diễn giải khác biệt delivery; OmniVoice voice-design/generation-parameters để chọn instruction hợp lệ/settings. Renderer, Flow, motion/VFX skills không áp dụng vì chỉ thử dry voice.

**Thao tác dự kiến:** Gradio `/_clone_fn` với reference/transcript có sẵn, synthesize các take ngắn; ffprobe đo WAV, lưu request/hash/receipt, trình audio cho người dùng nghe duyệt. Không dùng lệnh production V4 hiện tại vì route đó chưa hỗ trợ OmniVoice; đây là capability experiment riêng, không phải runner production mới.

**Đầu vào:** Jameson reference/transcript hiện có; câu thử đề xuất “Keep your voice down. There is someone outside the door.”; instruction `None`/`whisper` và tag `[sigh]`. **Đầu ra:** WAV mẫu và bảng so sánh/measurement trong D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-voice-trial. **Điểm dừng:** trình mẫu, phần đã nghe/chưa nghe và khả năng còn thiếu; chưa sửa repo, nâng cấp rule hoặc dựng phim.
