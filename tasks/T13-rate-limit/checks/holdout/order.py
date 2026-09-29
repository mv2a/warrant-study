"""H7: the log is in time order; ties are handled in listed order; going back is refused (C3)."""

import random

from _cmd import call, finish
from _model import A, R, compare, decisions_of, request

rng = random.Random(1307)
problems = []
refused = accepted = 0


def must_refuse(label, log):
    global refused
    status, body = call(request(2, 5, log))
    if status != 2 or body is not None:
        problems.append(f"{label}: expected a refusal (status 2, no output), got status {status} and {str(body)[:60]}")
    refused += 1


must_refuse("another client's earlier timestamp", [("a", 100), ("b", 50)])
must_refuse("the same client's earlier timestamp", [("a", 100), ("a", 99)])
must_refuse("one millisecond back after a tie", [("a", 5), ("b", 5), ("a", 4)])
must_refuse("back to 0 after a long run", [("a", t) for t in range(0, 3000, 10)] + [("b", 0)])
must_refuse("back in time at the second request", [("x", 1), ("x", 0), ("x", 2)])

# Generated logs: valid as recorded, refused once one timestamp steps back.
for n in range(20):
    names = ["a", "b", "c"]
    t, log = rng.randint(1, 1000), []
    for _ in range(rng.randint(10, 300)):
        t += rng.choice([0, 0, 1, 10, 250, 1000])
        log.append((rng.choice(names), t))
    status, body = call(request(2, 5, log))
    got = decisions_of(body)
    if status != 0 or not isinstance(got, list) or len(got) != len(log):
        problems.append(f"generated log {n + 1} is in time order and must be replayed, got status {status} and {str(body)[:60]}")
    accepted += 1
    i = rng.randint(1, len(log) - 1)
    back = log[i - 1][1] - rng.randint(1, min(500, log[i - 1][1]))
    other = [c for c in names if c != log[i - 1][0]]
    client = rng.choice(other) if n % 2 == 0 else log[i - 1][0]
    must_refuse(f"generated log {n + 1} with request {i + 1} stepped back", log[:i] + [(client, back)] + log[i + 1:])

# Equal timestamps are fine and are handled in the order listed.
compare(call, 1, 1, [("x", 5), ("y", 5), ("x", 5)], "ties across clients", problems, [A, A, R])
compare(call, 1, 1, [("a", 0), ("a", 0)], "a tie for one client", problems, [A, R])
compare(call, 2, 1, [("p", 7)] * 2 + [("q", 7)] * 3 + [("p", 1007)] * 2, "many ties", problems, [A, A, A, A, R, A, R])
accepted += 3

finish(problems, f"order ok: {refused} refused, {accepted} accepted")
