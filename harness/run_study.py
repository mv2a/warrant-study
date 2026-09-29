#!/usr/bin/env python3
"""Run harness for the Warrant study (protocol sections 3, 5, 6 and 7).

Runs on the verification host (14coresbeast). Every builder turn runs in a container
that mounts only that run's workspace; every evaluation runs in a network-less container
that mounts a pristine copy of the task's control files and a read-only snapshot of the
candidate. Builders never see checks/holdout (H) or audit (X).

Usage:
  run_study.py plan  --seed N                  write runs/plan.json (randomised order)
  run_study.py run   [--only RUN_ID ...] [--parallel K]

Set WSTUDY_TASKS and WSTUDY_RUNS to point the harness at other folders, for example a
smoke test on a non-study task before the protocol is frozen.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TASKS = pathlib.Path(os.environ.get("WSTUDY_TASKS", ROOT / "tasks"))
RUNS = pathlib.Path(os.environ.get("WSTUDY_RUNS", ROOT / "runs"))
VENDOR = ROOT / "harness" / "vendor"
ENV_FILE = pathlib.Path.home() / ".wstudy" / "env"

CONFIG = {
    "builder_image": "wstudy-builder:1",
    "verify_image": "python:3.11-slim",
    # Builder: Claude Code driving a local open-weights model through Ollama's
    # Anthropic-compatible API on the verification host's GPU (RTX 5070 Ti, 16 GB).
    "builder_backend": "ollama",
    "model": "gpt-oss-20b-32k",          # alias of gpt-oss:20b (digest 17052f91a42e) with num_ctx 32768
    "model_base": "gpt-oss:20b@17052f91a42e",
    "ollama_url": "http://localhost:11434",
    "max_submissions": 5,
    "wall_clock_s": 45 * 60,
    # The cap counts generated (output) tokens. A local model has no prompt caching, so every
    # turn re-sends the whole context and input tokens say more about turn count than work:
    # in the pilot a 1M total-token cap stopped B and C after 11 and 17 of their 45 minutes
    # (B's first submission: 390k input, 19k output). Input tokens are still recorded.
    "token_cap": 200_000,
    "token_cap_basis": "output",
    "run_budget_usd": 1.00,
    "study_budget_usd": 75.00,
    "builder_cpus": "2",
    "builder_memory": "2g",
    "verify_cpus": "2",
    "verify_memory": "1g",
    "check_timeout_s": 120,
}
CONDITIONS = ("A", "B", "C")
REPLICATES = (1, 2, 3)
LEDGER_LOCK = threading.Lock()


def sha256_dir(path):
    h = hashlib.sha256()
    for f in sorted(p for p in pathlib.Path(path).rglob("*") if p.is_file()):
        h.update(str(f.relative_to(path)).encode())
        h.update(b"\0")
        h.update(f.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def task_meta(task_dir):
    return json.loads((task_dir / "task.json").read_text())


def load_checks(check_dir):
    f = check_dir / "checks.toml"
    return tomllib.loads(f.read_text())["check"] if f.exists() else []


# ---------------------------------------------------------------- builder

PROMPT = """You are building a small command-line program. Its promises are in intent.md in this
directory. Write the program as one executable file named `{command}` in this directory,
starting with a python3 shebang, using only the Python standard library.

Before writing any code, read intent.md and every file in checks/public/. The visible
checks there show how the program will be called and what it must print. Run one with:
  cd checks/public && WARRANT_WORKSPACE=.. python3 <script>.py

When you have finished, stop. Your work will then be evaluated. If it is not accepted you
will get feedback and can revise it; you have at most {max_submissions} submissions in total."""

FEEDBACK = """Your submission {k} was not accepted.

{feedback}

Revise the program and stop when you are done. Submissions left after this one: {left}."""


def builder_turn(run_dir, message, resume_id, budget_usd, timeout_s):
    """One builder turn in a fresh container. Returns (parsed JSON result or None, wall seconds, raw)."""
    ws = run_dir / "workspace"
    home = run_dir / "builder_home"
    home.mkdir(exist_ok=True)
    cmd = ["docker", "run", "--rm", "--init",
           "--cpus", CONFIG["builder_cpus"], "--memory", CONFIG["builder_memory"], "-e", "IS_SANDBOX=1"]
    if CONFIG["builder_backend"] == "ollama":
        # Host network only so the builder can reach Ollama on localhost; no host paths but the workspace.
        cmd += ["--network", "host",
                "-e", f"ANTHROPIC_BASE_URL={CONFIG['ollama_url']}", "-e", "ANTHROPIC_API_KEY=ollama",
                "-e", f"ANTHROPIC_SMALL_FAST_MODEL={CONFIG['model']}",
                "-e", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1", "-e", "DISABLE_TELEMETRY=1",
                "-e", "DISABLE_AUTOUPDATER=1", "-e", "DISABLE_ERROR_REPORTING=1"]
    else:
        cmd += ["--env-file", str(ENV_FILE)]
    # Run as the host user so the builder can write its workspace and its session store,
    # with a per-run home directory (sessions persist across submissions for --resume).
    cmd += ["--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/home/builder",
            "-v", f"{ws}:/work", "-v", f"{home}:/home/builder", "-w", "/work",
            CONFIG["builder_image"],
            "claude", "-p", message, "--bare", "--model", CONFIG["model"],
            "--output-format", "json", "--permission-mode", "bypassPermissions",
            "--disallowedTools", "WebFetch", "WebSearch"]
    if CONFIG["builder_backend"] != "ollama":
        cmd += ["--max-budget-usd", f"{max(budget_usd, 0.01):.2f}"]
    if resume_id:
        cmd += ["--resume", resume_id]
    start = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=max(timeout_s, 30))
        raw = p.stdout
    except subprocess.TimeoutExpired as e:
        raw = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        return None, time.time() - start, raw + "\n[harness] builder turn timed out"
    wall = time.time() - start
    try:
        return json.loads(raw.strip().splitlines()[-1]), wall, raw
    except (json.JSONDecodeError, IndexError):
        return None, wall, raw + "\n" + p.stderr[-2000:]


def usage_tokens(result):
    """(input tokens including cache reads and writes, output tokens) for one builder turn."""
    u = (result or {}).get("usage") or {}
    tin = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return tin, int(u.get("output_tokens") or 0)


# ---------------------------------------------------------------- evaluation

def snapshot(run_dir, k):
    """Freeze the workspace for submission k: a tarball and its digest (protocol §6 step 3)."""
    ws = run_dir / "workspace"
    snap = run_dir / "snapshots" / f"s{k}"
    if snap.exists():
        shutil.rmtree(snap)
    shutil.copytree(ws, snap, ignore=shutil.ignore_patterns(".claude", "__pycache__"))
    return snap, sha256_dir(snap)


def verify_container(mounts, script, timeout):
    """Run a shell script in a network-less evaluation container."""
    cmd = ["docker", "run", "--rm", "--init", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp",
           "--cpus", CONFIG["verify_cpus"], "--memory", CONFIG["verify_memory"],
           "-e", "PYTHONDONTWRITEBYTECODE=1", "-e", "PYTHONPATH=/vendor"]
    for src, dst, mode in mounts:
        cmd += ["-v", f"{src}:{dst}:{mode}"]
    cmd += ["-v", f"{VENDOR}:/vendor:ro", CONFIG["verify_image"], "bash", "-c", script]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "evaluation timed out"


def run_suite(suite_dir, snap):
    """Run every check in a suite against a snapshot. Returns {id: {ok, covers, output}}."""
    results = {}
    for c in load_checks(suite_dir):
        runline = " ".join(json.dumps(a) for a in c["run"])
        script = f"cp -r /suite /tmp/s && cp -r /cand /tmp/ws && chmod -R u+rwX /tmp/ws && cd /tmp/s && WARRANT_WORKSPACE=/tmp/ws timeout {CONFIG['check_timeout_s']} {runline}"
        code, out, err = verify_container([(suite_dir, "/suite", "ro"), (snap, "/cand", "ro")], script, CONFIG["check_timeout_s"] + 60)
        results[c["id"]] = {"ok": code == 0, "covers": c.get("covers", []), "output": (out + err)[-600:]}
    return results


def warrant_eval(control, snap):
    """Conditions B and C: warrant verify, then warrant gate merge (protocol §3)."""
    script = ("cp -r /cand /tmp/ws && chmod -R u+rwX /tmp/ws && cd /control && "
              "python3 -m warrant verify --workspace /tmp/ws --audience builder > /tmp/v.txt 2>&1; echo \"VERIFY_EXIT=$?\"; "
              "python3 -m warrant gate merge --workspace /tmp/ws > /tmp/g.txt 2>&1; echo \"GATE_EXIT=$?\"; "
              "echo '---VERIFY---'; cat /tmp/v.txt; echo '---GATE---'; cat /tmp/g.txt")
    code, out, err = verify_container([(control, "/control", "rw"), (snap, "/cand", "ro")], script, 20 * 60)
    gate_ok = "GATE_EXIT=0" in out
    verify_txt = out.split("---VERIFY---", 1)[-1].split("---GATE---", 1)[0].strip()
    gate_txt = out.split("---GATE---", 1)[-1].strip()
    return gate_ok, verify_txt, gate_txt, code, err[-1000:]


def visible_feedback(v_results):
    lines = []
    for cid, r in v_results.items():
        lines.append(f"Visible check {cid}: {'passed' if r['ok'] else 'FAILED'}")
        if not r["ok"] and r["output"]:
            lines.append("  " + r["output"].strip().replace("\n", "\n  ")[-500:])
    return "\n".join(lines)


# ---------------------------------------------------------------- one run

def setup_run(run_id, task_dir, condition):
    run_dir = RUNS / run_id
    if run_dir.exists():
        shutil.rmtree(run_dir)
    ws = run_dir / "workspace"
    (ws / "checks").mkdir(parents=True)
    shutil.copy2(task_dir / "intent.md", ws / "intent.md")
    shutil.copytree(task_dir / "checks" / "public", ws / "checks" / "public")
    control = None
    if condition in ("B", "C"):
        control = run_dir / "control"
        control.mkdir()
        for name in ("intent.md", "warrant.toml"):
            shutil.copy2(task_dir / name, control / name)
        shutil.copytree(task_dir / "checks", control / "checks")
        code, out, err = verify_container(
            [(control, "/control", "rw")],
            "cd /control && python3 -m warrant check && python3 -m warrant approve --by study-harness --note 'Pre-registered study run'",
            300)
        if code != 0:
            raise RuntimeError(f"warrant approve failed: {out[-500:]} {err[-500:]}")
    return run_dir, ws, control


def execute_run(entry, spent):
    task_dir = TASKS / entry["task"]
    meta = task_meta(task_dir)
    run_id, condition = entry["run_id"], entry["condition"]
    run_dir, ws, control = setup_run(run_id, task_dir, condition)
    record = {"run_id": run_id, "label": entry["label"], "task": entry["task"], "condition": condition,
              "replicate": entry["replicate"], "config": CONFIG, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "workspace_digest_start": sha256_dir(ws), "submissions": [], "accepted": False}
    start = time.time()
    session, tokens_in, tokens_out, cost = None, 0, 0, 0.0
    message = PROMPT.format(command=meta["command"], max_submissions=CONFIG["max_submissions"])
    for k in range(1, CONFIG["max_submissions"] + 1):
        remaining_time = CONFIG["wall_clock_s"] - (time.time() - start)
        remaining_budget = min(CONFIG["run_budget_usd"] - cost, CONFIG["study_budget_usd"] - spent() - cost)
        capped = tokens_out if CONFIG["token_cap_basis"] == "output" else tokens_in + tokens_out
        limit = ("time" if remaining_time <= 0 else "tokens" if capped >= CONFIG["token_cap"]
                 else "budget" if remaining_budget <= 0 else None)
        if limit:
            record["ended"] = "limit:" + limit
            break
        result, wall, raw = builder_turn(run_dir, message, session, remaining_budget, remaining_time)
        (run_dir / f"transcript_s{k}.json").write_text(raw)
        session = (result or {}).get("session_id") or session
        tin, tout = usage_tokens(result)
        tokens_in, tokens_out = tokens_in + tin, tokens_out + tout
        tokens = tokens_in + tokens_out
        reported = float((result or {}).get("total_cost_usd") or 0)
        record["claude_reported_cost_usd"] = round(record.get("claude_reported_cost_usd", 0) + reported, 4)
        if CONFIG["builder_backend"] != "ollama":  # a local model has no list price (protocol deviation D1)
            cost += reported
        snap, digest = snapshot(run_dir, k)
        v = run_suite(task_dir / "checks" / "public", snap)
        sub = {"k": k, "digest": digest, "builder_wall_s": round(wall, 1), "tokens_cumulative": tokens, "output_tokens_cumulative": tokens_out,
               "cost_cumulative_usd": round(cost, 4), "visible": {c: r["ok"] for c, r in v.items()},
               "builder_error": None if result else "no parseable builder result"}
        if condition == "A":
            accepted = bool(v) and all(r["ok"] for r in v.values())
            feedback = visible_feedback(v)
        else:
            accepted, verify_txt, gate_txt, _, _ = warrant_eval(control, snap)
            sub["gate"] = gate_txt[-1500:]
            feedback = visible_feedback(v)
            if condition == "B":
                feedback += "\n\nWarrant's verification, as shown to builders:\n" + verify_txt[-3000:]
        sub["accepted"] = accepted
        record["submissions"].append(sub)
        if accepted:
            record["accepted"] = True
            record["ended"] = "accepted"
            break
        left = CONFIG["max_submissions"] - k
        if left == 0:
            record["ended"] = "submissions"
            break
        message = FEEDBACK.format(k=k, feedback=feedback, left=left)
    record.setdefault("ended", "limit:time")  # the last builder turn ran out the wall clock
    last = record["submissions"][-1]["k"] if record["submissions"] else None
    final_k = next((s["k"] for s in record["submissions"] if s["accepted"]), last)
    if final_k is not None:
        final_snap = run_dir / "snapshots" / f"s{final_k}"
        x = run_suite(task_dir / "audit", final_snap)
        broken = sorted({p for r in x.values() if not r["ok"] for p in r["covers"]})
        record["final_submission"] = final_k
        record["audit"] = {c: {"ok": r["ok"], "covers": r["covers"]} for c, r in x.items()}
        record["promises_broken"] = broken
        record["escaped_defects"] = len(broken) if record["accepted"] else 0
        record["false_pass"] = int(record["accepted"] and bool(broken))
        record["correct_delivery"] = int(record["accepted"] and not broken)
    else:
        record.update({"final_submission": None, "audit": {}, "promises_broken": [], "escaped_defects": 0, "false_pass": 0, "correct_delivery": 0})
    record["tokens"] = tokens_in + tokens_out
    record["tokens_input"] = tokens_in
    record["tokens_output"] = tokens_out
    record["cost_usd"] = round(cost, 4)
    record["wall_minutes"] = round((time.time() - start) / 60, 2)
    record["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if control:
        shutil.copytree(control / "ledger", run_dir / "ledger", dirs_exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps(record, indent=1))
    return record


# ---------------------------------------------------------------- plan and main

def make_plan(seed):
    rng = random.Random(seed)
    tasks = sorted(p.name for p in TASKS.iterdir() if (p / "task.json").exists())
    entries = []
    for t in tasks:
        cells = [(c, r) for c in CONDITIONS for r in REPLICATES]
        rng.shuffle(cells)
        for c, r in cells:
            label = "%08x" % rng.getrandbits(32)
            entries.append({"run_id": f"{t}-{c}-r{r}", "label": label, "task": t, "condition": c, "replicate": r})
    plan = {"seed": seed, "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "config": CONFIG, "runs": entries}
    RUNS.mkdir(exist_ok=True)
    (RUNS / "plan.json").write_text(json.dumps(plan, indent=1))
    print(f"planned {len(entries)} runs over {len(tasks)} tasks, seed {seed}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("plan"); p1.add_argument("--seed", type=int, required=True)
    p2 = sub.add_parser("run"); p2.add_argument("--only", nargs="*"); p2.add_argument("--parallel", type=int, default=3)
    a = ap.parse_args()
    if a.cmd == "plan":
        make_plan(a.seed)
        return
    if CONFIG["builder_backend"] != "ollama" and not ENV_FILE.exists():
        sys.exit(f"missing {ENV_FILE}: the API key file must be created by the study owner")
    plan = json.loads((RUNS / "plan.json").read_text())
    todo = [e for e in plan["runs"] if (not a.only or e["run_id"] in a.only) and not (RUNS / e["run_id"] / "run.json").exists()]
    lock = threading.Lock()
    totals = {"cost": sum(json.loads(p.read_text()).get("cost_usd", 0) for p in RUNS.glob("*/run.json"))}

    def spent():
        with lock:
            return totals["cost"]

    def one(e):
        if spent() >= CONFIG["study_budget_usd"]:
            return {"run_id": e["run_id"], "skipped": "study budget reached"}
        for attempt in (1, 2):  # infrastructure failures are rerun once (protocol §6)
            try:
                r = execute_run(e, spent)
                with lock:
                    totals["cost"] += r["cost_usd"]
                return r
            except Exception as err:  # noqa: BLE001 - recorded, not hidden
                (RUNS / e["run_id"]).mkdir(parents=True, exist_ok=True)
                (RUNS / e["run_id"] / f"infra_failure_{attempt}.txt").write_text(repr(err))
        rec = {"run_id": e["run_id"], "label": e["label"], "task": e["task"], "condition": e["condition"], "replicate": e["replicate"],
               "failed": "infrastructure failure twice", "accepted": False, "escaped_defects": 0, "false_pass": 0, "correct_delivery": 0, "cost_usd": 0}
        (RUNS / e["run_id"] / "run.json").write_text(json.dumps(rec, indent=1))
        return rec

    with cf.ThreadPoolExecutor(max_workers=a.parallel) as pool:
        for r in pool.map(one, todo):
            print(json.dumps({k: r.get(k) for k in ("run_id", "accepted", "escaped_defects", "cost_usd", "ended", "skipped", "failed")}), flush=True)
    print(f"total spent ${spent():.2f}")


if __name__ == "__main__":
    main()
