# Historical local setup and pilots

Not active new-production instructions. Read START_HERE.md for V4.

# Code2Video trên máy đại ca

# V4 active workflow

New productions use `schema_version: 4` and the current conversation's authoring
prompts in `prompts/v4.py`. Read `REPO40_PRODUCTION_CONTRACT.md` before continuing.
Draft -> `render_local.py --prepare-only` -> timed anchors -> authored source/shot
intervals -> render candidate -> independent review -> `v4_review.py --release-check`.
Do not confuse the unchanged original API/stage prompt path with this workflow.

Output mới nằm ở `D:/manim/outputs` (cùng cấp `Code2Video`). Topic sources, audio,
snapshot, render và QA đều đặt bên trong folder topic tại đây. Runner dùng
`src/output_paths.py`; có thể đổi bằng `CODE2VIDEO_OUTPUT_ROOT` hoặc
`render_local.py --output-root <path>`. Artifact cũ giữ ở đường dẫn lịch sử.

Legacy V3 remains available: read `REPO30_PRODUCTION_CONTRACT.md` for renderer routing,
authored mixed shots, lowbudget3d ownership, causal VFX and adaptive Freesound SFX.
The v1/v2 notes below describe historical setup and pilots; v3 rules supersede
their statements about missing browser adapters and procedural-only SFX.
Pre-v3 backup: branch `backup/code2video-v2-20261010`, tag `code2video-v2-20261010`.

```powershell
# V3 unit/contract/mix checks:
.venv/Scripts/python.exe -m unittest discover -s tests -v
# Three-route fixture, voice only:
.venv/Scripts/python.exe local_tools/render_local.py local_tools/v3_smoke/plan.json --no-tts
# Full Kokoro + selected Freesound + mixed renderer check:
.venv/Scripts/python.exe local_tools/v3_smoke/verify.py
```

Install the fixture browser dependencies with `npm ci` in `local_tools/v3_smoke/browser`.
The fixture is a technical example; successful export is not scientific/artistic
approval or proof of full lowbudget3d fidelity.

Repo: `D:\manim\Code2Video`, upstream commit `1142d8e`.
Môi trường đã cài: Python 3.12, `.venv`, Manim Community 0.19.0 theo requirements của repo,
FFmpeg/ffprobe và MiKTeX. `uv pip check` xác nhận 73 package tương thích.
Kokoro Docker đang dùng cổng `8880`, giọng tiếng Anh nam `am_michael`.

## Kết luận về nội dung

Code2Video phù hợp làm nền cho video giải thích khoa học theo lối sơ đồ có thể chỉnh sửa
bằng code. Với vũ trụ và địa lý, giá trị chính là diễn giải cơ chế bằng hình, nhãn,
công thức, biểu đồ và mô hình không gian; chất lượng còn phụ thuộc storyboard và code.

| Nội dung | Mức phù hợp và việc cần bổ sung |
|---|---|
| Quỹ đạo, lực hấp dẫn, trục nghiêng, nhật/nguyệt thực | Phù hợp với sơ đồ 2D/3D. Phải thống nhất hệ tọa độ, nguồn thông số và phân biệt minh họa với mô phỏng. |
| Sóng, trường, hình học, công thức vật lý | Rất hợp với khả năng biểu diễn toán học của Manim. |
| Cấu trúc Trái Đất, cơ chế kiến tạo, mặt cắt địa hình | Phù hợp với mô hình giải thích được dựng riêng và kiểm tra kiến thức. |
| Bản đồ thật, biên giới, độ cao địa hình | Cần dữ liệu địa lý, phép chiếu và nguồn dữ liệu có quyền sử dụng. Repo không tự cung cấp chúng. |
| Hành tinh có bề mặt chi tiết, khí quyển, hố đen thấu kính, cảnh điện ảnh | Cần thêm renderer/asset/shader chuyên biệt. Chưa có nhánh Three.js/Blender trong bản sửa này. |

Upstream dùng Planner → Coder → Critic và FFmpeg; Critic tập trung bố cục.
Danh sách benchmark local có 117 chủ đề lấy cảm hứng từ 3Blue1Brown, thiên về toán học.
Kết quả benchmark đó chưa chứng minh chất lượng cho kênh vũ trụ/địa lý của đại ca.
Repo gốc cũng chưa có bước kiểm chứng kiến thức, dữ liệu bản đồ hay narration Kokoro.

Nguồn: [repo và README](https://github.com/showlab/Code2Video),
[paper](https://arxiv.org/abs/2510.01174),
[tài liệu ThreeDScene](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html).
Tài liệu stable hiện có thể mới hơn bản 0.19.0 đã cài; code ở đây được thử trên 0.19.0.

## Đã sửa

- Sửa đường dẫn repo, import prompts, interpreter render và UTF-8 trên Windows.
- Worker đọc lại code trước khi render; mỗi section có media directory riêng để tránh tranh chấp file.
- Ghép theo thứ tự storyboard, dùng đường dẫn tuyệt đối, báo thất bại khi thiếu section.
- Thêm `scene_type: "3d"`, scaffold `Teaching3DScene`, camera và text cố định trong frame.
- Bỏ giới hạn cấm 3D trong prompt; ví dụ code và Critic có nhánh 3D riêng.
- Thay scaffold 2D/3D bằng bản chuẩn, không để định nghĩa 3D trùng ghi đè nhau.
- Text dùng Arial để chữ tiếng Việt hiển thị đúng.
- Thêm narration riêng với Kokoro, cache audio theo nội dung/voice và ghép audio vào từng section.
- Đọc thời lượng WAV bằng ffprobe vì header streaming của Kokoro có thể chứa độ dài sentinel.
- Khóa mọi lượt render ở **1920×1080, 60 fps**, kể cả smoke test và ghép narration; không nhận chất lượng thấp hơn.

## LLM là em trong chat hiện tại

Em trực tiếp nghiên cứu, viết narration/storyboard/code, chạy render và xem kết quả.
`local_tools/render_local.py` nhận các file đã viết; nó không gọi LLM API hay Codex CLI.
Không có endpoint API giả cho cuộc chat này. `src/agent.py` vẫn giữ chế độ provider API của upstream
cho nhu cầu chạy tự động độc lập, nhưng lối local đã kiểm tra không dùng chế độ đó.

Một plan tối thiểu:

```json
{
  "topic": "Why Earth has seasons",
  "target_audience": "General audience",
  "sections": [{
    "id": "section_1",
    "title": "Axial tilt",
    "scene_type": "3d",
    "lecture_lines": ["A tilted axis"],
    "animations": ["Show the tilt relative to the orbital plane"],
    "narration": "Complete English narration goes here.",
    "source": "section_1.py"
  }]
}
```

`source` là file Python đầy đủ, gồm imports và scaffold; class phải tên `Section1Scene`,
`Section2Scene`, ... tương ứng ID. Mỗi lượt local tạo snapshot mới để code/storyboard cũ
không ghi đè thay đổi. Lỗi render được ghi trong `section_N_render.log`.

Chạy từ thư mục repo:

```powershell
.venv/Scripts/python.exe local_tools/render_local.py path/to/plan.json --quality h
# Không narration:
.venv/Scripts/python.exe local_tools/render_local.py path/to/plan.json --no-tts
# Kiểm tra cài đặt 2D + 3D + Kokoro:
.venv/Scripts/python.exe local_tools/offline_smoke.py --fresh --tts
```

Kokoro cần hoạt động tại `http://127.0.0.1:8880`; có thể đổi bằng `--tts-endpoint`.
Audio hiện được căn theo section bằng cách retime toàn bộ animation để đủ narration.
Chưa có căn từng từ/beat, subtitle hay preservation của thời gian mô phỏng vật lý.
Video vật lý có thời gian thật cần được author trực tiếp theo thời lượng narration.

## Repo 2.0 visual contract

Storyboard mới yêu cầu `visual_thesis`, `visual_metaphor`, ba lớp `foreground` / `midground` /
`background`, `primary_object`, `secondary_objects`, `object_relationships`, `camera_plan`,
`transition_in`, `transition_out` và `sfx_cues`. Đây là metadata thiết kế; code Manim vẫn là nguồn
đúng cuối cùng của hình ảnh. Storyboard v1 thiếu trường vẫn chạy được với fallback.

Mỗi section có SFX procedural deterministic từ `src/sfx.py`, bám theo cue trong storyboard và được
trộn dưới narration Kokoro trước khi mux. Cues có `type`, `trigger`, `relative_time`, `duration`,
`intensity`, `purpose`; có thể mở rộng sang asset SFX sau mà không đổi schema.

Mốc v1 trước nâng cấp được giữ ở branch/tag `code2video-v1-20261009`.

## Phạm vi sử dụng lowbudget3d

Đã đọc nền đầy đủ `3dviz-pro-max` và overlay `lowbudget3d`; các thư mục tài nguyên nền có sẵn.
Route ở đây là custom analytical geometry, giữ Manim theo dự án đại ca đang sửa.
Áp dụng guidance về representation, claim → model → visual, cinematic motion và anti-fake-pass
vào prompt cùng việc kiểm tra đầu ra. Không bật module humanoid/animal/GPU vì chưa có đối tượng đó.

Đây là bridge hướng dẫn cho Manim, không phải tích hợp renderer Three.js hoặc toàn bộ asset pipeline
của lowbudget3d. Khi cần astronaut thật, hành tinh có khí quyển hoặc hố đen có thấu kính,
phải dùng đúng skill chuyên biệt, dựng representation thích hợp và kiểm tra cảnh thực tế.

## Kết quả quan sát

- Smoke test cold render: 2/2 section render và ghép thành công.
- Local plan runner đã kiểm tra trước khi khóa cấu hình; sau yêu cầu của đại ca, toàn bộ render mặc định và CLI chỉ nhận 1080p60.
- Smoke test sau khi khóa: 2/2 section ở 1080p60, Kokoro `am_michael`, 0 LLM API call.
- Video cuối H.264 1920×1080, cả `r_frame_rate` và `avg_frame_rate` là `60/1`, AAC mono 48kHz,
  dài 25.895625 giây; FFmpeg giải mã toàn bộ không báo lỗi.
- Đã xem frame 3s, 10s, 16s, 24s: chữ tiếng Việt, ellipse/công thức, khối 3D và arrow hiển thị;
  title/lecture nằm cố định. Các điểm chuyển động khác nhau giữa các frame.
- Python compilation, scaffold replacement/idempotence, nhánh prompt 3D và `git diff --check` đã qua.
- Chưa thử gọi provider LLM/VLM ngoài, chưa kiểm tra nhánh Critic qua VLM thật.

Evidence: `local_tools/evidence/current_1080p_contact.jpg`.
Video: `src/CASES/LOCAL_OFFLINE_c58c96fb/0-Space_and_geography_offline_check/Space_and_geography_offline_check.mp4`.
Fixture được viết bằng tay, có mục đích kiểm tra cài đặt; không phải video khoa học hoàn thiện.
Chuyển động điểm trên ellipse có tốc độ đều, không phải nghiệm quỹ đạo Kepler.
Hai cube và arrow chưa đạt domain fidelity của mô hình kiến tạo. Vì vậy chỉ kết luận pipeline chạy,
không gắn FINAL PASS về khoa học hoặc chất lượng điện ảnh cho fixture.
