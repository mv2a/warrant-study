"""X-C3: invalid requests are refused with exit status 2, never priced.

The exact refusal format (empty standard output, a reason on standard error) is X5's concern.
"""

import json

from _audit import call_all, posix_locale_env, priced, run_bytes
from _cmd import finish

BASE = {"check_in": "mon", "nights": 5, "rate_cents": 13750}


def with_field(field, literal):
    """The base request with one field's value replaced by a raw JSON (or near-JSON) literal."""
    parts = [f'"{k}": {literal if k == field else json.dumps(v)}' for k, v in BASE.items()]
    return "{" + ", ".join(parts) + "}"


def without(field):
    return json.dumps({k: v for k, v in BASE.items() if k != field})


texts = [
    # not a JSON object
    "", "   \n", "null", "true", "5", '"mon 5 13750"', "[]",
    "[" + json.dumps(BASE) + "]",
    json.dumps(BASE)[:-1],
    "{'check_in': 'mon', 'nights': 5, 'rate_cents': 13750}",
    json.dumps(BASE) + ' {"check_in": "tue"}',
    json.dumps(BASE) + " trailing words",
    "check_in=mon&nights=5&rate_cents=13750",
    # missing fields
    "{}", without("check_in"), without("nights"), without("rate_cents"),
    json.dumps({"checkin": "mon", "nights": 5, "rate_cents": 13750}),
    json.dumps({"check_in": "mon", "night": 5, "rate_cents": 13750}),
    json.dumps({"check_in": "mon", "nights": 5, "rate": 13750}),
    json.dumps({"CHECK_IN": "mon", "Nights": 5, "Rate_Cents": 13750}),
]
# check-in days other than the seven lowercase names
for literal in ('"Mon"', '"MON"', '"monday"', '"Monday"', '"Sat"', '"SUN"', '"thurs"', '"tues"',
                '" mon"', '"mon "', '"mon\\n"', '""', '"m"', '"mo"', '"weekday"', '"1"',
                "0", "1", "true", "null", '["mon"]', '{"day": "mon"}'):
    texts.append(with_field("check_in", literal))
# night counts that are not JSON integers or are outside 1 to 30
for literal in ("true", "false", "null", "2.5", "2.0", "5.0", "1.0", "30.0", "1e1", "5e0", '"3"', '"5"',
                "[5]", '{"n": 5}', "0", "-0", "-1", "-7", "31", "32", "60", "100000000000000000000",
                "NaN", "Infinity"):
    texts.append(with_field("nights", literal))
# rates that are not JSON integers or are below 1 cent
for literal in ("true", "false", "null", "2.5", "2.0", "13750.0", "1.0", "1e4", "1.5e3", "0.9",
                '"13750"', '"1"', "[13750]", '{"cents": 13750}', "0", "-0", "-1", "-13750",
                "NaN", "Infinity", "-Infinity"):
    texts.append(with_field("rate_cents", literal))

problems = []
for text, (status, body) in zip(texts, call_all(texts, raw=True)):
    if status != 2 or priced(body):
        problems.append(f"{text[:80]!r}: expected refusal with status 2 and no price, got status {status} and {body!r}")

# bytes that are not text at all, sent under the POSIX locale so the verdict does not depend on the host
status, out, _ = run_bytes(b'\xff\xfe{"check_in": "mon", "nights": 5, "rate_cents": 13750}',
                           env=posix_locale_env())
if status != 2 or "total_cents" in out:
    problems.append(f"input that is not UTF-8 text: expected refusal with status 2 and no price, got status {status} and {out[:60]!r}")

finish(problems, f"invalid requests refused: {len(texts) + 1} kinds")
