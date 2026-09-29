"""X-G4: a stay over a Saturday night must be at least 3 nights; other stays may be 1 night."""

from _audit import DAYS, call_all, priced, refused, request, show
from _cmd import finish

RATES = [1, 5, 999, 16300, 45555, 70001]

cases = []
for d, day in enumerate(DAYS):
    for nights in range(1, 8):
        cases.append(request(day, nights, RATES[(d + nights) % len(RATES)]))
for nights in range(8, 31):
    cases.append(request("sat", nights, RATES[nights % len(RATES)]))
    cases.append(request("fri", nights, RATES[(nights + 1) % len(RATES)]))

problems = []
for req, (status, body) in zip(cases, call_all(cases)):
    if refused(req["check_in"], req["nights"]):
        if status != 2 or priced(body):
            problems.append(f"{show(req)} includes a Saturday night and is under 3 nights: expected "
                            f"refusal with status 2 and no price, got status {status} and {body!r}")
    elif status != 0 or not priced(body):
        problems.append(f"{show(req)} should be priced, got status {status} and {body!r}")

n_refused = sum(refused(r["check_in"], r["nights"]) for r in cases)
finish(problems, f"Saturday minimum ok: {n_refused} short Saturday stays refused, {len(cases) - n_refused} others priced")
