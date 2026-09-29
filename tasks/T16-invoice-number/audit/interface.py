"""X1 (C5): successes are one JSON object with exactly number (text) and sequence (whole
number), exit 0; refusals of every kind exit 2 and write nothing at all on stdout."""

from _x import encode, finish, invoke_all, parse, show

SUCCESSES = [
    {"branch": "braga", "year": 2044, "previous": None},
    {"branch": "faro", "year": 2000, "previous": None},
    {"branch": "porto", "year": 9999, "previous": "OPO-9999-00318"},
    {"branch": "lisbon", "year": 2058, "previous": "LIS-2057-77310"},
    {"branch": "faro", "year": 3121, "previous": "FAO-3121-99998"},
    {"branch": "braga", "year": 2029, "previous": "BRG-2029-00009"},
]

REFUSALS = [
    ("malformed previous", {"branch": "porto", "year": 2033, "previous": "OPO-2033-0077"}),
    ("another branch's number", {"branch": "faro", "year": 2033, "previous": "BRG-2033-00077"}),
    ("previous from a later year", {"branch": "lisbon", "year": 2033, "previous": "LIS-2034-00002"}),
    ("sequence 99999 in the same year", {"branch": "braga", "year": 2033, "previous": "BRG-2033-99999"}),
    ("unknown branch", {"branch": "setubal", "year": 2033, "previous": None}),
    ("year out of range", {"branch": "porto", "year": 1998, "previous": None}),
    ("year as text", {"branch": "porto", "year": "2033", "previous": None}),
    ("previous as a number", {"branch": "faro", "year": 2033, "previous": 77}),
    ("missing previous", {"branch": "faro", "year": 2033}),
    ("JSON array", [{"branch": "faro", "year": 2033, "previous": None}]),
]
RAW_REFUSALS = [
    ("empty stdin", b""),
    ("not JSON", b"branch=faro year=2033"),
    ("truncated JSON", b'{"branch": "faro", "year": 2033, "previous": null'),
]

problems = []
results = invoke_all([encode(r) for r in SUCCESSES])
for request, (status, out) in zip(SUCCESSES, results):
    body = parse(out)
    if status != 0:
        problems.append(f"{show(request)}: status {status}, expected 0")
    elif body is None:
        problems.append(f"{show(request)}: stdout is not one JSON object: {show(out)}")
    elif set(body) != {"number", "sequence"}:
        problems.append(f"{show(request)}: expected exactly the fields number and sequence, got {sorted(body)}")
    elif type(body["number"]) is not str or type(body["sequence"]) is not int:
        problems.append(f"{show(request)}: number must be text and sequence a whole number, got {show(body)}")

cases = [(label, encode(r)) for label, r in REFUSALS] + RAW_REFUSALS
results = invoke_all([payload for _, payload in cases])
for (label, _), (status, out) in zip(cases, results):
    if status != 2:
        problems.append(f"{label}: status {status}, expected 2")
    elif out != b"":
        problems.append(f"{label}: refused but wrote {show(out)} on stdout, expected nothing")

finish(problems, f"interface ok: {len(SUCCESSES)} successes, {len(cases)} silent refusals")
