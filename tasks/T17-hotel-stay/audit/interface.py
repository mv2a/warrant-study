"""X-C1: the command's interface: input, output fields and types, exit status, refusals."""

import json

from _audit import DAYS, FIELDS, call_all, priced, run_bytes, show
from _cmd import finish

problems = []


def parse_one_object(stdout):
    """The whole of standard output must be exactly one JSON object (surrounding whitespace allowed)."""
    try:
        value = json.loads(stdout)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


# 1. Valid requests, including every weekday name and the edges of the valid ranges.
# (Short stays over a Saturday are left to X4, so this check does not depend on that rule.)
valid = [{"check_in": day, "nights": 5, "rate_cents": 10300 + 11 * i} for i, day in enumerate(DAYS)]
valid += [
    {"check_in": "mon", "nights": 1, "rate_cents": 1},
    {"check_in": "tue", "nights": 1, "rate_cents": 18777},
    {"check_in": "sun", "nights": 30, "rate_cents": 1},
    {"check_in": "fri", "nights": 30, "rate_cents": 21999},
    {"check_in": "wed", "nights": 17, "rate_cents": 250000000},
]
for req in valid:
    status, out, _ = run_bytes(json.dumps(req).encode())
    body = parse_one_object(out)
    if status != 0:
        problems.append(f"{show(req)}: a valid request should exit 0, got {status}")
    elif body is None:
        problems.append(f"{show(req)}: standard output should be exactly one JSON object, got {out[:80]!r}")
    elif set(body) != set(FIELDS):
        problems.append(f"{show(req)}: expected exactly the fields {sorted(FIELDS)}, got {sorted(body)}")
    elif not all(type(body[f]) is int for f in FIELDS):
        problems.append(f"{show(req)}: every amount should be a JSON integer, got {body!r}")

# 2. Other fields are ignored, and key order and layout of the input do not matter.
base = {"check_in": "tue", "nights": 9, "rate_cents": 13333}
variants = [
    {**base, "guests": 2},
    {**base, "room_cents": 1, "discount_cents": 500, "tax_cents": 0, "total_cents": 7},
    {**base, "rate": 1, "night": 1, "checkin": "sat", "Check_in": "sat", "NIGHTS": 2},
    {**base, "notes": None, "meta": {"nights": 30, "list": [1, "x", True]}},
    {**base, "weekend": True, "discount": 0.5, "currency": "EUR"},
    {"zzz": "last", "rate_cents": 13333, "nights": 9, "check_in": "tue", "aaa": [None]},
]
texts = [json.dumps(base)] + [json.dumps(v) for v in variants]
texts.append(json.dumps(base, indent=4) + "\n\n")
texts.append('\n  {  "rate_cents" : 13333 ,\n"check_in":"tue",\t"nights":9 }  \n')
results = call_all(texts, raw=True)
reference_status, reference_body = results[0]
if reference_status != 0 or not isinstance(reference_body, dict):
    problems.append(f"{show(base)}: should be priced, got status {reference_status} and {reference_body!r}")
else:
    for text, (status, body) in zip(texts[1:], results[1:]):
        if status != 0 or body != reference_body:
            problems.append(f"input {text.strip()[:90]!r} should be priced like {show(base)} "
                            f"({reference_body}), got status {status} and {body!r}")

# 3. Refused requests: exit status 2, nothing on standard output, a reason on standard error.
# Whether each of these is refused at all is checked by X4 and X9; here, a request that the
# command prices instead of refusing is skipped, and every refusal must have this form.
refusals = [
    json.dumps({"check_in": "sat", "nights": 1, "rate_cents": 15000}),
    json.dumps({"check_in": "fri", "nights": 2, "rate_cents": 15000}),
    json.dumps({"check_in": "mon", "nights": 31, "rate_cents": 15000}),
    json.dumps({"check_in": "mon", "nights": 4, "rate_cents": 0}),
    json.dumps({"check_in": "Mon", "nights": 4, "rate_cents": 15000}),
    json.dumps({"check_in": "mon", "rate_cents": 15000}),
    "[1, 2, 3]",
    "not json at all {",
]
for text in refusals:
    status, out, err = run_bytes(text.encode())
    if status == 0 and priced(parse_one_object(out)):
        continue
    if status != 2:
        problems.append(f"refusal of {text[:70]!r}: expected exit status 2, got {status}")
    if out.strip():
        problems.append(f"refusal of {text[:70]!r}: standard output should be empty, got {out[:60]!r}")
    if not err.strip():
        problems.append(f"refusal of {text[:70]!r}: standard error should say why, but it was empty")

finish(problems, f"interface ok: {len(valid)} valid requests, {len(texts) - 1} input variants, {len(refusals)} refusals")
