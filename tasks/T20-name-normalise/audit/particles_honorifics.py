"""X12 (G4): first and last word are counted after leading honorifics are removed."""

from _audit import display_of, show
from _cmd import finish

CASES = [
    ("Dr. van berg", "Van Berg"),
    ("Prof. von horst", "Von Horst"),
    ("Mr. amara di", "Amara Di"),
    ("Mrs. de la cruz", "De la Cruz"),
    ("Sir del", "Del"),
    ("Dame. mx. du pont", "Du Pont"),
    ("Dr. amara van berg", "Amara van Berg"),
    ("amara dr. van berg", "Amara Dr. van Berg"),
]

problems = []
for name, expected in CASES:
    display, error = display_of(name)
    if error:
        problems.append(f"{show(name)}: expected {show(expected)}, got {error}")
    elif display != expected:
        problems.append(f"{show(name)}: expected {show(expected)}, got {show(display)}")

finish(problems, f"particles after honorifics ok: {len(CASES)} names")
