import copy
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('audit', Path(__file__).parents[1] / 'scripts/acm_parallel_contract_audit.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    return {'multiplier': 3, 'abs_tol': 0.001, 'rel_tol': 0,
            'variables': [
                {'name': 'synthetic_intensity', 'classification': 'intensive',
                 'single': 2, 'aggregate': 2, 'single_unit': 'arb',
                 'aggregate_unit': 'arb', 'representation': 'physical'},
                {'name': 'synthetic_raw_bound', 'classification': 'extensive',
                 'single': -4, 'aggregate': -12, 'single_unit': 'canonical-arb',
                 'aggregate_unit': 'canonical-arb', 'representation': 'raw_canonical',
                 'single_basis': 'synthetic-source-type', 'aggregate_basis': 'synthetic-source-type'}]}


class ContractTests(unittest.TestCase):
    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"x": 1, "x": 2}', object_pairs_hook=MODULE.unique_object)

    def test_identity_and_scope(self):
        data = fixture(); data['multiplier'] = 1
        data['variables'][1]['aggregate'] = data['variables'][1]['single']
        result = MODULE.audit(data)
        self.assertTrue(result['passed'])
        for key in ('aspen_executed', 'engineering_accepted', 'learning_eligible'):
            self.assertIs(result[key], False)

    def test_positive_and_no_mutation(self):
        data = fixture(); before = copy.deepcopy(data)
        self.assertTrue(MODULE.audit(data)['passed'])
        self.assertEqual(before, data)

    def test_scaling_failure(self):
        for index in (0, 1):
            data = fixture(); data['variables'][index]['aggregate'] += 1
            self.assertFalse(MODULE.audit(data)['passed'])

    def test_explicit_tolerance(self):
        data = fixture(); data['variables'][0]['aggregate'] += 0.0005
        self.assertTrue(MODULE.audit(data)['passed'])
        data['abs_tol'] = 0
        self.assertFalse(MODULE.audit(data)['passed'])

    def test_missing_fields(self):
        data = fixture()
        for key in list(data):
            bad = copy.deepcopy(data); del bad[key]
            with self.assertRaises((ValueError, KeyError)): MODULE.audit(bad)
        for index, row in enumerate(data['variables']):
            for key in row:
                bad = copy.deepcopy(data); del bad['variables'][index][key]
                with self.assertRaises((ValueError, KeyError)): MODULE.audit(bad)

    def test_invalid_contracts(self):
        for field, value in [('classification', 'unknown'), ('single', float('nan')),
                             ('aggregate', float('inf')), ('single', True),
                             ('aggregate_unit', 'ARB'), ('representation', 'display')]:
            data = fixture(); data['variables'][0][field] = value
            with self.assertRaises(ValueError): MODULE.audit(data)
        data = fixture(); data['variables'][1]['aggregate_basis'] = 'display-only'
        with self.assertRaises(ValueError): MODULE.audit(data)

    def test_invalid_scale_tolerances_and_empty(self):
        for key, value in [('multiplier', 0), ('multiplier', 1.5), ('multiplier', True),
                           ('abs_tol', -1), ('rel_tol', float('inf')), ('variables', [])]:
            data = fixture(); data[key] = value
            with self.assertRaises(ValueError): MODULE.audit(data)


if __name__ == '__main__': unittest.main()
