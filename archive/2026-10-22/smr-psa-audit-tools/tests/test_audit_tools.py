"""Synthetic black-box tests for the archived SMR/PSA audit CLIs.

SPDX-License-Identifier: MIT
Copyright (c) 2026 Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TEST_DIR = Path(__file__).resolve().parent
REPO = TEST_DIR.parent
SCRIPTS = REPO / "scripts"
EXPORTER = SCRIPTS / "exported_phase_facts.py"
COMPARATOR = SCRIPTS / "compare_exported_streams.py"
UNITS = {"RES_TEMP": "K", "RES_PRES": "N/sqm", "RES_VFRAC": "",
         "RES_MOLEFLOW": "kmol/sec", "MOLEFLOW\\MIXED\\X": "kmol/sec"}


def worker(run_id="case-1", *, stream="S", overrides=None, extra_rows=None):
    values = {"RES_TEMP": 500.0, "RES_PRES": 2000000.0, "RES_VFRAC": 1.0,
              "RES_MOLEFLOW": 2.5, "MOLEFLOW\\MIXED\\X": 1.0}
    values.update(overrides or {})
    rows = []
    for field, value in values.items():
        rows.append({"path": f"\\Data\\Streams\\{stream}\\Output\\{field}",
                     "value": value, "unit": UNITS[field], "children": []})
    rows.extend(extra_rows or [])
    return {"run_id": run_id, "stream_results": {stream: rows}}


def write_json(path, obj):
    path.write_text(json.dumps(obj, allow_nan=False), encoding="utf-8")
    return path


class AuditCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not EXPORTER.is_file() or not COMPARATOR.is_file():
            raise unittest.SkipTest("CLI scripts are not present yet")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=TEST_DIR)
        self.addCleanup(self._cleanup_checked)
        self.tmp = Path(self._tmp.name).resolve()
        self.assertTrue(self.tmp.is_relative_to(TEST_DIR))

    def _cleanup_checked(self):
        self.assertTrue(Path(self._tmp.name).resolve().is_relative_to(TEST_DIR))
        self._tmp.cleanup()

    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(script), *map(str, args)],
                              cwd=str(REPO), capture_output=True, text=True, check=False)

    def export(self, data, name="worker.json", stream="S", component="X"):
        src = write_json(self.tmp / name, data)
        out = self.tmp / (Path(name).stem + "_facts.json")
        before = src.read_bytes()
        p = self.run_cli(EXPORTER, "--input", src, "--output", out,
                         "--streams", stream, "--component", component)
        self.assertEqual(src.read_bytes(), before, "exporter must leave source unchanged")
        return p, src, out

    def test_export_two_phase_and_single_phase_screening_and_source_receipt(self):
        data = worker(overrides={"RES_VFRAC": 0.4})
        data["stream_results"]["V"] = worker(stream="V", overrides={"RES_TEMP": 600.0})["stream_results"]["V"]
        src = write_json(self.tmp / "worker.json", data)
        out = self.tmp / "facts.json"
        before = src.read_bytes()
        p = self.run_cli(EXPORTER, "--input", src, "--output", out,
                         "--streams", "S", "V", "--component", "X")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(src.read_bytes(), before)
        result = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(result["schema"], "exported-phase-facts/1")
        self.assertEqual(result["source"]["run_id"], "case-1")
        self.assertEqual(result["source"]["sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(result["source"]["bytes"], len(before))
        two, one = result["facts"]["S"], result["facts"]["V"]
        required = {"temperature_K", "pressure_Pa", "molar_vapor_fraction",
                    "total_molar_flow_kmol_s", "component_molar_flow_kmol_s",
                    "overall_mole_fraction", "overall_z_times_pressure_Pa",
                    "vapor_partial_pressure_Pa"}
        self.assertTrue(required.issubset(two))
        self.assertIsNone(two["vapor_partial_pressure_Pa"])
        self.assertAlmostEqual(one["vapor_partial_pressure_Pa"], 800000.0)
        self.assertAlmostEqual(one["overall_mole_fraction"], 0.4)
        self.assertAlmostEqual(one["overall_z_times_pressure_Pa"], 800000.0)

    def test_export_rejects_missing_stream_leaf_null_container_and_wrong_unit(self):
        missing_stream = worker()
        missing_leaf = worker()
        missing_leaf["stream_results"]["S"] = missing_leaf["stream_results"]["S"][:-1]
        cases = [(missing_stream, "NO_SUCH_STREAM", "X")
                 ,(missing_leaf, "S", "X")]
        for defect in ("null", "container", "unit"):
            bad = worker()
            row = bad["stream_results"]["S"][-1]
            if defect == "null": row["value"] = None
            elif defect == "container": row["children"] = [{"path": "child"}]
            else: row["unit"] = "mol/s"
            cases.append((bad, "S", "X"))
        for i, (data, stream, component) in enumerate(cases):
            with self.subTest(i=i):
                p, _, out = self.export(data, f"bad{i}.json", stream, component)
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse(out.exists())

    def test_export_rejects_duplicate_and_nonfinite_json_including_overflow_exponent(self):
        bad_json = [("duplicate.json", '{"run_id":"a","run_id":"b"}'),
                    ("nan.json", '{"run_id":"a","unused":NaN}'),
                    ("infinite.json", '{"run_id":"a","unused":1e400}')]
        for name, raw in bad_json:
            src = self.tmp / name; src.write_text(raw, encoding="utf-8")
            out = self.tmp / (name + ".out.json")
            before = src.read_bytes()
            p = self.run_cli(EXPORTER, "--input", src, "--output", out,
                             "--streams", "S", "--component", "X")
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse(out.exists())
            self.assertEqual(src.read_bytes(), before)

    def compare(self, left_obj, right_obj, stem="compare"):
        left = write_json(self.tmp / f"{stem}_left.json", left_obj)
        right = write_json(self.tmp / f"{stem}_right.json", right_obj)
        out = self.tmp / f"{stem}_out.json"
        lbytes, rbytes = left.read_bytes(), right.read_bytes()
        p = self.run_cli(COMPARATOR, "--left", left, "--right", right, "--output", out)
        self.assertEqual(left.read_bytes(), lbytes, "comparator must leave left source unchanged")
        self.assertEqual(right.read_bytes(), rbytes, "comparator must leave right source unchanged")
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(out.read_text(encoding="utf-8")), left, right

    def test_compare_same_numeric_leaves_even_when_run_ids_differ(self):
        result, left, right = self.compare(worker("run-a"), worker("run-b"))
        self.assertTrue(result["same_exported_numeric_leaves"])
        self.assertFalse(result["run_ids_equal"])
        self.assertEqual(result["sources"]["left"]["run_id"], "run-a")
        self.assertEqual(result["sources"]["right"]["run_id"], "run-b")
        self.assertEqual(result["sources"]["left"]["sha256"], hashlib.sha256(left.read_bytes()).hexdigest())
        self.assertEqual(result["sources"]["right"]["bytes"], right.stat().st_size)
        self.assertFalse(result["diagnostics_evaluated"])

    def test_compare_added_removed_unit_and_value_changes(self):
        left = worker("same")
        right = worker("same", overrides={"RES_TEMP": 501.0})
        left["stream_results"]["S"].append({"path": "\\Data\\Streams\\S\\Output\\OLD",
                                             "value": 8, "unit": "kg/s", "children": []})
        right["stream_results"]["S"].append({"path": "\\Data\\Streams\\S\\Output\\NEW",
                                              "value": 9, "unit": "kg/s", "children": []})
        right["stream_results"]["S"][0]["unit"] = "degC"
        result, _, _ = self.compare(left, right, "changes")
        self.assertFalse(result["same_exported_numeric_leaves"])
        for key in ("added", "removed", "unit_changes", "value_changes"):
            self.assertTrue(result[key], key)
            self.assertIn("stream", result[key][0]); self.assertIn("path", result[key][0])
        self.assertEqual(result["unit_changes"][0]["left"], "K")
        self.assertEqual(result["unit_changes"][0]["right"], "degC")
        change = next(x for x in result["value_changes"] if x["path"].endswith("RES_TEMP"))
        self.assertEqual(change["left"], 500.0); self.assertEqual(change["right"], 501.0)
        self.assertEqual(change["delta_decimal"], "1.0")

    def test_compare_missing_stream_and_leaf_and_excludes_null_container_without_zero_coercion(self):
        left = worker("same")
        right = worker("same", stream="OTHER")
        result, _, _ = self.compare(left, right, "streams")
        self.assertIn("OTHER", result["added_streams"])
        self.assertIn("S", result["removed_streams"])
        left = worker("same")
        right = worker("same")
        right["stream_results"]["S"] = right["stream_results"]["S"][:-1]
        result, _, _ = self.compare(left, right, "leaf")
        self.assertEqual(len(result["removed"]), 1)
        self.assertTrue(any(x["path"].endswith("MOLEFLOW\\MIXED\\X") for x in result["removed"]))
        left = worker("same", extra_rows=[
            {"path": "container", "value": 0, "unit": "x", "children": [{"nested": 1}]},
            {"path": "null", "value": None, "unit": "x", "children": []}])
        right = worker("same")
        result, _, _ = self.compare(left, right, "excluded")
        self.assertTrue(result["same_exported_numeric_leaves"])
        self.assertEqual(result["numeric_leaf_counts"], {"left": 5, "right": 5})
        reasons = {x["path"]: x["reason"] for x in result["excluded_rows"]["left"]}
        self.assertEqual(reasons, {"container": "container", "null": "null"})

    def test_comparator_rejects_duplicate_and_nonfinite_json(self):
        valid = write_json(self.tmp / "valid.json", worker("x"))
        for name, raw in (("dupe.json", '{"run_id":"x","run_id":"x","stream_results":{}}'),
                          ("nan.json", '{"run_id":"x","unused":NaN,"stream_results":{}}'),
                          ("infinite.json", '{"run_id":"x","unused":1e400,"stream_results":{}}')):
            bad = self.tmp / name; bad.write_text(raw, encoding="utf-8")
            out = self.tmp / (name + ".out.json")
            before = bad.read_bytes()
            p = self.run_cli(COMPARATOR, "--left", valid, "--right", bad, "--output", out)
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse(out.exists())
            self.assertEqual(bad.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
