# OverSimplified → hướng sản xuất hoạt hình kinh dị

Ngày nghiên cứu: 13/10/2026. Workspace: `D:/manim-horror-v4.1`.

Yêu cầu hiện tại: tập trung hoàn toàn vào OverSimplified, nghiên cứu trước khi sửa repo; AI tạo artwork, Remotion ghép và motion. Camera chủ yếu focus và zoom in/out; diễn xuất, biểu cảm, bối cảnh và đạo cụ phải theo nội dung từng cảnh.

Tài liệu này là kết quả nghiên cứu và đề xuất triển khai. Nó **chưa thay thế contract/skill/validator của repo**, chưa duyệt artwork, chưa xác nhận có thể đạt chất lượng tương đương bằng một lần sinh ảnh. Tham chiếu hình ảnh chủ động chỉ còn OverSimplified; các nguồn ở packet cũ giữ lại như lịch sử.

## 1. Phạm vi và mức bằng chứng

Đã mở kênh gốc, chọn bốn tập từ danh sách video; xem các khung/chuỗi khung qua trình duyệt Codex, đọc transcript ba tập và đối chiếu với contract hiện tại. Đây là nghiên cứu có lấy mẫu theo các loại cảnh, **không phải tuyên bố đã xem trọn tất cả video của kênh**.

Phân loại dùng xuyên suốt:

- **OBSERVED:** hiện trên khung hình/chuỗi khung đã kiểm tra.
- **CAPTION:** suy ra từ transcript xuất từ YouTube; không phải word-level ASR và không chứng minh frame chính xác của chuyển động.
- **PROPOSED:** cách chúng ta áp dụng vào kinh dị hoặc Remotion, chưa chạy thử.
- **UNVERIFIED:** chưa kiểm chứng; không dùng làm bằng chứng PASS.

Không suy phần mềm, cấu trúc rig, số FPS nội bộ hoặc công thức easing của họ từ output. Bài Reddit tìm được là lời tự nhận của tài khoản đã bị xóa; không dùng làm căn cứ kỹ thuật của contract. Âm thanh của các tập chưa được kiểm tra bằng tai trong phiên này; cue ghi trong transcript chỉ giúp nghiên cứu cấu trúc, không chứng minh chất lượng mix, gain hay ducking.

## 2. Nhật ký nguồn quan sát

Timestamp dưới đây là đồng hồ nhìn thấy trong player, không phải chỉ thời điểm định seek. Quảng cáo và phần tài trợ không được tính là artwork của phim. Một lần seek ở Part 3 bị buffering giữ hình cũ: đã loại khỏi kết luận về VFX.

| Nguồn | Mẫu quan sát | Bằng chứng và ý nghĩa |
|---|---|---|
| [Second Punic War Part 1](https://www.youtube.com/watch?v=lsbcN9-jU1Y&t=65s) | 1:05 | Toàn cảnh sân, sân khấu, hai hàng quân, cây và kiến trúc; đám đông há miệng/phản ứng. Khoảng trống giữa hai hàng có chức năng dàn cảnh. |
| [Cùng scene](https://www.youtube.com/watch?v=lsbcN9-jU1Y&t=77s) | 1:17, 1:20 | Khung gần diễn giả rồi khung rộng nhóm nghe; nhiều miệng chuyển sang trạng thái ngạc nhiên. Sân khấu, diễn giả và đám đông vẫn thuộc một địa điểm. |
| [Part 1](https://www.youtube.com/watch?v=lsbcN9-jU1Y&t=150s) | 2:30 | Hai nhân vật trên nền bờ biển/địa hình, tay mảnh giơ theo câu thoại; mặt đơn giản nhưng trang phục và mũ có lớp/chi tiết. |
| [Part 1](https://www.youtube.com/watch?v=lsbcN9-jU1Y&t=240s) | 4:00 | Nhóm chiến đấu có vũ khí, khiên, ngựa, nhân vật ngã; hướng đạo cụ và hướng cơ thể tạo hành động. Không thể thay bằng pose đứng lắc. |
| [Part 1](https://www.youtube.com/watch?v=lsbcN9-jU1Y&t=330s) | 5:30 | Phòng họp có cột, nền phối cảnh, bục, bản đồ trên giá và người nghe ở nhiều vị trí. |
| [Cùng scene](https://www.youtube.com/watch?v=lsbcN9-jU1Y&t=340s) | 5:40–5:41; step frame | Khung gần giữ bản đồ/cột/người nghe. Có que chỉ hướng bản đồ rồi hạ; nét mặt nhân vật chính khác các mặt chấm đơn giản. Có pose hold qua câu thoại. Không đo tốc độ zoom từ kích thước screenshot vì player có thay đổi layout. |
| [Part 1](https://www.youtube.com/watch?v=lsbcN9-jU1Y&t=433s) | 7:13 | Cha và con trên mép cao, bờ biển, núi và trời xa; viền sáng ấm và bóng vẽ. 2D không đồng nghĩa mọi mặt chỉ một màu. |
| [Part 1](https://www.youtube.com/watch?v=lsbcN9-jU1Y&t=1385s) | 23:05, 23:10 | Vách núi, tuyết, băng và đạo cụ trong cảnh lạnh; tiếp theo là gag ăn uống với nền giản lược. Mật độ nền thay theo chức năng shot. |
| [Emu War](https://www.youtube.com/watch?v=BXpu6tbFCsI&t=130s) | 2:10 | Đồ họa giải thích bằng địa lý, đường nối, kéo và vàng. Đây là explanatory insert, khác scene nhân vật sống trong môi trường. |
| [Emu War](https://www.youtube.com/watch?v=BXpu6tbFCsI&t=303s) | 5:03 | Phòng nghị viện có bàn, ghế, hàng người, gỗ ốp, cửa và điểm tụ; nhân vật có mặt/eyebrow khác nhau. |
| [Emu War](https://www.youtube.com/watch?v=BXpu6tbFCsI&t=364s) | 6:04 | Đá, cỏ nhiều lớp, nền đất và bàn bản đồ. Cỏ/lông có texture vẽ; nền không phải một hình chữ nhật màu trơn. |
| [Emu War](https://www.youtube.com/watch?v=BXpu6tbFCsI&t=369s) | 6:09–6:10; step frame | Cảnh nhóm chụp hình có máy quay/tripod, ghế và cử chỉ hướng vào máy; có miệng đang nói. Nền sáng tối giản có chủ đích trong gag. |
| [Prohibition](https://www.youtube.com/watch?v=AAGIi62-sAU&t=182s) | khoảng 3:02 sau quảng cáo | Quán rượu có quầy, bàn, ghế, cốc, sàn phối cảnh, cửa và đám đông; nhiều trang phục/tóc và trạng thái mặt khác nhau. Transcript không xuất được. |
| [Second Punic War Part 3](https://www.youtube.com/watch?v=1BVJzaXv3rk&t=171s) | 2:51, phiên trước | Phòng dài có sàn gạch, giáp trưng bày, giáo, cửa và ghế; nhân vật ở các lớp sâu khác nhau. |
| [Part 3](https://www.youtube.com/watch?v=1BVJzaXv3rk&t=1767s) | 29:27 | Scene trại: lều, thùng, khiên/vũ khí và tờ giấy nhân vật đang đọc; đạo cụ kể chuyện, khuôn mặt thể hiện căng thẳng. |
| [Part 3](https://www.youtube.com/watch?v=1BVJzaXv3rk&t=2151s) | 35:51, 36:01, 36:11 | Trại có hàng rào/thang, nhiều lều; chuyển sang người lính nghỉ rồi khung gần nhân vật trong tối có tán lá che mép. Hành động và shot scale thay để kể cùng sự kiện. |

Transcript gốc ba tập và SHA256 được giữ trong `outputs/Chon_Ba_Hai_Lan_2026-10-11/research/oversimplified/`. Không dùng timestamp caption làm timestamp hoạt hình của phim chúng ta.

## 3. Tạo hình: hệ thống đơn giản có chủ đích

**OBSERVED:** đầu lớn, thân nhỏ, silhouette rõ, tay thường là nét mảnh; mặt phụ có thể chỉ là mắt chấm/miệng đơn giản. Tóc, mũ, râu, da và phục trang phân biệt người. Nhân vật chính đôi khi có mặt chi tiết hơn; không phải tất cả nhân vật cùng một preset. Trang phục, giáp, đồ gỗ và môi trường vẫn có nét, bóng và texture minh họa.

**PROPOSED:** khóa một character bible cho từng vai trước khi sinh assets: silhouette, tỉ lệ, khuôn mặt, màu/tóc, trang phục, tuổi nhìn thấy và trạng thái sống/biến đổi. Giữ Viễn 22–25, mẹ 48–52, bà 75–80; Việt Nam hiện đại theo lựa chọn đã có. Phải đọc được quan hệ mẹ–con ngay cả trong hình đơn giản. Không dùng tuổi giọng để chọn tuổi mặt.

Chúng ta sẽ có style của phim kinh dị riêng với cùng mức đơn giản, độ rõ và cách dàn cảnh. Việc AI có giữ identity ổn định qua nhiều view/biểu cảm phải kiểm tra trên ảnh thật; không dựa vào câu “same character” trong prompt.

## 4. Bối cảnh: scene là thế giới; shot là góc nhìn của thế giới đó

**OBSERVED:** phòng nghị viện, quán rượu và phòng họp có kiến trúc, đồ dùng, người và nền phối cảnh. Cảnh thiên nhiên có ground plane, lớp vật gần/xa và chi tiết vật liệu. Một số insert/gag dùng nền trắng giản lược. Vì vậy không đặt luật “mọi shot phải kín đồ vật”, cũng không lấy insert trắng làm lý do dựng cả phim trống.

**PROPOSED:** mỗi scene có `world_layout` gồm vùng hành động, đường ra/vào, vị trí vật thể, tỉ lệ người, điểm tụ/đường chân trời, hướng ánh sáng và trạng thái thời tiết. Shot chỉ chọn khung/crop/view của world đó. Giữ một mã scene và các mã đối tượng qua mọi cut.

Thiết kế nền theo ba loại chi tiết: chi tiết bắt buộc bởi truyện; chi tiết nhận diện nơi/thời đại; chi tiết không khí/chiều sâu. Mỗi chi tiết phải có lý do, không đặt quota cây/đồ vật. Trong phòng của bà, cửa, giường Viễn và giường bên của mẹ phải nằm đúng quan hệ để mẹ có thể lao sang. Vật thêm như ghế, đồ cá nhân hay ánh đèn là đề xuất phải nhất quán với bối cảnh, không giả thành chi tiết có trong lời kể.

Thử rừng mưa nếu được tiếp tục: cần canopy, thân/rễ, cây thấp, đường hoặc nền đất, vật ở gần/xa, nguồn mưa và bề mặt nhận mưa. Đây là benchmark riêng, không thêm một địa điểm vào kịch bản của Viễn. Không có cảnh rainforest OverSimplified nào được xác nhận trong tập mẫu đã xem; chỉ có cỏ, bờ biển, núi tuyết và lá trong cảnh tối.

## 5. Diễn xuất: face + body + prop + người nghe

**OBSERVED:** biểu cảm nhóm nghe thay theo thông tin; người nói có tay chỉ/giơ/hạ. Cùng một nhân vật có pose hold, cử chỉ và phản ứng. Hành động chiến đấu dùng hướng vũ khí, thân và trạng thái ngã. Mặt chấm và mặt chi tiết cùng tồn tại.

**PROPOSED:** mỗi beat có `acting_intent`, `trigger`, `gaze_target`, `face_state`, `body_pose`, `gesture`, `contact`, `listener_reaction` và `end_state`. Sợ, tức, nghi ngờ, thương hay nói nhỏ phải được thể hiện thành mắt/lông mày/miệng/tư thế cụ thể. Không có một “idle scared loop” dùng cho mọi câu.

Mắt có thể quay trước đầu; đầu và thân đến sau; tay bắt đầu khi có mục đích. Không bắt toàn thân, mặt, người nghe, đồ vật và camera cùng ease cùng lúc. Pose giữ vẫn là diễn xuất nếu nó truyền ý và được thay đúng beat. Số pose/miệng/cử chỉ theo hành động, không cố định theo scene hay số giây.

Mouth animation: ưu tiên câu đang nói và độ đọc được của nhân vật. Word-level ASR cho mốc từ, **không tự cho ra phoneme/viseme**. Nếu cần lip-sync chi tiết thì thêm alignment phù hợp; nếu chỉ animate miệng mở/đóng thì ghi rõ mức đó và nghe/xem kiểm tra. Không biến điều này thành tuyên bố biết rig của OverSimplified.

## 6. Rig và sprite: AI supplies art, Remotion supplies acting

**PROPOSED, phù hợp chỉ đạo user:** không chỉ sinh nguyên người đứng rồi lắc cả PNG. Dùng bộ phận cho acting thông thường; pose/view thay thế cho hành động mà rig đơn giản không biểu đạt được.

| Bộ asset | Nội dung | Mối nối/kiểm tra |
|---|---|---|
| Head/face | đầu, tóc; mắt/mí/eyebrow/miệng hoặc expression patches | pivot cổ, hệ tọa độ mặt, che khuất tóc, nét/thang màu thống nhất |
| Torso/costume | thân, quần áo, phần che khớp | cổ/vai/hông, vùng vẽ ẩn khi tay/thân quay |
| Limbs | tay trên/dưới, bàn tay hoặc đường vector; chân/feet phù hợp thiết kế | chiều dài, joint limits, thứ tự front/back, điểm cầm nắm |
| Replacement poses | quay mặt, nằm/ngồi, co rúm, ngã, chạy hoặc transformation | identity, registration, entry/exit và view thật có sẵn |
| Props | đồ cầm, cửa, nắp quan tài, nhang, hình nhân | chủ sở hữu, grip/hinge, trạng thái trước/sau, biến đổi có nguyên nhân |
| World layers | nền, nhóm kiến trúc, lớp che, vật tương tác | cùng phối cảnh/tỉ lệ/ánh sáng; sạch phần có thể lộ khi zoom hoặc nhân vật di chuyển |

AI thường trả raster dù hình trông như vector. Chỉ gọi là editable SVG khi file thực sự có paths. Nhân vật/lớp cần alpha phải có alpha thật; ảnh opaque không ép đổi PNG. Giữ originals, masks, hash, kích thước đo và anchors/socket đo; một alpha channel có tồn tại chưa chứng minh sạch viền.

Remotion: toàn bộ transform/pose/expression/camera theo frame tuyệt đối; có parent hierarchy, FK/IK hoặc solver khi tiếp xúc yêu cầu; không CSS animation hoặc trạng thái phụ thuộc lịch sử phát. Chân trụ khóa trước chuyển trọng tâm, tay chạm trước đồ vật phản ứng. Rig bundle không được miễn asset provenance, view limits, contact review hoặc snapshot validation.

## 7. Camera và bố cục

**OBSERVED:** chuỗi sân đổi wide/near/reaction; phòng bản đồ giữ các mốc khi khung gần; cảnh tối đổi từ camp sang khung gần. Không đo phần trăm camera move của cả kênh từ các mẫu này.

**USER RULE + PROPOSED:** mặc định khung cố định; focus bằng staging, eye trace, biểu cảm, tương phản, crop và zoom in/out. Không hiểu focus là phải blur nền ở mọi shot. Zoom chỉ khi nó đổi điều người xem hiểu/cảm thấy; giữ im khi hành động/âm thanh cần nổi bật.

Mỗi shot ghi frame vào/ra, focal target, lý do đổi khung, vùng artwork có thể lộ và khoảng crop an toàn. Không pan/orbit để tạo cảm giác phim trong khi nhân vật chết cứng. View khác phải có artwork tương ứng, không lật PNG khi thay đổi bên của đồ vật/costume có ý nghĩa.

## 8. Dựng và nhịp kể

**CAPTION + OBSERVED:** đoạn mở Part 1 đi từ trao đổi → thông tin gây sốc → phản ứng → hậu quả; sau đó narrator nối sang phần giải thích. Một cảnh không ứng với một câu hay một dòng caption. Cùng world có thể có nhiều shot; một đoạn kể có thể nối qua hành động và insert.

**PROPOSED:** ưu tiên cut theo thông tin mới, ánh nhìn, hành động, lời thoại hoặc phản ứng. Wide để định hướng; medium để thấy tương tác; close/insert để nhấn chi tiết; return shot để giữ địa lý khi cần. Không bắt tất cả scene đi qua một chuỗi kích thước cố định.

Kinh dị đổi phần chờ/punchline thành anticipation/reveal/aftershock theo kịch bản. Cửa chưa mở, khoảng tối hay gương mặt bị giấu có thể giữ lâu hơn người xem mong đợi. Đây là dụng ý của phim chúng ta; không tự thêm pause vào bản WAV đã đo hoặc kéo giãn voice. Khoảng lặng phải có kế hoạch từ voice/silence stage, lấy timestamp thật sau tổng hợp.

## 9. Màu, ánh sáng, chất liệu và thời tiết

**OBSERVED:** quán rượu có gỗ và chiều sâu; đồng cỏ có texture; costume/giáp có shading; cảnh cha–con có trời ấm/viền sáng; night close-up giữ được mặt và foliage tối. Kênh không phải hệ “solid fills only” tuyệt đối.

**PROPOSED:** thân/face chủ yếu shape rõ và màu gọn; môi trường được dùng bóng vẽ, texture minh họa và chuyển sắc tiết chế khi chúng phục vụ chiều sâu/không khí. Không dùng photorealistic texture hoặc PBR bóng để thay craft 2D. Mức chi tiết nền phải hỗ trợ nhân vật, không tranh điểm nhìn.

Kinh dị không phủ đen mọi thứ. Giữ đọc được đường cửa, bàn tay, mắt, vật chứng và silhouette; tương phản có thứ bậc. Mưa/sương/khói/ánh nhang là hệ riêng trong composition để điều khiển onset, occlusion, phản ứng và continuity. Không bake mưa động vào mọi sprite. Nhang chỉ xuất hiện/phát sáng đúng câu truyện; không dùng từ đầu phòng ngủ vì hợp mood.

## 10. Âm thanh và đồng hồ

Transcript của Part 1/Part 3 có cue crowd, suspenseful/dramatic music và thunder; đó là bằng chứng caption, chưa kiểm tra sound mix. Không lấy cue của họ vào phim chúng ta theo mặc định.

Giữ các quyết định repo đã có: OmniVoice, cast đã chọn; ASR word-level luôn luôn; Small-SFX theo event, GPU theo thứ tự; không BGM nếu chưa được yêu cầu; không sửa WAV test có rè mà user đã bảo giữ. Kết quả nghiên cứu không tự duyệt audio cũ.

Shot/acting/events lấy từ WAV thật và ASR đã kiểm tra. Giữ audio độc lập với scene cuts, cho phép room tone/tail tồn tại qua cut. Mốc chữ chỉ là một anchor; anticipation có thể trước chữ, phản ứng sau chữ nếu đã được đạo diễn, nhưng không được sửa nhận dạng để giả timestamp thuận tiện.

## 11. Quy trình asset AI đề xuất

1. Chốt world/character/style bible theo kịch bản, tuổi/thời đại và view cần dùng.
2. Làm layout/master environment để duyệt địa lý, rồi có clean plate và các lớp/đạo cụ cần tách. Master layout là tài liệu dàn cảnh, không trở thành video phẳng thay mọi tương tác.
3. Tạo bộ character/parts/expressions/replacement poses có cùng identity. Các phần bị che vẫn phải đủ vùng vẽ nếu motion làm lộ.
4. Kiểm tra art thật, tách alpha, crop, root/ground/joints/grips; sửa lỗi identity/chi tiết trước rig.
5. Animate chính scene đại diện: blocking → acting/contacts → camera → atmosphere/SFX → review video thực.
6. Chỉ sau kết quả scene đại diện mới nhân rộng.

Flow Nano Banana 2.1 và batch năm prompt là lựa chọn hiện có của user; batch là cách gửi request, **không phải quota assets hoặc poses**. Nếu một asset lỗi thì xử lý đúng asset ấy. Không sinh năm cảnh độc lập rồi cố ghép thành cùng phòng. Bộ phận không cần AI sinh lại từng frame; chuyển động đơn giản được code điều khiển, view/biểu cảm/pose cần artwork mới khi rig hiện có không đủ.

## 12. Ví dụ áp vào kịch bản hiện tại — đề xuất, chưa dựng

Scene buồng bà giữ cửa kín, giường Viễn, giường bên của mẹ và đường lao sang. Quan tài ở sân theo truyện, không chuyển vào phòng để tiện bố cục.

| Beat theo truyện | Hình/acting đề xuất | Cách dàn cảnh |
|---|---|---|
| Chó im; tiếng gõ | Viễn đang ngủ; ngưng/đổi trạng thái nghe; chú ý chuyển tới cửa | Wide trước để xác lập mẹ/Viễn/cửa; đồ trong phòng vẫn đúng vị trí |
| Giọng bà gọi bên ngoài | Viễn mở mắt, nhìn cửa, người căng; chưa thấy hình bà | Giữ ngưỡng cửa kín và điểm tối; không reveal bà sớm |
| Viễn ngồi bật, định hỏi | thân bật trước, tay chống giường, mặt/miệng chuẩn bị nói | Medium để đọc hỗ trợ và chuyển tư thế; không chỉ kéo PNG lên |
| Mẹ lao sang bịt miệng | mẹ hướng mắt vào Viễn, trọng tâm di chuyển, tay tới miệng; Viễn giật mình | Tay chạm trước miệng bị che; frame phản ứng giữ cửa/giường làm mốc |
| “Suỵt!” và lời cấm | mẹ giữ tay, mặt hoảng, người che; Viễn bị ghìm và nhìn mẹ | Close/medium theo thông tin; không reset về idle giữa hai câu |

Timing ở đây là semantic beat, không timestamp mới. Sẽ lấy anchor từ word-level ASR hiện có khi được giao storyboard/motion cụ thể.

## 13. Các chỗ repo cần sửa — chưa thực hiện

| File/nhóm | Vấn đề hiện tại | Đề xuất sửa |
|---|---|---|
| `Code2Video/AGENTS.md`, `START_HERE.md`, `docs/HORROR_CONTRACT.md` | Còn default 3D/Kage và một override 2D nằm trên; dễ tái dùng chỉ dẫn cũ | Một nguồn quyết định style hiện hành, primary reference OverSimplified; ưu tiên rõ so với lịch sử. Giữ mode từng bước. |
| `horror_contract.py` | Flat style vẫn bắt Kage; asset types chỉ sprite/prop/layer | Reference requirement theo style user chọn; thiết kế support rigged parts có validation đủ, không biến thành bypass asset checks. |
| `prompts/v4.py` | Hướng 2.5D pose playback/Flow và Kage chưa mô tả cutout acting đầy đủ | Cho context đưa đúng style/world/parts/acting, adjacent handoffs và current user decision; không nhét tất cả historical directives. |
| `docs/V4_AUTHORING_GUIDE.md` | Generic no-stick-default và whole-pose sprite route dễ mâu thuẫn với user chọn kiểu thân/tay đơn giản | Phân biệt thiết kế simple do user chọn với placeholder; thêm world → shots, cutout rig, expression/prop/contacts và measured word anchors. |
| Project `horror-asset-director` + workflow reference | Còn wording 3D mandatory; chỉ đặt trọng tâm pose/view | Đồng bộ style, master layout/clean plate, part bundles, expression states, alpha thật, vùng bị che và identity review. |
| `horror_assets.py`, `horror_sprites.py`, `flow_assets.py`, browser runtime/snapshot | Pipeline hiện ưu tiên pose files, root/socket và đơn giản pin một socket | Trước khi sửa phải audit sâu phần này: parent/joint registration, FK/IK contact, replacement-view selection, part hashes và snapshot dependencies. Không coi FK là đủ cho mọi tương tác. |
| `v4_workflow.py` và prompt routing | Routing dựa renderer/scene type; style phải đi đúng routes | Remotion cho cutout 2D; chỉ gọi 3D skills khi thực sự 3D, reference resources theo current style. |
| Quality gates/tests | Có technical observations nhưng chúng không đo đủ art/acting | Test parser/validator/seek/contact/invalidation; review thật world richness, expression, grip/support, reveal, join và audio. Không dựa unit tests để PASS hình. |
| Canonical `production_packet.json` | Còn hướng rainforest trial + nhiều style lịch sử | Ghi user chọn OverSimplified primary; archive đề xuất cũ, bổ sung style/scene/acting hợp nhất sau khi sửa được giao. Không rewrite full phim ở research stage. |

Skill files ở `.agents` hiện được sandbox cho đọc; nếu bước sửa sau chạm vào chúng, phải dùng quyền ghi đúng cơ chế của môi trường. Đây là vấn đề quyền file, không phải lý do đổi sang runner hoặc sửa riêng docs rồi nói toàn bộ route đã cập nhật.

## 14. Điều kiện review đề xuất

Mỗi mục cần evidence từ ảnh/clip hiện hành, không tự ghi expected thành observed:

- Wide đủ địa lý và chất liệu; zoomed shot vẫn thuộc cùng world, có vùng sạch khi lộ.
- Nhân vật nhận diện, tuổi/quan hệ đúng; costume/props không đổi không giải thích.
- Hero action và trạng thái mặt đọc được; người nghe có phản ứng hoặc giữ có chủ đích.
- Joint/hand/foot contacts đúng; đồ vật không tự chạy; môi trường phản ứng có nguyên nhân.
- Camera có lý do, focus/zoom giữ framing/crop; không chuyển động để che acting yếu.
- Pose/view/face changes không nháy; state qua cut đúng; seek không tuần tự cho cùng kết quả.
- Voice/SFX nghe thật và đúng clock; word timestamps được kiểm tra; không có auto-PASS.

Đây là các kiểm tra thực thi yêu cầu user và contract, không đặt quota cứng hay chấm nghệ thuật bằng số đối tượng.

## 15. Kết luận nghiên cứu và điểm còn chưa xác nhận

Hướng khả thi về kỹ thuật là AI artwork có identity/world nhất quán + part/replacement-pose assets + Remotion acting/compositing. Chất lượng tương đương kênh chỉ được đánh giá sau mẫu thật; chưa có bằng chứng output của chúng ta đạt mức đó.

Những điều đã đủ căn cứ để đề xuất sửa: đơn giản hóa nhân vật có chủ đích; môi trường được thiết kế đầy đủ; diễn xuất theo beat; camera/cut phục vụ thông tin; cảnh 2D được phép shading/texture minh họa; art tạo trước rồi motion các lớp, không mỗi shot sinh một world khác.

Những điều không được khẳng định: phần mềm/rig nội bộ của họ; tỷ lệ zoom/pan trên toàn kênh; FPS pose cadence; phoneme pipeline; gain/mix/mastering âm thanh; cảnh rừng mưa cụ thể chưa thấy; khả năng AI đạt likeness/alpha qua nhiều lần mà không sửa.

Bước tiếp theo đề xuất: sửa đồng bộ docs/contract/prompts/asset schema/runtime/skills theo các điểm trên, với `script-to-visual-director` cho world/shot, `horror-asset-director` cho part/pose/provider, `cinematic-motion-director` cho acting/contacts/camera và `remotion-best-practices` cho frame-driven execution; giữ `local_tools/production.py`, schema 4 và các audio/review gates. Chạy test cần thiết cho thay đổi contract/runtime, trình diff và hạn chế rồi dừng. Chưa tạo ảnh, TTS/SFX hoặc render trong bước nghiên cứu.
