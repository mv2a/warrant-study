"""H2: every client has its own bucket, keyed by its exact name (G1)."""

import random

from _cmd import call, finish
from _model import A, R, compare, decisions_of, request

rng = random.Random(1302)
POOL = ["alice", "Alice", "alice ", " alice", "ALICE", "bob", "Bob", "b", "carol"]
RATES = [1, 2, 3, 5, 10, 250]
GAPS = [0, 0, 0, 1, 7, 50, 100, 333, 500, 1000, 2500]
problems = []

# Names that differ only in case or spaces are different clients.
log = [("alice", 0), ("Alice", 0), ("alice ", 0), (" alice", 0), ("ALICE", 0), ("alice", 0)]
status, body = call(request(1, 1, log))
spellings = {"alice", "Alice", "alice ", " alice", "ALICE"}
if status != 0 or decisions_of(body) != [A, A, A, A, A, R] or not isinstance(body.get("clients"), dict) \
        or set(body["clients"]) != spellings:
    problems.append(f"five spellings of alice must be five clients with one token each, got status {status} and {str(body)[:100]}")

# Another client's traffic in between does not slow a client's refill.
compare(call, 1, 1, [("a", 0), ("b", 900), ("a", 1000)], "a refills while b is busy", problems, [A, A, A])
compare(call, 2, 4, [("a", 0), ("a", 0), ("b", 200), ("b", 200), ("b", 200), ("a", 250), ("b", 400), ("a", 500)],
        "two busy clients", problems, [A, A, A, A, R, A, R, A])

# Generated logs: each client's decisions match its requests replayed alone.
checked = 0
for n in range(40):
    names = rng.sample(POOL, rng.randint(2, 5))
    burst, rate = rng.randint(1, 4), rng.choice(RATES)
    t, log = rng.choice([0, 0, 1000, 123456]), []
    for _ in range(rng.randint(15, 40)):
        t += rng.choice(GAPS)
        log.append((rng.choice(names), t))
    status, body = call(request(burst, rate, log))
    together = decisions_of(body)
    if status != 0 or not isinstance(together, list) or len(together) != len(log):
        problems.append(f"log {n + 1}: expected status 0 and {len(log)} decisions, got status {status}")
        continue
    present = sorted({c for c, _ in log})
    if not isinstance(body.get("clients"), dict) or sorted(body["clients"]) != present:
        problems.append(f"log {n + 1}: clients should be exactly {present}, got {str(body.get('clients'))[:80]}")
    for name in present:
        positions = [i for i, (c, _) in enumerate(log) if c == name]
        status, alone = call(request(burst, rate, [log[i] for i in positions]))
        mixed = [together[i] for i in positions]
        if decisions_of(alone) != mixed:
            problems.append(f"log {n + 1}: {name!r} gets {mixed} among other clients but {decisions_of(alone)} alone")
            break
        checked += 1

finish(problems, f"clients ok: 40 generated logs, {checked} clients compared with their own replay")
