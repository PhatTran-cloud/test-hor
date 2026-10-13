"""Freeze reviewed pose files, selected voice references and take receipts."""
import copy
import json
from pathlib import Path
import shutil
from v4_contract import sha256


def freeze_horror_assets(plan,base,folder):
    if plan.get('profile')!='horror-v4.1': return
    folder=Path(folder)
    for asset in plan['horror'].get('assets',[]):
        for view in asset['views']:
            for pose in view['frames']:
                source=(Path(plan.get('asset_base_dir',base))/pose['file']).resolve()
                target=folder/'art_assets'/asset['id']/view['id']/(pose['id']+source.suffix)
                target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
                pose['file']=str(target)
    for section in plan['sections']:
        section['horror_assets']=[a for a in plan['horror'].get('assets',[]) if a['object_id'] in {o['id'] for o in section['objects']}]
        for u in section['speech'].get('utterances',[]):
            for key,hash_key in [('take_file','take_sha256'),('take_receipt','take_receipt_sha256')]:
                source=Path(u[key]); target=folder/'voice_takes'/section['id']/source.name
                target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
                if sha256(target)!=u[hash_key]: raise ValueError('Voice take snapshot changed')
                u[key]=str(target)
    original=Path(plan['cast']['library']); catalog=json.loads(original.read_text(encoding='utf-8'))
    selected={plan['cast']['narrator'],*plan['cast']['characters'].values()}
    catalog['entries']=[copy.deepcopy(e) for e in catalog['entries'] if e['speaker_id'] in selected]
    for entry in catalog['entries']:
        for ref in [entry['reference'],*entry.get('delivery_references',[])]:
            name=entry['speaker_id']+(('_'+ref['id']) if ref.get('id') else '')
            for key,suffix in [('path','.wav'),('transcript_path','.txt')]:
                source=(original.parent/ref[key]).resolve(); target=folder/'voice_references'/(name+suffix)
                target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target); ref[key]=str(target)
    target=folder/'voice_references'/'manifest.json'; target.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    plan['cast']['library']=str(target)
    for sec in plan['sections']:
        from omnivoice_tts import resolve_references
        sec['speech']['cast_references']=resolve_references(plan,sec)
    for section in plan['sections']:
        for cue in section['sfx_cues']:
            if cue.get('impulse_response'):
                ir=cue['impulse_response']; source=(Path(base)/ir['file']).resolve()
                target=folder/'audio_assets'/(sha256(source)[:16]+source.suffix)
                target.parent.mkdir(exist_ok=True); shutil.copy2(source,target); ir['file']=str(target)
