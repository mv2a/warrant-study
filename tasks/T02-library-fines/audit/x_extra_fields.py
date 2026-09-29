"""X02 (C1): fields other than the promised ones are ignored, at the top level and in items."""

from _audit import finish, item, succeed

problems = []

base = [item("e1", "book", 50, 61), item("e2", "dvd", 50, 80), item("e3", "reference", 50, 53)]
plain = {"items": base}

# Extra top-level fields, including ones named like output fields or that look invalid.
succeed(problems, "extra top-level fields", {
    "items": base, "borrower": "anon", "total_cents": 1, "Items": "not a list", "branch": None,
})

# Extra item fields, including output-like names and fields that differ from real ones only in case.
decorated = [
    item("e1", "book", 50, 61, title="A novel", fine_cents=-7, days_late=999),
    item("e2", "dvd", 50, 80, Type="book", DUE_DAY=-1, returned=True, notes=[1, 2]),
    item("e3", "reference", 50, 53, renewals=3, lost=None, borrower={"kind": "child"}),
]
succeed(problems, "extra item fields", {"items": decorated}, want=None)

# The extra fields change nothing: same response as without them.
succeed(problems, "extra fields at both levels",
        {"items": decorated, "account": {"id": 5}, "currency": "EUR"},
        want=None)

# An empty list with extra top-level fields.
succeed(problems, "empty list with extras", {"items": [], "note": "nothing borrowed"},
        want={"items": [], "total_cents": 0})

# Sanity: the undecorated request itself.
succeed(problems, "plain request", plain)

finish(problems, "extra fields ok: ignored at both levels")
