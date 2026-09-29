"""An independent model of intent.md, used by the hidden checks to compute expected answers."""

import re

CODES = ("banned", "classes", "repeat", "too_long", "too_short", "username")

# Pools for generated passwords. Non-ASCII letters and digits are symbols under G2.
LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGIT = "0123456789"
SYMBOL = "!#$%&*+-./:;=?@_~ " + "\u00e9\u00c9\u00df\u03a9\u0663\u4e2d\uff21\U0001f600"
USERNAME_CHARS = LOWER + UPPER + DIGIT + "._-"


def fold(text):
    """Lower-case ASCII letters only; every other character stays as it is."""
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in text)


def char_class(c):
    if "a" <= c <= "z":
        return "lower"
    if "A" <= c <= "Z":
        return "upper"
    if "0" <= c <= "9":
        return "digit"
    return "symbol"


def breaks_classes(password):
    return len({char_class(c) for c in password}) < 3


def breaks_username(password, username):
    p, u = fold(password), fold(username)
    return any(u[i:i + 4] in p for i in range(len(u) - 3))


def breaks_repeat(password):
    return re.search(r"(.)\1\1", password, re.DOTALL) is not None


def breaks_banned(password, banned):
    p = fold(password)
    return any(fold(entry) in p for entry in banned)


def expected(password, username, banned):
    found = []
    if len(password) < 12:
        found.append("too_short")
    if len(password) > 64:
        found.append("too_long")
    if breaks_classes(password):
        found.append("classes")
    if breaks_username(password, username):
        found.append("username")
    if breaks_repeat(password):
        found.append("repeat")
    if breaks_banned(password, banned):
        found.append("banned")
    return sorted(found)


def violations_of(body):
    """The violations list from a response, or None when the response has no such list."""
    if isinstance(body, dict) and isinstance(body.get("violations"), list):
        return body["violations"]
    return None


def random_password(rng, low, high, pools=(LOWER, UPPER, DIGIT, SYMBOL)):
    pool = "".join(pools)
    return "".join(rng.choice(pool) for _ in range(rng.randint(low, high)))


def random_username(rng, low=1, high=32):
    return "".join(rng.choice(USERNAME_CHARS) for _ in range(rng.randint(low, high)))


def flip_case(rng, text):
    return "".join(c.swapcase() if c.isascii() and c.isalpha() and rng.random() < 0.5 else c for c in text)
