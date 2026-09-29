"""X6 (G5): a password containing any banned entry breaks `banned`, ASCII case ignored."""

from _audit import breaks, generated, rule_check

TWENTY = [f"nope{i:02d}" for i in range(19)]

HAND = [
    # (label, password, banned list, breaks banned?)
    ("entry in the middle", "Tidewater#58k", ["water"], True),
    ("entry upper case, password lower", "Tidewater#58k", ["WATER"], True),
    ("entry lower case, password upper", "TIDEWATER#58K", ["water"], True),
    ("entry and password mixed case", "tIdEwAtEr#58k", ["TiDeWa"], True),
    ("entry absent", "Tidewater#58k", ["river"], False),
    ("entry one character longer", "Tidewater#58k", ["waters"], False),
    ("entry split by a character", "Tidewater#58k", ["tide water"], False),
    ("entry reversed", "Tidewater#58k", ["retaw"], False),
    ("entry with symbol and digit", "Tidewater#58k", ["#5"], True),
    ("entry in wrong order", "Tidewater#58k", ["58#"], False),
    ("entry at the very start", "Tidewater#58k", ["tid"], True),
    ("entry at the very end", "Tidewater#58k", ["58K"], True),
    ("entry equals the password", "Tidewater#58k", ["tidewater#58k"], True),
    ("entry longer than the password, containing it", "Tide1!", ["tide1!x"], False),
    ("single-character entry", "Tidewater#58k", ["#"], True),
    ("single-character entry absent", "Tidewater#58k", ["@"], False),
    ("empty list", "Tidewater#58k", [], False),
    ("several entries, last matches", "Tidewater#58k", ["river", "lake", "ATER#"], True),
    ("several entries, none matches", "Tidewater#58k", ["river", "lake", "sea"], False),
    ("duplicate entries", "Tidewater#58k", ["water", "water"], True),
    ("20 entries, only the 20th matches", "Tidewater#58k", TWENTY + ["DEWA"], True),
    ("20 entries, none matches", "Tidewater#58k", TWENTY + ["dewx"], False),
    ("entry overlapping a doubled letter", "Pa-aa9!Lookout", ["aaa"], False),
    ("entry inside a mixed-case run", "Pa-aAa9!Lookout", ["aaa"], True),
    # entries are plain text, never patterns or format strings
    ("dot-star", "Tidewater#58k", [".*"], False),
    ("dot-star present literally", "Tide.*water#58k", [".*"], True),
    ("single dot", "Tidewater#58k", ["."], False),
    ("dot as a wildcard", "Tidewater#58k", ["t.d"], False),
    ("character class", "Tidewater#58k", ["[a-z]"], False),
    ("backslash d", "Tidewater#58k", ["\\d"], False),
    ("backslash d present literally", "Tide\\dwater#58k", ["\\D"], True),
    ("unbalanced parenthesis", "Tidewater#58k", ["("], False),
    ("unbalanced bracket", "Tidewater#58k", ["["], False),
    ("plus sign", "Tidewater#58k", ["+"], False),
    ("caret and dollar", "Tidewater#58k", ["^T", "k$"], False),
    ("alternation", "Tidewater#58k", ["x|w"], False),
    ("star", "Tidewater#58k", ["*"], False),
    ("question mark", "Tidewater#58k", ["e?"], False),
    ("percent-s", "Tidewater#58k", ["%s"], False),
    ("brace format field", "Tidewater#58k", ["{0}"], False),
    ("brace format field present literally", "Tide{0}water#58k", ["{0}"], True),
    ("glob star", "Tidewater#58k", ["tide*"], False),
    # whitespace entries are ordinary text
    ("single-space entry, password with a space", "Tide water#58k", [" "], True),
    ("single-space entry, password without spaces", "Tidewater#58k", [" "], False),
    ("tab entry", "Tide\twater#58k", ["\t"], True),
    ("entry with inner space", "Tide water#58k", ["E WA"], True),
    ("entry with surrounding spaces", "Tidewater#58k", [" water "], False),
    # only ASCII case is ignored
    ("e-acute entry, e-acute present", "Caf\u00e9-Latte-9", ["\u00e9"], True),
    ("E-acute entry, e-acute present", "Caf\u00e9-Latte-9", ["\u00c9"], False),
    ("CAFE with capital E-acute", "Caf\u00e9-Latte-9", ["CAF\u00c9"], False),
    ("CAF plus small e-acute", "Caf\u00e9-Latte-9", ["CAF\u00e9"], True),
    ("Kelvin sign in the password", "\u212aelvin-Scale-9", ["kelvin"], False),
    ("Kelvin sign in the entry", "Kelvin-Scale-9", ["\u212aelvin"], False),
    ("sharp s vs SS", "STRASSE-Road-12", ["stra\u00dfe"], False),
    ("SS vs sharp s", "Stra\u00dfe-Road-12", ["strasse"], False),
    ("sharp s vs sharp s", "Stra\u00dfe-Road-12", ["STRA\u00dfE"], True),
    ("long s vs s", "Mo\u017fs-Garden-7", ["moss"], False),
    ("dotless i vs I", "L\u0131ly-Pond-44", ["LILY"], False),
    ("dotted capital I vs i", "\u0130ris-Pond-44", ["iris"], False),
    ("ff ligature vs ff", "O\ufb00er-Now-99", ["offer"], False),
    ("Greek sigma forms", "\u03a3\u03bf\u03c6\u03b9\u03b1-9", ["\u03c3\u03bf\u03c6"], False),
    ("fullwidth letters", "\uff27\uff49\uff54-Hub-12", ["git"], False),
    ("emoji entry present", "Sun\U0001F600Rise-2024", ["\U0001F600r"], True),
    ("emoji entry absent", "Sun\U0001F600Rise-2024", ["\U0001F642"], False),
    ("CJK entry present", "Pw-\u4e2d\u6587-2024", ["\u4e2d\u6587"], True),
    ("non-ASCII in the password, ASCII entry elsewhere", "\u00e9t\u00e9-Summer-9", ["SUMMER"], True),
]

CASES = [(label, {"password": p, "username": "wolfe", "banned": b}, expected) for label, p, b, expected in HAND]
CASES += generated(2250613, 160, "generated")

assert all(exp == ("banned" in breaks(r["password"], r["username"], r["banned"]))
           for _, r, exp in CASES if exp is not None), "audit harness bug: expectation vs model"

rule_check("banned", CASES, "banned ok: {n} passwords")
