"""P1: `policy` follows the interface in C1, and refuses the S4 request and non-JSON text."""

from _cmd import call, finish

FIELDS = {"ok", "violations"}
problems = []

VALID = [
    {"password": "Harbor-Lamp-42", "username": "alice", "banned": []},
    {"password": "short", "username": "alice", "banned": []},
]
for request in VALID:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{request}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif type(body["ok"]) is not bool:
        problems.append(f"{request}: ok must be true or false, got {body['ok']!r}")
    elif not isinstance(body["violations"], list) or not all(isinstance(v, str) for v in body["violations"]):
        problems.append(f"{request}: violations must be a list of strings, got {body['violations']!r}")

REFUSED = [
    ("the S4 request (a username with a space)",
     '{"password": "Harbor-Lamp-42", "username": "ana smith", "banned": []}'),
    ("text that is not JSON", "Harbor-Lamp-42"),
]
for name, raw in REFUSED:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")

finish(problems, "interface ok: 2 valid requests, 2 refusals")
