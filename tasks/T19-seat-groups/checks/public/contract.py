"""P1: `seats` follows the interface in C1 and refuses one malformed request."""

from _cmd import call, finish

REQUESTS = [
    {"rows": [4, 6], "groups": [{"id": "Adams", "size": 2}, {"id": "Baker", "size": 5}]},
    {"rows": [3], "blocked": ["A2"], "groups": [{"id": "Cole", "size": 2, "may_split": False}]},
]
problems = []

for request in REQUESTS:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
        continue
    if not isinstance(body, dict) or set(body) != {"seated", "refused", "free"}:
        problems.append(f"{request}: expected an object with exactly seated, refused and free, got {body!r}")
        continue
    if type(body["free"]) is not int:
        problems.append(f"{request}: free must be a whole number, got {body['free']!r}")
    for entry in body["seated"] if isinstance(body["seated"], list) else [None]:
        if not isinstance(entry, dict) or set(entry) != {"id", "seats"} or not isinstance(entry["seats"], list):
            problems.append(f"{request}: each seated entry needs exactly id and a list of seats, got {entry!r}")
    for entry in body["refused"] if isinstance(body["refused"], list) else [None]:
        if not isinstance(entry, dict) or set(entry) != {"id", "reason"}:
            problems.append(f"{request}: each refused entry needs exactly id and reason, got {entry!r}")

status, body = call({"rows": [4], "groups": [{"id": "Dunn", "size": 0}]})
if status != 2 or body is not None:
    problems.append(f"a group of size 0 must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, f"contract ok: {len(REQUESTS) + 1} requests")
