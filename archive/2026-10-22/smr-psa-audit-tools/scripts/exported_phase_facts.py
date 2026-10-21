#!/usr/bin/env python3
"""Read exported phase facts; perform no flash or engineering acceptance.

Supported rows use the worker JSON schema ``stream_results[stream]`` with
``path``, ``value``, ``unit`` and ``children``. Component flow is read from
the MIXED substream. Only VF == 1 permits ideal Dalton zP screening; no
fugacity or phase-specific composition is inferred.

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
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile


class AuditError(ValueError):
    """Invalid or insufficient exported evidence."""


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


def number(row, unit, label):
    if not isinstance(row, dict):
        raise AuditError(label + ": missing row")
    if not isinstance(row.get("children"), list) or row["children"]:
        raise AuditError(label + ": numeric leaf required")
    value = row.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AuditError(label + ": finite numeric value required")
    if isinstance(value, float) and not math.isfinite(value):
        raise AuditError(label + ": finite numeric value required")
    if row.get("unit") != unit:
        raise AuditError(label + ": expected unit " + repr(unit))
    return value


def phase_facts(data, streams, component):
    facts = {}
    for stream in streams:
        if stream not in data["stream_results"]:
            raise AuditError("missing stream: " + stream)
        rows = data["stream_results"][stream]
        if not isinstance(rows, list):
            raise AuditError(stream + ": row list required")
        index = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                raise AuditError(stream + ": each row requires string path")
            if row["path"] in index:
                raise AuditError(stream + ": duplicate exported path")
            index[row["path"]] = row
        prefix = "\\Data\\Streams\\" + stream + "\\Output\\"

        def get(key, unit):
            return number(index.get(prefix + key), unit, stream + "/" + key)

        temperature = get("RES_TEMP", "K")
        pressure = get("RES_PRES", "N/sqm")
        vf = get("RES_VFRAC", "")
        total = get("RES_MOLEFLOW", "kmol/sec")
        flow = get("MOLEFLOW\\MIXED\\" + component, "kmol/sec")
        if temperature <= 0 or pressure <= 0 or not 0 <= vf <= 1:
            raise AuditError(stream + ": invalid absolute state or vapor fraction")
        if total <= 0 or not 0 <= flow <= total:
            raise AuditError(stream + ": positive total and bounded component flow required")
        z = flow / total
        zp = z * pressure
        if not math.isfinite(z) or not math.isfinite(zp):
            raise AuditError(stream + ": derived fact is not finite")
        facts[stream] = {
            "temperature_K": temperature, "pressure_Pa": pressure,
            "molar_vapor_fraction": vf, "total_molar_flow_kmol_s": total,
            "component_molar_flow_kmol_s": flow, "overall_mole_fraction": z,
            "overall_z_times_pressure_Pa": zp,
            "vapor_partial_pressure_Pa": zp if vf == 1 else None,
            "interpretation": ("Ideal Dalton screening only; not fugacity."
                               if vf == 1 else
                               "Overall zP is not vapor partial pressure; phase x/y unknown."),
            "phase_specific_composition_inferred": False,
        }
    return facts


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
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--streams", required=True, nargs="+")
    parser.add_argument("--component", required=True)
    args = parser.parse_args(argv)
    try:
        if len(set(args.streams)) != len(args.streams):
            raise AuditError("duplicate selected stream")
        if not args.component or "\\" in args.component:
            raise AuditError("component must be a nonempty component identifier")
        data, source = load_worker(args.input)
        result = {"schema": "exported-phase-facts/1", "source": source,
                  "component": args.component, "substream": "MIXED",
                  "facts": phase_facts(data, args.streams, args.component),
                  "scope": "Isolated exported-data audit reference; no new physical calculation or engineering acceptance.",
                  "diagnostics_evaluated": False}
        write_result(args.output, result, [args.input])
    except (OSError, ValueError, ArithmeticError) as exc:
        print("audit error: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
