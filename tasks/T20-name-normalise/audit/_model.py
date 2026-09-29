"""Audit model: an independent reading of intent.md, used to work out expected answers.

Written from intent.md alone. The generators below only produce names whose answer the
intent settles without doubt: they never use a final capital sigma, a dotted or dotless I,
a sharp s where G3 would upper-case it, a character whose case mapping is more than one
character, or a character that some libraries count as whitespace and Unicode does not.
intent.md puts all of these out of scope except the dotless i, which is avoided anyway.
"""

import random
import unicodedata

HONORIFICS = ("mr", "mrs", "ms", "miss", "mx", "dr", "prof", "rev", "sir", "dame")
PARTICLES = ("da", "de", "del", "della", "der", "di", "du", "la", "le", "van", "von")
BREAKS = "-'\u2019."  # G3: a character right after one of these is upper-cased

# Every character with the Unicode White_Space property (25 of them).
WHITESPACE = (
    "\t\n\x0b\x0c\r \x85\xa0\u1680"
    "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
    "\u2028\u2029\u202f\u205f\u3000"
)
assert len(WHITESPACE) == 25

# Invented names, none of them a particle or an honorific.
GIVEN = ["maren", "tobias", "ilse", "kofi", "amara", "yusuf", "lena", "oskar", "priya",
         "tomasz", "ines", "rafael", "selin", "bram", "nadia", "hugo", "freya", "emil",
         "zara", "wim", "odile", "casimir", "runa", "teodor"]
FAMILY = ["kowalski", "haddad", "lindqvist", "okafor", "moreau", "brandt", "castillo",
          "nakamura", "fischer", "rossi", "jansen", "petrov", "silva", "duarte", "novak",
          "hughes", "keane", "bauer", "okonkwo", "varga", "berg", "cruz", "horst", "pont"]
for _w in GIVEN + FAMILY:
    assert _w not in PARTICLES and _w not in HONORIFICS

# Letters that NFKD splits into an ASCII letter and accent marks.
ACCENTED = {
    "a": "\xe1\xe0\xe2\xe4\xe3\xe5\u0101\u0103\u0105", "e": "\xe9\xe8\xea\xeb\u0113\u011b\u0119", "i": "\xed\xec\xee\xef", "o": "\xf3\xf2\xf4\xf6\xf5\u0151", "u": "\xfa\xf9\xfb\xfc\u016f\u0171",
    "n": "\xf1\u0144\u0148", "c": "\xe7\u0107\u010d", "s": "\u015b\u0161\u015f", "z": "\u017a\u017c\u017e", "y": "\xfd\xff", "r": "\u0159", "g": "\u011f",
}
MARKS = "\u0300\u0301\u0302\u0303\u0308\u030a\u030c"  # combining grave, acute, ...


def is_letter(ch):
    return unicodedata.category(ch).startswith("L")


def split_words(name):
    """G1: the words are the runs of non-whitespace characters."""
    words, current = [], []
    for ch in name:
        if ch in WHITESPACE:
            if current:
                words.append("".join(current))
                current = []
        else:
            current.append(ch)
    if current:
        words.append("".join(current))
    return words


def is_honorific(word):
    """G2: a whole word, any case, with or without exactly one trailing full stop."""
    bare = word[:-1] if word.endswith(".") else word
    return bare.lower() in HONORIFICS


def capitalise(word):
    """G3: upper-case the first character and any character right after - ' \u2019 or ."""
    out = []
    for i, ch in enumerate(word):
        out.append(ch.upper() if i == 0 or word[i - 1] in BREAKS else ch.lower())
    return "".join(out)


def key_of(display):
    """G5: NFKD, lower-case character by character, keep only letters."""
    lowered = "".join(ch.lower() for ch in unicodedata.normalize("NFKD", display))
    return "".join(ch for ch in lowered if is_letter(ch))


def normalise(name):
    """The whole intent: None for a refused name, else {"display": ..., "key": ...}."""
    if len(name) > 100:
        return None
    words = split_words(name)
    while words and is_honorific(words[0]):
        words.pop(0)
    if not any(is_letter(ch) for word in words for ch in word):
        return None
    last = len(words) - 1
    shown = [w.lower() if 0 < i < last and w.lower() in PARTICLES else capitalise(w)
             for i, w in enumerate(words)]
    display = " ".join(shown)
    return {"display": display, "key": key_of(display)}


# ---- generators --------------------------------------------------------------------

def rand_case(rng, text):
    return "".join(ch.upper() if rng.random() < 0.5 else ch.lower() for ch in text)


def whitespace_run(rng, lo, hi):
    return "".join(rng.choice(WHITESPACE) for _ in range(rng.randint(lo, hi)))


def honorific(rng):
    word = rand_case(rng, rng.choice(HONORIFICS))
    return word + "." if rng.random() < 0.5 else word


def accent(rng, ch):
    """Give a plain ASCII letter an accent, composed or decomposed, keeping its case."""
    base = ch.lower()
    if base in ACCENTED and rng.random() < 0.6:
        new = rng.choice(ACCENTED[base])
    elif base.isalpha():
        new = base + rng.choice(MARKS)
    else:
        return ch
    return new.upper() if ch.isupper() else new


def check_alphabet(chars):
    for ch in chars:
        assert len(ch.upper()) == 1 and len(ch.lower()) == 1, repr(ch)
        assert ch not in WHITESPACE and not ch.isspace(), repr(ch)


def new_rng(seed):
    return random.Random(seed)
