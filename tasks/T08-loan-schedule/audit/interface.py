"""X1 (C1): the command's interface: request and response fields, whole numbers, month numbering,
fields beyond the three being ignored, exit statuses, and a refusal that writes nothing at all on standard output."""

import json
import random

from _batch import call_all, raw_all
from _cmd import finish
from _loan import req, well_formed

problems = []
rng = random.Random(90817)

valid = [req(1, 0, 1), req(1000000000, 5000, 480), req(31, 4999, 2), req(2500001, 17, 360)]
for _ in range(24):
    size = rng.choice([(1, 999), (1000, 999999), (1000000, 1000000000)])
    valid.append(req(rng.randint(*size), rng.choice([0, rng.randint(1, 5000)]), rng.randint(1, 480)))

for request, (status, body) in zip(valid, call_all(valid)):
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not well_formed(body):
        problems.append(f"{request}: response is not one object with exactly payment_cents, total_interest_cents "
                        f"and rows of whole-number month/payment/interest/principal/balance numbered from 1: {body!r}"[:300])

# The same request, written as JSON in different ways, must be read the same way.
base = req(4321987, 1234, 37)
texts = [
    json.dumps(base),
    '{"months":37,"annual_rate_bp":1234,"principal_cents":4321987}',
    '\n  {\n    "annual_rate_bp" : 1234 ,\n    "months" : 37 ,\n    "principal_cents" : 4321987\n  }\n\n',
    '\t{"principal_cents": 4321987, "months": 37, "annual_rate_bp": 1234}   ',
]
outputs = raw_all(texts)
first = None
for text, (status, out) in zip(texts, outputs):
    try:
        body = json.loads(out) if out else None
    except json.JSONDecodeError:
        body = None
    if status != 0 or not well_formed(body):
        problems.append(f"request written as {text!r}: expected status 0 and one schedule object, "
                        f"got status {status} and {out!r}"[:300])
        continue
    if first is None:
        first = body
    elif body != first:
        problems.append(f"request written as {text!r} got a different schedule from the same loan written compactly")

# Any field other than the three is ignored: the loan is scheduled as if the field were not there,
# even when the field is named like a response field or looks like another way to give the rate or term.
LOAN = '"principal_cents": 2718281, "annual_rate_bp": 314, "months": 120'
extras = [
    "{" + LOAN + ', "purpose": "boat"}',
    '{"autopay": true, ' + LOAN + "}",
    "{" + LOAN + ', "annual_rate_percent": 3.14, "term_years": 10}',
    "{" + LOAN + ', "payment_cents": 1, "total_interest_cents": 0, "rows": []}',
    '{"schedule": {"months": 1, "principal_cents": 5}, ' + LOAN + ', "months_label": "ten years", "cosigner": null}',
]
outputs = raw_all(["{" + LOAN + "}"] + extras)
plain_status, plain_out = outputs[0]
try:
    plain = json.loads(plain_out) if plain_out else None
except json.JSONDecodeError:
    plain = None
if plain_status != 0 or not well_formed(plain):
    problems.append(f"{{{LOAN}}}: expected status 0 and one schedule object, got status {plain_status} and {plain_out!r}"[:300])
else:
    for text, (status, out) in zip(extras, outputs[1:]):
        try:
            body = json.loads(out) if out else None
        except json.JSONDecodeError:
            body = None
        if status != 0 or body != plain:
            problems.append(f"{text!r} carries fields beyond the three and must get the same schedule as the loan "
                            f"without them, got status {status} and {out!r}"[:300])

# Refusals: status 2 and nothing whatsoever on standard output.
refusals = ["not json at all", "{}", "[4321987, 1234, 37]"]
for text, (status, out) in zip(refusals, raw_all(refusals)):
    if status != 2 or out != "":
        problems.append(f"{text!r} must be refused with status 2 and an empty standard output, "
                        f"got status {status} and {out!r}"[:300])

finish(problems, f"interface ok: {len(valid)} loans, {len(texts)} spellings, {len(extras)} with extra fields, "
                 f"{len(refusals)} refusals")
