"""Export human-run illustration prompts and inspect registered asset sheets."""
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image,ImageDraw


def write_asset_briefs(plan,output):
    output=Path(output)
    if output.suffix.lower()!='.json': raise ValueError('Use .json output; the copyable .md export is written alongside it')
    from v4_contract import digest
    from horror_illustration import validate_illustration_coverage,asset_shots,shot_image_context
    validate_illustration_coverage(plan)
    tasks=[]
    horror=plan['horror']; packet=plan.get('production_packet',{})
    direction=packet.get('illustration_direction',{})
    worlds={w['id']:w for w in direction.get('scene_worlds',[])}
    operator=horror.get('illustrator',{})
    for asset in plan['horror'].get('assets',[]):
        alpha=asset.get('requires_alpha',asset['kind']!='layer')
        role=asset.get('illustration_role', 'character_pose' if asset['kind']=='sprite_sequence' else asset['kind'])
        background=role=='background'
        brief=packet.get('character_setting_brief',{})
        current_brief={k:brief[k] for k in ['physical_facts','approved_visual_age_bands','approved_setting','style'] if k in brief}
        world_fields=['id','layout','perspective','lighting','required_props','crop_safety','spatial_anchors']
        for view in asset['views']:
            for pose in view['frames']:
                usages=asset_shots(plan,asset,view,pose)
                used_worlds=list(dict.fromkeys(s.get('scene_id') for s in usages if s.get('scene_id') in worlds))
                prompt_context=json.dumps({'character_and_setting':current_brief,
                    'worlds':[{k:worlds[s][k] for k in world_fields if k in worlds[s]} for s in used_worlds],
                    'shot_constraints':[shot_image_context(s,asset['object_id']) for s in usages],
                    'style_bible':horror['style_bible']},ensure_ascii=False)
                treatment=("Draw the complete empty environment clean plate, with coherent architecture, ground plane, perspective and functional details. "
                    "Keep geography, scale, light direction and crop margins consistent with the shared scene world. No characters. " if background else
                    "Draw only this reusable object or character component, fully visible with crop margin and hidden joint overlap where required. ")
                matte=("Use a perfectly uniform solid chroma green #00FF00 background, including gaps between limbs. "
                    "No green on the subject, green spill, backdrop gradients/textures or cast ground shadow. "
                    "No added captions, watermarks or checkerboard; preserve only story-required subject markings. "
                    "This is a green-screen source; code will remove the background, do not paint fake transparency. " if alpha else
                    "Keep the authored opaque environment/background; transparency is not requested. ")
                prompt=(f"{horror['style_bible']['canonical_prompt']}. {asset['identity']}. Asset role: {role}. "
                        f"Action intention: {asset['action']['intent']}. Mechanics: {asset['action']['mechanics']}. "
                        f"View: {view['camera_region']}. Pose: {pose.get('description',pose['id'])}. "
                        f"Entry state: {asset['action']['entry_state']}. Exit state: {asset['action']['exit_state']}. "
                        f"{treatment}{matte}Preserve identity, scale and the planned state/expression/gesture. "
                        "Produce exactly one image of the described pose/component, not a storyboard grid or sequence. "
                        "Entry/exit and shot framing are continuity/construction notes, not additional moments or objects to draw. "
                        "Respect every applicable reveal ceiling; draw only what this requested image may show. "
                        f"Image constraints: {json.dumps(pose.get('image_constraints',[]),ensure_ascii=False)}. "
                        "Do not bake camera movement, motion blur, animated rain/fog or interactive moving shadows into reusable art. "
                        f"Story and construction context: {prompt_context}")
                tasks.append({'asset_id':asset['id'],'object_id':asset['object_id'],'view_id':view['id'],'pose_id':pose['id'],
                    'prompt':prompt,'prompt_sha256':digest(prompt),'requires_alpha':alpha,
                    'source_background':'#00FF00' if alpha else 'authored_opaque',
                    'output_format':'alpha_png_after_chroma_key' if alpha else 'provider_original',
                    'model':operator.get('model','Nano Banana 2.1'),
                    'scene_ids':used_worlds,'shot_ids':[s['id'] for s in usages],
                    'storyboard_usage':[{'shot_id':s['id'],'scene_id':s.get('scene_id'),
                        'primary_action':s.get('storyboard',{}).get('primary_action'),
                        'entry_state':s.get('storyboard',{}).get('start_state',{}).get(asset['object_id']),
                        'exit_state':s.get('storyboard',{}).get('end_state',{}).get(asset['object_id']),
                        'transition':s.get('storyboard',{}).get('transition')} for s in usages],
                    'action_prompt':prompt,
                    'reference_files':asset.get('reference_files',[]),'registration':pose,
                    'contact_requirements':asset['action']['contact_requirements'],
                    'status':'REQUEST_ONLY_NOT_GENERATED'})
    if not tasks: raise ValueError('No illustration prompts: author the required asset/action/view requests first')
    result={'provider':'flow','mode':'prompt_export_only','generation_operator':'human user',
        'style':horror['artwork_style'],'tasks':tasks,
        'batches':[tasks[i:i+5] for i in range(0,len(tasks),5)],
        'instruction':'User runs these prompts in Flow. Five prompts per batch is an export grouping, not a verified concurrent Flow capability. Preserve originals; chroma-key alpha assets locally, register measured anchors and review actual images. No generation or artwork PASS occurs here.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    text=['# Illustration prompts — user runs Flow\n',result['instruction']]
    for i,task in enumerate(tasks):
        text.append(f"\n## Batch {i//5+1} · {task['asset_id']} / {task['view_id']} / {task['pose_id']}\n\n"
                    f"Scenes: {', '.join(task['scene_ids'])}. Shots: {', '.join(task['shot_ids'])}.\n\n{task['prompt']}\n")
    output.with_suffix('.md').write_text('\n'.join(text),encoding='utf-8')
    return result


def contact_sheet(plan,asset_id,view_id,output):
    asset=next(a for a in plan['horror']['assets'] if a['id']==asset_id)
    view=next(v for v in asset['views'] if v['id']==view_id)
    images=[]
    for pose in view['frames']:
        image=Image.open(Path(plan['asset_base_dir'])/pose['file']).convert('RGBA')
        image.thumbnail((320,320)); images.append((pose,image.copy()))
    columns=min(4,len(images)); rows=(len(images)+columns-1)//columns
    sheet=Image.new('RGB',(columns*360,rows*380),(28,30,36)); draw=ImageDraw.Draw(sheet)
    for i,(pose,image) in enumerate(images):
        x=(i%columns)*360; y=(i//columns)*380
        sheet.paste(image,(x+(360-image.width)//2,y+10),image)
        draw.text((x+10,y+340),f"{pose['id']} / hold {pose['hold_frames']} frames",fill='white')
    sheet.save(output)


def doctor_report(check_weights=False):
    from gpu_lifecycle import configuration,container_state
    from v4_contract import sha256
    config=configuration(); report={'version':'4.1-horror','production_ready':'NOT_CLAIMED',
        'commands':{name:shutil.which(name) for name in ['ffmpeg','ffprobe','node','npm','docker','nvidia-smi']},
        'voice_provider':'omnivoice','sfx_provider':'stable_audio_3_small_sfx','freesound':'REMOVED','kokoro':'NOT_ROUTED'}
    try: report['voice_container_running']=container_state(config['omnivoice']['container'])
    except (subprocess.SubprocessError,FileNotFoundError) as e: report['voice_container_error']=str(e)
    catalog=json.loads(Path(config['voice_library']).read_text(encoding='utf-8'))
    report['voice_references']=len(catalog['entries'])
    report['references_with_asr_draft']=sum(e['reference'].get('transcript_status')=='ASR_DRAFT_UNREVIEWED' for e in catalog['entries'])
    report['references_with_reviewed_transcript']=sum(e['reference'].get('transcript_status')=='REVIEWED' for e in catalog['entries'])
    weights=json.loads(Path(config['small_sfx']['weights']).read_text(encoding='utf-8'))
    report['weights']=[{'file':f['file'],'exists':Path(f['path']).is_file(),
        'hash_matches':sha256(f['path'])==f['sha256'] if check_weights else 'NOT_CHECKED'} for f in weights['files']]
    report['small_sfx_python_exists']=Path(config['small_sfx']['python']).is_file()
    try:
        import requests
        response=requests.get('http://127.0.0.1:8100/health',timeout=3)
        response.raise_for_status()
        report['flowkit_extension_connected']=response.json().get('extension_connected') is True
    except Exception as e:
        report['flowkit']='UNAVAILABLE: '+str(e)
    report['note']='Read-only inventory; no model load/start, no quality approval.'
    return report
