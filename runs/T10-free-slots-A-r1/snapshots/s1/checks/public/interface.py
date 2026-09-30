"""P1: `slots` follows the interface in C5."""

from _cmd import call, finish

VALID = [
    {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660]], [[700, 760]]]},
    {"workday": [0, 1440], "min_length": 1, "quorum": 1, "busy": [[]]},
]
problems = []

for request in VALID:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != {"slots"}:
        problems.append(f"{request}: expected an object whose only field is slots, got {body!r}")
    elif not isinstance(body["slots"], list) or not all(
        isinstance(slot, list) and len(slot) == 2 and all(type(t) is int for t in slot) for slot in body["slots"]
    ):
        problems.append(f"{request}: slots must be a list of [start, end] pairs of whole numbers, got {body['slots']!r}")

status, body = call({"workday": [540, 1020], "min_length": 30, "quorum": 1})
if status != 2 or body is not None:
    problems.append(f"a request with no busy field must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, f"interface ok: {len(VALID) + 1} requests")
