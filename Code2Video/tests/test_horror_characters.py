"""Ensemble/acting contract regressions. Fixtures never approve art or a scare."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'src')]
from local_tools.production import read_plan
from horror_assets import write_asset_briefs
from horror_motion import write_motion_brief
from horror_characters import (validate_character_direction, validate_character_assets,
    resolve_character_cast, scene_cast_inventory, character_asset_fingerprint,
    character_asset_current, performance_at, validate_cast_sample)
from horror_sprites import validate_binding, sprite_state
from illustration_direction import resolve_shot_direction
from v4_contract import digest, visual_reference_policy
from v4_execution import validate_runtime_samples
from v4_quality import review_targets
from kage_fixture import kage_plan


def unit_tracks(plan):
    """In-memory authored-time fixture; no measured speech or film approval."""
    plan['phase']='authored'
    registry=plan['production_packet']['character_direction']
    for definition in registry['characters']+registry['crowd_groups']:
        definition['unresolved']=[]
        definition['decision_status']='UNIT_FIXTURE_ONLY_NOT_FILM_APPROVAL'
    objects={o['id']:o for o in plan['sections'][0]['objects']}
    assets={a['id']:a for a in plan['horror']['assets']}
    for shot in plan['sections'][0]['shots']:
        start=int(shot['planning_window']['start_seconds']*60)
        end=int(shot['planning_window']['end_seconds']*60)
        shot.update(start_frame=start,end_frame=end)
        shot['performance_tracks']={}
        shot['sprite_bindings']=[]
        for entry in shot['cast']:
            keys=[{'frame':start+i*(end-start)//len(entry['state_ids']),'state_id':sid}
                  for i,sid in enumerate(entry['state_ids'])]
            shot['performance_tracks'][entry['object_id']]=keys
            for aid in objects[entry['object_id']]['illustration']['asset_ids']:
                asset=assets[aid]
                poses=next(v for v in asset['views'] if v['id']==entry['view_id'])['frames']
                selected=[next(p for p in poses if k['state_id'] in p['performance_state_ids']
                    and ('count' not in entry or p.get('member_count')==entry['count'])) for k in keys]
                shot['sprite_bindings'].append({'object_id':entry['object_id'],'asset_id':aid,'view_id':entry['view_id'],
                    'loop':False,'start_frame':start,'end_frame':end,'contact_windows':[],
                    'root_track':[{'frame':start,'position':[500,600]},{'frame':end,'position':[500,600]}],
                    'pose_track':[{'frame':k['frame'],'pose_id':p['id'],'performance_state_id':k['state_id']} for k,p in zip(keys,selected)]})
    for asset in assets.values():
        expected=character_asset_fingerprint(plan,asset)
        if expected:asset['character_design_sha256']=expected


class CharacterTests(unittest.TestCase):
    def setUp(self):
        self.plan=read_plan(ROOT/'examples/horror-ensemble-draft.json')
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)

    def test_multiple_principals_and_changing_crowd_are_explicit(self):
        validate_character_direction(self.plan)
        registry=self.plan['production_packet']['character_direction']
        self.assertEqual(sum(c['importance']=='principal' for c in registry['characters']),2)
        inventory=scene_cast_inventory(self.plan)
        self.assertEqual(len(inventory),1)
        self.assertEqual([s['total_visible_people'] for s in inventory[0]['shots']],[9,4,1])
        self.assertEqual([s['crowd_count'] for s in inventory[0]['shots']],[6,2,0])
        self.assertFalse(self.plan['technical_fixture'])

    def test_zero_character_shots_and_unselected_template_stay_valid(self):
        p=read_plan(ROOT/'examples/horror-light-washer-draft.json')
        template=json.loads((ROOT/'examples/horror-profile-template.json').read_text())
        p['production_packet']['character_direction']=template['production_packet']['character_direction']
        validate_character_direction(p)
        self.assertEqual([s['total_visible_people'] for s in scene_cast_inventory(p)[0]['shots']],[0,0,0])
        self.assertIsNone(template['cast']['narrator'])
        self.assertEqual(template['production_packet']['character_direction']['characters'],[])

    def test_missing_invisible_unknown_or_unregistered_actor_is_rejected(self):
        mutations=[lambda p:p['sections'][0]['shots'][0]['cast'].pop(),
            lambda p:p['sections'][0]['shots'][2]['cast'].append(copy.deepcopy(p['sections'][0]['shots'][0]['cast'][1])),
            lambda p:p['sections'][0]['shots'][0]['cast'][0].update(state_ids=['missing']),
            lambda p:p['sections'][0]['objects'][-4].pop('character_id'),
            lambda p:p['production_packet'].pop('character_direction'),
            lambda p:(p['production_packet']['illustration_direction'].update(authoring_mode='full'),p['production_packet'].pop('character_direction'))]
        for mutate in mutations:
            bad=copy.deepcopy(self.plan);mutate(bad)
            with self.assertRaises(ValueError):validate_character_direction(bad)

    def test_an_individually_significant_extra_must_be_promoted(self):
        for field in ['speaking','independent_action','individual_focus']:
            bad=copy.deepcopy(self.plan)
            bad['sections'][0]['shots'][0]['cast'][-1][field]=True
            with self.assertRaisesRegex(ValueError,'Promote'):validate_character_direction(bad)
        shot=self.plan['sections'][0]['shots'][0]
        shot['attention'].append('onlookers')
        with self.assertRaisesRegex(ValueError,'collective'):validate_character_direction(self.plan)
        shot['cast'][-1]['focus_mode']='collective'
        validate_character_direction(self.plan)

    def test_crowd_count_and_per_state_gaze_are_checked(self):
        for count in [0,-2,True,2.5]:
            bad=copy.deepcopy(self.plan);bad['sections'][0]['shots'][0]['cast'][-1]['count']=count
            with self.assertRaises(ValueError):validate_character_direction(bad)
        note=self.plan['sections'][0]['shots'][1]['cast'][1]
        note['gaze_targets']['steady']='unregistered_target'
        with self.assertRaises(ValueError):validate_character_direction(self.plan)

    def test_design_face_detail_belongs_to_illustration_not_storyboard(self):
        character=self.plan['production_packet']['character_direction']['characters'][0]
        character['design'].pop('face_features')
        validate_character_direction(self.plan)
        with self.assertRaisesRegex(ValueError,'face_features'):write_asset_briefs(self.plan,self.folder/'bad.json')
        self.assertFalse((self.folder/'bad.json').exists())
        character['design']['face_features']='Original recognizable face controls'
        character['states'][0]['expression'].pop('brows')
        with self.assertRaisesRegex(ValueError,'brows'):write_asset_briefs(self.plan,self.folder/'bad.json')

    def test_missing_expression_view_or_group_population_blocks_export(self):
        mutations=[lambda p:p['horror']['assets'][4]['views'][0]['frames'].pop(),
            lambda p:p['sections'][0]['shots'][1]['cast'][0].update(view_id='back'),
            lambda p:p['sections'][0]['shots'][0]['cast'][-1].update(count=5)]
        for mutate in mutations:
            bad=copy.deepcopy(self.plan);mutate(bad)
            with self.assertRaises(ValueError):write_asset_briefs(bad,self.folder/'bad.json')
            self.assertFalse((self.folder/'bad.json').exists())

    def test_image_prompt_contains_only_its_performance_and_exact_group_count(self):
        character=self.plan['production_packet']['character_direction']['characters'][0]
        character['states'][-1]['expression']['eyes']='LATER_REVEAL_MARKER; only allowed in this later state'
        exported=write_asset_briefs(self.plan,self.folder/'illustration.json')
        self.assertEqual(len(exported['tasks']),12)
        quiet=next(t for t in exported['tasks'] if t['asset_id']=='art_observer_a' and t['pose_id']=='quiet')
        afraid=next(t for t in exported['tasks'] if t['asset_id']=='art_observer_a' and t['pose_id']=='afraid')
        self.assertNotIn('LATER_REVEAL_MARKER',quiet['prompt'])
        self.assertIn('LATER_REVEAL_MARKER',afraid['prompt'])
        self.assertIn('single still',afraid['prompt'])
        self.assertNotIn('Entry state: quiet',afraid['prompt'])
        groups=[t for t in exported['tasks'] if t['asset_id']=='art_onlookers']
        self.assertIn('exactly 6',groups[0]['prompt']);self.assertIn('exactly 2',groups[1]['prompt'])
        self.assertEqual(len(exported['generation_blockers']),4)
        self.assertIn('pending before generation',(self.folder/'illustration.md').read_text())
        room=next(t for t in exported['tasks'] if t['asset_id']=='art_room_bg')
        self.assertIn('empty wall socket',room['prompt'])

    def test_motion_export_preserves_cast_but_never_executes_or_approves_it(self):
        result=write_motion_brief(self.plan,self.folder/'motion.json')
        self.assertEqual([t['cast']['total_visible_people'] for t in result['tasks']],[9,4,1])
        self.assertEqual(len(result['asset_registry']),8)
        self.assertEqual(len(result['character_direction']['characters']),3)
        self.assertEqual(result['tasks'][1]['cast']['entries'][1]['gaze_targets'],{'steady':'washer_hatch'})
        self.assertIsNone(result['tasks'][0]['performance_tracks'])
        self.assertIn('CHARACTER_DESIGN_CHOICES_UNRESOLVED',result['blockers'])
        self.assertEqual(result['status'],'REQUEST_ONLY_NOT_EXECUTED')

    def test_design_and_expression_changes_invalidate_registered_art_binding(self):
        asset=self.plan['horror']['assets'][4]
        expected=character_asset_fingerprint(self.plan,asset)
        write_asset_briefs(self.plan,self.folder/'requests.json')
        self.assertNotIn('character_design_sha256',asset)  # request export cannot register art
        self.assertFalse(character_asset_current(self.plan,asset))
        asset['character_design_sha256']=expected
        self.assertTrue(character_asset_current(self.plan,asset))
        self.plan['production_packet']['character_direction']['characters'][0]['states'][0]['expression']['mouth']='changed restrained mouth'
        self.assertFalse(character_asset_current(self.plan,asset))

    def test_valid_cropped_subset_reuses_art_but_age_and_style_changes_invalidate_it(self):
        asset=self.plan['horror']['assets'][4]
        asset['character_design_sha256']=character_asset_fingerprint(self.plan,asset)
        self.plan['sections'][0]['shots']=self.plan['sections'][0]['shots'][:2]
        self.assertTrue(character_asset_current(self.plan,asset))
        self.plan['production_packet']['character_setting_brief']['approved_visual_age_bands']={'observer_a_design':[40,45]}
        self.assertFalse(character_asset_current(self.plan,asset))
        asset['character_design_sha256']=character_asset_fingerprint(self.plan,asset)
        self.plan['horror']['style_bible']['proportions']='Changed original face/head proportions'
        self.assertFalse(character_asset_current(self.plan,asset))

    def test_authored_state_sequence_needs_absolute_tracks_and_every_component_binding(self):
        unit_tracks(self.plan)
        validate_character_assets(self.plan)
        shot=self.plan['sections'][0]['shots'][1]
        shot['performance_tracks']['observer_a'].pop()
        with self.assertRaisesRegex(ValueError,'sequence'):validate_character_direction(self.plan)
        unit_tracks(self.plan)
        shot['sprite_bindings'].pop()
        with self.assertRaisesRegex(ValueError,'sprite binding'):validate_character_assets(self.plan)

    def test_unresolved_choices_and_unexplained_expression_reset_block_authored_production(self):
        unit_tracks(self.plan)
        character=self.plan['production_packet']['character_direction']['characters'][0]
        character['unresolved']=['Actual visible age still unresolved']
        with self.assertRaisesRegex(ValueError,'Resolve explicit'):validate_character_direction(self.plan)
        character['unresolved']=[]
        last=self.plan['sections'][0]['shots'][2]
        last['cast'][0]['state_ids']=['quiet']
        last['performance_tracks']['observer_a'][0]['state_id']='quiet'
        with self.assertRaisesRegex(ValueError,'entry_change_reason'):validate_character_direction(self.plan)
        last['cast'][0]['entry_change_reason']='Unit-only deliberate off-screen explanation; not film approval'
        validate_character_direction(self.plan)

    def test_selected_crowd_variant_and_actor_pose_track_must_match_intent(self):
        unit_tracks(self.plan)
        shot=self.plan['sections'][0]['shots'][1]
        group=next(b for b in shot['sprite_bindings'] if b['object_id']=='onlookers')
        group['pose_track'][0]['pose_id']='six_watch'
        with self.assertRaisesRegex(ValueError,'population'):validate_character_assets(self.plan)
        group['pose_track'][0]['pose_id']='two_watch'
        actor=next(b for b in shot['sprite_bindings'] if b['object_id']=='observer_a')
        actor['pose_track'][0]['performance_state_id']='afraid'
        with self.assertRaisesRegex(ValueError,'performance track'):validate_character_assets(self.plan)

    def test_absolute_pose_selection_retains_contacts_and_agrees_on_nonsequential_seeks(self):
        asset=self.plan['horror']['assets'][4]
        binding={'view_id':'front','loop':False,'start_frame':100,'end_frame':160,
            'root_track':[{'frame':100,'position':[100,100]},{'frame':160,'position':[200,100]}],
            'contact_windows':[{'start_frame':100,'end_frame':160,'socket':'ground','world_position':[115,130]}],
            'pose_track':[{'frame':100,'pose_id':'quiet','performance_state_id':'quiet'},
                          {'frame':120,'pose_id':'listening','performance_state_id':'listening'},
                          {'frame':140,'pose_id':'afraid','performance_state_id':'afraid'}]}
        validate_binding(asset,binding)
        frames=[125,100,119,149,125,160]
        py=[sprite_state(asset,binding,f) for f in frames]
        self.assertEqual(py[0],py[4]);self.assertEqual(py[0]['pose_id'],'listening')
        self.assertEqual(py[3]['performance_state_id'],'afraid')
        self.assertFalse(py[-1]['visible'])
        for value in py[:-1]:
            pose=next(p for p in asset['views'][0]['frames'] if p['id']==value['pose_id'])
            self.assertEqual([value['image_position'][i]+pose['ground_anchor'][i] for i in range(2)],[115,130])
        args=json.dumps({'asset':asset,'binding':binding,'frames':frames})
        code="import {spriteState} from './runtime/horror-sprites.mjs'; const d=JSON.parse(process.argv[1]); console.log(JSON.stringify(d.frames.map(f=>spriteState(d.asset,d.binding,f))));"
        js=json.loads(subprocess.check_output(['node','--input-type=module','-e',code,args],cwd=ROOT,text=True))
        self.assertEqual(js,py)
        for mutate in [lambda b:b.update(loop=True),lambda b:b['pose_track'][1].update(pose_id='missing'),
                       lambda b:b['pose_track'][1].update(frame=100),lambda b:b['pose_track'][1].update(performance_state_id='afraid')]:
            bad=copy.deepcopy(binding);mutate(bad)
            with self.assertRaises(ValueError):validate_binding(asset,bad)

    def test_runtime_requires_observed_state_gaze_and_population(self):
        unit_tracks(self.plan)
        section=self.plan['sections'][0];shot=section['shots'][0]
        shot['execution']={'review_frames':[0,200],'objects':{oid:{'layout':{'overlap_policy':'intentional'}} for oid in shot['object_ids']}}
        c={'shot':shot,'resolved_direction':resolve_shot_direction(self.plan,section,shot)}
        c['resolved_direction']['behaviors']={oid:{'exit_state':{'condition':'supported'}} for oid in shot['object_ids']}
        c['contract_sha256']=digest(c)
        def sample(frame):
            return {'shot':shot['id'],'frame':frame,'contract_sha256':c['contract_sha256'],'object_ids':shot['object_ids'],
                'pattern_kind':shot['pattern']['kind'],'bounds':{oid:[10+i*150,10,100,100] for i,oid in enumerate(shot['object_ids'])},
                'camera':{'transform':[1,0,0,1,0,0],'target_object':'loose_plug'},
                'object_states':{oid:{'condition':'supported'} for oid in shot['object_ids']},
                'visibility':{oid:{'opacity':1,'hidden':False} for oid in shot['object_ids']},'event_phases':{},
                'cast_states':{e['object_id']:performance_at(c,e['object_id'],frame) for e in shot['cast']}}
        observations=[sample(f) for f in [0,200]]
        log='\n'.join('V4_EXECUTION_SAMPLE '+json.dumps(s) for s in observations)
        self.assertEqual(len(validate_runtime_samples(c,log)),2)
        for mutate in [lambda s:s['cast_states'].pop('attendant'),
                       lambda s:s['cast_states']['observer_a'].update(state_id='afraid'),
                       lambda s:s['cast_states']['observer_b'].update(gaze_target='washer_hatch'),
                       lambda s:s['cast_states']['onlookers'].update(member_count=2)]:
            bad=sample(0);mutate(bad)
            with self.assertRaises(ValueError):validate_cast_sample(c,bad)

    def test_browser_native_control_intent_matches_python(self):
        browser=ROOT/'local_tools/v4_smoke/browser'
        if not (browser/'node_modules/typescript').is_dir():
            self.skipTest('Install fixture dev dependencies to compare the TypeScript runtime')
        unit_tracks(self.plan)
        section=self.plan['sections'][0];shot=section['shots'][1]
        c={'shot':shot,'resolved_direction':resolve_shot_direction(self.plan,section,shot)}
        frames=[700,300,500,719,300]
        code="""const fs=require('node:fs'), ts=require('typescript'), Module=require('node:module');
const source=fs.readFileSync('src/v4-runtime.ts','utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText;
const m=new Module(process.cwd()+'/src/v4-runtime.cjs');m.filename=process.cwd()+'/src/v4-runtime.cjs';m.paths=module.paths;m._compile(compiled,m.filename);
const d=JSON.parse(process.argv[1]);console.log(JSON.stringify(d.frames.map(f=>Object.fromEntries(d.ids.map(id=>[id,m.exports.performanceAt(d.contract,id,f)])))));"""
        ids=[e['object_id'] for e in shot['cast']]
        js=json.loads(subprocess.check_output(['node','-e',code,json.dumps({'contract':c,'frames':frames,'ids':ids})],cwd=browser,text=True))
        py=[{oid:performance_at(c,oid,f) for oid in ids} for f in frames]
        self.assertEqual(js,py)
        self.assertEqual(py[0]['observer_b']['gaze_target'],'washer_hatch')
        self.assertEqual(py[1]['observer_b']['gaze_target'],'observer_a')

    def test_review_and_scoped_contract_keep_designs_performance_and_horror_tone(self):
        targets=review_targets(self.plan,{'shots':[{'shot':'hatch_reply'}]})
        self.assertIn('character:observer_a_design',targets['visual'])
        self.assertIn('crowd:hatch_reply:onlookers',targets['visual'])
        self.assertIn('performance:hatch_reply:observer_b',targets['motion'])
        self.assertIn('horror_tone:hatch_reply',targets['editorial'])
        section=self.plan['sections'][0];shot=section['shots'][2]
        scoped=resolve_shot_direction(self.plan,section,shot)
        self.assertEqual(set(scoped['character_cast']['characters']),{'observer_a_design'})
        before=digest(scoped)
        self.plan['production_packet']['character_direction']['characters'][0]['design']['face_features']='changed visible face'
        self.assertNotEqual(before,digest(resolve_shot_direction(self.plan,section,shot)))
        self.assertTrue(visual_reference_policy(self.plan)['kage']['enabled'])
        self.assertTrue(visual_reference_policy(self.plan)['oversimplified']['enabled'])

    def test_native_character_performance_preserves_the_full_3d_request(self):
        native=copy.deepcopy(kage_plan()['horror']['assets'][1])
        original=self.plan['horror']['assets'][4]
        native.update(id=original['id'],object_id=original['object_id'],identity=original['identity'],
            illustration_role='character_model',scene_ids=['utility_room'])
        model=native['model_spec']
        model.update(dimensions={'unit':'metres','size':[.6,1.8,.3]},
            parts=[{'id':part,'parent_id':None if part=='torso' else 'torso','pivot':[0,0,0],'material_region':'authored_body'}
                   for part in ['torso','head','left_arm','right_arm','left_leg','right_leg']],
            anchors={'ground':[0,0,0],'head':[0,1.5,0],'left_grip':[-.3,1,0],'right_grip':[.3,1,0]},
            surface_regions=['authored_body'],texture_plan=[{'region':'authored_body','method':'original authored face/costume surfaces'}],
            articulation='Native humanoid controls and facial variants must support the requested state; request only, no fabricated source.',
            closest_camera_use='principal face/hand medium close inspection',
            variants=[{'id':sid,'performance_state_ids':[sid]} for sid in ['quiet','listening','afraid']])
        native['design_semantics'].update(recognition_traits=['original proposed human silhouette and face'],parts_or_layers=[p['id'] for p in model['parts']],
            variants=['quiet','listening','afraid'],closest_camera_use='principal face/hand inspection')
        self.plan['horror']['assets'][4]=native
        self.plan['sections'][0]['objects'][4]['illustration']['route']='3d'
        result=write_asset_briefs(self.plan,self.folder/'native.json')
        task=result['three_d_tasks'][0]
        self.assertIn('3dviz-pro-max',task['required_skills'])
        self.assertIn('performance_state_ids',task['prompt'])
        self.assertEqual(task['status'],'REQUEST_ONLY_NOT_FABRICATED')
        model['variants'].pop()
        with self.assertRaises(ValueError):write_asset_briefs(self.plan,self.folder/'bad-native.json')


if __name__=='__main__':unittest.main()
