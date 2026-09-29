"""H2: each type accepts exactly the JSON values G2 says it takes (G2)."""

import json
import random

from _cmd import call, finish


def same(got, expected):
    """Equal as collections of errors: this check is not about their order (C3 is)."""
    key = lambda x: json.dumps(x, sort_keys=True)
    return isinstance(got, list) and sorted(map(key, got)) == sorted(map(key, expected))

# Raw JSON literals, so forms like 4.0, -0.0 and 1e3 reach the command as written.
LITERALS = {
    '"hello"': {"string"}, '""': {"string"}, '"4"': {"string"}, '"true"': {"string"},
    '" "': {"string"},
    "true": {"boolean"}, "false": {"boolean"},
    "4": {"integer", "number"}, "0": {"integer", "number"}, "-17": {"integer", "number"},
    "4.0": {"integer", "number"}, "-0.0": {"integer", "number"}, "1e3": {"integer", "number"},
    "2.5E1": {"integer", "number"}, "12345678901234567890": {"integer", "number"},
    "4.5": {"number"}, "-0.25": {"number"}, "1e-3": {"number"}, "0.1": {"number"},
    "[]": set(), "[1]": set(), "{}": set(), '{"v": 1}': set(), '["a"]': set(),
}
problems = []

for kind in ("string", "integer", "number", "boolean"):
    literals = list(LITERALS)
    raw = ('{"schema": [{"name": "v", "type": "%s"}], "rows": [' % kind
           + ", ".join('{"v": %s}' % lit for lit in literals) + "]}")
    expected = [{"row": i, "field": "v", "code": "type"} for i, lit in enumerate(literals) if kind not in LITERALS[lit]]
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
        got = body.get("errors") if isinstance(body, dict) else body
        if isinstance(got, list):
            flagged = {x.get("row") for x in got if isinstance(x, dict)}
            wrongly = [literals[i] for i in range(len(literals)) if (i in flagged) != (kind not in LITERALS[literals[i]])]
            problems.append(f"{kind} field: these values were judged wrongly: {', '.join(wrongly) or '(order or shape differs)'}")
        else:
            problems.append(f"{kind} field: expected {len(expected)} type errors, got status {status} and {body!r}")

# Generated values, fixed seed, for all four types at once.
rng = random.Random(1402)


def generated():
    pick = rng.randrange(6)
    if pick == 0:
        return rng.randint(-10**6, 10**6), {"integer", "number"}
    if pick == 1:
        return float(rng.randint(-5000, 5000)), {"integer", "number"}
    if pick == 2:
        return rng.randint(-5000, 5000) + rng.choice([0.5, 0.25, 0.125, 0.75]), {"number"}
    if pick == 3:
        return rng.choice(["", "x", "12", "1.5", "false", "null"]), {"string"}
    if pick == 4:
        return rng.random() < 0.5, {"boolean"}
    return rng.choice([[], {}, [0], {"k": "v"}]), set()


SCHEMA = [{"name": k, "type": k} for k in ("string", "integer", "number", "boolean")]
rows, expected = [], []
for i in range(200):
    row = {}
    for rule in SCHEMA:
        value, takes = generated()
        row[rule["name"]] = value
        if rule["type"] not in takes:
            expected.append({"row": i, "field": rule["name"], "code": "type"})
    rows.append(row)
status, body = call(raw=json.dumps({"schema": SCHEMA, "rows": rows}))
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
    got = body.get("errors") if isinstance(body, dict) else body
    diff = ([x for x in got if x not in expected][:2] + [x for x in expected if x not in got][:2]) if isinstance(got, list) else got
    problems.append(f"200 generated rows (seed 1402): type errors differ, for example {diff!r}")

finish(problems, f"types ok: {len(LITERALS)} literals x 4 types, 200 generated rows")
