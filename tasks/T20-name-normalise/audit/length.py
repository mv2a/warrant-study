"""X3 (C2): the 100-code-point limit, counted on the name as sent, before any tidying."""

from _audit import ask, is_refusal, is_result, show
from _cmd import finish
from _model import new_rng

WIDE = "\U00020000"  # a CJK ideograph outside the Basic Multilingual Plane: one code point
ACCEPT = [
    "k" * 100,
    "Maren " * 16 + "Kofi",                # 100 with single spaces
    " " * 70 + "Lena" + " " * 26,          # mostly whitespace, tidies to 4 characters
    "Dr. " + "o" * 96,                     # the honorific counts
    WIDE * 100,                            # 100 code points, 200 UTF-16 units
    "e\u0301" * 50,                        # 100 code points, 50 once composed
    "\xe9" * 100,
    "ab\t" * 33 + "a",
]
REFUSE = [
    "k" * 101,
    " " + "k" * 100,                       # leading whitespace counts
    "Lena" + " " * 97,                     # trailing whitespace counts
    "Dr. " + "o" * 97,
    WIDE * 101,
    "e\u0301" * 50 + "x",                  # 101 code points, 51 once composed
    "ab\t" * 33 + "ab",
    "k" * 100 + "\n",
    "Maren Okafor " * 80,
]
for name in ACCEPT:
    assert len(name) == 100, (show(name), len(name))
for name in REFUSE:
    assert len(name) > 100, (show(name), len(name))

# Names of 97 to 104 code points built from letters, spaces and tabs, with a fixed seed.
rng = new_rng(20260929)
generated = []
for _ in range(10):
    size = rng.randint(97, 104)
    chars = [rng.choice("abcdefghijklmnopqrstuvwxyz") if rng.random() < 0.8 else rng.choice(" \t") for _ in range(size)]
    chars[0] = "q"
    generated.append("".join(chars))

problems = []
for name in ACCEPT + [n for n in generated if len(n) <= 100]:
    status, body = ask(name)
    if status != 0 or not is_result(body):
        problems.append(f"{len(name)} code points {show(name, 40)}: expected it accepted, got status {status} and {body!r}"[:200])
for name in REFUSE + [n for n in generated if len(n) > 100]:
    status, body = ask(name)
    if not is_refusal(status, body):
        problems.append(f"{len(name)} code points {show(name, 40)}: expected a refusal (status 2), got status {status}")

finish(problems, f"length limit ok: {len(ACCEPT) + len(REFUSE) + len(generated)} names")
