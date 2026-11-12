# EDR / hydraulics read-only checks

Portable snapshot of the existing `aspen-edr-rating-delivery` four-tool module.
The original professional owner remains canonical; this package does not fork
its engineering algorithms. The copied core, FastMCP facade and original tests
preserve their recorded owner snapshots with LF newline normalization only.
Raw owner and delivered hashes and the
limits of source publication verification are in [SOURCE_METADATA.json](SOURCE_METADATA.json).

| Tool | Implemented diagnostic | Outside its scope |
| --- | --- | --- |
| `screen_pipe_candidates` | Caller catalog ID and Q/A velocity screening | Catalog generation, automatic roundup or final pipe selection |
| `check_exchanger_basis` | Supplied absolute-pressure/DP closure, matching area basis and endpoint principal-phase Re | Native heat transfer, pressure prediction, phase calculation |
| `check_packed_beds` | Explicit stage coverage, per-stage FC, per-bed HETP/height and caller diameter branches | Native capacity correlation, physical bed continuity, operating-plot position |
| `audit_edr_geometry` | Supported endpoint tube rows, unique normal tubes, region bounds, tube/rod/spacer circular overlaps | All plates/strips/shells/axial collisions, vibration or mechanical approval |

Every tool returns `engineering_acceptance: not_assessed` and
`native_calculation_acceptance: not_assessed`. A diagnostic pass applies only to
implemented checks on supplied data and metadata, and cannot authenticate its
sources. A missing or unsupported check stays `unverified`.

## Run without installation

From this module directory, with Python 3.10 or newer:

```text
python -B -X utf8 scripts/engineering_checks.py screen_pipe_candidates --input examples/pipe.json
python -B -X utf8 scripts/engineering_checks.py check_exchanger_basis --input examples/exchanger.json
python -B -X utf8 scripts/engineering_checks.py check_packed_beds --input examples/packed.json
python -B -X utf8 scripts/engineering_checks.py audit_edr_geometry --input examples/geometry.json
python -B -X utf8 -m unittest discover -s tests -v
```

Core/CLI/tests need only the standard library. `--input -` reads UTF-8 JSON stdin.
Exit 0 means a JSON diagnostic was produced, including fail/unverified; exit 2
means input/file error. Inspect `diagnostic_status`, not just the process exit.
All example values are synthetic interface fixtures, never project values,
standard dimensions, engineering evidence or recommended thresholds.

## Optional real MCP entry

Install [requirements-mcp.txt](requirements-mcp.txt) in a caller-owned isolated
environment only if MCP is needed, then launch:

```text
python -B -X utf8 scripts/checks_mcp.py
```

This is a real `mcp.server.fastmcp.FastMCP` stdio server. It registers the four
functions directly from the same `engineering_checks.TOOLS`, with no copied
calculation layer. Tool arguments are `{"request": {...}}`. No app/MCP settings
are edited by this package. See [mcp-config.example.toml](mcp-config.example.toml)
for a non-installed configuration template. Without the optional SDK, use CLI;
the original real-stdio test explicitly skips in that interpreter.

## Rules, dependencies and verification

- [API contract](docs/API.md): all required fields, explicit units, metadata and checks.
- [Engineering method boundaries](docs/RULES.md): N/C/S/J/U, rounding feedback,
  warning physical diagnosis, real geometry, area basis and stage/plot distinction.
- [Dependency declaration](DEPENDENCIES.json) and [verification record](VERIFICATION.json).
- [Payload manifest](FILE_MANIFEST.json): exact file set and SHA256, excluding
  that manifest itself and Python cache directories. [Verify it](scripts/verify_manifest.py)
  with `python -B scripts/verify_manifest.py`.

Code is MIT; package documentation is CC BY 4.0 with attribution to
milklong888 and the recorded professional owners. See [LICENSE](LICENSE) and
[NOTICE.md](NOTICE.md). No standard PDF, commercial Help, models, real logs or
private runtime configuration is included. This is an offline tool package and
method reference, not an admitted inbox experience, engineering success,
canonical promotion or default retrieval authorization. Operating-plot position,
full native rating and exact-file delivery remain explicitly unverified here.
