"""H7 (C4): invalid requests are refused (status 2, nothing on standard output); valid edge cases are answered."""

import json

from _cmd import call, finish

GOOD = {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660]], []]}


def variant(**changes):
    request = dict(GOOD)
    for field, value in changes.items():
        if value is ...:
            request.pop(field)
        else:
            request[field] = value
    return json.dumps(request)


INVALID = [
    ("text that isn't JSON", "free at ten?"),
    ("an empty input", ""),
    ("a list instead of an object", "[[540, 1020], 30, []]"),
    ("a number instead of an object", "42"),
    ("two JSON objects", json.dumps(GOOD) + json.dumps(GOOD)),
    ("a missing workday", variant(workday=...)),
    ("a missing min_length", variant(min_length=...)),
    ("a missing quorum", variant(quorum=...)),
    ("a missing busy", variant(busy=...)),
    ("a workday of one number", variant(workday=[540])),
    ("a workday of three numbers", variant(workday=[540, 600, 1020])),
    ("a workday that isn't a list", variant(workday="09:00-17:00")),
    ("a reversed workday", variant(workday=[1020, 540])),
    ("an empty workday", variant(workday=[600, 600])),
    ("a workday starting before midnight", variant(workday=[-10, 600])),
    ("a workday ending after midnight", variant(workday=[540, 1441])),
    ("a workday with a fractional minute", variant(workday=[540.5, 1020])),
    ("a workday written with decimal points", variant(workday=[540.0, 1020.0])),
    ("a workday written as text", variant(workday=["540", "1020"])),
    ("a workday of true and false", variant(workday=[False, True])),
    ("a min_length of zero", variant(min_length=0)),
    ("a negative min_length", variant(min_length=-30)),
    ("a fractional min_length", variant(min_length=30.5)),
    ("a min_length written with a decimal point", variant(min_length=30.0)),
    ("a min_length written as text", variant(min_length="30")),
    ("a min_length of true", variant(min_length=True)),
    ("a min_length of null", variant(min_length=None)),
    ("a quorum of zero", variant(quorum=0)),
    ("a negative quorum", variant(quorum=-1)),
    ("a quorum larger than the group", variant(quorum=3)),
    ("a quorum larger than a one-person group", variant(quorum=2, busy=[[[600, 660]]])),
    ("a fractional quorum", variant(quorum=1.5)),
    ("a quorum written with a decimal point", variant(quorum=2.0)),
    ("a quorum written as text", variant(quorum="2")),
    ("a quorum of true", variant(quorum=True)),
    ("a quorum of null", variant(quorum=None)),
    ("a quorum given as a list of names", variant(quorum=["ana", "bo"])),
    ("a busy of no people", variant(quorum=1, busy=[])),
    ("a busy that isn't a list", variant(busy={"ana": [[600, 660]]})),
    ("a busy that is a flat list of intervals", variant(busy=[[600, 660], [700, 760]])),
    ("a person's entry that isn't a list", variant(busy=[[[600, 660]], None])),
    ("a person's entry that is a single interval object", variant(quorum=1, busy=[{"start": 600, "end": 660}])),
    ("a reversed busy interval", variant(busy=[[[660, 600]], []])),
    ("an empty busy interval", variant(busy=[[[600, 600]], []])),
    ("a busy interval ending after midnight", variant(busy=[[[1400, 1500]], []])),
    ("a busy interval starting before midnight", variant(busy=[[[-30, 600]], []])),
    ("a busy interval of one number", variant(busy=[[[600]], []])),
    ("a busy interval of three numbers", variant(busy=[[[600, 630, 660]], []])),
    ("a busy interval with a fractional minute", variant(busy=[[[600, 660.5]], []])),
    ("a busy interval written with decimal points", variant(busy=[[[600.0, 660.0]], []])),
    ("a busy interval written as text", variant(busy=[[["10:00", "11:00"]], []])),
    ("a busy interval of true and false", variant(busy=[[[False, True]], []])),
    ("a bad interval after good ones", variant(busy=[[[600, 660]], [[700, 760], [800, 790]]])),
]
VALID = [
    ("working hours from midnight to midnight", {"workday": [0, 1440], "min_length": 1, "quorum": 1, "busy": [[]]}, [[0, 1440]]),
    ("a one-minute working day", {"workday": [0, 1], "min_length": 1, "quorum": 1, "busy": [[]]}, [[0, 1]]),
    ("a meeting at the first and last minutes", {"workday": [0, 1440], "min_length": 1, "quorum": 2, "busy": [[[0, 1]], [[1439, 1440]]]}, [[1, 1439]]),
    ("a min_length longer than the day", {"workday": [540, 1020], "min_length": 100000, "quorum": 1, "busy": [[]]}, []),
    ("people with empty calendars", {"workday": [540, 1020], "min_length": 30, "quorum": 3, "busy": [[], [], []]}, [[540, 1020]]),
    ("meetings entirely outside the working hours", {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[0, 60]], [[1380, 1440]]]}, [[540, 1020]]),
    ("a quorum of one", {"workday": [540, 1020], "min_length": 30, "quorum": 1, "busy": [[[600, 660]], [[630, 700]]]}, [[540, 630], [660, 1020]]),
    ("a quorum of the whole group, people with empty calendars included", {"workday": [540, 1020], "min_length": 30, "quorum": 4, "busy": [[], [[600, 660]], [], []]}, [[540, 600], [660, 1020]]),
]

problems = []
for label, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for label, request, expected in VALID:
    status, body = call(request)
    slots = body.get("slots") if isinstance(body, dict) else None
    if status != 0 or slots != expected:
        problems.append(f"{label} is valid: expected slots {expected}, got {body!r} (status {status})")

finish(problems, f"refusals ok: {len(INVALID)} invalid and {len(VALID)} valid requests")
