# SpinDoctor Qwerty for DeepSeek Harness

**DeepSeek Harness (`dsh`) bundle for the SpinDoctor 3.1.2 quantum-circuit simulator.** It adds six tools to
[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (web, TUI, headless and SDK profiles): build and run `q.*`
circuits (1-298 logical qubits), run the 241 built-in presets, process folders of command files with `q.folder`, show the in-chat
function table, test theories from files, pasted text or the conversation itself, and get TXT, PDF, JSON and CSV reports.
Everything runs locally in a bundled, standard-library-only Python engine.

> **Honest limits:** SpinDoctor is a **classical** FP64 simulator running on your computer. It is not a quantum computer, does not
> connect to quantum hardware and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
> group (factor) is limited to 59 qubits and dense factors to the memory budget (2^n x 16 bytes); registers wider than 29 qubits
> sample in basis Z only. Histograms come from seeded Born sampling. Requires **Python 3.8+** (no packages) and, for dsh itself,
> **Node.js 22+**.

Version **1.1.0** (engine 1.1.0, "SpinDoctor 3.1.2 parity"). Author: RUSSELL PHILIP SMITHSON. License: GPL-3.0-or-later.
DeepSeek Harness is a public preview; this bundle was built and tested against `@deepseek-ai/dsh` **0.2.0-rc.2**.

## What's in the bundle

The repo root is a dsh **bundle** as described in the harness docs
([Package and install a plugin](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/publish.md),
[Build a tool](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/tool.md)).

| Part | File | What it does |
|---|---|---|
| Bundle manifest | `package.json` | `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }`, ESM entry `index.js`, license, author; `@deepseek-ai/dsh-tools` as a peer dependency so the running dsh's copy is used |
| Patch layer | `cordis.patch.yml` | Inserts one plugin row, `id: spindoctor-qwerty`, `name: dsh-spindoctor-qwerty` (resolved by package name) |
| Cordis plugin | `index.js` | `name`, `inject = ['tools']`, `apply(ctx)` registers six tools with `ctx.tools.register(defineTool(...))`; honours `exec.signal` (cancel stops the engine) |
| Engine | `engine/` | The Python engine (`engine/spindoctor/`), its CLI and MCP server (`engine/scripts/`) and sample theory files (`engine/examples/theory/`) |

The tools are `spindoctor_run_script`, `spindoctor_run_preset`, `spindoctor_list_presets`, `spindoctor_report`,
`spindoctor_functions` and `spindoctor_test_theory`. Each call runs `python3 engine/scripts/spindoctor_cli.py tool <name>` with
the arguments as JSON on stdin. No hooks, no settings, no secrets, no network access, no telemetry. Nothing runs until the model
calls a tool. Reports go to `~/spindoctor-workspace` (set `SPINDOCTOR_WORKSPACE` before starting dsh to change it).

## Install

You need DeepSeek Harness (`dsh`, Node.js 22+) and Python 3.8+.

**From a local checkout** (the documented route for a bundle):

```sh
git clone https://github.com/LKVexa/spindoctor-qwerty-deepseek-harness
dsh plugin --profile web add ./spindoctor-qwerty-deepseek-harness
dsh --profile web --dump-config      # shows a "# == dsh-spindoctor-qwerty" layer
dsh web
```

Use the profile you actually boot (`web`, `tui`, `headless`, or one of your own). `dsh plugin` links the checkout and appends
`dsh-spindoctor-qwerty` to the profile's bundle list. Then ask *"show the SpinDoctor functions"*.
`dsh plugin --profile web remove dsh-spindoctor-qwerty` removes it again.

**Straight from GitHub:** `dsh plugin --profile web add github:LKVexa/spindoctor-qwerty-deepseek-harness#<commit>`. The bundle is
plain JavaScript with no build step, so pnpm doesn't need an `allowBuilds` entry for it. Pin a commit so a later push can't
change what runs.

**Python command:** the tools try `python3`, then `python` (macOS/Linux), or `python`, then `py` (Windows). To use a specific
interpreter, set `SPINDOCTOR_PYTHON` (for example to the full path of `python.exe`) in the environment that starts dsh.
`SPINDOCTOR_TIMEOUT_MS` changes the 10-minute per-call limit.

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | Ask: "show the SpinDoctor functions" |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | Ask: "run preset qc-067 with shots=64" |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | Ask: "test the theory we discussed" or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In DeepSeek Harness, give the file's path on your computer (or paste the text).
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `engine/examples/theory/`. The two sample
PDFs are stored as text; run `python3 engine/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Testing

| Test | Command | Result for 1.1.0 |
|---|---|---|
| Host check (real dsh 0.2.0-rc.2, headless profile) | `DSH=$(command -v dsh) python3 tests/dsh_host_check.py` | 12/12 checks, end-to-end 12/12 |

**Real host, local stub model.** `@deepseek-ai/dsh` 0.2.0-rc.2 was installed from npm on a Linux test machine (Node.js 22.19) with
no account, sign-in or API key. `tests/dsh_host_check.py` installs the bundle with `dsh plugin --profile headless add`, checks the
profile and `--dump-config`, then runs `dsh --profile headless` with a `--patch` overlay that points dsh's model route at
`tests/stub_llm.py`, a local scripted OpenAI-compatible endpoint (not a language model; the overlay's `apiKeyEnv` value is a
placeholder the stub ignores). dsh offered the six tools and executed four calls through the plugin: the function table, a Bell
circuit, preset qc-001 and a chat-history theory test (verdict *supported*, PDFs written). It then removes the bundle. It also
loads `index.js` in plain Node (cancellation through `exec.signal`, a missing Python reported as a tool error) and runs the full
end-to-end suite against the bundled engine. Whether a real DeepSeek model picks the tools as intended isn't tested. Details in
[E2E_RESULTS.md](E2E_RESULTS.md).

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). `package.json` carries the license and author. DeepSeek is a
trademark of its owner; this project is not affiliated with DeepSeek.
