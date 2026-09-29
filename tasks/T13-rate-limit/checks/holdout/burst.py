"""H3: a bucket holds at most burst tokens and is full before a client's first request (G2)."""

from _cmd import call, finish
from _model import A, R, compare

problems = []
cases = 0

# Full before the first request, whenever it comes.
for burst in (1, 2, 3, 7, 100):
    for rate in (1, 1000):
        for start in (0, 1, 250, 86_400_000):
            log = [("k", start)] * (burst + 2)
            compare(call, burst, rate, log, f"burst {burst}, rate {rate}, first requests at {start} ms", problems,
                    [A] * burst + [R] * 2)
            cases += 1

# However long a client stays quiet, at most burst requests are accepted at one instant.
for burst in (1, 3, 8):
    for rate in (1, 4, 1000):
        fill = -(-burst * 1000 // rate)  # time to refill an empty bucket, rounded up to a millisecond
        for gap in (fill, fill + 12345, 10 ** 9):
            log = [("q", 0)] * burst + [("q", gap)] * (burst + 3)
            compare(call, burst, rate, log, f"burst {burst}, rate {rate}, quiet for {gap} ms", problems,
                    [A] * (2 * burst) + [R] * 3)
            cases += 1

# Tokens that would overflow a full bucket are lost: half a token of overflow does not carry over,
# so half a token's time after the bucket is emptied again, there is still no whole token.
for burst in (1, 2, 5):
    for rate in (1, 2, 4, 5, 10, 20, 50):
        token = 1000 // rate
        half = token // 2
        full_at = burst * token + half
        log = [("o", 0)] * burst + [("o", full_at)] * burst + [("o", full_at + half)]
        compare(call, burst, rate, log, f"burst {burst}, rate {rate}, overflow", problems, [A] * (2 * burst) + [R])
        cases += 1

# A client that first appears late, after others, starts with a full bucket too.
log = [("x", 0)] * 3 + [("y", 10)] * 2 + [("late", 5000)] * 4
compare(call, 3, 1, log, "a client that first appears at 5000 ms", problems, [A] * 3 + [A] * 2 + [A, A, A, R])
cases += 1

finish(problems, f"burst ok: {cases} logs")
