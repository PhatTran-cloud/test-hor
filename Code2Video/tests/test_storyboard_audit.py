"""Declared scene/shot continuity regressions; no pixels or artistic approval."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from storyboard_audit import audit_storyboard


def board():
    world = {'id': 'room', 'layout': 'door left; table right', 'perspective': 'eye-level',
             'lighting': 'window left', 'crop_safety': 'clean area above table', 'required_props': ['lamp'],
             'spatial_anchors': [{'id': 'door', 'description': 'left wall, fixed relative to table'}]}
    def shot(ident, framing, next_id):
        return {'id': ident, 'scene_id': 'room', 'object_ids': ['hero', 'lamp'], 'storyboard': {
            'function': 'Notice the lamp without revealing the cause', 'framing': framing,
            'attention': 'lamp', 'primary_action': 'hero watches, lamp intentionally still',
            'background_mode': 'lived_in', 'background_reason': 'door/table locate the interaction',
            'staging': {'fg': [], 'mg': ['hero', 'lamp'], 'bg': [],
                        'screen_direction': 'hero left of lamp', 'eyelines': 'hero looks right to lamp'},
            'start_state': {'hero': 'seated, looking right', 'lamp': 'on, at table'},
            'end_state': {'hero': 'seated, looking right', 'lamp': 'on, at table'},
            'information': {'audience_in': 'lamp is ordinary', 'audience_out': 'hero is listening',
                            'character_in': 'alone', 'character_out': 'uncertain',
                            'withheld': ['source of the sound'], 'reveal_ceiling': 'no visible threat'},
            'transition': {'relation': 'same_scene' if next_id else 'end', 'next_shot_id': next_id,
                           'trigger': 'attention changes', 'next_delta': 'closer attention' if next_id else 'hold aftermath',
                           'carry_channels': ['geography', 'prop_state'],
                           'preserved_objects': ['hero', 'lamp'] if next_id else []}}}
    return {'production_packet': {'illustration_direction': {'storyboard_contract': 'scene-shot/1', 'scene_worlds': [world]}},
            'sections': [{'objects': [{'id': 'hero'}, {'id': 'lamp'}],
                          'shots': [shot('wide', 'wide held frame', 'close'), shot('close', 'closer held frame', None)]}]}


class StoryboardAuditTests(unittest.TestCase):
    def test_same_world_reframing_and_intentional_hold_are_valid_structure_only(self):
        report = audit_storyboard(board(), required=True)
        self.assertEqual(report['status'], 'STRUCTURE_CHECKED')
        self.assertEqual((report['scenes'], report['shots']), (1, 2))
        self.assertEqual(report['artistic_review'], 'UNVERIFIED')
        self.assertEqual(report['pixel_continuity_review'], 'UNVERIFIED')

    def test_missing_staging_anchor_reveal_or_broken_next_pointer_is_rejected(self):
        for mutate in [lambda p: p['production_packet']['illustration_direction']['scene_worlds'][0].update(spatial_anchors=[]),
                       lambda p: p['sections'][0]['shots'][0]['storyboard']['staging'].update(bg=['lamp']),
                       lambda p: p['sections'][0]['shots'][0]['storyboard']['information'].pop('reveal_ceiling'),
                       lambda p: p['sections'][0]['shots'][0]['storyboard']['transition'].update(next_shot_id='missing')]:
            p = board(); mutate(p)
            with self.assertRaises(ValueError):
                audit_storyboard(p)

    def test_common_object_reset_cannot_hide_by_omitting_preserved_objects(self):
        p = board()
        p['sections'][0]['shots'][0]['storyboard']['transition']['preserved_objects'] = []
        p['sections'][0]['shots'][1]['storyboard']['start_state']['lamp'] = 'off, at table'
        with self.assertRaisesRegex(ValueError, 'resets.*cut'):
            audit_storyboard(p)
        p['sections'][0]['shots'][0]['storyboard']['transition']['state_changes'] = {'lamp': 'authored switch event at boundary'}
        self.assertEqual(audit_storyboard(p)['status'], 'STRUCTURE_CHECKED')

    def test_scene_change_must_be_declared_and_terminal_shot_cannot_carry(self):
        p = board()
        world = copy.deepcopy(p['production_packet']['illustration_direction']['scene_worlds'][0])
        world['id'] = 'courtyard'
        p['production_packet']['illustration_direction']['scene_worlds'].append(world)
        p['sections'][0]['shots'][1]['scene_id'] = 'courtyard'
        with self.assertRaisesRegex(ValueError, 'replace the scene world'):
            audit_storyboard(p)
        p['sections'][0]['shots'][0]['storyboard']['transition']['relation'] = 'scene_change'
        self.assertEqual(audit_storyboard(p)['scenes'], 2)
        p['sections'][0]['shots'][1]['storyboard']['transition']['preserved_objects'] = ['hero']
        with self.assertRaisesRegex(ValueError, 'Final shot'):
            audit_storyboard(p)

    def test_legacy_packet_is_not_misreported_as_checked(self):
        self.assertEqual(audit_storyboard({})['status'], 'NOT_DECLARED')
        with self.assertRaises(ValueError):
            audit_storyboard({}, required=True)

    def test_return_checks_object_that_was_offscreen_in_detail_shot(self):
        p = board(); shots = p['sections'][0]['shots']
        detail = shots[1]
        detail['object_ids'] = ['hero']
        detail['storyboard']['staging']['mg'] = ['hero']
        for key in ['start_state', 'end_state']:
            detail['storyboard'][key].pop('lamp')
        shots[0]['storyboard']['transition']['preserved_objects'] = ['hero']
        returned = copy.deepcopy(shots[0]); returned['id'] = 'return'
        returned['storyboard']['transition'].update(relation='end', next_shot_id=None, preserved_objects=[])
        returned['storyboard']['start_state']['lamp'] = 'off, at table'
        detail['storyboard']['transition'].update(relation='same_scene', next_shot_id='return', preserved_objects=['hero'])
        shots.append(returned)
        with self.assertRaisesRegex(ValueError, 'lamp resets on scene return'):
            audit_storyboard(p)
        detail['storyboard']['transition']['state_changes'] = {'lamp': 'authored offscreen switch event during detail'}
        self.assertEqual(audit_storyboard(p)['shots'], 3)

    def test_time_jump_invalidates_offscreen_state_without_waiving_explicit_carry(self):
        p = board(); first = p['sections'][0]['shots'][0]
        second = p['sections'][0]['shots'][1]
        first['storyboard']['transition'].update(relation='time_jump', preserved_objects=['hero'])
        second['storyboard']['start_state']['lamp'] = 'off, at table'
        self.assertEqual(audit_storyboard(p)['status'], 'STRUCTURE_CHECKED')
        first['storyboard']['transition']['preserved_objects'].append('lamp')
        with self.assertRaisesRegex(ValueError, 'resets across cut'):
            audit_storyboard(p)

    def test_production_entrypoint_audits_a_normalized_schema4_fixture(self):
        import numpy as np
        from scipy.io import wavfile
        spec = importlib.util.spec_from_file_location('fixture', ROOT / 'local_tools/v4_smoke/build_plan.py')
        fixture = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            audio = folder / 'clock.wav'
            wavfile.write(audio, 48000, np.zeros(540 * 800, dtype=np.float32))
            plan = fixture.make_plan(audio)
            world = board()['production_packet']['illustration_direction']['scene_worlds'][0]
            plan['production_packet']['illustration_direction'] = {'storyboard_contract': 'scene-shot/1', 'scene_worlds': [world]}
            shots = plan['sections'][0]['shots']
            for i, shot in enumerate(shots):
                shot['scene_id'] = 'room'
                card = copy.deepcopy(board()['sections'][0]['shots'][0]['storyboard'])
                card['staging'].update(mg=shot['object_ids'])
                card['start_state'] = card['end_state'] = {oid: 'synthetic static state' for oid in shot['object_ids']}
                nxt = shots[i + 1] if i + 1 < len(shots) else None
                card['transition'].update(relation='same_scene' if nxt else 'end',
                                          next_shot_id=nxt['id'] if nxt else None,
                                          preserved_objects=sorted(set(shot['object_ids']) & set(nxt['object_ids'])) if nxt else [])
                shot['storyboard'] = card
            path, report = folder / 'plan.json', folder / 'audit.json'
            path.write_text(json.dumps(plan), encoding='utf-8')
            run = subprocess.run([sys.executable, str(ROOT / 'local_tools/production.py'), 'storyboard-audit',
                                  str(path), '--output', str(report)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(report.read_text())['status'], 'STRUCTURE_CHECKED')
            self.assertEqual(json.loads(report.read_text())['artistic_review'], 'UNVERIFIED')


if __name__ == '__main__':
    unittest.main()
