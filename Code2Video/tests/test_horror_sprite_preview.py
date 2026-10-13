import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from horror_sprite_preview import read_sprite_spec


class SpritePreviewTests(unittest.TestCase):
    def make_spec(self, folder):
        frame = folder / 'frame.png'
        image = Image.new('RGBA', (8, 8))
        image.putpixel((4, 4), (100, 100, 100, 255))
        image.save(frame)
        digest = hashlib.sha256(frame.read_bytes()).hexdigest()
        spec = {'schema_version': 4, 'profile': 'horror-v4.1',
                'scope': 'isolated_sprite_test', 'duration_frames': 60,
                'frames': [{'file': 'frame.png', 'sha256': digest,
                            'rendered_file': 'frame.png', 'registered_sha256': digest}],
                'render_spec': {'project_dir': '.'}}
        path = folder / 'spec.json'
        path.write_text(json.dumps(spec), encoding='utf-8')
        return path, spec

    def test_registered_alpha_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            path, _ = self.make_spec(Path(temp))
            self.assertEqual(read_sprite_spec(path)['duration_frames'], 60)

    def test_film_scope_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path, spec = self.make_spec(Path(temp))
            spec['scope'] = 'film'
            path.write_text(json.dumps(spec), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'cannot render a film'):
                read_sprite_spec(path)

    def test_changed_rendered_copy_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path, spec = self.make_spec(Path(temp))
            spec['frames'][0]['registered_sha256'] = '0' * 64
            path.write_text(json.dumps(spec), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'differs from registered'):
                read_sprite_spec(path)

    def test_rgb_image_cannot_be_passed_as_alpha(self):
        with tempfile.TemporaryDirectory() as temp:
            path, spec = self.make_spec(Path(temp))
            frame = Path(temp) / 'frame.png'
            Image.new('RGB', (8, 8), 'red').save(frame)
            spec['frames'][0]['sha256'] = hashlib.sha256(frame.read_bytes()).hexdigest()
            path.write_text(json.dumps(spec), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'transparent and visible'):
                read_sprite_spec(path)


if __name__ == '__main__':
    unittest.main()
