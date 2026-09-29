"""C3 (and C1): valid requests at the edges of the rules are handled, not refused: exit
status 0 and a response that answers every group exactly once under its own id. These
are the valid neighbours of the malformed cases in malformed.py."""

import json

from _audit import answers, brief, call_all
from _cmd import finish


def one(gid="Ames", size=2, **extra):
    return {"id": gid, "size": size, **extra}


CASES = [
    ("one seat", {"rows": [1], "groups": [one(size=1)]}),
    ("one row of 50", {"rows": [50], "groups": [one(size=50)]}),
    ("26 rows of 1", {"rows": [1] * 26, "groups": [one(size=26, may_split=True)]}),
    ("26 rows of 50", {"rows": [50] * 26, "groups": [one(size=50), one("Bo", 1300)]}),
    ("mixed row lengths 1 and 50", {"rows": [1, 50, 1], "groups": [one(size=3)]}),
    ("no groups", {"rows": [5], "groups": []}),
    ("empty blocked list", {"rows": [5], "blocked": [], "groups": [one()]}),
    ("blocked Z50", {"rows": [50] * 26, "blocked": ["Z50"], "groups": [one()]}),
    ("blocked end of a short row", {"rows": [5, 3], "blocked": ["B3", "A5"], "groups": [one()]}),
    ("blocked two-digit seat", {"rows": [12], "blocked": ["A10", "A12", "A11"], "groups": [one()]}),
    ("every seat blocked", {"rows": [2, 2], "blocked": ["B2", "A1", "B1", "A2"], "groups": [one(size=1)]}),
    ("id of one space", {"rows": [5], "groups": [one(" ", 1)]}),
    ("ids differing only by case", {"rows": [5], "groups": [one("ames", 1), one("Ames", 1), one("AMES", 1)]}),
    ("ids differing by a trailing space", {"rows": [5], "groups": [one("Ames", 1), one("Ames ", 1)]}),
    ("id that looks like a seat", {"rows": [5], "groups": [one("A1", 1), one("0", 1), one("null", 1), one("true", 1)]}),
    ("long id", {"rows": [5], "groups": [one("x" * 300, 1)]}),
    ("non-ASCII ids", {"rows": [5], "groups": [one("Łucja", 1), one("李", 1), one("🎭", 1)]}),
    ("size 1", {"rows": [5], "groups": [one(size=1, may_split=False)]}),
    ("size 10**9", {"rows": [5], "groups": [one(size=10**9)]}),
    ("size 10**30 may split", {"rows": [5], "groups": [one(size=10**30, may_split=True)]}),
    ("may_split false", {"rows": [5], "groups": [one(may_split=False)]}),
    ("may_split true on one person", {"rows": [5], "groups": [one(size=1, may_split=True)]}),
    ("row of 50 and row of 1", {"rows": [50, 1], "groups": [one(size=51, may_split=True)]}),
    ("extra fields everywhere", {"rows": [5], "groups": [one(note=None, seats=["A9"], reason=1)], "price": 12.5, "blocked_extra": "a1"}),
    ("extra field holding 3.0 and 1e1", '{"rows": [5], "groups": [{"id": "Ames", "size": 2, "cost": 3.0}], "limit": 1e1}'),
    ("extra field holding huge exponent", '{"rows": [5], "groups": [], "x": 1e400}'),
    ("whitespace and newlines", '\n\n  {\n "groups" :\t[ { "size" : 2 , "id" : "Ames" } ] ,\n "rows" : [ 5 , 5 ]\n }  \n\n'),
    ("\\u escapes in id", '{"rows": [5], "groups": [{"id": "\\u00c5se", "size": 1}]}'),
    ("keys in unusual order", '{"groups": [{"may_split": true, "size": 2, "id": "Ames"}], "blocked": ["A2"], "rows": [3]}'),
]

texts = [value if isinstance(value, str) else json.dumps(value, ensure_ascii=False) for _, value in CASES]
problems = []
for (label, value), text, (status, body) in zip(CASES, texts, call_all(texts)):
    if status != 0:
        problems.append(f"{label}: valid request refused with status {status} | {text[:90]!r}")
        continue
    got = answers(body)
    ids = [g["id"] for g in json.loads(text)["groups"]]
    if got is None or sorted(got) != sorted(ids) or any(len(got[i]) != 1 for i in ids):
        problems.append(f"{label}: every group must be answered once, got {str(body)[:100]} | {brief(json.loads(text))}")

finish(problems, f"valid edge requests handled: {len(CASES)}")
