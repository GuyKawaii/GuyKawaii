"""Exercise canvas conversion without network requests or private data."""
import importlib.util
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image

spec = importlib.util.spec_from_file_location('canvas_portrait', Path(__file__).parent / 'src/canvas_portrait.py')
portrait = importlib.util.module_from_spec(spec)
spec.loader.exec_module(portrait)


class CanvasPortraitTests(unittest.TestCase):
    def test_color_conversion_and_deterministic_motion(self):
        buffer = BytesIO()
        Image.new('RGB', (80, 40), (120, 180, 240)).save(buffer, format='PNG')
        response = SimpleNamespace(content=buffer.getvalue(), raise_for_status=lambda: None)
        with patch.object(portrait.requests, 'get', return_value=response):
            frames = portrait.portrait_frames('https://example.test/avatar')
        self.assertEqual(len(frames), 16)
        self.assertEqual(frames[0].size, (480, 480))
        self.assertNotEqual(frames[0].tobytes(), frames[4].tobytes())
        self.assertEqual(frames[0].tobytes(), frames[8].tobytes())
        # A flat source still gets a multicolor character gradient, not one tint.
        self.assertGreater(len(frames[0].getcolors(480 * 480)), 200)


if __name__ == '__main__':
    unittest.main()
