"""X-C1: the fee command's interface.

Part A: seeded random valid requests with the exit later than the entry, plus the edge
values 0 and 10079, exit with status 0 and write exactly one JSON object whose keys are
exactly the five fields, each a JSON integer; minutes is exit minus entry and total_cents
is the sum of the three charges. Stays into the following week and zero-minute stays
belong to C2 and are left to it.
Part B: the same request written with other key orders, spacing, line breaks or an escaped
key name is still a JSON object and gets the same answer as its compact form.
Part C: a refused request exits with status 2, writes nothing on standard output and
says something on standard error.
"""

import json
import random

from _audit import FIELDS, WEEK, request, run_many, run_many_raw, show
from _cmd import finish

rng = random.Random(40_091)
valid = [request(0, WEEK - 1, True), request(0, WEEK - 1, False), request(0, 1, True),
         request(WEEK - 2, WEEK - 1, False), request(0, 16, False), request(4321, 8765, True)]
while len(valid) < 120:
    entry, exit = rng.randint(0, WEEK - 1), rng.randint(0, WEEK - 1)
    if exit > entry:
        valid.append(request(entry, exit, rng.random() < 0.3))

variants = [
    (request(3725, 3990, False), [
        '{"lost_ticket": false, "exit": 3990, "entry": 3725}',
        '{"entry":3725,"exit":3990,"lost_ticket":false}',
        '\n  {\n    "entry": 3725,\n    "exit": 3990,\n    "lost_ticket": false\n  }\n\n',
        '\t{"entry": 3725,\r\n "exit": 3990,\r\n "lost_ticket": false}\r\n',
        '{"\\u0065ntry": 3725, "exit": 3990, "lost_ticket": false}',
    ]),
    (request(6600, 9700, True), [
        '{"exit":9700,"lost_ticket":true,"entry":6600}\n',
        '   {"lost_ticket" : true , "entry" : 6600 , "exit" : 9700}   ',
    ]),
]
refusals = ["no ticket here", "{}", '{"entry": 3725, "exit": 3990}']

requests = valid + [base for base, _ in variants]
results = run_many(requests)
raw_texts = [text for _, texts in variants for text in texts]
raw_results = run_many_raw(raw_texts + refusals)

problems = []


def shape(req_text, status, body):
    if status != 0:
        return f"{req_text}: expected status 0, got {status} and {body!r}"
    if not isinstance(body, dict):
        return f"{req_text}: expected one JSON object on standard output, got {body!r}"
    if set(body) != set(FIELDS):
        return f"{req_text}: expected exactly the fields {', '.join(FIELDS)}, got {sorted(body)}"
    bad = [f for f in FIELDS if type(body[f]) is not int]
    if bad:
        return f"{req_text}: field(s) {', '.join(bad)} are not JSON integers in {body}"
    parts = body["time_cents"] + body["overnight_cents"] + body["lost_ticket_cents"]
    if body["total_cents"] != parts:
        return f"{req_text}: total_cents {body['total_cents']} is not the sum of the three charges ({parts})"
    return None


for req, (status, body) in zip(requests, results):
    problem = shape(show(req), status, body)
    if problem:
        problems.append(problem)
    elif body["minutes"] != req["exit"] - req["entry"]:
        problems.append(f"{show(req)}: expected minutes {req['exit'] - req['entry']}, got {body['minutes']}")

at = 0
base_results = results[len(valid):]
for (base, texts), (_, base_body) in zip(variants, base_results):
    for text in texts:
        status, out, _ = raw_results[at]
        at += 1
        try:
            body = json.loads(out)
        except ValueError:
            body = out.strip() or None
        if status != 0 or body != base_body:
            problems.append(f"{text!r}: expected the same answer as {show(base)} ({base_body!r}), "
                            f"got status {status} and {body!r}")
for text in refusals:
    status, out, err = raw_results[at]
    at += 1
    if status != 2 or out.strip() or not err.strip():
        problems.append(f"{text!r}: expected status 2, nothing on standard output and a message on standard error, "
                        f"got status {status}, stdout {out.strip()[:60]!r}, stderr {err.strip()[:60]!r}")

finish(problems, f"C1 ok: {len(requests)} valid requests, {len(raw_texts)} rewritten requests and "
                 f"{len(refusals)} refusals follow the interface")
