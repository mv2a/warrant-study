"""P3: one-night stays on each weekday."""

from _cmd import call, finish

EXPECTED_TOTAL = {"sun": 20275, "mon": 20275, "tue": 20275, "wed": 20275, "thu": 20275, "fri": 25275}
problems = []
for day, total in EXPECTED_TOTAL.items():
    status, body = call({"check_in": day, "nights": 1, "rate_cents": 20000})
    charged = body.get("total_cents") if isinstance(body, dict) else None
    if status != 0 or charged != total:
        problems.append(f"one {day} night at 20000: expected a total of {total}, got {charged!r} (status {status})")

status, body = call({"check_in": "sat", "nights": 1, "rate_cents": 20000})
if status == 0 or (isinstance(body, dict) and "total_cents" in body):
    problems.append(f"one sat night should be refused, got {body!r} (status {status})")

finish(problems, "one-night stays ok")
