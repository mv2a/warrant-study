"""X-S1..S4: the example stays written in the intent, one scenario per run.

Each request is sent in three layouts (compact, indented, keys in reverse order); all are the
same JSON object, so each must give the same answer.
"""

import json
import sys

from _audit import amount_problems, call_all, priced
from _cmd import finish

SCENARIOS = {
    "S1": ({"check_in": "wed", "nights": 2, "rate_cents": 12000},
           {"room_cents": 24000, "discount_cents": 0, "tax_cents": 550, "total_cents": 24550}),
    "S2": ({"check_in": "thu", "nights": 3, "rate_cents": 12000},
           {"room_cents": 42000, "discount_cents": 0, "tax_cents": 825, "total_cents": 42825}),
    "S3": ({"check_in": "sat", "nights": 2, "rate_cents": 12000}, None),
    "S4": ({"check_in": "sun", "nights": 14, "rate_cents": 8000},
           {"room_cents": 120000, "discount_cents": 18000, "tax_cents": 2750, "total_cents": 104750}),
}

scenario = sys.argv[1]
req, want = SCENARIOS[scenario]
texts = [json.dumps(req, separators=(",", ":")),
         json.dumps(req, indent=2) + "\n",
         json.dumps(dict(reversed(list(req.items()))))]
problems = []
for text, (status, body) in zip(texts, call_all(texts, raw=True)):
    if want is None:
        if status != 2 or priced(body):
            problems.append(f"{scenario}: {text!r} should be refused with status 2 and no price, "
                            f"got status {status} and {body!r}")
    elif status != 0 or amount_problems(body, want) is not None:
        problems.append(f"{scenario}: {text!r} should be priced {want}, got {body!r} (status {status})")

finish(problems, f"{scenario} ok in {len(texts)} layouts")
