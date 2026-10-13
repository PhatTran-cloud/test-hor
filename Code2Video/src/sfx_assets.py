"""Freeze selected generated Small-SFX assets; no search or fallback."""
import json
from pathlib import Path
from v4_contract import sha256, digest
from media_io import probe_duration
from horror_contract import validate_sfx_brief


def prepare_cues(cues, base_dir, **unused):
    frozen=[]
    for original in cues or []:
        cue=dict(original); validate_sfx_brief(cue)
        if not cue.get('file'):
            raise ValueError('Generate through production.py sfx, then audition/select the cue')
        path=(Path(base_dir)/cue['file']).resolve()
        sidecar=path.with_suffix('.json')
        provenance=json.loads(sidecar.read_text(encoding='utf-8')) if sidecar.exists() else cue.get('provenance',{})
        if provenance.get('provider')!='stable_audio_3_small_sfx' or provenance.get('source')!='model_generated':
            raise ValueError('Horror SFX requires Small-SFX generation provenance')
        if sha256(path)!=provenance.get('sha256') or provenance.get('request_sha256')!=digest(cue['generation']):
            raise ValueError('SFX asset or generation brief changed')
        if not cue.get('loop') and cue.get('asset_offset',0)+cue['duration']>probe_duration(path)+1/44100:
            raise ValueError('Selected interval/tail exceeds the actual generated WAV')
        review=cue.get('listening_review',{})
        if review.get('status')!='PASS' or review.get('asset_sha256')!=sha256(path) or not review.get('reviewer') or not review.get('notes'):
            raise ValueError('Listen/select the current SFX before freezing audio')
        cue.update(file=str(path),provenance=provenance,source='model_generated')
        frozen.append(cue)
    return frozen


def freeze_music(music,base_dir):
    path=(Path(base_dir)/music['file']).resolve(); provenance=music.get('provenance',{})
    if not provenance.get('source') or not provenance.get('license'):
        raise ValueError('Requested music needs explicit source/license metadata')
    if music['listening_review']['asset_sha256']!=sha256(path):
        raise ValueError('Music changed after review')
    return {**music,'file':str(path),'provenance':{**provenance,'sha256':sha256(path)}}
