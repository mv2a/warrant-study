"""X9 to X11 (S1, S2, S3): the intent's scenarios, each sent in three equivalent JSON forms.

Usage: python3 scenarios.py S1|S2|S3
"""

import json
import sys

from _audit import finish, raw_run_all, short

SCENARIOS = {
    "S1": ({"value": "12", "from": "ft", "to": "m", "places": 3}, {"value": "3.658", "unit": "m", "dimension": "length"}),
    "S2": ({"value": "2.5", "from": "lb", "to": "kg", "places": 4}, {"value": "1.1340", "unit": "kg", "dimension": "mass"}),
    "S3": ({"value": "3", "from": "kg", "to": "l", "places": 2}, None),  # refused
}

name = sys.argv[1]
req, wanted = SCENARIOS[name]
texts = [
    json.dumps(req),
    json.dumps(dict(reversed(list(req.items()))), indent=2) + "\n",
    json.dumps(req, separators=(",", ":")),
]
problems = []
for text, (status, out) in zip(texts, raw_run_all(texts)):
    label = f"{name} sent as {short(text, 60)}"
    if wanted is None:
        if status != 2 or out != "":
            problems.append(f"{label}: expected a refusal (status 2, nothing written), got status {status} and {short(out, 50)}")
        continue
    try:
        body = json.loads(out)
    except (TypeError, ValueError):
        body = out
    if status != 0 or body != wanted:
        problems.append(f"{label}: expected status 0 and {wanted}, got status {status} and {short(body, 70)}")

finish(problems, f"{name} ok: {len(texts)} forms of the request")
