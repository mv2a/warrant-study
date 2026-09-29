"""C3: every kind of malformed request in the intent is refused as a whole: exit status 2 and
nothing on standard output (so no group is seated). Each case changes one thing in an
otherwise valid request; accepted.py checks that the valid neighbours are handled."""

import json

from _audit import raw_all
from _cmd import finish

BASE = {"rows": [5, 5], "blocked": ["A1"], "groups": [{"id": "Ames", "size": 2}, {"id": "Bryce", "size": 3, "may_split": True}]}


def text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def with_top(**changes):
    return {**BASE, **changes}


def without(key):
    return {k: v for k, v in BASE.items() if k != key}


def with_group(index=0, drop=None, **changes):
    groups = [dict(g) for g in BASE["groups"]]
    groups[index].update(changes)
    if drop:
        del groups[index][drop]
    return {**BASE, "groups": groups}


def raw_group(fragment):
    """BASE with the first group's size written as raw JSON text (for 2.0, 1e1 and so on)."""
    return '{"rows": [5, 5], "blocked": ["A1"], "groups": [{"id": "Ames", "size": %s}]}' % fragment


def raw_rows(fragment):
    return '{"rows": [%s], "groups": [{"id": "Ames", "size": 1}]}' % fragment


def raw_split(fragment):
    return '{"rows": [5], "groups": [{"id": "Ames", "size": 1, "may_split": %s}]}' % fragment


CASES = [
    # standard input is not JSON, or not a JSON object
    ("empty input", ""),
    ("only whitespace", "  \n\t "),
    ("plain words", "rows 5 5, Ames 2"),
    ("unclosed object", '{"rows": [5, 5], "groups": []'),
    ("trailing comma", '{"rows": [5, 5], "groups": [],}'),
    ("single quotes", "{'rows': [5, 5], 'groups': []}"),
    ("two objects", '{"rows": [5], "groups": []} {"rows": [5], "groups": []}'),
    ("object then junk", '{"rows": [5], "groups": []} ok'),
    ("a list", "[]"),
    ("a list holding the request", json.dumps([{"rows": [5], "groups": []}])),
    ("null", "null"),
    ("a number", "12"),
    ("true", "true"),
    ("a string holding the request", json.dumps(json.dumps({"rows": [5], "groups": []}))),
    # rows
    ("rows missing", without("rows")),
    ("rows null", with_top(rows=None)),
    ("rows a number", with_top(rows=5)),
    ("rows a string", with_top(rows="5,5")),
    ("rows an object", with_top(rows={"A": 5, "B": 5})),
    ("rows empty", with_top(rows=[])),
    ("27 rows", {"rows": [1] * 27, "groups": []}),
    ("27 full rows", {"rows": [50] * 27, "groups": [{"id": "Ames", "size": 1}]}),
    ("row of 0", with_top(rows=[5, 0])),
    ("row of 51", with_top(rows=[51, 5])),
    ("row of -3", with_top(rows=[5, -3])),
    ("row of 1000", {"rows": [1000], "groups": []}),
    ("row true", with_top(rows=[5, True])),
    ("row false", with_top(rows=[False, 5])),
    ("row null", with_top(rows=[5, None])),
    ("row as text", with_top(rows=["5", 5])),
    ("row as list", with_top(rows=[[5], 5])),
    ("row 5.0", raw_rows("5.0")),
    ("row 1e1", raw_rows("1e1")),
    ("row 5E0", raw_rows("5E0")),
    ("row 50.0", raw_rows("50.0")),
    ("row 2.5", raw_rows("2.5")),
    ("row 1.0", raw_rows("1.0")),
    ("row -0", raw_rows("-0")),
    # groups
    ("groups missing", without("groups")),
    ("groups null", with_top(groups=None)),
    ("groups an object", with_top(groups={"id": "Ames", "size": 2})),
    ("groups a string", with_top(groups="Ames")),
    ("groups a number", with_top(groups=2)),
    ("groups true", with_top(groups=True)),
    ("group null", with_top(groups=[None])),
    ("group a string", with_top(groups=["Ames"])),
    ("group a list", with_top(groups=[["Ames", 2]])),
    ("group a number", with_top(groups=[{"id": "Ames", "size": 2}, 3])),
    ("id missing", with_group(0, drop="id")),
    ("id null", with_group(0, id=None)),
    ("id a number", with_group(0, id=7)),
    ("id true", with_group(0, id=True)),
    ("id a list", with_group(0, id=["Ames"])),
    ("id an object", with_group(1, id={"name": "Bryce"})),
    ("id empty", with_group(1, id="")),
    ("id repeated", with_group(1, id="Ames")),
    ("id repeated later", with_top(groups=[{"id": "Cy", "size": 1}, {"id": "Di", "size": 1}, {"id": "Cy", "size": 2}])),
    ("size missing", with_group(0, drop="size")),
    ("size null", with_group(0, size=None)),
    ("size 0", with_group(1, size=0)),
    ("size -2", with_group(0, size=-2)),
    ("size as text", with_group(0, size="2")),
    ("size true", with_group(0, size=True)),
    ("size false", with_group(0, size=False)),
    ("size a list", with_group(0, size=[2])),
    ("size 1.5", with_group(0, size=1.5)),
    ("size 2.0", raw_group("2.0")),
    ("size 1.0", raw_group("1.0")),
    ("size 2e0", raw_group("2e0")),
    ("size 1E1", raw_group("1E1")),
    ("size 20e-1", raw_group("20e-1")),
    ("size 1e400", raw_group("1e400")),
    ("may_split null", with_group(1, may_split=None)),
    ("may_split 1", raw_split("1")),
    ("may_split 0", raw_split("0")),
    ("may_split 1.0", raw_split("1.0")),
    ("may_split as text", with_group(1, may_split="true")),
    ("may_split false as text", with_group(1, may_split="false")),
    ("may_split a list", with_group(1, may_split=[])),
    ("may_split an object", with_group(1, may_split={})),
    ("bad group after good ones", with_top(groups=BASE["groups"] + [{"id": "Cole", "size": 0}])),
    # blocked
    ("blocked null", with_top(blocked=None)),
    ("blocked a string", with_top(blocked="A1")),
    ("blocked an object", with_top(blocked={"A1": True})),
    ("blocked a number", with_top(blocked=1)),
    ("blocked true", with_top(blocked=True)),
    ("seat lower case", with_top(blocked=["a1"])),
    ("seat leading zero", with_top(blocked=["A01"])),
    ("seat B07", with_top(blocked=["B07"])),
    ("seat with a space", with_top(blocked=["A 1"])),
    ("seat with leading space", with_top(blocked=[" A1"])),
    ("seat with trailing space", with_top(blocked=["A1 "])),
    ("seat with newline", with_top(blocked=["A1\n"])),
    ("seat number 0", with_top(blocked=["A0"])),
    ("seat past the row end", with_top(blocked=["A6"])),
    ("seat in a missing row", with_top(blocked=["C1"])),
    ("seat letter only", with_top(blocked=["A"])),
    ("seat number only", with_top(blocked=["1"])),
    ("seat empty", with_top(blocked=[""])),
    ("seat two letters", with_top(blocked=["AA1"])),
    ("seat letter after number", with_top(blocked=["A1A"])),
    ("seat reversed", with_top(blocked=["1A"])),
    ("seat minus sign", with_top(blocked=["A-1"])),
    ("seat plus sign", with_top(blocked=["A+1"])),
    ("seat decimal", with_top(blocked=["A1.0"])),
    ("seat arabic-indic digit", with_top(blocked=["A١"])),
    ("seat full-width digit", with_top(blocked=["A１"])),
    ("seat full-width letter", with_top(blocked=["Ａ1"])),
    ("seat superscript digit", with_top(blocked=["A¹"])),
    ("seat a number", with_top(blocked=[7])),
    ("seat null", with_top(blocked=[None])),
    ("seat a list", with_top(blocked=[["A1"]])),
    ("seat an object", with_top(blocked=[{"seat": "A1"}])),
    ("seat twice", with_top(blocked=["A1", "A1"])),
    ("seat twice, apart", with_top(blocked=["B2", "A1", "B2"])),
    ("seat past a short row", {"rows": [5, 3], "blocked": ["B4"], "groups": []}),
    ("seat A1_0", {"rows": [12], "blocked": ["A1_0"], "groups": []}),
    ("seat Z1 with 25 rows", {"rows": [4] * 25, "blocked": ["Z1"], "groups": []}),
    ("seat A51", {"rows": [50], "blocked": ["A51"], "groups": []}),
]

texts = [text(value) for _, value in CASES]
problems = []
for (label, _), sent, (status, out) in zip(CASES, texts, raw_all(texts)):
    if status != 2 or out != "":
        problems.append(f"{label}: expected status 2 and no output, got {status} and {out[:70]!r} | sent {sent[:90]!r}")

finish(problems, f"malformed requests refused: {len(CASES)}")
