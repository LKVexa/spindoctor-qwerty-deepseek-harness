# Changelog

## 1.1.0 - 2026-10-10

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics (.qasm2/.circuit, skipped-file listing, compact status, 128 files /
  4 MiB / 128 commands / 4096 characters), CSV report copies and measurement-CSV fitting equations. All 241 presets replayed.
- Tools `spindoctor_functions` (in-chat function table) and `spindoctor_test_theory` (theory testing from a file, pasted text or
  the chat history, with TXT+JSON+PDF theory reports) now take their definitions from the engine's own tool list, so the tool
  descriptions state the 298-qubit limits instead of the old 29-qubit cap.
- Re-checked against the current harness docs (publish.md, tool.md, the tool authoring reference) and the real dsh 0.2.0-rc.2:
  the bundle format (`dsh.bundle.patch` + `cordis.patch.yml` insert row by package name) is unchanged.
- Tool parameters now follow the dsh-tools schema DSL exactly: typed array `items` and explicit object openness (the old
  `excerpts`, `checks`, `assumptions` and `variables` arrays had no item type), preset overrides accepted as an object,
  `limit` as an integer, enums for `section`, `action` and `source`, and the `isolate` option for theory runs.
- `exec.signal` is honoured: cancelling a tool call stops the Python engine. A missing Python now raises a tool error, Python
  candidates are tried in order (`python3`/`python`, or `python`/`py` on Windows), output is capped, and UTF-8 is forced.
- The repo root is now the bundle (installable from a checkout or `github:`); dropped the unused `@deepseek-ai/cordis` peer;
  `engines.node >= 22` (dsh 0.2.0-rc.2 exits silently on Node 20).
- Tests: real dsh host check (install, dump-config, headless run with a local stub model, removal) and end-to-end suite.
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `spindoctor-qwerty/` bundle folder with `package.json`, `cordis.patch.yml`, `index.js` and the engine.
