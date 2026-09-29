"""X8 (C3): requests at the edge of validity are split, not refused. Only the requests the
intent calls invalid may be refused: a tip of exactly 0 or 100, a 1-cent item, names that
differ only by case, spacing or Unicode form (names are compared exactly), a name made
only of spaces (still a non-empty string), and items listed before their diner."""

from _cmd import call, finish
from _model import bill

NFC, NFD = "José", "José"
CASES = [
    ("a tip of 0", bill([("Oda", "own"), ("Brix", "share")], [("Oda", 1250), ("Brix", 80)], 0)),
    ("a tip of 100", bill([("Oda", "own"), ("Brix", "share")], [("Oda", 1250), ("Brix", 80)], 100)),
    ("a single 1-cent item", bill([("Nell", "share")], [("Nell", 1)], 18)),
    ("names differing only by case", bill([("Tove", "own"), ("tove", "own")], [("Tove", 900), ("tove", 700)], 10)),
    ("names differing only by a trailing space", bill([("Ines", "share"), ("Ines ", "share")], [("Ines ", 1001)], 15)),
    ("names in two Unicode forms", bill([(NFC, "own"), (NFD, "own")], [(NFC, 450), (NFD, 550)], 20)),
    ("a name of one space", bill([(" ", "own"), ("Galo", "share")], [(" ", 300), ("Galo", 700)], 12)),
    ("non-Latin names", bill([("李雷", "share"), ("Ζωή", "share"), ("Zoë", "own")], [("Ζωή", 2500), ("Zoë", 499)], 22)),
    ("names that match response fields", bill([("shares", "own"), ("total_cents", "share")],
                                              [("shares", 640), ("total_cents", 360)], 5)),
    ("items listed before their diner appears", bill([("Pim", "share"), ("Rune", "own"), ("Suvi", "share")],
                                                     [("Suvi", 1200), ("Rune", 800), ("Pim", 10)], 15)),
    ("own-payers who ordered nothing", bill([("Yara", "own"), ("Zeno", "own"), ("Elio", "own")], [("Zeno", 5000)], 20)),
    ("sharers who ordered nothing", bill([("Hedda", "share"), ("Caio", "share"), ("Mirte", "own")], [("Mirte", 3100)], 8)),
    ("one diner who pays for everything", bill([("Fumi", "share")], [("Fumi", 1100), ("Fumi", 2300)], 13)),
    ("a very large price", bill([("Aroha", "own"), ("Björn", "share")], [("Aroha", 10 ** 15), ("Björn", 3)], 15)),
    ("thirty diners and ninety items", bill([(f"Guest {k}", "own" if k % 4 == 0 else "share") for k in range(30)],
                                           [(f"Guest {(k * 11) % 30}", 150 + k * 37) for k in range(90)], 17)),
]

problems = []
for label, request in CASES:
    names = sorted(d["name"] for d in request["diners"])
    status, body = call(request)
    shares = body.get("shares") if isinstance(body, dict) else None
    if status != 0 or not isinstance(shares, dict):
        problems.append(f"{label}: expected the bill to be split, got status {status} and {body!r}")
    elif sorted(shares) != names:
        problems.append(f"{label}: expected a share for each of {names}, got {sorted(shares)}")

finish(problems, f"valid edge requests ok: {len(CASES)} split")
