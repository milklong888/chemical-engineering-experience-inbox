"""Verify the delivered module payload; read-only, standard library only."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def verify(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / 'FILE_MANIFEST.json').read_text(encoding='utf-8'))
    expected = manifest['files']
    if len({row['path'] for row in expected}) != len(expected):
        raise ValueError('Duplicate manifest paths')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*')
              if p.is_file() and '__pycache__' not in p.relative_to(root).parts
              and p.name != 'FILE_MANIFEST.json'}
    names = {row['path'] for row in expected}
    problems = []
    if actual != names:
        problems.append({'file_set_mismatch': {'missing': sorted(names-actual), 'unexpected': sorted(actual-names)}})
    for row in expected:
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe manifest path')
        path = root / relative
        if path.is_symlink():
            problems.append({'symlink_not_allowed': row['path']})
            continue
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            problems.append({'digest_or_size_mismatch': row['path']})
    return {'status': 'fail' if problems else 'pass', 'checked_file_count': len(expected),
            'problems': problems, 'engineering_acceptance': 'not_assessed'}

if __name__ == '__main__':
    try:
        result = verify()
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['status'] == 'pass' else 1)
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'invalid_manifest', 'error': str(exc)}))
        raise SystemExit(2)
