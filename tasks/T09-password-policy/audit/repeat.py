"""X5 (G4): the same character three or more times in a row breaks `repeat`; case matters."""

from _audit import breaks, generated, rule_check

HAND = [
    # (label, password, breaks repeat?)
    ("triple in the middle", "Pv7!mmm-Ks2?", True),
    ("triple at the start", "mmmPv7!Ks2?x", True),
    ("triple at the end", "Pv7!Ks2?xmmm", True),
    ("whole password one letter", "rrrrrrrrrrrr", True),
    ("run of seven", "Pv7!ttttttt-Ks2", True),
    ("pairs only", "Pv77!!mmKs22??", False),
    ("pair, other, pair", "Pv7!mm-mm-Ks2?", False),
    ("pair split by one", "Pv7!mm_m-Ks2?", False),
    ("alternating", "Pv7!mNmNmNmN-Ks2", False),
    ("pattern repeated, no run", "Pv7!abcabcabc", False),
    ("upper triple", "Pv7!QQQ-ks2?", True),
    ("lower-upper-lower", "Pv7!qQq-ks2?", False),
    ("upper-lower-upper", "Pv7!QqQ-ks2?", False),
    ("two lower then upper", "Pv7!qqQ-ks2?", False),
    ("upper then two lower", "Pv7!Qqq-ks2?", False),
    ("digit triple", "Pv7!Ks2?000x", True),
    ("hyphen triple", "Pv7!---Ks2?x", True),
    ("three spaces", "Pv7   Ks2?xy", True),
    ("two spaces twice", "Pv7  Ks2  xy", False),
    ("three tabs", "Pv7\t\t\tKs2?x", True),
    ("three newlines", "Pv7\n\n\nKs2?x", True),
    ("three dots", "Pv7...Ks2?xy", True),
    ("three backslashes", "Pv7\\\\\\Ks2?x", True),
    ("three double quotes", "Pv7\"\"\"Ks2?x", True),
    ("e-acute triple", "Pv7!\u00e9\u00e9\u00e9-Ks2", True),
    ("e-acute, E-acute, e-acute", "Pv7!\u00e9\u00c9\u00e9-Ks2", False),
    ("sharp s triple", "Pv7!\u00df\u00df\u00df-Ks2", True),
    ("sharp s, capital sharp s, sharp s", "Pv7!\u00df\u1e9e\u00df-Ks2", False),
    ("emoji triple", "Pv7!\U0001F600\U0001F600\U0001F600-Ks2", True),
    ("emoji pair then another emoji", "Pv7!\U0001F600\U0001F600\U0001F642\U0001F600-Ks2", False),
    ("three different emoji with the same high surrogate", "Pv7!\U0001F600\U0001F601\U0001F602-Ks2", False),
    ("CJK triple", "Pv7!\u4e2d\u4e2d\u4e2d-Ks2", True),
    ("Kelvin sign triple", "Pv7!\u212a\u212a\u212a-ks2", True),
    ("k, Kelvin sign, k", "Pv7!k\u212ak-Ks2", False),
    ("K, Kelvin sign, K", "Pv7!K\u212aK-ks2", False),
    ("i, dotless i, i", "Pv7!i\u0131i-Ks2", False),
    ("no-break space between two spaces", "Pv7 \u00a0 Ks2?x", False),
    ("three no-break spaces", "Pv7\u00a0\u00a0\u00a0Ks2?x", True),
    ("Arabic-Indic three, triple", "Pv7!\u0663\u0663\u0663-Ks2", True),
    ("3 vs Arabic-Indic three", "Pv7!3\u06633-Ks2", False),
    ("empty password", "", False),
    ("two characters", "xx", False),
    ("exactly three characters", "xxx", True),
    ("long, run near the end", "Pv7!Ks2?" * 8 + "wxyzzz", True),
    ("long, pairs everywhere", "Pv7!Ks2?".replace("v", "vv") * 8, False),
]

CASES = [(label, {"password": p, "username": "ansel", "banned": []}, expected) for label, p, expected in HAND]
CASES += generated(1140589, 160, "generated")

assert all(exp == ("repeat" in breaks(r["password"], r["username"], r["banned"]))
           for _, r, exp in CASES if exp is not None), "audit harness bug: expectation vs model"

rule_check("repeat", CASES, "repeat ok: {n} passwords")
