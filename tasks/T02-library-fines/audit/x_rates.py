"""X10 (G1): below the caps, an item's fine is its charged days times 25 (book), 100 (DVD) or 150 (reference)."""

from _audit import finish, item, succeed

problems = []

# Every uncapped charged-day count for each type, one item per request, on a due day other than
# anything visible. Charged days are written out here from G2 so the rate is checked directly.
SWEEPS = {
    # type: (rate, grace, largest uncapped charged-day count)
    "book": (25, 3, 32),        # 32 x 25 = 800, the book cap
    "dvd": (100, 3, 20),        # 20 x 100 = 2000, the DVD cap
    "reference": (150, 0, 10),  # 10 x 150 = 1500, the reference cap
}
due = 211
cases = 0
for kind, (rate, grace, top) in SWEEPS.items():
    for charged in range(1, top + 1):
        late = charged + grace
        fine = charged * rate
        cases += 1
        succeed(problems, f"{kind} {charged} charged day(s)",
                {"items": [item(f"{kind[0]}{charged}", kind, due, due + late)]},
                want={"items": [{"id": f"{kind[0]}{charged}", "days_late": late, "fine_cents": fine}],
                      "total_cents": fine})

# The three rates side by side in one request whose total stays under every cap.
succeed(problems, "one charged day of each type", {"items": [
    item("r", "reference", 17, 18), item("d", "dvd", 17, 21), item("b", "book", 17, 21)]},
    want={"items": [{"id": "r", "days_late": 1, "fine_cents": 150},
                    {"id": "d", "days_late": 4, "fine_cents": 100},
                    {"id": "b", "days_late": 4, "fine_cents": 25}], "total_cents": 275})

finish(problems, f"rates ok: {cases + 1} requests")
