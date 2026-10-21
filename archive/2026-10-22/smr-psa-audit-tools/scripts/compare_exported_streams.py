#!/usr/bin/env python3
"""Compare exported numeric stream leaves without evaluating native diagnostics.

Numeric equality never establishes a warning-free run. Null, container and
nonnumeric rows are excluded explicitly, rather than coerced to zero.

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
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile


class AuditError(ValueError):
    """Invalid or ambiguous exported evidence."""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuditError("duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise AuditError("non-finite JSON number: " + value)


def validate_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise AuditError("non-finite JSON number")
    if isinstance(value, dict):
        for child in value.values():
            validate_finite(child)
    elif isinstance(value, list):
        for child in value:
            validate_finite(child)


def load_worker(path):
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)
    validate_finite(data)
    if not isinstance(data, dict):
        raise AuditError("worker JSON must be an object")
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise AuditError("nonempty string run_id required")
    if not isinstance(data.get("stream_results"), dict):
        raise AuditError("stream_results must be an object")
    return data, {"path": str(path.resolve()), "run_id": run_id,
                  "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def numeric_leaves(data):
    leaves, excluded = {}, []
    for stream, rows in data["stream_results"].items():
        if not isinstance(rows, list):
            raise AuditError(stream + ": row list required")
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                raise AuditError(stream + ": each row requires string path")
            path = row["path"]
            if path in seen:
                raise AuditError(stream + ": duplicate exported path")
            seen.add(path)
            children = row.get("children")
            if not isinstance(children, list):
                raise AuditError(stream + ": explicit children list required")
            value = row.get("value")
            if children:
                reason = "container"
            elif value is None:
                reason = "null"
            elif isinstance(value, bool) or not isinstance(value, (int, float)):
                reason = "nonnumeric"
            else:
                if not isinstance(row.get("unit"), str):
                    raise AuditError(stream + ": numeric leaf requires string unit")
                leaves[(stream, path)] = {"value": value, "unit": row["unit"]}
                continue
            excluded.append({"stream": stream, "path": path, "reason": reason})
    return leaves, sorted(excluded, key=lambda r: (r["stream"], r["path"]))


def decimal_delta(left, right):
    """Return right-left as decimal text, avoiding overflow of finite floats."""
    a, b = Decimal(str(left)), Decimal(str(right))
    precision = max(a.adjusted(), b.adjusted()) - min(a.as_tuple().exponent,
                                                     b.as_tuple().exponent) + 3
    with localcontext() as ctx:
        ctx.prec = max(precision, 28)
        return str(b - a)


def compare(left, right):
    a, excluded_a = numeric_leaves(left)
    b, excluded_b = numeric_leaves(right)
    added, removed, units, values = [], [], [], []
    for stream, path in sorted(a.keys() | b.keys()):
        key = stream, path
        label = {"stream": stream, "path": path}
        if key not in a:
            added.append({**label, **b[key]})
        elif key not in b:
            removed.append({**label, **a[key]})
        else:
            if a[key]["unit"] != b[key]["unit"]:
                units.append({**label, "left": a[key]["unit"],
                              "right": b[key]["unit"]})
            if a[key]["value"] != b[key]["value"]:
                values.append({**label, "left": a[key]["value"],
                               "right": b[key]["value"],
                               "delta_decimal": decimal_delta(a[key]["value"],
                                                              b[key]["value"]),
                               "units_equal": a[key]["unit"] == b[key]["unit"]})
    streams_a, streams_b = set(left["stream_results"]), set(right["stream_results"])
    return {"added": added, "removed": removed, "unit_changes": units,
            "value_changes": values, "added_streams": sorted(streams_b - streams_a),
            "removed_streams": sorted(streams_a - streams_b),
            "excluded_rows": {"left": excluded_a, "right": excluded_b},
            "numeric_leaf_counts": {"left": len(a), "right": len(b)},
            "same_exported_numeric_leaves": not (added or removed or units or values),
            "same_exported_stream_set": streams_a == streams_b,
            "comparison": "Exact exported numeric values and unit strings; no unit conversion.",
            "delta_definition": "right-left decimal text; when units differ it is an arithmetic display, not a physical difference."}


def write_result(path, result, sources):
    if path.resolve() in {p.resolve() for p in sources}:
        raise AuditError("output must not overwrite an input")
    encoded = (json.dumps(result, ensure_ascii=False, allow_nan=False,
                          indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".audit-",
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(encoded)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--left", required=True, type=Path)
    parser.add_argument("--right", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        left, source_left = load_worker(args.left)
        right, source_right = load_worker(args.right)
        result = {"schema": "compare-exported-streams/1",
                  "sources": {"left": source_left, "right": source_right},
                  **compare(left, right),
                  "run_ids_equal": source_left["run_id"] == source_right["run_id"],
                  "diagnostics_evaluated": False,
                  "numeric_equality_does_not_imply_clean_run": True,
                  "scope": "Isolated exported-data audit reference; no native counter parsing, computation-engine calls or engineering acceptance."}
        write_result(args.output, result, [args.left, args.right])
    except (OSError, ValueError, ArithmeticError) as exc:
        print("audit error: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
