"""Exact model of the rate-limit replay, written from intent.md alone, plus shared helpers.

The model follows G2, G3, G4 and C2 literally, with exact fractions: a client's bucket is
full (burst tokens) at its first request; after that, at time t it holds
min(burst, k + rate * (t - p) / 1000), where k is what it was left with right after its
previous request at time p; a request is accepted when that is at least 1, and then takes
exactly 1; otherwise it is rejected and takes nothing. Buckets are keyed by the exact
client string (G1).
"""

from fractions import Fraction

from _cmd import call

A, R = "accept", "reject"


def replay(burst, rate, log):
    """Expected output for a time-ordered log of (client, at) pairs."""
    cap = Fraction(burst)
    buckets = {}
    decisions = []
    clients = {}
    for client, at in log:
        if client in buckets:
            left, then = buckets[client]
            tokens = min(cap, left + Fraction(rate * (at - then), 1000))
        else:
            tokens = cap
        if tokens >= 1:
            tokens -= 1
            decision = A
        else:
            decision = R
        buckets[client] = (tokens, at)
        decisions.append(decision)
        tally = clients.setdefault(client, {"accepted": 0, "rejected": 0})
        tally["accepted" if decision == A else "rejected"] += 1
    return {"decisions": decisions, "clients": clients}


def request(burst, rate, log):
    return {"burst": burst, "rate": rate, "requests": [{"client": c, "at": t} for c, t in log]}


def short(value, limit=70):
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def compare(label, log, body, want, problems):
    """Record the first decision that differs from want. Returns True when all match.

    Only the decisions are compared: they are what G1-G4, C2 and C3 promise. The exact
    output shape and the per-client counts belong to C1 and are checked by interface.py,
    so a counting or shape mistake does not also fail every other promise.
    """
    got = body.get("decisions") if isinstance(body, dict) else None
    if not isinstance(got, list) or len(got) != len(want["decisions"]):
        problems.append(f"{label}: expected an object whose decisions list has {len(want['decisions'])} entries, got {short(body)}")
        return False
    for i, (g, w) in enumerate(zip(got, want["decisions"])):
        if g != w:
            client, at = log[i]
            problems.append(f"{label}: request #{i} ({client!r} at {at} ms) got {short(g, 20)}, expected {w!r}")
            return False
    return True


def check_log(label, burst, rate, log, problems, want=None):
    """Run one log and compare its decisions with the exact model (or an explicit expectation)."""
    want = want if want is not None else replay(burst, rate, log)
    status, body = call(request(burst, rate, log))
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
        return False
    return compare(label, log, body, want, problems)
