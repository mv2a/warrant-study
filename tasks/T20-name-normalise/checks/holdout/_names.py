"""Word pools and small helpers shared by the holdout checks. Expectations are built
from how each test name is constructed, not by re-running a normaliser."""

HONORIFICS = ["Mr", "Mrs", "Ms", "Miss", "Mx", "Dr", "Prof", "Rev", "Sir", "Dame"]
PARTICLES = ["da", "de", "del", "della", "der", "di", "du", "la", "le", "van", "von"]

# Plain lower-case words: never a particle or an honorific, with or without a full stop.
WORDS = [
    "anna", "weber", "maria", "okafor", "jonas", "lindqvist", "priya", "raman", "tomasz",
    "nowak", "chiara", "bianchi", "kwame", "mensah", "ingrid", "halvorsen", "mateo", "ruiz",
    "yusuf", "demir", "aoife", "brennan", "lucas", "fontaine", "hana", "sato", "oskar",
    "berglund", "amara", "nwosu", "felix", "hartmann", "leila", "haddad", "tariq", "qureshi",
    "noor", "rahman", "emil", "strand", "olga", "petrova", "ravi", "menon", "sofia", "costa",
]


def cap(word):
    """Capitalise a word made only of letters: first upper, the rest lower."""
    return word[:1].upper() + word[1:].lower()


def recase(rng, word):
    """The same word in a random mix of upper and lower case."""
    style = rng.randrange(4)
    if style == 0:
        return word.lower()
    if style == 1:
        return word.upper()
    if style == 2:
        return cap(word)
    return "".join(c.upper() if rng.random() < 0.5 else c.lower() for c in word)
