import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import MagicMock, patch
import zipfile

# Load independently of the image renderer's optional local dependencies.
spec = importlib.util.spec_from_file_location('code_stats', Path(__file__).parent / 'src/code_stats.py')
stats = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = stats
spec.loader.exec_module(stats)


class CodeStatsTests(unittest.TestCase):
    def test_owned_public_private_and_combined_totals(self):
        repos = [NS(owner=NS(login='Owner'), private=False),
                 NS(owner=NS(login='Owner'), private=True),
                 NS(owner=NS(login='Other'), private=False)]
        user = NS(login='Owner', get_repos=lambda **kwargs: iter(repos))
        with patch.object(stats.shutil, 'which', return_value='cloc'), patch.object(stats, 'count_repository', side_effect=[12, 8]):
            self.assertEqual(stats.get_code_totals(NS(get_user=lambda: user)),
                             dict(public_lines_of_code=12, private_lines_of_code=8, total_lines_of_code=20))

    def test_failure_does_not_publish_partial_totals_or_private_names(self):
        user = NS(login='Owner', get_repos=lambda **kwargs: [NS(owner=NS(login='Owner'))])
        with patch.object(stats.shutil, 'which', return_value='cloc'), patch.object(stats, 'count_repository', side_effect=Exception('private-secret')):
            with self.assertRaises(RuntimeError) as error:
                stats.get_code_totals(NS(get_user=lambda: user))
            self.assertNotIn('private-secret', str(error.exception))
            self.assertTrue(error.exception.__suppress_context__)

    def test_archive_counting_cleanup_and_path_validation(self):
        repo = NS(size=1, default_branch='main', get_archive_link=lambda *args: 'https://example.test/snapshot')
        for filename in ['snapshot/main.py', '../escape.py']:
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr(filename, '# comment\nprint(1)\n')
            response = NS(raise_for_status=lambda: None, iter_content=lambda **kwargs: [archive.getvalue()])
            context = MagicMock()
            context.__enter__.return_value = response
            paths = []
            def cloc(args, **kwargs):
                source = Path(args[-1])
                paths.append(source)
                self.assertEqual((source / filename).read_text(), '# comment\nprint(1)\n')
                return NS(stdout=json.dumps({'SUM': {'code': 1}}))
            with patch.object(stats.requests, 'get', return_value=context), patch.object(stats.subprocess, 'run', side_effect=cloc):
                if filename.startswith('..'):
                    with self.assertRaises(ValueError):
                        stats.count_repository(repo)
                else:
                    self.assertEqual(stats.count_repository(repo), 1)
                    self.assertFalse(paths[0].exists())


if __name__ == '__main__':
    unittest.main()
