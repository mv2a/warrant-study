"""X10-X12 (S1, S2, S3): the example requests in the intent get exactly the responses the
intent gives, whether sent compactly or pretty-printed with the keys in another order.
Usage: python3 scenario.py S1|S2|S3"""

import json
import sys

from _cmd import call, finish

SCENARIOS = {
    "S1": (
        '{"diners": [{"name": "Ana", "pays": "own"}, {"name": "Ben", "pays": "own"}], "items": [{"diner": "Ana", "price_cents": 1200}, {"diner": "Ben", "price_cents": 2500}, {"diner": "Ana", "price_cents": 300}], "tip_percent": 20}',
        {"subtotal_cents": 4000, "tip_cents": 800, "total_cents": 4800, "shares": {"Ana": 1800, "Ben": 3000}},
    ),
    "S2": (
        '{"diners": [{"name": "Ana", "pays": "share"}, {"name": "Ben", "pays": "share"}, {"name": "Cy", "pays": "share"}], "items": [{"diner": "Ana", "price_cents": 1234}, {"diner": "Ben", "price_cents": 2000}, {"diner": "Cy", "price_cents": 1500}], "tip_percent": 10}',
        {"subtotal_cents": 4734, "tip_cents": 473, "total_cents": 5207,
         "shares": {"Ana": 1736, "Ben": 1736, "Cy": 1735}},
    ),
    "S3": (
        '{"diners": [{"name": "Ana", "pays": "share"}, {"name": "Ben", "pays": "share"}, {"name": "Cy", "pays": "own"}, {"name": "Dee", "pays": "share"}], "items": [{"diner": "Ana", "price_cents": 1600}, {"diner": "Cy", "price_cents": 2150}, {"diner": "Ben", "price_cents": 900}], "tip_percent": 18}',
        {"subtotal_cents": 4650, "tip_cents": 837, "total_cents": 5487,
         "shares": {"Ana": 984, "Ben": 983, "Cy": 2537, "Dee": 983}},
    ),
}


def reversed_keys(value):
    """The same JSON value with every object's keys in reverse order (lists keep their order)."""
    if isinstance(value, dict):
        return {k: reversed_keys(value[k]) for k in reversed(list(value))}
    if isinstance(value, list):
        return [reversed_keys(v) for v in value]
    return value


scenario = sys.argv[1] if len(sys.argv) > 1 else ""
if scenario not in SCENARIOS:
    sys.exit(f"usage: scenario.py {'|'.join(SCENARIOS)}")
text, want = SCENARIOS[scenario]
variants = [("as written in the intent", text),
            ("pretty-printed, keys reversed", json.dumps(reversed_keys(json.loads(text)), indent=2))]
problems = []
for label, raw in variants:
    status, body = call(raw=raw)
    if status != 0 or body != want:
        problems.append(f"{scenario} {label}: expected {want}, got {body!r} (status {status})")

finish(problems, f"{scenario} ok: {len(variants)} forms of the request")
