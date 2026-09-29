"""X9 (C3): errors come by row position, lowest first, and within a row in schema order.

Only the order is judged here, so that a mistake in what is reported is charged to the promise it breaks.
"""

import json
import random

from _audit import answer, request_text
from _cmd import finish
from _oracle import gen_rows, gen_schema

problems = []
tables = 0


def in_order(label, schema, rows):
    """The reported errors must be sorted by (row, position of the field in the schema)."""
    global tables
    tables += 1
    body, problem = answer(request_text(schema, rows), nrows=len(rows))
    if problem:
        problems.append(f"{label}: {problem}")
        return
    place = {rule["name"]: i for i, rule in enumerate(schema)}
    placed = [err for err in body["errors"] if err["field"] in place]  # other fields have no schema place
    keys = [(err["row"], place[err["field"]]) for err in placed]
    for i in range(1, len(keys)):
        if keys[i] < keys[i - 1]:
            a, b = placed[i - 1], placed[i]
            problems.append(f"{label}: row {b['row']} field {b['field']!r} is listed after row {a['row']} field {a['field']!r}")
            return


# 1. Schema order is neither alphabetical nor the order of the keys in the rows.
schema = [
    {"name": "zeta", "type": "integer"},
    {"name": "alpha", "type": "string", "required": True},
    {"name": "mid", "type": "boolean"},
    {"name": "beta", "type": "number", "min": 0},
]
rows = [
    {"beta": -1, "mid": 1, "alpha": 2, "zeta": "z"},
    {"beta": 1},
    {"mid": "no", "zeta": 0.5, "beta": -0.5},
    {"alpha": "ok"},
    {"beta": "b", "alpha": None, "zeta": []},
]
in_order("schema order, not key or alphabetical order", schema, rows)

# 2. Duplicates and missing fields sit in their own row and schema place, not in a later pass.
schema = [
    {"name": "u", "type": "string", "unique": True},
    {"name": "v", "type": "integer"},
    {"name": "w", "type": "string", "unique": True},
    {"name": "x", "type": "boolean", "required": True},
]
rows = [
    {"x": True, "w": "s", "u": "p"},
    {"w": "s", "v": "bad", "u": "p"},
    {"x": False, "v": "bad", "u": "q"},
    {"x": True, "w": "t", "v": 1.5},
    {"w": "t", "u": "q"},
]
in_order("duplicates and missing in place", schema, rows)

# 3. Row positions beyond 9 sort as numbers, not as text.
schema = [{"name": "n", "type": "integer", "max": 0}, {"name": "m", "type": "string", "required": True}]
rows = [{"n": 1 if i in (2, 10, 11, 19, 20, 100) else 0, "m": "k"} for i in range(101)]
rows[3] = {"n": 0}
rows[99] = {"n": 5}
in_order("rows 2 to 100", schema, rows)

# 4. Seeded generated tables with row keys in shuffled order.
rng = random.Random(6_602_117)
for case in range(40):
    schema = gen_schema(rng, width=rng.randint(3, 6))
    rows = gen_rows(rng, schema, count=rng.randint(4, 20))
    in_order(f"generated table {case}", schema, rows)
    if len(problems) > 6:
        break

finish(problems, f"order ok: {tables} tables")
