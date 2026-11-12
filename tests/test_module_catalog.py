import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('module_catalog', Path(__file__).resolve().parents[1] / 'scripts/check_module_catalog.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ModuleCatalogTests(unittest.TestCase):
    def fixture(self, root):
        (root / 'modules').mkdir()
        (root / 'rules.md').write_text('Synthetic rule reference', encoding='utf-8')
        data = {'modules': [{'id': 'synthetic', 'kind': 'rules', 'entrypoints': [],
                            'rules': ['rules.md'], 'tests': [], 'dependencies': ['Markdown']} ]}
        return data

    def evaluate(self, root, data):
        (root / 'modules/catalog.json').write_text(json.dumps(data), encoding='utf-8')
        return MODULE.check(root)

    def test_rules_need_no_fake_mcp_or_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.evaluate(root, self.fixture(root))['status'], 'pass')

    def test_missing_unsafe_duplicate_and_empty_executable(self):
        for mode in ['missing', 'escape', 'duplicate', 'empty_code']:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                data = self.fixture(root)
                if mode == 'missing': data['modules'][0]['rules'] = ['absent.md']
                if mode == 'escape': data['modules'][0]['rules'] = ['../rules.md']
                if mode == 'duplicate': data['modules'].append(dict(data['modules'][0]))
                if mode == 'empty_code': data['modules'][0]['kind'] = 'mcp_cli'
                self.assertEqual(self.evaluate(root, data)['status'], 'fail')


if __name__ == '__main__':
    unittest.main()
