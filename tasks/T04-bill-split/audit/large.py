"""X13 and X14 (G1; G4 and C2): the intent sets no upper limit on prices and says the
arithmetic is exact, so very large bills (up to 10**20 cents, past what a float holds
exactly) must still come out to the cent.

  python3 large.py totals   subtotal, tip and total are exact (G1)
  python3 large.py shares   shares follow the exact fair amounts and the leftover rule,
                            judged against the total the command reports (G4, C2)"""

import sys

from _cmd import call, finish
from _model import allocate, bill, fair, subtotal, tip

CASES = [
    bill([("Oda", "own")], [("Oda", 2 ** 53 + 1)], 15),
    bill([("Brix", "share"), ("Nell", "share"), ("Tove", "share")], [("Nell", 10 ** 15 + 1)], 18),
    bill([("Galo", "own"), ("Ines", "share"), ("Pim", "share"), ("Rune", "share")],
         [("Galo", 123456789012), ("Pim", 987654321098), ("Rune", 5)], 22),
    bill([("Suvi", "own"), ("Yara", "own"), ("Zeno", "share")],
         [("Suvi", 10 ** 20 + 7), ("Yara", 3), ("Zeno", 10 ** 18 + 1)], 7),
    bill([("Elio", "share"), ("Hedda", "own"), ("Fumi", "share"), ("Caio", "own"), ("Mirte", "share")],
         [(n, 10 ** 14 + 7919 * k) for k, n in enumerate(["Elio", "Hedda", "Fumi", "Caio", "Mirte"] * 2)], 33),
    # Tips that a float calculation gets one cent wrong.
    bill([("Oda", "own"), ("Galo", "own"), ("Suvi", "own")], [("Suvi", 193421896586406), ("Oda", 627359092107480)], 68),
    bill([("Oda", "share"), ("Galo", "share"), ("Suvi", "share")], [("Oda", 870073273646576)], 98),
    bill([("Oda", "own"), ("Galo", "share"), ("Suvi", "own")], [("Galo", 204251832137416), ("Suvi", 263538242176700)], 53),
    # Shares that float fair amounts hand out wrongly.
    bill([("Oda", "share"), ("Galo", "own"), ("Suvi", "own"), ("Yara", "share")],
         [("Suvi", 85030158939), ("Galo", 68428896740), ("Galo", 12412399577), ("Oda", 4247666934)], 10),
    bill([("Oda", "own"), ("Galo", "own"), ("Suvi", "own")],
         [("Suvi", 2059989163665), ("Oda", 3389555663755), ("Suvi", 159165435365), ("Galo", 1211422797715)], 52),
    bill([("Oda", "own"), ("Galo", "own"), ("Suvi", "own"), ("Yara", "share")],
         [("Galo", 31509276118), ("Oda", 54565458291), ("Suvi", 34747094831), ("Yara", 26144498945)], 40),
    bill([("Oda", "share"), ("Galo", "own")], [("Galo", 96849660109), ("Oda", 81524691581)], 50),
]

mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode not in ("totals", "shares"):
    sys.exit("usage: large.py totals|shares")


def whole_number(value):
    """An integer, or a float holding a whole number (the type itself is C4's business)."""
    return not isinstance(value, bool) and (type(value) is int or (type(value) is float and value.is_integer()))


problems = []
for k, request in enumerate(CASES, 1):
    status, body = call(request)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"large bill {k}: expected a split, got {body!r} (status {status})")
        continue
    s = subtotal(request)
    if mode == "totals":
        t = tip(s, request["tip_percent"])
        want = {"subtotal_cents": s, "tip_cents": t, "total_cents": s + t}
        got = {f: body.get(f) for f in want}
        if got != want:
            problems.append(f"large bill {k}: expected {want}, got {got}")
    else:
        total = body.get("total_cents")
        if not whole_number(total):
            problems.append(f"large bill {k}: total_cents is not a whole number: {total!r}")
            continue
        total = int(total)
        want = allocate(fair(request, total=total, sub=s), total)
        if body.get("shares") != want:
            problems.append(f"large bill {k}: expected shares {want}, got {body.get('shares')!r}")

finish(problems, f"large bills ok ({mode}): {len(CASES)} bills")
