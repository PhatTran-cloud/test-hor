import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {writeFile,rename,rm} from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import {OUTPUT,run} from './voice.mjs';
import {renderFrame} from '../src/draw.mjs';

// A Chrome-free review export of the same JS drawings, explicitly not an
// encoded-output PASS for the Remotion or Hyperframes browser adapters.
export async function rasterPreview(board) {
  const output=path.join(OUTPUT,'day47-animatic.mp4'),pending=path.join(OUTPUT,'day47-animatic.pending.mp4');
  const child=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(board.fps),'-i','pipe:0','-i',path.join(OUTPUT,'narration.wav'),'-frames:v',String(board.duration_frames),'-t',String(board.duration_frames/board.fps),'-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',pending],{stdio:['pipe','ignore','pipe']});
  let stderr='';child.stderr.on('data',d=>{stderr=(stderr+d.toString()).slice(-8192);});
  const finished=new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',code=>code===0?resolve():reject(new Error(`FFmpeg preview failed (${code}): ${stderr}`)));});
  finished.catch(()=>{});
  let lastSvg='',png,lastPercent=-1;
  try {
    for(let frame=0;frame<board.duration_frames;frame++) {
      const svg=renderFrame(board,frame).replace(/ data-frame="\d+"/,'');
      if(svg!==lastSvg){png=await sharp(Buffer.from(svg)).png({compressionLevel:1}).toBuffer();lastSvg=svg;}
      if(!child.stdin.write(png))await once(child.stdin,'drain');
      const percent=Math.floor(frame/board.duration_frames*10)*10;
      if(percent!==lastPercent){lastPercent=percent;console.log(`JavaScript raster preview ${percent}%`);}
    }
    child.stdin.end();await finished;await rename(pending,output);
  }catch(error){child.kill('SIGTERM');await rm(pending,{force:true});throw error;}
  const {stdout}=await run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output]);
  const probe=JSON.parse(stdout),video=probe.streams.find(s=>s.codec_type==='video');
  if(video.width!==1920||video.height!==1080||video.avg_frame_rate!=='60/1'||Number(video.nb_frames)!==board.duration_frames||!probe.streams.some(s=>s.codec_type==='audio'))throw new Error('Preview does not match the measured voice clock');
  await writeFile(path.join(OUTPUT,'preview-probe.json'),JSON.stringify({producer:'javascript-svg-raster-preview',browser_adapter_review:'UNVERIFIED',probe},null,2)+'\n');
  console.log(output);
}
