"""H8 (C3): invalid requests are refused (status 2, no output), and valid edge cases are not."""

import json

from _cmd import call, finish

GOOD = {"password": "Harbor-Lamp-42", "username": "alice", "banned": ["lamp"]}


def but(**changes):
    request = dict(GOOD)
    for key, value in changes.items():
        if value is ...:
            del request[key]
        else:
            request[key] = value
    return json.dumps(request)


REFUSED = [
    ("empty input", ""),
    ("text that is not JSON", "Harbor-Lamp-42"),
    ("JSON cut short", '{"password": "Harbor-Lamp-42", "username": "alice"'),
    ("two JSON objects", but() + " " + but()),
    ("a comma and a second object", but() + "," + but()),
    ("a word on the line after the object", but() + "\nEND"),
    ("a label before the object", "request: " + but()),
    ("a JSON list", '["Harbor-Lamp-42", "alice", []]'),
    ("a JSON string", '"Harbor-Lamp-42"'),
    ("a JSON number", "42"),
    ("JSON null", "null"),
    ("an empty object", "{}"),
    ("a missing password", but(password=...)),
    ("a missing username", but(username=...)),
    ("a missing banned list", but(banned=...)),
    ("an extra field", but(role="admin")),
    ("an extra field named ok", but(ok=True)),
    ("a password of null", but(password=None)),
    ("a numeric password", but(password=12345678901234)),
    ("a password of true", but(password=True)),
    ("a password given as a list", but(password=["Harbor-Lamp-42"])),
    ("a password given as an object", but(password={"text": "Harbor-Lamp-42"})),
    ("a username of null", but(username=None)),
    ("a numeric username", but(username=7)),
    ("an empty username", but(username="")),
    ("a 33-character username", but(username="a" * 33)),
    ("a username with a space", but(username="ana smith")),
    ("a username with an at sign", but(username="ana@example")),
    ("a username with a slash", but(username="ana/smith")),
    ("a username with a plus", but(username="ana+1")),
    ("a username with a tab", but(username="ana\tsmith")),
    ("a username with a non-ASCII letter", but(username="jos\u00e9")),
    ("a username with a fullwidth letter", but(username="\uff41lice")),
    ("a username with a non-ASCII digit", but(username="alice\u0663")),
    ("a username given as a list", but(username=["alice"])),
    ("a banned value of null", but(banned=None)),
    ("a banned value that is a string", but(banned="lamp")),
    ("a banned value that is an object", but(banned={"lamp": True})),
    ("21 banned entries", but(banned=[f"w{n}" for n in range(21)])),
    ("an empty banned entry", but(banned=[""])),
    ("an empty banned entry after good ones", but(banned=["lamp", "harbor", ""])),
    ("a numeric banned entry", but(banned=[3])),
    ("a null banned entry", but(banned=["lamp", None])),
    ("a nested banned list", but(banned=[["lamp"]])),
    ("a banned entry of true", but(banned=[True])),
]

ACCEPTED = [
    ("a 32-character username", but(username="a" * 32)),
    ("a one-character username", but(username="a")),
    ("a username with dot, underscore, hyphen and digits", but(username="A.b_c-9")),
    ("a username made only of symbols", but(username="._-")),
    ("20 banned entries", but(banned=[f"w{n}" for n in range(20)])),
    ("an empty banned list", but(banned=[])),
    ("repeated banned entries", but(banned=["lamp", "lamp"])),
    ("banned entries with spaces and accents", but(banned=[" ", "caf\u00e9", "\U0001f600"])),
    ("an empty password", but(password="")),
    ("a password with a space, tab and accents", but(password="Harbor Lamp\t\u00e9\u00c9 42")),
    ("a password of over 500 characters", but(password="Harbor-Lamp-42" * 36)),
    ("the fields in another order", json.dumps({"banned": [], "username": "alice", "password": "Harbor-Lamp-42"})),
]

problems = []
for name, raw in REFUSED:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for name, raw in ACCEPTED:
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("violations"), list):
        problems.append(f"{name}: a valid request, expected status 0 and an answer, got status {status} and {body!r}")

finish(problems, f"validation ok: {len(REFUSED)} refused, {len(ACCEPTED)} accepted")
