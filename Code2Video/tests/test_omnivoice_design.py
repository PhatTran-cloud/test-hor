"""Design request boundaries; these tests do not judge generated voice quality."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from omnivoice_design import validate_request, design_arguments


class DesignTests(unittest.TestCase):
    def setUp(self):
        self.request = {'authorization': 'user requests two dialogue auditions', 'language_id': 'vi',
                        'voices': [{'id': 'grandmother', 'character_id': 'grandmother', 'role': 'dialogue',
                                    'text': 'Bà đây.', 'attributes': {'gender': 'female', 'age': 'elderly', 'pitch': 'low pitch'}}]}

    def test_age_pitch_are_real_design_controls_without_forced_duration(self):
        validate_request(self.request)
        args = design_arguments(self.request, self.request['voices'][0])
        self.assertEqual(args[1], 'Vietnamese')
        self.assertIsNone(args[6])
        self.assertEqual(args[9:12], ['Female / 女', 'Elderly / 老年', 'Low Pitch / 低音调'])
        self.assertEqual(args[-2:], ['Auto', 'Auto'])

    def test_narrator_emotion_unknown_controls_and_unsafe_id_are_rejected(self):
        for mutation in [lambda v: v.update(role='narrator'), lambda v: v['attributes'].update(style='scared'),
                         lambda v: v['attributes'].update(emotion='angry'), lambda v: v.update(id='../bad')]:
            request = copy.deepcopy(self.request); mutation(request['voices'][0])
            with self.assertRaises(ValueError):
                validate_request(request)

    def test_child_does_not_need_an_invented_gender(self):
        self.request['voices'][0]['attributes'] = {'age': 'child', 'pitch': 'high pitch'}
        validate_request(self.request)
        self.assertEqual(design_arguments(self.request, self.request['voices'][0])[9:12],
                         ['Auto', 'Child / 儿童', 'High Pitch / 高音调'])


if __name__ == '__main__':
    unittest.main()
