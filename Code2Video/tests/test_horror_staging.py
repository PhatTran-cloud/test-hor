"""Scene reuse and story links; fixtures do not establish reference findings/art."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'src')]
from local_tools.production import read_plan
from horror_assets import write_asset_briefs
from horror_motion import write_motion_brief
from horror_staging import validate_staging, resolve_staging, plate_fingerprint, plate_current
from illustration_direction import resolve_shot_direction
from v4_quality import review_targets


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.plan = read_plan(ROOT/'examples/horror-ensemble-draft.json')
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def test_one_plate_three_views_keeps_inventory_and_people(self):
        validate_staging(self.plan)
        result = write_asset_briefs(self.plan, self.folder/'art.json')
        self.assertEqual(len(result['tasks']), 12)
        plates = [t for t in result['tasks'] if t['asset_id']=='art_room_bg']
        self.assertEqual(len(plates), 1)
        self.assertEqual(len(plates[0]['scene_usage'][0]['views']), 3)
        self.assertIn('empty_socket', plates[0]['prompt'])
        self.assertIn('supply_return', plates[0]['prompt'])
        self.assertIn('no inserted plug', plates[0]['prompt'].lower())
        self.assertEqual([r['cast']['total_visible_people'] for r in result['shot_inventory']], [9,4,1])
        self.assertEqual([r['staging']['view']['kind'] for r in result['shot_inventory']], ['master','crop','crop'])

    def test_offscreen_inventory_is_not_deleted_and_link_survives_handoff(self):
        sec = self.plan['sections'][0]; shot = sec['shots'][1]
        stage = resolve_staging(self.plan,shot)
        self.assertEqual(stage['outside_this_shot_object_ids'], ['attendant'])
        self.assertEqual(stage['story_link']['link_kind'], 'evidence_return')
        self.assertEqual(stage['story_link']['returns_to_shot_id'], 'establish_supply')
        self.assertEqual(resolve_shot_direction(self.plan,sec,shot)['scene_staging'],stage)
        motion = write_motion_brief(self.plan,self.folder/'motion.json')
        self.assertEqual(motion['tasks'][1]['staging'],stage)
        self.assertIn('observer_b',motion['tasks'][2]['staging']['outside_this_shot_object_ids'])
        self.assertIn('empty_socket',(self.folder/'motion.md').read_text())
        self.assertEqual(motion['character_setting_brief'],self.plan['production_packet']['character_setting_brief'])
        self.assertIn('SETTING_DESIGN_DECISION_UNRESOLVED',motion['blockers'])
        self.assertTrue(motion['setting_blockers'])
        self.assertNotIn('washer_hatch',{i['object_id'] for i in motion['tasks'][2]['instances']})
        final=self.plan['sections'][0]['shots'][2]
        scoped=resolve_shot_direction(self.plan,sec,final)
        self.assertIn('washer_body',{o['id'] for o in scoped['objects']})
        self.assertEqual(scoped['active_events'][0]['id'],'hatch_knock')

    def test_background_hash_tracks_layout_light_static_evidence_and_style(self):
        asset = self.plan['horror']['assets'][0]
        original = plate_fingerprint(self.plan,asset)
        self.assertFalse(plate_current(self.plan,asset))
        asset['scene_staging_sha256'] = original
        self.assertTrue(plate_current(self.plan,asset))
        for mutate in [lambda p:p['production_packet']['illustration_direction']['scene_worlds'][0].update(lighting='changed light'),
            lambda p:p['production_packet']['illustration_direction']['scene_worlds'][0]['staging']['static_details'][0].update(description='changed socket'),
            lambda p:p['horror']['style_bible'].update(materials='changed materials')]:
            bad = copy.deepcopy(self.plan); mutate(bad)
            self.assertFalse(plate_current(bad,bad['horror']['assets'][0]))

    def test_unknown_view_cannot_use_a_prop_plate_or_silently_change_angle(self):
        mutations = [lambda p:p['sections'][0]['shots'][1]['camera'].update(stage_view_id='missing'),
            lambda p:p['production_packet']['illustration_direction']['scene_worlds'][0]['staging'].update(master_plate_object_id='loose_plug'),
            lambda p:p['production_packet']['illustration_direction']['scene_worlds'][0]['staging']['static_details'][0].update(readable_in_view_ids=['missing']),
            lambda p:p['sections'][0]['shots'][0]['object_ids'].remove('room_bg')]
        for mutate in mutations:
            p=copy.deepcopy(self.plan);mutate(p)
            with self.assertRaises(ValueError):validate_staging(p)

    def test_generic_unknown_end_and_fake_return_links_are_rejected(self):
        for mutation in [{'link_kind':'next'}, {'link_kind':'end'},
            {'link_kind':'location_change'}, {'link_kind':'evidence_return','returns_to_shot_id':'supply_still_off'}]:
            p=copy.deepcopy(self.plan);p['sections'][0]['shots'][1]['handoff'].update(mutation)
            with self.assertRaises(ValueError):validate_staging(p)
        p=copy.deepcopy(self.plan);p['production_packet']['illustration_direction']['staging_revision']=True
        with self.assertRaises(ValueError):validate_staging(p)

    def test_actual_review_targets_keep_readable_background_and_story_link(self):
        targets=review_targets(self.plan,{'shots':[{'shot':'supply_still_off'}]})
        self.assertIn('background_detail:utility_room:empty_socket',targets['visual'])
        self.assertIn('staging:supply_still_off',targets['layout'])
        self.assertIn('story_link:supply_still_off',targets['editorial'])
        other=review_targets(self.plan,{'shots':[{'shot':'hatch_reply'}]})
        self.assertNotIn('background_detail:utility_room:empty_socket',other['visual'])

    def test_frozen_unstaged_plan_keeps_legacy_mode(self):
        self.plan['production_packet']['illustration_direction'].pop('staging_revision')
        for w in self.plan['production_packet']['illustration_direction']['scene_worlds']:w.pop('staging')
        for shot in self.plan['sections'][0]['shots']:shot['camera'].pop('stage_view_id')
        validate_staging(self.plan)
        self.assertIsNone(resolve_staging(self.plan,self.plan['sections'][0]['shots'][0]))
        result=write_asset_briefs(self.plan,self.folder/'legacy.json')
        self.assertEqual(len(result['tasks']),12)


if __name__=='__main__':unittest.main()
