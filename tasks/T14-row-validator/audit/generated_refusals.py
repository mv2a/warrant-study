"""X16 (C4): seeded random well-formed requests, each broken in one way that C4 names, are all refused."""

import copy
import json
import random

from _audit import answer, refused, request_text
from _cmd import finish
from _oracle import POOLS, gen_rows, gen_schema

WRONG_FOR = {  # values that are not of the field's type (G2)
    "string": [1, 1.5, True, None, ["a"], {"a": 1}],
    "integer": [1.5, "1", True, False, None, [1]],
    "number": ["1", True, None, [1], {"n": 1}],
    "boolean": [1, 0, "true", None, [True]],
}
NOT_BOOL = [1, 0, "true", "false", None, [], 1.0]
NOT_NUMBER = ["1", True, False, None, [0], {"v": 0}]
UNKNOWN_TYPES = ["date", "Integer", "int", "float", "str", "bool", "", "STRING", "array", "object", None, 3]
UNKNOWN_KEYS = ["pattern", "default", "Required", "label", "maxLength", "min_value", "enum", "Name"]


def mutate(rng, schema, rows):
    """Return (description, request text) for one C4 violation."""
    schema = copy.deepcopy(schema)
    rule = rng.choice(schema)
    kind = rng.randrange(17)
    if kind == 0:
        return "extra top-level key", json.dumps({"schema": schema, "rows": rows, rng.choice(["meta", "Rows", "x"]): 1})
    if kind == 1:
        body = {"schema": schema, "rows": rows}
        body.pop(rng.choice(["schema", "rows"]))
        return "missing top-level key", json.dumps(body)
    if kind == 2:
        return "schema not a non-empty list", json.dumps({"schema": rng.choice([[], {}, "s", None, schema[0]]), "rows": rows})
    if kind == 3:
        schema.insert(rng.randrange(len(schema) + 1), rng.choice([None, 0, "k", [], {}]))
        return "schema entry not a field rule", request_text(schema, rows)
    if kind == 4:
        choice = rng.choice([..., "", None, 5])
        if choice is ...:
            del rule["name"]
        else:
            rule["name"] = choice
        return f"bad name {choice!r}", request_text(schema, rows)
    if kind == 5:
        twin = {"name": rule["name"], "type": rng.choice(["string", "integer", "number", "boolean"])}
        schema.insert(rng.randrange(len(schema) + 1), twin)
        return "repeated name", request_text(schema, rows)
    if kind == 6:
        choice = rng.choice(UNKNOWN_TYPES + [...])
        if choice is ...:
            del rule["type"]
        else:
            rule["type"] = choice
        return f"bad type {choice!r}", request_text(schema, rows)
    if kind == 7:
        rule[rng.choice(UNKNOWN_KEYS)] = rng.choice([1, "x", None, True])
        return "unknown rule key", request_text(schema, rows)
    if kind == 8:
        rule[rng.choice(["required", "unique"])] = rng.choice(NOT_BOOL)
        return "required or unique not true or false", request_text(schema, rows)
    if kind == 9:
        rule["type"] = rng.choice(["integer", "number"])
        rule.pop("allowed", None)
        rule[rng.choice(["min", "max"])] = rng.choice(NOT_NUMBER)
        return "min or max not a number", request_text(schema, rows)
    if kind == 10:
        rule["type"] = rng.choice(["string", "boolean"])
        rule.pop("allowed", None)
        rule[rng.choice(["min", "max"])] = rng.choice([0, 1, -2.5, 10])
        return "min or max on a string or boolean field", request_text(schema, rows)
    if kind == 11:
        rule["type"] = rng.choice(["integer", "number"])
        rule.pop("allowed", None)
        low = rng.choice([-3, 0, 1, 2.5, 7])
        rule["min"], rule["max"] = low, low - rng.choice([1, 0.5, 0.001])
        return "min above max", request_text(schema, rows)
    if kind == 12:
        rule["allowed"] = rng.choice([[], "a", 1, None, {"a": 1}])
        return "allowed not a non-empty list", request_text(schema, rows)
    if kind == 13:
        good = rng.sample(POOLS[rule["type"]], rng.randint(0, 2))
        good.insert(rng.randrange(len(good) + 1), rng.choice(WRONG_FOR[rule["type"]]))
        rule["allowed"] = good
        return f"allowed entry of the wrong type for {rule['type']}", request_text(schema, rows)
    if kind == 14:
        return "rows not a list", json.dumps({"schema": schema, "rows": rng.choice([{}, "r", 0, None, True])})
    if kind == 15:
        rows = list(rows)
        rows.insert(rng.randrange(len(rows) + 1), rng.choice([None, 1, "row", [], [{}], False]))
        return "a row that is not an object", request_text(schema, rows)
    text = request_text(schema, rows)
    cut = rng.randrange(1, len(text) - 1)
    return "text that is not JSON", rng.choice([text[:cut], text + "}", text + text, "x" + text])


problems = []
rng = random.Random(2_718_281)
accepted = refusals = 0
for case in range(110):
    schema = gen_schema(rng)
    rows = gen_rows(rng, schema, count=rng.randint(1, 6))
    if case % 10 == 0:
        # The unbroken request must be accepted, so the refusals below are about the one change made.
        body, problem = answer(request_text(schema, rows), nrows=len(rows))
        accepted += 1
        if problem:
            problems.append(f"case {case}: the unbroken request was not accepted: {problem}")
    label, text = mutate(rng, schema, rows)
    refused(problems, f"case {case} ({label})", text)
    refusals += 1
    if len(problems) > 10:
        break

finish(problems, f"generated refusals ok: {refusals} broken requests refused, {accepted} unbroken ones accepted")
