"""X1 (C1): the interface: output shape, decision order, per-client counts, ignored fields."""

import json
import random

from _cmd import call, finish
from _model import A, R, request, short

problems = []


def shaped(label, body, log):
    """C1's shape: exactly decisions and clients, one decision per request, one entry per client."""
    if not isinstance(body, dict) or set(body) != {"decisions", "clients"}:
        problems.append(f"{label}: expected an object with exactly decisions and clients, got {short(body)}")
        return False
    decisions, clients = body["decisions"], body["clients"]
    if not isinstance(decisions, list) or len(decisions) != len(log):
        problems.append(f"{label}: expected a list of {len(log)} decisions, got {short(decisions)}")
        return False
    odd = [d for d in decisions if not isinstance(d, str) or d not in (A, R)]
    if odd:
        problems.append(f"{label}: every decision must be \"accept\" or \"reject\", got {short(odd[0])}")
        return False
    names = {c for c, _ in log}
    if not isinstance(clients, dict) or set(clients) != names:
        problems.append(f"{label}: clients must have exactly one entry per client in the log {short(sorted(names))}, got {short(clients)}")
        return False
    for name in sorted(names):
        mine = [d for (c, _), d in zip(log, decisions) if c == name]
        want = {"accepted": mine.count(A), "rejected": mine.count(R)}
        entry = clients[name]
        if (not isinstance(entry, dict) or set(entry) != {"accepted", "rejected"}
                or any(type(v) is not int for v in entry.values()) or entry != want):
            problems.append(f"{label}: clients[{name!r}] should be {want}, got {short(entry)}")
            return False
    return True


def run(label, log, burst, rate, raw=None):
    status, body = call(request(burst, rate, log)) if raw is None else call(raw=raw)
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
        return None
    return body if shaped(label, body, log) else None


# An empty log: no decisions and no clients.
for burst, rate in ((1, 1), (7, 250)):
    status, body = call({"burst": burst, "rate": rate, "requests": []})
    if status != 0 or body != {"decisions": [], "clients": {}}:
        problems.append(f"empty log (burst {burst}, rate {rate}): expected status 0 and "
                        f"{{'decisions': [], 'clients': {{}}}}, got status {status} and {short(body)}")

# Decisions come back in the order the requests were listed. The per-client counts must match
# the decisions at each client's own positions, which fails if decisions are grouped or
# reordered (these interleaved logs give clients different mixes of accepts and rejects).
ordered = [
    [("x", 0), ("y", 0), ("x", 0), ("y", 0)],
    [("y", 3), ("x", 3), ("y", 3), ("y", 3), ("x", 3), ("z", 3), ("y", 3)],
    [("b", 0), ("a", 0), ("b", 0), ("b", 0), ("a", 900), ("c", 900), ("b", 900), ("a", 900), ("a", 900)],
]
for n, log in enumerate(ordered, 1):
    run(f"interleaved log {n}", log, 1, 1)

# A generated multi-client log: shape and counts must agree with the decisions given.
rng = random.Random(50929)
names = ["gw-eu", "gw-us", "batch", "Batch", "mobile app", "Zoë", "東京", "\U0001f6a6 edge"]
for n in range(3):
    t, log = rng.randint(0, 5000), []
    for _ in range(rng.randint(40, 90)):
        t += rng.choice([0, 0, 1, 3, 17, 120, 400])
        log.append((rng.choice(names), t))
    run(f"generated log {n + 1} ({len(log)} requests)", log, rng.randint(1, 3), rng.choice([2, 3, 9, 40]))

# Client names are reported back exactly, including characters that JSON must escape.
odd_names = ['say "hi"', "back\\slash", "tab\there", "new\nline", " ", "Zoë", "\U0001f6a6", "\u0000nul"]
run("names that need escaping", [(c, 10) for c in odd_names], 1, 1)

# One client, many requests at one instant, and a longer log: counts still match.
run("300 requests at one instant", [("solo", 77)] * 300, 4, 1)
big_rng = random.Random(3301)
t, big = 0, []
for _ in range(2500):
    t += big_rng.choice([0, 1, 2, 5])
    big.append((f"c{big_rng.randint(0, 49)}", t))
run("2500 requests from 50 clients", big, 2, 30)

# Fields other than burst, rate, requests, client and at are ignored.
base_log = [("north", 0), ("south", 0), ("north", 0), ("north", 150), ("south", 600), ("north", 900), ("north", 900)]
plain = run("reference log without extra fields", base_log, 1, 4)
if plain is not None:
    top = request(1, 4, base_log)
    top.update({"window_ms": 1000, "cost": 5, "Burst": 0, "RATE": "fast", "note": None,
                "decisions": ["reject"], "clients": {"north": {"accepted": 0, "rejected": 9}},
                "version": 2.5, "requests_count": -1})
    status, body = call(top)
    if status != 0 or body != plain:
        problems.append(f"extra top-level fields must be ignored: expected status 0 and {short(plain)}, got status {status} and {short(body)}")
    inner = request(1, 4, base_log)
    for i, entry in enumerate(inner["requests"]):
        entry.update({"path": "/v1/items", "method": "GET", "cost": 3, "id": i, "Client": "other", "AT": -5, "ok": True})
    status, body = call(inner)
    if status != 0 or body != plain:
        problems.append(f"extra fields inside requests must be ignored: expected status 0 and {short(plain)}, got status {status} and {short(body)}")
    # The same request written with other key orders and whitespace gives the same answer.
    reordered = {"requests": [{"at": t, "client": c} for c, t in base_log], "rate": 4, "burst": 1}
    for label, raw in (("keys in another order", json.dumps(reordered)),
                       ("pretty-printed with surrounding whitespace", "\n\n  " + json.dumps(request(1, 4, base_log), indent=3) + "\n\n")):
        status, body = call(raw=raw)
        if status != 0 or body != plain:
            problems.append(f"{label}: expected status 0 and {short(plain)}, got status {status} and {short(body)}")

# A refused request exits with status 2 and writes nothing to standard output.
for label, raw in (("rate 0", '{"burst": 2, "rate": 0, "requests": []}'),
                   ("a JSON list", '[{"burst": 2, "rate": 1, "requests": []}]'),
                   ("a request with no client", '{"burst": 2, "rate": 1, "requests": [{"at": 4}]}')):
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: must be refused with status 2 and no output, got status {status} and {short(body)}")

finish(problems, "interface ok: shape, order, counts, escaping, ignored fields and refusals")
