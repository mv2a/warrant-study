"""X13 (G4): total_cents is the sum of item fines capped at 2500; item fines are reported before that cap."""

import random

from _audit import TYPES, expected, finish, item, succeed

problems = []


def line(ident, late, fine):
    return {"id": ident, "days_late": late, "fine_cents": fine}


# Just below, exactly at, and just above the account cap (all fines are multiples of 25).
succeed(problems, "sum 2475", {"items": [
    item("a", "reference", 10, 20), item("b", "dvd", 10, 22), item("c", "book", 10, 16)]},
    want={"items": [line("a", 10, 1500), line("b", 12, 900), line("c", 6, 75)], "total_cents": 2475})
succeed(problems, "sum 2500", {"items": [
    item("a", "reference", 10, 20), item("b", "dvd", 10, 23)]},
    want={"items": [line("a", 10, 1500), line("b", 13, 1000)], "total_cents": 2500})
succeed(problems, "sum 2525", {"items": [
    item("a", "reference", 10, 20), item("b", "dvd", 10, 23), item("c", "book", 10, 14)]},
    want={"items": [line("a", 10, 1500), line("b", 13, 1000), line("c", 4, 25)], "total_cents": 2500})

# Far above the cap: every item keeps its own capped fine, and the total is 2500.
succeed(problems, "three capped DVDs", {"items": [
    item("d1", "dvd", 0, 60), item("d2", "dvd", 0, 23), item("d3", "dvd", 5, 500)]},
    want={"items": [line("d1", 60, 2000), line("d2", 23, 2000), line("d3", 495, 2000)], "total_cents": 2500})
succeed(problems, "items summing to 4300", {"items": [
    item("b", "book", 1, 100), item("d", "dvd", 1, 100), item("r", "reference", 1, 100)]},
    want={"items": [line("b", 99, 800), line("d", 99, 2000), line("r", 99, 1500)], "total_cents": 2500})

# Many small fines crossing the cap: forty books at 75 cents each sum to 3000.
books = [item(f"bk{n:02d}", "book", 100, 106) for n in range(40)]
succeed(problems, "forty small book fines", {"items": books},
        want={"items": [line(f"bk{n:02d}", 6, 75) for n in range(40)], "total_cents": 2500})

# Below the cap, the total is the plain sum, not rounded or altered.
succeed(problems, "sum 1200", {"items": [
    item("x", "book", 0, 5), item("y", "reference", 0, 7), item("z", "dvd", 0, 4)]},
    want={"items": [line("x", 5, 50), line("y", 7, 1050), line("z", 4, 100)], "total_cents": 1200})
succeed(problems, "sum 2450 with a capped item", {"items": [
    item("x", "dvd", 0, 90), item("y", "book", 0, 21), item("z", "reference", 0, 0)]},
    want={"items": [line("x", 90, 2000), line("y", 21, 450), line("z", 0, 0)], "total_cents": 2450})

# Generated accounts of 1 to 12 items around the cap (fixed seed).
rng = random.Random(9024417)
for n in range(40):
    items = []
    for k in range(rng.randint(1, 12)):
        due = rng.randint(0, 900)
        items.append(item(f"acct{n}-{k}", rng.choice(TYPES), due, due + rng.randint(0, 40)))
    request = {"items": items}
    succeed(problems, f"generated account {n}", request, want=expected(request))

finish(problems, "account cap ok: total capped at 2500, item fines unchanged")
