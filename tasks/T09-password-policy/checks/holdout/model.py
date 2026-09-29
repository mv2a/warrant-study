"""H10 (G1-G5, C2): generated requests get exactly the answer an independent model of the rules gives."""

import random

from _cmd import call, finish
from _oracle import (DIGIT, LOWER, SYMBOL, UPPER, expected, flip_case, random_password,
                     random_username)

rng = random.Random(9808)
requests = []
for _ in range(120):
    username = random_username(rng, 1, 12)
    pools = rng.sample((LOWER, UPPER, DIGIT, SYMBOL, "aA1-"), rng.randint(1, 5))
    password = random_password(rng, 0, 75, pools)
    if rng.random() < 0.3 and len(username) >= 3:
        start = rng.randrange(len(username) - 2)
        piece = flip_case(rng, username[start:start + rng.choice((3, 4, 4, 5))])
        at = rng.randint(0, len(password))
        password = password[:at] + piece + password[at:]
    banned = []
    for _ in range(rng.randint(0, 4)):
        if password and rng.random() < 0.3:
            start = rng.randrange(len(password))
            banned.append(flip_case(rng, password[start:start + rng.randint(2, 5)]))
        else:
            banned.append(random_password(rng, 2, 5))
    requests.append({"password": password, "username": username, "banned": banned})

problems = []
for request in requests:
    want = expected(request["password"], request["username"], request["banned"])
    status, body = call(request)
    if status != 0 or body != {"ok": not want, "violations": want}:
        problems.append(f"{request}: expected {want}, got status {status} and {body!r}")

finish(problems, f"model ok: {len(requests)} generated requests")
