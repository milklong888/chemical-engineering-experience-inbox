"""Read-only synthetic-data contract checker; never starts ACM or Aspen.

Input: {multiplier, abs_tol, rel_tol, variables:[{name, classification,
single, aggregate, single_unit, aggregate_unit, representation}]}.
classification: intensive or extensive. representation: physical or raw_canonical.
Raw canonical values additionally require identical nonempty single_basis and
aggregate_basis, supplied from source declarations, never inferred from display units.
Caller supplies tolerances; no model parameters or acceptance defaults are provided.
"""
import argparse
import json
import math


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(label + ' must be a finite number')
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(label + ' must be finite')
    return value


def audit(data):
    if not isinstance(data, dict):
        raise ValueError('input must be an object')
    n = number(data['multiplier'], 'multiplier')
    if n < 1 or n != int(n):
        raise ValueError('multiplier must be a positive integer')
    atol = number(data['abs_tol'], 'abs_tol')
    rtol = number(data['rel_tol'], 'rel_tol')
    if atol < 0 or rtol < 0:
        raise ValueError('tolerances must be nonnegative')
    variables = data['variables']
    if not isinstance(variables, list) or not variables:
        raise ValueError('variables must be a nonempty list')
    results, names = [], set()
    for row in variables:
        name = row['name']
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError('variable names must be nonempty and unique')
        names.add(name)
        classification = row['classification']
        if classification not in ('intensive', 'extensive'):
            raise ValueError('explicit intensive/extensive classification required')
        a = number(row['single'], name + '.single')
        b = number(row['aggregate'], name + '.aggregate')
        unit = row['single_unit']
        if not isinstance(unit, str) or not unit.strip() or unit != row['aggregate_unit']:
            raise ValueError(name + ': units must match exactly; no conversion performed')
        representation = row['representation']
        if representation not in ('physical', 'raw_canonical'):
            raise ValueError(name + ': explicit representation required')
        if representation == 'raw_canonical':
            basis = row['single_basis']
            if not isinstance(basis, str) or not basis.strip() or basis != row['aggregate_basis']:
                raise ValueError(name + ': identical explicit canonical basis required')
        expected = number(a * n if classification == 'extensive' else a, name + '.expected')
        limit = number(atol + rtol * abs(expected), name + '.tolerance')
        difference = number(b - expected, name + '.difference')
        results.append({'name': name, 'expected': expected, 'actual': b,
                        'difference': difference, 'limit': limit,
                        'passed': abs(difference) <= limit})
    return {'schema': 'acm-parallel-contract-audit/v1',
            'passed': all(x['passed'] for x in results), 'checks': results,
            'proof_scope': 'caller_supplied_json_arithmetic_only',
            'aspen_executed': False, 'engineering_accepted': False,
            'strict_passed': False, 'success_case_eligible': False,
            'default_rule_eligible': False, 'default_retrieval_eligible': False,
            'learning_eligible': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_json')
    args = parser.parse_args()
    try:
        with open(args.input_json, encoding='utf-8-sig') as handle:
            data = json.load(handle, object_pairs_hook=unique_object)
        result = audit(data)
    except (ValueError, KeyError, TypeError, OverflowError, OSError) as error:
        print(json.dumps({'passed': False, 'input_error': str(error)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
