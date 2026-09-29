"""X7 (G2): runs of leading honorifics are all removed, removal stops at the first word that
is not an honorific, near-miss words are kept, and honorifics later in the name are kept.

Words are separated by single spaces and only the words of the display name are compared,
ignoring case, so faults in whitespace tidying or capitalisation do not show up here."""

from _audit import display_of, show
from _cmd import finish
from _model import new_rng, honorific

problems = []


def expect_words(name, words):
    display, error = display_of(name)
    if error:
        problems.append(f"{show(name)}: expected words {words}, got {error}")
    elif [w.casefold() for w in display.split(" ")] != [w.casefold() for w in words]:
        problems.append(f"{show(name)}: expected words {words}, got {show(display)}")


# Several honorifics in a row, with a fixed seed.
rng = new_rng(70561)
for _ in range(8):
    lead = [honorific(rng) for _ in range(rng.randint(2, 4))]
    name = "".join(h + " " for h in lead) + "selin novak"
    expect_words(name, ["selin", "novak"])
expect_words("REV. SIR dame. MX selin novak", ["selin", "novak"])

# Words that only look like honorifics are kept, and so is everything after them.
NEAR = ["Dr..", "Drs", "Doctor", "Mister", "Mrs..", "Profs", "Prof..", "Sirs", "Dames", "Revd",
        "Mz", "D.r.", "Dr,", "Dr-", ".Dr", "Madam"]
for word in NEAR:
    expect_words(f"{word} selin novak", [word, "selin", "novak"])
expect_words("Dr.selin novak", ["dr.selin", "novak"])
expect_words("Mr.Mrs. selin", ["mr.mrs.", "selin"])

# Removal stops at the first word that is not an honorific.
expect_words("Prof. Dr.. selin", ["dr..", "selin"])
expect_words("Mr Doctor Mrs selin", ["doctor", "mrs", "selin"])
expect_words("Dr. selin dr. novak", ["selin", "dr.", "novak"])

# Honorifics after the first word are ordinary words.
expect_words("selin MR. novak", ["selin", "mr.", "novak"])
expect_words("selin novak PROF", ["selin", "novak", "prof"])
expect_words("selin sir dame novak", ["selin", "sir", "dame", "novak"])
expect_words("selin novak rev.", ["selin", "novak", "rev."])

finish(problems, "honorific boundaries ok")
