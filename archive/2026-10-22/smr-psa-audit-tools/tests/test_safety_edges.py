"""Black-box source-preservation and finite-difference checks.

SPDX-License-Identifier: MIT
Copyright (c) 2026 Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:
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
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TEST_DIR = Path(__file__).resolve().parent
SCRIPTS = TEST_DIR.parent / "scripts"


class SafetyEdges(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=TEST_DIR)
        self.root = Path(self.directory.name).resolve()
        self.assertTrue(self.root.is_relative_to(TEST_DIR))
        self.addCleanup(self.cleanup)

    def cleanup(self):
        self.assertTrue(self.root.is_relative_to(TEST_DIR))
        self.directory.cleanup()

    def write(self, name, data):
        path = self.root / name
        path.write_text(json.dumps(data, allow_nan=False), encoding="utf-8")
        return path

    def call(self, name, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / name),
                               *map(str, args)], capture_output=True, text=True)

    def worker(self, value=1):
        fields = {"RES_TEMP": (300, "K"), "RES_PRES": (100000, "N/sqm"),
                  "RES_VFRAC": (1, ""), "RES_MOLEFLOW": (2, "kmol/sec"),
                  "MOLEFLOW\\MIXED\\X": (value, "kmol/sec")}
        return {"run_id": "synthetic", "stream_results": {"a": [
            {"path": "\\Data\\Streams\\a\\Output\\" + key,
             "value": val, "unit": unit, "children": []}
            for key, (val, unit) in fields.items()]}}

    def test_output_alias_cannot_overwrite_either_source(self):
        source = self.write("input.json", self.worker())
        original = source.read_bytes()
        result = self.call("exported_phase_facts.py", "--input", source,
                           "--output", source, "--streams", "a", "--component", "X")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(source.read_bytes(), original)
        other = self.write("other.json", self.worker())
        result = self.call("compare_exported_streams.py", "--left", source,
                           "--right", other, "--output", other)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(other.read_bytes(), original)

    def test_finite_exported_values_can_have_large_decimal_difference(self):
        left, right = self.worker(), self.worker()
        left["stream_results"]["a"][0]["value"] = -1e308
        right["stream_results"]["a"][0]["value"] = 1e308
        a, b = self.write("a.json", left), self.write("b.json", right)
        output = self.root / "comparison.json"
        result = self.call("compare_exported_streams.py", "--left", a,
                           "--right", b, "--output", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["value_changes"][0]["delta_decimal"], "2E+308")
        self.assertFalse(data["diagnostics_evaluated"])

    def test_duplicate_paths_are_ambiguous_and_rejected(self):
        data = self.worker()
        data["stream_results"]["a"].append(dict(data["stream_results"]["a"][0]))
        bad = self.write("duplicate-path.json", data)
        good = self.write("good.json", self.worker())
        for script, args in [
            ("exported_phase_facts.py", ["--input", bad, "--streams", "a", "--component", "X"]),
            ("compare_exported_streams.py", ["--left", bad, "--right", good]),
        ]:
            with self.subTest(script=script):
                output = self.root / (script + ".json")
                result = self.call(script, *args, "--output", output)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
