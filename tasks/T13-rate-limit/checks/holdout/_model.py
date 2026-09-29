"""Shared helpers for the hidden checks: an exact model of G1-G4 and C2, using fractions."""

from fractions import Fraction

A, R = "accept", "reject"


def request(burst, rate, log, **extra):
    """Build a request from a list of (client, at) pairs."""
    return {"burst": burst, "rate": rate, "requests": [{"client": c, "at": t} for c, t in log], **extra}


def replay(burst, rate, log):
    """The decisions the intent requires for a log of (client, at) pairs."""
    buckets, decisions = {}, []
    for client, at in log:
        if client in buckets:
            tokens, previous = buckets[client]
            tokens = min(Fraction(burst), tokens + Fraction(rate * (at - previous), 1000))
        else:
            tokens = Fraction(burst)
        if tokens >= 1:
            tokens -= 1
            decisions.append(A)
        else:
            decisions.append(R)
        buckets[client] = (tokens, at)
    return decisions


def decisions_of(body):
    return body.get("decisions") if isinstance(body, dict) else None


def compare(call, burst, rate, log, label, problems, expected=None):
    """Run a log and record the first decision that differs from the expected ones."""
    expected = replay(burst, rate, log) if expected is None else expected
    status, body = call(request(burst, rate, log))
    got = decisions_of(body)
    if status != 0 or not isinstance(got, list):
        problems.append(f"{label}: expected status 0 and decisions, got status {status} and {str(body)[:80]}")
        return False
    if got != expected:
        if len(got) != len(expected):
            problems.append(f"{label}: expected {len(expected)} decisions, got {len(got)}")
        else:
            i = next(i for i, (g, e) in enumerate(zip(got, expected)) if g != e)
            client, at = log[i]
            problems.append(f"{label}: request {i + 1} ({client!r} at {at} ms) should be {expected[i]}, got {got[i]}")
        return False
    return True
