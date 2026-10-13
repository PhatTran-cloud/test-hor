"""Export scene assembly tasks; does not fabricate, animate or render assets."""
import copy
import json
from pathlib import Path

from horror_contract import asset_digest
from v4_contract import digest
from horror_illustration import validate_illustration_coverage, setting_questions
from illustration_direction import resolve_shot_direction
from horror_characters import character_asset_current, direction as character_direction, scene_cast_inventory
from horror_staging import plate_current


def registered(asset):
    if asset['kind'] == 'model_3d':
        model=asset['model_spec']
        return bool(model.get('file') and model.get('sha256') and model.get('inspection_evidence'))
    return all(p.get('file') and p.get('sha256') for v in asset['views'] for p in v['frames'])


def write_motion_brief(plan, output):
    output = Path(output)
    if output.suffix.lower() != '.json':
        raise ValueError('Motion brief uses .json with a sibling readable .md')
    validate_illustration_coverage(plan)
    assets = plan['horror'].get('assets', [])
    pending = [a['id'] for a in assets if not registered(a) or a.get('review', {}).get('status') != 'PASS'
               or a['review'].get('asset_digest') != asset_digest(a) or not character_asset_current(plan,a) or not plate_current(plan,a)]
    blockers = (['MEASURED_VOICE_TIMING_REQUIRED'] if plan['phase'] == 'draft' else [])
    setting_blockers=setting_questions(plan)
    if setting_blockers:
        blockers.append('SETTING_DESIGN_DECISION_UNRESOLVED')
    if pending:
        blockers.append('ASSET_REGISTRATION_AND_CURRENT_REVIEW_REQUIRED')
    tasks = []
    for section in plan['sections']:
        objects = {o['id']: o for o in section['objects']}
        for shot in section['shots']:
            scoped = resolve_shot_direction(plan, section, shot)
            tasks.append({'section_id':section['id'], 'shot_id': shot['id'], 'scene_id': shot.get('scene_id'),
                'purpose': shot['visual_thesis'], 'action': shot.get('action', shot.get('panel_plan')),
                'focus': shot['attention'], 'camera': shot['camera'],
                'instances': [{'object_id':oid, 'illustration':objects[oid]['illustration']} for oid in shot['object_ids']],
                'motion': shot.get('behaviors'), 'motion_status':'DECLARED_NOT_EXECUTED' if shot.get('behaviors') else 'AUTHOR_AT_MOTION_STAGE',
                'active_events':scoped['active_events'], 'dependency_events':scoped['dependency_events'],
                'vfx':[e for e in scoped['active_events'] if e['kind']=='vfx'],
                'sound':shot.get('sound_intent', shot.get('sound_plan')), 'handoff':shot['handoff'],
                'clock':{'fps':60,'section_start_frame':shot.get('start_frame'),
                    'section_end_frame':shot.get('end_frame'),'film_start_frame':section.get('film_start_frame'),
                    'planning_window':shot.get('planning_window'),
                    'status':'PROVISIONAL_NOT_MEASURED' if plan['phase']=='draft' else 'MEASURED_PLAN_FILE_VERIFICATION_PENDING'}})
            if scoped.get('character_cast') is not None:
                tasks[-1]['cast']={k:v for k,v in scoped['character_cast'].items() if k not in {'characters','crowd_groups'}}
                tasks[-1]['performance_tracks']=shot.get('performance_tracks')
            if scoped.get('scene_staging') is not None:
                tasks[-1]['staging']=scoped['scene_staging']
    result = {'schema_version':4,'plan_sha256':digest(plan),'mode':'motion_vfx_brief_only','status':'REQUEST_ONLY_NOT_EXECUTED',
        'blockers':blockers,'pending_asset_ids':pending,
        'file_verification':'NOT_RUN_BY_BRIEF_EXPORT; production.py check validates authored files before rendering',
        'required_skills':['storyboard-motion-executor','cinematic-motion-director','cinematic-vfx-director'],
        'visual_system':copy.deepcopy(plan.get('visual_system',{})),
        'character_setting_brief':copy.deepcopy(plan.get('production_packet',{}).get('character_setting_brief',{})),
        'setting_blockers':setting_blockers,
        'scene_worlds':plan['production_packet']['illustration_direction']['scene_worlds'],
        'section_objects':{s['id']:{o['id']:copy.deepcopy(o) for o in s['objects']} for s in plan['sections']},
        'asset_registry':{a['id']:copy.deepcopy(a) for a in assets}, 'tasks':tasks,
        'execution_order':['Register and review each separate asset; verify native resources and alpha/anchors.',
            'Mount each shared scene once by ID, layer, scale and named anchors. Change shot framing without rebuilding/resetting its geography or offscreen cast.',
            'Author per-object trigger/response/secondary/settle/exit_state and camera intent against measured section time.',
            'Expand only declared VFX events into source/transport/contact/light/aftermath inside that assembly.',
            'Keep object/event states across cuts and nonsequential seeks; preview and inspect the actual encoded clip.'],
        'instruction':'Export is a planning handoff. Missing ledger/camera/source evidence blocks authored rendering; technical validity never supplies visual/motion/VFX/listening PASS.'}
    if character_direction(plan) is not None:
        result['character_direction']=copy.deepcopy(character_direction(plan))
        result['scene_cast_inventory']=scene_cast_inventory(plan)
        if any(c.get('unresolved') for c in result['character_direction']['characters']+result['character_direction']['crowd_groups']):
            blockers.append('CHARACTER_DESIGN_CHOICES_UNRESOLVED')
        result['execution_order'].insert(2,'Execute the declared cast state sequence and gaze; use absolute-frame pose_track for 2D replacements, native facial/articulation controls for 3D. Keep anonymous groups at their declared population and shared behavior.')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    rows=['# Motion / VFX assembly brief\n',result['instruction'],
        '\nBlockers: '+(', '.join(blockers) or 'No metadata blockers; file/runtime/media review still required'),
        '\n## Execution order\n',*['- '+step for step in result['execution_order']]]
    if setting_blockers:
        rows.extend(['\n## Setting decisions pending\n',*['- '+q for q in setting_blockers]])
    for task in tasks:
        rows.extend(['\n## '+task['shot_id'], '\nPurpose: '+str(task['purpose']),
            '\nAction: '+str(task['action']), '\nFocus: '+', '.join(task['focus']),
            '\nCamera: '+str(task['camera']['purpose']), '\nSound: '+str(task['sound']),
            '\nMount: '+', '.join(i['object_id']+' ← '+', '.join(i['illustration'].get('asset_ids',[])) for i in task['instances']),
            '\nMotion: '+task['motion_status'], '\nVFX: '+(', '.join(e['id'] for e in task['vfx']) or 'none requested; do not add decorative effects'),
            '\nHandoff: '+str(task['handoff']['reason'])])
        if 'staging' in task:
            stage=task['staging']
            rows.extend(['\nShared scene view: '+stage['view']['id']+' ('+stage['view']['kind']+'); plate='+stage['view']['plate_object_id'],
                '\nOutside this shot: '+(', '.join(stage['outside_this_shot_object_ids']) or 'none declared')+'; preserve continuity.',
                '\nStory link: '+stage['story_link']['link_kind'],
                '\nReadable static details: '+(', '.join(d['id'] for d in stage['static_details']) or 'none declared')])
        if 'cast' in task:
            rows.append('\nPeople represented: '+str(task['cast']['total_visible_people']))
            rows.extend('- '+e['object_id']+': '+' -> '.join(e['state_ids'])+'; '+e['blocking']+
                '; '+('count='+str(e['count']) if 'count' in e else 'gaze='+e['gaze_target']+'; state gaze='+str(e.get('gaze_targets',{}))) for e in task['cast']['entries'])
    output.with_suffix('.md').write_text('\n'.join(rows)+'\n')
    return result
