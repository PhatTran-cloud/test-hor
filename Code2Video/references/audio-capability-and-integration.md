# V4.1 horror — thiết kế voice, SFX và lịch chạy tuần tự

Ngày 11/10/2026. Đây là kết quả bước nghiên cứu/audit theo yêu cầu người dùng, **chưa triển khai provider, chưa cài/tải weights Small-SFX, chưa synthesize, chưa nghe, chưa render**. Người dùng đã xác định lịch chạy: xong voice thì tắt voice, sau đó mở model SFX. Lịch đó được đưa vào thiết kế; chưa thực hiện thao tác dịch vụ ở bước này.

## Kết luận đề xuất

**Dùng OmniVoice cho lời kể/thoại; Stable Audio 3 Small-SFX là ứng viên gen từng asset âm thanh; Freesound là nguồn recording để đối chiếu và chọn khi phù hợp.** Chọn bằng chất lượng nghe và quan hệ với hành động, không chọn chỉ vì asset được AI gen hay là recording thật. Chưa chứng minh Small-SFX đủ chất lượng trên máy này.

Small-SFX tạo nguồn âm. Đạo diễn và code vẫn quyết định tiếng nào xảy ra, nguyên nhân, lúc nào phát, vị trí, cường độ, khoảng cách, môi trường và tiết lộ gì. Không giao cả soundtrack/shot nhiều sự kiện cho một prompt rồi mong các tiếng rơi đúng frame.

Giữ hướng artwork đã chọn: **3D horror cartoon + nguyên tắc chiều sâu Kage**, asset/pose/layer Flow và motion/VFX được author riêng. Audio không thay đổi route hình. Đây chưa phải nâng cấp rule/schema đã được áp dụng; production hiện tại vẫn V4/schema 4/`local_tools/production.py`.

## Rule và skill thực sự áp dụng trong bước này

- [AGENTS.md](D:/manim/Code2Video/AGENTS.md) và [START_HERE.md](D:/manim/Code2Video/START_HERE.md): chỉ bước được giao rồi báo cáo/dừng; research trong outputs; measured speech; sound gắn event, giữ nguồn/license/hash; kỹ thuật khác listening review; không sửa repo hay chạy bước sau.
- [script-to-visual-director](C:/Users/thebl/.codex/skills/script-to-visual-director/SKILL.md) + [visual-reasoning.md](C:/Users/thebl/.codex/skills/script-to-visual-director/references/visual-reasoning.md): áp dụng intention/mood/reveal, continuity, sound relationship vào brief voice/SFX dưới đây; không tuyên bố đã dựng storyboard toàn phim.
- [cinematic-motion-director](C:/Users/thebl/.codex/skills/cinematic-motion-director/SKILL.md) + [object-motion-physics.md](C:/Users/thebl/.codex/skills/cinematic-motion-director/references/object-motion-physics.md) + [scene-motion-orchestration.md](C:/Users/thebl/.codex/skills/cinematic-motion-director/references/scene-motion-orchestration.md): truy nguyên contact/force/material và phản ứng môi trường để quyết định trigger, onset và decay của âm. Chưa author animation.
- Không áp dụng skill install/render hoặc `production.py` trong bước này: chỉ đọc source, tài liệu chính thức, query metadata và biên tập thiết kế. Không có skill chuyên sound directing/Small-SFX trong route đã đọc; không coi hai skill motion/visual là bằng chứng đã hoàn tất chuyên môn audio.

## 1. Những gì đã kiểm chứng

| Thành phần | Kết quả thực tế | Giới hạn bằng chứng |
|---|---|---|
| OmniVoice Docker | `omnivoice-demo`, localhost:8001, API/source runtime có clone + instruct | Chưa chạy synthesis/listening; tên image latest không chứng minh checkpoint revision |
| Instruction runtime | Parser nhận `whisper`; từ chối `scared`, `angry`, `sad`, câu diễn xuất tự do | Syntax hợp lệ không chứng minh diễn xuất hay giữ identity |
| Freesound | Key cấu hình dùng được; 3 search trả metadata/license/preview | Chưa tải, nghe, chọn hoặc duyệt asset |
| Small-SFX | Model và repo chính thức tồn tại, API text-to-audio/duration/seed được tài liệu hóa | Chưa cài, chưa xác minh quyền tải weights, chưa chạy trên máy |
| GPU | RTX 3050 8GB; tại lần kiểm tra ~5104MiB đang dùng, OmniVoice đang chạy | Không suy ra Small-SFX sẽ vừa VRAM hoặc đạt latency quảng cáo |
| V4 mixer | Có gain, static pan, fades, asset offset, loop, ducking | Không có acoustic automation đầy đủ; không phải mix horror đã được duyệt |

Bằng chứng đã lưu: [OmniVoice runtime/parser/API](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-capability-study.md), [Freesound metadata](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/freesound-capability-evidence.json). API key không được ghi vào báo cáo/output.

Source upstream đọc trong audit: OmniVoice commit `08be0b4ccbac3e13e374e86fbfead4b4cac343e2`; Stable Audio 3 commit `77e0398c26f7d22d801ec1bb036307e8b231f741`. Bản runtime OmniVoice khác working copy local/upstream; thiết kế adapter phải theo API runtime và pin phiên bản, không mặc định source clone vừa đọc là code Docker đang chạy.

## 2. OmniVoice: mood cần thiết kế thành diễn xuất và thử thật

Nguồn: [repo](https://github.com/k2-fsa/OmniVoice), [voice design](https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md), [tips](https://github.com/k2-fsa/OmniVoice/blob/master/docs/tips.md), [generation parameters](https://github.com/k2-fsa/OmniVoice/blob/master/docs/generation-parameters.md).

Mỗi người kể/nhân vật có **speaker_id riêng**, identity/reference được duyệt. Không dùng cùng một giọng cho toàn bộ cast. Không tự chọn reference Jameson làm narrator chỉ vì file đã có.

Tách hai trường:

- **Acting direction cho người duyệt:** nhân vật muốn gì, nói với ai, biết điều gì, sợ ở mức nào, đang kìm nén hay mất kiểm soát, tốc độ/pause/breath mong muốn, câu nào là reveal.
- **Payload thật cho model:** text, language, reference audio + transcript, các thuộc tính instruct được runtime chấp nhận, settings. Không gửi `terrified`, `angry` hay văn xuôi diễn xuất vào parser hiện tại rồi ghi là hỗ trợ emotion.

OmniVoice docs nói reference thường thắng nếu reference style mâu thuẫn instruct. Vì vậy neutral reference + `whisper` chỉ là một thử nghiệm, không bảo đảm đổi delivery. Với mood ngoài whitelist, cần thử reference có diễn xuất phù hợp của **cùng speaker**, kiểm tra cả identity lẫn mood; hoặc chọn provider khác sau khi có bằng chứng. Không sửa whitelist rồi coi model đã học cảm xúc.

Reference chính thức khuyên khoảng 3–10s và transcript chính xác; cùng ngôn ngữ giúp tránh lệch accent. Câu thoại 1–2s ưu tiên clone vì docs cảnh báo generation không reference có thể thiếu ổn định. Nonverbal tags như sigh/laughter là khả năng cần audition, không thay toàn bộ diễn xuất.

**Một utterance/take** giữ: speaker_id, utterance_id, nguyên text, role narrator/dialogue, acting brief, runtime instruction đã gửi, ref path/hash/transcript, model/runtime identity, settings, output WAV/hash và trạng thái nghe. Draft direction không phải receipt chứng minh model đã thực hiện.

Không nhét tên speaker/stage direction vào nội dung đọc. Ghi riêng. Chọn take trước rồi đo duration/Whisper/alignment và author timing; không kéo voice cho vừa slot. Pre/postprocess có thể cắt silence, nên phải đo file cuối cùng, giữ breath/pause có chủ đích theo kết quả nghe. Runtime Gradio chưa có seed control được xác nhận: frozen take là bằng chứng tái dựng, không hứa regeneration bit-identical.

Upstream mới có reusable VoiceClonePrompt và batch xử lý instruct/reference. Docker đang chạy không tự có mọi endpoint đó. Nếu batch, chia nhóm clone/non-clone tương thích API và giữ utterance IDs; không sắp thoại theo thứ tự task hoàn tất.

## 3. Small-SFX: phù hợp ở lớp tạo asset

Nguồn: [model card](https://huggingface.co/stabilityai/stable-audio-3-small-sfx), [repo](https://github.com/Stability-AI/stable-audio-3), [inference](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/workflows/inference.md), [prompt guide](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md).

Model `small-sfx` chuyên SFX, English prompting, stereo 44.1kHz, tối đa 120s. Python API có duration, steps, seed, batch; có audio-to-audio/inpainting/continuation. Default duration 120s nên phải đặt duration cho từng brief. Default 8 steps; tăng steps không được bảo đảm tăng chất lượng post-trained model.

**`negative_prompt` và `cfg_scale` không có tác dụng với post-trained `small-sfx` theo tài liệu Python.** Không thiết kế workflow dựa vào negative prompt để chắc chắn xóa giọng/music. Miêu tả nguồn/action/đặc tính rõ trong prompt chính, sau đó nghe để loại contamination.

Đề xuất gen một loại nguồn/action mỗi request: một knock, một hinge creak, một bước chân, một lớp mưa, một texture thực thể. Chuỗi bước chân/gõ theo nhiều beat được dựng từ các take phù hợp và onset đã đo; không yêu cầu model đặt chuỗi tiếp xúc đúng timestamp phim. Ambience bed có thể liên tục vì cùng một nguồn/điều kiện; cần kiểm tra diễn biến và điểm loop.

### Mẫu brief âm thanh — minh họa, chưa gửi model

| Asset | Cơ chế và mục đích | Prompt ứng viên | Handoff vào dựng |
|---|---|---|---|
| Wood knock | Khớp contact bàn tay–gỗ; force tiết chế, vật liệu đúng cửa | `TrackType: SFX. A single restrained knuckle knock on a heavy wooden door, a sharp contact followed by a short woody resonance, close microphone in a dry quiet room, isolated one-shot.` | Đánh dấu onset thật, chọn body/tail; đặt contact event |
| Wet gravel step | Đế giày nén/cọ sỏi ướt, không phải boot kim loại | `TrackType: SFX. One slow boot step pressing into wet gravel, compact crunch and a small damp squelch, close ground-level microphone, natural short decay, isolated footstep.` | Nghe tách heel/body/scuff; chọn đúng gait; giữ biến thể tự nhiên |
| Rain layer | Mưa tác động một bề mặt xác định; không chung một rain cho mái/lá/kính | `TrackType: SFX. Steady moderate rain striking a thin metal roof, irregular fine taps and low resonant patter, close recording beneath the roof, continuous even rainfall.` | Bed kiểm tra loop; biến đổi theo mái che/cửa và perspective |
| Entity texture | Âm ngoài tự nhiên do brief thực thể xác định; không mặc định mọi reveal là boom | Brief phải nghiên cứu identity/action trước; chưa chốt prompt | Duyệt âm đơn rồi audition trong mix; phân biệt expressive sound với literal sound |

Các prompt này chỉ minh họa cấu trúc source → action/force → decay → microphone/room. Đúng mô tả chưa chứng minh output đúng vật liệu, event count hay onset.

### Triển khai máy này: hai route, chưa chọn bằng benchmark

- Python/PyTorch GPU chính thức: môi trường riêng, batch 1 ban đầu, duration theo asset, đo peak VRAM/latency thật. Không sửa môi trường OmniVoice/V4; dependency torch/transformers/numpy mới có nguy cơ khác phiên bản.
- [TFLite CPU Windows](https://github.com/Stability-AI/stable-audio-3/blob/main/optimized/tflite/README.md): có route Windows x64, không cần chiếm GPU. Tuy nhiên README vừa mô tả short rungs vừa khuyên clip ≥~20s cho coherence; còn các đoạn default precision không nhất quán. Phải pin source và kiểm tra code/runtime, không hứa đây là route tối ưu cho one-shot 0.5s. Không kéo impact ngắn thành 20s chỉ để né vấn đề; nếu gen clip dài để extract phải kiểm tra vẫn đúng event/decay.

Model card chính có gated access/license/Gemma conditions; exact terms/checkpoint access chưa kiểm chứng trên tài khoản máy. License code không đồng nghĩa license weights. Chưa chấp nhận terms hoặc tải weights. Xem [nguồn license chính thức](https://stability.ai/license) khi chuẩn bị route; không đưa kết luận pháp lý vào quality proof.

## 4. Freesound: vẫn hữu ích, đã kiểm tra API

[API overview](https://freesound.org/docs/api/overview.html), [resources](https://freesound.org/docs/api/resources_apiv2.html), [authentication](https://freesound.org/docs/api/authentication.html).

Đã query ba nhóm `rain metal roof` (194 kết quả), `wood door knock` (528), `footsteps wet gravel` (30). Ví dụ candidate CC0: rain [673284](https://freesound.org/s/673284/), knock [629986](https://freesound.org/s/629986/), footsteps [531570](https://freesound.org/s/531570/). **Tất cả UNSELECTED/UNVERIFIED listening.** Metadata/keyword không chứng minh đúng môi trường hoặc âm sạch.

Key hiện có đủ search/metadata/preview; original-file download API cần OAuth2 theo tài liệu. Không đòi người dùng cung cấp key mới. Khi production chọn asset: giữ license, creator, permalink, source file/preview, hash và attribution tương ứng. Repo hiện giới hạn commercially usable CC0/CC-BY; không tự tải NC rồi dùng.

Nguồn gen và recording cùng phải qua audition dry/in-context. Nếu Freesound đúng contact/material hơn model, dùng recording đó. Nếu không có recording phù hợp, Small-SFX là nguồn candidate có thể thử; không tự thay lỗi tải bằng beep/tone.

## 5. Hợp đồng sound design theo storyboard

Mỗi cue cần: shot/beat/event_id; source_object_id (có thể là object ngoài frame); action, force/contact/material; story purpose; diegetic/expressive; screen/world position và listener perspective; dry source/onset/tail; môi trường/occlusion; automation; liên hệ speech/reveal; provenance/selected take. Nhiều nhân vật chính và nhiều nguồn trong cùng shot là bình thường, cần hierarchy theo tình huống.

**Timing:** voice final → duration/anchors thật → beat/contact/reveal được author → onset thật của SFX → clip placement. Với onset tại giây `o` trong source và contact tại thời gian phim `t`, đặt clip sao cho sample onset chạm `t`; không coi đầu file là contact nếu có leading silence. Không thêm timestamp bịa ở bước research này.

**Vật lý và perspective:** pan theo vị trí tương đối với listener, attenuation theo khoảng cách được author, lọc/occlusion khi qua cửa/kính, reverb hợp không gian, wet/dry theo geometry. Camera zoom không tự đồng nghĩa listener tiến tới; phải định nghĩa cinematic listening perspective. Tail không bị cắt tùy tiện khi đổi shot. Gió/mưa thay đổi theo exposure; cloth/footstep/engine không phát chỉ vì object hiện trong frame.

**Horror hierarchy:** thoại là nguồn thông tin cần nghe; sound ngoài frame có thể báo trước reveal; silence/low ambience có chủ đích tạo chờ đợi; impact không cần phủ mọi cut. Không tự thêm BGM vì repo chỉ cho khi yêu cầu. Không mặc định mọi thoại whisper hoặc mọi thực thể có bass boom.

**Voice treatment:** narrator và dialogue tách bus/identity. Narrator có thể giữ dry/intelligible; dialogue chịu room/distance theo shot. Điều đó là đề xuất đạo diễn, cần duyệt theo cảnh. Giữ diễn xuất gốc trước khi FX; FX không sửa được câu đọc thiếu mood.

## 6. Những chỗ V4 cần đổi nếu sau này được giao triển khai

Đã đọc `src/kokoro_tts.py`, `src/v4_contract.py`, `local_tools/v4_pipeline.py`, `src/freesound.py`, `src/sfx_assets.py`, `src/sfx.py`, `local_tools/prepare_sfx.py` và cue validation trong `src/v3_contract.py`. Đây là thiết kế thay đổi, chưa patch những file đó.

1. **Voice provider contract:** hiện V4 ép Kokoro `am_michael`, chưa có per-utterance cast/mood. Cần adapter OmniVoice, voice segments/IDs và provider-specific measured receipt; giữ Kokoro/legacy behavior và `production.py` schema 4, không dựng runner bypass.
2. **SFX gen receipt:** WAV Small-SFX được chọn cần model/revision/runtime, prompt/duration/seed/settings, raw/derived path/hash, edit chain, license source và listening evidence. Runtime cue dùng frozen file; không gán giả là Freesound. `source=procedural` bị V4 cấm cho fallback; không dùng đổi tên để vượt contract. Cần định nghĩa provenance source generated rõ khi cập nhật contract.
3. **Audition/selection:** hiện helper có search-only candidates, và `resolve_query` có legacy first-result route. Horror không auto chọn kết quả đầu. Production cần explicit ID/file, provenance/license và listening review gắn hash.
4. **Mixer:** hiện gain/static pan/fades/offset/loop; duck dựa speech amplitude (>0.008) có thể bỏ sót whisper; peak normalization không phải true-peak/LUFS validation. Cần duck theo utterance occupancy/envelope hợp lý, bus priority, pan/distance/filter/reverb automation được author, kiểm tra clipping/độ rõ/tiếng quá lớn bằng cả đo và nghe.
5. **Continuity:** section mixer có nguy cơ reset ambience/tail tại cut. Thiết kế giữ film-level source cursor/tail hoặc author split có sample continuity được kiểm chứng. Không coi crossfade tự động là giải pháp cho mọi sound bridge.
6. **Triển khai tối thiểu có kiểm soát:** spatial/EQ/reverb có thể bake thành derived asset với edit chain/receipt trước, để hạn chế phạm vi đổi mixer; sound chuyển động liên tục vẫn cần route automation rõ. Đây là phương án cần duyệt, không coi là đã đủ toàn bộ horror sound design.

## 7. Lịch chạy tuần tự — theo yêu cầu mới của người dùng

1. Cast/brief utterances → OmniVoice generate các take → nghe/chọn → frozen raw và final WAV/receipts. Nếu phải sửa voice sau, đó là lượt voice riêng.
2. Đo/transcribe/alignment voice final bằng công cụ độc lập, author beat/event. TTS model không cần tiếp tục resident để đo WAV. Không giả Whisper đã chạy; tại audit chưa xác minh service Whisper.
3. Sau khi file/receipts hoàn tất: `docker stop omnivoice-demo`, kiểm tra container stopped và `nvidia-smi` để xác nhận VRAM được giải phóng. Không xóa container, weights hay audio. Chưa chạy lệnh này.
4. Load Small-SFX trong process/env riêng → gen từng asset theo briefs → unload/terminate model process sau batch để nhả VRAM. Nếu transcription cần GPU, cũng không chạy chồng thời điểm.
5. Audition Small-SFX/Freesound, chọn source, edit/onset/receipt → mix/QA theo một bước được giao sau. V4 renderer có thể tiếp tục dùng GPU khi SFX đã unload. Không dùng chế độ GPU resident song song.

Voice/SFX không phụ thuộc hai model sống cùng lúc: giao nhau bằng frozen WAV + manifest. Nếu cần pickup thoại: unload SFX → khởi động OmniVoice → lưu/đo take sửa → tắt voice → gen SFX bổ sung nếu cần. Không tự chạy pickup hay vòng lặp production ở bước research.

## 8. Trạng thái và bước tiếp theo

Đã làm: đọc repo/docs/source thực, đối chiếu runtime và V4, query Freesound metadata, kiểm tra hardware, viết thiết kế này. Technical API/metadata đã có bằng chứng; **quality/mood/SFX/listening/integration vẫn UNVERIFIED**. Chưa sửa Code2Video, chưa cài Small-SFX, chưa tải/nghe/generate audio, chưa đổi Docker lifecycle.

**Bước tiếp theo — đề xuất, chưa chạy:** chuẩn bị route Small-SFX riêng: kiểm tra access/checkpoint/terms, dependency và code Windows/GPU trước khi chọn môi trường. Rule: từng bước/dừng, source/hash/license, không bypass V4 từ AGENTS.md/START_HERE.md. `script-to-visual-director` dùng brief/reveal để chốt phạm vi thử; `cinematic-motion-director` dùng force/contact/material để chốt asset thử; docs inference/install chính thức là reference kỹ thuật cài model, không có skill cài Small-SFX phù hợp. Thao tác dự kiến: đọc installer/weights manifest, kiểm tra khả năng truy cập và tạo báo cáo preflight trong outputs; không chạy remote installer bằng pipe. Đầu vào: báo cáo này + nguồn pin + máy đang có OmniVoice. Đầu ra: route chuẩn bị cụ thể, access/dependency/VRAM/điểm chưa kiểm chứng để duyệt. Dừng sau preflight, trước tải/cài/gen, không tự nâng V4.1.
