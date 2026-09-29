#!/usr/bin/env python3
"""Validity gates for one study task (protocol section 4). Usage: gates.py TASK_DIR

Exit 0 when every gate passes. Writes TASK_DIR/gates_report.json.
Runs only trusted code: the task's reference and deliberately broken implementations.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
VENDOR = HERE / "vendor"


def load(check_dir):
    f = check_dir / "checks.toml"
    return tomllib.loads(f.read_text())["check"] if f.exists() else []


def run(check_dir, check, workspace, timeout=120):
    env = {**os.environ, "WARRANT_WORKSPACE": str(workspace), "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        p = subprocess.run(check["run"], cwd=check_dir, env=env, capture_output=True, text=True, timeout=timeout)
        return p.returncode == 0, (p.stdout + p.stderr).strip()[-400:]
    except subprocess.TimeoutExpired:
        return False, "timed out"


def suite(check_dir, workspace):
    return {c["id"]: (*run(check_dir, c, workspace), c.get("covers", [])) for c in load(check_dir)}


def main(task):
    task = pathlib.Path(task).resolve()
    fails, notes, report = [], [], {"task": task.name}
    meta = json.loads((task / "task.json").read_text())
    cmd, promised = meta["command"], meta["promises"]
    intent_ids = re.findall(r"^- ([GCS]\d+):", (task / "intent.md").read_text(), re.M)
    if sorted(intent_ids) != sorted(promised):
        fails.append(f"intent.md promises {intent_ids} differ from task.json {promised}")
    if not 5 <= len(intent_ids) <= 12:
        fails.append(f"{len(intent_ids)} promises; the protocol needs 5 to 12")
    dirs = {"V": task / "checks/public", "H": task / "checks/holdout", "X": task / "audit"}
    ref = task / "reference"
    if not os.access(ref / cmd, os.X_OK):
        fails.append(f"reference/{cmd} is missing or not executable")
    for name, d in dirs.items():
        checks = load(d)
        if not checks:
            fails.append(f"{name} has no checks")
        for c in checks:
            bad = set(c.get("covers", [])) - set(promised)
            if bad:
                fails.append(f"{name} check {c['id']} covers unknown promises {sorted(bad)}")
    nv = len(load(dirs["V"]))
    if not 2 <= nv <= 4:
        fails.append(f"V has {nv} checks; the spec asks for 2 to 4")
    for name in ("H", "X"):
        covered = {p for c in load(dirs[name]) for p in c.get("covers", [])}
        missing = sorted(set(promised) - covered)
        if missing:
            fails.append(f"{name} does not cover {missing}")
    report["reference"] = {}
    for name, d in dirs.items():
        res = suite(d, ref)
        report["reference"][name] = {k: v[0] for k, v in res.items()}
        for cid, (ok, out, _) in res.items():
            if not ok:
                fails.append(f"reference fails {name} check {cid}: {out[:160]}")
    report["broken"] = {}
    broken_dir = task / "broken"
    have = sorted(p.name for p in broken_dir.iterdir() if p.is_dir()) if broken_dir.exists() else []
    for p in promised:
        if p not in have:
            listed = (broken_dir / "README.md").exists() and p in (broken_dir / "README.md").read_text()
            if not listed:
                fails.append(f"no broken implementation for {p}, and broken/README.md does not explain why")
            continue
        impl = broken_dir / p
        if not os.access(impl / cmd, os.X_OK):
            fails.append(f"broken/{p}/{cmd} is missing or not executable")
            continue
        xres = suite(dirs["X"], impl)
        caught = [cid for cid, (ok, _, cov) in xres.items() if not ok and p in cov]
        vres = suite(dirs["V"], impl)
        fools_v = all(ok for ok, _, _ in vres.values())
        report["broken"][p] = {"caught_by_X": caught, "passes_V": fools_v}
        if not caught:
            fails.append(f"X does not catch broken/{p}: no failing X check covers {p}")
    env = {**os.environ, "PYTHONPATH": str(VENDOR)}
    wc = subprocess.run([sys.executable, "-m", "warrant", "-C", str(task), "check"], env=env, capture_output=True, text=True)
    report["warrant_check"] = wc.returncode
    if wc.returncode != 0:
        fails.append("warrant check failed: " + (wc.stdout + wc.stderr).strip()[-300:])
    report["fails"] = fails
    report["passed"] = not fails
    (task / "gates_report.json").write_text(json.dumps(report, indent=1))
    fooling = sum(1 for b in report["broken"].values() if b["passes_V"])
    print(f"{task.name}: {'PASS' if not fails else 'FAIL'} | promises {len(promised)} | V {nv} H {len(load(dirs['H']))} X {len(load(dirs['X']))} checks | broken {len(report['broken'])} ({fooling} pass V)")
    for f in fails:
        print("  -", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
