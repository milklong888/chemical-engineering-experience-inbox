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
        normalization = item.get('normalization')
        if normalization and normalization.get('action') == 'excluded_archive':
            if any(normalization.get(key) is not False for key in
                   ('default_runtime_installed', 'learning_eligible', 'success_case_eligible', 'default_retrieval_eligible')):
                errors.append({'module': ident, 'error': 'archive_eligibility_not_preserved'})
        rows.append({'id': ident, 'kind': item['kind'], 'checked': checked})
    if data.get('main_library'):
        proposal_file = root / 'modules/normalized_proposals.json'
        if not proposal_file.is_file() or proposal_file.is_symlink():
            errors.append({'error': 'missing_normalized_proposals'})
        else:
            seen_rules = set()
            for proposal in json.loads(proposal_file.read_text(encoding='utf-8'))['proposal_dispositions']:
                for key in proposal['qualified_rule_ids']:
                    if not key.startswith(proposal['source_id'] + '#') or key in seen_rules:
                        errors.append({'error': 'ambiguous_qualified_rule_id', 'key': key})
                    seen_rules.add(key)
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
