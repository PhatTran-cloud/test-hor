"""Serialize audio stages and release the voice container before Small-SFX."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import time

WORKSPACE=Path(__file__).resolve().parents[2]


def configuration():
    return json.loads((WORKSPACE/'config.json').read_text(encoding='utf-8'))


def memory_mib():
    result=subprocess.run(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
    return [int(s.strip()) for s in result.stdout.splitlines() if s.strip()]


def container_state(name):
    r=subprocess.run(['docker','inspect','--format','{{.State.Running}}',name],capture_output=True,text=True,check=True)
    return r.stdout.strip()=='true'


def stop_voice(config):
    name=config['omnivoice']['container']
    if container_state(name):
        subprocess.run(['docker','stop',name],capture_output=True,text=True,check=True,timeout=90)
    if container_state(name): raise RuntimeError('OmniVoice did not stop')


@contextmanager
def audio_stage(stage,receipt_dir):
    if stage not in {'voice','sfx','asr'}: raise ValueError(stage)
    config=configuration(); receipt_dir=Path(receipt_dir); receipt_dir.mkdir(parents=True,exist_ok=True)
    lock=WORKSPACE/'.audio-gpu.lock'
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,json.dumps({'pid':os.getpid(),'stage':stage}).encode()); os.close(fd)
    record={'stage':stage,'status':'STARTING','start_time':time.time()}
    baseline=None
    try:
        stop_voice(config)
        baseline=memory_mib(); record['idle_vram_mib']=baseline
        if stage=='voice':
            import requests
            subprocess.run(['docker','start',config['omnivoice']['container']],capture_output=True,text=True,check=True)
            subprocess.run(['docker','exec',config['omnivoice']['container'],'python','-c',
                'import torch; assert torch.cuda.is_available(), "OmniVoice GPU unavailable"'],
                capture_output=True,text=True,check=True,timeout=60)
            deadline=time.monotonic()+config['omnivoice'].get('startup_timeout_s',180)
            while True:
                try:
                    r=requests.get(config['omnivoice']['endpoint'].rstrip('/')+'/gradio_api/info',timeout=5)
                    r.raise_for_status(); break
                except requests.RequestException:
                    if time.monotonic()>deadline: raise RuntimeError('OmniVoice API startup timed out')
                    time.sleep(1)
        record['status']='RUNNING'
        yield config
        record['status']='COMPLETED'
    except BaseException as exc:
        record['status']='FAILED'; record['error']=str(exc); raise
    finally:
        try:
            stop_voice(config)
            if baseline is not None:
                # Observe release relative to this stage's idle baseline; tolerate display allocations.
                tolerance=config.get('vram_release_tolerance_mib',256)
                deadline=time.monotonic()+30
                while True:
                    after=memory_mib()
                    if len(after)==len(baseline) and all(a<=b+tolerance for a,b in zip(after,baseline)):
                        record['released_vram_mib']=after; break
                    if time.monotonic()>deadline:
                        record['status']='RELEASE_FAILED'
                        raise RuntimeError('GPU memory was not released; stop before the next stage')
                    time.sleep(.5)
        finally:
            record['end_time']=time.time()
            (receipt_dir/(stage+'_lifecycle.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
            lock.unlink(missing_ok=True)


def renderer_guard():
    config=configuration()
    if (WORKSPACE/'.audio-gpu.lock').exists() or container_state(config['omnivoice']['container']):
        raise RuntimeError('Finish/unload the audio stage before rendering')


@contextmanager
def render_stage():
    """Hold the same exclusive resource lock throughout rendering, not just preflight."""
    renderer_guard()
    lock=WORKSPACE/'.audio-gpu.lock'
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,json.dumps({'pid':os.getpid(),'stage':'render'}).encode()); os.close(fd)
    try:
        # Recheck after acquiring to close the audio/render preflight race.
        if container_state(configuration()['omnivoice']['container']):
            raise RuntimeError('OmniVoice started during render preflight')
        yield
    finally:
        lock.unlink(missing_ok=True)
