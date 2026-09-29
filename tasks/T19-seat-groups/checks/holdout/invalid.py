"""H7: malformed requests are refused as a whole, and valid requests at the limits are accepted."""

import json

from _cmd import call, finish

OK_GROUPS = [{"id": "a", "size": 2}]


def req(**fields):
    request = {"rows": [4, 4], "groups": OK_GROUPS}
    request.update(fields)
    return json.dumps({k: v for k, v in request.items() if v is not ...})


def group(**fields):
    g = {"id": "a", "size": 2}
    g.update(fields)
    return req(groups=[{k: v for k, v in g.items() if v is not ...}])


INVALID = [
    ("text that isn't JSON", "row A please"),
    ("empty input", ""),
    ("a list instead of an object", '[[4, 4], [{"id": "a", "size": 2}]]'),
    ("a JSON string", '"rows"'),
    ("missing rows", req(rows=...)),
    ("rows that is not a list", req(rows=8)),
    ("rows that is null", req(rows=None)),
    ("no rows", req(rows=[])),
    ("27 rows", req(rows=[5] * 27)),
    ("a row of 0 seats", req(rows=[4, 0])),
    ("a row of 51 seats", req(rows=[51])),
    ("a negative row", req(rows=[-3])),
    ("a row of 3.0 seats", '{"rows": [4, 3.0], "groups": []}'),
    ("a row count in text", req(rows=[4, "4"])),
    ("a row count of true", req(rows=[4, True])),
    ("missing groups", req(groups=...)),
    ("groups that is an object", req(groups={"id": "a", "size": 2})),
    ("groups that is null", req(groups=None)),
    ("a group that is a list", req(groups=[["a", 2]])),
    ("a group that is null", req(groups=[None])),
    ("a group with no id", group(id=...)),
    ("a group id that is a number", group(id=7)),
    ("an empty group id", group(id="")),
    ("a repeated group id", req(groups=[{"id": "a", "size": 1}, {"id": "b", "size": 1}, {"id": "a", "size": 1}])),
    ("a group with no size", group(size=...)),
    ("a size of 0", group(size=0)),
    ("a negative size", group(size=-2)),
    ("a size of 2.5", group(size=2.5)),
    ("a size of 2.0", '{"rows": [4, 4], "groups": [{"id": "a", "size": 2.0}]}'),
    ("a size of 1e1", '{"rows": [4, 4], "groups": [{"id": "a", "size": 1e1}]}'),
    ("a size in text", group(size="2")),
    ("a size of true", group(size=True)),
    ("a size of null", group(size=None)),
    ('may_split "yes"', group(may_split="yes")),
    ("may_split 1", group(may_split=1)),
    ("may_split null", group(may_split=None)),
    ("blocked that is a single seat name", req(blocked="A1")),
    ("blocked that is null", req(blocked=None)),
    ("a blocked seat given as a number", req(blocked=[1])),
    ("a blocked seat in lower case", req(blocked=["a1"])),
    ("a blocked seat with a leading zero", req(blocked=["A01"])),
    ("a blocked seat with a space", req(blocked=["A 1"])),
    ("a blocked seat number 0", req(blocked=["A0"])),
    ("a blocked seat past the end of its row", req(blocked=["B5"])),
    ("a blocked seat in a row that does not exist", req(blocked=["C1"])),
    ("a blocked seat named twice", req(blocked=["A2", "B1", "A2"])),
    ("a blocked seat as a pair", req(blocked=[["A", 1]])),
    ("a valid request whose last group is malformed", req(groups=[{"id": "a", "size": 1}, {"id": "b", "size": "lots"}])),
    # Not JSON under RFC 8259, though Python's json module accepts these words by default.
    ("an ignored top-level field holding Infinity", '{"rows": [4, 4], "groups": [{"id": "a", "size": 2}], "price": Infinity}'),
    ("an ignored group field holding NaN", '{"rows": [4, 4], "groups": [{"id": "a", "size": 2, "rating": NaN}]}'),
    ("an ignored nested field holding -Infinity", '{"rows": [4, 4], "groups": [], "extra": {"floor": [1, -Infinity]}}'),
]
VALID = [
    ("26 rows of 50 seats", req(rows=[50] * 26, blocked=["Z50", "A1"])),
    ("a one-seat theatre", req(rows=[1], groups=[{"id": "a", "size": 1}])),
    ("no groups", req(groups=[])),
    ("an empty blocked list", req(blocked=[])),
    ("may_split false and true", req(groups=[{"id": "a", "size": 1, "may_split": False}, {"id": "b", "size": 1, "may_split": True}])),
    ("ids with spaces and symbols", req(groups=[{"id": " ", "size": 1}, {"id": "Smith & Jones (2)", "size": 1}])),
    ("a group of a million", req(groups=[{"id": "a", "size": 1000000}])),
    ("ids that differ only in case", req(groups=[{"id": "a", "size": 1}, {"id": "A", "size": 1}])),
]
problems = []
for label, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for label, raw in VALID:
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{label}: a valid request must be handled with status 0, got status {status} and {body!r}")

finish(problems, f"validation ok: {len(INVALID)} malformed and {len(VALID)} valid requests")
