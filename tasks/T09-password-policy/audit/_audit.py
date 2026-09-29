"""Shared helpers for the audit checks (X), written from intent.md alone.

It holds an independent model of the rules in intent.md, generators for seeded random
requests, and runners that call the workspace's `policy` command through _cmd.py.
"""

import json
import os
import random
import string
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from _cmd import COMMAND, PATH, call, finish

CODES = ("banned", "classes", "repeat", "too_long", "too_short", "username")
FIELDS = {"ok", "violations"}
USERNAME_CHARS = string.ascii_letters + string.digits + "._-"

# ---------------------------------------------------------------- model of intent.md


def ascii_fold(text):
    """Lower-case the ASCII letters A-Z only; every other character is left alone."""
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in text)


def char_class(c):
    if "a" <= c <= "z":
        return "lower"
    if "A" <= c <= "Z":
        return "upper"
    if "0" <= c <= "9":
        return "digit"
    return "symbol"


def breaks(password, username, banned):
    """The sorted list of rule codes that intent.md says the password breaks."""
    found = set()
    if len(password) < 12:
        found.add("too_short")
    if len(password) > 64:
        found.add("too_long")
    if len({char_class(c) for c in password}) < 3:
        found.add("classes")
    folded = ascii_fold(password)
    user = ascii_fold(username)
    if len(user) >= 4 and any(user[i:i + 4] in folded for i in range(len(user) - 3)):
        found.add("username")
    if any(password[i] == password[i + 1] == password[i + 2] for i in range(len(password) - 2)):
        found.add("repeat")
    if any(ascii_fold(entry) in folded for entry in banned):
        found.add("banned")
    return sorted(found)


def answer(request):
    violations = breaks(request["password"], request["username"], request["banned"])
    return {"ok": not violations, "violations": violations}


def is_valid(request):
    """True when intent.md C1/C3 call the request valid (it must be judged, not refused)."""
    if not isinstance(request, dict) or set(request) != {"password", "username", "banned"}:
        return False
    password, username, banned = request["password"], request["username"], request["banned"]
    if not isinstance(password, str):
        return False
    if not isinstance(username, str) or not 1 <= len(username) <= 32:
        return False
    if any(c not in USERNAME_CHARS for c in username):
        return False
    if not isinstance(banned, list) or len(banned) > 20:
        return False
    return all(isinstance(e, str) and e != "" for e in banned)


# ---------------------------------------------------------------- running the command


def _ensure_command():
    if not os.access(PATH, os.X_OK):
        sys.exit(f"the workspace has no executable named {COMMAND}")


def call_all(requests):
    """Call the command once per request (in parallel); returns [(status, body)] in order."""
    _ensure_command()
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(lambda r: call(r), requests))


def call_raw_all(texts):
    """Send each text as-is on stdin (through _cmd.call); returns [(status, body)] in order."""
    _ensure_command()
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(lambda t: call(raw=t), texts))


def run_bytes(data, timeout=10):
    """Send raw bytes on stdin. Returns (status, stdout bytes) without stripping anything."""
    try:
        done = subprocess.run([PATH], input=data, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, b"(timed out)"
    return done.returncode, done.stdout


def run_bytes_all(blobs):
    _ensure_command()
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(run_bytes, blobs))


def shape_problem(status, body):
    """None when (status, body) is a well-formed answer to a valid request, else the reason."""
    if status != 0:
        return f"exited with status {status}, expected 0"
    if not isinstance(body, dict) or set(body) != FIELDS:
        return f"expected an object with exactly {sorted(FIELDS)}, got {short(body)}"
    if type(body["ok"]) is not bool:
        return f"ok must be true or false, got {short(body['ok'])}"
    violations = body["violations"]
    if not isinstance(violations, list) or not all(isinstance(v, str) for v in violations):
        return f"violations must be a list of strings, got {short(violations)}"
    return None


def short(value, limit=90):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=True)
    text = text.encode("unicode_escape").decode("ascii") if isinstance(value, str) else text
    return text if len(text) <= limit else text[:limit - 3] + "..."


def rule_check(codes, cases, summary, extra=()):
    """Run (label, request, expected) cases and judge only the rule codes in `codes`.

    `expected` is the set of those codes the password must break (the others in `codes` must
    not appear), True/False when `codes` holds one code, or None to take it from the model.
    Reports a problem whenever the answer is malformed or a code is present/absent wrongly;
    `extra` holds problems the caller already found.
    """
    codes = (codes,) if isinstance(codes, str) else tuple(codes)
    requests = [request for _, request, _ in cases]
    results = call_all(requests)
    problems = list(extra)
    for (label, request, expected), (status, body) in zip(cases, results):
        if expected is None:
            model = breaks(request["password"], request["username"], request["banned"])
            expected = {c for c in codes if c in model}
        elif isinstance(expected, bool):
            expected = set(codes) if expected else set()
        reason = shape_problem(status, body)
        if reason:
            problems.append(f"{label} {short(request)}: {reason}")
            continue
        for code in codes:
            if (code in body["violations"]) != (code in expected):
                verb = "should" if code in expected else "should not"
                problems.append(f"{label} {short(request)}: {verb} break {code}, got {body['violations']}")
    finish(problems, summary.format(n=len(cases)))


# ---------------------------------------------------------------- seeded generators

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGIT = string.digits
PUNCT = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "
# Characters outside ASCII letters and digits: all are symbols under G2, some look like
# letters or digits, some change under Unicode case mapping, some are outside the BMP.
OTHER = ("\u00e9\u00c9\u00fc\u00dc\u00f1\u00d1\u00df\u00f8\u00d8\u00e5\u00c5\u00e7\u00c7\u00e6\u0153"
         "\u03a9\u03c9\u0416\u0436\u0431\u0663\u0664\u096b\u0967\uff11\uff12\uff21\uff22\uff41\uff42"
         "\u20ac\u00a3\u00a5\u00b0\u00b1\u00a7\u00b6\u2022\u2014\u2026\u00a0\t\n"
         "\U0001F600\U0001F642\U0001F389\U0001F680\U0001F98A\u4e2d\u6587\u5b57"
         "\u212a\u0130\u0131\u017f\ufb00\u1e9e")
POOLS = (LOWER, UPPER, DIGIT, PUNCT, OTHER)
# Non-ASCII look-alikes that Unicode case mapping (lower/upper/casefold) would confuse
# with ASCII letters; intent.md ignores only ASCII case, so these never match.
LOOKALIKE = {"k": "\u212a", "K": "\u212a", "s": "\u017f", "S": "\u017f", "i": "\u0131",
             "I": "\u0130", "e": "\u00e9", "E": "\u00c9", "a": "\u00e5", "o": "\u00f8"}
REGEXY = [".*", ".", "a.c", "[a-z]", "\\d", "\\w+", "(", ")", "+", "?", "^", "$", "|", "{2}",
          "%s", "{0}", "*", "[", "\\"]


def flip_case(rng, text, p=0.5):
    return "".join(c.swapcase() if c in string.ascii_letters and rng.random() < p else c for c in text)


def insert(rng, text, piece):
    i = rng.randint(0, len(text))
    return text[:i] + piece + text[i:]


def random_text(rng, length, pools):
    return "".join(rng.choice(rng.choice(pools)) for _ in range(length))


def random_length(rng):
    band = rng.random()
    if band < 0.30:
        return rng.randint(9, 15)
    if band < 0.55:
        return rng.randint(60, 69)
    if band < 0.70:
        return rng.randint(0, 8)
    if band < 0.90:
        return rng.randint(16, 59)
    return rng.randint(70, 140)


def random_username(rng):
    n = rng.choice([rng.randint(1, 3), rng.randint(3, 5), rng.randint(4, 8), rng.randint(4, 8),
                    rng.randint(9, 32)])
    return "".join(rng.choice(USERNAME_CHARS if rng.random() < 0.3 else string.ascii_letters)
                   for _ in range(n))


def lookalike(rng, text):
    spots = [i for i, c in enumerate(text) if c in LOOKALIKE]
    if not spots:
        return text
    i = rng.choice(spots)
    return text[:i] + LOOKALIKE[text[i]] + text[i + 1:]


def random_banned(rng, password):
    n = rng.choice([0, 0, 1, 1, 2, 3, 5, rng.randint(0, 20)])
    entries = []
    for _ in range(n):
        r = rng.random()
        if r < 0.35 and password:
            start = rng.randrange(len(password))
            piece = password[start:start + rng.randint(1, 6)]
            entries.append(flip_case(rng, piece))
        elif r < 0.50 and password:
            start = rng.randrange(len(password))
            piece = lookalike(rng, password[start:start + rng.randint(2, 6)])
            entries.append(piece.swapcase() if rng.random() < 0.3 else piece)
        elif r < 0.62:
            entries.append(rng.choice(REGEXY))
        else:
            entries.append(random_text(rng, rng.randint(1, 6), rng.sample(POOLS, rng.randint(1, 3))))
    return [e if e else "x" for e in entries]


def random_request(rng):
    """A valid request, biased so that every rule is broken in some cases and kept in others."""
    username = random_username(rng)
    pools = rng.sample(POOLS, rng.randint(1, 5))
    password = random_text(rng, random_length(rng), pools)
    if len(username) >= 4 and rng.random() < 0.35:
        size = rng.randint(4, min(len(username), 7))
        start = rng.randint(0, len(username) - size)
        password = insert(rng, password, flip_case(rng, username[start:start + size]))
    if len(username) >= 3 and rng.random() < 0.25:
        start = rng.randint(0, len(username) - 3)
        password = insert(rng, password, flip_case(rng, username[start:start + 3]))
    if len(username) >= 4 and rng.random() < 0.15:
        start = rng.randint(0, len(username) - 4)
        password = insert(rng, password, lookalike(rng, username[start:start + 4]))
    if rng.random() < 0.25:
        c = rng.choice(rng.choice(POOLS))
        password = insert(rng, password, c * rng.choice([3, 3, 4, 7]))
    if rng.random() < 0.25:
        c = rng.choice(string.ascii_letters)
        password = insert(rng, password, c + c.swapcase() + c)
    if rng.random() < 0.15:
        c = rng.choice(rng.choice(POOLS))
        password = insert(rng, password, c * 2)
    return {"password": password, "username": username, "banned": random_banned(rng, password)}


def generated(seed, count, label):
    rng = random.Random(seed)
    return [(f"{label} #{i}", random_request(rng), None) for i in range(count)]
