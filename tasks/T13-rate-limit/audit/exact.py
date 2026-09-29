"""X8 (C2): tokens are counted exactly, never rounded, however many requests come in between.

A token due at the very millisecond of a request is available to it; one due a fraction of a
millisecond later is not. Rates here make token times fall between milliseconds, where
rounding or floating-point drift would change a decision.
"""

import random

from _cmd import call, finish
from _model import A, R, check_log, replay, request

problems = []
logs = 0


def run(label, burst, rate, log):
    global logs
    logs += 1
    check_log(label, burst, rate, log, problems)


def due(rate, k, start=0):
    """The first millisecond at which the k-th token after an empty bucket at start is complete."""
    return start + -(-1000 * k // rate)


# The two examples written in C2 itself.
run("C2 example: rate 3, empty at 0, asks at 333 and 334 ms", 1, 3, [("x", 0), ("x", 333), ("x", 334)])
for burst in (1, 4):
    run(f"C2 example: rate 10, burst {burst}, asks every 10 ms", burst, 10,
        [("x", 0)] * burst + [("x", 10 * i) for i in range(1, 11)])

# The first token after an empty bucket, just before and at the millisecond it is due.
for rate in (3, 6, 7, 9, 11, 13, 17, 30, 70, 101, 333, 600, 997, 999, 1001, 1003, 2999):
    exact = 1000 / rate
    before = int(exact) if 1000 % rate else int(exact) - 1
    log = [("f", 0), ("f", before), ("f", due(rate, 1))]
    want = replay(1, rate, log)
    if want["decisions"] != [A, R, A]:
        problems.append(f"rate {rate}: the audit's own expectation is inconsistent; fix the check")
        continue
    run(f"rate {rate}: empty at 0, asks at {before} and {due(rate, 1)} ms", 1, rate, log)


# Many requests in between do not make the token times drift: with a request every step
# ms after emptying the bucket at start, the k-th token is accepted at the first request
# at or after its exact due time.
def no_drift(label, burst, rate, start, step, end):
    global logs
    logs += 1
    times = list(range(start + step, start + end + 1, step))
    log = [("d", start)] * burst + [("d", t) for t in times]
    want_times = []
    k = 1
    for t in times:
        if t >= due(rate, k, start):
            want_times.append(t)
            k += 1
    status, body = call(request(burst, rate, log))
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("decisions"), list) \
            or len(body["decisions"]) != len(log):
        problems.append(f"{label}: did not get status 0 and one decision per request")
        return
    got = [t for t, d in zip(times, body["decisions"][burst:]) if d == A]
    if got != want_times:
        wrong = next((i for i, (g, w) in enumerate(zip(got, want_times)) if g != w), min(len(got), len(want_times)))
        g = got[wrong] if wrong < len(got) else None
        w = want_times[wrong] if wrong < len(want_times) else None
        problems.append(f"{label}: token {wrong + 1} should be accepted at {w} ms, the first accept there was at {g} ms "
                        f"({len(got)} accepts, expected {len(want_times)})")
    elif body["decisions"] != replay(burst, rate, log)["decisions"]:
        problems.append(f"{label}: accept times right but the decisions differ from the exact model")


no_drift("rate 7, burst 3, every ms for 3 s", 3, 7, 0, 1, 3000)
no_drift("rate 3, burst 5, every ms for 2 s", 5, 3, 0, 1, 2000)
no_drift("rate 13, burst 2, every 3 ms for 3 s", 2, 13, 0, 3, 3000)
no_drift("rate 6, burst 2, every 7 ms for 5 s", 2, 6, 0, 7, 5000)
no_drift("rate 999, burst 2, every ms for 1.5 s", 2, 999, 0, 1, 1500)

# The same at realistic epoch-millisecond times, and at times far beyond them.
EPOCH = 1_790_000_000_000
no_drift("rate 3, burst 5, every ms from epoch 1.79e12", 5, 3, EPOCH, 1, 2000)
no_drift("rate 7, burst 2, every 3 ms from epoch 1.79e12", 2, 7, EPOCH + 7, 3, 3000)
HUGE = 10**17 + 1
run("rate 3 at 10^17 + 1 ms: asks 333 and 334 ms later", 1, 3, [("h", HUGE), ("h", HUGE + 333), ("h", HUGE + 334)])
no_drift("rate 7, burst 3, every ms from 10^17 + 1", 3, 7, HUGE, 1, 1000)

# Generated single-client logs whose gaps hug the token period, so many requests land within
# a millisecond of a token falling due.
rng = random.Random(60221)
RATES = [3, 7, 9, 11, 12, 13, 21, 29, 30, 33, 37, 60, 77, 90, 111, 123, 301, 333, 347, 666, 777, 998, 1001, 1234, 1999]
for n in range(30):
    rate = rng.choice(RATES) if n % 3 else rng.randint(1, 1500)
    burst = rng.randint(1, 6)
    period = 1000 / rate
    gaps = sorted({0, 1, int(period), int(period) + 1, int(period / 2), int(period / 3) + 1, int(2 * period)})
    t = rng.choice([0, rng.randint(0, 10**6), EPOCH + rng.randint(0, 10**6)])
    log = []
    for _ in range(rng.randint(120, 260)):
        t += rng.choice(gaps) if rng.random() < 0.85 else rng.randint(0, int(3 * period) + 2)
        log.append(("g", t))
    run(f"generated log {n + 1} (rate {rate}, burst {burst}, {len(log)} requests)", burst, rate, log)

finish(problems, f"exact ok: {logs} logs")
