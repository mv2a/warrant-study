"""H1: the interface in C1: fields, order of decisions, per-client counts, refusals."""

import random

from _cmd import call, finish
from _model import A, R, request

rng = random.Random(1301)
NAMES = ["web", "cron", "Mobile", "svc-7", "a b", "über"]
problems = []


def shape(label, req, log):
    status, body = call(req)
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
        return None
    if not isinstance(body, dict) or set(body) != {"decisions", "clients"}:
        problems.append(f"{label}: expected an object with exactly decisions and clients, got {str(body)[:80]}")
        return None
    decisions, clients = body["decisions"], body["clients"]
    if not isinstance(decisions, list) or len(decisions) != len(log) or any(d not in (A, R) for d in decisions):
        problems.append(f"{label}: decisions must hold accept or reject for each of {len(log)} requests, got {str(decisions)[:80]}")
        return None
    names = {c for c, _ in log}
    if not isinstance(clients, dict) or set(clients) != names:
        problems.append(f"{label}: clients must list exactly {sorted(names)}, got {str(clients)[:80]}")
        return None
    for name in names:
        mine = [d for (c, _), d in zip(log, decisions) if c == name]
        want = {"accepted": mine.count(A), "rejected": mine.count(R)}
        entry = clients[name]
        if entry != want or not all(type(v) is int for v in entry.values()):
            problems.append(f"{label}: clients[{name!r}] should be {want}, got {entry!r}")
            return None
    return body


# Generated logs: shape and per-client counts.
for n in range(30):
    names = rng.sample(NAMES, rng.randint(1, 4))
    t, log = rng.choice([0, 5, 90000]), []
    for _ in range(rng.randint(1, 25)):
        t += rng.choice([0, 0, 1, 40, 300, 1000, 5000])
        log.append((rng.choice(names), t))
    shape(f"log {n + 1}", request(rng.randint(1, 4), rng.choice([1, 3, 20, 1000]), log), log)

# Decisions come in the order the requests were given, not grouped by client.
log = [("p", 0), ("q", 0), ("p", 0), ("q", 0), ("r", 5)]
body = shape("interleaved clients", request(1, 1, log), log)
if body is not None and body["decisions"] != [A, A, R, R, A]:
    problems.append(f"interleaved clients: decisions must follow the log order, expected {[A, A, R, R, A]}, got {body['decisions']}")

# An empty log.
status, body = call(request(2, 5, []))
if status != 0 or body != {"decisions": [], "clients": {}}:
    problems.append(f"an empty log: expected status 0 and empty decisions and clients, got status {status} and {body!r}")

# Other fields are ignored, at the top level and in each request.
log = [("web", 0), ("web", 0), ("api", 3), ("web", 700), ("web", 1000)]
plain = request(1, 1, log)
extra = request(1, 1, log, window=60, note="replay", requests_total=5)
for entry in extra["requests"]:
    entry.update({"path": "/v1/items", "cost": 3, "ip": "10.0.0.1"})
s1, b1 = call(plain)
s2, b2 = call(extra)
if s1 != 0 or s2 != 0 or b1 != b2:
    problems.append(f"extra fields must be ignored: without them status {s1} and {b1!r}, with them status {s2} and {b2!r}")

# Refusals exit with status 2 and write nothing on standard output.
REFUSED = [
    ("a burst of 0", '{"burst": 0, "rate": 1, "requests": []}'),
    ("text that isn't JSON", "replay please"),
    ("a log that goes back in time", '{"burst": 1, "rate": 1, "requests": [{"client": "a", "at": 9}, {"client": "a", "at": 8}]}'),
    ("a request without a client", '{"burst": 1, "rate": 1, "requests": [{"at": 9}]}'),
]
for name, raw in REFUSED:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected status 2 and no output, got status {status} and {body!r}")

finish(problems, "interface ok: 30 generated logs, ordering, empty log, extra fields, 4 refusals")
