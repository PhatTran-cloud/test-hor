"""V4.1 horror: one entrypoint, explicit human-authorized stages."""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(ROOT))
from v3_contract import normalize_plan
from v4_workflow import skill_routes
from gpu_lifecycle import configuration


def read_plan(path):
    path=Path(path).resolve(); data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema_version')!=4: raise ValueError('Horror retains schema_version=4')
    if data.get('profile')!='horror-v4.1' and not data.get('technical_fixture'):
        raise ValueError('This workspace requires profile=horror-v4.1')
    if data.get('cast',{}).get('library'):
        data['cast']['library']=str((path.parent/data['cast']['library']).resolve())
    data.setdefault('asset_base_dir',str(path.parent))
    return normalize_plan(data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ['context','check','prepare','sfx','asset-brief','motion-brief','sheet','flow-submit','flow-status','preview','render']:
        sub=commands.add_parser(name); sub.add_argument('plan',type=Path)
        if name=='context':
            sub.add_argument('--shot'); sub.add_argument('--output',type=Path,required=True)
        elif name in {'asset-brief','motion-brief','sheet','flow-submit','flow-status'}:
            sub.add_argument('--output',type=Path,required=True)
            if name=='sheet': sub.add_argument('--asset',required=True); sub.add_argument('--view',required=True)
        else:
            sub.add_argument('--output-root',type=Path); sub.add_argument('--no-tts',action='store_true',help='Technical fixtures only')
    doctor=commands.add_parser('doctor'); doctor.add_argument('--check-weights',action='store_true')
    chroma=commands.add_parser('chroma-key',help='Remove solid #00FF00 locally; preserve original, output alpha PNG/mask/receipt, no artwork approval')
    chroma.add_argument('source',type=Path); chroma.add_argument('--output',type=Path,required=True)
    chroma.add_argument('--inner',type=float,default=30); chroma.add_argument('--outer',type=float,default=100)
    chroma.add_argument('--no-despill',action='store_true')
    sprite=commands.add_parser('sprite-preview',help='Render an isolated supplied-sprite test, never a film/release or artwork approval')
    sprite.add_argument('spec',type=Path); sprite.add_argument('--output',type=Path,required=True)
    design=commands.add_parser('voice-design',help='Audition designed dialogue references; no film synthesis or listening approval')
    design.add_argument('request',type=Path); design.add_argument('--output',type=Path,required=True)
    asr=commands.add_parser('reference-asr',help='Word-level ASR drafts for explicitly scoped references; no listening approval')
    asr.add_argument('manifest',type=Path); asr.add_argument('--model',type=Path,required=True)
    asr.add_argument('--python',type=Path,required=True,help='Existing CUDA ASR runtime')
    sample=commands.add_parser('reference-sample',help='Sample a real local reference video at 1 image/second; no download, analysis or film production')
    sample.add_argument('source',type=Path); sample.add_argument('--source-url',required=True)
    sample.add_argument('--start',type=float,default=0); sample.add_argument('--seconds',type=int,default=180)
    sample.add_argument('--source-offset',type=float,default=0,help='Original-source time at local file time zero; declared provenance')
    sample.add_argument('--output',type=Path,required=True)
    reference_check=commands.add_parser('reference-check',help='Verify reference frame hashes and annotation coverage; never auto-approve analysis')
    reference_check.add_argument('folder',type=Path); reference_check.add_argument('--annotations',type=Path)
    review=commands.add_parser('review'); review.add_argument('run',type=Path); review.add_argument('file',type=Path)
    release=commands.add_parser('release'); release.add_argument('run',type=Path)
    args=parser.parse_args()
    if args.command=='reference-sample':
        from reference_study import sample_reference
        result=sample_reference(args.source,args.output,args.source_url,args.start,args.seconds,args.source_offset)
        print(json.dumps({'output':str(args.output.resolve()),'status':result['status'],'sample_count':len(result['frames'])},indent=2)); return
    if args.command=='reference-check':
        from reference_study import check_reference
        print(json.dumps(check_reference(args.folder,args.annotations),indent=2)); return
    if args.command=='flow-submit':
        parser.error('Illustration exports prompts only. Use asset-brief; the human user runs Flow manually.')
    if args.command=='chroma-key':
        from horror_chroma import chroma_key
        print(json.dumps(chroma_key(args.source,args.output,args.inner,args.outer,not args.no_despill),ensure_ascii=False,indent=2)); return
    if args.command=='sprite-preview':
        from horror_sprite_preview import render_sprite_preview
        print(json.dumps(render_sprite_preview(args.spec,args.output),ensure_ascii=False,indent=2)); return
    if args.command=='doctor':
        from horror_assets import doctor_report
        print(json.dumps(doctor_report(args.check_weights),ensure_ascii=False,indent=2)); return
    if args.command=='voice-design':
        from omnivoice_design import run_audition
        print(run_audition(args.request,args.output)); return
    if args.command=='reference-asr':
        subprocess.run([str(args.python.resolve()),str(ROOT.parent/'voice_library/transcribe_references.py'),
                        '--manifest',str(args.manifest.resolve()),'--model',str(args.model.resolve())],check=True)
        return
    if args.command in {'review','release'}:
        from v4_quality import apply_review,release_check
        result=release_check(args.run) if args.command=='release' else apply_review(args.run,json.loads(args.file.read_text(encoding='utf-8')))
        print(json.dumps(result,ensure_ascii=False,indent=2)); return
    args.plan=args.plan.resolve(); plan=read_plan(args.plan)
    if args.command=='context':
        from prompts.v4 import get_v4_direction_prompt,get_v4_execution_prompt
        packet=plan.get('production_packet',{})
        content=get_v4_execution_prompt(plan,args.shot) if args.shot else get_v4_direction_prompt(
            {**packet.get('brief',{}),'content_profile':plan['content_profile'],'profile':plan.get('profile'),'language_id':plan.get('language_id'),'cast':plan.get('cast'),'horror':plan.get('horror'),
             'production_packet':{k:packet.get(k) for k in ['visual_style_decision','character_setting_brief','illustration_direction']}},packet.get('research',{}),
            '\n'.join(s.get('narration','') for s in plan['sections']))
        routed=plan if not args.shot else {**plan,'sections':[{'shots':[s for sec in plan['sections'] for s in sec['shots'] if s['id']==args.shot]}]}
        header='# V4.1 horror production context\n\nPlan: '+str(args.plan)+'\nStage: '+plan['phase']+'\nApplicable skills: '+', '.join(skill_routes(routed))
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(header+'\n\n'+content,encoding='utf-8')
        print(args.output.resolve()); return
    if args.command in {'flow-submit','flow-status'}:
        if plan['phase']!='timed': raise ValueError('Artwork generation uses the reviewed timed direction')
        from flow_assets import submit,status
        args.output.parent.mkdir(parents=True,exist_ok=True)
        if args.command=='flow-submit': submit(plan,args.output)
        else: status(plan,args.output)
        print(args.output.resolve()); return
    if args.command in {'asset-brief','motion-brief','sheet'}:
        from horror_assets import write_asset_briefs,contact_sheet
        args.output.parent.mkdir(parents=True,exist_ok=True)
        if args.command in {'asset-brief','motion-brief'}:
            if args.output.resolve()==args.plan: raise ValueError('Do not overwrite the input plan with exported prompts')
            if args.command=='asset-brief': write_asset_briefs(plan,args.output)
            else:
                from horror_motion import write_motion_brief
                write_motion_brief(plan,args.output)
        else: contact_sheet(plan,args.asset,args.view,args.output)
        print(args.output.resolve()); return
    if args.command=='sfx':
        if plan['phase']!='timed': raise ValueError('Generate SFX from a timed plan; audition before authored rendering')
        if args.no_tts: raise ValueError('SFX generation uses actual measured voice timing')
        from v4_contract import validate_files
        validate_files(plan,args.plan.parent)
        from horror_audio import prepare_sfx
        from output_paths import get_output_root
        root=args.output_root or get_output_root()
        folder=root/'sfx_runs'/('SFX_'+uuid.uuid4().hex[:8])
        prepare_sfx(plan,args.plan.parent,folder)
        print(folder/'sfx_plan.json'); return
    config=configuration()
    from v4_pipeline import run_v4
    from snapshot_project import snapshot_browser_project
    runtime_args=SimpleNamespace(plan=args.plan,output_root=args.output_root,no_tts=args.no_tts,
        tts_endpoint=config['omnivoice']['endpoint'],voice=None,validate_only=args.command=='check',
        prepare_only=args.command=='prepare',preview_shot=plan.get('production_packet',{}).get('representative',{}).get('shot_id') if args.command=='preview' else None)
    if args.command in {'preview','render'}:
        from gpu_lifecycle import render_stage
        with render_stage():
            run_v4(plan,runtime_args,snapshot_browser_project)
    else:
        run_v4(plan,runtime_args,snapshot_browser_project)


if __name__=='__main__': main()
