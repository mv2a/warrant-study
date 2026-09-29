"""X9 (C1, C3): valid requests at the edge of the rules in C3 are judged, not refused.

Each must exit 0 with one JSON object holding exactly ok (true/false) and violations (a
list of strings). Only the form of the answer is judged here, not which rules are broken.
"""

import json
import random
import string

from _audit import OTHER, USERNAME_CHARS, finish, is_valid, run_bytes_all, shape_problem, short

BASE = {"password": "Hq4?lantern-Vy", "username": "tobias", "banned": ["lamp"]}


def with_(**changes):
    request = dict(BASE)
    request.update(changes)
    return request


OBJECTS = [
    # usernames
    ("one-letter username", with_(username="t")),
    ("two-character username", with_(username="T9")),
    ("one-digit username", with_(username="7")),
    ("username a single dot", with_(username=".")),
    ("username a single hyphen", with_(username="-")),
    ("username a single underscore", with_(username="_")),
    ("username of dots, hyphens and underscores only", with_(username="._-_.")),
    ("username digits only", with_(username="00420017")),
    ("username upper case only", with_(username="TOBIAS")),
    ("username with every allowed kind", with_(username="T.o_b-i9S")),
    ("username of 31 characters", with_(username="t" * 31)),
    ("username of 32 characters", with_(username="Ab1._-" * 5 + "Ab")),
    ("username of 32 letters", with_(username=string.ascii_letters[:32])),
    ("username starting with a hyphen", with_(username="-tobias")),
    ("username starting with a dot", with_(username=".tobias")),
    # banned lists
    ("empty banned list", with_(banned=[])),
    ("banned with 19 entries", with_(banned=[f"x{i}" for i in range(19)])),
    ("banned with 20 entries", with_(banned=[f"x{i}" for i in range(20)])),
    ("banned with 20 identical entries", with_(banned=["lamp"] * 20)),
    ("banned entry a single space", with_(banned=[" "])),
    ("banned entry a tab", with_(banned=["\t"])),
    ("banned entry non-ASCII", with_(banned=["\u00e9t\u00e9", "\u4e2d\u6587", "\U0001F600"])),
    ("banned entry of 500 characters", with_(banned=["lamp" * 125])),
    ("banned entry that looks like a number", with_(banned=["5", "0"])),
    ("banned entries with quotes and backslashes", with_(banned=["\"", "\\", "'"])),
    ("banned entry that looks like JSON", with_(banned=["{}", "[]", "null"])),
    # passwords
    ("empty password", with_(password="")),
    ("password a single space", with_(password=" ")),
    ("password of 10,000 characters", with_(password="Hq4?lantern-Vy" * 715)),
    ("password with control characters", with_(password="Hq4\u0000\u0001\u001f\u007flantern")),
    ("password with quotes and backslashes", with_(password="Hq4\"lan\\tern'Vy")),
    ("password that looks like JSON", with_(password="{\"ok\": true}")),
    ("password null as text", with_(password="null")),
    ("password of emoji and CJK", with_(password="\U0001F600\u4e2d\u6587Hq4?")),
    ("password of combining marks", with_(password="e\u0301\u0301\u0301\u0301")),
    # everything at its edge together
    ("all fields at their edges", {"password": "", "username": "Z" * 32, "banned": ["\u00a0"] * 20}),
]

# The same valid request written as JSON text in other legal ways.
TEXTS = [
    ("keys in another order", '{"banned": ["lamp"], "username": "tobias", "password": "Hq4?lantern-Vy"}'),
    ("pretty-printed", json.dumps(BASE, indent=4)),
    ("CRLF line endings", json.dumps(BASE, indent=2).replace("\n", "\r\n")),
    ("whitespace around the object", " \n\t" + json.dumps(BASE) + "\n\n  "),
    ("no whitespace at all", json.dumps(BASE, separators=(",", ":"))),
    ("no trailing newline", json.dumps(BASE)),
    ("ASCII letters written as \\u escapes", '{"password": "Hq4?lantern-Vy", "username": "\\u0074obias", '
                                               '"banned": ["\\u006Camp"]}'),
    ("escaped slash in the password", '{"password": "Hq4\\/lantern-Vy", "username": "tobias", "banned": []}'),
    ("non-ASCII as raw UTF-8", json.dumps(with_(password="Hq4?l\u00e4ntern-\u00dfy\U0001F600"), ensure_ascii=False)),
    ("surrogate-pair escape for an emoji", '{"password": "Hq4?lantern-\\ud83d\\ude00", "username": "tobias", '
                                             '"banned": ["\\ud83d\\ude00"]}'),
]

rng = random.Random(5580937)
GENERATED = []
for i in range(80):
    username = "".join(rng.choice(USERNAME_CHARS) for _ in range(rng.choice([1, 2, 3, 4, 31, 32, rng.randint(1, 32)])))
    banned = ["".join(rng.choice(rng.choice([string.printable, OTHER])) for _ in range(rng.randint(1, 8)))
              for _ in range(rng.choice([0, 1, 19, 20, rng.randint(0, 20)]))]
    password = "".join(rng.choice(rng.choice([string.printable, OTHER])) for _ in range(rng.randint(0, 80)))
    GENERATED.append((f"generated #{i}", {"password": password, "username": username, "banned": banned}))

assert all(is_valid(r) for _, r in OBJECTS + GENERATED), "audit harness bug: a listed request is invalid"

cases = [(label, short(r), json.dumps(r).encode("utf-8")) for label, r in OBJECTS + GENERATED]
cases += [(label, short(t), t.encode("utf-8")) for label, t in TEXTS]

problems = []
for (label, shown, data), (status, out) in zip(cases, run_bytes_all([d for _, _, d in cases])):
    try:
        body = json.loads(out.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        body = out.decode("utf-8", "replace").strip() or None
    reason = shape_problem(status, body)
    if reason:
        problems.append(f"{label} {shown}: {reason}")

finish(problems, f"boundaries ok: {len(cases)} valid requests at the edges were judged")
