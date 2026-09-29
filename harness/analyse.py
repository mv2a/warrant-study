#!/usr/bin/env python3
"""Part 2 analysis (EVALUATION_PLAN.md): conditions A and B, one run per task.

Written and committed after the first run finished and before the results were analysed,
so that the tests below are fixed in advance:
  - false pass and correct delivery: exact McNemar test on the task-paired binary
    outcomes, i.e. a two-sided binomial test on the discordant pairs (p = 0.5);
  - escaped defects: Wilcoxon signed-rank test on the paired per-task counts, B minus A,
    two-sided, zero differences dropped (Wilcoxon's method, scipy zero_method="wilcox"),
    with scipy choosing the exact distribution or the normal approximation (method="auto");
  - acceptance, submissions, wall-clock minutes, input and output tokens: descriptive.
All tests are exploratory. A task with a failed run in either condition is dropped from
the paired tests and reported.

Usage: analyse.py RUNS_DIR [--out results/agent_runs.json]
"""
import argparse
import json
import math
import pathlib
import statistics

try:
    from scipy.stats import wilcoxon
except ImportError:  # the verification host has no scipy; run the analysis on a machine that has it
    wilcoxon = None


def mcnemar_exact(pairs):
    """pairs: list of (a, b) booleans. Returns (b_only, a_only, p) for the exact McNemar test."""
    a_only = sum(1 for a, b in pairs if a and not b)
    b_only = sum(1 for a, b in pairs if b and not a)
    n = a_only + b_only
    if n == 0:
        return b_only, a_only, 1.0
    k = min(a_only, b_only)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n * 2
    return b_only, a_only, min(1.0, p)


def load(runs_dir):
    runs = {}
    for f in sorted(pathlib.Path(runs_dir).glob("*/run.json")):
        d = json.loads(f.read_text())
        runs[(d["task"], d["condition"])] = d
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs")
    ap.add_argument("--out", default=str(pathlib.Path(__file__).resolve().parent.parent / "results" / "agent_runs.json"))
    a = ap.parse_args()
    runs = load(a.runs)
    tasks = sorted({t for t, _ in runs})
    table, pairs, dropped = [], [], []
    for t in tasks:
        row = {"task": t}
        for c in ("A", "B"):
            d = runs.get((t, c))
            if d is None or d.get("failed"):
                row[c] = None
                continue
            row[c] = {k: d.get(k) for k in ("accepted", "escaped_defects", "false_pass", "correct_delivery",
                                           "promises_broken", "ended", "wall_minutes", "tokens_input",
                                           "tokens_output", "model_calls")}
            row[c]["submissions"] = len(d.get("submissions", []))
            row[c]["visible_pass_denied_by_gate"] = sum(
                1 for s in d.get("submissions", []) if c == "B" and s.get("visible") and all(s["visible"].values()) and not s.get("accepted"))
        table.append(row)
        if row["A"] and row["B"]:
            pairs.append((row["A"], row["B"]))
        else:
            dropped.append(t)

    def total(c, k):
        return sum(int(r[c][k]) for r in table if r[c])

    def med(c, k):
        v = [r[c][k] for r in table if r[c] and r[c][k] is not None]
        return statistics.median(v) if v else None

    summary = {"tasks": len(tasks), "paired_tasks": len(pairs), "dropped_tasks": dropped}
    for c in ("A", "B"):
        n = sum(1 for r in table if r[c])
        summary[c] = {"runs": n, "accepted": total(c, "accepted"), "false_pass": total(c, "false_pass"),
                      "correct_delivery": total(c, "correct_delivery"), "escaped_defects": total(c, "escaped_defects"),
                      "median_submissions": med(c, "submissions"), "median_wall_minutes": med(c, "wall_minutes"),
                      "median_tokens_input": med(c, "tokens_input"), "median_tokens_output": med(c, "tokens_output"),
                      "ended": {e: sum(1 for r in table if r[c] and r[c]["ended"] == e)
                                for e in sorted({r[c]["ended"] for r in table if r[c]})}}
    summary["B"]["visible_pass_denied_by_gate"] = total("B", "visible_pass_denied_by_gate")

    tests = {}
    for k in ("false_pass", "correct_delivery"):
        b_only, a_only, p = mcnemar_exact([(bool(x[k]), bool(y[k])) for x, y in pairs])
        tests[k] = {"test": "exact McNemar", "A_only": a_only, "B_only": b_only, "p_two_sided": round(p, 4)}
    diffs = [y["escaped_defects"] - x["escaped_defects"] for x, y in pairs]
    nz = [d for d in diffs if d != 0]
    w = {"test": "Wilcoxon signed-rank, B minus A, zero_method=wilcox, method=auto",
         "n_pairs": len(diffs), "n_nonzero": len(nz), "median_difference": statistics.median(diffs) if diffs else None}
    if wilcoxon is None:
        w["note"] = "scipy not available; rerun on a machine with scipy"
    elif nz:
        r = wilcoxon(diffs, zero_method="wilcox", alternative="two-sided", method="auto")
        w.update({"statistic": float(r.statistic), "p_two_sided": round(float(r.pvalue), 4)})
    else:
        w["note"] = "all paired differences are zero"
    tests["escaped_defects"] = w

    report = {"summary": summary, "tests": tests, "table": table}
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps({"summary": summary, "tests": tests}, indent=1))


if __name__ == "__main__":
    main()
