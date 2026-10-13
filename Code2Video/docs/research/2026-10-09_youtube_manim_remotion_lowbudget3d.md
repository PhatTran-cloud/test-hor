**Nghiên cứu niche YouTube và chọn Manim, Remotion, lowbudget3d cho Code2Video**

Thời gian khảo sát: 09–10/10/2026 (Asia/Bangkok). Tài liệu web được truy cập trong lượt nghiên cứu này. Trạng thái: nghiên cứu đã được tích hợp vào Code2Video v3; các kết luận về visual/scientific quality vẫn cần review riêng từng video.

**Kết luận để ra quyết định**

Chọn renderer theo nhiệm vụ của từng shot. Manim là lựa chọn ưu tiên khi người xem cần hiểu một phép biến đổi, một quan hệ hình học hoặc một cơ chế được điều khiển bằng tham số. Remotion là lựa chọn ưu tiên khi video cần phối hợp typography, map, ảnh, footage, UI, dữ liệu và narration trên một timeline. Khi chất lượng object 3D, nhân vật, vật liệu, ánh sáng và camera quyết định trải nghiệm, dùng toàn bộ 3dviz-pro-max + lowbudget3d; Remotion có thể là nơi sắp xếp và xuất các cảnh đó nếu đã giải quyết việc điều khiển thời gian.

Khuyến nghị cho một v3 phục vụ nhiều niche là giữ cả hai engine và có nhánh 3D chuyên biệt. Đây là đề xuất kiến trúc, chưa phải hệ thống đã xây hoặc đã benchmark.

**Phạm vi và phương pháp**

YouTube không có danh mục đóng chứa “tất cả niche”. Category upload, curated topic của API, niche khán giả và format video là các lớp khác nhau. API cung cấp nhóm category/topic ở mức rộng; cộng đồng tạo thêm các phân ngách và giao thoa liên tục. Bản đồ dưới đây là taxonomy sản xuất do em tổng hợp, gồm 48 nhóm và 240 ví dụ phân ngách; không phải danh sách 48 niche chính thức của YouTube. Cơ sở phân loại: [VideoCategories API](https://developers.google.com/youtube/v3/docs/videoCategories/list), [curated topics trong Videos API](https://developers.google.com/youtube/v3/docs/videos), [Explore](https://support.google.com/youtube/answer/9744563?hl=en).

Nghiên cứu kết hợp: nguồn chính thức YouTube; tài liệu Manim, Remotion, Three.js và MapLibre; đọc trực tiếp skill local; đọc cấu hình, storyboard và source của hai pilot El Niño. Đây là đánh giá mức phù hợp kỹ thuật và sản xuất. Không có crawl toàn bộ YouTube, số liệu CPM/RPM, khảo sát thị phần 48 nhóm hoặc thử nghiệm retention của khán giả. Các tuyến công cụ là suy luận sản xuất từ đặc tính cảnh và tài liệu, không phải kết quả đo thắng/thua trên 240 phân ngách.

Nghiên cứu YouTube/NRG tháng 9/2026 mô tả văn hóa phân mảnh, cộng đồng và fandom như những nguồn hình thành nội dung. Điều này hỗ trợ cách nhìn niche theo cộng đồng cụ thể, không chỉ theo category upload. Không suy rộng khảo sát đó thành nhu cầu của mọi quốc gia. [YouTube Culture & Trends 2026](https://blog.youtube/culture-and-trends/youtube-culture-trends-modern-mainstream-research/).

Niche nên được mô tả bằng: chủ đề × nhóm người xem × nhu cầu × format × phong cách. Ví dụ “vũ trụ” còn quá rộng: chứng minh quỹ đạo cho học sinh, kể bí ẩn không gian, đọc tin nhiệm vụ vũ trụ và cinematic planetary journey có yêu cầu hình ảnh rất khác nhau.

**Bản đồ 48 nhóm niche**

M = Manim. R = Remotion. L = toàn bộ 3dviz-pro-max + lowbudget3d, renderer Three.js. MEDIA = footage/ảnh/recording/âm thanh là nội dung nguồn chính. Dấu + thể hiện phối hợp theo shot, không có nghĩa repo hiện đã tích hợp. Tuyến trong bảng giả định sản xuất dạng explainer hoặc video có dựng bằng code; đối với trải nghiệm đời thực, source media vẫn là phần thiết yếu.

| ID | Nhóm niche | 5 ví dụ phân ngách | Ngôn ngữ hình ảnh thường cần | Tuyến ưu tiên | Vai trò của lowbudget3d |
| --- | --- | --- | --- | --- | --- |
| 01 | Toán học | hình học; giải tích; đại số tuyến tính; xác suất; nghịch lý vô hạn | Chứng minh, phép biến đổi, đồ thị, công thức giữ danh tính | M | Mô hình không gian nếu chiều sâu là luận điểm |
| 02 | Vật lý | cơ học; điện từ; sóng; quang học; nhiệt động lực học | Tham số, lực, trường, mặt cắt, đồ thị | M + L khi cần | Máy móc và hiện tượng 3D; solver phải riêng |
| 03 | Thiên văn và vũ trụ | quỹ đạo; hành tinh; sao; hố đen; nhiệm vụ không gian | Scale, hệ quy chiếu, hình học và hero shots | M + R + L | Bề mặt hành tinh, spacecraft, astronaut, camera |
| 04 | Địa lý tự nhiên | sông; sa mạc; núi; bờ biển; phân bố khí hậu | Map, mặt cắt, địa hình, scale | R + M/L | Địa hình hoặc diorama có chiều sâu |
| 05 | Bản đồ và cartography | phép chiếu; đường bay; biên giới; atlas dân số; bản đồ giao thông | GeoJSON, tọa độ, route, nhãn và phép chiếu | R; M cho chứng minh | Globe/terrain nếu shot cần; không thay dữ liệu GIS |
| 06 | Khí tượng và khí hậu | El Niño; bão; gió mùa; jet stream; biến đổi khí hậu | Trường dữ liệu, map, luồng và mặt cắt | R + M + L tùy shot | Mây, biển, địa hình minh họa; không tự có dự báo |
| 07 | Địa chất và đại dương | kiến tạo; núi lửa; động đất; dòng biển; biển sâu | Lát cắt, lớp vật chất, chuyển động không gian | M + L; R dựng | Khối địa chất và đại dương có vật liệu/ánh sáng |
| 08 | Sinh học và sinh thái | tế bào; tiến hóa; di truyền; hệ sinh thái; hành vi động vật | Mạng quan hệ, cấu trúc, quá trình và morphology | R + M/L | Cơ thể, loài vật, habitat; asset đúng loài |
| 09 | Cơ thể và y học giáo dục | giải phẫu; tuần hoàn; thần kinh; miễn dịch; cơ chế thuốc | Giải phẫu, dòng chảy, mặt cắt và nhãn | L + R; M cho cơ chế | Anatomy và biomechanical QA; cần nguồn chuyên môn |
| 10 | Tâm lý và neuroscience | thiên kiến; trí nhớ; chú ý; cảm xúc; nhận thức | Visual metaphor, tình huống, mạng và thí nghiệm | R + M tùy shot | Dùng khi mô hình não/cơ thể có giá trị giải thích |
| 11 | Hóa học và vật liệu | liên kết; phản ứng; điện hóa; polymer; vật liệu nano | Molecule, cấu trúc, năng lượng và phương trình | M + L | Phân tử và cấu trúc vật liệu 3D |
| 12 | Kỹ thuật cơ khí | động cơ; bánh răng; turbine; cầu; cơ cấu truyền động | Exploded view, pivot, constraint và mặt cắt | L + M; R dựng | Assembly, attachment, vật liệu và contact |
| 13 | Điện tử và robotics | mạch; chip; cảm biến; robot; điều khiển | Sơ đồ, state trace, tín hiệu, joint/frame | M + L/R | Robot, cơ cấu và equipment; logic vẫn cần evaluator |
| 14 | Lập trình và thuật toán | sorting; cấu trúc dữ liệu; web dev; cybersecurity; system design | Code, state trace, cây/graph, UI và demo | M cho thuật toán; R cho UI | 3D chỉ khi spatial mechanism thật sự cần |
| 15 | AI và công nghệ số | neural network; LLM; computer vision; AI tools; automation | Tensor/graph, workflow, UI và screen recording | M + R | Không nên 3D hóa mạng chỉ để trang trí |
| 16 | Lịch sử và văn minh | cổ đại; trung đại; khảo cổ; lịch sử quốc gia; lịch sử công nghệ | Timeline, map, tư liệu, tái dựng | R + MEDIA; L tùy shot | Kiến trúc, cổ vật, diorama có nguồn |
| 17 | Quân sự và chiến lược | chiến dịch; chiến thuật; hậu cần; vũ khí lịch sử; chiến lược biển | Map, route, state, địa hình và tư liệu | R + M/L | Tái dựng scale/terrain; phân biệt minh họa với chứng cứ |
| 18 | Chính trị và địa chính trị | thể chế; ngoại giao; bầu cử; thương mại quốc tế; xung đột | Map, timeline, biểu đồ và nguồn phát biểu | R + MEDIA | Spatial shot nếu cần, không lấn át dữ kiện |
| 19 | Luật và xã hội | luật phổ thông; quyền công dân; chính sách; criminology; xã hội học | Tình huống, quy trình, tài liệu và comparison | R | Tái dựng có phạm vi rõ; nguồn pháp lý riêng |
| 20 | Kinh tế học | lạm phát; thị trường; chu kỳ kinh tế; game theory; chuỗi cung ứng | Đồ thị, dòng tiền, network, feedback | M + R | Hoạt động logistics khi không gian giúp hiểu |
| 21 | Tài chính cá nhân | budgeting; lãi kép; nợ; hưu trí; đầu tư cơ bản | Chart, ví dụ tính toán, dashboard | R; M cho cơ chế | Hiếm cần hero 3D; giá trị nằm ở số và giả định |
| 22 | Kinh doanh và doanh nghiệp | case study; startup; quản trị; thương hiệu; vận hành | Timeline, data, asset thương hiệu và causal diagram | R + M tùy shot | Nhà máy/logistics/product khi cần |
| 23 | Marketing và creator economy | SEO; quảng cáo; YouTube strategy; ecommerce; storytelling | UI, funnel, dữ liệu, ví dụ và graphic | R | Product shot phụ nếu có yêu cầu |
| 24 | Kiến trúc và bất động sản | nhà ở; quy hoạch; nội thất; công trình; urbanism | Mặt bằng, walkthrough, section, map | L + R; M phụ | Kiến trúc, scale, ánh sáng, material, camera |
| 25 | Môi trường và năng lượng | năng lượng tái tạo; chất thải; bảo tồn; carbon; nước | Map, flows, process, hạ tầng và số liệu | R + M/L | Cấu trúc hạ tầng và hệ sinh thái |
| 26 | Kinh dị và bí ẩn | cosmic horror; ghost story; analog horror; folklore horror; mystery fiction | Không gian, atmosphere, reveal, nhịp kể | R + MEDIA/L | Môi trường và creature có morphology; cinematic motion |
| 27 | True crime và điều tra | hồ sơ vụ án; missing persons; forensic science; timeline investigation; cold cases | Tài liệu, location, timeline, reconstruction | R + MEDIA; M/L phụ | Reconstruction được nhận diện rõ; không giả chứng cứ |
| 28 | Văn học và kể chuyện | tóm tắt sách; phân tích truyện; mythology; fairy tales; original fiction | Nhân vật, illustration, visual metaphor, world | R + MEDIA/L | Character/world nếu scene cần 3D; không tự tạo acting tốt |
| 29 | Film, anime và fandom | film essay; anime analysis; lore; character breakdown; media history | Footage, illustration, typography và luận điểm | R + MEDIA | Tái dựng hoặc world riêng có mục đích |
| 30 | Gaming | gameplay; walkthrough; esports; game review; game lore | Gameplay, UI, stats, strategy và map | MEDIA + R; M phụ | Dùng cho tái dựng/giải thích cơ chế riêng |
| 31 | Thể thao | bóng đá; bóng rổ; motorsport; combat sports; chiến thuật thi đấu | Footage, tracking, diagram, score và motion | MEDIA + R; M/L phụ | Biomechanics hoặc sân/đường đua có scale |
| 32 | Âm nhạc | music theory; instrument tutorial; production; music history; lyric visualizer | Âm thanh, nốt, waveform, footage và timing | R + MEDIA; M cho theory | Visualizer/world tùy art direction |
| 33 | Mỹ thuật và thiết kế | graphic design; illustration; animation craft; typography; art history | Artwork thật, process, comparison và typography | R + MEDIA | Product/sculpture/material study |
| 34 | Ngôn ngữ và giao tiếp | tiếng Anh; pronunciation; vocabulary; grammar; linguistics | Text, highlight, audio, tình huống và phonetics | R; M cho cấu trúc | Không mặc định 3D; mouth model khi đủ fidelity |
| 35 | Giáo dục trẻ em | đếm số; alphabet; basic science; social skills; puzzles | Character, action rõ, nhịp học và simple shapes | R + M/L theo bài | Character có rig và contact; phụ thuộc asset |
| 36 | Triết học và tôn giáo | tư tưởng; ethics; logic; comparative religion; spiritual history | Visual metaphor, narrative, text và tư liệu | R; M cho logic | Không gian/di sản khi tăng ý nghĩa |
| 37 | Productivity và self-improvement | habits; time management; study skills; motivation; career development | Tình huống, systems, timeline và UI | R | 3D là tùy chọn, thường không phải lõi |
| 38 | Ẩm thực và cooking | recipes; food science; restaurant review; culinary history; nutrition education | Footage thao tác, ingredient, quá trình và text | MEDIA + R; M/L cho khoa học | Food mechanism có thể minh họa; không thay trải nghiệm món |
| 39 | Du lịch và outdoor | destination guide; hiking; backpacking; road trips; survival | Footage thực, route, map, scale và itinerary | MEDIA + R | Terrain/route preview; cần GIS cho vị trí thật |
| 40 | Fitness và movement | strength training; mobility; running; yoga; exercise technique | Demo thực, joint/force overlay, rhythm | MEDIA + R; L/M phụ | Humanoid, anatomy, grounded contact và joint limits |
| 41 | Beauty và thời trang | skincare; makeup; fashion history; styling; product comparisons | Người/sản phẩm thật, trước/sau, texture và text | MEDIA + R | Product/garment nếu asset và cloth đủ tốt |
| 42 | Nhà cửa, DIY và làm vườn | home improvement; woodworking; repairs; gardening; organization | Demo, kích thước, assembly, step order | MEDIA + R; L/M phụ | Exploded view, đồ vật, garden planning |
| 43 | Thú cưng và thiên nhiên hoang dã | pet care; dog training; cat behavior; wildlife facts; animal documentaries | Footage, hành vi, anatomy, habitat | MEDIA + R; L/M phụ | Đúng loài và gait; không suy từ generic quadruped |
| 44 | Vlog, gia đình và quan hệ | daily vlog; parenting; relationships; personal journeys; local lifestyle | Con người thật, trải nghiệm, conversation và pacing | MEDIA + R | Ít cần, trừ illustration/reconstruction có chủ đích |
| 45 | Podcast, phỏng vấn và commentary | expert interviews; conversational shows; debate; news commentary; creator commentary | Người nói, footage, insert, text và timeline | MEDIA + R | Cảnh minh họa độc lập; không thay cuộc phỏng vấn |
| 46 | ASMR, ambience và relaxation | sound triggers; nature ambience; sleep stories; meditation; lo-fi environments | Âm thanh, không gian, chuyển động nhẹ và loop | MEDIA + R; L cho world | Environment đẹp và loop ổn định; audio là lõi |
| 47 | Review và công nghệ tiêu dùng | smartphone review; gadgets; software review; shopping guides; product teardown | Product thật, UI, test, benchmark và comparison | MEDIA + R; L/M phụ | Hero product, exploded view; không thay test sản phẩm |
| 48 | Hobbies, xe và giải trí tổng hợp | collecting; model making; automotive; comedy skits; challenges | Object/people thật, process, action và graphic | MEDIA + R; L/M theo shot | Object riêng, vehicle mechanism, diorama; cần brief cụ thể |

Các giao thoa chưa tách thành hàng riêng vẫn có chỗ trong taxonomy: sustainability travel = 25 + 39; airplane engineering = 12 + 48; aviation route = 05 + 39; chess tactics = 14/35 + 48 tùy audience; space horror = 03 + 26; disaster documentary = 06/07 + format documentary. Nhóm 48 cần phân nhỏ tiếp khi có kênh cụ thể. Phân loại này tối ưu cho chọn công cụ, không phải phân loại văn hóa hoàn hảo.

“Documentary”, “Shorts”, “video essay”, “livestream” và “faceless” là format, có thể cắt ngang nhiều niche. Podcast vừa là một format vừa có hệ sinh thái nội dung riêng nên được giữ thành nhóm thực dụng. Báo cáo YouTube cuối 2025 cho thấy fandom, gaming, music và podcasts cùng tồn tại trong các dạng sáng tạo khác nhau. Không thể suy rằng một renderer phù hợp với toàn bộ category chỉ từ một video nổi bật. [YouTube 2025 summary](https://blog.youtube/culture-and-trends/end-of-year-summary-2025/), [podcasts 2025](https://blog.youtube/news-and-events/podcasts-living-room-in-2025/).

**So sánh chính hai skill đang cài**

| Khía cạnh | manimce-best-practices | remotion-best-practices |
| --- | --- | --- |
| Đối tượng | Manim Community Edition; không phải ManimGL của 3Blue1Brown | Router nhiều module cho authoring, maps, media, Studio và rendering |
| Cách nghĩ chủ đạo | Scene, Mobject, transform, tham số, play và updater | React component, frame, composition, sequence, asset và timeline |
| Bao phủ trực tiếp | Hình học, graph, LaTeX, styling, layout, camera, 3D primitives | Typography, image/video/audio, maps, transition, đo text, data props, 3D integration |
| Toán học | Hướng dẫn MathTex và TransformMatchingTex khá trực tiếp | Cần thêm math renderer và logic morph nếu muốn derivation tinh tế |
| Object 3D phức tạp | Chỉ dẫn 3D cơ bản; không có workflow character/GLB/PBR toàn diện | Có cầu nối Three.js/R3F, nhưng hướng dẫn 3D chủ yếu là runtime contract |
| Audio | Skill không đi sâu narration alignment; repo đã thêm Kokoro riêng | Có audio, voiceover, silence, sequencing; provider ví dụ không bắt buộc |
| Map | Skill thiếu GIS/projection/data pipeline chuyên biệt | Có routing static, MapLibre, MapTiler, Mapbox, Cesium và stability |
| Review | Best practices giúp tránh lỗi; không có đầy đủ domain/art gates | Best practices và Studio không tự chứng minh scientific/art fidelity |
| Vai trò v3 hợp lý | Chuyên gia cảnh mang luận điểm toán/cơ chế | Chuyên gia composition và video có nhiều loại media |

Skill là hướng dẫn; engine là phần mềm; visual direction là công việc sáng tạo. Đọc một skill không tự có asset đẹp hoặc storyboard tốt. Skill Manim không mặc định tạo video “3Blue1Brown”, và skill Remotion không mặc định tạo video “Kurzgesagt”. 3Blue1Brown dùng nhánh Manim riêng, vì vậy các snippet ManimGL không nên chuyển thẳng vào ManimCE. [3b1b/manim](https://github.com/3b1b/manim).

Nguồn local đã đọc: [Manim skill](C:/Users/thebl/.codex/skills/manimce-best-practices/SKILL.md), [Remotion skill](C:/Users/thebl/.codex/skills/remotion-best-practices/SKILL.md). Đã đọc các module liên quan scenes/camera/3D/timing/updaters/text/LaTeX, Remotion markup/3D/maps/interactivity/text measurement/voiceover/multi-scene/render; không sửa skill.

**So sánh engine sâu hơn**

| Nhiệm vụ | Manim | Remotion | Cách chọn |
| --- | --- | --- | --- |
| Hình học và công thức có danh tính | Có object và animation chuyên dụng cho toán | Có thể làm qua SVG/math library nhưng tự author nhiều hơn | M khi chuyển đổi là nội dung cần hiểu |
| Đồ thị và mô hình tham số | Coordinate systems, trackers và Python thuận tiện | D3/JS và data components rất linh hoạt | M cho mechanism; R cho dashboard/editorial chart |
| Artwork 2D tùy chỉnh | Vector, SVG, raster, geometry dựng bằng code | HTML/CSS/SVG/Canvas và asset ecosystem | Art phụ thuộc thiết kế; R thuận phối hợp nhiều loại asset |
| Morph hình/biểu thức | Nhiều transform tích hợp | Interpolation/path morph phải chọn thư viện hoặc tự dựng | M thường tiết kiệm authoring cho toán |
| Typography phức tạp | Pango text + LaTeX, tự kiểm soát bbox/layout | Web font/layout và text measurement tools | R cho typographic composition; cả hai phải kiểm tra font |
| Map dữ liệu thật | Làm được nhưng cần adapter/projection/label strategy riêng | Map libraries và GIS toolchain thuận hơn | R cho map-led story; M cho hình học trên map |
| Kể chuyện bằng ảnh/footage | Có thể đưa ảnh vào scene; dựng media thường qua FFmpeg/custom code | Thành phần media và timeline là đường đi trực tiếp | R khi footage và timing biên tập là lõi |
| Timeline | Sequence play/wait và trạng thái scene theo tiến trình | Frame xác định composition/sequence | R khi cần tua, reposition và phối hợp nhiều layer |
| Căn narration | Có plugin hoặc pipeline tùy chỉnh | Audio + sequence + metadata | Cả hai được; chất lượng phụ thuộc speech/beat alignment |
| Object phụ và causality | Updater/transform phù hợp dependency | Component/state-at-frame phù hợp dependency | Cả hai cần storyboard về quan hệ, không chỉ thêm props |
| Character animation | Không phải tuyến thuận cho rigged hero characters | Dùng Three.js/skinning/GLB khi có asset và clock adapter | L để author/QA; R có thể host |
| 3D khoa học schematic | Native ThreeDScene, axes, surface và camera | ThreeCanvas + Three.js, phải dựng cấu trúc khoa học | M cho shot gọn; L khi hình ảnh/asset quan trọng |
| Cảnh 3D giàu vật liệu/lighting | Ngoài thế mạnh của workflow Manim đang dùng | Tiếp cận ecosystem Three.js nhưng không tự có art direction | L + R hoặc L độc lập tùy delivery |
| Simulation khoa học | Python thuận tích hợp solver; bản thân animation không là simulation | Có thể playback dữ liệu hoặc solver JS có kiểm chứng | Chọn solver trước; renderer theo nhu cầu hình ảnh |
| Tái sử dụng template/data | Python classes/config tốt | Props và React components hợp data-driven variants | R thuận cho nhiều biến thể; không tự giảm công việc nội dung |
| Render performance | Phụ thuộc renderer, geometry, updater, cache và scene complexity | Phụ thuộc browser, media decoding, WebGL/GPU, memory và concurrency | Chưa có benchmark ngang bằng để tuyên bố nhanh hơn |

Các cơ sở kỹ thuật: [MathTex](https://docs.manim.community/en/stable/reference/manim.mobject.text.tex_mobject.MathTex.html), [TransformMatchingTex](https://docs.manim.community/en/stable/reference/manim.animation.transform_matching_parts.TransformMatchingTex.html), [Axes](https://docs.manim.community/en/stable/reference/manim.mobject.graphing.coordinate_systems.Axes.html), [Scene](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html), [Remotion fundamentals](https://www.remotion.dev/docs/the-fundamentals), [Remotion maps](https://www.remotion.dev/docs/maps), [fitText](https://www.remotion.dev/docs/layout-utils/fit-text), [audio](https://www.remotion.dev/docs/using-audio), [transitions](https://www.remotion.dev/docs/transitions), [parameterized rendering](https://www.remotion.dev/docs/parameterized-rendering), [performance](https://www.remotion.dev/docs/performance).

**So sánh 3D đúng đối tượng: Remotion/R3F với toàn bộ lowbudget3d**

lowbudget3d là overlay bổ sung cho toàn bộ 3dviz-pro-max, không thay thế base. Base có workflow sáng tạo, object reasoning, research, catalog, kits, rigs, materials, lighting, state, interaction và validation. Overlay tăng fidelity cho humanoid, animal, prop attachment, runtime hiện đại, optional GPU, cinematic motion và anti-fake-pass. Final rendering mặc định là Three.js; Blender có thể author/export asset, không trở thành renderer cuối cạnh tranh với Three.js trong workflow đó.

Đã xác nhận thư mục base có data/references/templates/kits/scripts, không chỉ SKILL.md. Đã đọc entrypoint, catalog index, kits/scaffold index, motion/state và Blender handoff, cùng các reference của lowbudget3d về ownership, routing, runtime, motion, GPU, humanoid, animal, attachments và anti-fake-pass. Không chạy toàn bộ kit, không tạo asset và không coi catalog coverage là runtime proof.

| Tiêu chí 3D | Remotion + Three.js/R3F, theo skill Remotion | 3dviz-pro-max + lowbudget3d | Ý nghĩa thực tế |
| --- | --- | --- | --- |
| Engine hình ảnh | Three.js được host bằng ThreeCanvas/R3F | Three.js với core scene/runtime | Không có trần đồ họa riêng chỉ do tên Remotion |
| Geometry | Có thể dùng procedural mesh/GLB; skill không giải quyết silhouette sâu | Object reasoning, kits/custom/sourced route, continuity | L hỗ trợ quyết định dựng đúng object |
| Human/astronaut | Chạy được skinned/morph asset; phải tự chọn rig và QA | Skeleton, morphology, suit layers, hands/face và multiple-view QA | L mạnh hơn về quy trình fidelity, không bảo đảm asset tự có |
| Animals/creatures | Có thể load và animate asset | Species morphology, gait, anatomical analogue | L giúp tránh generic animal và sai gait |
| Props/attachments | Parent/transform thông thường | Owner/socket/contact/clearance/motion inheritance | L kiểm tra tính hợp lý của vật đeo/cầm |
| Materials/lighting | Three.js PBR và ánh sáng sử dụng được | Art direction, material scale, rigs, emitter/receiver ownership | L sâu hơn về dựng look; R giữ timing và composition |
| Camera | Frame-driven camera authoring | Reveal/pursue/isolate, scale/parallax và continuity | Kết hợp direction của L với clock của R |
| Secondary motion | Có thể tự code ở frame hiện tại | Causal chain, mass/constraints, lag và energy transfer | L không đồng nghĩa hiệu ứng chạy chung một nhịp |
| Asset sourcing/offline authoring | Loader/asset synchronization | Representation choice, GLB handoff và kiểm tra source→runtime | L tạo quy trình; cần asset cụ thể và quyền sử dụng |
| Time model | Frame bất kỳ phải tái hiện được; scrub được | Elapsed time/stable state, interactive pause/reset; kits có update(dt) | Cần adapter thời gian nếu ghép trực tiếp |
| Simulation | Phải giải quyết deterministic seek/playback | Tách authoritative solver với visual interpolation | L cũng không tự chứng nhận physics/science |
| GPU | Có backend Three.js/WebGPU, tùy hỗ trợ | Chỉ route khi workload/bottleneck cần | Đo rồi chọn; GPU không sửa hình xấu |
| Video/audio export | Composition, narration, transitions và MP4 trực tiếp | Skill thiên về scene/interactive delivery; không có master Kokoro film sẵn | R bổ sung lớp hoàn thiện video |
| Visual QA | Lint/render/Studio là nền kỹ thuật | Runtime, geometry, domain, readability, motion, performance, evidence | Mang gates của L vào film thay vì chỉ kiểm tra MP4 tồn tại |
| Fidelity ceiling | Phụ thuộc asset/shader/material/light/backend đã author | Cũng phụ thuộc các thành phần đó | Cùng nội dung Three.js có thể gần tương đương nếu host/config phù hợp |

Do đó “3D Remotion hay 3D lowbudget3d đẹp hơn?” cần cùng asset, camera, lighting, tone mapping, backend và thời gian. Chưa có A/B đó trên máy. Kết luận chắc hiện tại là **lowbudget3d có hướng dẫn dựng và QA 3D sâu hơn skill Remotion 3D**, còn **Remotion có workflow timeline và film export trực tiếp hơn**. Đó là hai lợi thế bổ sung, không phải kết quả thi đấu hình ảnh đã đo.

Nguồn local: [lowbudget3d](C:/Users/thebl/.codex/skills/lowbudget3d/SKILL.md), [base 3dviz-pro-max](C:/Users/thebl/.codex/skills/3dviz-pro-max/SKILL.md), [ownership](C:/Users/thebl/.codex/skills/lowbudget3d/references/preservation-and-ownership.md), [cinematic motion](C:/Users/thebl/.codex/skills/lowbudget3d/references/cinematic-motion.md), [anti-fake-pass](C:/Users/thebl/.codex/skills/lowbudget3d/references/anti-fake-pass.md).

Nguồn engine: [Remotion Three.js integration](https://www.remotion.dev/docs/three), [ThreeCanvas time contract](https://www.remotion.dev/docs/three-canvas), [R3F Canvas](https://r3f.docs.pmnd.rs/api/canvas), [GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html), [PBR materials](https://threejs.org/docs/pages/MeshStandardMaterial.html).

**Điểm khó nhất nếu sau này kết hợp 3D với Remotion**

Clock và ownership phải được thiết kế trước. Scene interactive có thể chạy tuần tự theo dt; Remotion cần ảnh đúng ở một frame được yêu cầu, kể cả sau khi tua lùi hoặc render frame không theo thứ tự. useFrame/requestAnimationFrame tự chạy, timer thực hoặc random không cố định sẽ làm motion phụ thuộc lịch sử. ThreeCanvas yêu cầu dùng useCurrentFrame cho animation. [ThreeCanvas](https://www.remotion.dev/docs/three-canvas).

Đề xuất adapter, chưa triển khai:

1. Hình học, vật liệu, rig, asset và camera direction của lowbudget3d được giữ nguyên; host video quản lý render tick. Không copy cả standalone app với renderer/scene root/loop thứ hai vào ThreeCanvas.
2. Đổi các motion giải tích sang sample tại thời gian tuyệt đối t = frame/fps, hoặc tương đương dùng phase/seconds rõ ràng. Không mặc định một increment mỗi lần React render.
3. Với GLB animation, sample clip bằng thời gian xác định; AnimationMixer có setTime để nhảy tới thời điểm cụ thể. Blend/action setup vẫn phải kiểm tra khi seek, không chỉ gọi hàm rồi mặc định đúng. [AnimationMixer](https://threejs.org/docs/pages/AnimationMixer.html).
4. Với solver, gait tích lũy, cloth và GPU particle state: dùng dữ liệu precomputed/playback, checkpoint + replay từ trạng thái chuẩn, hoặc một solver có reset và fixed-step thích hợp. t = frame/fps đơn độc không giải quyết history-dependent simulation.
5. Camera spring, exposure adaptation, temporal postprocessing và motion blur phải có lịch sử tái tạo được hoặc chế độ offline ổn định. Hiệu ứng đẹp khi chạy realtime chưa chứng minh render không flicker.
6. Chờ asset/shader/map sẵn sàng trước khi chụp frame; check ánh sáng, color management và backend. [delayRender](https://www.remotion.dev/docs/delay-render).
7. Kiểm tra cùng frame theo forward, backward, random seek và render MP4; kiểm tra continuity của A→B, không chỉ still đẹp.

Có hai tuyến kết hợp đáng xem xét: (A) giữ scene lowbudget3d độc lập, xuất shot có timing xác định rồi đưa media vào Remotion; (B) host các scene component trong ThreeCanvas và viết adapter thời gian. A giảm rủi ro coupling nhưng thêm asset intermediates; B tiện sửa timeline/3D chung nhưng cần engineering và QA cao hơn. Cả hai phải giữ core guidance và một chủ sở hữu duy nhất cho mỗi trách nhiệm. Đây là lựa chọn v3 tương lai, chưa được quyết định tự động.

Tài liệu hiện có ThreeWebGPUCanvas nhưng đánh dấu experimental và có yêu cầu phiên bản/backend. Đây là năng lực có thể nghiên cứu cho workload cụ thể, không phải lý do tự nâng cấp hoặc đổi sang GPU cho mọi scene. [ThreeWebGPUCanvas](https://www.remotion.dev/docs/three-webgpu-canvas).

**Lúc nào dùng gì: quy tắc chọn theo shot**

| Câu hỏi trọng tâm của shot | Chọn trước | Ví dụ |
| --- | --- | --- |
| Người xem phải thấy một quan hệ toán/hình được biến đổi ra sao? | M | Công thức, vector, tiếp tuyến, shortest path, probability geometry |
| Người xem phải hiểu dữ kiện qua map/text/image/UI/footage ra sao? | R | Biên giới, infographic, business case study, history timeline |
| Người xem phải cảm nhận cấu trúc/vật liệu/không gian/acting 3D ra sao? | L | Astronaut, engine assembly, terrain, animal, interior, planetary shot |
| Giá trị nằm ở trải nghiệm, performance hoặc chứng cứ thực tế? | MEDIA + R | Cooking demo, vlog, gameplay, podcast, product benchmark |
| Có cả nhiều loại nhiệm vụ? | Chia theo shot, giữ visual system chung | El Niño: map R, mechanism M, cinematic globe/ocean L |

Manim có thể làm narrative art và Remotion có thể làm mathematics. Tuyến ưu tiên dựa trên chi phí authoring, primitive phù hợp và khả năng kiểm tra; không phải giới hạn bất khả thi của công cụ. Không cần đổi renderer giữa mọi shot: chỉ phối hợp khi lợi ích hình ảnh/giải thích đủ lớn để trả chi phí handoff và continuity.

**Các ví dụ cụ thể cho kênh của đại ca**

Con Kiến Đi Trên Quả Cầu: dùng Manim để dựng tangent, great circle, shortest-path constraint và quan hệ với đường thẳng trong không gian. Nếu cần kiến recognizable, chân bám surface và gait đúng, dùng lowbudget3d cho hero object. Remotion có thể giữ phần montage/narration, không cần tự viết lại mọi công thức.

Khách Sạn Vô Hạn: Manim phù hợp phép gán n→n+1 và n→2n, identity của guest/room và chứng minh. Remotion phù hợp kể chuyện với card, signs, số phòng và typography. lowbudget3d phù hợp corridor có chiều sâu hoặc camera reveal, nhưng dựng hàng nghìn phòng không được thay thế việc diễn giải quy tắc ánh xạ.

El Niño: Remotion phù hợp data/map/labels và comparison; Manim phù hợp thermocline, feedback và parameter-linked diagrams; lowbudget3d phù hợp globe có texture/lighting, ocean cross-section hoặc môi trường nếu chúng tăng hiểu biết. Weather VFX không được giả làm kết quả mô hình khí hậu.

Space horror: lowbudget3d dựng habitat/ship/creature/camera; Remotion dựng nhịp reveal, voice, shot transitions và media. Manim chỉ nên nhận shot phân tích như tín hiệu, tọa độ hoặc scanner nếu logic đó thuộc câu chuyện. Không mặc định bật SFX: preference hiện tại của đại ca là narration-only.

Biên giới và lịch sử địa lý: Remotion + GIS assets là tuyến chính; Manim cho chart/geometry đặc biệt; lowbudget3d cho terrain reconstruction có ích. Dữ liệu coastline không tương đương dữ liệu biên giới lịch sử; provenance và thời điểm phải theo chủ đề.

**Artwork, object phụ và khoảng nghỉ: vấn đề nằm ở đâu?**

Một scene đẹp cần visual thesis, focal hierarchy, visual metaphor, object identity, causal relation và transition có ý nghĩa. Engine không thay bước art direction. Có thể giữ ít object mà kể tốt, hoặc thêm nhiều object nhưng làm giảm clarity. Background phải cung cấp scale, context hoặc câu hỏi; object phụ phải làm visible cause/effect, contact, comparison hoặc motion handoff.

Overlap phải được kiểm tra theo thời gian và camera, không chỉ frame đầu. Cả hai engine cần vùng text/primary object được bảo vệ, bbox theo font thật, depth/occlusion rules và inspection ở các điểm chuyển trạng thái. Remotion có công cụ đo text, nhưng SVG label/manual positioning vẫn có thể đè nhau. Manim có positioning/bounds, nhưng animation/camera cũng có thể phá layout ban đầu.

Pause dài và scene đều đặn 30 giây là lựa chọn timeline/storyboard, không phải giới hạn Manim. Remotion cũng có thể có pause dài nếu duration đặt sai. Nên chia scene theo thay đổi luận điểm, không gian, attention target hoặc state quan trọng; chia thành shot/beat ngắn trong một scene nếu cần. Thời lượng phải theo measured narration và comprehension, không cố nhồi đúng 3 phút. Hướng dẫn YouTube cũng đề nghị phân tích format/audience/budget, retention và video length của chính kênh. [YouTube content strategy](https://support.google.com/youtube/answer/13616340?hl=en).

**Điểm cần lưu ý ở skill hiện tại**

1. Manim skill gợi ý preview -ql/-qm; preference của repo luôn 1920×1080 60fps ghi trong AGENTS.md. Khi làm ở repo phải ưu tiên cấu hình đó, kể cả preview. Skill Remotion cũng có ví dụ still scale=0.25; dự án của đại ca cần kiểm tra layout ở đúng delivery resolution.
2. Manim đang cài 0.19.0; tài liệu stable em đọc hiện có 0.22.0. Skill không là bằng chứng mọi snippet của stable chạy trên local. Remotion project pin 4.0.534, skill khai báo 4.0.520; từng API/module mới cần kiểm tra theo installed packages. Không nâng phiên bản trong lượt nghiên cứu.
3. Remotion map router nói MapLibre không có 3D buildings và “fully free”. Đây là shortcut không nên dùng làm kết luận engine: MapLibre có ví dụ fill-extrusion buildings chính thức; dữ liệu/styles/tiles và nhà cung cấp là quyết định riêng. Technique local đang chủ động scope tuyến 2D deterministic, không đại diện toàn bộ MapLibre. [MapLibre 3D buildings](https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/).
4. Voiceover guide dùng ElevenLabs làm ví dụ và cho phép provider khác. Với đại ca tiếp tục Kokoro Docker am_michael; Remotion không bắt buộc ElevenLabs, không cần phát sinh API provider mới.
5. Skill layout có ví dụ size cho composition 1080px-wide. Video hiện tại rộng 1920 và cao 1080; không copy máy móc hoặc coi 1080p đồng nghĩa width=1080. Dùng hierarchy/readability ở frame thực tế.
6. Inline styles/literal keyframes trong Remotion skill nhằm hỗ trợ Studio editing. Không có nghĩa mọi biểu thức shader/camera/solver phải biến thành literals hoặc bỏ design tokens. Cần cân bằng editability với logic chung có một nguồn dữ liệu.
7. lowbudget3d yêu cầu Three.js final rendering theo mặc định. Chỉ đọc skill và dùng vài quy tắc trong Manim không chứng minh đã triển khai đầy đủ workflow Three.js. Bản El Niño Manim đang có 3D native, không phải benchmark toàn bộ lowbudget3d.
8. lowbudget3d catalog và kit tiers là coverage/candidate guidance, không tự chứng minh hero quality. Một kit chạy được hoặc một screenshot đẹp không đủ thay kiểm tra domain, geometry, motion và evidence.

Chi phí vận hành cũng có phần ngoài render: thư viện, asset authoring, QA và điều kiện license. Manim phát hành MIT; Remotion dùng license riêng, nên lựa chọn production phải đối chiếu với mô hình sử dụng và quy mô thực tế tại thời điểm triển khai. Không suy từ việc trial render thành kết luận về license cho mọi business. [Manim license](https://github.com/ManimCommunity/manim/blob/main/LICENSE), [Remotion license](https://www.remotion.dev/license).

**Những gì hai bản El Niño thực sự chứng minh**

| Bằng chứng local | Manim pilot | Remotion trial |
| --- | --- | --- |
| Cấu hình | 1920×1080, 60fps | 1920×1080, 60fps |
| Thời lượng | 181.883333 giây, 10.913 frame | 36 giây, 2.160 frame |
| Audio | Kokoro narration, không SFX/music/subtitles | Visual-only, không audio |
| Globe | Manim Sphere/ThreeDScene | d3-geo orthographic SVG 2D |
| Nhịp | Scene theo narration tự nhiên | 6 đoạn cố định 6 giây |
| Phạm vi | Pipeline hoàn chỉnh đã có file verification | Thử React/SVG composition độc lập |

Manim verification có full_decode=passed và khoảng im lặng giữa narration scene khoảng 0,427–0,451 giây. Remotion source không cài three/@remotion/three và không dùng ThreeCanvas. Vì vậy so sánh cũ chỉ cho phép nhận xét hai sản phẩm đó, chưa cho phép tuyên bố Manim mạnh hơn Remotion 3D hoặc lowbudget3d.

Bằng chứng: [Manim verification](D:/manim/Code2Video/outputs/elnino/verification.json), [Manim scene source](D:/manim/Code2Video/local_tools/pilot_elnino/section_5.py), [Remotion composition](D:/manim/remotion_elnino_trial/src/Composition.tsx), [Remotion dependencies](D:/manim/remotion_elnino_trial/package.json), [trial brief](D:/manim/remotion_elnino_trial/BRIEF.md).

**Đề xuất v3 đang chờ lệnh**

Đề xuất một storyboard trung lập engine ở cấp shot/beat. Mỗi shot giữ visual thesis/metaphor, narration cues, object identities, causal behaviors, camera states, label zones, entry/exit continuity và dữ liệu nguồn. Renderer là quyết định downstream theo nhiệm vụ của shot; không để planner nghĩ mọi kiến thức đều phải là mobjects hoặc mọi scene đều phải là HTML panel.

Ba năng lực sẽ có vai trò rõ: Manim cho mathematical/mechanism shots; Remotion cho editorial/map/media composition và master timeline khi phù hợp; lowbudget3d cho 3D fidelity với đầy đủ base core. lowbudget3d không phải renderer thứ ba thay Three.js, và Remotion không sở hữu art direction 3D chỉ vì nó đang host canvas.

Không thể đạt đẹp bằng cách chỉ thêm key renderer vào plan. Trước khi triển khai cần chọn tuyến handoff 3D, contracts thời gian và kiểm tra continuity; mọi scene cần cho người xem hiểu hoặc cảm được điều gì cụ thể.

Giữ các preference đã chốt: 1920×1080 60fps, narration Kokoro English am_michael, không burn subtitle, mặc định không music/SFX, không cố định 3 phút, khoảng nghỉ scene dưới một giây; em trong chat author/review, không tạo Codex CLI LLM adapter.

Benchmark tương lai nên có cùng script/voice/timing/asset và delivery settings: một math transform, một map story, một 3D hero object, một creature/astronaut motion và một physics playback. Đánh giá riêng clarity, domain correctness, artwork, seek determinism, temporal continuity, audio alignment, render time, memory và công sửa. Mẫu 3D nên so lowbudget3d standalone với scene tương đương được host trong Remotion; Manim schematic là đối chứng riêng, không ép làm realistic character để lấy điểm thấp. Chưa chạy benchmark này.

Trạng thái sau nghiên cứu: chỉ tạo tài liệu và bảng CSV ở D:/manim/research; không sửa repo, skill, dependency, storyboard, renderer hoặc video. Chờ lệnh nâng cấp v3 của đại ca.
