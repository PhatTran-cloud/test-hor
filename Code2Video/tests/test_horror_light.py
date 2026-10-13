"""Short storyboard authoring preserves illustration and motion evidence gates."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'src')]
from local_tools.production import read_plan
from horror_assets import write_asset_briefs
from horror_motion import write_motion_brief
from horror_contract import asset_digest
from illustration_direction import validate_direction, resolve_shot_direction
from v4_quality import review_targets
from kage_fixture import kage_plan


class HorrorLightTests(unittest.TestCase):
    def setUp(self):
        self.plan = read_plan(ROOT/'examples/horror-light-washer-draft.json')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def test_default_template_selects_light_without_inventing_cast(self):
        template = json.loads((ROOT/'examples/horror-profile-template.json').read_text())
        self.assertEqual(template['production_packet']['illustration_direction']['authoring_mode'],'horror_light')
        self.assertNotIn('bindings',template['visual_system'])
        self.assertIsNone(template['cast']['narrator'])
        self.assertIsNone(template['language_id'])

    def test_short_draft_needs_no_role_quota_metaphor_or_motion_ledger(self):
        self.assertFalse(self.plan['technical_fixture'])
        self.assertEqual(self.plan['phase'],'draft')
        for shot in self.plan['sections'][0]['shots']:
            self.assertNotIn('components',shot)
            self.assertNotIn('behaviors',shot)
            self.assertNotIn('attention_plan',shot)
        validate_direction(self.plan)

    def test_unknown_mode_is_rejected_instead_of_bypassing_validation(self):
        self.plan['production_packet']['illustration_direction']['authoring_mode']='light_typo'
        with self.assertRaisesRegex(ValueError,'Unknown'):validate_direction(self.plan)

    def test_actual_next_shot_and_main_action_are_still_required(self):
        for mutate in [lambda p:p['sections'][0]['shots'][0].pop('action'),
                       lambda p:p['sections'][0]['shots'][0]['handoff'].update(to_shot_id='wrong')]:
            bad=copy.deepcopy(self.plan);mutate(bad)
            with self.assertRaises(ValueError):validate_direction(bad)

    def test_asset_export_is_small_and_complete(self):
        result=write_asset_briefs(self.plan,self.folder/'illustration.json')
        self.assertEqual(len(result['tasks']),4)
        self.assertEqual(result['three_d_tasks'],[])
        self.assertEqual(len(result['shot_inventory']),3)
        self.assertNotIn('direction',result['shot_inventory'][0])
        self.assertNotIn('action_prompt',result['tasks'][0])
        self.assertIn('shared_context',result)
        self.assertIn('motion-brief',result['motion_vfx_handoff']['next_command'])
        background=next(t for t in result['tasks'] if t['asset_id']=='art_room_bg')
        self.assertNotIn('#00FF00',background['prompt'])
        self.assertIn('cool upper-left',background['prompt'])

    def test_short_prompts_keep_approved_identity_state_and_art_constraints(self):
        brief=self.plan['production_packet']['character_setting_brief']
        brief['approved_visual_age_bands']={'proposed_character':[22,25]}
        brief['reference_design_choices_to_review']=['approved cropped dark hair']
        brief['state_design_correction']={'loose_plug':'unplugged throughout this trial'}
        result=write_asset_briefs(self.plan,self.folder/'identity.json')
        for task in result['tasks']:
            prompt=task['prompt']
            self.assertIn('proposed_character',prompt)
            self.assertIn('[22, 25]',prompt)
            self.assertIn('approved cropped dark hair',prompt)
            self.assertIn('unplugged throughout this trial',prompt)
            self.assertIn('no visible human cast',prompt)
            self.assertIn('Same washer seam',prompt)
            self.assertIn('#16222D',prompt)

    def test_missing_illustration_and_route_mismatch_still_fail(self):
        for mutate in [lambda p:p['horror']['assets'].pop(),
                       lambda p:p['sections'][0]['objects'][1]['illustration'].update(route='3d')]:
            bad=copy.deepcopy(self.plan);mutate(bad)
            with self.assertRaises(ValueError):write_asset_briefs(bad,self.folder/'bad.json')
            self.assertFalse((self.folder/'bad.json').exists())

    def test_motion_export_reports_pending_assets_timing_and_event_carry(self):
        result=write_motion_brief(self.plan,self.folder/'motion.json')
        self.assertEqual(len(result['asset_registry']),4)
        self.assertEqual(len(result['tasks']),3)
        section_id=self.plan['sections'][0]['id']
        self.assertEqual(result['tasks'][0]['section_id'],section_id)
        self.assertEqual(result['section_objects'][section_id]['washer_hatch']['initial_state'],{'pressure':0})
        self.assertEqual(result['visual_system'],self.plan['visual_system'])
        self.assertEqual(result['status'],'REQUEST_ONLY_NOT_EXECUTED')
        self.assertIn('MEASURED_VOICE_TIMING_REQUIRED',result['blockers'])
        self.assertEqual(set(result['pending_asset_ids']),set(result['asset_registry']))
        self.assertEqual(result['tasks'][0]['vfx'],[])
        self.assertIsNone(result['tasks'][0]['motion'])
        self.assertEqual(result['tasks'][2]['active_events'][0]['id'],'hatch_knock')
        self.assertTrue((self.folder/'motion.md').is_file())

    def test_review_metadata_cannot_hide_missing_asset_registration(self):
        for asset in self.plan['horror']['assets']:
            asset['review']={'status':'PASS','asset_digest':asset_digest(asset)}
        result=write_motion_brief(self.plan,self.folder/'unregistered.json')
        self.assertEqual(len(result['pending_asset_ids']),4)

    def test_authored_motion_cannot_omit_object_ledger_or_camera_information(self):
        self.plan['phase']='authored'
        with self.assertRaisesRegex(ValueError,'Motion authoring'):validate_direction(self.plan)
        for shot in self.plan['sections'][0]['shots']:
            shot['behaviors']={oid:{'mode':'passive','motivation':'stable clue','trigger':{'kind':'intentional_hold','reason':'make the clue readable'},
                'response':'hold','secondary_response':'none','settle':'stable','exit_state':{'condition':'fixed'}} for oid in shot['object_ids']}
        with self.assertRaisesRegex(ValueError,'Authored camera'):validate_direction(self.plan)

    def test_review_keeps_attention_camera_relation_without_forcing_metaphor(self):
        targets=review_targets(self.plan,{'shots':[{'shot':'hatch_reply'}]})
        self.assertEqual(targets['visual'],['shot:hatch_reply'])
        self.assertIn('attention:hatch_reply',targets['motion'])
        self.assertIn('camera:hatch_reply',targets['motion'])
        self.assertIn('relation:hatch_reply',targets['editorial'])
        self.assertIn('event:hatch_knock',targets['vfx'])

    def test_native_3d_route_keeps_full_fabrication_contract(self):
        p=kage_plan();p['production_packet']['illustration_direction']['authoring_mode']='horror_light'
        for obj in p['sections'][0]['objects']:
            if obj['illustration']['method']=='generated':obj['illustration']['route']='3d' if obj['id']=='trunk_mg' else '2d'
        sh=p['sections'][0]['shots'][0];sh.update(action='inspect the source',sound_intent='quiet')
        sh['handoff']['to_shot_id']=None
        result=write_asset_briefs(p,self.folder/'native.json')
        self.assertEqual(result['three_d_tasks'][0]['provider'],'lowbudget3d')
        self.assertIn('3dviz-pro-max',result['three_d_tasks'][0]['required_skills'])
        p['horror']['assets'][1]['model_spec'].pop('anchors')
        with self.assertRaises(ValueError):write_asset_briefs(p,self.folder/'invalid-native.json')


if __name__=='__main__':unittest.main()
