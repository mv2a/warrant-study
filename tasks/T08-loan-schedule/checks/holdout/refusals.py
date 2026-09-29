"""H7: invalid requests are refused with status 2 and nothing on standard output, never scheduled; the edges of
the valid range are accepted (C3)."""

import json

from _cmd import call, call_exact, finish
from _model import MAX_MONTHS, MAX_PRINCIPAL, MAX_RATE, is_schedule

GOOD = {"principal_cents": 250000, "annual_rate_bp": 725, "months": 36}


def with_field(field, value):
    request = dict(GOOD)
    request[field] = value
    return json.dumps(request)


def without(field):
    return json.dumps({k: v for k, v in GOOD.items() if k != field})


INVALID = [
    ("empty input", ""),
    ("text that is not JSON", "a loan of 2500 dollars"),
    ("JSON cut short", '{"principal_cents": 250000, "annual_rate_bp": 725,'),
    ("a list", "[250000, 725, 36]"),
    ("a string", '"250000"'),
    ("a number", "250000"),
    ("null", "null"),
]
for field in GOOD:
    INVALID.append((f"a missing {field}", without(field)))
    for label, value in (("true", True), ("false", False), ("null", None), ('"36"', "36"), ("12.5", 12.5),
                         ("12.0", 12.0), ("[36]", [36]), ("an object", {"value": 36})):
        INVALID.append((f"{field} of {label}", with_field(field, value)))
for field, value in (("principal_cents", 0), ("principal_cents", -1), ("principal_cents", -250000),
                     ("principal_cents", MAX_PRINCIPAL + 1), ("principal_cents", 10**12),
                     ("annual_rate_bp", -1), ("annual_rate_bp", -725), ("annual_rate_bp", MAX_RATE + 1),
                     ("annual_rate_bp", 100000), ("months", 0), ("months", -36), ("months", MAX_MONTHS + 1),
                     ("months", 1200)):
    INVALID.append((f"{field} of {value}", with_field(field, value)))

VALID = [
    {"principal_cents": 1, "annual_rate_bp": 725, "months": 36},
    {"principal_cents": MAX_PRINCIPAL, "annual_rate_bp": 725, "months": 36},
    {"principal_cents": 250000, "annual_rate_bp": 0, "months": 36},
    {"principal_cents": 250000, "annual_rate_bp": MAX_RATE, "months": 36},
    {"principal_cents": 250000, "annual_rate_bp": 725, "months": 1},
    {"principal_cents": 250000, "annual_rate_bp": 725, "months": MAX_MONTHS},
    {"principal_cents": 1, "annual_rate_bp": 0, "months": 1},
    {"principal_cents": MAX_PRINCIPAL, "annual_rate_bp": MAX_RATE, "months": MAX_MONTHS},
]

problems = []
for name, raw in INVALID:
    # A refusal (C1) exits 2 and writes nothing at all: not a schedule, not an error object, not even null.
    status, out = call_exact(raw=raw)
    if status != 2 or out != "":
        problems.append(f"{name}: expected a refusal with status 2 and nothing on standard output, "
                        f"got status {status} and {str(out)[:60]!r}")
for request in VALID:
    status, body = call(request)
    if status != 0 or not is_schedule(body):
        problems.append(f"{request} is valid and should be scheduled, got status {status}")

finish(problems, f"refusals ok: {len(INVALID)} invalid requests refused, {len(VALID)} edge requests accepted")
