#!/usr/bin/env python3
"""Seeded-defect evaluation: visible-only acceptance versus Warrant's gate, no builder involved.

For every task, the reference implementation and each deliberately broken implementation
(broken/<promise>/) are judged three ways:
  visible-only  every visible check (V) passes, the acceptance rule of condition A;
  Warrant       `warrant verify` then `warrant gate merge` issues a warrant, as in B and C;
  audit         the audit suite (X) run against it: the promises it breaks (ground truth).

Caveat, reported with the results: each task's author (an AI agent) wrote V, H, the reference
and the broken implementations; a separate AI agent wrote X. So H was written by the same
agent that planted the defects, and the Warrant column is a sanity check on the suites rather
than an estimate of how often hidden checks catch defects an independent builder makes.

Runs locally with the vendored Warrant. Usage: eval_mutants.py [--jobs N] [--out FILE]
"""
import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import gates  # noqa: E402  (reuses its suite runner)

ROOT = pathlib.Path(__file__).resolve().parent.parent
TASKS = ROOT / "tasks"
VENDOR = ROOT / "harness" / "vendor"


def warrant(control, *args, timeout=1200):
    env = {**os.environ, "PYTHONPATH": str(VENDOR), "PYTHONDONTWRITEBYTECODE": "1"}
    p = subprocess.run([sys.executable, "-m", "warrant", *args], cwd=control, env=env,
                       capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)


def judge(task_dir, control, impl_dir, command):
    with tempfile.TemporaryDirectory() as tmp:
        ws = pathlib.Path(tmp) / "ws"
        ws.mkdir()
        shutil.copy2(impl_dir / command, ws / command)
        os.chmod(ws / command, 0o755)
        v = gates.suite(task_dir / "checks" / "public", ws)
        t = time.time()
        vcode, vout = warrant(control, "verify", "--workspace", str(ws), "--audience", "builder")
        gcode, gout = warrant(control, "gate", "merge", "--workspace", str(ws))
        secs = time.time() - t
        x = gates.suite(task_dir / "audit", ws)
    return {
        "visible_accept": bool(v) and all(ok for ok, _, _ in v.values()),
        "warrant_accept": gcode == 0,
        "x_broken": sorted({p for ok, _, cov in x.values() if not ok for p in cov}),
        "verify_gate_seconds": round(secs, 2),
        "gate_tail": gout.strip().splitlines()[:4],
    }


def eval_task(task_dir):
    meta = json.loads((task_dir / "task.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        control = pathlib.Path(tmp) / "control"
        control.mkdir()
        for name in ("intent.md", "warrant.toml"):
            shutil.copy2(task_dir / name, control / name)
        shutil.copytree(task_dir / "checks", control / "checks", ignore=shutil.ignore_patterns("__pycache__"))
        code, out = warrant(control, "check")
        if code != 0:
            return {"task": task_dir.name, "error": "warrant check failed: " + out[-300:]}
        code, out = warrant(control, "approve", "--by", "study-harness", "--note", "Seeded-defect evaluation")
        if code != 0:
            return {"task": task_dir.name, "error": "warrant approve failed: " + out[-300:]}
        rows = [{"task": task_dir.name, "impl": "reference", "target": None,
                 **judge(task_dir, control, task_dir / "reference", meta["command"])}]
        for b in sorted(p for p in (task_dir / "broken").iterdir() if p.is_dir()):
            rows.append({"task": task_dir.name, "impl": "broken/" + b.name, "target": b.name,
                         **judge(task_dir, control, b, meta["command"])})
    return {"task": task_dir.name, "rows": rows}


def summarise(rows):
    ref = [r for r in rows if r["impl"] == "reference"]
    mut = [r for r in rows if r["impl"] != "reference"]
    defective = [r for r in mut if r["x_broken"]]
    n = len(defective)
    s = {
        "tasks": len(ref),
        "reference_visible_accept": sum(r["visible_accept"] for r in ref),
        "reference_warrant_accept": sum(r["warrant_accept"] for r in ref),
        "reference_x_clean": sum(not r["x_broken"] for r in ref),
        "broken_implementations": len(mut),
        "broken_with_x_defect": n,
        "broken_hitting_target_promise": sum(r["target"] in r["x_broken"] for r in mut),
        "defective_accepted_visible_only": sum(r["visible_accept"] for r in defective),
        "defective_accepted_by_warrant": sum(r["warrant_accept"] for r in defective),
        "defective_accepted_by_both": sum(r["visible_accept"] and r["warrant_accept"] for r in defective),
        "verify_gate_seconds_median": round(statistics.median(r["verify_gate_seconds"] for r in rows), 2),
        "verify_gate_seconds_max": max(r["verify_gate_seconds"] for r in rows),
    }
    s["false_pass_rate_visible_only"] = round(s["defective_accepted_visible_only"] / n, 3) if n else None
    s["false_pass_rate_warrant"] = round(s["defective_accepted_by_warrant"] / n, 3) if n else None
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", default=str(ROOT / "results" / "seeded_defects.json"))
    a = ap.parse_args()
    tasks = sorted(p for p in TASKS.iterdir() if (p / "task.json").exists())
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(eval_task, tasks))
    errors = [r for r in results if "error" in r]
    rows = [row for r in results for row in r.get("rows", [])]
    report = {"started": started, "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "python": sys.version.split()[0], "errors": errors, "summary": summarise(rows), "rows": rows}
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps(report["summary"], indent=1))
    if errors:
        print("ERRORS:", json.dumps(errors, indent=1))


if __name__ == "__main__":
    main()
