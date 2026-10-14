import React from 'react';
import {AbsoluteFill,Audio,Composition,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import board from '../public/board.json';
import {renderFrame} from './draw.mjs';

const Day47=()=>{
  const frame=useCurrentFrame();
  return <AbsoluteFill style={{background:'#060d18'}}>
    <div style={{width:1920,height:1080}} dangerouslySetInnerHTML={{__html:renderFrame(board,frame)}}/>
    <Audio src={staticFile('narration.wav')}/>
  </AbsoluteFill>;
};
const Root=()=> <Composition id="Day47" component={Day47} width={board.width} height={board.height} fps={board.fps} durationInFrames={board.duration_frames}/>;
registerRoot(Root);
