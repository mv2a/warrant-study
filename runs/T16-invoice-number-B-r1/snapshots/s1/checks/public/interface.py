"""P1: `next` follows the interface in C5."""

from _cmd import call, finish

VALID = [
    {"branch": "porto", "year": 2031, "previous": None},
    {"branch": "lisbon", "year": 2026, "previous": "LIS-2026-00007"},
]
problems = []
for request in VALID:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != {"number", "sequence"}:
        problems.append(f"{request}: expected an object with exactly number and sequence, got {body!r}")
    elif type(body["number"]) is not str or type(body["sequence"]) is not int:
        problems.append(f"{request}: number must be text and sequence a whole number, got {body!r}")

status, _ = call({"branch": "coimbra", "year": 2026, "previous": None})
if status != 2:
    problems.append(f"the unknown branch coimbra must be refused with status 2, got status {status}")

finish(problems, "interface ok: 3 requests")
