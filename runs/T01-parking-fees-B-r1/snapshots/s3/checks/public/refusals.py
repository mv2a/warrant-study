"""P3: a few invalid requests are refused, never charged."""

from _cmd import call, finish

INVALID = [
    ("text that isn't JSON", "Tuesday morning"),
    ("a missing lost_ticket", '{"entry": 600, "exit": 700}'),
    ("an entry of -5", '{"entry": -5, "exit": 700, "lost_ticket": false}'),
    ("an exit of 10080", '{"entry": 600, "exit": 10080, "lost_ticket": false}'),
]
problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")

finish(problems, f"refusals ok: {len(INVALID)} invalid requests")
