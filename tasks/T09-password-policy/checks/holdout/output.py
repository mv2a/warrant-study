"""H7 (C2): violations lists each broken rule once, only the six codes, sorted; ok means none."""

import random

from _cmd import call, finish
from _oracle import CODES, random_password, random_username, violations_of

# Requests whose exact answer is fixed by construction.
EXACT = [
    ({"password": "aaaa", "username": "aaaa", "banned": ["a"]},
     ["banned", "classes", "repeat", "too_short", "username"]),
    ({"password": "a" * 65, "username": "aaaa", "banned": ["a"]},
     ["banned", "classes", "repeat", "too_long", "username"]),
    ({"password": "Harbor-Lamp-42", "username": "harbor", "banned": ["lamp", "LAMP", "42", "harbor", "-"]},
     ["banned", "username"]),
    ({"password": "harbor-lamp-42-harbor", "username": "xharborx", "banned": ["zz"]},
     ["username"]),
    ({"password": "Harbor-Lamp-42", "username": "alice", "banned": ["zz"]}, []),
    ({"password": "Hb1", "username": "alice", "banned": []}, ["too_short"]),
    ({"password": "zzzHarbor-Lamp", "username": "harb", "banned": ["zzz", "Lamp"]},
     ["banned", "repeat", "username"]),
]

problems = []
for request, expected in EXACT:
    status, body = call(request)
    want = {"ok": not expected, "violations": expected}
    if status != 0 or body != want:
        problems.append(f"{request}: expected {want}, got status {status} and {body!r}")

# Generated requests: whatever the rules find, the list must be well formed.
rng = random.Random(9707)
count = 0
for _ in range(90):
    username = random_username(rng, 1, 8)
    password = random_password(rng, 0, 70)
    if rng.random() < 0.5 and len(username) >= 4:
        password += username.upper()
    banned = [random_password(rng, 1, 2) for _ in range(rng.randint(0, 20))]
    request = {"password": password, "username": username, "banned": banned}
    status, body = call(request)
    got = violations_of(body)
    count += 1
    if status != 0 or got is None or not isinstance(body.get("ok"), bool):
        problems.append(f"{request}: expected status 0, ok and a violations list, got status {status} and {body!r}")
    elif any(code not in CODES for code in got):
        problems.append(f"{request}: unknown codes in {got}")
    elif len(set(got)) != len(got):
        problems.append(f"{request}: repeated codes in {got}")
    elif got != sorted(got):
        problems.append(f"{request}: codes are not in ascending order: {got}")
    elif "too_short" in got and "too_long" in got:
        problems.append(f"{request}: too_short and too_long together: {got}")
    elif body["ok"] != (got == []):
        problems.append(f"{request}: ok is {body['ok']} with violations {got}")

finish(problems, f"output ok: {len(EXACT)} exact answers, {count} generated requests")
