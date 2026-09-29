"""X4 (C2): a name with no letters once whitespace is tidied and leading honorifics removed
is refused, and a name with a letter left is not.

Honorifics are separated by ordinary spaces, so a fault in tidying other whitespace does
not show up here."""

from _audit import ask, is_refusal, is_result, show
from _cmd import finish
from _model import HONORIFICS, new_rng, rand_case

REFUSE = [
    "", "\u2003", " \t\r\n ", "\xa0\u3000\u2028",
    "Dr.", "Mr. Mrs.", "Mr. 42",
    "Prof", "SIR DAME", "mx. MISS ms MRS. mr dr. prof rev.", "  Ms.   ", "Miss. Mx.",
    "Dr. Mr", "Mr. Dr. Mrs",
    "42", "3.14", "-", "' . \u2019",
    "Rev. 1 2 3", "Prof. Dr. ---", "Dame (42)", "Mr. #1", "Dr. 007-42",
    "Dr. \xb2", "Dr. \xbd", "Mr. \u0663\u0664",   # superscript two, one half, Arabic-Indic digits
    "Mr. \u200b",                                      # a zero width space is not a letter
    "\u0301",                                          # a lone combining accent is not a letter
]
ACCEPT = [
    "Mr. 42 b", "Dr. x", "Mr. 42nd", "Mx. Ms. Sir Maren",
    "Dr. \xe9", "Dr. \u0434", "Dr. \u4e2d", "-a-", "Maren dr.", "Dr. Mr. 1a",
]

# Leading honorifics followed by words without letters, with a fixed seed.
rng = new_rng(4471)
generated = []
for _ in range(6):
    parts = [rand_case(rng, rng.choice(HONORIFICS)) + rng.choice(["", "."]) for _ in range(rng.randint(0, 3))]
    parts += ["".join(rng.choice("0123456789-.'#/()") for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(1, 2))]
    generated.append(" ".join(parts))

problems = []
for name in REFUSE + generated:
    status, body = ask(name)
    if not is_refusal(status, body):
        problems.append(f"{show(name)}: no letters left, expected a refusal (status 2), got status {status} and {body!r}")
for name in ACCEPT:
    status, body = ask(name)
    if status != 0 or not is_result(body):
        problems.append(f"{show(name)}: a letter is left, expected it accepted, got status {status} and {body!r}")

finish(problems, f"letterless names ok: {len(REFUSE) + len(generated)} refused, {len(ACCEPT)} accepted")
