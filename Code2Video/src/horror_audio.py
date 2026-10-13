"""Explicit SFX stage and film-wide measured voice/event assembly."""
import copy
import json
from pathlib import Path
import subprocess
import numpy as np
from scipy.io import wavfile
from gpu_lifecycle import audio_stage
from v4_contract import sha256


def prepare_sfx(plan,base,folder):
    from horror_contract import validate_sfx_brief
    result=copy.deepcopy(plan); folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    requests=[]
    for section in result['sections']:
        for cue in section['sfx_cues']:
            validate_sfx_brief(cue)
            requests.append({'key':section['id']+'__'+cue['id'],'generation':cue['generation']})
    if not requests: raise ValueError('No SFX requests; intentional silence does not load a model')
    path=folder/'sfx_requests.json'; path.write_text(json.dumps(requests,indent=2),encoding='utf-8')
    with audio_stage('sfx',folder) as config:
        subprocess.run([config['small_sfx']['python'],str(Path(__file__).with_name('small_sfx_cuda.py')),
                        str(path),str(folder/'sfx'),config['small_sfx']['weights']],check=True)
    for section in result['sections']:
        for cue in section['sfx_cues']:
            path=folder/'sfx'/(section['id']+'__'+cue['id']+'.wav')
            cue.update(file=str(path.resolve()),source='model_generated',
                       provenance=json.loads(path.with_suffix('.json').read_text(encoding='utf-8')),
                       listening_review={'status':'UNVERIFIED','reviewer':None,'notes':None,'asset_sha256':sha256(path)})
    result['asset_base_dir']=str(Path(result.get('asset_base_dir',base)).resolve())
    (folder/'sfx_plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


def film_mix(plan,folder,include_music):
    from sfx import mix_narration_with_sfx,_read_stereo
    folder=Path(folder); pieces=[]; cues=[]; intervals=[]; cursor=0
    for section in plan['sections']:
        audio=_read_stereo(section['speech']['file'])
        if len(audio)!=section['speech']['frames']*800: raise ValueError('Voice WAV length changed')
        pieces.append(audio)
        for u in section['speech'].get('utterances',[]):
            intervals.append([cursor/48000+u['speech_start'],cursor/48000+u['speech_end']])
        for cue in section['sfx_cues']:
            cues.append({**cue,'relative_time':cursor/48000+cue['relative_time']})
        cursor+=len(audio)
    voice=folder/'audio'/'film_voice.wav'; voice.parent.mkdir(exist_ok=True)
    wavfile.write(voice,48000,np.concatenate(pieces))
    if include_music and plan.get('music'):
        cues.append({**plan['music'],'relative_time':0,'duration':cursor/48000,'role':'ambience'})
    output=folder/'audio'/'film_mix.wav'
    mix_narration_with_sfx(voice,output,cues,duration=cursor/48000,speech_intervals=intervals)
    return output
