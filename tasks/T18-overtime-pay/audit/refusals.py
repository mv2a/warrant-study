"""X: invalid requests are refused, never paid (C3).

Every request below breaks one rule of C3 and must get exit status 2 with no output.
Numbers are written as raw JSON text, so 480.0 and 4.8e2 reach the command exactly as
written. The edges of the valid ranges (0 and 1440 minutes, rates 1 and 100000) must still
be paid. A fixed-seed generator also corrupts one field of otherwise valid weeks. The
refused request given as an example in C3 is sent exactly as written there, and must exit
2 with nothing at all on standard output.
"""

import json
import random
import subprocess

from _cmd import PATH, call, finish
from _expect import call_all

GOOD_DAYS = ["300", "0", "615", "0", "480", "90", "0"]


def week(days=None, rate="1850", day=None, value=None):
    """Raw JSON text for a request, with one day's text replaced when asked."""
    days = list(days or GOOD_DAYS)
    if day is not None:
        days[day] = value
    return '{"minutes": [%s], "rate_cents": %s}' % (", ".join(days), rate)


REFUSED = [
    # not JSON at all
    ("empty input", ""),
    ("only whitespace", "  \n\t "),
    ("plain words", "minutes=300 rate=1850"),
    ("a truncated object", week()[:-1]),
    ("single quotes", week().replace('"', "'")),
    ("a trailing comma", week()[:-1] + ", }"),
    ("two objects in a row", week() + " " + week()),
    ("NaN as the rate", week(rate="NaN")),
    ("Infinity as the rate", week(rate="Infinity")),
    ("-Infinity as a day", week(day=2, value="-Infinity")),
    ("NaN as a day", week(day=0, value="NaN")),
    # JSON, but not an object
    ("an empty list", "[]"),
    ("a list holding a valid request", "[" + week() + "]"),
    ("null", "null"),
    ("a bare number", "1850"),
    ("a bare string", json.dumps(week())),
    ("true", "true"),
    ("false", "false"),
    # a field missing
    ("an empty object", "{}"),
    ("no rate_cents", '{"minutes": [300, 0, 615, 0, 480, 90, 0]}'),
    ("no minutes", '{"rate_cents": 1850}'),
    ("Minutes capitalised", '{"Minutes": [300, 0, 615, 0, 480, 90, 0], "rate_cents": 1850}'),
    ("rateCents instead of rate_cents", '{"minutes": [300, 0, 615, 0, 480, 90, 0], "rateCents": 1850}'),
    ("minutes under another object", '{"week": {"minutes": [300, 0, 615, 0, 480, 90, 0]}, "rate_cents": 1850}'),
    # minutes is not a list of exactly 7
    ("an empty minutes list", '{"minutes": [], "rate_cents": 1850}'),
    ("one day", '{"minutes": [300], "rate_cents": 1850}'),
    ("six days", '{"minutes": [300, 0, 615, 0, 480, 90], "rate_cents": 1850}'),
    ("eight days", '{"minutes": [300, 0, 615, 0, 480, 90, 0, 0], "rate_cents": 1850}'),
    ("fourteen days", '{"minutes": [%s], "rate_cents": 1850}' % ", ".join(GOOD_DAYS * 2)),
    ("minutes as a string", '{"minutes": "300, 0, 615, 0, 480, 90, 0", "rate_cents": 1850}'),
    ("minutes as an object", '{"minutes": {"1": 300, "2": 0, "3": 615, "4": 0, "5": 480, "6": 90, "7": 0}, "rate_cents": 1850}'),
    ("minutes as a number", '{"minutes": 1485, "rate_cents": 1850}'),
    ("minutes null", '{"minutes": null, "rate_cents": 1850}'),
    ("minutes true", '{"minutes": true, "rate_cents": 1850}'),
    ("the week nested in a list", '{"minutes": [[300, 0, 615, 0, 480, 90, 0]], "rate_cents": 1850}'),
    # a day out of range
    ("day 1 at -1", week(day=0, value="-1")),
    ("day 4 at -480", week(day=3, value="-480")),
    ("day 7 at -1440", week(day=6, value="-1440")),
    ("day 2 at 1441", week(day=1, value="1441")),
    ("day 7 at 1441", week(day=6, value="1441")),
    ("day 5 at 2880", week(day=4, value="2880")),
    ("day 3 at 10 to the 20th", week(day=2, value="100000000000000000000")),
    # a day that is not a whole number
    ("day 1 at 480.5", week(day=0, value="480.5")),
    ("day 3 at 480.0", week(day=2, value="480.0")),
    ("day 6 at 0.0", week(day=5, value="0.0")),
    ("day 2 at 1440.0", week(day=1, value="1440.0")),
    ("day 4 at 4.8e2", week(day=3, value="4.8e2")),
    ("day 5 at 48E1", week(day=4, value="48E1")),
    ("day 7 at 4800e-1", week(day=6, value="4800e-1")),
    ("day 1 at 1e2", week(day=0, value="1e2")),
    ("day 6 at 0e0", week(day=5, value="0e0")),
    ("day 2 at -0.0", week(day=1, value="-0.0")),
    ("day 3 at 0.25", week(day=2, value="0.25")),
    ("day 1 at true", week(day=0, value="true")),
    ("day 7 at false", week(day=6, value="false")),
    ("day 4 at true", week(day=3, value="true")),
    ("day 2 as a string", week(day=1, value='"480"')),
    ("day 5 as an empty string", week(day=4, value='""')),
    ("day 3 null", week(day=2, value="null")),
    ("day 6 as a list", week(day=5, value="[90]")),
    ("day 1 as an object", week(day=0, value='{"minutes": 300}')),
    # a rate out of range
    ("rate 0", week(rate="0")),
    ("rate -1", week(rate="-1")),
    ("rate -1850", week(rate="-1850")),
    ("rate 100001", week(rate="100001")),
    ("rate 250000", week(rate="250000")),
    ("rate 10 to the 15th", week(rate="1000000000000000")),
    # a rate that is not a whole number
    ("rate 1850.0", week(rate="1850.0")),
    ("rate 1.85e3", week(rate="1.85e3")),
    ("rate 185E1", week(rate="185E1")),
    ("rate 1e5", week(rate="1e5")),
    ("rate 100000.0", week(rate="100000.0")),
    ("rate 1.0", week(rate="1.0")),
    ("rate 1850.5", week(rate="1850.5")),
    ("rate 0.5", week(rate="0.5")),
    ("rate true", week(rate="true")),
    ("rate false", week(rate="false")),
    ("rate as a string", week(rate='"1850"')),
    ("rate as an empty string", week(rate='""')),
    ("rate null", week(rate="null")),
    ("rate as a list", week(rate="[1850]")),
    ("rate as an object", week(rate='{"cents": 1850}')),
]

# The same kinds of mistakes in random places, from a fixed seed.
rng = random.Random(18_40_1440)
BAD_DAY_TEXT = [
    lambda r: str(-r.randint(1, 1440)),
    lambda r: str(r.randint(1441, 50000)),
    lambda r: "%d.0" % r.randint(0, 1440),
    lambda r: "%d.%d" % (r.randint(0, 1439), r.randint(1, 9)),
    lambda r: "%de0" % r.randint(0, 1440),
    lambda r: "%dE-1" % (10 * r.randint(0, 144)),
    lambda r: r.choice(["true", "false", "null", '"%d"' % r.randint(0, 1440), "[%d]" % r.randint(0, 1440)]),
]
BAD_RATE_TEXT = [
    lambda r: str(-r.randint(0, 100000)),
    lambda r: str(r.randint(100001, 10 ** 9)),
    lambda r: "%d.0" % r.randint(1, 100000),
    lambda r: "%d.%d" % (r.randint(1, 99999), r.randint(1, 9)),
    lambda r: "%de0" % r.randint(1, 100000),
    lambda r: "%dE+0" % r.randint(1, 100000),
    lambda r: r.choice(["true", "false", "null", '"%d"' % r.randint(1, 100000), "[%d]" % r.randint(1, 100000)]),
]
for index in range(56):
    days = [str(rng.choice([0, rng.randint(1, 1440)])) for _ in range(7)]
    if index % 2 == 0:
        position = rng.randrange(7)
        text = rng.choice(BAD_DAY_TEXT)(rng)
        REFUSED.append((f"generated week {index}, day {position + 1} at {text}",
                        week(days, rate=str(rng.randint(1, 100000)), day=position, value=text)))
    else:
        text = rng.choice(BAD_RATE_TEXT)(rng)
        REFUSED.append((f"generated week {index}, rate {text}", week(days, rate=text)))

problems = []
for (name, raw), (status, body) in zip(REFUSED, call_all(call, [raw for _, raw in REFUSED], raw=True)):
    if status != 2 or body is not None:
        problems.append(f"{name}: expected status 2 and no output, got status {status} and {body!r}")

# The example in C3, as written there: exit status 2 and nothing at all on standard output.
C3_EXAMPLE = '{"minutes": [480, -30, 0, 0, 0, 0, 0], "rate_cents": 1500}'
try:
    done = subprocess.run([PATH], input=C3_EXAMPLE, capture_output=True, text=True, timeout=10)
    if done.returncode != 2 or done.stdout != "":
        problems.append(f"the example in C3 must exit 2 with nothing on standard output, "
                        f"got status {done.returncode} and {done.stdout[:80]!r}")
except subprocess.TimeoutExpired:
    problems.append("the example in C3 timed out")

# The edges of the valid ranges are still paid.
PAID = [
    week(["0", "0", "0", "0", "0", "0", "0"], rate="1"),
    week(["1440", "0", "0", "0", "0", "0", "0"], rate="100000"),
    week(["0", "0", "0", "1440", "0", "0", "1440"], rate="1"),
    week(["1440", "1440", "1440", "1440", "1440", "1440", "1440"], rate="100000"),
    week(["1", "1439", "0", "1", "0", "1440", "0"], rate="99999"),
    week(rate="2"),
    week(rate="1"),
    week(rate="100000"),
]
for raw, (status, body) in zip(PAID, call_all(call, PAID, raw=True)):
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{raw}: a valid request must be paid with status 0, got status {status} and {body!r}")

finish(problems, f"refusals ok: {len(REFUSED)} invalid requests and the C3 example refused, "
                 f"{len(PAID)} edge requests paid")
