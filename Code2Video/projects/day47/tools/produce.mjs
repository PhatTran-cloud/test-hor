import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {prepareVoice,PROJECT,OUTPUT,run} from './voice.mjs';
import {makeBoard,makeStills,makeHyperframes,loadTiming,j} from './board-output.mjs';
const require=createRequire(import.meta.url);
let cachedBundle;

async function rendererProject() {
  if(!cachedBundle){const {bundle}=await import('@remotion/bundler');cachedBundle=await bundle({entryPoint:path.join(PROJECT,'src/remotion.jsx'),publicDir:path.join(PROJECT,'public'),outDir:path.join(OUTPUT,'remotion-bundle')});}
  const {selectComposition}=await import('@remotion/renderer');
  const composition=await selectComposition({serveUrl:cachedBundle,id:'Day47',browserExecutable:process.env.CHROME_BIN});
  return {serveUrl:cachedBundle,composition,browserExecutable:process.env.CHROME_BIN};
}

async function render(board) {
  await loadTiming();
  const {renderMedia}=await import('@remotion/renderer'),project=await rendererProject();
  let last=-1;
  const outputLocation=path.join(OUTPUT,'day47-remotion.mp4');
  await renderMedia({...project,codec:'h264',crf:19,x264Preset:'fast',pixelFormat:'yuv420p',outputLocation,concurrency:2,onProgress:p=>{const percent=Math.floor(p.progress*100/10)*10;if(percent!==last){last=percent;console.log(`Remotion ${percent}%`);}}});
  const {stdout}=await run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',outputLocation]);
  const probe=JSON.parse(stdout),video=probe.streams.find(x=>x.codec_type==='video'),audio=probe.streams.find(x=>x.codec_type==='audio');
  if(video.width!==1920||video.height!==1080||video.avg_frame_rate!=='60/1'||Number(video.nb_frames)!==board.duration_frames||!audio)throw new Error('Encoded video does not match measured storyboard');
  await writeFile(path.join(OUTPUT,'render-probe.json'),j(probe));
  console.log(outputLocation);
}

async function hyperframes(board) {
  const dir=await makeHyperframes(board);
  const packagePath=require.resolve('hyperframes/package.json'),pkg=JSON.parse(await readFile(packagePath,'utf8'));
  const cli=path.resolve(path.dirname(packagePath),typeof pkg.bin==='string'?pkg.bin:pkg.bin.hyperframes);
  const env={...process.env,HYPERFRAMES_NO_TELEMETRY:'1',HYPERFRAMES_NO_UPDATE_CHECK:'1'};
  const lint=await run(process.execPath,[cli,'lint',dir,'--json'],{env,maxBuffer:2**20});
  console.log(lint.stdout);await writeFile(path.join(OUTPUT,'hyperframes-lint.json'),lint.stdout);
  const result=await run(process.execPath,[cli,'render',dir,'--fps','60','--workers','2','--quality','standard','--output',path.join(OUTPUT,'day47-hyperframes.mp4')],{env,maxBuffer:8*2**20,timeout:45*60*1000});
  console.log(result.stdout);
}

const action=process.argv[2];
if(action==='voice')await prepareVoice();
else if(action==='all') {await prepareVoice();const board=await makeBoard();await makeStills(board);await makeHyperframes(board);await render(board);}
else if(['board','stills','render','hyperframes','raster-preview'].includes(action)){const board=await makeBoard();await makeHyperframes(board);if(action==='stills')await makeStills(board);if(action==='render')await render(board);if(action==='hyperframes')await hyperframes(board);if(action==='raster-preview'){const {rasterPreview}=await import('./raster-preview.mjs');await rasterPreview(board);}}
else throw new Error(`Unknown action: ${action}. Use voice, board, stills, render, hyperframes, raster-preview or all.`);
