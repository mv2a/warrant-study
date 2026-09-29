"""X11 (G4): parts of hyphenated words and words that only resemble particles are
capitalised, and first and last are counted on the tidied words.

Names are sent in lower case with ordinary spaces, so the check does not depend on G3
lower-casing the rest of a word or on G1 handling other whitespace."""

from _audit import display_of, show
from _cmd import finish

CASES = [
    # Parts of a hyphenated word are never particles.
    ("amara-de-la-cruz", "Amara-De-La-Cruz"),
    ("amara van-der-berg", "Amara Van-Der-Berg"),
    ("teodor de-la cruz", "Teodor De-La Cruz"),
    ("amara von-der okafor", "Amara Von-Der Okafor"),
    # Words that are not one of the eleven particles.
    ("amara dos santos", "Amara Dos Santos"),
    ("amara des pres", "Amara Des Pres"),
    ("amara den berg", "Amara Den Berg"),
    ("amara ten broek", "Amara Ten Broek"),
    ("amara ter horst", "Amara Ter Horst"),
    ("amara y castillo", "Amara Y Castillo"),
    ("amara zu berg", "Amara Zu Berg"),
    ("amara dei rossi", "Amara Dei Rossi"),
    ("amara vander berg", "Amara Vander Berg"),
    ("amara dela cruz", "Amara Dela Cruz"),
    ("amara dellas okafor", "Amara Dellas Okafor"),
    ("amara vanessa okafor", "Amara Vanessa Okafor"),
    ("amara van. berg", "Amara Van. Berg"),
    ("amara du. pont", "Amara Du. Pont"),
    # First and last are counted on the words, not on empty strings around them.
    ("amara van   ", "Amara Van"),
    ("  van berg  ", "Van Berg"),
    ("amara van 3", "Amara van 3"),
    ("amara VON -", "Amara von -"),
]

problems = []
for name, expected in CASES:
    display, error = display_of(name)
    if error:
        problems.append(f"{show(name)}: expected {show(expected)}, got {error}")
    elif display != expected:
        problems.append(f"{show(name)}: expected {show(expected)}, got {show(display)}")

finish(problems, f"particle edge cases ok: {len(CASES)} names")
