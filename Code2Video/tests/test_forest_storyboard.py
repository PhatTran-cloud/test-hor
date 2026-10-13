"""Creative draft trial of the real new contract, without fixture bypass or media."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from local_tools.production import read_plan
from horror_assets import write_asset_briefs
from illustration_direction import resolve_shot_direction
from v4_contract import normalize_v4


class ForestStoryboardTrialTests(unittest.TestCase):
    def setUp(self):
        self.plan = read_plan(ROOT / 'examples/forest-listens-storyboard-draft.json')

    def test_real_draft_exports_full_inventory_with_estimated_clock(self):
        self.assertFalse(self.plan.get('technical_fixture'))
        self.assertEqual(self.plan['phase'], 'draft')
        self.assertEqual(self.plan['trial']['clock_status'], 'PROVISIONAL_NOT_MEASURED')
        section = self.plan['sections'][0]
        cursor = 0
        for shot in section['shots']:
            window = shot['planning_window']
            self.assertEqual(window['start_seconds'], cursor)
            self.assertGreater(window['end_seconds'], cursor)
            cursor = window['end_seconds']
            self.assertNotIn('start_frame', shot)  # do not impersonate measured timing
        self.assertEqual(cursor, 24)
        with tempfile.TemporaryDirectory() as folder:
            exported = write_asset_briefs(self.plan, Path(folder) / 'prompts.json')
        self.assertEqual(len(exported['tasks']), 13)
        self.assertEqual(len(exported['three_d_tasks']), 1)
        self.assertEqual(len(exported['shot_inventory']), 5)
        for shot, row in zip(section['shots'], exported['shot_inventory']):
            self.assertEqual(set(shot['object_ids']), {c['object_id'] for c in row['components']})

    def test_macro_context_keeps_transitive_causes_without_replaying_them(self):
        section = self.plan['sections'][0]
        shot = next(s for s in section['shots'] if s['id'] == 'macro_identify')
        scoped = resolve_shot_direction(self.plan, section, shot)
        self.assertEqual({e['id'] for e in scoped['active_events']}, {'dew_release', 'insect_land'})
        self.assertEqual({e['id'] for e in scoped['dependency_events']},
            {'signal_question', 'trunk_pressure', 'dew_release', 'insect_land'})
        pressure = next(e for e in scoped['dependency_events'] if e['id'] == 'trunk_pressure')
        self.assertEqual(pressure['owner_section_id'], 'section_1')
        self.assertIn('local pressure', pressure['action'])
        self.assertIn('dew_drop', {o['id'] for o in scoped['objects']})

    def test_cyclic_unknown_and_duplicate_cause_references_are_rejected(self):
        mutations = [
            lambda events: events['signal_question'].update(cause_event_ids=['dew_release']),
            lambda events: events['dew_release'].update(cause_event_ids=['missing_event']),
            lambda events: events['dew_release'].update(cause_event_ids=['trunk_pressure', 'trunk_pressure']),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                plan = copy.deepcopy(self.plan)
                events = {e['id']: e for sh in plan['sections'][0]['shots'] for e in sh.get('events', [])}
                mutate(events)
                with self.assertRaises(ValueError):
                    normalize_v4(plan)


if __name__ == '__main__':
    unittest.main()
