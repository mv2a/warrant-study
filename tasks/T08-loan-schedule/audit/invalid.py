"""X7 (C3): invalid requests are refused with status 2 and nothing on standard output, never scheduled;
requests exactly at the edges of the allowed ranges are scheduled."""

import json

from _batch import raw_all
from _cmd import finish

GOOD = {"principal_cents": 314159, "annual_rate_bp": 725, "months": 60}


def with_field(name, literal):
    """The good request with one field's value written as the given JSON text."""
    parts = [f'"{k}": {literal if k == name else json.dumps(v)}' for k, v in GOOD.items()]
    return "{" + ", ".join(parts) + "}"


def without(name):
    return json.dumps({k: v for k, v in GOOD.items() if k != name})


REFUSED = [
    # text that is not JSON
    ("empty input", ""),
    ("blank input", "   \n"),
    ("plain words", "please schedule my loan"),
    ("truncated object", '{"principal_cents": 314159, "annual_rate_bp": 725, "months": 60'),
    ("single-quoted keys", "{'principal_cents': 314159, 'annual_rate_bp': 725, 'months': 60}"),
    ("a leading plus sign", with_field("months", "+60")),
    ("a leading zero", with_field("months", "060")),
    ("two objects", json.dumps(GOOD) + json.dumps(GOOD)),
    ("a trailing comma", '{"principal_cents": 314159, "annual_rate_bp": 725, "months": 60,}'),
    # JSON that is not an object
    ("a list", json.dumps([GOOD])),
    ("a list of numbers", "[314159, 725, 60]"),
    ("a string", json.dumps(json.dumps(GOOD))),
    ("a number", "314159"),
    ("null", "null"),
    ("true", "true"),
    # missing fields
    ("an empty object", "{}"),
    ("no principal_cents", without("principal_cents")),
    ("no annual_rate_bp", without("annual_rate_bp")),
    ("no months", without("months")),
    ("misspelled months", json.dumps({"principal_cents": 314159, "annual_rate_bp": 725, "month": 60})),
]
for field in ("principal_cents", "annual_rate_bp", "months"):
    whole = GOOD[field]
    for label, literal in (
        ("true", "true"), ("false", "false"), ("null", "null"), ("a string", json.dumps(str(whole))),
        ("a fraction", f"{whole}.5"), ("a whole value written with .0", f"{whole}.0"),
        ("an exponent", f"{whole}e0"), ("a list", f"[{whole}]"), ("an object", f'{{"cents": {whole}}}'),
        ("NaN", "NaN"),
    ):
        REFUSED.append((f"{field} as {label}", with_field(field, literal)))

# Out of range, just past each edge and far past it.
for field, literal in (
    ("principal_cents", "0"), ("principal_cents", "-1"), ("principal_cents", "-314159"),
    ("principal_cents", "1000000001"), ("principal_cents", "100000000000000000000000"),
    ("annual_rate_bp", "-1"), ("annual_rate_bp", "-725"), ("annual_rate_bp", "5001"),
    ("annual_rate_bp", "120000"),
    ("months", "0"), ("months", "-1"), ("months", "481"), ("months", "1200"),
):
    REFUSED.append((f"{field} of {literal}", with_field(field, literal)))

ACCEPTED = [
    ("principal_cents of 1", with_field("principal_cents", "1")),
    ("principal_cents of 1000000000", with_field("principal_cents", "1000000000")),
    ("annual_rate_bp of 0", with_field("annual_rate_bp", "0")),
    ("annual_rate_bp of 5000", with_field("annual_rate_bp", "5000")),
    ("months of 1", with_field("months", "1")),
    ("months of 480", with_field("months", "480")),
    ("every field at its top edge", '{"principal_cents": 1000000000, "annual_rate_bp": 5000, "months": 480}'),
    ("every field at its bottom edge", '{"principal_cents": 1, "annual_rate_bp": 0, "months": 1}'),
]

problems = []
results = raw_all([text for _, text in REFUSED + ACCEPTED])
for (label, text), (status, out) in zip(REFUSED, results):
    if status != 2 or out != "":
        problems.append(f"{label} ({text!r}) must be refused with status 2 and no output, "
                        f"got status {status} and {out!r}"[:300])
for (label, text), (status, out) in zip(ACCEPTED, results[len(REFUSED):]):
    if status != 0 or not (out or "").strip():
        problems.append(f"{label} is allowed and must be scheduled, got status {status} and {out!r}"[:300])

finish(problems, f"refusals ok: {len(REFUSED)} invalid requests refused, {len(ACCEPTED)} edge requests scheduled")
