"""Check the actual encoded GIF, including timing and stable numeric content."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

from PIL import Image

spec = importlib.util.spec_from_file_location('animated_card', Path(__file__).parent / 'src/animated_card.py')
card = importlib.util.module_from_spec(spec)
spec.loader.exec_module(card)


class AnimatedCardTests(unittest.TestCase):
    def test_animation_preserves_statistics_and_loops(self):
        with tempfile.TemporaryDirectory() as directory:
            card.render_card(dict(username='GuyKawaii', total_lines_of_code=1234567,
                                  public_repos=42, total_stars=128, total_commits=2456),
                             {'additional_info': 'Stack: .NET | Vue.js'}, directory)
            with Image.open(Path(directory) / 'fetch.gif') as gif:
                self.assertTrue(gif.is_animated)
                self.assertEqual(gif.info['loop'], 0)
                frames, duration = [], 0
                for index in range(gif.n_frames):
                    gif.seek(index)
                    duration += gif.info['duration']
                    frames.append(gif.convert('RGB'))
                self.assertEqual(duration, 3500)
                self.assertNotEqual(frames[0].tobytes(), frames[1].tobytes())
                numeric_area = (575, 190, 1360, 390)
                for frame in frames[1:]:
                    self.assertEqual(frame.crop(numeric_area).tobytes(), frames[0].crop(numeric_area).tobytes())
            self.assertTrue((Path(directory) / 'fetch.png').is_file())
            self.assertLess((Path(directory) / 'fetch.gif').stat().st_size, 500000)


if __name__ == '__main__':
    unittest.main()
