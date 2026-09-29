"""X12 (G3): an item's fine stops at 800 (book), 2000 (DVD) or 1500 (reference) cents, however late it is."""

from _audit import finish, item, succeed

problems = []
cases = 0

# (type, days late, expected fine) written out by hand around each cap and far beyond it.
TABLE = [
    ("book", 34, 775), ("book", 35, 800), ("book", 36, 800), ("book", 37, 800), ("book", 40, 800),
    ("book", 100, 800), ("book", 3650, 800), ("book", 10 ** 9, 800),
    ("dvd", 22, 1900), ("dvd", 23, 2000), ("dvd", 24, 2000), ("dvd", 25, 2000), ("dvd", 31, 2000),
    ("dvd", 400, 2000), ("dvd", 10 ** 9, 2000),
    ("reference", 9, 1350), ("reference", 10, 1500), ("reference", 11, 1500), ("reference", 12, 1500),
    ("reference", 45, 1500), ("reference", 10 ** 9, 1500),
]
for kind, late, fine in TABLE:
    for due in (3, 777):
        cases += 1
        succeed(problems, f"{kind} {late} days late from day {due}",
                {"items": [item("cap", kind, due, due + late)]},
                want={"items": [{"id": "cap", "days_late": late, "fine_cents": fine}], "total_cents": fine})

# Once capped, further late days add nothing: a sweep well past each cap stays flat.
for kind, cap, first in (("book", 800, 35), ("dvd", 2000, 23), ("reference", 1500, 10)):
    for late in range(first, first + 15):
        cases += 1
        succeed(problems, f"{kind} sweep {late}", {"items": [item("s", kind, 40, 40 + late)]},
                want={"items": [{"id": "s", "days_late": late, "fine_cents": cap}], "total_cents": cap})

finish(problems, f"item caps ok: {cases} requests")
