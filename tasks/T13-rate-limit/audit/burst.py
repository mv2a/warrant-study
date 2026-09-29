"""X5 (G2): a bucket is full at its client's first request, whenever it comes, and never holds more than burst.

Refill amounts here are whole or binary fractions of a token, so rounding (C2) cannot be
the reason for a failure.
"""

from _cmd import finish
from _model import A, R, check_log

problems = []
cases = 0


def expect(label, burst, rate, log, decisions):
    """Check a log against the exact model and against decisions worked out by hand."""
    global cases
    cases += 1
    want = {"decisions": decisions, "clients": {}}
    for (c, _), d in zip(log, decisions):
        tally = want["clients"].setdefault(c, {"accepted": 0, "rejected": 0})
        tally["accepted" if d == A else "rejected"] += 1
    check_log(label, burst, rate, log, problems, want=want)


# Full at the first request, whenever that is: burst accepts at once, then rejects.
for burst in (1, 2, 3, 6, 11, 40):
    for first in (0, 999, 1_790_000_000_123):
        expect(f"burst {burst}, first request at {first} ms", burst, 5,
               [("k", first)] * (burst + 3), [A] * burst + [R] * 3)

# However long a client stays quiet, at most burst requests are accepted at one instant.
expect("burst 4, rate 1000, quiet for 10^9 ms", 4, 1000,
       [("q", 0)] * 4 + [("q", 10**9)] * 7, [A] * 4 + [A] * 4 + [R] * 3)
expect("burst 1, rate 1, quiet for ten years", 1, 1,
       [("q", 0)] + [("q", 315_360_000_000)] * 3, [A, A, R, R])
expect("burst 3, rate 8, quiet for an hour", 3, 8,
       [("q", 0)] * 3 + [("q", 3_600_000)] * 5, [A] * 3 + [A] * 3 + [R] * 2)
expect("burst 9, rate 250, quiet for 10^6 ms", 9, 250,
       [("q", 5)] * 9 + [("q", 1_000_005)] * 12, [A] * 9 + [A] * 9 + [R] * 3)

# Tokens that overflow a full bucket are lost: after refilling to the cap, the next token
# takes its full time again.
expect("burst 3, rate 4: overflow is not kept", 3, 4,
       [("o", 0)] * 3 + [("o", 5000)] * 4 + [("o", 5125), ("o", 5250), ("o", 5500), ("o", 5500)],
       [A] * 3 + [A, A, A, R] + [R, A, A, R])
expect("burst 2, rate 1: overflow is not kept", 2, 1,
       [("o", 0)] * 2 + [("o", 10_000)] * 2 + [("o", 10_500), ("o", 11_000), ("o", 11_000)],
       [A, A, A, A, R, A, R])

# A partly used bucket refills only up to the cap.
expect("burst 5, rate 2: 3 left plus 3 more caps at 5", 5, 2,
       [("p", 0)] * 2 + [("p", 1500)] * 6, [A, A] + [A] * 5 + [R])
expect("burst 6, rate 8: empty, 1 token, then capped at 6", 6, 8,
       [("p", 0)] * 6 + [("p", 125)] * 4 + [("p", 875)] * 7, [A] * 6 + [A, R, R, R] + [A] * 6 + [R])

# A large burst.
expect("burst 1000 at one instant", 1000, 1, [("big", 42)] * 1002, [A] * 1000 + [R] * 2)

finish(problems, f"burst ok: {cases} logs")
