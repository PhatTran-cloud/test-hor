import {renderFrame} from './draw.mjs';
const board=window.DAY47_BOARD;
const stage=document.getElementById('art');
const draw=t=>{const frame=Math.floor(Math.max(0,t)*board.fps+1e-6);stage.innerHTML=renderFrame(board,frame);};
const clock={time:0};
const timeline=window.gsap.timeline({paused:true});
timeline.to(clock,{time:board.duration_frames/board.fps,duration:board.duration_frames/board.fps,ease:'none',onUpdate:()=>draw(clock.time)});
// Capture suppresses GSAP callbacks; explicitly commit SVG after every seek.
const originalTotalTime=timeline.totalTime.bind(timeline);
timeline.totalTime=function(time,suppressEvents){
  if(time===undefined)return originalTotalTime();
  const result=originalTotalTime(time,suppressEvents);
  draw(Number(time));
  return result;
};
window.__timelines=window.__timelines||{};
window.__timelines['day47']=timeline;
window.gsap.ticker.sleep();
draw(0);
window.__renderReady=true;
