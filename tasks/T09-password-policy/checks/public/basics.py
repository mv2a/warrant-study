"""P3: a first look at the length and character-class rules."""

from _cmd import call, finish

BASE = "Harbor-Lamp-42" * 5  # 70 characters, four classes, no repeats
CASES = [
    ("a 64-character password", BASE[:64], "too_long", False),
    ("a 65-character password", BASE[:65], "too_long", True),
    ("lowercase letters and digits only", "harborlamp42", "classes", True),
    ("lowercase letters, digits and a hyphen", "harbor-lamp42", "classes", False),
]
problems = []
for name, password, code, broken in CASES:
    status, body = call({"password": password, "username": "alice", "banned": []})
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("violations"), list):
        problems.append(f"{name}: expected status 0 and a violations list, got status {status} and {body!r}")
    elif (code in body["violations"]) != broken:
        verb = "should" if broken else "should not"
        problems.append(f"{name}: {verb} break {code}, got {body['violations']}")

finish(problems, f"basics ok: {len(CASES)} passwords")
