"""H2: stays of 15 minutes or less have no time or overnight charge; longer ones pay from minute one."""

from _cmd import call, finish
from _oracle import clock, request

TUE_0200 = 1440 + 120
FREE = [(e, e + m) for e, m in ((600, 0), (600, 1), (3000, 7), (5000, 14), (6000, 15), (9000, 15), (0, 15), (10064, 15))]
FREE += [(TUE_0200 - 10, TUE_0200 + 5),   # 01:50 to 02:05 crosses 02:00
         (TUE_0200, TUE_0200 + 15),       # enters exactly at 02:00
         (TUE_0200 - 15, TUE_0200),       # leaves exactly at 02:00
         (TUE_0200 - 1, TUE_0200 + 14)]
CHARGED = [
    (600, 616, 250, 0), (600, 630, 250, 0), (600, 660, 250, 0), (600, 675, 500, 0),
    (600, 676, 500, 0), (600, 735, 750, 0), (600, 795, 1000, 0), (600, 855, 1250, 0),
    (TUE_0200 - 10, TUE_0200 + 6, 250, 600),   # 16 minutes over 02:00 pays the night too
    (TUE_0200, TUE_0200 + 16, 250, 600),
    (1000, 1000 + 1455, 1850, 600),             # 24 h 15 min: the leftover 15 minutes are charged
]
problems = []
for entry, exit_ in FREE:
    status, body = call(request(entry, exit_))
    got = (body.get("time_cents"), body.get("overnight_cents")) if isinstance(body, dict) else None
    if status != 0 or got != (0, 0):
        problems.append(f"{clock(entry)} to {clock(exit_)}: expected no time or overnight charge, "
                        f"got {got!r} (status {status})")
for entry, exit_, time_cents, overnight_cents in CHARGED:
    status, body = call(request(entry, exit_))
    got = (body.get("time_cents"), body.get("overnight_cents")) if isinstance(body, dict) else None
    if status != 0 or got != (time_cents, overnight_cents):
        problems.append(f"{exit_ - entry} minutes from {clock(entry)}: expected (time, overnight) "
                        f"{(time_cents, overnight_cents)}, got {got!r} (status {status})")

finish(problems, f"grace ok: {len(FREE)} free stays and {len(CHARGED)} charged from their first minute")
