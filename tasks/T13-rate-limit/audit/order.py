"""X3 (C3): a log that goes back in time anywhere is refused; equal times are allowed and handled in listed order."""

import random

from _cmd import call, finish
from _model import A, R, request, short

problems = []

# Refused: the log goes back in time somewhere, whichever clients are involved.
ramp = [(f"u{i % 5}", 1000 + 2 * i) for i in range(300)]
backwards = [
    ("one client, 10 then 9 ms", [("a", 10), ("a", 9)]),
    ("different clients, 5 then 4 ms", [("a", 0), ("b", 5), ("c", 4)]),
    ("each client in order but the log is not", [("a", 0), ("b", 10), ("a", 5)]),
    ("a tie then a step back", [("x", 100), ("y", 100), ("z", 99)]),
    ("back to 0 after a long log", [("p", 0), ("q", 86_400_000), ("p", 0)]),
    ("back then forward again", [("m", 0), ("m", 50), ("m", 40), ("m", 60)]),
    ("second entry earlier than the first", [("k", 7)] + [("k", 6)] + [("k", 8 + i) for i in range(50)]),
    ("300 ordered entries then one 1 ms early", ramp + [("u0", ramp[-1][1] - 1)]),
    ("a step back in the middle of 300 entries", ramp[:150] + [("u9", ramp[149][1] - 1)] + [(c, t + 10) for c, t in ramp[150:]]),
    ("epoch times one millisecond out of order", [("e", 1_790_000_000_001), ("f", 1_790_000_000_000)]),
]
for label, log in backwards:
    status, body = call(request(2, 5, log))
    if status != 2 or body is not None:
        problems.append(f"{label}: must be refused with status 2 and no output, got status {status} and {short(body, 50)}")

# Not refused: equal times are allowed anywhere, and requests with the same time are handled
# in the order listed. Time does not pass between them and a reject takes nothing, so for one
# client at one instant the listed order shows as accepts first, then rejects: no request may
# be accepted after an earlier request of the same client at the same time was rejected.
# (This does not depend on how many tokens the bucket holds, which other checks cover.)
def ties_in_order(label, burst, rate, log):
    status, body = call(request(burst, rate, log))
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("decisions"), list) \
            or len(body["decisions"]) != len(log):
        problems.append(f"{label}: a log in time order must get status 0 and one decision per request, "
                        f"got status {status} and {short(body, 50)}")
        return
    rejected = set()
    for i, ((c, t), d) in enumerate(zip(log, body["decisions"])):
        if d == R:
            rejected.add((c, t))
        elif d == A and (c, t) in rejected:
            problems.append(f"{label}: request #{i} ({c!r} at {t} ms) is accepted after an earlier request of "
                            f"{c!r} at the same time was rejected, so ties were not handled in listed order")
            return


same_instant = [
    ("two clients alternating at 0 ms", 2, 1, [("p", 0), ("q", 0)] * 4),
    ("four at 5 ms then another client", 2, 1, [("p", 5)] * 4 + [("q", 5)]),
    ("a refill due at 250 ms, then ties at 250 ms", 1, 4, [("m", 0), ("m", 250), ("n", 250), ("m", 250), ("n", 250)]),
    ("twenty requests all at 9000 ms", 3, 1, [("w", 9000)] * 20),
    ("120 requests in plateaus of 4 equal times", 2, 3, [(f"s{i % 3}", 400 * (i // 4)) for i in range(120)]),
]
rng = random.Random(41113)
for n in range(8):
    t, log = rng.randint(0, 50_000), []
    for _ in range(rng.randint(40, 120)):
        t += rng.choice([0, 0, 0, 0, 1, 7, 300, 1000])
        log.append((rng.choice(["alpha", "beta", "Beta", "gamma"]), t))
    same_instant.append((f"generated log with many ties {n + 1}", rng.randint(1, 3), rng.choice([1, 2, 5, 50]), log))
for label, burst, rate, log in same_instant:
    ties_in_order(label, burst, rate, log)

finish(problems, f"order ok: {len(backwards)} backward logs refused, {len(same_instant)} logs with ties replayed in order")
