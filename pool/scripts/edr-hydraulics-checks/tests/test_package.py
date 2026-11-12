"""Package acceptance tests, synthetic/read-only; no engineering certificate."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_manifest import verify

class PackageTests(unittest.TestCase):
    def test_payload_manifest(self):
        self.assertEqual(verify()['status'], 'pass')

    def test_manifest_rejects_added_missing_and_changed_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'module'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__'))
            target = copy / 'examples' / 'pipe.json'
            original = target.read_bytes()
            target.write_bytes(original + b' ')
            self.assertEqual(verify(copy)['status'], 'fail')
            target.write_bytes(original)
            extra = copy / 'unexpected.txt'
            extra.write_text('synthetic', encoding='utf-8')
            self.assertEqual(verify(copy)['status'], 'fail')
            extra.unlink()
            target.unlink()
            self.assertEqual(verify(copy)['status'], 'fail')

    def test_all_four_documented_cli_examples_are_readonly_diagnostics(self):
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'examples').glob('*.json')}
        for tool, file in [('screen_pipe_candidates','pipe'), ('check_exchanger_basis','exchanger'),
                           ('check_packed_beds','packed'), ('audit_edr_geometry','geometry')]:
            with self.subTest(tool=tool):
                process = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(ROOT/'scripts/engineering_checks.py'),
                                          tool, '--input', str(ROOT/'examples'/f'{file}.json')],
                                         text=True, encoding='utf-8', capture_output=True, timeout=10)
                self.assertEqual(process.returncode, 0, process.stderr)
                result = json.loads(process.stdout)
                self.assertEqual(result['diagnostic_status'], 'pass')
                self.assertEqual(result['engineering_acceptance'], 'not_assessed')
                self.assertEqual(result['native_calculation_acceptance'], 'not_assessed')
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before})

    def test_source_digests_bind_the_delivered_single_core_and_entry(self):
        metadata = json.loads((ROOT/'SOURCE_METADATA.json').read_text(encoding='utf-8'))
        self.assertIsNone(metadata['source_commit'])
        for source in metadata['source_files']:
            if source.get('delivered_path'):
                raw = (ROOT/source['delivered_path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), source['delivered_sha256'])
                self.assertNotIn(b'\r', raw)

if __name__ == '__main__':
    unittest.main(verbosity=2)
