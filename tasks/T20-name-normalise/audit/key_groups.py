"""X15 (G5): names that differ only in whitespace, case, leading honorifics, accents that
NFKD splits off, hyphens, apostrophes or full stops get the same key: four groups written
by hand and eight generated groups of three spellings, fixed seed."""

from _audit import key_of, show
from _cmd import finish
from _model import FAMILY, GIVEN, accent, honorific, new_rng, normalise, whitespace_run

GROUPS = [
    ("runalenaohara", ["Runa-Lena O'Hara", "runa lena ohara", "RUNA  LENA O\u2019HARA",
                       "Dr. Runa.Lena O Hara", "Mrs runa-lena o'hara", "\trUnA   lEnA\xa0o'hArA "]),
    ("jurgenmuller", ["J\xfcrgen M\xfcller", "jurgen muller", "Prof. J\xdcRGEN M\xdcLLER",
                      "Ju\u0308rgen Mu\u0308ller"]),
    ("zoesaldana", ["Zo\xeb Salda\xf1a", "zoe saldana", "Ms. ZO\xcb   SALDA\xd1A"]),
    ("asalenaost", ["\xc5sa-Lena \xd6st", "asa lena ost", "Dame \xe5sa.lena \xf6st"]),
]


def spelling(rng, words):
    """Respell plain words: case, accents, inner punctuation, joins, whitespace, honorifics."""
    out = []
    for w in words:
        chars = []
        for ch in w:
            ch = ch.upper() if rng.random() < 0.5 else ch
            chars.append(accent(rng, ch) if rng.random() < 0.3 else ch)
            if rng.random() < 0.08:
                chars.append(rng.choice("-'\u2019."))
        out.append("".join(chars))
    name = out[0]
    for w in out[1:]:
        name += (rng.choice("-'\u2019.") if rng.random() < 0.25 else whitespace_run(rng, 1, 3)) + w
    lead = "".join(honorific(rng) + whitespace_run(rng, 1, 2) for _ in range(rng.randint(0, 2)))
    return lead + name + whitespace_run(rng, 0, 2)


rng = new_rng(55219)
for _ in range(8):
    words = [rng.choice(GIVEN), rng.choice(FAMILY)] + ([rng.choice(FAMILY)] if rng.random() < 0.4 else [])
    expected = "".join(words)
    names = [spelling(rng, words) for _ in range(3)]
    for name in names:
        assert normalise(name)["key"] == expected, (name, expected)  # the generator's own promise
    GROUPS.append((expected, names))

problems = []
for expected, names in GROUPS:
    for name in names:
        key, error = key_of(name)
        if error:
            problems.append(f"{show(name)}: expected key {expected}, got {error}")
        elif key != expected:
            problems.append(f"{show(name)}: expected key {expected} like the rest of its group, got {show(key)}")

finish(problems, f"key groups ok: {len(GROUPS)} groups, {sum(len(n) for _, n in GROUPS)} spellings")
