# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for DeepSeek Harness
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""DeepSeek Harness host check. Standard library only (Python 3.8+); Node.js 22+ for the plugin and dsh.
No account, no sign-in, no API key, no model.

1. Static: package.json (dsh.bundle.patch, ESM entry, license, author, files, peer dependency), cordis.patch.yml (one insert
   row whose `name` is the package name), text only.
2. Node, no host: index.js exports name/inject/apply; its TOOL_DEFS equal the engine's own tool list; definitions() builds six
   tools; a call returns the function table; a pre-aborted exec.signal cancels; a missing Python throws (tool error).
3. With the REAL dsh CLI (DSH=/path/to/dsh, Node 22+ on PATH) in a throw-away DSH_HOME/HOME: `dsh plugin --profile headless add
   <repo>` (the documented install), the profile lists the bundle, `dsh --profile headless --dump-config` shows its layer and row,
   then `dsh --profile headless --patch <overlay> "<task>"` with an overlay that routes the model to tests/stub_llm.py, a local
   scripted OpenAI-compatible endpoint (not an LLM; the apiKeyEnv value is a placeholder the stub ignores): dsh offers the six
   tools and EXECUTES scripted calls (function table, Bell script, preset qc-001, chat-history theory test). Finally
   `dsh plugin --profile headless remove dsh-spindoctor-qwerty` removes the dependency and the layer.
4. Engine end-to-end: tests/e2e_mcp.py through engine/scripts/spindoctor_mcp.py (same engine the tools call).

usage: python3 tests/dsh_host_check.py [REPO_DIR]"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = (".py", ".md", ".json", ".txt", ".csv", ".html", ".q", ".js", ".yml", "")
TOOLS = ["spindoctor_run_script", "spindoctor_run_preset", "spindoctor_list_presets", "spindoctor_report", "spindoctor_functions", "spindoctor_test_theory"]

NODE_PROBE = r"""
const m = await import(process.argv[2]);
const out = { name: m.name, inject: m.inject, apply: typeof m.apply, defs: m.TOOL_DEFS };
const tools = m.definitions(); out.n = tools.length; out.names = tools.map((t) => t.name);
out.params = Object.fromEntries(tools.map((t) => [t.name, t.parameters]));
const fn = tools.find((t) => t.name === "spindoctor_functions");
out.table = (await fn.execute({ section: "gates" }, { signal: new AbortController().signal })).slice(0, 200);
const ac = new AbortController(); ac.abort();
out.cancelled = await fn.execute({}, { signal: ac.signal });
process.env.SPINDOCTOR_PYTHON = "/nonexistent/python3";
const m2 = await import(process.argv[2] + "?nopython");
try { await m2.definitions()[4].execute({}, { signal: new AbortController().signal }); out.nopython = "no error"; } catch (e) { out.nopython = "threw: " + e.message; }
console.log(JSON.stringify(out));
"""


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def main():
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"; sys.dont_write_bytecode = True
    repo = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
    ok = True; mode = "host-simulated"

    def T(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:700])); sys.stdout.flush()

    pkg = json.load(open(os.path.join(repo, "package.json"), encoding="utf-8"))
    patch = open(os.path.join(repo, "cordis.patch.yml"), encoding="utf-8").read()
    T("package.json: dsh.bundle.patch -> ./cordis.patch.yml, ESM main index.js, GPL-3.0-or-later, author, files cover the runtime, peer @deepseek-ai/dsh-tools",
      pkg["dsh"] == {"bundle": {"patch": "./cordis.patch.yml"}} and pkg["type"] == "module" and pkg["main"] == "index.js" and pkg["license"] == "GPL-3.0-or-later"
      and pkg["author"]["name"] == "RUSSELL PHILIP SMITHSON" and pkg["version"] == "1.1.0" and {"index.js", "cordis.patch.yml", "engine/"} <= set(pkg["files"])
      and "@deepseek-ai/dsh-tools" in pkg.get("peerDependencies", {}) and not pkg.get("dependencies"), pkg)
    rows = re.findall(r"^\s*-\s*id:\s*(\S+)\s*\n\s*name:\s*(\S+)\s*$", patch, re.M)
    T("cordis.patch.yml: one `insert` row whose name is the package name (resolved by Node from the installed bundle)",
      re.search(r"^- insert:\s*$", patch, re.M) and rows == [("spindoctor-qwerty", pkg["name"])], rows)
    bad = [os.path.relpath(os.path.join(r, f), repo) for r, ds, fs in os.walk(repo) if ".git" not in r.split(os.sep) and "__pycache__" not in r and "node_modules" not in r
           for f in fs if os.path.splitext(f)[1].lower() not in TEXT and not (f.endswith(".pdf") and r.endswith(os.path.join("examples", "theory")))]
    T("only text files (sample PDFs are generated by make_sample_pdfs.py and git-ignored)", not bad, bad)

    node = shutil.which("node")
    if not node:
        T("Node.js found", False, "node not on PATH"); print("HOST-CHECK FAIL"); return 1
    nv = subprocess.run([node, "--version"], stdout=subprocess.PIPE, text=True).stdout.strip()
    tmp = tempfile.mkdtemp(prefix="sdq_dsh_"); home = os.path.join(tmp, "home"); os.makedirs(home)
    probe = os.path.join(tmp, "probe.mjs"); open(probe, "w").write(NODE_PROBE)
    r = subprocess.run([node, probe, "file://" + os.path.join(repo, "index.js")], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       env=dict(os.environ, HOME=home, SPINDOCTOR_WORKSPACE=os.path.join(tmp, "ws0")), timeout=300)
    try: pr = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: pr = {}
    sys.path.insert(0, os.path.join(repo, "engine")); from spindoctor import api
    eng = [{"name": t["name"], "description": t["description"], "parameters": t.get("inputSchema") or t.get("parameters")} for t in api.TOOLS]
    T("node %s, no host: exports name/inject=['tools']/apply; TOOL_DEFS equal the engine's tool list" % nv,
      pr.get("name") == "spindoctor-qwerty" and pr.get("inject") == ["tools"] and pr.get("apply") == "function" and pr.get("defs") == eng, r.stdout[-600:])
    pa = pr.get("params", {})
    T("definitions(): six tools; parameters use the dsh-tools DSL (required flags, explicit object openness, typed array items)",
      pr.get("names") == TOOLS and pa["spindoctor_run_script"]["script"].get("required") is True
      and pa["spindoctor_run_preset"]["overrides"].get("additionalProperties") is True and pa["spindoctor_test_theory"]["excerpts"]["items"] == {"type": "string"}
      and pa["spindoctor_test_theory"]["checks"]["items"] == {"type": "object", "additionalProperties": True}, pa)
    T("execute(): function table returned; a pre-aborted exec.signal cancels; a missing Python throws (reported as a tool error)",
      "| Function | What it does | Command to type |" in pr.get("table", "") and "cancelled" in pr.get("cancelled", "") and pr.get("nopython", "").startswith("threw: Python 3.8+ was not found"),
      {k: pr.get(k) for k in ("table", "cancelled", "nopython")})

    dsh = os.environ.get("DSH") or shutil.which("dsh")
    if dsh:
        mode = "real DeepSeek Harness dsh (headless, model = local scripted stub)"
        dhome = os.path.join(tmp, "dshhome"); proj = os.path.join(tmp, "project"); os.makedirs(proj)
        env = dict(os.environ, HOME=home, DSH_HOME=dhome, DBUS_SESSION_BUS_ADDRESS="disabled:", SPINDOCTOR_WORKSPACE=os.path.join(tmp, "ws"))
        for k in [k for k in env if k.endswith("_API_KEY") or k.startswith("DSH_PROFILE")]: env.pop(k)

        def run(*a, **k):
            return subprocess.run([dsh] + list(a), env=k.pop("env", env), cwd=k.pop("cwd", proj), stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=600)
        v = run("--version").stdout.strip()
        r = run("plugin", "--profile", "headless", "add", repo)
        prof = json.load(open(os.path.join(dhome, "profiles", "headless", "package.json"))) if r.returncode == 0 else {}
        T("dsh %s: `dsh plugin --profile headless add <repo>` links the bundle and appends it to dsh.profile.bundles" % v,
          r.returncode == 0 and prof.get("dsh", {}).get("profile", {}).get("bundles", [])[-1:] == [pkg["name"]] and pkg["name"] in prof.get("dependencies", {}), (r.stdout[-400:], r.stderr[-400:]))
        r = run("--profile", "headless", "--dump-config")
        T("dsh --dump-config: '# == dsh-spindoctor-qwerty' layer with the spindoctor-qwerty row", r.returncode == 0 and "# == dsh-spindoctor-qwerty" in r.stdout
          and re.search(r"- id: spindoctor-qwerty\n\s+name: dsh-spindoctor-qwerty", r.stdout), r.stdout[-500:] + r.stderr[-300:])
        port = free_port(); log = os.path.join(tmp, "stub.jsonl"); script = os.path.join(tmp, "script.json"); overlay = os.path.join(tmp, "stub.patch.yml")
        open(overlay, "w").write("""- id: llm-pi-ai
  config:
    providers:
      stub:
        displayName: Local scripted stub
        api: openai-completions
        apiKeyEnv: SDQ_STUB_KEY
        baseURL: http://127.0.0.1:%d/v1
        models:
          - id: stub
            name: stub
            contextWindow: 131072
- id: agent-default-model
  config:
    provider: stub
    model: stub
""" % port)
        steps = [{"tool": "spindoctor_functions", "args": {"section": "commands"}},
                 {"tool": "spindoctor_run_script", "args": {"script": "q.circuit new bell 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 1000 basis z"}},
                 {"tool": "spindoctor_run_preset", "args": {"preset_id": "qc-001"}},
                 {"tool": "spindoctor_test_theory", "args": {"action": "run", "source": "chat", "text": "Claim: H then CX gives a Bell state; P(00)=P(11)=0.5.",
                  "excerpts": ["User: so H then CX should split 00 and 11 evenly?", "Assistant: yes, about half each"],
                  "hypothesis": "H on qubit 0 then CX(0,1) prepares a Bell state.", "prediction": "P(11) = 0.5 within shot noise.",
                  "script": "q.circuit new t 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 2000 basis z",
                  "checks": [{"kind": "probability", "outcome": "11", "expected": 0.5, "tolerance": 0.05}]}},
                 {"text": "FINAL-DONE"}]
        json.dump(steps, open(script, "w"))
        stub = subprocess.Popen([sys.executable, os.path.join(HERE, "stub_llm.py"), str(port), log, script])
        flat = lambda x: x if isinstance(x, str) else json.dumps(x)
        try:
            time.sleep(1.0)
            r = run("--profile", "headless", "--patch", overlay, "show the SpinDoctor functions, run a Bell pair, preset qc-001 and test our theory",
                    env=dict(env, SDQ_STUB_KEY="local-stub-placeholder"))
            recs = [json.loads(l) for l in open(log) if l.strip()] if os.path.isfile(log) else []; ag = [x for x in recs if x["tools"]]
            T("dsh --profile headless (local stub model, no account): the model is offered the six spindoctor_* tools",
              r.returncode == 0 and "FINAL-DONE" in r.stdout and ag and all(t in ag[0]["tools"] for t in TOOLS), (r.stdout[-300:], r.stderr[-500:], ag[0]["tools"] if ag else None))
            res = ag[-1]["tool_results"] if ag else []
            pdfs = [p for p in re.findall(r"[^\"\s\\]+?\.pdf", " ".join(flat(x) for x in res)) if os.path.isabs(p)]
            T("dsh executed 4 tool calls through the plugin: table, Bell, qc-001, chat-history theory (supported); PDFs on disk",
              len(res) == 4 and "| Function | What it does | Command to type |" in flat(res[0]) and "q.circuit" in flat(res[1]) and '"qc-001"' in flat(res[2])
              and '"ok": true' in flat(res[2]) and "supported" in flat(res[3]) and len(pdfs) >= 6 and any("theory" in p.lower() for p in pdfs) and all(os.path.isfile(p) for p in pdfs),
              {"n": len(res), "res": [flat(x)[:200] for x in res], "pdfs": pdfs[:4]})
        finally:
            stub.kill()
        r = run("plugin", "--profile", "headless", "remove", pkg["name"]); d2 = run("--profile", "headless", "--dump-config").stdout
        T("dsh plugin --profile headless remove dsh-spindoctor-qwerty: dependency and layer gone", r.returncode == 0 and "dsh-spindoctor-qwerty" not in d2, (r.stdout[-300:], r.stderr[-300:]))
    else:
        print("SKIP real dsh not found (set DSH=/path/to/dsh; needs Node.js 22+)")
    ex = os.path.join(repo, "engine", "examples", "theory")
    r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server", sys.executable, os.path.join(repo, "engine", "scripts", "spindoctor_mcp.py"),
                        "--examples", ex, "--out", os.path.join(tmp, "e2e_results.json")], env=dict(os.environ, SPINDOCTOR_WORKSPACE=os.path.join(tmp, "ws2"), HOME=home))
    T("engine end-to-end (tests/e2e_mcp.py through engine/scripts/spindoctor_mcp.py)", r.returncode == 0)
    shutil.rmtree(tmp, ignore_errors=True)
    print("HOST-CHECK (%s)" % mode, "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
