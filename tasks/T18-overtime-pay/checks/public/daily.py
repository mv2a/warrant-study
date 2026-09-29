"""P3: a few short weeks split at the 8-hour mark of each day."""

from _cmd import call, finish

WEEKS = [
    ([480, 0, 0, 0, 0, 0, 0], 1600, (480, 0, 0)),
    ([600, 300, 0, 0, 0, 0, 0], 2000, (780, 120, 0)),
    ([0, 0, 660, 0, 0, 0, 0], 1250, (480, 180, 0)),
]
problems = []
for minutes, rate, expected in WEEKS:
    status, body = call({"minutes": minutes, "rate_cents": rate})
    got = tuple(body.get(k) for k in ("regular_minutes", "overtime_minutes", "double_minutes")) \
        if isinstance(body, dict) else None
    if status != 0 or got != expected:
        problems.append(f"{minutes}: expected regular, overtime, double minutes {expected}, got {got!r} (status {status})")

finish(problems, f"daily split ok: {len(WEEKS)} weeks")
