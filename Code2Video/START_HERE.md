# V4.1 horror: one production route

Current film direction (13 October 2026): OverSimplified is the primary visual
reference, adapted to horror, AI art plus Remotion animation. Illustration exports
prompts only; the human user runs Flow. Prompt every generated object, including
backgrounds and props. Use uniform #00FF00 sources for objects requiring alpha;
local code keys them to PNG. See docs/OVERSIMPLIFIED_ILLUSTRATION.md. Storytelling
and usable action assets matter more than a rigid flat-fill drawing recipe.
Historical 3D/Kage directions are superseded for this film, without artwork PASS
or permission to render. Preserve the user's stepwise mode below.

Dedicated workspace: D:/manim-horror-v4.1. Original V4 is in D:/manim.
This folder is the user's authorized comprehensive horror upgrade. Keep schema 4
and local_tools/production.py; never use an old provider/legacy runner here.

## BẮT BUỘC: từng bước → báo cáo → dừng

Yêu cầu trực tiếp của người dùng ngày 10/10/2026. Chế độ này thay thế việc tự chạy
end-to-end trước đây. Áp dụng cả session mới, topic cũ và source ngoài repo.
Không tự làm bước sau, kể cả trong background. Chỉ tiếp tục khi người dùng ra lệnh.
Đây là yêu cầu về cách làm việc, không phải thêm bộ tiêu chí nghệ thuật tự đặt.

**Trước mỗi bước**, báo: “Bước N: sẽ làm ...; rule ... từ file ...; dùng skill ...
để làm ...”. Thực sự đọc và thực hiện chỉ dẫn đầy đủ liên quan, kể cả references
bắt buộc. Đọc tiếp phần bị truncate. Không ghi “đã dùng” khi chỉ đọc tên hoặc hash.

**Khai báo bắt buộc cho cả bước hiện tại và bước tiếp theo:**

- Công việc và phạm vi: làm gì, với đầu vào nào.
- Rule: yêu cầu cụ thể và đường dẫn file nguồn.
- Skill/reference: từng skill dùng để làm phần nào; đọc references bắt buộc ở
  bước đó. Không có skill phù hợp thì ghi “không áp dụng” và lý do.
- Lệnh/thao tác: lệnh repo dự kiến với đường dẫn đầu vào/đầu ra; nếu làm trực tiếp
  bằng nghiên cứu/biên tập/review thì nêu thao tác và công cụ, không bịa lệnh.
- Kết quả và điểm dừng: artifact nào sẽ được trình và việc nào chưa thực hiện.

**Mẫu cuối bước:** “Bước tiếp theo (đề xuất, chưa chạy): ...; rule từ ...;
skill ... để ...; lệnh/thao tác ...; đầu vào ...; đầu ra ...; dừng sau ...”.
Không chỉ viết “tiếp theo sẽ dựng/render”. Đề xuất không phải quyền thực hiện.
Tên từng skill và phần việc nó xử lý phải xuất hiện ngay trong đề xuất gửi
người dùng, không chỉ nằm trong file được link hoặc câu “dùng skill liên quan”.
Khi người dùng ra lệnh tiếp, khai báo lại bước đó trước khi làm. Im lặng, PASS
hoặc lời hứa của assistant không thay thế lệnh người dùng.

| Bước | Chỉ làm công việc này | Báo cáo rồi dừng |
|---|---|---|
| 1. Đọc và đối chiếu | Đọc yêu cầu, repo và toàn bộ skill/reference áp dụng; liệt kê yêu cầu chính xác và những quyết định còn cần trình | Rule/skill đã đọc, nguồn cụ thể, yêu cầu phải giữ, chỗ chưa rõ; chưa viết plan/source, chưa TTS/render |
| 2. Kịch bản và nghiên cứu | Dịch/biên tập theo yêu cầu, kiểm chứng kiến thức, ghi rõ sửa gì và vì sao | Bản kịch bản, nguồn, thay đổi; chưa tự quyết art cho cả phim |
| 3. Đạo diễn hình và storyboard | Thực hiện script-to-visual-director: luận điểm hình ảnh, metaphor/reveal, quan hệ nhân quả, object phụ/background, camera, handoff, B-roll; trình lựa chọn renderer/craft từng cảnh | Storyboard reviewable và ví dụ cụ thể; phân biệt đề xuất với yêu cầu đã có; chưa code artwork |
| 4. Lời đọc | Dùng OmniVoice cast đã chọn, đo audio/anchors, phân bổ timing theo kịch bản đã thống nhất | WAV, thời lượng và timing thực; chưa dựng toàn phim |
| 5. Artwork cảnh mẫu | Chỉ dựng chủ thể/môi trường cho cảnh khó đã chọn; thực hiện đủ skill vẽ/3D liên quan | Ảnh/cảnh mẫu và cách áp dụng skill, vật liệu/ánh sáng/chiều sâu; chưa nhân rộng |
| 6. Motion/VFX/âm thanh cảnh mẫu | Thực hiện storyboard-motion-executor, motion/VFX skills và sound theo yêu cầu cho chính cảnh mẫu; render 1080p60 | Clip thực, hành vi/camera/nhân quả/transition, sound đã chọn và phần chưa nghe; chưa full render |
| 7. Review cảnh mẫu | Đối chiếu clip với yêu cầu người dùng và chỉ dẫn repo/skill, không tự hạ chuẩn | Từng yêu cầu có/thiếu ở đâu, bằng chứng, lỗi và cách sửa; chưa tự PASS rồi triển khai |
| 8. Triển khai toàn phim | Chỉ sau lệnh tiếp rõ ràng của người dùng: triển khai hướng đã thống nhất và render toàn phim | Video và lỗi còn lại; chưa tự tuyên bố giao đạt |
| 9. Review toàn phim | Kiểm tra hình/chuyển động/science/timing/âm thanh trên output thật | Kết quả có bằng chứng; sửa chữa là bước riêng theo lệnh tiếp |
| 10. Bản giao | Sau lệnh người dùng: chuẩn bị bản giao theo kết quả review | File final và trạng thái thực; dừng |

**Báo cáo cuối mỗi bước phải có:**

1. Đã làm gì (hành động thật, không viết lại kế hoạch như kết quả).
2. Rule nào từ file nào; skill nào và đã áp dụng cụ thể vào phần nào.
3. Kết quả để xem: link script/storyboard/source/ảnh/clip/audio thích hợp.
4. Yêu cầu còn thiếu, chưa kiểm chứng, lỗi hoặc khác biệt với chỉ dẫn.
5. Bước tiếp theo theo mẫu khai báo ở trên: công việc, rule/file nguồn,
   skill/reference và mục đích, lệnh/thao tác, đầu vào/đầu ra, điểm dừng.
   Ghi rõ **đề xuất, chưa chạy**. **Dừng chờ lệnh**, không tự chuyển bước.

Không tạo acceptance dễ hơn để hợp thức hóa output. Truy vết tiêu chuẩn về
yêu cầu người dùng/repo/skill; tiêu chí bổ sung chỉ là đề xuất. Nếu rule không rõ
hoặc mâu thuẫn, trình cụ thể ở bước hiện tại. Nếu không đủ công cụ/thời gian,
báo hạn chế; không âm thầm đổi sang vector sơ sài, placeholder hoặc bỏ motion/VFX.
Không sao chép cùng một câu vào expected và observed rồi dùng nó như bằng chứng.
Không cần hỏi lại những lựa chọn đã được người dùng quyết định.

Các lệnh kỹ thuật dưới đây là công cụ cho bước được giao, KHÔNG phải quyền chạy
một mạch toàn bộ bảng. Trong phiên đã chạy, yêu cầu session đọc lại phần này
trước khi tiếp tục; sửa file không tự cập nhật context đang hoạt động.


## Current horror route

Before artwork, complete the character and setting brief in
docs/HORROR_CONTRACT.md inside the same production packet: script evidence,
character relationships/visible ages/appearance/costume, location and era,
consistent architecture/technology/props, approved style and remaining questions.
Ask the user when a missing or conflicting detail affects design. Do not infer
an exact age from a voice-library label or a decade from a village funeral.
Keep proposals distinct from user decisions and preserve choices already made.

Characters will animate: plan reusable action poses and required camera views as
sprite sequences before requesting production assets. Standing references alone
are not complete animation assets. Character cutouts require actual alpha PNG;
props and backgrounds need PNG only if transparency is required. Check the actual
image against the dark horror cartoon style and the character/world brief.

Read docs/HORROR_CONTRACT.md for fields and docs/V4_AUTHORING_GUIDE.md for inherited
semantic planning, continuity, runtime observations and QA. Follow the user's
current style/reference decision. Illustration exports individual part/pose/prop/
background prompts for the human to run in Flow. Authored code owns acting,
environment/VFX and camera. Shared scene layouts support multiple shots. Use the
complete lowbudget3d + 3dviz-pro-max route only for actual spatial 3D.

Each film requires user-selected language en/vi, one main narrator without any
instruction and stable dialogue cast. OmniVoice only. SFX is generated Small-SFX
only, each with explicit generation seconds, audible duration, event onset and tail.
Freesound and Kokoro are removed from this production route. Voice and SFX run
sequentially on GPU, save results, unload, verify VRAM release; render later.

Read project skills ../.agents/skills/horror-asset-director and horror-audio-director
for these bridges alongside visual/motion/VFX director skills. Skill routes, hashes
and source symbols never prove art, acting or sound quality.

## Commands (only for the human-authorized stage)

Run from D:/manim-horror-v4.1/Code2Video with .venv/Scripts/python.exe.

| Stage | Command | Result / stop |
|---|---|---|
| Inventory | local_tools/production.py doctor --check-weights | Read-only provider/reference/model inventory; no start |
| Reference sampling | local_tools/production.py reference-study examples/reference-windows.json --output ../outputs/reference-study | Local 180s windows, 1 image/second, PTS/hashes/sheets/blank annotations; no visual approval; docs/REFERENCE_STUDY.md |
| Storyboard structure | local_tools/production.py storyboard-audit draft.json --output ../outputs/storyboard-audit.json | Opt-in scene-shot/1 staging/knowledge/carry audit; no pixel/art/audio approval; docs/SCENE_SHOT_GRAMMAR.md |
| Direction/check | local_tools/production.py context draft.json --output context.md; check draft.json | One packet with script/cast/behavior/beat/shot intent; no synthesis |
| Cast audition | local_tools/production.py voice-design request.json --output AUDITION_DIR | Designed dialogue WAVs and request/runtime/GPU receipts; listening and transcript remain UNVERIFIED; stop before selection/cloning |
| Reference ASR | local_tools/production.py reference-asr manifest.json --model LOCAL_MODEL --python CUDA_PYTHON | Scoped reference ASR with word timestamps; drafts require review; GPU released; no synthesis |
| Voice | local_tools/production.py prepare draft.json | Measured multi-speaker WAV/timed_plan/receipts; voice stopped; audition separately |
| Illustration | local_tools/production.py asset-brief timed_plan.json --output prompts.json | JSON + copyable Markdown; coverage for every generated part/pose/prop/background; human runs Flow; no automatic submission |
| Alpha cleanup | local_tools/production.py chroma-key source.jpg --output cutout.png | Preserved source, real alpha PNG, mask and hashed receipt; edge review still UNVERIFIED |
| Supplied sprite test | local_tools/production.py sprite-preview sprite_spec.json --output sprite_test.mp4 | Isolated 1080p60 alpha/pose/root test; hashed frames; no film, representative approval or release |
| Historical Flow status | local_tools/production.py flow-status timed_plan.json --output status.json | Legacy read-only diagnostics only; extension not required for prompt export; flow-submit is disabled |
| Artwork review | local_tools/production.py sheet plan.json --asset ID --view ID --output sheet.png | Registered returned poses/alpha; actual visual review; not acting proof |
| SFX | local_tools/production.py sfx timed_plan.json | Variable-duration generated cues/sfx_plan; GPU unloaded, listening UNVERIFIED |
| Author/check | local_tools/production.py check authored.json | Measured timing, current takes/assets/reviews, registered sprite/contact/view binding |
| Representative | local_tools/production.py preview authored.json | 1080p60 selected shot, film-clock mix/carry, hashed observations; stop for independent review |
| Production | local_tools/production.py render authored.json | Only after specific instruction and current representative review; no auto-release |
| Review/release | local_tools/production.py review RUN review.json; release RUN | Separate evidence-backed quality gates; previews/fixtures never releases |

Use one production_packet, no duplicate document forest. Counts and renderer choices
come from content, no fixed shot/pose/beat quotas. No burned subtitles or decorative
HUD. Sound may be silent; BGM only if explicitly requested. All preview/delivery
1920×1080 at 60fps. Timing is measured, speech never stretched to a predetermined slot.
Outputs live in ../outputs. CODE2VIDEO_OUTPUT_ROOT or --output-root is an explicit
override. Model exports in ../models, selected voice references in ../voice_library,
provider/host configuration in ../config.json. Do not copy credentials into source.

Do one step, report actual actions/skill decisions/artifacts/unverified work and a
fully declared proposed next step, then stop. An audit/test PASS is not art/audio PASS.
