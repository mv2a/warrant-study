"""X09 (C2): days_late is returned_day minus due_day, never below zero; early or on-time returns owe nothing."""

import random

from _audit import TYPES, finish, item, item_fine, succeed

problems = []

# Early and on-time returns owe nothing for every type, reference included.
for kind in TYPES:
    for due, returned in ((60, 60), (60, 59), (60, 1), (60, 0), (0, 0), (1, 0), (500, 250)):
        want = {"items": [{"id": "c", "days_late": 0, "fine_cents": 0}], "total_cents": 0}
        succeed(problems, f"{kind} due {due} returned {returned}", {"items": [item("c", kind, due, returned)]}, want=want)

# days_late is the plain difference: not reduced by the grace period and not stopped by any cap.
exact = [
    ("book", 70, 71, 1), ("book", 70, 73, 3), ("book", 70, 74, 4), ("book", 0, 365, 365),
    ("dvd", 9, 11, 2), ("dvd", 9, 40, 31), ("dvd", 1, 1001, 1000),
    ("reference", 33, 34, 1), ("reference", 33, 60, 27), ("reference", 2, 100002, 100000),
]
for kind, due, returned, late in exact:
    fine = item_fine(kind, due, returned)
    succeed(problems, f"{kind} {due}->{returned}", {"items": [item("c2", kind, due, returned)]},
            want={"items": [{"id": "c2", "days_late": late, "fine_cents": fine}], "total_cents": fine})

# A request mixing early, on-time and late returns: only the late ones are charged, and early
# returns never produce a credit that lowers the total.
mixed = {"items": [
    item("early-ref", "reference", 90, 10),
    item("late-ref", "reference", 90, 94),
    item("ontime-dvd", "dvd", 90, 90),
    item("late-book", "book", 90, 99),
]}
succeed(problems, "mixed early and late", mixed,
        want={"items": [{"id": "early-ref", "days_late": 0, "fine_cents": 0},
                        {"id": "late-ref", "days_late": 4, "fine_cents": 600},
                        {"id": "ontime-dvd", "days_late": 0, "fine_cents": 0},
                        {"id": "late-book", "days_late": 9, "fine_cents": 150}],
              "total_cents": 750})

# Generated: whole-day numbers anywhere in 0..5000, early and late, one request per case.
rng = random.Random(58113)
for n in range(30):
    due = rng.randint(0, 5000)
    returned = rng.randint(0, 5000) if n % 2 else max(0, due - rng.randint(0, 40))
    succeed(problems, f"generated {n}", {"items": [item(f"c{n}", rng.choice(TYPES), due, returned)]})

finish(problems, "days_late ok: returned minus due, floored at zero")
