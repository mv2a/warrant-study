"""X3 (G2): fewer than three of the four ASCII-defined character classes breaks `classes`."""

from _audit import breaks, generated, rule_check

# Every password here is at least 12 characters unless the label says otherwise; only the
# presence of `classes` is judged.
HAND = [
    # (label, password, breaks classes?)
    ("lowercase only", "quietmoorland", True),
    ("uppercase only", "QUIETMOORLAND", True),
    ("digits only", "80421736590412", True),
    ("ASCII symbols only", "!#$%&*+,-./:;<=>?", True),
    ("lower + upper", "quietMOORland", True),
    ("lower + digit", "quiet8moor4land", True),
    ("upper + symbol", "QUIET#MOOR!LAND", True),
    ("digit + symbol", "8042-1736/5904", True),
    ("lower + upper + digit", "quietMOOR4land", False),
    ("lower + upper + symbol", "quiet?MOORland", False),
    ("lower + digit + symbol", "quiet8moor_land", False),
    ("upper + digit + symbol", "QUIET8MOOR.LAND", False),
    ("all four", "quiet8MOOR~land", False),
    ("empty password: no class at all", "", True),
    ("3 characters, 3 classes (too short, but classes kept)", "q8M", False),
    ("2 characters, 2 classes", "q8", True),
    ("70 characters, 2 classes", "quietmoorland0" * 5, True),
    ("70 characters, 3 classes", "quietmoorland0" * 4 + "quiet+moorland", False),
    # the space and other whitespace are symbols
    ("lower + space + digit", "quiet moor 4land", False),
    ("lower + space", "quiet moor land", True),
    ("lower + tab + digit", "quietmoor\t4land", False),
    ("upper + newline + digit", "QUIETMOOR\n4LAND", False),
    ("lower + no-break space + digit", "quiet\u00a0moor4land", False),
    ("lower + NUL + digit", "quietmoor\u00004land", False),
    # letters and digits outside ASCII are symbols, never lower/upper/digit
    ("lower + digit + e-acute", "quietmoor4land\u00e9", False),
    ("lower + e-acute only", "quietmoorl\u00e9nd\u00e9", True),
    ("upper + digit + E-acute", "QUIETMOOR4LAND\u00c9", False),
    ("lower + digit + Arabic-Indic three", "quietmoor4land\u0663", False),
    ("lower + digit + Devanagari five", "quietmoor4land\u096b", False),
    ("lower + digit + fullwidth one", "quietmoor4land\uff11", False),
    ("lower + upper + Arabic-Indic digits only", "quietMOORland\u0663\u0664", False),
    ("lower + Arabic-Indic digits: 2 classes", "quietmoorland\u0663\u0664\u0665", True),
    ("upper + accented capitals: 2 classes", "QUIETMOORLAND\u00c9\u00c0\u00dc", True),
    ("lower + accented capitals: 2 classes", "quietmoorland\u00c9\u00c0\u00dc", True),
    ("lower + Greek capital omega: 2 classes", "quietmoorland\u03a9", True),
    ("upper + n-tilde: 2 classes", "QUIETMOORLAND\u00f1", True),
    ("lower + fullwidth capitals: 2 classes", "quietmoorland\uff21\uff22", True),
    ("digit + fullwidth small letters: 2 classes", "80421736\uff41\uff42\uff43", True),
    ("upper + sharp s + digit", "QUIETMOOR\u00df4LAND", False),
    ("lower + Kelvin sign: 2 classes", "quietmoorland\u212a", True),
    ("lower + dotless i + long s: 2 classes", "quietmoorland\u0131\u017f", True),
    ("upper + dotted capital I: 2 classes", "QUIETMOORLAND\u0130", True),
    ("Cyrillic lower + upper look-alikes + digit: 2 classes", "\u0430\u0431\u0432\u0413\u0414\u0415\u0436\u0437\u0438\u0439\u043a4", True),
    ("CJK only", "\u4e2d\u6587\u5b57\u7b26\u6d4b\u8bd5\u5bc6\u7801\u5b89\u5168\u89c4\u5219", True),
    ("emoji + lower: 2 classes", "quietmoorland\U0001F600", True),
    ("emoji + lower + digit", "quietmoor4land\U0001F600", False),
    # ASCII characters next to the letter and digit ranges are symbols
    ("lower + backtick/brace + digit", "quietmoor`{land4", False),
    ("upper + at/bracket + digit", "QUIETMOOR@[LAND4", False),
    ("digit + slash/colon + lower", "80421736/:quiet", False),
    ("lower + backtick/brace/bar/tilde: 2 classes", "quietmoorland`{|}~", True),
    ("upper + at/brackets/caret: 2 classes", "QUIETMOORLAND@[\\]^", True),
    ("digit + slash/colon/semicolon: 2 classes", "8042173659/:;<", True),
    ("underscore, dot and hyphen as the third class", "quietMOOR_.-land", False),
]

CASES = [(label, {"password": p, "username": "wren", "banned": []}, expected) for label, p, expected in HAND]
CASES += generated(8120353, 150, "generated")

assert all(exp == ("classes" in breaks(r["password"], r["username"], r["banned"]))
           for _, r, exp in CASES if exp is not None), "audit harness bug: expectation vs model"

rule_check("classes", CASES, "classes ok: {n} passwords")
