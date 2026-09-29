"""H6: invalid requests are refused with status 2 and no output; the extreme valid ones are not."""

from _cmd import call, finish

WEEK = "[480, 480, 0, 0, 0, 0, 0]"
INVALID = [
    ("text that isn't JSON", "480 480 0 0 0 0 0"),
    ("empty input", ""),
    ("a list instead of an object", "[[480, 0, 0, 0, 0, 0, 0], 1500]"),
    ("a bare number", "1500"),
    ("null", "null"),
    ("a JSON string", '"minutes"'),
    ("a missing minutes field", '{"rate_cents": 1500}'),
    ("a missing rate", '{"minutes": %s}' % WEEK),
    ("an empty object", "{}"),
    ("minutes as text", '{"minutes": "480,480,0,0,0,0,0", "rate_cents": 1500}'),
    ("minutes as an object", '{"minutes": {"1": 480}, "rate_cents": 1500}'),
    ("minutes as a number", '{"minutes": 960, "rate_cents": 1500}'),
    ("minutes of null", '{"minutes": null, "rate_cents": 1500}'),
    ("an empty week", '{"minutes": [], "rate_cents": 1500}'),
    ("six days", '{"minutes": [480, 480, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("eight days", '{"minutes": [480, 480, 0, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a negative day", '{"minutes": [480, -1, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a day of 1441 minutes", '{"minutes": [480, 0, 0, 0, 0, 0, 1441], "rate_cents": 1500}'),
    ("a fractional day", '{"minutes": [480.5, 0, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a day written 480.0", '{"minutes": [480.0, 0, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a day written 4.8e2", '{"minutes": [4.8e2, 0, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a day as text", '{"minutes": ["480", 0, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a day of true", '{"minutes": [true, 0, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a day of false", '{"minutes": [480, false, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a day of null", '{"minutes": [480, null, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a nested list day", '{"minutes": [[480], 0, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
    ("a rate of 0", '{"minutes": %s, "rate_cents": 0}' % WEEK),
    ("a negative rate", '{"minutes": %s, "rate_cents": -1500}' % WEEK),
    ("a rate of 100001", '{"minutes": %s, "rate_cents": 100001}' % WEEK),
    ("a fractional rate", '{"minutes": %s, "rate_cents": 1500.5}' % WEEK),
    ("a rate written 1500.0", '{"minutes": %s, "rate_cents": 1500.0}' % WEEK),
    ("a rate written 1.5e3", '{"minutes": %s, "rate_cents": 1.5e3}' % WEEK),
    ("a rate as text", '{"minutes": %s, "rate_cents": "1500"}' % WEEK),
    ("a rate of true", '{"minutes": %s, "rate_cents": true}' % WEEK),
    ("a rate of null", '{"minutes": %s, "rate_cents": null}' % WEEK),
]
VALID = [
    ("the lowest rate", '{"minutes": %s, "rate_cents": 1}' % WEEK),
    ("the highest rate", '{"minutes": %s, "rate_cents": 100000}' % WEEK),
    ("every day at 1440 minutes", '{"minutes": [1440, 1440, 1440, 1440, 1440, 1440, 1440], "rate_cents": 100000}'),
    ("a week with no work", '{"minutes": [0, 0, 0, 0, 0, 0, 0], "rate_cents": 1500}'),
]
problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for name, raw in VALID:
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{name}: a valid request must be paid, got status {status} and {body!r}")

finish(problems, f"validation ok: {len(INVALID)} refused, {len(VALID)} accepted")
