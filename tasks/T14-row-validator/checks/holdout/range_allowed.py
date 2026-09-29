"""H3: inclusive min and max bounds, and exact `allowed` matching (G3)."""

import json
import random

from _cmd import call, finish


def same(got, expected):
    """Equal as collections of errors: this check is not about their order (C3 is)."""
    key = lambda x: json.dumps(x, sort_keys=True)
    return isinstance(got, list) and sorted(map(key, got)) == sorted(map(key, expected))

problems = []


def run(label, schema, cases):
    """cases: list of (field, value, expect_code or None); one field per row."""
    rows = [{field: value} for field, value, _ in cases]
    expected = [{"row": i, "field": f, "code": c} for i, (f, _, c) in enumerate(cases) if c]
    status, body = call({"schema": schema, "rows": rows})
    if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
        got = body.get("errors") if isinstance(body, dict) else None
        if isinstance(got, list):
            flagged = {(x.get("row"), x.get("code")) for x in got if isinstance(x, dict)}
            wrong = [f"{f}={v!r}" for i, (f, v, c) in enumerate(cases) if ((i, c) in flagged) != bool(c) or
                     any(r == i and cc != c for r, cc in flagged)]
            problems.append(f"{label}: judged wrongly: {', '.join(wrong[:8]) or '(order or shape differs)'}")
        else:
            problems.append(f"{label}: expected {expected}, got status {status} and {body!r}")


RANGES = [
    {"name": "i", "type": "integer", "min": -3, "max": 7},
    {"name": "n", "type": "number", "min": 0.5, "max": 2.25},
    {"name": "lo", "type": "integer", "min": 10},
    {"name": "hi", "type": "number", "max": -1.5},
    {"name": "eq", "type": "integer", "min": 4, "max": 4},
    {"name": "w", "type": "number", "min": -1, "max": 1000000},
]
R = "range"
run("bounds", RANGES, [
    ("i", -3, None), ("i", 7, None), ("i", 0, None), ("i", -4, R), ("i", 8, R), ("i", -100, R), ("i", 10**15, R),
    ("n", 0.5, None), ("n", 2.25, None), ("n", 1, None), ("n", 0.49999, R), ("n", 2.2500001, R), ("n", 0, R),
    ("n", 3, R), ("n", 2, None), ("n", 2.0, None), ("n", 3.0, R),
    ("lo", 10, None), ("lo", 9, R), ("lo", 10**12, None), ("lo", -10, R),
    ("hi", -1.5, None), ("hi", -1.4, R), ("hi", -1000, None), ("hi", 0, R),
    ("eq", 4, None), ("eq", 3, R), ("eq", 5, R),
    ("w", -1, None), ("w", 1000000, None), ("w", 1000000.0, None), ("w", 1000000.5, R), ("w", -1.0001, R),
])

# Whole numbers too large for a float to hold exactly: bounds are compared by exact value, so one past
# a bound is out of range even where a float would round it onto the bound.
BIG = [
    {"name": "b", "type": "integer", "min": 2**55 + 1, "max": 2**62 - 1},
    {"name": "c", "type": "number", "min": -(2**53), "max": 10**20},
]
run("bounds beyond float precision", BIG, [
    ("b", 2**55 + 1, None), ("b", 2**55, R), ("b", 2**62 - 1, None), ("b", 2**62, R), ("b", 2**58, None),
    ("b", 2**62 - 2, None),
    ("c", -(2**53), None), ("c", -(2**53) - 1, R), ("c", 10**20, None), ("c", 10**20 + 1, R), ("c", -(10**20), R),
    ("c", 0, None),
])

A = "allowed"
ALLOWED = [
    {"name": "s", "type": "string", "allowed": ["red", "green", "Blue"]},
    {"name": "k", "type": "integer", "allowed": [1, 2, 3]},
    {"name": "x", "type": "number", "allowed": [0.5, 2]},
    {"name": "b", "type": "boolean", "allowed": [True]},
    {"name": "z", "type": "number", "allowed": [0]},
    # One entry with a composed accent, one with a base letter plus a combining accent: never normalized.
    {"name": "u", "type": "string", "allowed": ["über", "café"]},
]
run("allowed values", ALLOWED, [
    ("s", "red", None), ("s", "Red", A), ("s", "Blue", None), ("s", "blue", A), ("s", " red", A), ("s", "red ", A),
    ("s", "", A), ("s", "green", None), ("s", "GREEN", A), ("s", "redgreen", A), ("s", "re", A),
    ("k", 2, None), ("k", 4, A), ("k", 0, A), ("k", 3, None), ("k", -1, A),
    ("x", 0.5, None), ("x", 2.0, None), ("x", 2, None), ("x", 0.25, A), ("x", 1, A),
    ("b", True, None), ("b", False, A),
    ("z", 0, None), ("z", 0.0, None), ("z", -0.0, None), ("z", 1, A),
    ("u", "über", None), ("u", "über", A), ("u", "café", None), ("u", "café", A), ("u", "uber", A),
])

# Generated bounds and values, fixed seed.
rng = random.Random(1403)
for n in range(6):
    lo = rng.randint(-50, 50)
    hi = lo + rng.randint(0, 30)
    cases = []
    for _ in range(60):
        v = rng.choice([lo, hi, lo - 1, hi + 1, rng.randint(lo - 8, hi + 8)])
        cases.append(("g", v, None if lo <= v <= hi else R))
    run(f"generated integer bounds [{lo}, {hi}] (seed 1403, set {n})", [{"name": "g", "type": "integer", "min": lo, "max": hi}], cases)
for n in range(4):
    lo = rng.randint(-400, 400) / 8
    hi = lo + rng.randint(0, 200) / 8
    cases = []
    for _ in range(60):
        v = rng.choice([lo, hi, lo - 0.125, hi + 0.125, rng.randint(int(lo * 8) - 40, int(hi * 8) + 40) / 8])
        cases.append(("g", v, None if lo <= v <= hi else R))
    run(f"generated number bounds [{lo}, {hi}] (seed 1403, set {n})", [{"name": "g", "type": "number", "min": lo, "max": hi}], cases)
for n in range(4):
    words = ["ok", "hold", "done", "open", "late"]
    allowed = rng.sample(words, 2)
    cases = []
    for _ in range(50):
        w = rng.choice(words)
        v = rng.choice([w, w.upper(), w.capitalize(), w + " ", " " + w, w])
        cases.append(("t", v, None if v in allowed else A))
    run(f"generated allowed {allowed} (seed 1403, set {n})", [{"name": "t", "type": "string", "allowed": allowed}], cases)

finish(problems, "range and allowed ok: 33 bounds cases, 12 big-integer bounds cases, 32 allowed cases, 14 generated sets")
