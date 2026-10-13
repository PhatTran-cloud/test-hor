"""Mixed-route, causal-context and evidence regressions; no art/model execution."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from kage_fixture import kage_plan
from illustration_direction import validate_direction, validate_model_request, resolve_shot_direction
from horror_assets import write_asset_briefs
from horror_contract import check_horror_files, asset_digest, validate_horror
from horror_snapshot import freeze_native_model
from v4_contract import normalize_v4, shot_contract, digest, sha256
from v4_execution import validate_runtime_samples
from v4_workflow import representative_fingerprint, skill_routes
from v4_quality import review_targets
from prompts.v4 import get_v4_execution_prompt


class KageIllustrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name);self.plan=kage_plan()

    def test_mixed_export_covers_every_component_without_network_or_fabrication(self):
        plan=normalize_v4(self.plan)
        with patch('requests.sessions.Session.request',side_effect=AssertionError('No network')):
            result=write_asset_briefs(plan,self.folder/'prompts.json')
        self.assertEqual(len(result['tasks']),3)
        self.assertEqual(len(result['three_d_tasks']),1)
        task=result['three_d_tasks'][0]
        self.assertEqual(task['provider'],'lowbudget3d')
        self.assertIn('3dviz-pro-max',task['required_skills'])
        self.assertEqual(task['status'],'REQUEST_ONLY_NOT_FABRICATED')
        self.assertIn('UNVERIFIED',task['base_package_status'])
        self.assertIn('quietness is incomplete perception',json.dumps(result['motion_vfx_handoff']))
        inventory=result['shot_inventory'][0]
        self.assertEqual({c['object_id'] for c in inventory['components']},set(plan['sections'][0]['shots'][0]['object_ids']))
        background=next(t for t in result['tasks'] if t['object_id']=='forest_bg')
        self.assertNotIn('#00FF00',background['prompt'])
        self.assertIn('design_semantics',background['prompt'])
        self.assertIn('same practical direction',background['prompt'])
        self.assertTrue((self.folder/'prompts.md').is_file())
        self.assertFalse(any(p.suffix in {'.glb','.png','.mp4'} for p in self.folder.iterdir()))
        self.assertIn('lowbudget3d-illustration-bridge',skill_routes(plan))

    def test_semantic_and_complete_shot_negative_cases_fail_before_export(self):
        mutations=[lambda p:p['sections'][0]['beats'][0]['direction'].pop('metaphor'),
            lambda p:p['sections'][0]['shots'][0]['components']['items'].pop(),
            lambda p:p['sections'][0]['shots'][0]['components'].update(required_roles=['subject'],omissions={}),
            lambda p:p['sections'][0]['shots'][0]['behaviors'].pop('fog'),
            lambda p:p['sections'][0]['shots'][0]['camera'].pop('information_intent'),
            lambda p:p['sections'][0]['shots'][0]['attention_plan'].pop(),
            lambda p:p['sections'][0]['shots'][0]['components']['items'][1].update(route='2d'),
            lambda p:p['production_packet']['illustration_direction']['scene_worlds'][0]['semantic_layers'].pop(),
            lambda p:p['horror']['assets'][0].pop('design_semantics')]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                plan=copy.deepcopy(self.plan);mutate(plan)
                with self.assertRaises(ValueError):write_asset_briefs(plan,self.folder/'bad.json')
                self.assertFalse((self.folder/'bad.json').exists())

    def test_unneeded_roles_have_reasons_without_forcing_prop_or_pose_counts(self):
        shot=self.plan['sections'][0]['shots'][0]
        shot['components']['required_roles'].remove('interactive_prop')
        shot['components']['omissions']={'interactive_prop':'no contact prop in this macro benchmark'}
        shot['components']['items'][1]['roles'].remove('interactive_prop')
        validate_direction(self.plan)

    def test_revision_cannot_bypass_current_artwork_selection_with_a_legacy_label(self):
        self.plan['horror']['artwork_style']='3d_horror_cartoon'
        self.plan['horror']['artwork_provider']='flow'
        with self.assertRaisesRegex(ValueError,'selected Kage hybrid'):normalize_v4(self.plan)

    def test_bad_3d_contract_and_flattened_replacement_are_rejected(self):
        model=self.plan['horror']['assets'][1]
        validate_model_request(model,'draft')
        for mutate in [lambda a:a['model_spec'].pop('anchors'),
                       lambda a:a['model_spec']['dimensions'].update(size=[1,0,1]),
                       lambda a:a['model_spec']['parts'][0].update(parent_id='bole'),
                       lambda a:a['model_spec']['parts'][0].update(pivot=[0,float('inf'),0]),
                       lambda a:a['model_spec'].update(representation='flattened_png')]:
            bad=copy.deepcopy(model);mutate(bad)
            with self.assertRaises(ValueError):validate_model_request(bad,'draft')
        with self.assertRaises(ValueError):validate_model_request(model,'authored')

    def test_authored_native_assets_need_spatial_instance_bindings(self):
        # Synthetic registration exercises the contract, never artwork approval.
        p=copy.deepcopy(self.plan);p['phase']='authored'
        section=p['sections'][0];section['speech']={'frames':120};section['film_start_frame']=0
        shot=section['shots'][0];shot['execution']={'objects':{}}
        for asset in p['horror']['assets']:
            if asset['kind']=='model_3d':
                asset['model_spec'].update(file='fixture.mjs',sha256='fixture hash',resources=[],
                    inspection_evidence=[{'view_id':v['id'],'file':'fixture.png','sha256':'fixture hash'} for v in asset['views']])
            else:
                for view in asset['views']:
                    for pose in view['frames']:pose.update(file='fixture.png',sha256='fixture hash')
            asset['review']={'status':'PASS','reviewer':'synthetic unit fixture',
                'notes':'No actual art; contract test only','asset_digest':asset_digest(asset)}
        with self.assertRaisesRegex(ValueError,'model binding'):validate_horror(p)
        shot['model_bindings']=[{'object_id':'trunk_mg','asset_id':'art_trunk_mg','instance_symbol':'nativeTrunk'}]
        validate_horror(p)
        shot['scene_type']='2d'
        with self.assertRaisesRegex(ValueError,'spatial Three.js'):validate_horror(p)
        shot['scene_type']='3d';shot['renderer']='manim'
        with self.assertRaisesRegex(ValueError,'spatial Three.js'):validate_horror(p)

    def timed_fixture(self):
        p=copy.deepcopy(self.plan);section=p['sections'][0]
        section['speech']={'frames':120,'fps':60};section['state_tracks']=[]
        first=section['shots'][0];first.update(start_frame=0,end_frame=60,duration_frames=60)
        event={'id':'signal_event','kind':'motion','source_object':'insect','target_objects':['leaf_fg'],
            'start_frame':20,'peak_frame':30,'end_frame':100,'carry_across_shots':True,
            'cause':'original signal','action':'UNIQUE_OWNER_ACTION','reaction':'delayed leaf response','aftermath':'same evidence persists'}
        first['events']=[event]
        second=copy.deepcopy(first);second.update(id='macro_follow',start_frame=60,end_frame=120,duration_frames=60,event_ids=['signal_event'])
        second.pop('events')
        first['handoff']['semantic_link']={'to_shot_id':'macro_follow','kind':'causal','relation':'follow the discovered source',
            'invariants':['same insect identity'],'trigger_event_id':'signal_event'}
        second['handoff']['semantic_link']={'to_shot_id':None,'kind':'end','relation':'close macro','invariants':[]}
        section['shots']=[first,second]
        p['production_packet']['representative']['shot_id']='macro_follow'
        return p,section,first,second

    def test_context_and_renderer_share_carried_events_world_and_visual_system(self):
        p,section,first,second=self.timed_fixture()
        context=get_v4_execution_prompt(p,'macro_follow')
        self.assertIn('UNIQUE_OWNER_ACTION',context)
        contract=shot_contract(section,second,p)
        self.assertEqual(contract['shot']['events'][0]['start_frame'],20)
        self.assertEqual(contract['visual_system'],p['visual_system'])
        self.assertEqual(contract['scene_world']['id'],'forest_world')
        self.assertEqual(contract['resolved_direction']['active_events'][0]['id'],'signal_event')
        section['illustration_revision']=1
        with self.assertRaisesRegex(ValueError,'owning plan'):shot_contract(section,second)

    def test_scoped_context_keeps_current_state_and_foreign_event_owner(self):
        p,section,first,second=self.timed_fixture()
        section['film_start_frame']=0
        later=copy.deepcopy(section);later['id']='section_2';later['film_start_frame']=120
        later['shots']=[copy.deepcopy(second)];later['shots'][0]['id']='later_shot'
        later['shots'][0]['events']=[{'id':'later_signal','source_object':'insect','target_objects':['leaf_fg'],
            'start_frame':0,'peak_frame':5,'end_frame':20}]
        next(o for o in later['objects'] if o['id']=='insect')['initial_state']['activity']='future state'
        p['sections'].append(later)
        second['behaviors']['leaf_fg']['trigger']={'kind':'event','ref':'later_signal','phase':'start','reason':'explicit dependency fixture'}
        resolved=resolve_shot_direction(p,section,second)
        self.assertEqual(next(o for o in resolved['objects'] if o['id']=='insect')['initial_state']['activity'],'rest')
        foreign=next(e for e in resolved['dependency_events'] if e['id']=='later_signal')
        self.assertEqual(foreign['owner_section_id'],'section_2')
        self.assertEqual(foreign['owner_film_start_frame'],120)
        self.assertNotIn('later_signal',{e['id'] for e in resolved['active_events']})

    def test_wrong_scene_successor_is_rejected(self):
        p,section,first,second=self.timed_fixture()
        validate_direction(p)
        first['handoff']['semantic_link']['to_shot_id']='invented_scene'
        with self.assertRaises(ValueError):validate_direction(p)

    def test_representative_world_changes_invalidate_but_unrelated_world_does_not(self):
        p,section,first,second=self.timed_fixture()
        p['visual_reference_policy']={'kage':{'enabled':True}}
        (self.folder/'source.tsx').write_text('export function Study(){return null;}\n')
        for shot in section['shots']:shot['render_spec']={'project_dir':str(self.folder),'entry_point':'source.tsx'}
        before=representative_fingerprint(p,self.folder)
        unrelated=copy.deepcopy(p['production_packet']['illustration_direction']['scene_worlds'][0]);unrelated['id']='unused_world'
        p['production_packet']['illustration_direction']['scene_worlds'].append(unrelated)
        self.assertEqual(before,representative_fingerprint(p,self.folder))
        p['production_packet']['illustration_direction']['scene_worlds'][0]['layout']='changed reveal geography'
        self.assertNotEqual(before,representative_fingerprint(p,self.folder))

    def test_directed_runtime_requires_actual_observation_channels(self):
        p,section,first,second=self.timed_fixture()
        second['execution']={'review_frames':[60,119],'objects':{oid:{'layout':{'overlap_policy':'intentional'}} for oid in second['object_ids']}}
        contract=shot_contract(section,second,p);contract['contract_sha256']=digest(contract)
        samples=[]
        for frame in second['execution']['review_frames']:
            samples.append({'shot':second['id'],'frame':frame,'contract_sha256':contract['contract_sha256'],
                'object_ids':second['object_ids'],'pattern_kind':'custom',
                'bounds':{oid:[0,0,300,300] for oid in second['object_ids']}})
        def log(rows):return '\n'.join('V4_EXECUTION_SAMPLE '+json.dumps(s) for s in rows)
        with self.assertRaisesRegex(ValueError,'camera'):validate_runtime_samples(contract,log(samples))
        for sample in samples:
            sample.update(camera={'transform':[1,0,0,1,0,0],'target_object':'insect'},
                object_states={oid:{'activity':'rest'} for oid in second['object_ids']},
                visibility={oid:{'opacity':1,'hidden':False} for oid in second['object_ids']},
                event_phases={'signal_event':'decay'})
        self.assertEqual(len(validate_runtime_samples(contract,log(samples))),2)
        samples[0]['object_states'].pop('fog')
        with self.assertRaisesRegex(ValueError,'state/visibility'):validate_runtime_samples(contract,log(samples))

    def test_review_targets_include_meaning_attention_and_scene_relation(self):
        targets=review_targets(self.plan,{'shots':[{'shot':'forest_open'}]})
        self.assertIn('metaphor:forest_idea',targets['visual'])
        self.assertIn('attention:forest_open',targets['motion'])
        self.assertIn('relation:forest_open',targets['editorial'])

    def test_python_observer_cannot_override_measured_contract_fields(self):
        from types import SimpleNamespace
        from v4_runtime import record_execution
        contract={'shot':{'id':'forest_open'},'resolved_direction':{'contract_revision':1},'contract_sha256':'real hash'}
        observed={'camera':{},'object_states':{},'visibility':{},'event_phases':{},'contract_sha256':'forged hash'}
        with patch.dict(sys.modules,{'manim':SimpleNamespace(config=SimpleNamespace())}):
            with self.assertRaisesRegex(ValueError,'only contain'):record_execution(contract,0,{},'custom',observed)

    def test_native_file_and_inspection_hashes_and_review_digest(self):
        from PIL import Image
        model=copy.deepcopy(self.plan['horror']['assets'][1])
        module=self.folder/'trunk.mjs';module.write_text('export const geometry = {}; // unit integrity fixture\n')
        images=[]
        for view in model['views']:
            path=self.folder/(view['id']+'.png');Image.new('RGB',(16,16),'gray').save(path)
            images.append({'view_id':view['id'],'file':str(path),'sha256':sha256(path)})
        model['model_spec'].update(file=str(module),sha256=sha256(module),inspection_evidence=images,resources=[])
        validate_model_request(model,'authored')
        plan={'profile':'horror-v4.1','phase':'authored','sections':[],'horror':{'assets':[model]}}
        check_horror_files(plan,self.folder)
        before=asset_digest(model)
        model['model_spec']['file']='/relocated/trunk.mjs'
        self.assertEqual(before,asset_digest(model))
        model['model_spec']['file']=str(module)
        module.write_text('changed geometry')
        with self.assertRaisesRegex(ValueError,'changed'):check_horror_files(plan,self.folder)

    def test_native_snapshot_keeps_relative_texture_imports_and_hashes(self):
        from PIL import Image
        asset=copy.deepcopy(self.plan['horror']['assets'][1])
        bundle=self.folder/'native';(bundle/'textures').mkdir(parents=True)
        source=bundle/'trunk.mjs';source.write_text("export const textureURL = new URL('./textures/bark.png', import.meta.url);\n")
        texture=bundle/'textures'/'bark.png';Image.new('RGB',(16,16),'gray').save(texture)
        evidence=[]
        for view in asset['views']:
            image=self.folder/(view['id']+'.png');Image.new('RGB',(16,16),'gray').save(image)
            evidence.append({'view_id':view['id'],'file':str(image),'sha256':sha256(image)})
        asset['model_spec'].update(file=str(source),sha256=sha256(source),bundle_root=str(bundle),
            resources=[{'file':str(texture),'sha256':sha256(texture)}],inspection_evidence=evidence)
        before=asset_digest(asset)
        freeze_native_model(asset,self.folder,self.folder/'run')
        model=asset['model_spec'];model_file=Path(model['file']);texture_file=Path(model['resources'][0]['file'])
        self.assertEqual(texture_file,model_file.parent/'textures'/'bark.png')
        self.assertEqual(sha256(texture_file),sha256(texture))
        self.assertEqual(asset_digest(asset),before)
        check_horror_files({'profile':'horror-v4.1','phase':'authored','sections':[],'horror':{'assets':[asset]}},self.folder)
        asset['model_spec']['resources'][0]['file']=str(texture)
        with self.assertRaisesRegex(ValueError,'outside its bundle'):check_horror_files(
            {'profile':'horror-v4.1','phase':'authored','sections':[],'horror':{'assets':[asset]}},self.folder)


if __name__=='__main__':unittest.main()
