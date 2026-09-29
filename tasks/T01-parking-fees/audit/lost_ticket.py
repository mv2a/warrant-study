"""X-G5: a lost ticket adds exactly $25.00, whatever the stay, not limited by the daily cap.

Each stay is sent twice, once with lost_ticket false and once with true. With false,
lost_ticket_cents must be 0; with true it must be 2500, the minutes, time charge and
overnight fee must be the same as without, and total_cents must be exactly 2500 more.
The stays include free stays of 0 to 15 minutes, capped stays, stays with nights, stays
into the following week, and seeded random stays anywhere in the week. Comparing the two
answers keeps this check independent of how the other charges are worked out. A stay the
command refuses both with and without a lost ticket, with the same status and no output,
is skipped (accepting the stay is C1's and C2's business), but at least 60 stays must be
answered (92 of them lie inside one week).
"""

import random

from _audit import WEEK, field, got, request, run_many, show
from _cmd import finish

rng = random.Random(18_845)
stays = []
for minutes in range(0, 16):
    for start in (rng.randint(0, WEEK - 1 - minutes), 120 - minutes // 2):
        stays.append((start, start + minutes))
stays += [(0, WEEK - 1), (1200, 2640), (300, 2000), (100, 3100), (2000, 2016),
          (9840, 510), (WEEK - 1, 0), (1, 0), (9000, 121), (7777, 7777)]
for _ in range(110):
    stays.append((rng.randint(0, WEEK - 1), rng.randint(0, WEEK - 1)))

requests = []
for e, x in stays:
    requests += [request(e, x, False), request(e, x, True)]
results = run_many(requests)

problems = []
SAME = ("minutes", "time_cents", "overnight_cents")
compared = 0
for i in range(0, len(requests), 2):
    kept, lost = results[i], results[i + 1]
    q_kept, q_lost = requests[i], requests[i + 1]
    if kept[0] != 0 and kept[1] is None and lost[0] == kept[0] and lost[1] is None:
        continue
    compared += 1
    if field(kept, "lost_ticket_cents") != 0:
        problems.append(f"{show(q_kept)}: expected lost_ticket_cents 0, got {got(kept, 'lost_ticket_cents')}")
        continue
    if field(lost, "lost_ticket_cents") != 2500:
        problems.append(f"{show(q_lost)}: expected lost_ticket_cents 2500, got {got(lost, 'lost_ticket_cents')}")
        continue
    changed = [f for f in SAME if field(kept, f) is None or field(kept, f) != field(lost, f)]
    if changed:
        problems.append(f"{show(q_lost)}: a lost ticket changed {', '.join(changed)}: {kept[1]!r} vs {lost[1]!r}")
        continue
    a, b = field(kept, "total_cents"), field(lost, "total_cents")
    if a is None or b is None or b != a + 2500:
        problems.append(f"{show(q_lost)}: expected total_cents 2500 more than {a}, got {b}")

if compared < 60:
    problems.append(f"only {compared} of {len(stays)} stays were answered; at least 60 are needed to check the lost-ticket fee")
finish(problems, f"G5 ok: {compared} stays each with and without a lost ticket")
