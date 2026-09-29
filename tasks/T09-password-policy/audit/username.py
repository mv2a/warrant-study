"""X4 (G3): four consecutive username characters in the password break `username`, ASCII case ignored."""

from _audit import breaks, generated, rule_check

HAND = [
    # (label, password, username, breaks username?)
    ("first window, upper case in password", "Xy!REBE9021qz", "rebecca_7", True),
    ("middle window", "zq-ecca-9021Q", "rebecca_7", True),
    ("last window with punctuation, mixed case", "q_CA_7!Zm0p", "rebecca_7", True),
    ("five consecutive characters", "Zm0p!ebecc-Qx", "rebecca_7", True),
    ("whole username", "Zm0p!REBECCA_7", "rebecca_7", True),
    ("only runs of three", "reb-ecc-a_7-Zm0p", "rebecca_7", False),
    ("username reversed", "7_acceber!Zm0p", "rebecca_7", False),
    ("runs of three joined by a gap", "rebXecca_Zm0p", "rebecca_7", True),  # "ecca" and "cca_"
    ("runs of three only, all upper", "REB!BEC!CCA!A_7", "rebecca_7", False),
    ("username of 3 fully present", "Zm0p!abc!ABC!abc", "abc", False),
    ("username of 3, password equal", "abc", "abc", False),
    ("username of 1 present", "q-Zm0p-q-q-q", "q", False),
    ("username of 2 present", "Qx8!qxQX-qx", "qx", False),
    ("username of 4, exact", "--ABCD--Zm0p", "abcd", True),
    ("username of 4, split", "--abc-d--Zm0p", "abcd", False),
    ("username of 4 equals the password", "Ohio", "OHIO", True),
    ("password shorter than 4", "Ohi", "OHIO", False),
    ("upper-case username, lower-case password", "xx9!jordan!xx", "JORDAN", True),
    ("mixed-case username and password", "xxMARIxx-40!", "MaRiA", True),
    ("dot inside the window", "Zz9!OM.H!Qq", "Tom.Hanks", True),
    ("underscore and digits", "Pass-E_99-word", "j.doe_99", True),
    ("digits-only username", "x!2024!Qx", "20242025", True),
    ("digits-only username, last window", "x!202!4Qx2025", "20242025", True),
    ("digits-only username, runs of three", "x!202!024!425!Qx", "20242025", False),
    ("punctuation-only username", "Qx8a--__b", "--__", True),
    ("punctuation-only username, split", "Qx8a--_-_b", "--__", False),
    ("dots are literal, not wildcards", "Zz9!axbxcxd!Qq", "a.b.c.d", False),
    ("dots are literal, window present", "Zz9!B.C.!Qq", "a.b.c.d", True),
    ("32-character username, last window", "Zz9!RCHAR!Qq", "averyveryverylongusername_32char", True),
    ("32-character username, repeated window", "Zz9!very-long-name!Qq", "averyveryverylongusername_32char", True),
    ("32-character username, only 3s", "Zz9!ave-ery-lon-ame!Qq", "averyveryverylongusername_32char", False),
    ("window at the very start", "kellyQ!9zzz", "kelly", True),
    ("window at the very end", "Q!9zzzELLY", "kelly", True),
    # only ASCII case is ignored: non-ASCII look-alikes never match
    ("Kelvin sign for K", "Xx9-\u212aate-Yy", "kate", False),
    ("ASCII K for k", "Xx9-Kate-Yy", "kate", True),
    ("long s for s", "Zz9!\u017fam5!Qq", "sam5", False),
    ("dotless i for i", "Zz9!b\u0131rd!Qq", "bird", False),
    ("dotted capital I for i", "Zz9!\u0130bis!Qq", "ibis", False),
    ("sharp s for ss", "Zz9!ba\u00df!Qq", "bass", False),
    ("ff ligature for ff", "Zz9!o\ufb00er!Qq", "offer", False),
    ("fullwidth letters", "Zz9!\uff4e\uff4f\uff52\uff41!Qq", "nora", False),
    ("e-acute for e", "Zz9!r\u00e9n\u00e9e!Qq", "renee", False),
    ("combining accent splits the run", "Zz9!re\u0301nee!Qq", "renee", False),
    ("combining accent after the run", "Zz9!renee\u0301!Qq", "renee", True),
]

CASES = [(label, {"password": p, "username": u, "banned": []}, expected) for label, p, u, expected in HAND]
CASES += generated(9030467, 160, "generated")

assert all(exp == ("username" in breaks(r["password"], r["username"], r["banned"]))
           for _, r, exp in CASES if exp is not None), "audit harness bug: expectation vs model"

rule_check("username", CASES, "username ok: {n} passwords")
