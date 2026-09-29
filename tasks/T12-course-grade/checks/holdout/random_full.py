"""H9: many seeded random students get exactly the percent and letter the intent's rules give."""

import random

from _cmd import call, finish
from _oracle import expected, percent_tenths, random_request, show

rng = random.Random(1209)
requests = [random_request(rng, max_quizzes=10, max_homework=8) for _ in range(200)]
problems = []
for r in requests:
    want_percent, want_letter = expected(r)
    status, body = call(r)
    got_letter = body.get("letter") if isinstance(body, dict) else None
    if status != 0 or percent_tenths(body) != want_percent or got_letter != want_letter:
        problems.append(f"{r}: expected percent {show(want_percent)} and letter {want_letter}, got {body!r} (status {status})")

finish(problems, f"random students ok: {len(requests)} requests")
