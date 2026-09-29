"""H8: invalid requests are refused, never replayed (C4)."""

import json

from _cmd import call, finish

OK = [{"client": "a", "at": 0}, {"client": "a", "at": 5}]


def body(**changes):
    base = {"burst": 2, "rate": 3, "requests": OK}
    for key, value in changes.items():
        if value is ...:
            base.pop(key)
        else:
            base[key] = value
    return json.dumps(base)


def entry(**changes):
    """A log whose first request has one bad field; the requests after it are valid and later."""
    item = {"client": "a", "at": 7}
    for key, value in changes.items():
        if value is ...:
            item.pop(key)
        else:
            item[key] = value
    return json.dumps({"burst": 2, "rate": 3, "requests": [item, {"client": "a", "at": 10}, {"client": "b", "at": 12}]})


INVALID = [
    ("text that isn't JSON", "limit everything"),
    ("empty input", ""),
    ("a list instead of an object", "[2, 3, []]"),
    ("a string instead of an object", '"burst"'),
    ("null instead of an object", "null"),
    ("a missing burst", body(burst=...)),
    ("a burst of 0", body(burst=0)),
    ("a negative burst", body(burst=-1)),
    ("a burst of 2.5", body(burst=2.5)),
    ("a burst of 2.0", '{"burst": 2.0, "rate": 3, "requests": []}'),
    ('a burst of "2"', body(burst="2")),
    ("a burst of true", body(burst=True)),
    ("a burst of null", body(burst=None)),
    ("a missing rate", body(rate=...)),
    ("a rate of 0", body(rate=0)),
    ("a rate of 1e3", '{"burst": 2, "rate": 1e3, "requests": []}'),
    ("a rate of false", body(rate=False)),
    ("a rate of true", body(rate=True)),
    ('a rate of "10"', body(rate="10")),
    ("missing requests", body(requests=...)),
    ("requests as an object", body(requests={"client": "a", "at": 0})),
    ("requests as a string", body(requests="a@0")),
    ("requests of null", body(requests=None)),
    ("a request that is a list", json.dumps({"burst": 2, "rate": 3, "requests": OK + [["a", 7]]})),
    ("a request that is a string", json.dumps({"burst": 2, "rate": 3, "requests": ["a"]})),
    ("a missing client", entry(client=...)),
    ("an empty client", entry(client="")),
    ("a client that is a number", entry(client=7)),
    ("a client of null", entry(client=None)),
    ("a missing at", entry(at=...)),
    ("a negative at", entry(at=-1)),
    ("an at of 7.5", entry(at=7.5)),
    ("an at of 7.0", '{"burst": 2, "rate": 3, "requests": [{"client": "a", "at": 7.0}, {"client": "a", "at": 10}]}'),
    ('an at of "7"', entry(at="7")),
    ("an at of true", entry(at=True)),
    ("an at of false", entry(at=False)),
    ("an invalid request late in the log",
     json.dumps({"burst": 2, "rate": 3, "requests": [{"client": "a", "at": t} for t in range(50)] + [{"client": "", "at": 50}]})),
]
problems = []
for name, raw in INVALID:
    status, out = call(raw=raw)
    if status != 2 or out is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {str(out)[:60]}")

VALID = [
    ("the smallest values", {"burst": 1, "rate": 1, "requests": [{"client": "a", "at": 0}]}),
    ("very large values", {"burst": 10 ** 6, "rate": 10 ** 9, "requests": [{"client": "a", "at": 10 ** 15}]}),
    ("a client named with one space", {"burst": 1, "rate": 1, "requests": [{"client": " ", "at": 3}]}),
]
for name, request in VALID:
    status, out = call(request)
    got = out.get("decisions") if isinstance(out, dict) else None
    if status != 0 or not isinstance(got, list) or len(got) != 1:
        problems.append(f"{name} must not be refused: expected status 0 and one decision, got status {status} and {str(out)[:60]}")

finish(problems, f"invalid ok: {len(INVALID)} refused, {len(VALID)} valid edge requests replayed")
