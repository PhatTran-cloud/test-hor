# Dọn repo V4.1 — 14/10/2026

Theo yêu cầu rút gọn repo, đã bỏ **157 file** khỏi cây source hiện tại. Dung
lượng file source giảm từ khoảng **64.39 MiB xuống 4.8 MiB**, khoảng **92.6%**.
Đây là dung lượng checkout, không gồm lịch sử Git, môi trường hoặc output local.

| Nhóm đã bỏ | Lý do |
| --- | --- |
| Paper PDF, demo GIF, figures, video benchmark và ảnh toán cũ | Không được entrypoint V4.1 hoặc test hiện hành dùng |
| Freesound assets | Route hiện hành dùng Small-SFX, các file này không còn được gọi |
| Pilot El Niño, Hilbert Hotel, great circle, Europa và V3 smoke | Các thử nghiệm cũ ngoài phim/route hiện tại |
| Provider-stage scripts/prompts và evaluator API cũ | Không có caller trong route/test giữ lại; tránh thêm entrypoint cạnh production.py |
| Flowkit snapshot, các bản contract/report/guide cũ, README nghiên cứu gốc | Trùng hoặc thuộc hướng đã thay thế; hướng Flow hiện tại xuất prompt cho người dùng |
| Source-copy receipt và fixture preview dùng host cũ | Receipt thuộc snapshot ban đầu; fixture cũ tham chiếu máy Windows và Kokoro |

Đã kiểm tra import/caller và link trước khi bỏ. Giữ `production.py`, pipeline,
renderer adapters, helper `v3_contract.py` mà V4 vẫn dùng, runtime sprites,
test, V4 browser fixture, current contracts/skills, reference camera/art cần cho
asset direction, dependency manifests và Small-SFX vendor/tokenizer/license.
Giữ các research hiện hành có ghi rõ mức bằng chứng; chưa xóa lịch sử Git.

Các file đã bỏ có thể xem lại trong
[snapshot gốc](https://github.com/PhatTran-cloud/test-hor/tree/40d29e39857c94e7ae66c52e8037fcb7082e66fd).
Để clone gọn, chỉ lấy trạng thái `main` hiện tại:

```bash
git clone --depth 1 https://github.com/PhatTran-cloud/test-hor.git
```

## Kiểm tra và thay đổi đi kèm

- **87 regression tests chạy qua**, gồm FFmpeg 180s/180 ảnh, ba cửa sổ/540 mẫu
  giả lập, PTS/offset, file lỗi/ghi đè, CLI và scene/state carry qua cut/return.
- Fixture test V4 không còn đòi `C:/Users/thebl/.codex/skills`. Nó vẫn là
  `technical_fixture`; không tạo receipt giả rằng đã dùng skill sản xuất.
- Kiểm tra link Markdown local và diff có xét newline CRLF của repo.
- Đối chiếu skill bằng brief hành lang giả lập đã chỉ ra cần phân biệt detail
  shot cùng world với insert/return đổi world; hướng dẫn đã làm rõ điều này.

Các test là kiểm tra source/công cụ, không phải artwork/audio hay chứng minh
đã xem reference. [Nghiên cứu](2026-10-14_reference_study.md) vẫn ghi **0/540
ảnh tham chiếu**, vì media bị chặn. Chưa tạo artwork, TTS/SFX hoặc render phim.
