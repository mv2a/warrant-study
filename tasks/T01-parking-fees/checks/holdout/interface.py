"""H6: the fee command's input and output follow C1, and refusals write only to standard error."""

import json
import random
import subprocess

from _cmd import PATH, call, finish
from _oracle import FIELDS, request, stay_minutes

rng = random.Random(60606)
problems = []
requests = [request(0, 0), request(0, 10079, True), request(10079, 0), request(1560, 1561)]
requests += [request(rng.randint(0, 10079), rng.randint(0, 10079), rng.random() < 0.5) for _ in range(36)]
for req in requests:
    status, body = call(req)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{req}: expected status 0 and one JSON object, got status {status} and {body!r}")
        continue
    bad = [f for f in FIELDS if type(body.get(f)) is not int]
    if bad:
        problems.append(f"{req}: missing or non-integer field(s) {', '.join(bad)} in {body}")
        continue
    if body["minutes"] != stay_minutes(req["entry"], req["exit"]):
        problems.append(f"{req}: expected minutes {stay_minutes(req['entry'], req['exit'])}, got {body['minutes']}")
    parts = body["time_cents"] + body["overnight_cents"] + body["lost_ticket_cents"]
    if body["total_cents"] != parts or min(body[f] for f in FIELDS) < 0:
        problems.append(f"{req}: total_cents must be the sum of the three non-negative charges, got {body}")

for raw in ("not json", '{"entry": 4710, "exit": 4800}', '{"entry": 600, "exit": 99999, "lost_ticket": false}'):
    done = subprocess.run([PATH], input=raw, capture_output=True, text=True, timeout=10)
    if done.returncode != 2 or done.stdout.strip() or not done.stderr.strip():
        problems.append(f"{raw!r}: expected status 2, empty standard output and a reason on standard error, "
                        f"got status {done.returncode}, stdout {done.stdout.strip()[:60]!r}")

one = subprocess.run([PATH], input=json.dumps(request(600, 700)), capture_output=True, text=True, timeout=10)
try:
    json.loads(one.stdout)
except ValueError:
    problems.append(f"standard output must hold exactly one JSON object, got {one.stdout[:80]!r}")

finish(problems, f"interface ok: {len(requests)} valid requests and 3 refusals")
