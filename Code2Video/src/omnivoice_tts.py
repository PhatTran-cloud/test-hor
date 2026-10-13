"""OmniVoice reference cloning with cast-bound measured utterance receipts."""
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from v4_contract import digest, sha256


def line_identity(plan, segment):
    role = segment.get("role")
    if role not in {"narrator", "dialogue"}:
        raise ValueError("Each spoken segment declares role narrator or dialogue")
    if role == "narrator":
        speaker = plan["cast"]["narrator"]
        if segment.get("instruct") is not None or segment.get("acting_direction"):
            raise ValueError("Narrator has no instruction or acting prompt")
    else:
        character = segment.get("character_id")
        if character not in plan["cast"]["characters"]:
            raise ValueError("Dialogue needs a stable cast character_id")
        speaker = plan["cast"]["characters"][character]
        direction = segment.get("acting_direction", {})
        if not direction.get("intention") or not direction.get("mood"):
            raise ValueError("Dialogue needs intention and mood; these are creative direction, not model tags")
    instruction = segment.get("instruct")
    if instruction not in {None, "whisper"}:
        raise ValueError("Clone instruction supports null or whisper; arbitrary emotion is unsupported")
    return {"id":segment["id"],"text":segment["text"],"role":role,"speaker_id":speaker,
            "character_id":segment.get("character_id"),"instruct":instruction,
            "acting_direction":segment.get("acting_direction"),
            "delivery_reference_id":segment.get("delivery_reference_id"),
            "pause_after":segment.get("pause_after",.12)}


def resolve_references(plan, section):
    library = Path(plan["cast"]["library"])
    catalog = json.loads(library.read_text(encoding="utf-8"))
    entries = {e["speaker_id"]:e for e in catalog["entries"]}
    resolved = {}
    for segment in section["narration_segments"]:
        line = line_identity(plan,segment)
        sid = line["speaker_id"]
        if sid not in entries:
            raise ValueError(f"Unknown speaker {sid}")
        entry = entries[sid]
        required_role = "narrator" if line["role"] == "narrator" else "dialogue"
        if entry["role"] != required_role:
            raise ValueError("Main references are narrator-only; other references are dialogue-only")
        if entry["language_id"] != plan["language_id"]:
            raise ValueError("Select a same-language voice reference for this video")
        reference = entry["reference"]
        ref_id = line["delivery_reference_id"]
        if ref_id:
            if required_role == "narrator":
                raise ValueError("Narrator uses its canonical reference without mood variants")
            choices = {d["id"]:d for d in entry.get("delivery_references",[])}
            if ref_id not in choices or choices[ref_id].get("speaker_id") != sid:
                raise ValueError("Delivery reference must be auditioned as the same speaker")
            reference = choices[ref_id]
        path = (library.parent / reference["path"]).resolve()
        if not path.is_file() or sha256(path) != reference["sha256"]:
            raise ValueError("Reference WAV is missing or changed")
        transcript_path = (library.parent / reference["transcript_path"]).resolve()
        transcript = transcript_path.read_text(encoding="utf-8").strip()
        if not transcript or reference.get("transcript_status") != "REVIEWED":
            raise ValueError("A reviewed reference transcript is required; auto-ASR is not silently accepted")
        review = reference.get("listening_review",{})
        if review.get("status") != "PASS" or review.get("asset_sha256") != reference["sha256"] or not review.get("reviewer") or not review.get("notes"):
            raise ValueError("Reference needs a current listening review before cloning")
        key = sid + (":"+ref_id if ref_id else "")
        resolved[key] = {"speaker_id":sid,"reference_id":ref_id,"role":required_role,
            "language_id":entry["language_id"],"file":str(path),"sha256":reference["sha256"],
            "ref_text":transcript,"transcript_sha256":digest(transcript),"listening_review":review}
    return resolved


def configuration_identity(plan, section):
    refs = resolve_references(plan,section)
    settings = {"steps":int(plan.get("voice_settings",{}).get("steps",32)),
        "guidance":float(plan.get("voice_settings",{}).get("guidance",2)),
        "denoise":bool(plan.get("voice_settings",{}).get("denoise",False)),
        "preprocess":bool(plan.get("voice_settings",{}).get("preprocess",False)),
        "postprocess":bool(plan.get("voice_settings",{}).get("postprocess",False)),
        "speed":plan["tts_speed"],"duration":None}
    if settings["steps"] < 1 or not math.isfinite(settings["guidance"]):
        raise ValueError("Invalid OmniVoice settings")
    data = {"provider":"omnivoice","language_id":plan["language_id"],
        "narrator":plan["cast"]["narrator"],"lines":[line_identity(plan,s) for s in section["narration_segments"]],
        "references":{k:{a:b for a,b in v.items() if a != "file"} for k,v in refs.items()},
        "settings":settings,"lead_seconds":section.get("lead_seconds",.12),"tail_seconds":section.get("tail_seconds",.15)}
    return {"sha256":digest(data),"data":data,"references":refs,"settings":settings}


class OmniVoiceClient:
    def __init__(self, endpoint):
        import requests
        from gradio_client import Client
        response=requests.get(endpoint.rstrip('/')+'/gradio_api/info',timeout=30)
        response.raise_for_status()
        api=response.json().get('named_endpoints',{}).get('/_clone_fn',{})
        names=[p.get('parameter_name') for p in api.get('parameters',[])]
        expected=['text','lang','ref_aud','ref_text','instruct','ns','gs','dn','sp','du','pp','po']
        if names != expected:
            raise ValueError(f"OmniVoice clone API changed: {names}; audit runtime before inference")
        self.receipt={"endpoint":endpoint,"clone_api":"/_clone_fn","parameters":names,
                      "model_revision":"NOT_EXPOSED_BY_RUNTIME","seed":"NOT_EXPOSED_BY_RUNTIME"}
        self.client=Client(endpoint,verbose=False)

    def clone(self,text,language,reference,instruction,settings):
        from gradio_client import handle_file
        # Gradio Dropdown forbids arbitrary ISO values even though model accepts codes.
        display_language={'en':'English','vi':'Vietnamese'}[language]
        result=self.client.predict(text,display_language,handle_file(reference['file']),reference['ref_text'],instruction,
            settings['steps'],settings['guidance'],settings['denoise'],settings['speed'],None,
            settings['preprocess'],settings['postprocess'],api_name='/_clone_fn')
        path=result[0]
        if isinstance(path,dict): path=path.get('path')
        if not path or not Path(path).is_file():
            raise RuntimeError(f"OmniVoice returned no audio; status {result[1:]}")
        return Path(path),str(result[1:])


def prepare_section(plan,section,output,endpoint,client=None):
    """Preserve utterance PCM after decode; never trim whispers or stretch to a slot."""
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    identity=configuration_identity(plan,section)
    takes=output.parent/(output.stem+'_takes'); takes.mkdir(exist_ok=True)
    pieces=[np.zeros(round(section.get('lead_seconds',.12)*48000),np.float32)]
    cursor=len(pieces[0]); ledger=[]; boundaries=[]; raw_total=0
    for segment in section['narration_segments']:
        line=line_identity(plan,segment)
        ref_key=line['speaker_id']+(':'+line['delivery_reference_id'] if line['delivery_reference_id'] else '')
        reference=identity['references'][ref_key]
        take_identity={"line":line,"language_id":plan['language_id'],"reference":{k:v for k,v in reference.items() if k != 'file'},
                       "settings":identity['settings'],"endpoint":endpoint}
        raw=takes/(segment['id']+'_raw.wav'); sidecar=raw.with_suffix('.json')
        cached=json.loads(sidecar.read_text(encoding='utf-8')) if sidecar.exists() else {}
        if not raw.is_file() or cached.get('identity_sha256') != digest(take_identity) or cached.get('sha256') != sha256(raw):
            if client is None: client=OmniVoiceClient(endpoint)
            generated,status=client.clone(line['text'],plan['language_id'],reference,line['instruct'],identity['settings'])
            shutil.copy2(generated,raw)
            cached={"identity_sha256":digest(take_identity),"identity":take_identity,"sha256":sha256(raw),
                    "runtime":client.receipt,"status":status,"listening_status":"UNVERIFIED"}
            sidecar.write_text(json.dumps(cached,ensure_ascii=False,indent=2),encoding='utf-8')
        pcm=subprocess.run(['ffmpeg','-v','error','-i',str(raw),'-f','f32le','-ac','1','-ar','48000','pipe:1'],
                           capture_output=True,check=True).stdout
        audio=np.frombuffer(pcm,dtype='<f4').copy()
        if not len(audio) or not np.isfinite(audio).all() or np.max(np.abs(audio)) < 1e-6:
            raise ValueError('Voice take is empty/non-finite/silent')
        active=np.flatnonzero(np.abs(audio)>max(1e-6,float(np.max(np.abs(audio)))*.001))
        start=cursor/48000; speech_start=(cursor+int(active[0]))/48000
        speech_end=(cursor+int(active[-1])+1)/48000
        pieces.append(audio); cursor+=len(audio); raw_total+=len(audio)/48000
        pause=float(segment.get('pause_after',.12))
        pieces.append(np.zeros(round(pause*48000),np.float32)); cursor+=len(pieces[-1])
        item={"id":segment['id'],"text":line['text'],"start":start,"end":cursor/48000,
              "speech_start":speech_start,"speech_end":speech_end,"line_identity":line,
              "take_file":str(raw),"take_sha256":sha256(raw),"take_receipt":str(sidecar),
              "take_receipt_sha256":sha256(sidecar),"listening_status":"UNVERIFIED",
              "listening_review":{"status":"UNVERIFIED","reviewer":None,"notes":None,"asset_sha256":sha256(raw)}}
        ledger.append(item); boundaries.append((speech_start,speech_end))
    pieces.append(np.zeros(round(section.get('tail_seconds',.15)*48000),np.float32))
    audio=np.concatenate(pieces); frames=math.ceil(len(audio)/800)
    audio=np.pad(audio,(0,frames*800-len(audio))); wavfile.write(output,48000,audio)
    return {"file":str(output.resolve()),"duration":frames/60,"frames":frames,"fps":60,
        "speech_start":boundaries[0][0],"speech_end":boundaries[-1][1],"raw_duration":raw_total,
        "voice":plan['cast']['narrator'],"provider":"omnivoice","speed":plan['tts_speed'],"time_stretch":False,
        "configuration_sha256":identity['sha256'],"cast_references":identity['references'],
        "utterances":ledger,"beats":ledger,"timing_basis":"measured utterances; not word/phoneme alignment",
        "delivery_status":"UNVERIFIED; creative mood is not proof of provider acting"}
