"""X13-X16 (S1-S4): the scenarios written in the intent, exactly. Usage: scenarios.py S1|S2|S3|S4.
A success must be status 0 with exactly the stated object (sequence a JSON whole number);
the refusal must be status 2 with nothing at all on standard output."""

import sys

from _x import encode, finish, invoke, parse, show

SCENARIOS = {
    "S1": ({"branch": "lisbon", "year": 2026, "previous": "LIS-2026-00041"}, {"number": "LIS-2026-00042", "sequence": 42}),
    "S2": ({"branch": "porto", "year": 2027, "previous": "OPO-2026-01873"}, {"number": "OPO-2027-00001", "sequence": 1}),
    "S3": ({"branch": "faro", "year": 2026, "previous": None}, {"number": "FAO-2026-00001", "sequence": 1}),
    "S4": ({"branch": "braga", "year": 2026, "previous": "LIS-2026-00041"}, None),
}

scenario = sys.argv[1]
request, expected = SCENARIOS[scenario]
status, out = invoke(encode(request))
problems = []
if expected is None:
    if status != 2 or out != b"":
        problems.append(f"{scenario}: expected a refusal (status 2, nothing on stdout), got status {status} and {show(out)}")
else:
    body = parse(out)
    if status != 0 or body != expected or type((body or {}).get("sequence")) is not int:
        problems.append(f"{scenario}: expected {expected} with status 0, got {show(out)} (status {status})")

finish(problems, f"{scenario} ok")
