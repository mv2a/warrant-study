"""X4 (G1): one bucket per exact client name; other clients never change a client's decisions.

Differential: each client's decisions and counts in a mixed log must equal what the same
command gives when that client's requests are replayed on their own. This isolates G1 from
the refill arithmetic, which other checks cover.
"""

import random

from _cmd import call, finish
from _model import request, short

problems = []
calls = 0


def replay(burst, rate, log):
    global calls
    calls += 1
    status, body = call(request(burst, rate, log))
    ok = (status == 0 and isinstance(body, dict) and isinstance(body.get("decisions"), list)
          and len(body["decisions"]) == len(log) and isinstance(body.get("clients"), dict))
    return body if ok else None


def independent(label, burst, rate, log):
    mixed = replay(burst, rate, log)
    if mixed is None:
        problems.append(f"{label}: the mixed log did not get status 0 and a well-formed answer")
        return
    names = list(dict.fromkeys(c for c, _ in log))
    if set(mixed["clients"]) != set(names):
        problems.append(f"{label}: clients should be exactly {short(names)}, got {short(sorted(mixed['clients']))}")
        return
    for name in names:
        where = [i for i, (c, _) in enumerate(log) if c == name]
        alone = replay(burst, rate, [log[i] for i in where])
        if alone is None:
            problems.append(f"{label}: {name!r} replayed alone did not get status 0 and a well-formed answer")
            return
        beside = [mixed["decisions"][i] for i in where]
        if beside != alone["decisions"]:
            k = next(j for j, (x, y) in enumerate(zip(beside, alone["decisions"])) if x != y)
            problems.append(f"{label}: {name!r} at {log[where[k]][1]} ms gets {beside[k]!r} beside other clients "
                            f"but {alone['decisions'][k]!r} alone")
            return
        if mixed["clients"].get(name) != alone["clients"].get(name):
            problems.append(f"{label}: {name!r} is counted {short(mixed['clients'].get(name))} beside other clients "
                            f"but {short(alone['clients'].get(name))} alone")
            return


# Names that differ only in case, spacing or invisible characters are different clients.
near = ["alice", "Alice", "ALICE", "alice ", " alice", "alice\t", "al ice", "alice​"]
independent("case and spacing variants", 1, 1, [(n, 0) for n in near] * 2 + [(n, 400) for n in near])

# Unicode look-alikes are compared as exact strings, with no normalisation or case folding.
alike = ["été", "été", "straße", "strasse", "STRASSE", "ﬁle", "file", "Ⅳ", "IV", "İd", "id"]
independent("unicode look-alikes", 2, 1, [(n, 0) for n in alike] * 3 + [(n, 10) for n in alike])

# Names that look like numbers, keywords or the output's own field names are ordinary clients.
tricky = ["__proto__", "constructor", "toString", "accepted", "rejected", "decisions", "clients", "null", "0", "00", "-1", "true"]
independent("names that look like keywords", 1, 2, [(n, 0) for n in tricky] * 2 + [(n, 500) for n in tricky])

# A client flooding the limiter does not change a quiet client's decisions.
flood = [("flood", t) for t in range(400)]
calm = [("calm", 0), ("calm", 0), ("calm", 200), ("calm", 399)]
independent("a flood beside a quiet client", 2, 5, sorted(flood + calm, key=lambda e: e[1]))

# Generated logs: several clients, some with near-duplicate names, sharing a timeline.
rng = random.Random(77003)
pool = ["api-1", "API-1", "api-1 ", "worker", "Worker", "cron", "cron\n", "partner/acme", "partner/Acme", "x"]
for n in range(18):
    names = rng.sample(pool, rng.randint(3, 5))
    burst, rate = rng.randint(1, 4), rng.choice([1, 2, 3, 5, 7, 10, 40, 125, 999])
    t, log = rng.randint(0, 10_000), []
    for _ in range(rng.randint(30, 70)):
        t += rng.choice([0, 0, 0, 1, 4, 25, 90, 333, rng.randint(0, 1500)])
        log.append((rng.choice(names), t))
    independent(f"generated log {n + 1} (burst {burst}, rate {rate})", burst, rate, log)

finish(problems, f"clients ok: every client decided the same beside others as alone ({calls} runs)")
