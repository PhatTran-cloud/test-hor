"""Prompt coverage/manual ownership and actual matte pixels, not visual approval."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from horror_assets import write_asset_briefs
from horror_chroma import chroma_key
from horror_contract import validate_horror,check_horror_files
from v4_contract import sha256,visual_reference_policy


def illustration_plan():
    objects=[]; assets=[]
    for i in range(6):
        oid=f'object_{i}'; aid=f'art_{i}'
        objects.append({'id':oid,'illustration':{'method':'generated','asset_ids':[aid]}})
        assets.append({'id':aid,'object_id':oid,'provider':'flow',
            'kind':'sprite_sequence' if i==0 else 'layer' if i==5 else 'prop',
            'illustration_role':'character_part' if i==0 else 'background' if i==5 else 'prop',
            'requires_alpha':i!=5,'scene_ids':['room'],
            'identity':'Test component, consistent identity; not production art',
            'action':{'intent':'Guard the door','mechanics':'Hand on hinge-side edge',
                'entry_state':'alert','exit_state':'holding','source_ids':['inspected_source'],'contact_requirements':[]},
            'views':[{'id':'front','camera_region':'front','frames':[{
                'id':'pose','description':'Concerned eyes, braced support','width':256,'height':256,
                'root_anchor':[128,128],'ground_anchor':[128,256],'sockets':{},'hold_frames':12}]}]})
    assets[0]['views'][0]['frames'].append({**assets[0]['views'][0]['frames'][0],'id':'reaction','description':'Eyes toward door, mouth closed'})
    objects.append({'id':'limb','illustration':{'method':'procedural','reason':'Authored thin vector limb attached at measured joints'}})
    return {'profile':'horror-v4.1','phase':'draft','language_id':'vi','tts_speed':1,
        'content_profile':{'genre':'horror','kind':'storytelling_rich'},
        'cast':{'library':'unused_fixture','narrator':'unused_fixture','characters':{}},
        'horror':{'artwork_style':'2d_flat_geometric_vector','artwork_provider':'flow','kage_reference':False,
            'visual_reference':{'primary':'oversimplified'},
            'illustrator':{'mode':'prompt_export_only','generation_operator':'human user','model':'Nano Banana 2.1','chroma_key_color':'#00FF00'},
            'voice_provider':'omnivoice','sfx_provider':'stable_audio_3_small_sfx',
            'style_bible':dict.fromkeys(['canonical_prompt','proportions','materials','lighting','depth','identity_rules'],'Simple expressive 2D illustration with drawn shadows'),
            'assets':assets},
        'production_packet':{'visual_style_decision':{'status':'USER_SELECTED','selected_style':'2d_flat_geometric_vector',
            'primary_reference':'oversimplified','authorization':{'reviewer':'human user','request':'Follow OverSimplified storytelling'}},
            'character_setting_brief':{'approved_setting':{'era':'Contemporary Vietnam'},'approved_visual_age_bands':{'vien':[22,25]},
                'flow_agent_research':{'production_application':'Historical mandatory 3D/Kage is no longer active'}},
            'research':{'sources':[{'id':'inspected_source'}]},
            'illustration_direction':{'scene_worlds':[{'id':'room','layout':'two adjacent beds; side window; courtyard door',
                'perspective':'shared eye level','lighting':'same window direction','required_props':['bed','door'],'crop_safety':'clean doorway margin'}]}},
        'sections':[{'id':'section','objects':objects,'sfx_cues':[],
            'shots':[{'id':'shot','scene_id':'room','object_ids':[o['id'] for o in objects]}]}]}


class IllustrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name); self.plan=illustration_plan()

    def test_prompt_export_covers_parts_props_and_opaque_world_without_network(self):
        with patch('requests.sessions.Session.request',side_effect=AssertionError('No network permitted')):
            result=write_asset_briefs(self.plan,self.folder/'prompts.json')
        self.assertEqual(len(result['tasks']),7)
        self.assertEqual([len(b) for b in result['batches']],[5,2])
        self.assertEqual(result['style'],self.plan['horror']['artwork_style'])
        self.assertEqual({t['object_id'] for t in result['tasks']},{f'object_{i}' for i in range(6)})
        background=result['tasks'][-1]
        self.assertFalse(background['requires_alpha']); self.assertEqual(background['output_format'],'provider_original')
        self.assertIn('complete empty environment',background['prompt'])
        self.assertNotIn('#00FF00',background['prompt'])
        self.assertIn('two adjacent beds',background['prompt'])
        self.assertNotIn('Historical mandatory',background['prompt'])
        for task in result['tasks'][:-1]: self.assertEqual(task['source_background'],'#00FF00')
        self.assertIn('Eyes toward door',result['tasks'][1]['prompt'])
        exported=json.loads((self.folder/'prompts.json').read_text(encoding='utf-8'))
        self.assertEqual(exported,result)
        self.assertTrue((self.folder/'prompts.md').is_file())

    def test_incomplete_background_object_pose_world_and_ownership_block_export(self):
        mutations=[lambda p:p['sections'][0]['objects'][-2].pop('illustration'),
            lambda p:p['horror']['assets'].pop(),
            lambda p:p['horror']['assets'][0]['views'][0].update(frames=[]),
            lambda p:p['sections'][0]['shots'][0].update(scene_id='another_room'),
            lambda p:p['sections'][0]['objects'][0]['illustration'].update(asset_ids=['art_1']),
            lambda p:p['horror']['assets'][0].update(requires_alpha=False)]
        for mutate in mutations:
            bad=copy.deepcopy(self.plan); mutate(bad)
            with self.assertRaises(ValueError): write_asset_briefs(bad,self.folder/'bad.json')
            self.assertFalse((self.folder/'bad.json').exists())

    def test_current_reference_and_human_illustrator_are_enforced(self):
        validate_horror(self.plan)
        policy=visual_reference_policy(self.plan)
        self.assertTrue(policy['oversimplified']['enabled']); self.assertFalse(policy['kage']['enabled'])
        for mutate in [lambda p:p['production_packet']['visual_style_decision'].pop('primary_reference'),
                       lambda p:p['horror']['illustrator'].update(mode='automatic')]:
            bad=copy.deepcopy(self.plan); mutate(bad)
            with self.assertRaises(ValueError): validate_horror(bad)

    def two_shots(self):
        shot=self.plan['sections'][0]['shots'][0]
        following=copy.deepcopy(shot); following['id']='close'
        self.plan['sections'][0]['shots'].append(following)
        return shot,following

    def test_pose_scope_exports_the_correct_shot_and_single_moment(self):
        self.two_shots()
        asset=self.plan['horror']['assets'][0]
        asset['shot_ids']=['shot','close']
        asset['views'][0]['shot_ids']=['shot','close']
        asset['views'][0]['frames'][0].update(shot_ids=['shot'])
        asset['views'][0]['frames'][1].update(shot_ids=['close'],image_constraints=['Eyes toward the closed door; no figure behind it'])
        result=write_asset_briefs(self.plan,self.folder/'prompts.json')
        self.assertEqual(result['tasks'][0]['shot_ids'],['shot'])
        self.assertEqual(result['tasks'][1]['shot_ids'],['close'])
        self.assertEqual(result['tasks'][1]['scene_ids'],['room'])
        self.assertIn('exactly one image',result['tasks'][1]['prompt'])
        self.assertIn('no figure behind it',result['tasks'][1]['prompt'])
        self.assertIn('Shots: close',(self.folder/'prompts.md').read_text())

    def test_unknown_duplicate_and_out_of_parent_scope_fail_before_export(self):
        self.two_shots()
        for mutate in [lambda p:p['horror']['assets'][0].update(shot_ids=['missing']),
                       lambda p:p['horror']['assets'][0].update(shot_ids=['shot','shot']),
                       lambda p:p['horror']['assets'][0]['views'][0].update(shot_ids=[]),
                       lambda p:p['horror']['assets'][0]['views'][0]['frames'][0].update(image_constraints='not a list'),
                       lambda p:(p['horror']['assets'][0].update(shot_ids=['shot']),
                                 p['horror']['assets'][0]['views'][0].update(shot_ids=['close']))]:
            bad=copy.deepcopy(self.plan); mutate(bad)
            with self.assertRaises(ValueError): write_asset_briefs(bad,self.folder/'bad.json')
            self.assertFalse((self.folder/'bad.json').exists())

    def test_every_generated_object_needs_scoped_coverage_in_each_visible_shot(self):
        self.two_shots()
        self.plan['horror']['assets'][0]['shot_ids']=['shot']
        with self.assertRaisesRegex(ValueError,'close.*object_0.*no scoped'):
            write_asset_briefs(self.plan,self.folder/'bad.json')
        self.assertFalse((self.folder/'bad.json').exists())

    def test_separate_assets_can_cover_the_same_object_in_different_scene_worlds(self):
        _,following=self.two_shots(); following.update(scene_id='other_room',object_ids=['object_0'])
        world=copy.deepcopy(self.plan['production_packet']['illustration_direction']['scene_worlds'][0])
        world.update(id='other_room',layout='door on the opposite wall, same character identity')
        self.plan['production_packet']['illustration_direction']['scene_worlds'].append(world)
        extra=copy.deepcopy(self.plan['horror']['assets'][0]); extra.update(id='art_other_view',scene_ids=['other_room'])
        self.plan['horror']['assets'].append(extra)
        self.plan['sections'][0]['objects'][0]['illustration']['asset_ids'].append('art_other_view')
        result=write_asset_briefs(self.plan,self.folder/'prompts.json')
        self.assertEqual(result['tasks'][0]['shot_ids'],['shot'])
        self.assertEqual(result['tasks'][-1]['shot_ids'],['close'])
        self.assertNotIn('opposite wall',result['tasks'][0]['prompt'])
        self.assertIn('opposite wall',result['tasks'][-1]['prompt'])

    def test_image_prompt_gets_reveal_ceiling_without_internal_or_future_truth(self):
        shot=self.plan['sections'][0]['shots'][0]
        shot['storyboard']={'function':'Listen near the door','framing':'medium, door on right','attention':'closed doorway',
            'staging':{'fg':[],'mg':['object_0'],'bg':['object_5'],'screen_direction':'hero left of door','eyelines':'toward right'},
            'primary_action':'INTERNAL_ACTION_NOTE','start_state':{'object_0':'alert'},'end_state':{'object_0':'watching'},
            'information':{'reveal_ceiling':'closed door only, no entity', 'withheld':['SECRET_ENTITY'],
                           'character_out':'SECRET_CHARACTER_TRUTH'},
            'transition':{'next_delta':'SECRET_FUTURE_REVEAL'}}
        world=self.plan['production_packet']['illustration_direction']['scene_worlds'][0]
        world.update(internal_truth='SECRET_WORLD_TRUTH',future_reveal='SECRET_FUTURE_WORLD')
        brief=self.plan['production_packet']['character_setting_brief']
        brief.update(script_facts={'plot':'SECRET_SCRIPT_ENDING'},physical_facts={'object_0':'plain cotton costume'},
                     state_design_correction={'grandmother':'SECRET_LATER_TRANSFORMATION'})
        result=write_asset_briefs(self.plan,self.folder/'prompts.json')
        for task in result['tasks']:
            self.assertIn('closed door only, no entity',task['prompt'])
            self.assertIn('plain cotton costume',task['prompt'])
            self.assertNotIn('SECRET_',task['prompt'])
            self.assertNotIn('INTERNAL_ACTION_NOTE',task['prompt'])
        usage=result['tasks'][0]['storyboard_usage'][0]
        self.assertEqual(usage['primary_action'],'INTERNAL_ACTION_NOTE')
        self.assertEqual(usage['entry_state'],'alert')
        self.assertEqual(usage['exit_state'],'watching')

    def test_flow_submit_rejects_before_loading_a_plan_or_using_network(self):
        from flow_assets import submit
        with patch('requests.sessions.Session.request',side_effect=AssertionError('No network permitted')):
            with self.assertRaisesRegex(ValueError,'human user'): submit({},self.folder/'receipt.json')
        command=[sys.executable,str(ROOT/'local_tools/production.py'),'flow-submit','missing-plan.json','--output',str(self.folder/'receipt.json')]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0); self.assertIn('human user runs Flow',result.stderr)
        self.assertNotIn('FileNotFoundError',result.stderr)
        self.assertFalse((self.folder/'receipt.json').exists())

    def test_authoring_context_routes_to_current_illustration_and_remotion(self):
        from prompts.v4 import get_v4_direction_prompt,get_v4_execution_prompt
        from v4_workflow import skill_routes
        shot=self.plan['sections'][0]['shots'][0]
        shot.update(renderer='remotion',scene_type='2d',beat_ids=['beat'],handoff={'type':'cut'})
        self.plan['sections'][0]['beats']=[{'id':'beat'}]
        context=get_v4_execution_prompt(self.plan,'shot')
        direction=get_v4_direction_prompt(self.plan,{},'Unit fiction')
        for text in [context,direction]:
            self.assertIn('Illustration direction: OverSimplified storytelling for horror',text)
            self.assertNotIn('# Kage Visual Reference',text)
        routes=skill_routes(self.plan)
        self.assertIn('remotion-best-practices',routes); self.assertNotIn('lowbudget3d',routes)

    def test_key_pixels_holes_thin_black_limb_partial_edge_and_source_preservation(self):
        pixels=np.zeros((16,16,4),dtype=np.uint8); pixels[:]=[0,255,0,255]
        pixels[3:13,3:13]=[220,20,20,255]; pixels[5:7,5:7]=[0,255,0,255]
        pixels[2,4:12]=[0,0,0,255]; pixels[3,3]=[10,190,10,255]
        pixels[12,12]=[220,20,20,128]
        source=self.folder/'source.png'; Image.fromarray(pixels).save(source); before=sha256(source)
        output=self.folder/'cutout.png'; receipt=chroma_key(source,output)
        keyed=np.array(Image.open(output)); self.assertEqual(sha256(source),before)
        self.assertEqual(keyed[0,0,3],0); self.assertEqual(keyed[5,5,3],0)
        self.assertEqual(keyed[2,6,3],255); self.assertEqual(list(keyed[8,8]),[220,20,20,255])
        self.assertGreater(keyed[3,3,3],0); self.assertLess(keyed[3,3,3],255)
        self.assertLessEqual(keyed[3,3,1],max(keyed[3,3,0],keyed[3,3,2]))
        self.assertEqual(keyed[12,12,3],128)
        self.assertEqual(receipt['review']['status'],'UNVERIFIED')
        self.assertEqual(receipt['output_sha256'],sha256(output))
        self.assertTrue(np.array_equal(np.array(Image.open(receipt['mask'])),keyed[:,:,3]))

    def test_bad_key_inputs_do_not_create_or_overwrite_art(self):
        source=self.folder/'source.png'; Image.new('RGB',(8,8),'red').save(source)
        for output,inner,outer in [(source,30,100),(self.folder/'cut.jpg',30,100),
            (self.folder/'cut.png',100,30),(self.folder/'cut.png',float('nan'),100)]:
            with self.assertRaises(ValueError): chroma_key(source,output,inner,outer)
        with self.assertRaisesRegex(ValueError,'No removable'): chroma_key(source,self.folder/'cut.png')
        Image.new('RGB',(8,8),'#00FF00').save(source)
        with self.assertRaisesRegex(ValueError,'entire'): chroma_key(source,self.folder/'cut.png')
        self.assertFalse((self.folder/'cut.png').exists())

    def test_opaque_prop_is_allowed_but_alpha_cutouts_must_be_real_and_visible(self):
        file=self.folder/'opaque.jpg'; Image.new('RGB',(16,16),'red').save(file)
        asset={'kind':'prop','requires_alpha':False,'views':[{'frames':[{'file':str(file),'sha256':sha256(file),'width':16,'height':16}]}]}
        plan={'profile':'horror-v4.1','phase':'authored','sections':[],'horror':{'assets':[asset]}}
        check_horror_files(plan,self.folder)
        asset['requires_alpha']=True
        with self.assertRaises(ValueError): check_horror_files(plan,self.folder)
        file=self.folder/'empty.png'; Image.new('RGBA',(16,16),(0,0,0,0)).save(file)
        asset['views'][0]['frames'][0].update(file=str(file),sha256=sha256(file))
        with self.assertRaisesRegex(ValueError,'entirely transparent'): check_horror_files(plan,self.folder)


if __name__=='__main__': unittest.main()
