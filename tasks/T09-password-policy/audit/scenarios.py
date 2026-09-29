"""X10-X13 (S1-S4): each scenario's exact request, sent as JSON text written three ways.

Usage: python3 scenarios.py S1|S2|S3|S4
"""

import json
import sys

from _audit import finish, run_bytes_all, short

SCENARIOS = {
    "S1": ({"password": "Bell-Book-77", "username": "rebel", "banned": ["books"]},
           {"ok": True, "violations": []}),
    "S2": ({"password": "maria.silva2024", "username": "MSILVA", "banned": ["2024"]},
           {"ok": False, "violations": ["banned", "username"]}),
    "S3": ({"password": "kim111", "username": "kim", "banned": ["11"]},
           {"ok": False, "violations": ["banned", "classes", "repeat", "too_short"]}),
    "S4": ({"password": "Harbor-Lamp-42", "username": "ana smith", "banned": []},
           None),  # refused: exit status 2 and nothing on standard output
}

sid = sys.argv[1]
request, expected = SCENARIOS[sid]
forms = [
    ("as written in the intent", json.dumps(request)),
    ("keys reversed, no spaces", json.dumps(dict(reversed(list(request.items()))), separators=(",", ":"))),
    ("indented, with a trailing newline", json.dumps(request, indent=3) + "\n"),
]

problems = []
for (form, text), (status, out) in zip(forms, run_bytes_all([t.encode("utf-8") for _, t in forms])):
    if expected is None:
        if status != 2 or out != b"":
            problems.append(f"{sid} {form}: expected a refusal (status 2, no output), got status {status} "
                            f"and {short(out.decode('utf-8', 'replace'), 60)}")
        continue
    try:
        body = json.loads(out.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        body = out.decode("utf-8", "replace").strip() or None
    if status != 0 or body != expected:
        problems.append(f"{sid} {form}: expected status 0 and {json.dumps(expected)}, "
                        f"got status {status} and {short(body)}")

finish(problems, f"{sid} ok: the request gives the intended answer in {len(forms)} JSON layouts")
