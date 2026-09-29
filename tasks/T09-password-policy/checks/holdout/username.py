"""H3 (G3): username is broken by any four consecutive username characters, ignoring ASCII case."""

import random

from _cmd import call, finish
from _oracle import SYMBOL, breaks_username, flip_case, random_password, random_username, violations_of

# (username, password, whether the password breaks the username rule)
CASES = [
    ("harbor", "Q1-harb-zz", True),          # first window
    ("harbor", "Q1-arbo-zz", True),          # a middle window
    ("harbor", "Q1-rbor-zz", True),          # last window
    ("harbor", "HARBOR-zz-1", True),         # the whole username, other case
    ("harbor", "Q1-har-bor-zz", False),      # only three-character pieces
    ("harbor", "Q1-robrah-zz", False),       # reversed
    ("harbor", "Q1-h.a.r.b-zz", False),      # interrupted
    ("lynx", "Big-LYNX-cat-7", True),        # a four-character username is one window
    ("lynx", "Big-LYN-cat-7", False),
    ("lynx", "Big-ynx-cat-7", False),
    ("kim", "Big-kim-cat-7", False),         # shorter than four: forbids nothing
    ("KIM", "Big-KIM-kim-7", False),
    ("ab", "ab-AB-ab-1234", False),
    ("x", "x-X-x-Harbor-1", False),
    ("MacLeod", "xx-macleod-1", True),
    ("macleod", "xx-MACLEOD-1", True),
    ("MacLeod", "xx-mACl-99", True),
    ("j.doe_99", "Zz-oe_9-k", True),         # windows may hold ., _ and -
    ("j.doe_99", "Zz-E_99-k", True),
    ("j.doe_99", "Zz-doe-99-k", False),
    ("user2024", "Harbor-2024-x", True),     # the last window is all digits
    ("user2024", "Harbor-202-4x", False),
    ("a-b-c-d", "Harbor-B-C-x1", True),
    ("a-b-c-d", "Harbor-bc-d1", False),
    ("aaaa", "Harbor-AAAA-1", True),
    ("abcdefghijklmnopqrstuvwxyz012345", "Harbor-2345-x", True),   # 32 characters, last window
    ("abcdefghijklmnopqrstuvwxyz012345", "Harbor-345-x", False),
    ("Harbor", "har\u00e9bor-Lamp-1", False),  # a non-ASCII character in between
    # Text is compared as given: no Unicode normalization, no case mapping beyond ASCII.
    ("lopez", "Qx-lope\u0301z-9", True),                 # "lope", then a separate accent
    ("lopez", "Qx-lop\u00e9z-9", False),                 # a precomposed e-acute is not e
    ("lopez", "Qx-\uff4c\uff4f\uff50\uff45z-9", False),  # fullwidth letters are not ASCII
    ("kestrel", "Qq9-KEST-zz", True),
    ("kestrel", "Qq9-\u212aest-zz", False),              # the Kelvin sign is not K
    ("castle", "Qq9-ca\u017ftl-zz", False),              # the long s is not s
]

rng = random.Random(9303)
for i in range(70):
    username = random_username(rng)
    password = random_password(rng, 4, 24)
    roll = rng.random()
    if roll < 0.45 and len(username) >= 4:
        start = rng.randrange(len(username) - 3)
        piece = flip_case(rng, username[start:start + 4])
    elif roll < 0.75:
        start = rng.randrange(len(username))
        piece = flip_case(rng, username[start:start + 3])
    else:
        piece = rng.choice(SYMBOL)
    at = rng.randint(0, len(password))
    password = password[:at] + piece + password[at:]
    CASES.append((username, password, breaks_username(password, username)))

problems = []
for username, password, should in CASES:
    status, body = call({"password": password, "username": username, "banned": []})
    got = violations_of(body)
    if status != 0 or got is None:
        problems.append(f"{username!r}/{password!r}: expected status 0 and a violations list, got status {status} and {body!r}")
    elif ("username" in got) != should:
        verb = "should" if should else "should not"
        problems.append(f"username {username!r}, password {password!r}: {verb} break username, got {got}")

finish(problems, f"username ok: {len(CASES)} requests")
