"""H5 (G5): banned is broken when the password contains any banned entry, ignoring ASCII case."""

import random

from _cmd import call, finish
from _oracle import breaks_banned, flip_case, random_password, violations_of

PASSWORD = "Harbor-Lamp-42"
FILLER = [f"word{n}x" for n in range(19)]  # none of these appear in PASSWORD

# (password, banned list, whether the password breaks the banned rule)
CASES = [
    (PASSWORD, [], False),
    (PASSWORD, ["lamp"], True),
    (PASSWORD, ["LAMP"], True),
    (PASSWORD, ["hArBoR"], True),
    (PASSWORD, ["harbor-lamp-42"], True),          # the whole password
    (PASSWORD, ["Harbor-Lamp-42!"], False),        # longer than the password
    (PASSWORD, ["amp-4"], True),
    (PASSWORD, ["42"], True),
    (PASSWORD, ["2"], True),
    (PASSWORD, ["lamps"], False),
    (PASSWORD, ["harborlamp"], False),
    (PASSWORD, ["24"], False),
    (PASSWORD, ["x", "y", "-l"], True),            # a later entry, other case
    (PASSWORD, FILLER + ["BOR-LA"], True),          # the 20th entry
    (PASSWORD, FILLER + ["BOR LA"], False),
    (PASSWORD, ["lamp", "lamp", "LAMP"], True),
    ("Caf\u00e9-Lamp-42", ["CAF\u00e9"], True),    # ASCII letters fold, the accent matches as is
    ("Caf\u00e9-Lamp-42", ["caf\u00c9"], False),   # non-ASCII letters do not fold
    ("Stra\u00dfe-Lamp-42", ["STRASSE"], False),
    ("Harbor Lamp 42", [" lamp "], True),
    ("Harbor Lamp 42", ["lamp  "], False),
    ("\U0001f600-Harbor-42", ["\U0001f600-h"], True),
    ("", ["a"], False),
    # Text is compared as given: no Unicode normalization, no case mapping beyond ASCII.
    ("Crème-Lamp-42", ["cre"], True),                   # c, r, e, then a separate accent
    ("Crème-Lamp-42", ["CRE"], False),                   # a precomposed e-grave is not e
    ("Crème-Lamp-42", ["crè"], False),             # nor is e plus a separate accent
    ("Harbor-Ｌａｍｐ-42", ["lamp"], False),  # fullwidth letters are not ASCII
    ("Kelp-Harbor-42", ["KELP"], False),                 # the Kelvin sign is not K
]

rng = random.Random(9505)
for i in range(70):
    password = random_password(rng, 1, 24)
    banned = []
    for _ in range(rng.randint(0, 6)):
        if rng.random() < 0.4 and password:
            start = rng.randrange(len(password))
            banned.append(flip_case(rng, password[start:start + rng.randint(1, 6)]))
        else:
            banned.append(random_password(rng, 1, 6))
    CASES.append((password, banned, None))

problems = []
for password, banned, should in CASES:
    if should is None:
        should = breaks_banned(password, banned)
    status, body = call({"password": password, "username": "zq", "banned": banned})
    got = violations_of(body)
    if status != 0 or got is None:
        problems.append(f"{password!r} with {banned!r}: expected status 0 and a violations list, got status {status} and {body!r}")
    elif ("banned" in got) != should:
        verb = "should" if should else "should not"
        problems.append(f"{password!r} with banned {banned!r}: {verb} break banned, got {got}")

finish(problems, f"banned ok: {len(CASES)} requests")
