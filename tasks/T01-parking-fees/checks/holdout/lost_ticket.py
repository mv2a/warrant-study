"""H5: a lost ticket adds exactly 2500 cents to any stay, free or capped, and changes nothing else."""

import random

from _cmd import call, finish
from _oracle import clock, request

rng = random.Random(50505)
stays = [(600, 600), (600, 605), (600, 615), (1550, 1565), (600, 616), (600, 1000),
         (600, 2040), (600, 2041), (60, 3001), (0, 10079), (3360, 6390)]
for _ in range(30):
    minutes = rng.choice((rng.randint(0, 30), rng.randint(16, 1440), rng.randint(0, 10079)))
    entry = rng.randint(0, 10079 - minutes)
    stays.append((entry, entry + minutes))
problems = []
for entry, exit_ in stays:
    kept_status, kept = call(request(entry, exit_, False))
    lost_status, lost = call(request(entry, exit_, True))
    where = f"{clock(entry)} to {clock(exit_)}"
    if kept_status != 0 or lost_status != 0 or not isinstance(kept, dict) or not isinstance(lost, dict):
        problems.append(f"{where}: expected status 0 and an object both ways, got {kept_status}/{lost_status}")
        continue
    if kept.get("lost_ticket_cents") != 0:
        problems.append(f"{where} with the ticket: expected lost_ticket_cents 0, got {kept.get('lost_ticket_cents')!r}")
    if lost.get("lost_ticket_cents") != 2500:
        problems.append(f"{where} with a lost ticket: expected lost_ticket_cents 2500, got {lost.get('lost_ticket_cents')!r}")
    for field in ("minutes", "time_cents", "overnight_cents"):
        if lost.get(field) != kept.get(field):
            problems.append(f"{where}: {field} changed with a lost ticket ({kept.get(field)!r} -> {lost.get(field)!r})")
    total = kept.get("total_cents")
    if not isinstance(total, int) or lost.get("total_cents") != total + 2500:
        problems.append(f"{where}: expected the lost-ticket total to be {total!r} + 2500, got {lost.get('total_cents')!r}")

finish(problems, f"lost ticket ok: {len(stays)} stays, each with and without the ticket")
