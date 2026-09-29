"""X2 (G1): too_short below 12 and too_long above 64 characters, counted as Unicode code points."""

import json

from _audit import breaks, generated, rule_check, run_bytes_all, shape_problem, short

CODES = ("too_long", "too_short")
FILL = "Tq8!Wz3?Kp5;Nm2:Rx6%Jv4=" * 500          # four classes, no repeats
ACCENTED = "\u00e9\u00fc\u00f1\u00f8\u00e7\u00e5\u00df\u00e6\u0153\u00f0\u00fe\u0142" * 6
EMOJI = "\U0001F600\U0001F642\U0001F389\U0001F680\U0001F98A\U0001F31F\U0001F4A1\U0001F525" * 9
CJK = "\u4e2d\u6587\u5b57\u7b26\u6d4b\u8bd5\u5bc6\u7801\u5b89\u5168\u89c4\u5219" * 6
DECOMPOSED = "e\u0301"                             # two code points that display as one letter


def case(label, password, expected, username="quill", banned=()):
    return (label, {"password": password, "username": username, "banned": list(banned)}, set(expected))


CASES = [
    case("empty", "", {"too_short"}),
    case("1 ASCII", FILL[:1], {"too_short"}),
    case("7 ASCII", FILL[:7], {"too_short"}),
    case("11 ASCII", FILL[:11], {"too_short"}),
    case("12 ASCII", FILL[:12], set()),
    case("13 ASCII", FILL[:13], set()),
    case("40 ASCII", FILL[:40], set()),
    case("63 ASCII", FILL[:63], set()),
    case("64 ASCII", FILL[:64], set()),
    case("65 ASCII", FILL[:65], {"too_long"}),
    case("66 ASCII", FILL[:66], {"too_long"}),
    case("128 ASCII", FILL[:128], {"too_long"}),
    case("5000 ASCII", FILL[:5000], {"too_long"}),
    case("11 incl. trailing space", FILL[:10] + " ", {"too_short"}),
    case("12 incl. trailing space", FILL[:11] + " ", set()),
    case("12 incl. leading space", " " + FILL[:11], set()),
    case("12 spaces", " " * 12, set()),
    case("12 incl. two newlines", FILL[:10] + "\n\n", set()),
    case("65 with spaces at both ends", " " + FILL[:63] + " ", {"too_long"}),
    case("64 with tabs at both ends", "\t" + FILL[:62] + "\t", set()),
    case("11 accented letters", ACCENTED[:11], {"too_short"}),
    case("12 accented letters (24 UTF-8 bytes)", ACCENTED[:12], set()),
    case("64 accented letters (128 UTF-8 bytes)", ACCENTED[:64], set()),
    case("65 accented letters", ACCENTED[:65], {"too_long"}),
    case("11 emoji", EMOJI[:11], {"too_short"}),
    case("12 emoji (48 UTF-8 bytes, 24 UTF-16 units)", EMOJI[:12], set()),
    case("64 emoji", EMOJI[:64], set()),
    case("65 emoji", EMOJI[:65], {"too_long"}),
    case("3 ASCII + 8 emoji = 11", "Aa1" + EMOJI[:8], {"too_short"}),
    case("32 emoji + 32 ASCII = 64", EMOJI[:32] + FILL[:32], set()),
    case("33 emoji + 32 ASCII = 65", EMOJI[:33] + FILL[:32], {"too_long"}),
    case("11 CJK", CJK[:11], {"too_short"}),
    case("12 CJK", CJK[:12], set()),
    case("64 CJK", CJK[:64], set()),
    case("65 CJK", CJK[:65], {"too_long"}),
    case("11 ASCII + one CJK = 12", FILL[:11] + CJK[:1], set()),
    case("63 ASCII + one emoji = 64", FILL[:63] + EMOJI[:1], set()),
    case("64 ASCII + one accented = 65", FILL[:64] + ACCENTED[:1], {"too_long"}),
    case("6 decomposed e-acute = 12 code points", DECOMPOSED * 6, set()),
    case("5 decomposed e-acute + 1 = 11 code points", DECOMPOSED * 5 + "Q", {"too_short"}),
    case("32 decomposed e-acute + 1 = 65 code points", DECOMPOSED * 32 + "Q", {"too_long"}),
    case("32 decomposed e-acute = 64 code points", DECOMPOSED * 32, set()),
    case("mixed 12: Latin, Greek, Cyrillic, Arabic digit", "Ab\u03a9\u0436\u0663\u00e9-9\u20ac\u2022\u00a0z", set()),
    case("mixed 11", "Ab\u03a9\u0436\u0663\u00e9-9\u20ac\u2022z", {"too_short"}),
    case("11, username and banned also long", FILL[:11], {"too_short"},
         username="averyveryverylongusername_32char", banned=["x" * 90]),
] + generated(7310041, 140, "generated")

# The same boundaries sent as raw UTF-8 JSON text instead of \u escapes.
RAW = [
    ("raw UTF-8, 11 accented", ACCENTED[:11], {"too_short"}),
    ("raw UTF-8, 12 accented", ACCENTED[:12], set()),
    ("raw UTF-8, 64 emoji", EMOJI[:64], set()),
    ("raw UTF-8, 65 CJK", CJK[:65], {"too_long"}),
]
raw_problems = []
blobs = [json.dumps({"password": p, "username": "quill", "banned": []}, ensure_ascii=False).encode("utf-8")
         for _, p, _ in RAW]
for (label, password, expected), (status, out) in zip(RAW, run_bytes_all(blobs)):
    try:
        body = json.loads(out.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        body = out.decode("utf-8", "replace").strip() or None
    reason = shape_problem(status, body)
    if reason:
        raw_problems.append(f"{label} {short(password)}: {reason}")
        continue
    for code in CODES:
        if (code in body["violations"]) != (code in expected):
            verb = "should" if code in expected else "should not"
            raw_problems.append(f"{label} {short(password)}: {verb} break {code}, got {body['violations']}")

# Sanity: the hand-written expectations agree with the model of intent.md.
assert all(exp == {c for c in CODES if c in breaks(r["password"], r["username"], r["banned"])}
           for _, r, exp in CASES if exp is not None), "audit harness bug: expectation vs model"

rule_check(CODES, CASES, "length ok: {n} passwords, plus " + str(len(RAW)) + " sent as raw UTF-8", raw_problems)
