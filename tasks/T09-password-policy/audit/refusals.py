"""X8 (C3): every kind of invalid request is refused: exit status 2 and nothing on standard output."""

import json
import random
import string

from _audit import USERNAME_CHARS, finish, is_valid, random_request, run_bytes_all, short

BASE = {"password": "Gx7!pond-Reed4", "username": "marlow", "banned": ["reed"]}
BASE_TEXT = json.dumps(BASE)


def with_(**changes):
    request = dict(BASE)
    request.update(changes)
    return request


def without(key):
    return {k: v for k, v in BASE.items() if k != key}


OBJECTS = [
    # fields
    ("an extra field", with_(note="hi")),
    ("an extra field named ok", with_(ok=True)),
    ("an extra field set to null", with_(extra=None)),
    ("an extra field Password next to password", with_(Password="Gx7!pond-Reed4")),
    ("missing password", without("password")),
    ("missing username", without("username")),
    ("missing banned", without("banned")),
    ("an empty object", {}),
    ("field names in upper case", {"PASSWORD": "Gx7!pond-Reed4", "USERNAME": "marlow", "BANNED": []}),
    ("field name with a trailing space", {"password ": "Gx7!pond-Reed4", "username": "marlow", "banned": []}),
    # password type
    ("password null", with_(password=None)),
    ("password an integer", with_(password=740512983311)),
    ("password a float", with_(password=3.25)),
    ("password true", with_(password=True)),
    ("password false", with_(password=False)),
    ("password an empty list", with_(password=[])),
    ("password a list of one string", with_(password=["Gx7!pond-Reed4"])),
    ("password an object", with_(password={"value": "Gx7!pond-Reed4"})),
    # username type, length and characters
    ("username null", with_(username=None)),
    ("username an integer", with_(username=4217)),
    ("username true", with_(username=True)),
    ("username a list", with_(username=["marlow"])),
    ("username an object", with_(username={})),
    ("username empty", with_(username="")),
    ("username of 33 characters", with_(username="m" * 33)),
    ("username of 33 mixed characters", with_(username="Ab1._-" * 5 + "Ab1")),
    ("username of 64 characters", with_(username="marlow_" * 9 + "x")),
    ("username with an inner space", with_(username="mar low")),
    ("username with a leading space", with_(username=" marlow")),
    ("username with a trailing space", with_(username="marlow ")),
    ("username a single space", with_(username=" ")),
    ("username with a trailing newline", with_(username="marlow\n")),
    ("username with a leading newline", with_(username="\nmarlow")),
    ("username with a tab", with_(username="mar\tlow")),
    ("username with a NUL", with_(username="mar\u0000low")),
    ("username with @", with_(username="mar@low")),
    ("username with +", with_(username="mar+low")),
    ("username with !", with_(username="marlow!")),
    ("username with /", with_(username="mar/low")),
    ("username with a backslash", with_(username="mar\\low")),
    ("username with :", with_(username="mar:low")),
    ("username with ,", with_(username="mar,low")),
    ("username with an apostrophe", with_(username="mar'low")),
    ("username with a double quote", with_(username="mar\"low")),
    ("username with #", with_(username="#marlow")),
    ("username with ~", with_(username="marlow~")),
    ("username with a backtick", with_(username="mar`low")),
    ("username with *", with_(username="mar*")),
    ("username with e-acute", with_(username="ren\u00e9e")),
    ("username with an Arabic-Indic digit", with_(username="marlow\u0663")),
    ("username with a superscript two", with_(username="marlow\u00b2")),
    ("username in fullwidth letters", with_(username="\uff4d\uff41\uff52\uff4c\uff4f\uff57")),
    ("username with a Kelvin sign", with_(username="\u212aelly")),
    ("username with a dotted capital I", with_(username="\u0130ris")),
    ("username with a Cyrillic a", with_(username="m\u0430rlow")),
    ("username with a no-break space", with_(username="mar\u00a0low")),
    ("username with an emoji", with_(username="marlow\U0001F600")),
    ("username of 33 with an invalid character", with_(username="m" * 32 + "!")),
    # banned
    ("banned null", with_(banned=None)),
    ("banned a string", with_(banned="reed")),
    ("banned an object", with_(banned={"reed": 1})),
    ("banned an integer", with_(banned=5)),
    ("banned true", with_(banned=True)),
    ("banned with 21 entries", with_(banned=[f"w{i}" for i in range(21)])),
    ("banned with 30 entries", with_(banned=[f"word{i}" for i in range(30)])),
    ("banned with 21 identical entries", with_(banned=["reed"] * 21)),
    ("banned with one empty entry", with_(banned=[""])),
    ("banned with an empty entry last", with_(banned=["reed", "pond", ""])),
    ("banned with an integer entry", with_(banned=[5])),
    ("banned with a null entry", with_(banned=["reed", None])),
    ("banned with a list entry", with_(banned=[["reed"]])),
    ("banned with an object entry", with_(banned=[{"w": "reed"}])),
    ("banned with a true entry", with_(banned=[True])),
    ("banned with a float entry", with_(banned=["reed", 1.5])),
    # several problems at once
    ("bad username and bad banned", with_(username="a b", banned=None)),
    ("valid fields plus two extras", with_(x=1, y=2)),
]

TEXTS = [
    ("no input at all", ""),
    ("only whitespace", "  \n\t "),
    ("an opening brace", "{"),
    ("a closing brace", "}"),
    ("a bare word", "marlow"),
    ("JSON null", "null"),
    ("JSON true", "true"),
    ("a JSON number", "42"),
    ("a JSON string", "\"Gx7!pond-Reed4\""),
    ("an empty JSON list", "[]"),
    ("the request wrapped in a list", "[" + BASE_TEXT + "]"),
    ("single-quoted keys", BASE_TEXT.replace('"', "'")),
    ("unquoted keys", '{password: "Gx7!pond-Reed4", username: "marlow", banned: []}'),
    ("a trailing comma", '{"password": "Gx7!pond-Reed4", "username": "marlow", "banned": [],}'),
    ("a missing closing brace", BASE_TEXT[:-1]),
    ("text after the object", BASE_TEXT + " ok"),
    ("two objects", BASE_TEXT + BASE_TEXT),
    ("two objects on two lines", BASE_TEXT + "\n" + BASE_TEXT + "\n"),
    ("a comment before the object", "// request\n" + BASE_TEXT),
    ("NaN as password", '{"password": NaN, "username": "marlow", "banned": []}'),
    ("an unterminated string", '{"password": "Gx7!pond-Reed4, "username": "marlow", "banned": []}'),
]

BYTES = [
    ("bytes that are not UTF-8", b"\xff\xfe\xfd\x00\x81"),
]

# Seeded mutations of valid generated requests, each made invalid in exactly one way.
BAD_USERNAME_CHARS = (" !\"#$%&'()*+,/:;<=>?@[\\]^`{|}~\t\n\r\x00\x7f"
                      "\u00e9\u00c9\u00df\u0663\u00b2\uff41\u212a\u0130\u0131\u0430\u00a0\U0001F600")
NOT_STRINGS = [None, 0, 17, -3, 2.5, True, False, [], ["x"], {}, {"k": "v"}]


def mutate(rng, request):
    request = dict(request)
    kind = rng.randrange(9)
    if kind == 0:
        name = rng.choice(["id", "email", "user", "passwords", "banned_list", "Username", "", "ok"])
        request[name] = rng.choice(NOT_STRINGS + ["x"])
    elif kind == 1:
        del request[rng.choice(["password", "username", "banned"])]
    elif kind == 2:
        request["password"] = rng.choice(NOT_STRINGS)
    elif kind == 3:
        request["username"] = rng.choice(NOT_STRINGS + [""])
    elif kind == 4:
        request["username"] = "".join(rng.choice(USERNAME_CHARS) for _ in range(rng.randint(33, 50)))
    elif kind == 5:
        name = request["username"]
        i = rng.randint(0, len(name))
        request["username"] = name[:i] + rng.choice(BAD_USERNAME_CHARS) + name[i:]
    elif kind == 6:
        request["banned"] = rng.choice([None, 3, True, "reed", {"w": "reed"}])
    elif kind == 7:
        request["banned"] = [rng.choice(string.ascii_lowercase) * rng.randint(1, 4)
                             for _ in range(rng.randint(21, 40))]
    else:
        banned = list(request["banned"])
        banned.insert(rng.randint(0, len(banned)), rng.choice(NOT_STRINGS + [""]))
        request["banned"] = banned
    return request


rng = random.Random(4470829)
MUTATED = []
while len(MUTATED) < 90:
    candidate = mutate(rng, random_request(rng))
    if not is_valid(candidate):
        MUTATED.append((f"mutation #{len(MUTATED)}", candidate))

assert not any(is_valid(r) for _, r in OBJECTS), "audit harness bug: a listed request is valid"

cases = [(label, short(r), json.dumps(r).encode("utf-8")) for label, r in OBJECTS + MUTATED]
cases += [(label, short(t), t.encode("utf-8")) for label, t in TEXTS]
cases += [(label, repr(b), b) for label, b in BYTES]

problems = []
for (label, shown, data), (status, out) in zip(cases, run_bytes_all([d for _, _, d in cases])):
    if status != 2 or out != b"":
        problems.append(f"{label} {shown}: expected a refusal (status 2, no output), "
                        f"got status {status} and {short(out.decode('utf-8', 'replace'), 60)!s}")

finish(problems, f"refusals ok: {len(cases)} invalid requests refused with status 2 and no output")
