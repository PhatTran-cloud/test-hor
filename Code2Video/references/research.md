# Nghiên cứu Kage và cinematic-video-prompt-skill cho V4.1 horror

Ngày: 11/10/2026. Trạng thái: **nghiên cứu, chưa nâng cấp V4.1 horror**. Cập nhật sau bốn ý kiến của người dùng: xem mục 8–13; đề xuất ở mục 7 thuộc lượt nghiên cứu trước và chưa được chạy.

## Kết luận

**Kage và cinematic-video-prompt-skill tương thích về định hướng nghệ thuật. Kage cung cấp tham chiếu cụ thể cho artwork, không gian và chiều sâu; skill prompt cung cấp cách lựa chọn và mô tả camera, bố cục, ánh sáng, phong cách, vật liệu, môi trường, pose và cảm xúc.** Đánh giá lượt trước nhấn mạnh giới hạn thực thi quá nhiều, chưa làm rõ giá trị của skill đối với việc đạo diễn/storyboard. Hệ thống V4 đã có phần hành vi, sự kiện và continuity để bổ sung; không mặc định phải xây lại từ đầu. Các giới hạn riêng của model sinh video cần được giữ đúng phạm vi, không đưa thành luật chung của V4.

Hướng người dùng đã xác định: giữ illustration, dùng Flow để tạo artwork theo ý đồ; code phối hợp chuyển động của từng object với camera và VFX. Flow thay công đoạn vẽ. Các hành vi và thời điểm sự kiện vẫn thuộc storyboard và runtime V4. Đây là hướng riêng cho horror; chưa thay đổi các loại video khác.

Không chuyển yêu cầu thành cả bộ asset 2D để tránh nghiên cứu 3D. Những chuyển động cần hình học không gian vẫn giữ nhánh 3D của V4; việc chọn cách biểu diễn phải được trình trong bước đạo diễn hình sau này.

## 1. Bằng chứng đã kiểm tra

| Nguồn | Phiên bản nghiên cứu | Phần đã kiểm tra |
|---|---|---|
| [MengTo/kage](https://github.com/MengTo/kage) | `4399487d2fb42bce39c7b032fbbb50d230bf4f0b` | README, PROMPT đầy đủ; ảnh preview; danh mục asset; các phần source liên quan đến lớp foreground, cutout trong không gian, lá, vải, camera, thời tiết và vòng cập nhật. Không tuyên bố đã đọc toàn bộ 4.821 dòng HTML. |
| [Rylaispirit/cinematic-video-prompt-skill](https://github.com/Rylaispirit/cinematic-video-prompt-skill) | `389c193cecafa6118989a2938b7cedc49be2456b` | README, SKILL.md, sáu tài liệu references, examples/example-prompts.md, cả hai bonus skill và LICENSE đầy đủ. |

Bản nguồn lưu tại [sources/kage](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/sources/kage) và [sources/cinematic-video-prompt-skill](D:/manim/outputs/V4_1_Horror_Repo_Research_2026-10-11/sources/cinematic-video-prompt-skill). Chỉ clone/đọc để nghiên cứu; không cài hay kích hoạt các skill bên ngoài, không chạy code của hai repo.

## 2. Kage: mượn ngôn ngữ artwork nào?

Kage là chuyến đi đêm qua một ngôi đền Kyoto, kết hợp cảnh Three.js với ảnh tạo sẵn và foreground có alpha. Nó có kiến trúc procedural, ánh sáng đèn, sương, mưa và lá; không phải hệ thống sprite nhân vật. [README](https://github.com/MengTo/kage/blob/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/README.md).

Quan sát từ ảnh preview: khối kiến trúc chìm trong nền lạnh tối, điểm sáng ấm nhỏ, màu đỏ làm điểm nhấn; cỏ và cành ở trước che một phần cảnh, các lớp xa mất tương phản. Đây là quan sát ảnh tĩnh; chưa đánh giá trải nghiệm chuyển động trực tiếp trên website.

**Có thể chuyển thành định hướng horror:** bố cục có khoảng tối để giấu/reveal chủ thể; foreground tạo che khuất; điểm sáng dẫn mắt; chiều sâu đến từ tương quan kích thước, phối cảnh, độ che khuất và khí quyển. Không cần biến toàn bộ artwork thành một ảnh shot hoàn chỉnh để có chất lượng này. Đây là diễn giải cho ứng dụng mới, chưa phải style bible đã được duyệt.

### Source cho biết giới hạn quan trọng

| Hệ thống trong Kage | Quan sát có bằng chứng | Ý nghĩa đối với V4.1 horror |
|---|---|---|
| Foreground | Có 10 cutout môi trường và 4 scene plate trong bản nguồn; không thấy bộ hành động của nhân vật. [Danh mục foreground](https://github.com/MengTo/kage/tree/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/secret-pathways-assets/foreground/png). | Học cách phân lớp; chưa thể coi là bằng chứng đã giải quyết pose hoặc nhiều góc nhân vật. |
| Plane artwork trong world | Cutout dùng plane, alpha, fog và shader sway; dùng MeshBasicMaterial. [Source, từ dòng 2958](https://github.com/MengTo/kage/blob/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/index.html#L2958). | Có chiều sâu vị trí và che khuất, nhưng một plane không có thể tích của chủ thể; vật liệu này cũng không tự nhận ánh sáng như một mesh PBR. |
| Lá rơi | Quad xoay nhiều trục, rơi và trôi; tái sinh quanh hướng camera. [Source, từ dòng 3172](https://github.com/MengTo/kage/blob/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/index.html#L3172). | Là tham chiếu chuyển động môi trường có hình dáng đọc được; chưa phải hệ lực gió chung tác động nhất quán lên mọi object. |
| Vải | Có cập nhật dạng sóng, lực gió, damping, cạnh ghim và bước mô phỏng cố định; không chỉ dịch chuyển ảnh. [Source, từ dòng 3601](https://github.com/MengTo/kage/blob/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/index.html#L3601). | Tham khảo cách vật liệu phản ứng. Chưa có bằng chứng cho rig áo nhân vật, va chạm cơ thể hoặc độ chính xác vật lý. |
| Camera và thời gian | Camera theo đường cong, scroll và mouse; runtime dùng thời gian thực, có nguồn ngẫu nhiên khi cập nhật. [Camera](https://github.com/MengTo/kage/blob/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/index.html#L4033), [vòng cập nhật](https://github.com/MengTo/kage/blob/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/index.html#L4669). | Không thể đưa nguyên vào video cần seek/render lặp lại chính xác theo frame. Cần thích nghi với clock và quyền điều khiển camera của V4. |

Không mang typography lớn, chapter navigation, cursor hoặc tương tác scroll vào phim chỉ vì chúng xuất hiện trong Kage. Bối cảnh Nhật của Kage cũng không mặc nhiên quyết định bối cảnh văn hóa của horror mới.

README của Kage chưa cấp phép tái sử dụng/phân phối code và artwork gốc. Vì vậy nghiên cứu này dùng nó làm reference để phát triển thiết kế riêng; không coi asset gốc là thư viện production được phép mang sang dự án. [Mục License](https://github.com/MengTo/kage/blob/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/README.md#license).

## 3. Repo cinematic-video-prompt-skill: hợp ở vị trí nào?

**Đính chính:** repo có cả mục 3.6 và reference 05 về artwork style, chứ không thiếu toàn bộ phần style. Điều chưa có là bộ định hướng artwork cụ thể đã được lựa chọn, kiểm chứng và duyệt cho horror của chúng ta. Tên phong cách, ví dụ và từ khóa là dữ liệu đầu vào có giá trị; chúng chưa tự xác định silhouette, mức chi tiết, độ sâu, tỉ lệ nhân vật và cách xử lý vật liệu cho một phim cụ thể.

| Thành phần | Có thể tham khảo | Phần còn thiếu hoặc cần loại khỏi route V4 |
|---|---|---|
| Camera, composition, lens | Diễn đạt cỡ cảnh, hướng nhìn, truck/pan/dolly, tiền cảnh che khung, khoảng nhìn và vị trí chủ thể. | Từ khóa không thay cho đường camera, FOV và kiểm tra vùng nhìn thấy thực tế. |
| Lighting, material, weather | Mô tả hình dạng, chất liệu và ánh sáng cụ thể khi lập brief artwork. | Không giải quyết alpha, relighting, chiều sâu, điểm gắn hay các lớp cần tách để animate. |
| Chuỗi cảm xúc | Mô tả diễn xuất theo trình tự; hữu ích khi nghiên cứu pose thay vì một nhãn cảm xúc chung. | Chưa có cơ chế mắt–đầu–thân, chuyển trọng tâm, anticipation, tiếp xúc và phục hồi. |
| Sự kiện horror | Mục 8.10 nhấn mạnh vị trí, thời điểm và kết quả nhìn thấy. | Chưa có hệ tác nhân → lực → phản ứng object → hậu quả môi trường; cũng chưa là phương pháp xây dựng căng thẳng horror hoàn chỉnh. |
| Khóa nhận diện | Nhắc lại đặc điểm, dùng reference và mô tả giải phẫu chủ thể lạ. | Chưa chứng minh Flow giữ được nhận diện qua các hành động và góc khác nhau. |

Các nhận xét trên dựa vào [SKILL.md](https://github.com/Rylaispirit/cinematic-video-prompt-skill/blob/389c193cecafa6118989a2938b7cedc49be2456b/SKILL.md) và [references](https://github.com/Rylaispirit/cinematic-video-prompt-skill/tree/389c193cecafa6118989a2938b7cedc49be2456b/references). Đánh giá “có thể tham khảo” là suy luận cho yêu cầu của người dùng, không phải kết quả thử nghiệm tích hợp.

### Những phần không phù hợp nếu dùng nguyên bản

- Workflow chính hướng tới AI sinh cả clip ngắn. Công thức gồm hành động, bối cảnh, ánh sáng và chuyển động camera trong cùng prompt. Nó lại giao cho AI nhiệm vụ mà người dùng muốn giữ trong code.
- Mục 8.1 chấp nhận lệch thời gian khoảng vài giây. V4 cần timing dựa trên audio đo thật và frame; không mang sự chấp nhận lệch này sang production.
- Giới hạn số nhịp cho clip ngắn là kinh nghiệm giảm tải model video của tác giả. V4 không đặt quota shot/beat; beat phải theo ý nghĩa và thời gian thực của nội dung.
- Cảnh báo model bỏ qua con số không phải lý do bỏ kiểm tra độ phân giải, fps, thời lượng hoặc camera của runtime.
- Những nhận xét thành công của model là kinh nghiệm tác giả. Repo không kèm tập kết quả và quy trình đánh giá đủ để xác minh độc lập các khẳng định đó; không coi là benchmark hay bảo đảm cho Flow.

### Hai bonus skill không giải quyết bài toán asset animation

**character-sheet-lite** tạo một bảng gồm trước/nghiêng/sau ở A-pose và cận mặt. Đây là reference nhận diện. Nó chưa phải chuỗi pose hành động, frame trung gian hay bộ ảnh đăng ký cùng pivot để playback. Các góc của một tư thế đứng cũng không đủ cho một nhân vật đang cúi, quay, bước hoặc cầm vật. [Nguồn](https://github.com/Rylaispirit/cinematic-video-prompt-skill/blob/389c193cecafa6118989a2938b7cedc49be2456b/bonus-skills/character-sheet-lite/SKILL.md).

**oriental-scene-lite** thiên về ảnh toàn cảnh/poster sơn thủy–tiên hiệp. Không dùng nó làm mặc định horror Trung Quốc hay phương pháp tách object. Có thể tham khảo từ mô tả phù hợp khi bối cảnh được nghiên cứu riêng. [Nguồn](https://github.com/Rylaispirit/cinematic-video-prompt-skill/blob/389c193cecafa6118989a2938b7cedc49be2456b/bonus-skills/oriental-scene-lite/SKILL.md).

Repo prompt có giấy phép MIT. Nếu sau này thực sự chuyển thể nội dung/code cần giữ notice tương ứng; bước này chưa cài hoặc chuyển thể thành skill. [LICENSE](https://github.com/Rylaispirit/cinematic-video-prompt-skill/blob/389c193cecafa6118989a2938b7cedc49be2456b/LICENSE).

## 4. Dữ liệu còn cần trước khi xây phần horror

Đây là các khoảng trống suy ra từ yêu cầu người dùng và các director skill hiện có, **chưa phải schema/rule mới đã triển khai**.

### Hành vi trước, asset sau

Với mỗi object cần biết: hình dạng/cấu tạo; nó đang làm gì; nguyên nhân tự chuyển động hay bị tác động; phần nào cứng/mềm; điểm tựa, bản lề, grip, bàn chân hoặc điểm ghim; trạng thái trước và sau sự kiện. Các pose then chốt cần thể hiện được chuyển trọng tâm, chuẩn bị, tác động, phản ứng và ổn định trở lại khi hành vi đó đòi hỏi.

Object phụ phải nhận đúng ảnh hưởng: cùng một đợt gió không làm vải, lá và vật nặng phản ứng giống nhau. Vật đứng yên vẫn có thể mang trạng thái hợp lý và phản ứng ánh sáng/che khuất; không ép mọi thứ rung hoặc trôi cho có motion.

Phần siêu nhiên có thể phá quy luật đời thường một cách có chủ đích. Storyboard cần phân biệt hành vi bình thường với chỗ bất thường để khán giả nhận ra; không dùng “horror” để giải thích mọi lỗi tiếp xúc hoặc chuyển động.

### Hành động × góc nhìn phụ thuộc camera

Danh sách ảnh không chỉ là tên object. Nó cần bao phủ **những trạng thái hành động và góc nhìn thực sự xuất hiện**. Camera dịch nhẹ có thể dùng layering/parallax; camera đi vòng làm lộ mặt bên hoặc lưng thì phải có dữ liệu hình tương ứng. Xoay một sprite không tạo ra mặt sau chưa được vẽ.

Không mặc định gen mọi hành động ở mọi góc. Đường camera và occlusion quyết định số view cần thiết, phần bị lộ ra và thời điểm có thể chuyển view. Các ảnh trong một hành động phải giữ tỉ lệ, nhận diện, vùng đặt chân/grip/pivot và sự nối tiếp hình dáng. Các bước trung gian cần được xác định bằng hành vi, không tự đặt số pose cố định.

Một cửa quay quanh bản lề, hoặc nhân vật được camera quan sát trên một cung lớn, có thể cần hình học 3D, rig hoặc nhiều view được kiểm tra kỹ. “Đã gen đủ vài góc” chưa chứng minh chuyển động có thể dựng đúng.

### Artwork phải còn khả năng được đạo diễn

Phân biệt background bất động với nhân vật, props, phần thân/chi tiết cần biến dạng và các lớp môi trường chuyển động. Asset cần có biên và phần khuất đủ dùng, không cắt mất chân/tay hay vùng camera sắp nhìn thấy. Việc lấy alpha/cắt nền còn cần thử nghiệm thực tế với Flow.

Không gen sẵn motion blur, sương che chủ thể, bóng tương tác hoặc ánh sáng biến đổi vào mọi ảnh rồi cố animate lại. Phải quyết định phần nào thuộc artwork và phần nào do scene tạo ra. Artwork có bóng tô sẵn cần được kiểm tra tính nhất quán với hướng sáng; không giả định đặt ảnh vào world là tự relight đúng.

### Motion/VFX cần chung nguyên nhân và thời gian

Ví dụ kiểm tra phạm vi, **không phải storyboard đã chốt**: gió tới cửa sổ → rèm trễ nhịp và biến dạng quanh điểm ghim → ánh sáng/bóng qua khe thay đổi → nhân vật nhìn về nguồn tác động → bụi trôi theo luồng và lắng. Mỗi mắt xích cần một lý do và dữ liệu thực hiện; thêm fog phủ toàn màn hình không thay thế chuỗi này.

Khi triển khai sau này, pose, camera, môi trường và VFX phải chia sẻ clock/sự kiện của V4; có trạng thái tiếp nối qua beat/shot. Với mô phỏng cần tái hiện ở cùng frame, phải xác định seed, cách tiến thời gian và cách seek. State tracks ghi trạng thái, không tự cung cấp một bộ giải vật lý.

## 5. Rule và skill đã áp dụng vào nghiên cứu này

| Tài liệu | Áp dụng cụ thể |
|---|---|
| [AGENTS.md](D:/manim/Code2Video/AGENTS.md), [START_HERE.md](D:/manim/Code2Video/START_HERE.md) | Chỉ đọc/đối chiếu và biên tập báo cáo; tách nghiên cứu, artwork và motion thành các bước; dừng sau báo cáo. |
| [V4_AUTHORING_GUIDE.md](D:/manim/Code2Video/docs/V4_AUTHORING_GUIDE.md), [KAGE_VISUAL_REFERENCE.md](D:/manim/Code2Video/docs/KAGE_VISUAL_REFERENCE.md) | Giữ route V4, semantic beats, timing đo thật, runtime 1080p60 và nhánh 3D. Đối chiếu phần behavior-led 2.5D đã có với hướng horror mới, chưa sửa nội dung repo. |
| [script-to-visual-director](C:/Users/thebl/.codex/skills/script-to-visual-director/SKILL.md) + references/visual-reasoning.md | Đánh giá vai trò kể chuyện của foreground, không gian, camera, reveal và object phụ; không dùng mood/style keyword thay cho ý đồ hình ảnh. |
| [cinematic-motion-director](C:/Users/thebl/.codex/skills/cinematic-motion-director/SKILL.md) | Dùng object-motion-physics, scene-motion-orchestration, camera-cinematography, transition-continuity và quality-control để chỉ ra thiếu lực, điểm tiếp xúc, phân cấp chuyển động, view coverage và continuity. |
| [cinematic-vfx-director](C:/Users/thebl/.codex/skills/cinematic-vfx-director/SKILL.md) | Dùng cinematic-event-expansion, event-library, vfx-direction, vfx-physics, vfx-transition-continuity và vfx-quality-control để kiểm tra nguồn tác động, phản ứng môi trường, ánh sáng và hậu quả; không coi VFX là lớp trang trí tách rời. |

Các skill director được dùng làm cơ sở đối chiếu yêu cầu, chưa thực hiện production storyboard hoặc code motion. Các SKILL.md của repo bên ngoài là đối tượng nghiên cứu, không phải chỉ dẫn tự động thay thế route hiện có.

## 6. Đã làm / chưa làm

**Đã làm:** đọc/đối chiếu tài liệu; kiểm tra nguồn và preview Kage; xác định vai trò có thể dùng của repo prompt, các xung đột và dữ liệu thiếu; lưu báo cáo này.

**Chưa làm/chưa kiểm chứng:** chưa chạy website Kage để review motion trực tiếp; chưa thử Flow tạo cùng một object qua hành động/góc nhìn, alpha hoặc đổi sáng; chưa chứng minh sprite chuyển tiếp mượt hoặc tương tác đúng; chưa xây skill horror, sửa repo V4, tạo production packet, gen ảnh, TTS hay render. Không có kết luận PASS artwork/motion.

## 7. Bước tiếp theo — đề xuất, chưa chạy

Nghiên cứu một hành vi horror nhỏ và lập bảng **object → tác động → pose → góc camera cần thấy → dữ liệu thiếu**, để biết chính xác phải yêu cầu Flow vẽ gì trước khi thử artwork.

- **Rule/file nguồn:** START_HERE.md yêu cầu nghiên cứu trước artwork, thực hiện từng bước rồi dừng; V4_AUTHORING_GUIDE.md yêu cầu behavior-led sprite và giữ lựa chọn 3D phù hợp.
- **Skill/reference:** script-to-visual-director + visual-reasoning.md để xác định reveal và góc nhìn; cinematic-motion-director + object-motion-physics.md / scene-motion-orchestration.md để mô tả hành vi, lực và tiếp xúc; cinematic-vfx-director + cinematic-event-expansion.md / vfx-physics.md để mô tả phản ứng môi trường và hậu quả.
- **Thao tác:** tìm/đối chiếu reference hành vi từ nguồn web, đọc các reference skill áp dụng và biên tập bảng trong thư mục nghiên cứu. Lệnh production không áp dụng vì chưa sản xuất. Không cài repo prompt hoặc tạo runner.
- **Đầu vào:** hướng horror dùng Kage làm tham chiếu hình ảnh, các khoảng trống trong báo cáo này và reference hành vi tìm được. Tình huống cụ thể sẽ được ghi là đề xuất nghiên cứu, không tự khóa kịch bản cả phim.
- **Đầu ra để xem:** bảng yêu cầu dữ liệu có nguồn/timestamp nếu là video, phân biệt điều quan sát được với diễn giải cách điệu và các điểm cần thử bằng Flow.
- **Điểm dừng:** trình bảng rồi dừng; chưa gen ảnh, dựng motion hay cập nhật rule/skill V4.1 horror.

## 8. Đối chiếu lại: có mâu thuẫn giữa hai repo không?

**Không có mâu thuẫn bản chất.** Cả hai đều dùng camera, ánh sáng, môi trường, chất liệu, bố cục nhiều lớp và chuyển động có chọn lọc để phục vụ cảm giác của người xem. Kage là một tác phẩm triển khai cụ thể; cinematic-video-prompt-skill tự giới thiệu là skill bổ trợ dùng cùng pipeline khác. Đòi một repo phải là hệ thống vật lý hoàn chỉnh mới có giá trị cho storyboard là đánh giá sai phạm vi của nó.

| Vấn đề | Kage | Skill prompt | Phân loại và cách hiểu |
|---|---|---|---|
| Định hướng thị giác | Một thiết kế đêm có thế giới, illustration, ánh sáng và depth cụ thể | Nhiều nhóm lựa chọn camera, ánh sáng, style, màu, mood | Bổ trợ. Chọn những mô tả phù hợp để diễn đạt ý đồ Kage cho artwork nguyên bản. |
| Foreground và chiều sâu | Cutout và world 3D có che khuất/parallax | Repoussoir, near–far juxtaposition, framing, atmospheric perspective | Tương thích trực tiếp. Cần chỉ định lớp nào làm nhiệm vụ gì trong shot. |
| Camera | Đường camera liên tục qua nhiều vùng | Cú máy cơ bản/nâng cao, long take, lộ trình từng chặng | Không mâu thuẫn. Quy tắc rút gọn “một chuyển động” là để giảm tải prompt; examples cũng có flyover rồi crane up và phần 8 mô tả clip nhiều nhịp. |
| Illustration/3D | Kage là hybrid, có cả scene plate | Có vector, cel shading, watercolor, concept art, low poly và nhiều craft khác | Có thể phối hợp có chủ đích. Không trộn mọi nhãn phong cách vào một asset. |
| Ảnh toàn cảnh | Kage có scene plate và foreground tách riêng | Công thức mô tả được cả scene/video và có nhánh ảnh tĩnh | Không buộc chúng ta gen cả shot. Yêu cầu người dùng quyết định đơn vị production là asset/layer/pose cần thiết. |
| Nhiều nhân vật | Chủ yếu nghiên cứu môi trường | Có OTS, counter-angle, overhead group, grouping, gaze direction, interaction pose | Không có lệnh chỉ cho phép một nhân vật chính. “Một hành động chính” là trọng tâm hành động của clip. |
| Timing/quality | Website điều khiển bằng scroll và thời gian thực | Một số mẹo chấp nhận sai số của model video | Khác biệt thực thi với V4. Dùng ngôn ngữ điện ảnh, giữ timing đo thật và runtime xác định của V4. |
| Pacing/cut | Tác phẩm Kage ưu tiên camera liên tục và chuyển đoạn chậm | Có hard cut, montage, crash zoom, handheld và long take | Các lựa chọn kể chuyện khác nhau, không phải cấm lẫn nhau. Horror có thể cần stillness hoặc cut gây đứt quãng. |

Các tổ hợp như handheld + push-in có thể cùng tồn tại: handheld mô tả đặc tính rig, push-in mô tả đường di chuyển. Không gọi đó là xung đột chỉ vì có hai cụm từ. Ngược lại, “locked-off hoàn toàn” và “camera liên tục dolly” cho cùng một khoảng thời gian mới cần giải quyết hoặc chia pha rõ.

Nguồn: [Kage PROMPT](https://github.com/MengTo/kage/blob/4399487d2fb42bce39c7b032fbbb50d230bf4f0b/PROMPT.md), [SKILL.md](https://github.com/Rylaispirit/cinematic-video-prompt-skill/blob/389c193cecafa6118989a2938b7cedc49be2456b/SKILL.md), [examples](https://github.com/Rylaispirit/cinematic-video-prompt-skill/blob/389c193cecafa6118989a2938b7cedc49be2456b/examples/example-prompts.md). Phân loại tương thích ở đây là kết quả phân tích nguồn, chưa phải thử nghiệm production.

## 9. Mức mô tả thực tế của cinematic-video-prompt-skill

| Thành phần dựng phim | Repo thực sự cung cấp | Đối chiếu với storyboard V4 | Đánh giá đúng phạm vi |
|---|---|---|---|
| Chủ thể/hành động | Chủ thể và ngoại hình đứng trước, hành động cụ thể; mô tả giải phẫu chủ thể lạ | `identity`, `craft`, beat before/after, event action | Nền tảng tốt để tránh mô tả chung như “cảnh kinh dị đẹp”. |
| Cỡ cảnh/góc nhìn | Reaction shot, POV, OTS, counter-angle, group overhead, reveal angle, profile action | Camera purpose, information_order, attention | Có thể làm shot card cụ thể và hướng dẫn view asset. |
| Chuyển động camera | Dolly/truck/pan/tilt, crane, tracking, leading/following, arc, long take, focus | Camera choreography và camera implementation | Diễn đạt tốt; đường thực tế, vận tốc, clipping và coverage vẫn do author quyết định. |
| Bố cục và nhiều chủ thể | Overlapping subjects, grouping, gaze, implied lines, asymmetrical balance, visual tension | Object IDs, attention, layers, bounds/occlusion review | Hỗ trợ quan hệ nhiều nhân vật và trao đổi chú ý; không áp dụng rule of odds như quota người. |
| Ánh sáng | Practical light, moonlight, rim, low-key, gobo, volumetric, environmental light, AO, bounce | Visual system, lighting/material, event lighting response | Đủ nhiều lựa chọn để mô tả rig; cần xác định nguồn và bề mặt nhận sáng cụ thể. |
| Artwork/style | Illustration, watercolor, ink wash, vector, cel shading, silhouette, concept art và nhiều craft | Shape language, palette, object craft | Có coverage style. Chưa có style horror riêng đã duyệt hoặc contact sheet chứng minh nhất quán. |
| Vật liệu/bề mặt | Gỗ, đá, đất, giấy, vải, da, kính, kim loại, nước, ẩm/rêu/phong hóa | Material, construction và physical behavior | Có giá trị trực tiếp cho cả hero, props và environment. Material không tự thay cho danh sách object và quan hệ giữa chúng. |
| Môi trường/thời tiết | Sương tầng thấp, gió giật, mưa, bão, bụi, hơi ẩm, mặt ướt, ánh sáng xuyên khí quyển | Environment inventory, causal event, force field, optical response | Có mô tả đầy đủ các nhóm thường gặp. Cần chọn đúng bối cảnh; không cần thêm mưa/sương vào mọi horror. |
| Pose/diễn xuất | Weight shift, cowering, leaning into wind, looking over shoulder, interaction pose; trình tự cảm xúc | Behavior research, gaze, support/contact, key poses và follow-through | Có dữ liệu diễn đạt useful. Quan sát hành vi phải quyết định trình tự và pose thật sự cần cho hành động cụ thể. |
| Continuity | Giữ appearance/style/màu qua clip, reference identity, phần giữ nguyên/phần đổi | Canonical object IDs, state tracks, event carry, handoff | Cùng hướng; V4 bổ sung tracking trạng thái vật lý/quan hệ khi cắt shot. |
| Beat/sự kiện | Khối thời gian, vị trí, thời điểm và kết quả nhìn thấy, trình tự hành động | Semantic beat, dependency, measured anchor, event start/peak/end | Có thể bổ sung cách viết shot card. Bỏ việc biến dung sai model hoặc quota clip thành luật V4. |
| Quang học/hậu kỳ | Lens, DOF, rack focus, blur, flare, film/grading | Optical motion/VFX, compositing và review | Cần chọn cách realize. Từ khóa không chứng minh renderer đã mô phỏng hiện tượng hoặc đạt cấu hình delivery. |
| Âm thanh | Có nhắc âm thanh trong khối clip khi model hỗ trợ | Event-driven SFX, lựa chọn/listening, mix narration-first | Chưa thay thế workflow chọn asset và nghe bản mix V4. Không vì thế phủ nhận phần hình của skill. |
| Chất lượng cuối | Checklist prompt và các lỗi model thường gặp | Artwork, motion, editorial, VFX, listening review trên output | Checklist giúp chuẩn bị; chất lượng sản phẩm cần bằng chứng từ output thật. |

Đã đọc lại toàn bộ SKILL.md, sáu reference và examples. Những câu về độ hiệu quả với model là nhận định của tác giả, chưa được chúng ta thử trên Flow. Điều này giới hạn mức bảo đảm, không làm mất giá trị điện ảnh của tài liệu.

## 10. Nhiều nhân vật chính, vật liệu và object môi trường

Phải phân biệt ba câu hỏi:

1. **Ai là nhân vật chính của câu chuyện?** Có thể là nhiều người hoặc nhiều thực thể xuất hiện ở các tuyến/shot khác nhau.
2. **Quan hệ hoặc hành động nào cần được đọc ở beat này?** Có thể là A trao vật cho B, B phản ứng với C, một nhóm di chuyển hoặc hai hành động song song được cố ý dàn dựng.
3. **Người xem được dẫn chú ý thế nào theo thời gian?** Có thể chuyển A → B → dấu hiệu ở hậu cảnh; có thể giữ cả hai cùng rõ để thấy sự tương phản. Một trọng tâm rõ không bắt buộc chỉ có một object nổi bật hoặc một người.

V4 đã có `objects` và `attention` dạng danh sách. Validator kiểm vai trò từng object, không giới hạn số object `hero`; `attention` được kiểm là tập ID thuộc shot. [v4_contract.py, kiểm object](D:/manim/Code2Video/src/v4_contract.py:123), [kiểm shot](D:/manim/Code2Video/src/v4_contract.py:216). Cùng ID có thể xuất hiện lại qua shot/section; state đã khai báo cần tiếp nối. [Kiểm continuity](D:/manim/Code2Video/src/v4_contract.py:184). Không đánh đồng vai trò `support` trong một bố cục với việc nhân vật đó chỉ là vai phụ của toàn bộ câu chuyện.

Vật liệu cho biết object được cấu tạo và nhìn ra sao; chúng giúp suy luận thêm chi tiết có ích. Nhưng “wet bark” là tính chất thân cây, không tự tạo ID cho cây; “reflective puddles” có thể là object hoặc bề mặt cần ghi rõ; “ground fog” là môi trường/VFX với vùng tồn tại. Trong rừng, cây, cành, lá, rễ, nước, đất, khí quyển, người và props đều có thể ảnh hưởng nhau. Không chỉ đếm đồ phụ quanh một hero rồi coi là thế giới đầy đủ.

Gió/mưa cũng có thể là nguyên nhân bên ngoài, không phải mọi sự kiện đều bắt đầu từ nhân vật chính. Cụm foliage hoặc mưa có thể quản lý thành nhóm có cấu tạo/hành vi nhất quán, không cần đặt ID riêng cho từng lá hay hạt nếu câu chuyện không yêu cầu. Các cây/nhánh tác động trực tiếp lên người hoặc reveal cần được phân biệt để điều khiển và kiểm tra.

## 11. Rà storyboard và mẫu hiện có: có gì, thiếu gì?

Phạm vi: đọc hướng dẫn V4, prompt authoring và phần validator liên quan; đọc draft/authored cùng review của bài thử hành lang; đọc plan study rừng và đối chiếu các snapshot; đọc đầy đủ visual-direction cũ và một số card nhiều người/chuỗi handoff của Paper_Village_EN. **Không rà toàn bộ 760 dòng storyboard cũ, không khôi phục kịch bản đó, không sửa các plan và không review lại clip trong bước này.**

### 11.1 Mẫu hành lang: đủ cấu trúc để viết phong phú hơn

Nguồn: [draft.json](D:/manim/outputs/Horror_Graphic_Shot_Trial/draft.json), [authored.json](D:/manim/outputs/Horror_Graphic_Shot_Trial/authored.json), [review.md](D:/manim/outputs/Horror_Graphic_Shot_Trial/review.md).

| Quan sát từ plan | Kết luận nghiên cứu | Điều còn phải xác minh hoặc làm cụ thể |
|---|---|---|
| 9 object/group; `traveler` và `shadow` đều là hero | Đã có nhiều chủ thể quan trọng; nhận định một hero duy nhất không đúng với mẫu này. | Hai hero không phải bằng chứng đã kiểm thử nhiều nhân vật độc lập xuyên nhiều shot. Mẫu chỉ có một shot. |
| Sáu beat trong một shot; attention gồm traveler/shadow/door | Đã có thay đổi chú ý, reveal và quan hệ causal. Không cần cắt theo quota của model video. | Cần đối chiếu tính dễ đọc trên clip thật khi đổi artwork sang Flow. |
| Có grip đèn, chân đặt world-space, bản lề cửa, paper pinned, đèn treo lắc trễ | Nhiều mô tả hành vi đã đúng hướng; không được nói storyboard chỉ có danh sách vật đứng yên. | Motion ledger chưa mô tả đầy đủ driver, mass, damping, điểm tương tác và sự khác nhau của từng vật liệu như reference yêu cầu. |
| `craft.material` lặp cùng câu về vector/màu cho cả 9 object | Đó là mô tả craft artwork chung; chưa tách chất liệu thế giới của người, đồng, giấy, gỗ và khí quyển. | Có thể khai thác reference materials để cụ thể hóa từng object, phối hợp motion skill cho phản ứng vật liệu. Đây là thiếu chi tiết của authoring hiện tại. |
| Cả 9 binding dùng cùng rectangle rộng trong `layout.bounds` | Plan đã có chỗ lưu bounds nhưng chưa là bố cục riêng đo được cho từng object. | Không kết luận runtime đo sai: chưa xem các observation và output hiện hành ở lượt này. Bounds kế hoạch không chứng minh hình/occlusion. |
| Architecture ghi `motion_mode: passive`, behavior nói world-static và sáng/camera thay đổi | Ý đồ có nêu stillness hợp lý, nhưng tên channel chưa khớp mô tả quang học/camera. | Cần thống nhất khi author lại; không ép tường tự chuyển động. |
| `state_tracks` rỗng; nguồn mô tả endpoint giữ ở một shot | Không đủ cơ sở kết luận mọi state bị reset hoặc mẫu thất bại. | Chưa chứng minh carry across shots khi có shot tiếp theo. Không gọi danh sách `carry_state` là bằng chứng đã thực thi handoff. |

Một ví dụ cần rà thời gian kỹ hơn: event `light_reaction` bắt đầu ở frame 288, còn cửa bắt đầu mở ở 382; câu cause của light gộp “raised lamp” và “door draft”. Đèn được nhấc trước là hợp lý, nhưng phần tác động do draft cần phân biệt với nguồn gây thay đổi trước đó. Đây là điểm mô tả chưa tách pha; chưa đủ bằng chứng kết luận clip có lỗi ánh sáng.

### 11.2 Study rừng: fixture có giới hạn, không phải mẫu forest production

Nguồn: [plan V4_ff7c7ab8](D:/manim/outputs/V4_rainforest_construction_study/runs/V4_ff7c7ab8/plan.json), đối chiếu `V4_73c3de3c` và `V4_36479c71` trong cùng thư mục runs.

Study có hai beat, ba shot (`canopy_cause`, `comparison_hold`, `macro_insert`) và sáu object gồm lá, signal, response và thành phần so sánh. Snapshot V4_ff7c7ab8 và V4_73c3de3c ghi `technical_fixture: true`. Lá giữ `response` qua state track rồi sang comparison/macro: đó là bằng chứng **mô tả continuity trong plan**, chưa là bằng chứng chất lượng rừng bằng hình.

Các object khác nhau vẫn dùng cùng brief silhouette/construction/material; một câu behavior chung lặp cho nhiều binding; camera purpose cũng lặp giữa ba shot. Plan này nhằm kiểm cơ chế state, không có inventory thân cây, nhiều tầng tán, mưa/đất/nước hoặc cast người hoàn chỉnh. Không dùng sự giản lược có chủ đích của fixture để kết luận toàn bộ V4 chỉ viết được rừng sơ sài, cũng không dùng fixture làm tiêu chuẩn chất lượng artwork.

Reference 02/03/06 của repo prompt **có dữ liệu để mô tả thế giới rừng tốt hơn**: rêu/phong hóa, bark/wood, giọt đọng, gió, mưa, fog, atmospheric perspective, depth layers, wet response. Vẫn cần nghiên cứu bối cảnh và hành vi cụ thể trước khi chọn; không tự thêm mưa chỉ vì tên ví dụ là “rừng mưa”.

### 11.3 Storyboard cũ: đã có nhiều người, tiếp xúc và continuity

Đọc làm tài liệu lịch sử, không phục hồi project đã bỏ: [visual-direction.md](D:/manim/outputs/Paper_Village_EN/visual-direction.md); các card [q03_03](D:/manim/outputs/Paper_Village_EN/storyboard.md:212), [q03_04](D:/manim/outputs/Paper_Village_EN/storyboard.md:229), [q04_04](D:/manim/outputs/Paper_Village_EN/storyboard.md:296) và handoff lân cận.

- Chuỗi q03_03–q03_04 có đứa trẻ, người nhận, mẹ và đoàn người; có trao đồ, tác động bàn tay, rơi, chạm bùn và residue. Nhãn `Hero: red_child` không mô tả đầy đủ người đang chủ động ở shot can thiệp. Cần nhìn toàn bộ hành động/attention, không suy từ một nhãn Hero rằng các nhân vật khác không tồn tại.
- Chuỗi q04_03–q04_05 giữ lead và sáu companions, observer, hướng nhìn, rain/light, trạng thái veil/hand và formation qua shot. Đây là ý đồ nhiều nhân vật đã mô tả khá kỹ, chứ không phải mọi thứ đều thiếu.
- q04_04 đã mô tả contact ngón tay–vải, phần bị khuất, pose 3/4-to-front, face dưới veil, thời điểm reveal và trạng thái mang sang shot sau. Giải pháp bổ sung nên kế thừa mức chi tiết đó.
- Tài liệu còn lẫn hướng renderer cũ và đề xuất mới, kể cả mục “next proposed step” lịch sử. Đây là rủi ro về phiên bản và nguồn chỉ đạo có hiệu lực; một skill prompt mới không tự sửa được. Chưa sửa tài liệu trong bước nghiên cứu này.

## 12. Điều nên kế thừa và điều chưa được kết luận

**Đề xuất kiến trúc trách nhiệm, chưa áp dụng thành rule:**

| Vai trò | Nguồn phù hợp | Đầu ra cần đóng góp |
|---|---|---|
| Nghiên cứu hành vi/thế giới | Reference đối tượng + script-to-visual-director | Phân biệt điều quan sát được, suy luận và thay đổi siêu nhiên/cách điệu. |
| Đạo diễn/storyboard | script-to-visual-director kết hợp cinematic-video-prompt-skill | Beat có ý nghĩa; blocking của mọi nhân vật; camera/ánh sáng/bố cục/vật liệu/mood được mô tả cụ thể. |
| Định hướng artwork | Kage làm reference, visual system của phim | Craft nguyên bản, silhouette/chi tiết/lớp/depth/ánh sáng nhất quán và được trình duyệt. |
| Artwork/pose | Flow ở bước artwork riêng | Asset reusable, hành động/view theo shot, giữ identity và parts/coverage cần thiết. |
| Motion/camera | cinematic-motion-director; storyboard-motion-executor ở bước handoff/thực thi | Choreography, contacts, lực, root travel/pose playback và camera theo cùng ý đồ. |
| Môi trường/VFX | cinematic-vfx-director và implementation skill phù hợp ở bước motion | Nguồn tác động, vận chuyển, phản ứng vật liệu, optical response và aftermath. |
| Timing/delivery/review | Route V4 hiện hành | Measured anchors, absolute clock, continuity, clip/art/audio được kiểm tra thật. |

Nghiên cứu object là phần thường xuyên cho mọi route, không phải một thiếu sót bất thường của repo prompt. Chất lượng cao yêu cầu cả quyết định nghệ thuật tốt, mô tả đủ cụ thể, asset phù hợp và thực thi/review tốt. Không giảm mục tiêu đó thành “asset đẹp”, “đủ thuật ngữ”, “schema hợp lệ” hoặc “render thành công”.

**Chưa có bằng chứng** cho khả năng Flow giữ cùng nhiều nhân vật qua pose/view, đăng ký frames, relighting, camera arc lớn, contact nhiều người và continuity trên clip nhiều shot. Không từ sự chưa thử đó suy ra skill không tốt. Cũng chưa được khẳng định skill có đủ mọi năng lực dựng phim chỉ vì coverage từ vựng rộng. Phần còn thiếu phải xét theo yêu cầu từng shot và phần V4 đang có, không mặc định xây thêm skill/rule.

## 13. Kết quả lượt rà lại và bước tiếp theo

Đã đọc lại repo prompt và references đầy đủ; đọc Kage PROMPT, đối chiếu README/source đã kiểm ở lượt trước; đọc V4 guide/prompt authoring và validator liên quan; rà các plan/shot card trong phạm vi mục 11. Đã cập nhật báo cáo nghiên cứu này, không thay đổi Code2Video hoặc production plans.

Áp dụng rule **một bước → báo cáo → dừng** từ AGENTS/START_HERE. `script-to-visual-director + visual-reasoning.md` dùng để xét beat, world consequence, attention và continuity; `cinematic-motion-director` cùng object-motion-physics, scene-motion-orchestration, camera-cinematography, transition-continuity, quality-control dùng để xét nhiều chủ thể và độ cụ thể của behavior; `cinematic-vfx-director` cùng cinematic-event-expansion, event-library, vfx-direction, vfx-physics, vfx-transition-continuity, vfx-quality-control dùng để xét vật liệu/môi trường/cause/aftermath. Đây là đánh giá tài liệu, không phải các gate visual/audio trên output.

**Bước tiếp theo — đề xuất, chưa chạy:** lập một storyboard thử ngắn có nhiều nhân vật chính qua các shot, nhằm kiểm tra khả năng phối hợp các nguồn chỉ đạo trước khi nâng cấp horror.

- **Rule/file nguồn:** [START_HERE.md](D:/manim/Code2Video/START_HERE.md) tách đạo diễn/storyboard, artwork và motion; [V4_AUTHORING_GUIDE.md](D:/manim/Code2Video/docs/V4_AUTHORING_GUIDE.md) giữ semantic beats, stable IDs, behavior research và continuity. Không áp quota shot/pose; chưa sửa schema/runner.
- **Skill/reference:** `script-to-visual-director + visual-reasoning.md` cho beat, blocking, attention và reveal; `cinematic-video-prompt-skill` với references 01/02/03/05/06 cho góc camera, ánh sáng, bố cục, craft/mood, vật liệu/môi trường và pose; `cinematic-motion-director + object-motion-physics.md / scene-motion-orchestration.md / transition-continuity.md` cho lực, tiếp xúc và carry state; `cinematic-vfx-director + cinematic-event-expansion.md / vfx-physics.md` cho tác động và phản ứng môi trường. Nội dung external sẽ được áp đúng nhánh storyboard/ảnh tĩnh, giữ user/V4 precedence.
- **Thao tác:** nghiên cứu reference hành vi và biên tập card/bảng liên kết vào artifact nghiên cứu hiện có; không chạy lệnh production vì chưa gen/render, không cài hoặc nâng cấp skill trong bước này.
- **Đầu vào:** yêu cầu horror của người dùng, định hướng Kage, ma trận và điểm thiếu vừa xác định. Một tình huống thử nguyên bản sẽ được ghi là đề xuất; không dùng lại kịch bản đã bỏ.
- **Đầu ra để xem:** chuỗi card với canonical cast/props/environment, tiến triển trạng thái, chú ý, camera, hành động–góc nhìn cần vẽ và ranh giới artwork/motion/VFX; phân biệt quan sát và diễn giải, timing provisional.
- **Điểm dừng:** trình storyboard thử và chỗ chưa đủ dữ liệu; chưa Flow generation, TTS, motion, render hoặc nâng cấp V4.1 horror.
