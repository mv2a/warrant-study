"""H8: invalid requests are refused, never charged, and the valid extremes are not refused."""

from _cmd import call, finish

INVALID = [
    ("text that isn't JSON", "Tuesday at nine"),
    ("empty input", ""),
    ("a list instead of an object", "[600, 700, false]"),
    ("a bare number", "600"),
    ("a bare string", '"600"'),
    ("null", "null"),
    ("a missing entry", '{"exit": 700, "lost_ticket": false}'),
    ("a missing exit", '{"entry": 3150, "lost_ticket": false}'),
    ("a missing lost_ticket", '{"entry": 2300, "exit": 2475}'),
    ("an entry of true", '{"entry": true, "exit": 700, "lost_ticket": false}'),
    ("an entry of false", '{"entry": false, "exit": 700, "lost_ticket": false}'),
    ("an exit of true", '{"entry": 600, "exit": true, "lost_ticket": false}'),
    ("an entry of null", '{"entry": null, "exit": 700, "lost_ticket": false}'),
    ("an entry of 1.5", '{"entry": 1.5, "exit": 700, "lost_ticket": false}'),
    ("an exit of 700.5", '{"entry": 600, "exit": 700.5, "lost_ticket": false}'),
    ("an entry of 600.0", '{"entry": 600.0, "exit": 700, "lost_ticket": false}'),
    ("an exit of 7e2", '{"entry": 600, "exit": 7e2, "lost_ticket": false}'),
    ("deeply nested lists", "[" * 100000 + "]" * 100000),
    ('an entry of "600"', '{"entry": "600", "exit": 700, "lost_ticket": false}'),
    ("an entry of [600]", '{"entry": [600], "exit": 700, "lost_ticket": false}'),
    ("an entry of -1", '{"entry": -1, "exit": 700, "lost_ticket": false}'),
    ("an exit of -1", '{"entry": 600, "exit": -1, "lost_ticket": false}'),
    ("an entry of 10080", '{"entry": 10080, "exit": 700, "lost_ticket": false}'),
    ("an exit of 10080", '{"entry": 4100, "exit": 10080, "lost_ticket": true}'),
    ("an exit of 100000", '{"entry": 600, "exit": 100000, "lost_ticket": false}'),
    ("a lost_ticket of 0", '{"entry": 600, "exit": 700, "lost_ticket": 0}'),
    ("a lost_ticket of 1", '{"entry": 600, "exit": 700, "lost_ticket": 1}'),
    ("a lost_ticket of null", '{"entry": 600, "exit": 700, "lost_ticket": null}'),
    ('a lost_ticket of "no"', '{"entry": 600, "exit": 700, "lost_ticket": "no"}'),
    ('a lost_ticket of "true"', '{"entry": 600, "exit": 700, "lost_ticket": "true"}'),
]
VALID = [
    '{"entry": 0, "exit": 10079, "lost_ticket": false}',
    '{"entry": 10079, "exit": 0, "lost_ticket": true}',
    '{"entry": 0, "exit": 0, "lost_ticket": false}',
    '{"entry": 9000, "exit": 100, "lost_ticket": false}',
]
# Not refused either: -0 is the integer 0, and fields other than the three are ignored.
# Each request must be charged exactly like its plain form.
SAME_AS_PLAIN = [
    ('{"entry": -0, "exit": 45, "lost_ticket": false}', '{"entry": 0, "exit": 45, "lost_ticket": false}'),
    ('{"entry": 8000, "exit": -0, "lost_ticket": true}', '{"entry": 8000, "exit": 0, "lost_ticket": true}'),
    ('{"entry": 2200, "exit": 2500, "lost_ticket": false, "plate": "KX-4471", "gate": 3}',
     '{"entry": 2200, "exit": 2500, "lost_ticket": false}'),
    ('{"meta": {"entry": 1, "exit": 2}, "entry": 5500, "note": null, "exit": 5800, "lost_ticket": true, "paid": [250]}',
     '{"entry": 5500, "exit": 5800, "lost_ticket": true}'),
]
problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for raw in VALID:
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{raw}: a valid request was not charged (status {status}, {body!r})")
for raw, plain in SAME_AS_PLAIN:
    status, body = call(raw=raw)
    plain_status, plain_body = call(raw=plain)
    if status != 0 or not isinstance(body, dict) or (plain_status, plain_body) != (status, body):
        problems.append(f"{raw}: expected status 0 and the same answer as {plain} ({plain_body!r}), "
                        f"got status {status} and {body!r}")

finish(problems, f"refusals ok: {len(INVALID)} invalid requests refused, {len(VALID)} valid extremes accepted, "
                 f"{len(SAME_AS_PLAIN)} requests with -0 or extra fields charged like their plain form")
