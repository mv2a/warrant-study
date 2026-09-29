"""H6 (C1): the command's interface: status 0 and exactly {ok, violations} for every valid request,
status 2 and nothing on standard output for a refused one."""

import json
import random
import subprocess

from _cmd import PATH, call, finish
from _oracle import random_password, random_username

FIELDS = {"ok", "violations"}

REQUESTS = [
    {"password": "Harbor-Lamp-42", "username": "alice", "banned": []},     # passes
    {"password": "short", "username": "alice", "banned": []},              # breaks rules
    {"password": "", "username": "a", "banned": []},
    {"password": "aaaa", "username": "aaaa", "banned": ["a"]},             # breaks five rules
    {"password": "x" * 300, "username": "x" * 32, "banned": ["x"] * 20},
]
rng = random.Random(9606)
for _ in range(45):
    REQUESTS.append({
        "password": random_password(rng, 0, 80),
        "username": random_username(rng),
        "banned": [random_password(rng, 1, 5) for _ in range(rng.randint(0, 20))],
    })

problems = []
for request in REQUESTS:
    status, body = call(request)
    shown = json.dumps(request)[:70]
    if status != 0:
        problems.append(f"{shown}: exited with status {status}, expected 0 for every valid request")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{shown}: expected one JSON object with exactly {sorted(FIELDS)}, got {body!r}")
    elif type(body["ok"]) is not bool:
        problems.append(f"{shown}: ok must be true or false, got {body['ok']!r}")
    elif not isinstance(body["violations"], list) or not all(isinstance(v, str) for v in body["violations"]):
        problems.append(f"{shown}: violations must be a list of strings, got {body['violations']!r}")

# The request may arrive with or without a trailing newline and with surrounding whitespace.
for raw in ('{"password": "Harbor-Lamp-42", "username": "alice", "banned": []}\n',
            '\n  {"banned": [], "username": "alice", "password": "short"}  \n'):
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{raw.strip()!r}: expected status 0 and {sorted(FIELDS)}, got status {status} and {body!r}")

# Refusals write nothing at all on standard output, not even whitespace or an error message.
REFUSED = [
    "",
    "not json",
    '["Harbor-Lamp-42", "alice", []]',
    '{"password": "Harbor-Lamp-42", "username": "alice"}',
    '{"password": 42, "username": "alice", "banned": []}',
    '{"password": "Harbor-Lamp-42", "username": "ana smith", "banned": []}',
    '{"password": "Harbor-Lamp-42", "username": "alice", "banned": [""]}',
]
for raw in REFUSED:
    try:
        done = subprocess.run([PATH], input=raw, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        problems.append(f"{raw!r}: timed out")
        continue
    if done.returncode != 2 or done.stdout != "":
        problems.append(f"{raw!r}: expected status 2 and empty standard output, got status {done.returncode} and {done.stdout[:60]!r}")

finish(problems, f"interface ok: {len(REQUESTS) + 2} valid requests, {len(REFUSED)} refusals")
