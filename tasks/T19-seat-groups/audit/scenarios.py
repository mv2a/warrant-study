"""S1, S2, S3: the intent's example requests get exit status 0 and exactly the responses the
intent gives. Usage: scenarios.py S1|S2|S3

Each request is sent twice: as compact JSON, and as the same JSON object written with
newlines, indentation and its keys in reverse order (still the same request)."""

import json
import sys

from _audit import call_all
from _cmd import finish

SCENARIOS = {
    "S1": (
        {"rows": [6, 6], "groups": [{"id": "Ruiz", "size": 4}, {"id": "Chen", "size": 3}, {"id": "Patel", "size": 2}]},
        {
            "seated": [
                {"id": "Ruiz", "seats": ["A1", "A2", "A3", "A4"]},
                {"id": "Chen", "seats": ["B1", "B2", "B3"]},
                {"id": "Patel", "seats": ["A5", "A6"]},
            ],
            "refused": [],
            "free": 3,
        },
    ),
    "S2": (
        {
            "rows": [5, 5],
            "blocked": ["A3", "B3"],
            "groups": [{"id": "Novak", "size": 3}, {"id": "Okafor", "size": 2}, {"id": "Lind", "size": 2}],
        },
        {
            "seated": [{"id": "Okafor", "seats": ["A1", "A2"]}, {"id": "Lind", "seats": ["A4", "A5"]}],
            "refused": [{"id": "Novak", "reason": "not_together"}],
            "free": 4,
        },
    ),
    "S3": (
        {
            "rows": [4, 4],
            "groups": [
                {"id": "Ito", "size": 3},
                {"id": "Berg", "size": 3},
                {"id": "Kim", "size": 3},
                {"id": "Diaz", "size": 2, "may_split": True},
            ],
        },
        {
            "seated": [
                {"id": "Ito", "seats": ["A1", "A2", "A3"]},
                {"id": "Berg", "seats": ["B1", "B2", "B3"]},
                {"id": "Diaz", "seats": ["A4", "B4"]},
            ],
            "refused": [{"id": "Kim", "reason": "not_enough_seats"}],
            "free": 0,
        },
    ),
}


def reverse_keys(value):
    if isinstance(value, dict):
        return {k: reverse_keys(value[k]) for k in reversed(list(value))}
    if isinstance(value, list):
        return [reverse_keys(v) for v in value]
    return value


key = sys.argv[1]
request, want = SCENARIOS[key]
texts = {
    "compact": json.dumps(request, separators=(",", ":")),
    "reformatted": json.dumps(reverse_keys(request), indent=3) + "\n",
}
problems = []
for (form, text), (status, body) in zip(texts.items(), call_all(list(texts.values()))):
    if status != 0 or body != want:
        problems.append(f"{key} ({form}): expected status 0 and {json.dumps(want)}, got status {status} and {body!r}")

finish(problems, f"{key} ok")
