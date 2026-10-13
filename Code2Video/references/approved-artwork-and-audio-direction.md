# V4.1 horror — hướng artwork đã chọn và yêu cầu audio

Nghiên cứu provider/SFX tiếp theo: [thiết kế OmniVoice + Small-SFX + Freesound](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/audio-capability-and-integration.md), gồm lịch voice → tắt voice → mở SFX theo yêu cầu người dùng. Đây là thiết kế, chưa đổi provider production hoặc triển khai sound mix.

Ngày 11/10/2026. Quyết định trực tiếp của người dùng: chọn **3D horror cartoon**, đưa vào prompt asset và **không bỏ Kage**. Sound design là phần quan trọng của sản phẩm; có voice dẫn chuyện và voice nhân vật, thoại phải diễn theo mood.

Trạng thái: hướng artwork và yêu cầu audio đã được người dùng xác định; prompt bên dưới đã biên tập nhưng chưa gửi Flow. Chưa có mẫu nghe, chưa kiểm chứng khả năng TTS diễn xuất. Đây là tài liệu định hướng trong outputs, không phải nâng cấp schema/runner hay rule production đã triển khai. Cập nhật nghiên cứu provider theo yêu cầu mới: [OmniVoice Docker và giới hạn instruction](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/omnivoice-capability-study.md); chưa chuyển provider production.

## Artwork: phạm vi lựa chọn

Ảnh người dùng chọn làm hướng cảm giác: [ảnh 1](C:/Users/thebl/AppData/Local/Temp/codex-clipboard-d1ae4cd5-5529-495d-9687-98ef0910bb41.png). [Ảnh 2](C:/Users/thebl/AppData/Local/Temp/codex-clipboard-3f6d60be-c475-4b75-a03a-d1f40ee22a24.png) là đối chiếu truyện tranh trên giấy, không phải hướng chính. Các liên kết Temp có thể mất sau khi hệ thống dọn file.

Chọn ngôn ngữ tạo hình có khối, mặt/pose cách điệu, vật liệu phân biệt và ánh sáng có chiều sâu. Không tự chốt toàn bộ cast từ tài xế của ảnh 1: mặt xác sống không phù hợp cho mọi nhân vật đang sợ hãi. Người sống, thực thể và vật thể phải có identity đúng vai; nhiều nhân vật chính có thể ở cùng shot hoặc xuyên nhiều shot.

Ảnh Flow mang diện mạo 3D không tự trở thành mesh có thể orbit. Asset 2.5D do Flow gen; code dựng các object/layer, pose, camera và VFX. Shot cần không gian/occlusion/lighting mà cutout không đáp ứng vẫn giữ route 3D đầy đủ của V4.

## Prompt asset dùng với Flow — tiếng Anh

Đây là block dùng chung để ghép với brief từng asset. Các trường trong ngoặc vuông phải được điền từ storyboard/behavior đã nghiên cứu; không gửi nguyên template còn placeholder.

```text
Create a reusable animation asset in the approved STYLIZED 3D HORROR CARTOON
illustration direction. Use convincing sculpted volume, expressive but controlled
character stylization, readable silhouettes, and coherent material rendering.
Keep the character, props, and environment within the same degree of stylization.
Use the supplied approved image as a reference for volume, material richness and
cinematic depth, not as a mandatory character identity or scene to reproduce.

ASSET ID / TYPE: [canonical ID; character pose, prop, object part, or environment layer]
IDENTITY: [fixed face landmarks, proportions, hair, costume, colors, asymmetry;
living/supernatural status only as specified by the story]
BEAT / STATE: [story intention and visible state change]
POSE / ACTION PHASE: [researched preparation, action, reaction, or settle state]
EXPRESSION / GAZE: [specific mood, facial action, gaze target and head direction]
VIEW: [camera-required facing, elevation, perspective/lens consistency and framing]
PHYSICAL SUPPORT: [weight-bearing foot/seat/hand contact; grip; attached prop;
required pivot region and hidden-part coverage]
MATERIALS: [specific skin, hair, cloth, metal, wood, glass or other materials;
wear/wetness only when justified; keep texture scale consistent]
LIGHTING: [agreed key direction, softness, fill, rim and color temperature;
compatible with the shot lighting plan and the other assets]
OUTPUT: [one specified pose/view or one specified separable layer per output;
canvas/crop padding; transparent alpha when supported, otherwise a uniform
separation background chosen to avoid colors in the subject]

Preserve the Kage-informed depth plan: the asset must fit its authored
foreground/midground/background role, perspective, occlusion and lighting.
For an isolated character or prop, show clear local form and material without
baking an entire scene, foreground fog, falling rain or another moving object
into its cutout. For an environment layer, preserve the requested depth band,
camera coverage and occlusion role; do not include unrelated depth layers.
Use warm/cool separation, restrained glow and atmospheric depth only where the
specified scene lighting and layer role call for them. Leave parallax, camera
movement and evolving VFX to the authored composition.

Keep identity, costume, proportions, material scale and perspective consistent
with the approved canonical reference and related poses. Deliver the requested
asset rather than a finished flattened shot or a multi-panel illustration.
Do not replace this direction with ink-comic linework, aged-paper borders or
pencil hatching. Do not make every surface glossy plastic, every person a corpse,
or use exaggerated cute mascot proportions unless the character brief calls
for them. No baked captions, decorative HUD, watermark, unrelated props or
cropped extremities. Do not fabricate a new identity when changing pose/view.
```

### Kage phải hiện diện trong cả brief và dựng cảnh

Nguồn: [KAGE_VISUAL_REFERENCE.md](D:/manim/Code2Video/docs/KAGE_VISUAL_REFERENCE.md).

- Chia FG/MG/BG theo chức năng kể chuyện; từng asset có depth/occlusion role và camera coverage. Không chỉ thêm chữ “Kage style”.
- Giữ continuity về world, camera, hướng sáng và vật liệu; ánh sáng phân tách focus, haze/bloom có mục đích. Không mặc định mọi cảnh phải đêm, mưa hoặc xanh lạnh.
- Perspective giữa asset, contact và lớp môi trường phải khớp. Các phần moving/optical cần tách hoặc có strategy runtime; highlight vẽ sẵn không chứng minh phản chiếu đúng khi camera đi.
- Một asset đẹp không thay thế cho acting, physical contact hoặc chiều sâu thật. Không copy code/art Kage; không nhập UI, chữ Nhật hay bố cục Kyoto làm yêu cầu.

## Sound design: đạo diễn cùng beat, không thêm cuối cùng

Đây là yêu cầu người dùng bổ sung, kết hợp rule event-driven sound của V4. Sound storyboard phải được tính từ ý định câu chuyện và hành động. Timing chỉ là provisional trước khi có speech đã đo.

| Lớp âm | Chức năng và điều phải xác định |
|---|---|
| Narrator | Voice identity ổn định, kể rõ, kiểm soát tension theo passage; không đọc toàn bộ phim như cùng một trạng thái sợ |
| Character dialogue | Speaker identity riêng, intention, người nghe, mood/energy chuyển theo câu, vị trí trong không gian; nhiều nhân vật chính được hỗ trợ |
| Foley / vật thể | Contact, vật liệu, khối lượng, lực, nhịp và aftermath khớp hành động; không ghép sound chỉ vì có keyword |
| Ambience | Không gian trong/ngoài, khoảng cách và thời tiết; continuity qua cut và phản ứng khi đổi acoustic space |
| Offscreen / reveal | Âm có thể báo nguồn chưa thấy hoặc dẫn sự chú ý; ghi rõ nguồn, khoảng cách, nguyên nhân và mục đích |
| Designed horror cue | Căng thẳng, sai lệch chủ quan hoặc supernatural có chủ đích; phân biệt với âm vật lý, không phủ stinger lên mọi beat |
| Silence / reduction | Giảm một số lớp để nghe chi tiết, giữ breath/room tone nếu cần; không mặc định mute sạch mọi thứ |
| Music / underscore | Chưa chọn nhạc hoặc asset. Rule hiện yêu cầu BGM từ brief rõ ràng; yêu cầu sound design không tự quyết một music bed cụ thể |

Ví dụ diễn giải vật lý, chưa là shot/storyboard được duyệt: ở ngoài xe, mưa/đường/động cơ khác khi camera vào cabin; trong cabin có thể nghe mưa trên mái, wiper hoặc rattle khi các vật đó thực sự hoạt động. Tiếng gõ cần xác định gõ vào kính/gỗ/kim loại, lực và người nghe ở đâu. Ánh chớp nhìn thấy trước tiếng sấm xa; không mặc định fog hay ánh sáng có tiếng. Không ép mọi object phải phát âm.

Mỗi cue cần cause/event/source, trigger và offset, purpose, vật liệu/contact, perspective/khoảng cách/occlusion, onset–sustain–decay/aftermath, carry qua shot hoặc kết thúc, file nguồn/licence/hash, gain/pan/fade/ducking và listening review. Pan không đơn giản bám tọa độ màn hình nếu acoustic perspective không phù hợp. Voice rõ; cue gây bất ngờ vẫn phải phục vụ reveal, không dùng mức âm lớn thay cho đạo diễn.

Theo [V4_AUTHORING_GUIDE — Event-driven sound](D:/manim/Code2Video/docs/V4_AUTHORING_GUIDE.md), asset phải nghe/chọn thật, freeze provenance/licence/hash; không thay sound thiếu bằng tone tổng hợp chung chung. Meter hoặc file tồn tại không chứng minh nghe đạt. Review asset đơn và review final mix là hai việc khác nhau.

## Voice casting và diễn xuất theo mood

Voice narrator và thoại không nhập thành một loại lời đọc. Mỗi nhân vật có canonical speaker/voice identity; hai người có thể cùng mood nhưng vẫn khác giọng. Một người thay đổi mood vẫn phải giữ identity.

Mỗi utterance cần speaker ID, text, addressee/intention, mood đầu–cuối, subtext, delivery (nhịp, nhấn, hơi, intensity), interaction/reaction/overlap nếu có, vị trí/acoustic context, pronunciation và take được chọn. Ví dụ “sợ nhưng cố trấn an người khác” khác “hoảng loạn gọi cứu”; chỉ ghi “scared” chưa đủ. Không mặc định whisper cho mọi horror hoặc đổi pitch để giả mọi tuổi/giới.

Đề xuất workflow cho bước audio sau này, chưa thực hiện:

1. Cast giọng bằng mẫu nghe; narrator giữ default am_michael theo V4 cho tới khi có thay đổi được chỉ định. Nhân vật cần giọng phù hợp và identity riêng.
2. Thử các take của cùng câu theo intention/mood, nghe và chọn; lưu dry voice riêng trước ambience/reverb. Yêu cầu cảm xúc không được coi là đã thực hiện chỉ vì prompt chứa mood.
3. Đo take thực sau khi chọn. Timing thoại, reaction, mouth pose và beat follow audio thật; không dựng timestamp tưởng tượng hay time-stretch để lấp slot.
4. Mix narrator/dialogue/foley/ambience/cue theo priority của beat. Voice có thể nhường khoảng cho reveal được đạo diễn; không để effects che thoại vô tình.
5. Nghe continuity danh tính, phát âm, diễn xuất và final mix; tách QA kỹ thuật khỏi QA nghe.

## Khoảng thiếu trong V4 hiện tại — đã kiểm tra code, chưa sửa

- [src/kokoro_tts.py](D:/manim/Code2Video/src/kokoro_tts.py:24) gửi model/input/voice/format/speed; không có emotion instruction trong payload này.
- [Vòng tạo speech từng segment](D:/manim/Code2Video/src/kokoro_tts.py:80) dùng cùng `voice`/`speed` truyền vào. `delivery_requested` được ghi lại, không điều khiển acting. File còn ghi plain Kokoro, whisper/acting not guaranteed.
- [src/v4_contract.py](D:/manim/Code2Video/src/v4_contract.py:154) kiểm tra speech voice `am_michael` và speed của plan; [local_tools/v4_pipeline.py](D:/manim/Code2Video/local_tools/v4_pipeline.py:152) giữ voice narrator đó.

Vì vậy yêu cầu multi-character mood dialogue **chưa có hỗ trợ đầy đủ trong route hiện tại**. Lựa chọn artwork đã chốt không làm khoảng thiếu này biến mất. Chưa chọn provider thay thế, chưa thử năng lực dịch vụ đang chạy, chưa build skill audio hay sửa validator/mixer. Muốn nâng cấp phải thiết kế cách track speaker/take/timing/receipt và review qua route V4; không đi vòng bằng custom runner hoặc đánh dấu technical_fixture.

## Rule/skill thực sự áp dụng trong bước này

- Đọc lại đầy đủ AGENTS.md, START_HERE.md và V4_AUTHORING_GUIDE.md: chỉ biên tập bước hiện tại, output trong D:/manim/outputs, không production/TTS/render hay sửa repo; giữ measured timing và QA nghe độc lập.
- script-to-visual-director + visual-reasoning.md: prompt tách identity/craft/layer/story state; sound relationship được đưa vào direction thay vì trang trí cuối cùng.
- cinematic-motion-director + object-motion-physics.md: action/contact/material làm đầu vào SFX và pose; secondary response có cause. Không tuyên bố đã nghiên cứu hành vi của một shot cụ thể trong bước này.
- cinematic-video-prompt-skill refs 03/05/06: composition/depth, style/mood và vật liệu/pose được diễn đạt thành trường cụ thể, không chỉ một chuỗi adjective.
- KAGE_VISUAL_REFERENCE.md: chiều sâu, optical continuity và purposeful FG/MG/BG được đưa vào prompt/brief, giữ quyền tác giả và route 3D.
- Đã kiểm tra media-use và remotion-best-practices để đối chiếu route: không dùng CLI HyperFrames/HeyGen hoặc renderer ở bước tài liệu này; chúng chưa là skill chuyên đạo diễn horror audio. Audio specification dùng rule V4 và phần sound relationship của visual-director. Không nhận đã sử dụng một skill mood-TTS chưa tồn tại.

## Bước tiếp theo — đề xuất, chưa chạy

**Công việc:** audit chi tiết voice/SFX route của V4 và nghiên cứu khả năng multi-speaker + mood acting; trình thiết kế nâng cấp audio/skill trước khi sửa code hoặc synthesize. Đây là phần thiếu cụ thể mới xác định, không yêu cầu đổi provider chỉ vì tên model.

**Rule/file:** AGENTS.md và START_HERE.md — từng bước, giữ V4 entrypoint, đo audio thật và QA nghe; V4_AUTHORING_GUIDE.md — event-driven sound, recording receipts và không giả alignment. Yêu cầu user mới về narrator/character/mood là nguồn quyết định ưu tiên.

**Skill/reference:** script-to-visual-director để thiết kế sound relationship/voice intention theo beat; cinematic-motion-director để audit causal SFX/contact; skill-creator để đánh giá phạm vi một horror-sound-and-voice-direction skill và đề xuất cấu trúc, chưa tạo/install; tài liệu provider chính thức cùng code V4 để đối chiếu điều khiển emotion/speaker/timing thật. Không dùng skill renderer vì chưa dựng cảnh.

**Thao tác dự kiến:** đọc code/schema/mixer và skill/reference áp dụng; tra tài liệu provider chính thức, biên tập bảng capability và thiết kế tích hợp. **Đầu vào:** yêu cầu audio trong tài liệu này, code V4 hiện tại. **Đầu ra:** audio-capability-and-integration.md trong thư mục nghiên cứu hiện có. **Điểm dừng:** trình khả năng đã xác minh, phần thiếu và đề xuất thay đổi; chưa sửa repo, tạo skill, TTS, chọn SFX hay render. Lệnh production không áp dụng vì đầu ra là audit/design.
