"""H4: a stay with a Saturday night needs at least 3 nights; other stays need only one."""

from _cmd import call, finish
from _model import DAYS, priced, refused, refused_by_min_stay

cases = [(day, n) for day in DAYS for n in range(1, 9)] + [(day, 30) for day in DAYS]
problems = []
for day, n in cases:
    status, body = call({"check_in": day, "nights": n, "rate_cents": 10000})
    if refused_by_min_stay(day, n):
        if not refused(status, body):
            problems.append(f"{day}, {n} nights includes a Saturday night and should be refused, got {body!r} (status {status})")
    elif not (priced(status, body) and "total_cents" in body):
        problems.append(f"{day}, {n} nights should be priced, got {body!r} (status {status})")

finish(problems, f"minimum stay ok: {len(cases)} stays")
