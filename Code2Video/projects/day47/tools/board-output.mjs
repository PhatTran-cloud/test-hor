import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {PROJECT,OUTPUT,hash,pcmData} from './voice.mjs';
import {SCRIPT,CUES,VIDEO,assertScriptSegmentation} from '../src/script.mjs';
import {buildBoard} from '../src/board.mjs';
import {renderFrame} from '../src/draw.mjs';
const require=createRequire(import.meta.url);
export const j=value=>JSON.stringify(value,null,2)+'\n';
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export async function loadTiming() {
  assertScriptSegmentation();
  const timing=JSON.parse(await readFile(path.join(OUTPUT,'voice-timing.json'),'utf8'));
  const audio=await readFile(path.join(OUTPUT,'narration.wav'));
  if(timing.script_sha256!==hash(SCRIPT)||timing.audio_sha256!==hash(audio)||pcmData(audio).length/2!==timing.frames*VIDEO.sampleRate/VIDEO.fps)throw new Error('Stale or altered measured narration; run voice again');
  if(timing.utterances.map(u=>u.text).join(' ')!==CUES.map(u=>u.text).join(' '))throw new Error('Measured takes do not match the locked script');
  return timing;
}

export async function makeBoard() {
  const timing=await loadTiming(),board=buildBoard(timing);
  await mkdir(path.join(PROJECT,'public'),{recursive:true});
  for(const file of [path.join(PROJECT,'storyboard.json'),path.join(OUTPUT,'storyboard.json'),path.join(PROJECT,'public/board.json')])await writeFile(file,j(board));
  await copyFile(path.join(OUTPUT,'narration.wav'),path.join(PROJECT,'public/narration.wav'));
  const shots=board.sections[0].shots;
  const rows=shots.map(s=>`| ${s.id} | ${(s.start_frame/60).toFixed(2)}–${(s.end_frame/60).toFixed(2)} | ${s.title} | ${s.storyboard.primary_action} | ${s.storyboard.information.reveal_ceiling} |`).join('\n');
  const md=`# NGÀY 47 — Storyboard có lời đọc\n\n${board.duration_frames} frame, ${(board.duration_frames/60).toFixed(3)} giây, 1920×1080 / 60 fps. ${shots.length} shot; Edge TTS vi-VN-NamMinhNeural, rate -8%, pitch -6 Hz. Không kéo giãn âm thanh.\n\nGiữ nguyên kịch bản người dùng. Nhân vật chỉ lộ găng tay và POV; không suy ra tuổi/diện mạo từ giọng. Tranh SVG gốc vẽ bằng JavaScript; Remotion và Hyperframes dùng cùng hàm renderFrame.\n\n| Shot | Giây | Chức năng | Hình / hành động | Trần tiết lộ |\n| --- | --- | --- | --- | --- |\n${rows}\n\n## Các nối cảnh quan trọng\n\n- Mở DAY 47, sau đó lùi về lần thử đầu DAY 00; không thêm lời kể.\n- HELLO thứ ba tại frame ${board.events.send_frames[2]}; RX tại frame ${board.events.reply_frame}: chênh đúng 240 frame / 4.000 giây.\n- Đá → co đồng loạt → mắt: cùng belt_01, giữ thứ tự góc và vị trí trạm ở bên trong.\n- Hai góc nhìn chớp mắt dùng một sự kiện frame ${board.events.blink_close}–${board.events.blink_open}; cắt trong lúc đóng, mở lại ở ngoài trạm.\n- Găng xanh/cổ tay hổ phách ở đầu trở thành găng bên ngoài cửa ở cuối; găng người nhận màu đất để tránh nhầm. REPLY không được bấm.\n\n## Giới hạn khoa học và kiểm tra\n\n4 giây là thời gian đi và về. D = c × 4 / 2 = 599584.916 km, làm tròn 600000 km nếu thứ trả lời đáp ngay; nếu có độ trễ xử lý, đây là cận trên theo giả định đường truyền trực tiếp. “Ngôi sao gần nhất” được hiểu là ngoài Mặt Trời ở gần hệ Mặt Trời, không là khẳng định ở mọi vị trí trạm. Vành đai/mắt/chớp mắt là hư cấu, không mô phỏng hấp dẫn số.\n\nNguồn: [NIST](https://physics.nist.gov/cuu/Constants/Value/c.html), [NASA](https://science.nasa.gov/mission/hubble/science/science-behind-the-discoveries/time-travel-observing-cosmic-history/), [Edge TTS](https://github.com/rany2/edge-tts), [Remotion](https://www.remotion.dev/docs/the-fundamentals), [Hyperframes](https://hyperframes.app/docs/2-concepts/3-frame-adapters).\n\nMốc nội bộ co vành đai/đổi gaze là nhịp biên tập trong đoạn đo, không gắn nhãn word alignment. Boundary Edge là metadata dịch vụ, không là kiểm tra bằng nghe. Nhạc và SFX để trống có chủ ý. Không có phụ đề cháy hoặc HUD trang trí. Kiểm tra cấu trúc, khung hình render và nghe giọng ghi riêng trong REVIEW.md; đây là storyboard để duyệt, chưa phải phim đã release.\n`;
  await writeFile(path.join(PROJECT,'STORYBOARD.md'),md);await writeFile(path.join(OUTPUT,'STORYBOARD.md'),md);
  console.log(`Board: ${shots.length} shots / ${(board.duration_frames/60).toFixed(3)} seconds`);
  return board;
}

export async function makeHyperframes(board) {
  const dir=path.join(OUTPUT,'hyperframes');await mkdir(dir,{recursive:true});
  const {build}=await import('esbuild');
  await build({entryPoints:[path.join(PROJECT,'src/hyperframes.mjs')],bundle:true,format:'iife',outfile:path.join(dir,'frame.js'),target:'chrome120'});
  const frameSource=(await readFile(path.join(dir,'frame.js'),'utf8')).replace(/<\/script/gi,'<\\/script');
  await copyFile(require.resolve('gsap/dist/gsap.min.js'),path.join(dir,'gsap.min.js'));
  await copyFile(path.join(OUTPUT,'narration.wav'),path.join(dir,'narration.wav'));
  const duration=board.duration_frames/board.fps;
  const content=`<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Ngày 47</title><style>*{box-sizing:border-box;margin:0}html,body{width:1920px;height:1080px;overflow:hidden;background:#060d18}#root,#art{width:1920px;height:1080px;position:relative}audio{display:none}</style></head><body><div id="root" data-composition-id="day47" data-start="0" data-duration="${duration}" data-width="1920" data-height="1080"><div id="art" class="clip" data-start="0" data-duration="${duration}" data-track-index="0"></div><audio id="narration" data-start="0" data-duration="${duration}" data-track-index="1" data-volume="1" src="narration.wav"></audio></div><script src="gsap.min.js"></script><script>window.DAY47_BOARD=${JSON.stringify(board).replace(/</g,'\\u003c')};</script><script src="frame.js"></script></body></html>`;
  await writeFile(path.join(dir,'index.html'),content.replace('<script src="frame.js"></script>',`<script>${frameSource}</script>`));
  return dir;
}

export async function makeStills(board) {
  const {default:sharp}=await import('sharp');
  const dir=path.join(OUTPUT,'panels');await mkdir(dir,{recursive:true});
  const shots=board.sections[0].shots,panels=[];
  for(const shot of shots) {
    let frame=Math.min(shot.end_frame-1,Math.round(shot.start_frame+shot.duration_frames*.68));
    if(shot.view==='send')frame=board.events.send_frames[1]+14;
    if(shot.view==='look')frame=board.events.gaze_end+10;
    if(shot.view==='blink')frame=shot.end_frame-4;
    if(shot.view==='warning')frame=shot.start_frame+16;
    const file=path.join(dir,shot.id+'.png');
    await sharp(Buffer.from(renderFrame(board,frame))).png().toFile(file);
    panels.push({shot,frame,file});
  }
  const cards=[];
  for(let i=0;i<panels.length;i++) {
    const {shot,frame,file}=panels[i];
    const tile=await sharp(file).resize(460,259).toBuffer();
    const caption=Buffer.from(`<svg width="460" height="56" xmlns="http://www.w3.org/2000/svg"><rect width="460" height="56" fill="#101e2a"/><text x="13" y="23" font-family="DejaVu Sans,sans-serif" font-size="16" fill="#c3e0d9">${shot.id} · ${esc(shot.title)}</text><text x="13" y="45" font-family="DejaVu Sans Mono,monospace" font-size="12" fill="#8ea4a8">${(shot.start_frame/60).toFixed(2)}–${(shot.end_frame/60).toFixed(2)}s | f${frame}</text></svg>`);
    cards.push({input:tile,left:30+(i%4)*474,top:95+Math.floor(i/4)*329},{input:caption,left:30+(i%4)*474,top:354+Math.floor(i/4)*329});
  }
  const header=Buffer.from(`<svg width="1920" height="75" xmlns="http://www.w3.org/2000/svg"><text x="31" y="44" font-family="DejaVu Sans,sans-serif" font-size="30" fill="#c3e0d9">NGÀY 47 · STORYBOARD / ${shots.length} SHOTS</text><text x="31" y="66" font-family="DejaVu Sans,sans-serif" font-size="14" fill="#8ea4a8">Edge TTS · ${(board.duration_frames/60).toFixed(2)} giây · 1920×1080 / 60 fps · tranh JavaScript / SVG · bản duyệt</text></svg>`);
  await sharp({create:{width:1920,height:1430,channels:4,background:'#071422'}}).composite([{input:header,left:0,top:0},...cards]).png().toFile(path.join(OUTPUT,'day47-storyboard.png'));
  const html=`<!doctype html><html lang="vi"><meta charset="utf-8"><title>Ngày47 · Storyboard</title><style>body{margin:0;background:#071422;color:#c3e0d9;font:16px system-ui;padding:32px}main{max-width:1450px;margin:auto}header{margin-bottom:30px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:26px}article{background:#101e2a;padding:16px;border-radius:12px}img{width:100%}small{color:#8ea4a8}p{line-height:1.5}audio{width:100%}@media(max-width:900px){.grid{grid-template-columns:1fr}}</style><main><header><h1>NGÀY 47</h1><p>${shots.length} shot · ${(board.duration_frames/60).toFixed(3)} giây · lời kể giữ nguyên · giọng Edge TTS đo thực tế.</p><audio controls src="narration.wav"></audio><p>Bản storyboard/animatic để duyệt. Giọng chưa được phê duyệt bằng nghe; nhạc và SFX để trống có chủ ý.</p></header><section class="grid">${panels.map(({shot,frame})=>`<article><img src="panels/${shot.id}.png" alt="${esc(shot.title)}"><h2>${shot.id} · ${esc(shot.title)}</h2><small>${(shot.start_frame/60).toFixed(2)}–${(shot.end_frame/60).toFixed(2)} giây · panel f${frame}</small><p>${esc(shot.storyboard.primary_action)}</p><p>${esc(shot.narration_ids.map(id=>CUES.find(c=>c.id===id).text).join(' '))}</p><small>${esc(shot.storyboard.information.reveal_ceiling)}</small></article>`).join('')}</section></main></html>`;
  await writeFile(path.join(OUTPUT,'storyboard.html'),html);
  await writeFile(path.join(OUTPUT,'panel-index.json'),j(panels.map(({shot,frame})=>({id:shot.id,frame,file:`panels/${shot.id}.png`}))));
  console.log(`Drawn panels: ${shots.length}`);
}
