"""X7 (G4): accept needs at least one whole token and takes exactly one; a reject takes nothing.

A client that keeps retrying must get its next token at the same moment as one that waits.
Refill amounts are whole or binary fractions of a token, so rounding (C2) is not involved.
"""

from _cmd import call, finish
from _model import A, R, check_log, replay, request

problems = []
CASES = [
    # (label, burst, rate, times for one client, decisions worked out by hand)
    ("exactly one whole token is enough", 1, 2, [0, 500, 500], [A, A, R]),
    ("seven eighths of a token is not", 1, 1, [0, 875, 1000], [A, R, A]),
    ("an accept takes one token, not all of them", 5, 4,
     [0] * 5 + [625] * 3 + [750] * 2, [A] * 5 + [A, A, R] + [A, R]),
    ("fifty rejects at one instant take nothing", 2, 4, [0, 0] + [125] * 50 + [250, 250], [A, A] + [R] * 50 + [A, R]),
    ("a reject does not restart the refill", 1, 2, [0, 375, 500], [A, R, A]),
]
for label, burst, rate, times, decisions in CASES:
    log = [("g", t) for t in times]
    want = replay(burst, rate, log)
    if want["decisions"] != decisions:
        problems.append(f"{label}: the audit's own expectation is inconsistent; fix the check")
        continue
    check_log(label, burst, rate, log, problems, want=want)


def accept_times(burst, rate, times):
    status, body = call(request(burst, rate, [("c", t) for t in times]))
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("decisions"), list) \
            or len(body["decisions"]) != len(times):
        return None
    return [t for t, d in zip(times, body["decisions"]) if d == A]


# Retrying versus waiting: the same accept times either way.
PAIRS = [
    # (label, burst, rate, how the bucket is emptied, retry times, wait times, the accept times after emptying)
    ("rate 1, retry every 125 ms", 1, 1, [0], [125 * i for i in range(1, 17)], [1000, 2000], [1000, 2000]),
    ("rate 125, retry every ms", 1, 125, [0], list(range(1, 25)), [8, 16, 24], [8, 16, 24]),
    ("rate 250, burst 3, retry every ms", 3, 250, [0, 0, 0], list(range(1, 13)), [4, 8, 12], [4, 8, 12]),
    ("rate 375, burst 2, retry every ms", 2, 375, [0, 0], list(range(1, 17)), [3, 6, 8, 11, 14, 16], [3, 6, 8, 11, 14, 16]),
]
for label, burst, rate, empty, retry, wait, due in PAIRS:
    got_retry = accept_times(burst, rate, empty + retry)
    got_wait = accept_times(burst, rate, empty + wait)
    if got_retry is None or got_wait is None:
        problems.append(f"{label}: did not get status 0 and one decision per request")
        continue
    after_retry = [t for t in got_retry[len(empty):]]
    after_wait = [t for t in got_wait[len(empty):]]
    if after_retry != due or after_wait != due:
        problems.append(f"{label}: tokens are due at {due} ms; the retrying client got them at {after_retry} "
                        f"and the waiting client at {after_wait}")

finish(problems, f"retry ok: {len(CASES)} logs and {len(PAIRS)} retry/wait pairs")
