"""48k stereo event mix with explicit durations and measured quiet-speech ducking."""
import json
import math
from pathlib import Path
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.ndimage import maximum_filter1d,uniform_filter1d
from scipy.signal import butter,sosfilt,fftconvolve
RATE=48000


def _read_stereo(path):
    raw=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ac','2','-ar',str(RATE),'pipe:1'],capture_output=True,check=True).stdout
    pcm=np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy()
    if not len(pcm) or not np.isfinite(pcm).all(): raise ValueError('Empty/non-finite audio')
    return pcm


def envelope(keys,count,default):
    if not keys: return np.full(count,default,np.float32)
    times=[k['time'] for k in keys]; values=[k['value'] for k in keys]
    if any(not math.isfinite(v) for v in times+values) or times[0]<0 or any(b<=a for a,b in zip(times,times[1:])):
        raise ValueError('Automation needs ordered finite cue-local times/values')
    return np.interp(np.arange(count)/RATE,times,values).astype(np.float32)


def _fit_clip(clip,count,loop):
    if len(clip)>=count: return clip[:count].copy()
    if not loop: raise ValueError('Selected sound/decay shorter than explicit cue duration')
    overlap=min(round(.08*RATE),len(clip)//4); out=clip.copy()
    while len(out)<count:
        if overlap:
            ramp=np.linspace(0,1,overlap)[:,None]
            out[-overlap:]=out[-overlap:]*(1-ramp)+clip[:overlap]*ramp
        out=np.concatenate([out,clip[overlap:]])
    return out[:count]


def mix_narration_with_sfx(narration,output,cues,duration=None,speech_intervals=None):
    voice=_read_stereo(narration); length=max(len(voice),round((duration or 0)*RATE))
    voice=np.pad(voice,((0,length-len(voice)),(0,0)))
    if speech_intervals is not None:
        active=np.zeros(length,bool)
        for start,end in speech_intervals:
            if not 0<=start<end<=length/RATE+1/RATE: raise ValueError('Invalid measured speech interval')
            active[max(0,round(start*RATE)):min(length,round(end*RATE))]=True
        method='measured utterance activity; whisper independent of RMS threshold'
    else:
        rms=np.sqrt(np.maximum(0,uniform_filter1d(np.square(voice.mean(axis=1)),round(.025*RATE))))
        active=rms>max(1e-6,float(rms.max())*.005)
        method='relative waveform fallback; listening required'
    vrms=max(.0001,float(np.sqrt(np.mean(voice[active]**2))) if active.any() else .02)
    activity=maximum_filter1d(active.astype(np.float32),round(.18*RATE)|1)
    activity=uniform_filter1d(activity,round(.03*RATE))
    effects=np.zeros_like(voice); ledger=[]
    for cue in cues or []:
        if 'duration' not in cue or isinstance(cue['duration'],bool) or not isinstance(cue['duration'],(int,float)) or not math.isfinite(cue['duration']) or cue['duration']<=0:
            raise ValueError('Every cue requires an explicit duration; no 8s/default duration')
        if not cue.get('file') or cue.get('source')=='procedural': raise ValueError('Selected local asset required')
        start=round(cue.get('relative_time',0)*RATE); count=round(cue['duration']*RATE)
        if start<0 or count<1 or start+count>length: raise ValueError('Cue onset/tail outside measured film')
        clip=_read_stereo(cue['file']); offset=round(cue.get('asset_offset',0)*RATE); clip=clip[offset:]
        if not len(clip): raise ValueError('Asset offset exceeds WAV')
        clip=_fit_clip(clip,count,cue.get('loop',False))
        lowpass=cue.get('lowpass_hz')
        if lowpass is not None:
            if not 0<lowpass<RATE/2: raise ValueError('Invalid acoustic lowpass cutoff')
            clip=sosfilt(butter(2,lowpass,fs=RATE,output='sos'),clip,axis=0).astype(np.float32)
        if cue.get('impulse_response'):
            ir=cue['impulse_response']; from v4_contract import sha256
            if sha256(ir['file'])!=ir['sha256']: raise ValueError('Acoustic IR changed')
            impulse=_read_stereo(ir['file']); wet=cue.get('reverb_wet',.2)
            if not 0<=wet<=1: raise ValueError('reverb_wet outside 0..1')
            clip=clip*(1-wet)+np.stack([fftconvolve(clip[:,i],impulse[:,i])[:count] for i in range(2)],axis=1)*wet
        gain=envelope(cue.get('gain_keyframes'),count,cue.get('gain_db',-24 if cue.get('role')=='ambience' else -18))
        crms=max(1e-7,float(np.sqrt(np.mean(clip**2)))); clip*=vrms/crms*np.power(10,gain[:,None]/20)
        pan=envelope(cue.get('pan_keyframes'),count,cue.get('pan',0))
        if np.any(np.abs(pan)>1): raise ValueError('Pan outside -1..1')
        clip[:,0]*=np.minimum(1,1-pan); clip[:,1]*=np.minimum(1,1+pan)
        for key,default,reverse in [('fade_in',.012,False),('fade_out',.06,True)]:
            seconds=cue.get(key,default)
            if not math.isfinite(seconds) or seconds<0: raise ValueError('Invalid fade')
            n=min(count//2,round(seconds*RATE))
            if n:
                ramp=np.linspace(0,1,n)[:,None]
                if reverse: clip[-n:]*=ramp[::-1]
                else: clip[:n]*=ramp
        duck_db=cue.get('duck_db',-9)
        if not math.isfinite(duck_db) or duck_db>0: raise ValueError('Ducking cannot boost SFX')
        clip*=np.power(10,activity[start:start+count,None]*duck_db/20)
        effects[start:start+count]+=clip; ledger.append({**cue,'effective_duration':count/RATE})
    mix=voice+effects; peak=float(np.max(np.abs(mix))); attenuation=min(1,.95/max(peak,1e-8)); mix*=attenuation
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True); wavfile.write(output,RATE,mix.astype(np.float32))
    output.with_suffix('.sfx.json').write_text(json.dumps({'rate':RATE,'channels':2,'cues':ledger,'ducking':method,
        'master_attenuation':attenuation,'true_peak_status':'UNVERIFIED','listening_status':'UNVERIFIED'},indent=2),encoding='utf-8')
    return str(output)
