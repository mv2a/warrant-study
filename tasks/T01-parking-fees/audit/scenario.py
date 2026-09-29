"""X-S1 to X-S4: one concrete stay from intent.md, sent as written there, gets exactly the answer written there.

Usage: python3 scenario.py S1 (or S2, S3, S4). The request text is sent exactly as the
intent writes it, and the answer must exit with status 0 and have the intent's value in
each of the five fields. Integer typing, extra fields and leaving out a zero field are
C1's contract, checked by C1 (a missing field counts as 0 here).
"""

import sys

from _audit import FIELDS, field
from _cmd import call, finish

SCENARIOS = {
    "S1": ('{"entry": 1990, "exit": 2140, "lost_ticket": false}',
           {"minutes": 150, "time_cents": 750, "overnight_cents": 0, "lost_ticket_cents": 0, "total_cents": 750}),
    "S2": ('{"entry": 6480, "exit": 6495, "lost_ticket": true}',
           {"minutes": 15, "time_cents": 0, "overnight_cents": 0, "lost_ticket_cents": 2500, "total_cents": 2500}),
    "S3": ('{"entry": 9840, "exit": 510, "lost_ticket": false}',
           {"minutes": 750, "time_cents": 1600, "overnight_cents": 600, "lost_ticket_cents": 0, "total_cents": 2200}),
    "S4": ('{"entry": 3360, "exit": 6390, "lost_ticket": false}',
           {"minutes": 3030, "time_cents": 3950, "overnight_cents": 1200, "lost_ticket_cents": 0, "total_cents": 5150}),
}

if len(sys.argv) != 2 or sys.argv[1] not in SCENARIOS:
    sys.exit("usage: scenario.py S1|S2|S3|S4")
name = sys.argv[1]
text, want = SCENARIOS[name]
status, body = call(raw=text)
problems = []
if any(field((status, body), f) != want[f] for f in FIELDS):
    problems.append(f"{name}: expected {want}, got status {status} and {body!r}")
finish(problems, f"{name} ok")
