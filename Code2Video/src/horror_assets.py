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
    from horror_illustration import validate_illustration_coverage, setting_questions
    validate_illustration_coverage(plan)
    from illustration_direction import directed, lightweight, shot_inventory, MODEL_SKILLS
    from horror_characters import asset_actor_context, character_asset_fingerprint, direction as character_direction, scene_cast_inventory
    from horror_staging import plate_usage, plate_fingerprint
    tasks=[]; three_d_tasks=[]
    horror=plan['horror']; packet=plan.get('production_packet',{})
    direction=packet.get('illustration_direction',{})
    worlds={w['id']:w for w in direction.get('scene_worlds',[])}
    operator=horror.get('illustrator',{})
    for asset in plan['horror'].get('assets',[]):
        alpha=asset.get('requires_alpha',asset['kind']!='layer')
        role=asset.get('illustration_role', 'character_pose' if asset['kind']=='sprite_sequence' else asset['kind'])
        background=role=='background'
        brief=packet.get('character_setting_brief',{})
        current_brief={k:brief[k] for k in ['script_facts','approved_visual_age_bands','approved_setting',
            'reference_design_choices_to_review','style'] if k in brief}
        if brief.get('state_design_correction'):
            current_brief['story_states']=brief['state_design_correction']
        context={'character_and_setting':current_brief,
            'worlds':[worlds[s] for s in asset.get('scene_ids',[])],
            'style_bible':horror['style_bible'], 'visual_system':plan.get('visual_system',{}),
            'design_semantics':asset.get('design_semantics',{})}
        if lightweight(plan):
            # Copyable prompts still need the approved identity/state and art
            # constraints; a shorter storyboard must not discard these facts.
            context={'character_and_setting':current_brief,
                'style_constraints':{k:v for k,v in horror['style_bible'].items() if k!='canonical_prompt'},
                'visual_system':plan.get('visual_system',{}),
                'worlds':[{k:w[k] for k in ['id','layout','perspective','lighting','crop_safety'] if k in w} for w in context['worlds']],
                'design_semantics':asset.get('design_semantics',{})}
        prompt_context=json.dumps(context,ensure_ascii=False)
        actor=asset_actor_context(plan,asset)
        actor_hash=character_asset_fingerprint(plan,asset)
        scene_usage=plate_usage(plan,asset)
        if scene_usage:
            context['plate_staging']=scene_usage
            prompt_context=json.dumps(context,ensure_ascii=False)
        if asset['kind']=='model_3d':
            construction={k:v for k,v in asset['model_spec'].items() if k not in {'file','sha256','resources','inspection_evidence'}}
            prompt=(f"Use the complete 3dviz-pro-max core with lowbudget3d and its illustration bridge. "
                f"Fabricate the original native 3D asset {asset['id']} for canonical object {asset['object_id']}: {asset['identity']}. "
                f"Target Kage artwork principles through original geometry, authored surfaces, depth and light response. "
                f"Action/attachment needs: {json.dumps(asset['action'],ensure_ascii=False)}. "
                f"Construction contract: {json.dumps(construction,ensure_ascii=False)}. "
                f"Inspection views: {json.dumps(asset['views'],ensure_ascii=False)}. Context: {prompt_context}. "
                +(f"Character/crowd construction and restrained performance: {json.dumps(actor,ensure_ascii=False)}. " if actor else '')+
                "Return independently editable GLB/Three.js geometry, named parts, pivots/anchors, variants and textures. "
                "Verify the full base package before fabrication. Preserve source, resource hashes and actual inspection evidence. "
                "Do not make a flattened scene plate or a competing renderer/camera/animation loop. "
                "Motion assembles and animates later; VFX expands causal events later. No artwork PASS from this request.")
            three_d_tasks.append({'asset_id':asset['id'],'object_id':asset['object_id'],'route':'3d',
                'provider':'lowbudget3d','required_skills':MODEL_SKILLS,'base_package_status':'UNVERIFIED_UNTIL_FABRICATOR_CHECKS_COMPLETE_PACKAGE',
                'prompt':prompt,'prompt_sha256':digest(prompt),'construction':construction,
                'status':'REQUEST_ONLY_NOT_FABRICATED'})
            if actor_hash:
                three_d_tasks[-1]['character_design_sha256']=actor_hash
            if scene_usage:
                three_d_tasks[-1].update(scene_usage=scene_usage,scene_staging_sha256=plate_fingerprint(plan,asset))
            continue
        for view in asset['views']:
            for pose in view['frames']:
                performance=asset_actor_context(plan,asset,pose)
                group_instruction=(f"Draw exactly {pose['member_count']} anonymous people in this separate shared-behavior group cutout; "
                    "keep the count legible and do not invent an individually speaking/acting member. " if performance and performance['kind']=='crowd' else '')
                state_instruction=("Draw a single still of the specified performance/component appearance, not an entry-to-exit timeline or blended emotions. "
                    if performance else f"Entry state: {asset['action']['entry_state']}. Exit state: {asset['action']['exit_state']}. ")
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
                        f"{state_instruction}"
                        f"{treatment}{matte}{group_instruction}Preserve identity, scale and the planned state/expression/gesture. "
                        "Do not bake camera movement, motion blur, animated rain/fog or interactive moving shadows into reusable art. "
                        f"Story and construction context: {prompt_context}"
                        +(f" Character performance for this image only: {json.dumps(performance,ensure_ascii=False)}. "
                          "Keep stable facial construction and restrained eyes/brows/mouth/body cues. "
                          "No meme face, comic rubber deformation, laughter, gag pose or copied channel design. "
                          if performance else ''))
                tasks.append({'asset_id':asset['id'],'object_id':asset['object_id'],'view_id':view['id'],'pose_id':pose['id'],
                    'prompt':prompt,'prompt_sha256':digest(prompt),'requires_alpha':alpha,
                    'source_background':'#00FF00' if alpha else 'authored_opaque',
                    'output_format':'alpha_png_after_chroma_key' if alpha else 'provider_original',
                    'model':operator.get('model','Nano Banana 2.1'),
                    'action_prompt':prompt,
                    'reference_files':asset.get('reference_files',[]),'registration':pose,
                    'contact_requirements':asset['action']['contact_requirements'],
                    'status':'REQUEST_ONLY_NOT_GENERATED'})
                if performance:
                    tasks[-1].update(character_performance=performance,character_design_sha256=actor_hash)
                if scene_usage:
                    tasks[-1].update(scene_usage=scene_usage,scene_staging_sha256=plate_fingerprint(plan,asset))
    if not tasks and not three_d_tasks: raise ValueError('No illustration prompts: author the required asset/action/view requests first')
    inventory=shot_inventory(plan)
    result={'provider':'hybrid' if three_d_tasks else 'flow','mode':'prompt_export_only','generation_operator':'human user',
        'style':horror['artwork_style'],'tasks':tasks,
        'three_d_tasks':three_d_tasks,'shot_inventory':inventory,
        'motion_vfx_handoff':{'schema_version':4,'direction_revision':1 if directed(plan) else None,
            'shots':inventory,'required_skills':['storyboard-motion-executor','cinematic-motion-director','cinematic-vfx-director'],
            'status':'BLOCKED_UNTIL_ASSETS_REGISTERED_AND_REVIEWED',
            'instruction':'Mount reviewed assets by canonical IDs and anchors; preserve world, attention, camera information intent, behaviors, events and handoff. Use the section-absolute 60fps clock. Artifact export is not authorization to run motion/VFX.'},
        'batches':[tasks[i:i+5] for i in range(0,len(tasks),5)],
        'instruction':'User runs 2D prompts in Flow; 3D requests go to complete lowbudget3d + 3dviz-pro-max fabrication. Five prompts per batch is an export grouping, not a verified concurrent Flow capability. Preserve originals; chroma-key alpha assets locally, register measured anchors and review actual artwork. Motion/VFX remain later stages; no generation, fabrication or artwork PASS occurs here.'}
    if lightweight(plan):
        # Shared state/registry is already in the one plan. Avoid embedding the
        # whole asset bible repeatedly in each shot of an illustration export.
        result['authoring_mode']='horror_light'
        result['plan_sha256']=digest(plan)
        for task in tasks:
            task.pop('action_prompt',None)  # identical legacy alias
        result['shared_context']={'visual_system':plan['visual_system'],'scene_worlds':list(worlds.values())}
        result['shot_inventory']=[{k:v for k,v in row.items() if k!='direction'} for row in inventory]
        result['motion_vfx_handoff']={'status':'BLOCKED_UNTIL_ASSETS_REGISTERED_AND_REVIEWED',
            'next_command':'production.py motion-brief PLAN --output motion.json',
            'instruction':'Mount reviewed assets by canonical IDs and anchors. Motion/VFX detail is authored in the existing plan at the next authorized stage.'}
    if character_direction(plan) is not None:
        registry=character_direction(plan)
        result['character_direction']=registry
        result['scene_cast_inventory']=scene_cast_inventory(plan)
        requested={ctx['definition']['id'] for a in horror.get('assets',[]) if (ctx:=asset_actor_context(plan,a))}
        result['generation_blockers']=[{'character_id':c['id'],'unresolved':c['unresolved']}
            for c in registry['characters']+registry['crowd_groups'] if c['id'] in requested and c.get('unresolved')]
    result['setting_blockers']=setting_questions(plan)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    text=['# Illustration prompts — user runs Flow\n',result['instruction']]
    if result['setting_blockers']:
        text.append('\n## Setting choices pending before generation\n')
        text.extend('- '+q for q in result['setting_blockers'])
    if result.get('generation_blockers'):
        text.append('\n## Design choices pending before generation\n')
        for pending in result['generation_blockers']:
            text.append('- '+pending['character_id']+': '+'; '.join(pending['unresolved']))
    for i,task in enumerate(tasks):
        text.append(f"\n## Batch {i//5+1} · {task['asset_id']} / {task['view_id']} / {task['pose_id']}\n\n{task['prompt']}\n")
    for task in three_d_tasks:
        text.append(f"\n## 3D fabrication · {task['asset_id']}\n\n{task['prompt']}\n")
    text.append('\n## Complete-shot inventory and motion/VFX handoff\n')
    for row in inventory:
        text.append(f"\n### {row['shot_id']} / {row['scene_id']}\n")
        if row.get('staging') is not None:
            stage=row['staging']
            text.append(f"View: {stage['view']['id']} ({stage['view']['kind']}); reuse plate {stage['view']['plate_object_id']}. {stage['view']['framing']}\n")
            text.append('Static details readable here: '+(', '.join(d['id'] for d in stage['static_details']) or 'none declared')+'\n')
            text.append('Next link: '+stage['story_link']['link_kind']+'\n')
        if row.get('cast') is not None:
            text.append(f"People: {row['cast']['total_visible_people']} represented; {row['cast']['crowd_count']} in anonymous groups.\n")
            for actor in row['cast']['entries']:
                text.append(f"- Cast {actor['object_id']}: {actor['attention_role']}; states={' -> '.join(actor['state_ids'])}; "
                    f"count={actor.get('count',1)}; {actor['blocking']}; gaze={actor.get('gaze_target','shared group behavior')}; "
                    f"state gaze={actor.get('gaze_targets',{})}\n")
        for component in row['components']:
            text.append(f"- {component['object_id']}: {component['method']}; assets={', '.join(component['asset_ids']) or 'explicit code/existing route'}; routes={', '.join(component['routes']) or component['method']}\n")
    text.append('\nMotion/VFX: register and review actual assets first. The JSON carries the scoped direction/causal/camera/handoff contract. Export does not start a later stage.\n')
    output.with_suffix('.md').write_text('\n'.join(text),encoding='utf-8')
    return result


def contact_sheet(plan,asset_id,view_id,output):
    asset=next(a for a in plan['horror']['assets'] if a['id']==asset_id)
    if asset['kind']=='model_3d':
        raise ValueError('Inspect native 3D views in the final Three.js route; sprite contact sheets are for 2D assets')
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
