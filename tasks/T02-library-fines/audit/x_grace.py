"""X11 (G2): books and DVDs forgive up to 3 late days and charge only the days after the third; reference items forgive none."""

from _audit import finish, item, succeed

problems = []
cases = 0

RATE = {"book": 25, "dvd": 100, "reference": 150}

# (type, days late, charged days written out by hand from G2)
TABLE = [
    ("book", 1, 0), ("book", 2, 0), ("book", 3, 0), ("book", 4, 1), ("book", 5, 2),
    ("book", 6, 3), ("book", 8, 5), ("book", 13, 10),
    ("dvd", 1, 0), ("dvd", 2, 0), ("dvd", 3, 0), ("dvd", 4, 1), ("dvd", 5, 2),
    ("dvd", 6, 3), ("dvd", 9, 6), ("dvd", 15, 12),
    ("reference", 1, 1), ("reference", 2, 2), ("reference", 3, 3), ("reference", 4, 4),
    ("reference", 6, 6), ("reference", 7, 7),
]
for due in (0, 88, 1234):
    for kind, late, charged in TABLE:
        fine = charged * RATE[kind]
        cases += 1
        succeed(problems, f"{kind} {late} day(s) late from day {due}",
                {"items": [item("g", kind, due, due + late)]},
                want={"items": [{"id": "g", "days_late": late, "fine_cents": fine}], "total_cents": fine})

# The grace period applies to each item separately, not to the account.
succeed(problems, "grace per item", {"items": [
    item("b-a", "book", 50, 53), item("b-b", "book", 50, 53), item("d-a", "dvd", 50, 53),
    item("d-b", "dvd", 50, 54), item("r-a", "reference", 50, 53)]},
    want={"items": [{"id": "b-a", "days_late": 3, "fine_cents": 0},
                    {"id": "b-b", "days_late": 3, "fine_cents": 0},
                    {"id": "d-a", "days_late": 3, "fine_cents": 0},
                    {"id": "d-b", "days_late": 4, "fine_cents": 100},
                    {"id": "r-a", "days_late": 3, "fine_cents": 450}], "total_cents": 550})

finish(problems, f"grace ok: {cases + 1} requests")
