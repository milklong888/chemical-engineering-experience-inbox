"""Check declared module file coverage. Does not import or execute modules."""
import argparse
import json
from pathlib import Path, PurePosixPath


def check(root):
    root = Path(root).resolve()
    data = json.loads((root / 'modules/catalog.json').read_text(encoding='utf-8'))
    errors, ids, rows = [], set(), []
    for item in data['modules']:
        ident = item['id']
        if ident in ids:
            errors.append({'module': ident, 'error': 'duplicate_id'})
        ids.add(ident)
        checked = []
        for field in ['entrypoints', 'rules', 'tests']:
            for name in item[field]:
                rel = PurePosixPath(name)
                target = root.joinpath(*rel.parts)
                safe = bool(name) and not rel.is_absolute() and '..' not in rel.parts and '\\' not in name and ':' not in name
                safe = safe and target.resolve().is_relative_to(root)
                if not safe or target.is_symlink() or not target.exists():
                    errors.append({'module': ident, 'field': field, 'path': name, 'error': 'unsafe_or_missing'})
                elif field == 'tests' and not any(target.rglob('test_*.py')):
                    errors.append({'module': ident, 'path': name, 'error': 'empty_tests'})
                elif field != 'tests' and not target.is_file():
                    errors.append({'module': ident, 'path': name, 'error': 'not_file'})
                checked.append(name)
        if not item['rules'] or not item['dependencies']:
            errors.append({'module': ident, 'error': 'missing_rules_or_dependency_declaration'})
        if item['kind'] != 'rules' and (not item['entrypoints'] or not item['tests']):
            errors.append({'module': ident, 'error': 'missing_code_or_tests'})
        rows.append({'id': ident, 'kind': item['kind'], 'checked': checked})
    return {'status': 'fail' if errors else 'pass', 'module_count': len(rows),
            'modules': rows, 'errors': errors,
            'scope': 'declared file coverage only; imports, transport and native capability require separate tests',
            'engineering_acceptance': 'not_assessed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = check(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'status': 'invalid', 'error': str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'pass' else 1)
