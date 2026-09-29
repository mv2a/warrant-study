"""X9-X11 (S1, S2, S3): the intent's example logs get exactly the answer the intent gives.

Usage: python3 scenarios.py S1|S2|S3. Each scenario is sent as three JSON texts that encode
the same object (compact, pretty-printed with keys in another order, and with the client
names written as \\u escapes), and must get the intent's exact answer every time.
"""

import json
import sys

from _cmd import call, finish
from _model import A, R, short

SCENARIOS = {
    "S1": (3, 2, [("alice", t) for t in (0, 0, 0, 0, 499, 500, 1000, 1000)],
           {"decisions": [A, A, A, R, R, A, A, R], "clients": {"alice": {"accepted": 5, "rejected": 3}}}),
    "S2": (1, 1, [("a", 0), ("b", 0), ("a", 0), ("b", 600), ("a", 1000), ("b", 1000)],
           {"decisions": [A, A, R, R, A, A],
            "clients": {"a": {"accepted": 2, "rejected": 1}, "b": {"accepted": 2, "rejected": 1}}}),
    "S3": (2, 1, [("carol", t) for t in (0, 0, 0, 60000, 60000, 60000)],
           {"decisions": [A, A, R, A, A, R], "clients": {"carol": {"accepted": 4, "rejected": 2}}}),
}

sid = sys.argv[1] if len(sys.argv) > 1 else ""
if sid not in SCENARIOS:
    sys.exit(f"usage: scenarios.py {'|'.join(SCENARIOS)}")
burst, rate, log, expected = SCENARIOS[sid]

compact = json.dumps({"burst": burst, "rate": rate, "requests": [{"client": c, "at": t} for c, t in log]},
                     separators=(",", ":"))
reordered = json.dumps({"requests": [{"at": t, "client": c} for c, t in log], "rate": rate, "burst": burst},
                       indent=2) + "\n"
escaped_entries = ", ".join('{"client": "' + "".join(f"\\u{ord(ch):04x}" for ch in c) + f'", "at": {t}}}'
                            for c, t in log)
escaped = f'{{"burst": {burst}, "rate": {rate}, "requests": [{escaped_entries}]}}'

problems = []
for label, raw in (("compact", compact), ("pretty-printed, keys reordered", reordered),
                   ("client names written as \\u escapes", escaped)):
    status, body = call(raw=raw)
    if status != 0 or body != expected:
        problems.append(f"{sid} ({label}): expected status 0 and {short(expected, 120)}, "
                        f"got status {status} and {short(body, 120)}")

finish(problems, f"{sid} ok: exact answer in 3 encodings")
