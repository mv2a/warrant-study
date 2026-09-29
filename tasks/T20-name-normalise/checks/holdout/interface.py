"""H7 (C1): one JSON object in, one JSON object with exactly the string fields display
and key out, status 0 on success; other request fields are ignored; a refusal is status
2 with nothing on standard output."""

import random

from _cmd import call, finish
from _names import WORDS, cap

problems = []


def expect(label, status, body, expected):
    if status != 0:
        problems.append(f"{label}: expected exit status 0, got {status}")
    elif not isinstance(body, dict) or set(body) != {"display", "key"}:
        problems.append(f"{label}: expected an object with exactly display and key, got {body!r}")
    elif not all(isinstance(value, str) for value in body.values()):
        problems.append(f"{label}: display and key must be strings, got {body!r}")
    elif body != expected:
        problems.append(f"{label}: expected {expected}, got {body!r}")


plain = {"display": "Anna Weber", "key": "annaweber"}
status, body = call({"name": "anna weber"})
expect("a plain request", status, body, plain)

extras = [
    {"name": "anna weber", "email": "anna@example.org"},
    {"id": 7, "name": "anna weber", "list": ["news"], "opt_in": True},
    {"name": "anna weber", "display": "Someone Else", "key": "other"},
    {"name": "anna weber", "honorifics": ["Anna"], "nickname": None},
]
for request in extras:
    status, body = call(request)
    expect(f"extra fields {sorted(set(request) - {'name'})}", status, body, plain)

status, body = call(raw='\n  {\n  "name" :  "anna weber"\n}\n\n')
expect("a request spread over several lines", status, body, plain)
status, body = call(raw='{"name": "Jos\\u00e9 Garc\\u00eda"}')
expect("a request with JSON escapes", status, body, {"display": "José García", "key": "josegarcia"})

rng = random.Random(2220260929)
for _ in range(20):
    words = [rng.choice(WORDS) for _ in range(rng.randint(1, 3))]
    request = {"name": " ".join(words)}
    if rng.random() < 0.5:
        request["source"] = rng.choice(["form", "import", 3, None])
    status, body = call(request)
    display = " ".join(cap(w) for w in words)
    expect(repr(request), status, body, {"display": display, "key": "".join(words)})

for label, request in [("a name that is a number", {"name": 42}), ("an empty name", {"name": ""})]:
    status, body = call(request)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected status 2 and no output, got status {status} and {body!r}")

finish(problems, "interface ok: 27 accepted, 2 refused")
