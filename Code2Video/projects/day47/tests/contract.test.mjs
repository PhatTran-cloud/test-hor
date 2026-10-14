import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {CUES,SCRIPT,VIDEO,assertScriptSegmentation} from '../src/script.mjs';
import {buildBoard,shotAt} from '../src/board.mjs';
import {renderFrame} from '../src/draw.mjs';
import {hash,wave,pcmData,parseSrt} from '../tools/voice.mjs';

// Artificial durations are for unit tests only; never emitted as film timing.
let cursor=VIDEO.leadFrames;
const utterances=CUES.map(c=>{const start=cursor;cursor+=180;const u={id:c.id,text:c.text,start_frame:start,end_frame:cursor,pause_frames:Math.round(c.pauseAfter*60),confidence:'test_only'};cursor+=u.pause_frames;return u;});
const timing={...VIDEO,frames:cursor,time_stretch:false,script_sha256:hash(SCRIPT),utterances};
const board=buildBoard(timing);

test('The segmentation retains every supplied word and punctuation in order',()=>{
  assert.equal(CUES.map(c=>c.text).join(' '),SCRIPT.replace(/\s+/g,' '));
  assert.doesNotThrow(()=>assertScriptSegmentation());
  assert.throws(()=>assertScriptSegmentation('A changed script',CUES),/segments differ/);
});
test('Shots cover the whole clock with no gaps; flashbacks are authored',()=>{
  const shots=board.sections[0].shots;let end=0;
  for(const s of shots){assert.equal(s.start_frame,end);assert.ok(s.end_frame>s.start_frame);end=s.end_frame;}
  assert.equal(end,board.duration_frames);
  assert.equal(shots[2].storyboard.transition.relation,'time_jump');
  assert.equal(shots.at(-1).storyboard.transition.relation,'end');
});
test('The return begins exactly four seconds after the last of three sends',()=>{
  assert.equal(board.events.send_frames.length,3);
  assert.equal(board.events.reply_frame-board.events.send_frames.at(-1),240);
  assert.throws(()=>buildBoard({...timing,utterances:utterances.map(u=>u.id==='vo_07'?{...u,start_frame:u.start_frame+1}:u)}),/exactly 4/);
});
test('Random and repeated seeks are stable; frame bounds are clamped',()=>{
  const frames=[90,board.events.gaze_end,10,board.events.blink_peak,90,10];
  const observed=frames.map(f=>hash(renderFrame(board,f)));
  assert.equal(observed[0],observed[4]);assert.equal(observed[2],observed[5]);
  assert.equal(renderFrame(board,-9),renderFrame(board,0));
  assert.equal(renderFrame(board,Infinity),renderFrame(board,board.duration_frames-1));
  assert.equal(shotAt(board,board.events.blink_peak).id,'s13_station_blink');
});
test('The outside blue glove is withheld until the final shot',()=>{
  const shots=board.sections[0].shots;
  for(const s of shots.filter(x=>x.scene_id==='receiver_02')){
    const svg=renderFrame(board,s.start_frame+Math.floor(s.duration_frames*.75));
    assert.equal(svg.includes('data-object-id="glove_01"'),s.id==='s16_knock');
  }
});
test('PCM assembly preserves samples and boundary times',()=>{
  const data=Buffer.from([0,0,1,0,254,255,0,0]);assert.deepEqual(pcmData(wave(data)),data);
  assert.deepEqual(parseSrt('1\n00:00:00,100 --> 00:00:05,303\nNgày 47.\n'),[{start:.1,end:5.303,text:'Ngày 47.'}]);
  assert.throws(()=>pcmData(Buffer.from('not audio')),/Expected PCM/);
});
test('Both engine adapters call the same pure drawing function',async()=>{
  const files=await Promise.all(['remotion.jsx','hyperframes.mjs'].map(f=>readFile(new URL('../src/'+f,import.meta.url),'utf8')));
  for(const source of files)assert.match(source,/import \{renderFrame\} from '\.\/draw\.mjs'/);
});
