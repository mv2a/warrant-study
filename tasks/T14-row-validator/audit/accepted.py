"""X11 (C4): requests that sit just inside the rules of C4 are validated, not refused, and bad row values are never refused."""

import json

from _audit import e, expect, request_text
from _cmd import finish

problems = []
count = 0


def accepted(label, schema, rows, errors, text=None):
    global count
    count += 1
    expect(problems, label, text if text is not None else request_text(schema, rows), errors, nrows=len(rows))


INT = {"name": "n", "type": "integer"}

# Near misses on the schema.
accepted("no rows", [INT], [], [])
accepted("min equal to max", [{**INT, "min": 3, "max": 3}], [{"n": 3}, {"n": 4}], [e(1, "n", "range")])
accepted("min 3 and max 3.0", [{**INT, "min": 3, "max": 3.0}], [{"n": 3.0}], [])
accepted("fractional min on an integer field", [{**INT, "min": 0.5}], [{"n": 0}, {"n": 1}], [e(0, "n", "range")])
accepted("negative and zero bounds", [{**INT, "min": -5, "max": 0}], [{"n": -5}, {"n": 0}, {"n": 1}], [e(2, "n", "range")])
accepted("only min", [{"name": "x", "type": "number", "min": -1.5}], [{"x": -2}], [e(0, "x", "range")])
accepted("only max", [{"name": "x", "type": "number", "max": 1e300}], [{"x": 5}], [])
accepted("integer allowed list holding 2.0", [{**INT, "allowed": [1, 2.0]}], [{"n": 2}, {"n": 3}], [e(1, "n", "allowed")])
accepted("integer allowed list holding -0.0 and a big integer", [{**INT, "allowed": [-0.0, 10**20]}],
         [{"n": 0}, {"n": 10**20}], [])
accepted("allowed list with a repeated entry", [{"name": "s", "type": "string", "allowed": ["a", "a"]}],
         [{"s": "a"}, {"s": "b"}], [e(1, "s", "allowed")])
accepted("allowed list holding the empty string", [{"name": "s", "type": "string", "allowed": [""]}],
         [{"s": ""}, {"s": " "}], [e(1, "s", "allowed")])
accepted("boolean allowed list", [{"name": "b", "type": "boolean", "allowed": [True, False]}], [{"b": False}], [])
accepted("number allowed list mixing integers and fractions", [{"name": "x", "type": "number", "allowed": [1, 0.5]}],
         [{"x": 0.5}, {"x": 1.0}], [])
accepted("allowed entries outside the range", [{**INT, "min": 0, "max": 5, "allowed": [3, 50]}],
         [{"n": 50}], [e(0, "n", "range")])
accepted("required and unique written as false", [{"name": "s", "type": "string", "required": False, "unique": False}],
         [{}, {"s": "a"}, {"s": "a"}], [])
accepted("unique on a boolean field", [{"name": "b", "type": "boolean", "unique": True}],
         [{"b": True}, {"b": True}], [e(1, "b", "duplicate")])
accepted("names that differ only in case", [{"name": "id", "type": "string"}, {"name": "ID", "type": "integer"}],
         [{"id": 1, "ID": "x"}], [e(0, "id", "type"), e(0, "ID", "type")])
accepted("a name that is one space", [{"name": " ", "type": "integer", "required": True}], [{}], [e(0, " ", "missing")])
accepted("names that look like output keys", [{"name": "row", "type": "string"}, {"name": "code", "type": "integer"}],
         [{"row": 1, "code": "x"}], [e(0, "row", "type"), e(0, "code", "type")])
accepted("keys of a rule in an unusual order", [{"max": 9, "type": "integer", "name": "n", "min": 1}], [{"n": 10}],
         [e(0, "n", "range")])
accepted("a twelve-field schema", [{"name": f"f{i}", "type": "string", "required": True} for i in range(12)],
         [{}], [e(0, f"f{i}", "missing") for i in range(12)])

# Bad values inside rows are reported, never refused.
schema = [{"name": "s", "type": "string", "required": True}, {"name": "x", "type": "number", "min": 0, "max": 1}]
rows = [
    {"s": {"deep": {"deeper": [1, 2, {"x": None}]}}, "x": [[[]]]},
    {"s": [None, None], "x": {"": ""}},
    {"s": "fine", "x": 10**40, "": "empty key", "s ": 5},
    {},
    {"s": "\u0000\ud7ff\ue000 control and private-use", "x": -1e-300},
]
accepted("strange values in rows", schema, rows, [
    e(0, "s", "type"), e(0, "x", "type"), e(1, "s", "type"), e(1, "x", "type"), e(2, "x", "range"),
    e(3, "s", "missing"), e(4, "x", "range")])
accepted("an empty row object", schema, [{}, {}], [e(0, "s", "missing"), e(1, "s", "missing")])
wide = {f"k{i}": i for i in range(300)}
accepted("a row with 300 unknown keys", schema, [{**wide, "s": "ok"}], [])

# Formatting of a well-formed request does not matter.
schema = [{"name": "n", "type": "integer", "min": 1}]
text = '\n\t{ "rows" :\n [ { "n" : 0 } , {"n":1} ] ,\r\n "schema" : %s }\n  ' % json.dumps(schema)
accepted("rows before schema, with odd whitespace", schema, [{}, {}], [e(0, "n", "range")], text=text)
text = json.dumps({"schema": [{"name": "caf\u00e9", "type": "string"}], "rows": [{"caf\u00e9": 1}]}, ensure_ascii=False)
accepted("unescaped non-ASCII text", None, [{}], [e(0, "caf\u00e9", "type")], text=text)

finish(problems, f"accepted ok: {count} well-formed requests validated")
