# Scene và shot: thế giới, thông tin, hành động, liên kết

Đây là hướng dẫn tác giả cho phim của chúng ta, **không phải kết luận từ 540 ảnh
chưa lấy được**. Mức bằng chứng ở [nghiên cứu](research/2026-10-14_reference_study.md).

## Thiết kế bên trong shot

Scene xác định một không gian/thời điểm liên tục. Shot là đơn vị camera/dựng;
đổi câu thoại hoặc biểu cảm không mặc nhiên tạo shot mới. Panel là keyframe.
Khóa `scene_worlds` trong `production_packet.illustration_direction`: layout,
perspective, lighting, required_props, crop_safety và `spatial_anchors` có tên.
Ghi cửa vào/ra, vùng hành động, vị trí tương đối, ground plane, tỉ lệ người,
hướng sáng và vùng có thể lộ khi đổi khung. Draft dùng lời; sản xuất đo anchors
từ artwork thật. Shot chọn một góc nhìn của world, không sinh lại địa lý mỗi cut.

Phân FG/MG/BG theo chức năng che/định khung, tương tác và định nơi/chiều sâu.
Lớp trống hợp lệ; không có quota đồ vật. Nền lived-in cần địa lý/đồ dùng có
chức năng. Insert giải thích, chủ quan hoặc khoảng trống có dụng ý được giản
lược với lý do cụ thể. Tách người/vật cầm/vật tương tác khỏi clean plate.
Một view mới chỉ cần khi camera lộ phía artwork hiện tại chưa cung cấp.

Ghi function, điểm chú ý chính và frame đầu → hành động chính → frame cuối.
Diễn xuất kết hợp intent, gaze, mặt/pose/gesture, grip/support, phản ứng và
hậu quả. Giữ/focus/zoom có lý do thông tin/cảm xúc; không thay diễn xuất bằng
zoom. Không ép wide → medium → close hay cắt theo mỗi caption. Tĩnh có chủ
đích là state. Người xem biết gì, nhân vật biết gì, điều giấu và reveal ceiling
phải riêng biệt; hình/VO/bóng/phản chiếu/âm thanh/prompt đều giữ trần đó.

## Liên kết shot/scene

Ghi trigger: vì sao cut ngay đây? Ghi next_delta: shot sau thêm điều gì?
Xác định cùng scene, đổi scene, nhảy thời gian, insert, return hoặc kết thúc.
Giữ channel có ý nghĩa: địa lý, gaze/attention, prop state/ownership, motif,
câu hỏi chưa giải quyết hoặc audio tail. Không ép mọi cut nối vận tốc camera
hay luôn giữ hai channel. Cut liên tục trong cùng world phải giữ end_state →
start_state hoặc giải thích thay đổi. Đèn/đồ cầm/vết dấu không tự reset.
Return từ insert cần đối chiếu state trước insert với state lúc trở lại.
Phá địa lý hoặc nhảy thời gian có dụng ý phải ghi rõ; dissolve không che lỗi.
Mix audio trên film clock, không restart ambience/tail mỗi cut.

Phân biệt **insert về cỡ hình** với **insert sang world khác**. Cận cảnh cùng
cánh cửa trong cùng hành lang vẫn là `same_scene`, dù gọi là detail/insert shot.
Relation `insert`/`return` chỉ dùng khi thực sự đổi `scene_id` (ví dụ cắt sang
đồ họa giải thích rồi quay lại). Quay từ cận cửa về wide cùng hành lang vẫn
`same_scene`. Không tạo world mới chỉ để đổi crop hoặc thỏa mãn tên relation.

## Contract tùy chọn cho packet mới, giữ schema 4

Khai `illustration_direction.storyboard_contract="scene-shot/1"` và thêm
`shot.storyboard`. Packet lịch sử chưa có field giữ nguyên, audit trả
`NOT_DECLARED`, không giả đã kiểm tra. Packet mới theo hướng dẫn này dùng
contract để bắt thiếu cấu trúc trước prompt export/production check.

```json
{
  "function": "Phát hiện tín hiệu, giữ nguyên nguyên nhân chưa biết",
  "framing": "Medium giữ khung, hero trái, cửa phải",
  "attention": "hero nhìn khe cửa",
  "primary_action": "hero ngừng tay; cửa giữ tĩnh có chủ đích",
  "background_mode": "lived_in",
  "background_reason": "cửa và đèn xác lập nơi diễn ra sự kiện",
  "staging": {
    "fg": [], "mg": ["hero"], "bg": ["door", "lamp"],
    "screen_direction": "hero trái cửa", "eyelines": "hero nhìn phải về cửa"
  },
  "start_state": {"hero": "đứng trái, nhìn cửa", "door": "khép", "lamp": "tắt"},
  "end_state": {"hero": "đứng trái, nhìn cửa", "door": "khép", "lamp": "tắt"},
  "information": {
    "audience_in": "cửa bình thường", "audience_out": "có tín hiệu ở cửa",
    "character_in": "chưa chắc nguồn", "character_out": "đang quan sát",
    "withheld": ["nguồn tín hiệu"], "reveal_ceiling": "chỉ khe cửa, không lộ thực thể"
  },
  "transition": {
    "relation": "same_scene", "next_shot_id": "door_insert",
    "trigger": "ánh nhìn chốt ở cửa", "next_delta": "thấy tín hiệu ở cỡ gần",
    "carry_channels": ["geography", "prop_state"],
    "preserved_objects": ["door", "lamp"], "state_changes": {}
  }
}
```

Đây là minh họa cấu trúc, không thêm cảnh vào kịch bản đã duyệt. Dùng canonical
IDs thật; state phủ mọi object nhìn thấy. World thêm `spatial_anchors` dạng
`[{"id":"doorway","description":"cửa phải, cố định tương đối với đèn"}]`.
Background modes: `lived_in|explanatory_insert|subjective|empty_by_story`.
Relations: `same_scene|scene_change|time_jump|insert|return|end`. Shot cuối khai
end, next_shot_id=null, preserved_objects=[]. `state_changes` là ID → lý do;
khai báo đó chưa chứng minh animation đã thực hiện sự thay đổi.

```powershell
python local_tools/production.py storyboard-audit draft.json --output ../outputs/storyboard-audit.json
```

Lệnh đọc packet schema 4 và xuất `STRUCTURE_CHECKED`, cùng các edge.
`production.py check` và `asset-brief` cũng kiểm tra khi contract đã khai.
Cùng state dùng cùng wording. Audit kiểm tra IDs, layer coverage, hiện diện
trần reveal và carry khai báo; chưa đọc pixel, so eyeline thật, phát hiện mọi
reveal leak hoặc nghe audio. Nó nhớ state khai báo của vật trong mỗi world,
kể cả lúc vật ra ngoài khung, để bắt reset khi quay lại. `time_jump` cho phép
thay đổi theo thời gian đã khai; state_changes vẫn cần review trên timeline.
Review ảnh/clip/timeline và audio luôn độc lập, không tự art PASS.
