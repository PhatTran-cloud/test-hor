"""Model-provider worker called by the V4 entrypoint, not a production runner."""
import argparse
from collections import Counter
import gc
import importlib.util
import json
import math
from pathlib import Path
import sys
import wave
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from v4_contract import sha256,digest


def generate(request_path,output_dir,weights_path):
    import onnxruntime as ort
    ort.preload_dlls(directory='')
    if 'CUDAExecutionProvider' not in ort.get_available_providers():
        raise RuntimeError('CUDA unavailable; refusing CPU substitution')
    requests=json.loads(Path(request_path).read_text(encoding='utf-8'))
    for req in requests:
        g=req['generation']
        if not isinstance(g.get('seconds'),(float,int)) or not math.isfinite(g['seconds']) or g['seconds']<=0:
            raise ValueError('Explicit generation seconds are required')
        if g.get('steps',8)!=8 or g.get('cfg',1)!=1:
            raise ValueError('This optimized export uses steps=8/cfg=1; other settings need a separate audit')
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    weights=json.loads(Path(weights_path).read_text(encoding='utf-8'))
    for f in weights['files']:
        if sha256(f['path'])!=f['sha256']: raise ValueError('Model weights changed')
    graph={f['file']:f['path'] for f in weights['files']}
    spec=importlib.util.spec_from_file_location('sa3_vendor',ROOT/'vendor/stable_audio_3/sampler.py')
    vendor=importlib.util.module_from_spec(spec); spec.loader.exec_module(vendor)
    tokenizer=vendor.Tokenizer(ROOT/'vendor/stable_audio_3/tokenizer.model')
    receipt={'provider':'stable_audio_3_small_sfx','source':'model_generated','backend':'ONNX Runtime CUDA',
             'weights_repo':weights['repo'],'weights_revision':weights['revision'],'stages':[],
             'sampler_sha256':sha256(ROOT/'vendor/stable_audio_3/sampler.py'),
             'tokenizer_sha256':sha256(ROOT/'vendor/stable_audio_3/tokenizer.model')}
    receipt['vendor_source']=json.loads((ROOT/'vendor/stable_audio_3/source-receipt.json').read_text(encoding='utf-8'))
    def session(name,file):
        options=ort.SessionOptions(); options.enable_profiling=True; options.log_severity_level=3
        options.intra_op_num_threads=2; options.profile_file_prefix=str(output_dir/name)
        s=ort.InferenceSession(graph[file],sess_options=options,
              providers=[('CUDAExecutionProvider',{'device_id':0,'arena_extend_strategy':'kSameAsRequested'})])
        if 'CUDAExecutionProvider' not in s.get_providers(): raise RuntimeError('CUDA execution provider missing')
        return s
    def finish(name,s):
        path=s.end_profiling(); events=json.loads(Path(path).read_text())
        counts=Counter(e['args']['provider'] for e in events if e.get('cat')=='Node' and e.get('args',{}).get('provider'))
        if not counts.get('CUDAExecutionProvider'): raise RuntimeError('No CUDA kernels observed')
        receipt['stages'].append({'name':name,'kernel_counts':dict(counts),'profile':path})
    hidden={}; latents={}
    s=session('encoder','onnx/t5gemma/encoder.onnx')
    for req in requests:
        ids,mask=tokenizer(req['generation']['prompt'])
        h=s.run(None,{'input_ids':ids.astype(np.int64),'attention_mask':mask.astype(np.int64)})[0]
        if not np.isfinite(h).all(): raise RuntimeError('Non-finite encoding')
        hidden[req['key']]=(h.astype(np.float32),mask.astype(np.float32))
    finish('encoder',s); del s; gc.collect()
    s=session('dit','onnx/sa3-sm-sfx/dit_fp16.onnx')
    for req in requests:
        g=req['generation']; length=math.ceil(g['seconds']*44100/4096); length+=length%2
        h,mask=hidden[req['key']]
        feed={'t5_hidden':h,'t5_mask':mask,'seconds_total':np.array([g['seconds']],np.float32),
              'local_add_cond':np.zeros((1,257,length),np.float32)}
        def forward(x,sigma,cross,gcond):
            return s.run(None,{**feed,'x':x.astype(np.float32),'t':np.array([sigma],np.float32)})[0]
        noise,steps=vendor.make_noise(length,8,g['seed'])
        latent=vendor.sample(forward,noise,steps,vendor.build_pingpong_schedule(8),None,None)
        if not np.isfinite(latent).all(): raise RuntimeError('Non-finite latent')
        latents[req['key']]=latent
        print('Sampled',req['key'],g['seconds'],'seconds',flush=True)
    finish('dit',s); del s; gc.collect()
    s=session('decoder','onnx/same-s/dec_bf16_limiter.onnx')
    generated=[]
    for req in requests:
        pcm=s.run(None,{'latent':latents[req['key']]})[0]
        if pcm.dtype!=np.int32 or pcm.ndim!=3 or pcm.shape[0]!=1 or pcm.shape[2]!=2:
            raise RuntimeError('Unexpected integer PCM decoder interface')
        pcm=pcm[0,:round(req['generation']['seconds']*44100)]
        if len(pcm)!=round(req['generation']['seconds']*44100) or np.abs(pcm.astype(np.int64)).max()>32767:
            raise RuntimeError('Decoder duration/range invalid')
        path=output_dir/(req['key']+'.wav')
        with wave.open(str(path),'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes(pcm.astype(np.int16).tobytes())
        generated.append({'file':str(path),'key':req['key'],'generation':req['generation'],
                          'sha256':sha256(path),'duration':len(pcm)/44100})
    finish('decoder',s); del s; gc.collect()
    for item in generated:
        sidecar={**receipt,**item,'request_sha256':digest(item['generation']),
                 'listening_status':'UNVERIFIED','short_generation_caveat':'L<256: outside documented consumer training range; audition required'}
        Path(item['file']).with_suffix('.json').write_text(json.dumps(sidecar,indent=2),encoding='utf-8')
    (output_dir/'generation_receipt.json').write_text(json.dumps({'provider':receipt,'outputs':generated},indent=2),encoding='utf-8')


if __name__=='__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('requests',type=Path); cli.add_argument('output',type=Path); cli.add_argument('weights',type=Path)
    args=cli.parse_args(); generate(args.requests,args.output,args.weights)
