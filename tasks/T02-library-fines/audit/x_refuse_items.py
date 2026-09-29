"""X05 (C3): refusal for items that are not objects, lack a field, have a bad id, share an id, or a bad type."""

from _audit import TYPES, finish, item, refuse

problems = []
count = 0


def check(label, items):
    global count
    count += 1
    refuse(problems, label, {"items": items})


ok = item("m0", "dvd", 30, 45)

# An item that is not an object.
for label, bad in {"number": 12, "string": "m1", "null": None, "list": ["m1", "book", 1, 5],
                   "true": True, "empty list": []}.items():
    check(f"item is {label}", [ok, bad])

# An item lacking any one of its four fields, for every type.
for kind in TYPES:
    for field in ("id", "type", "due_day", "returned_day"):
        entry = item("m2", kind, 5, 15)
        del entry[field]
        check(f"{kind} lacking {field}", [entry])
check("empty object item", [{}])
check("lacking id and type", [{"due_day": 1, "returned_day": 4}])

# An id that is not a non-empty string.
for label, bad in {"empty": "", "integer": 7, "zero": 0, "null": None, "false": False,
                   "list": ["m3"], "object": {"id": "m3"}, "float": 1.5}.items():
    check(f"id {label}", [ok, item(bad, "book", 5, 15)])

# Two (or more) items sharing an id, adjacent or not, same or different types.
check("adjacent duplicate", [item("dup", "book", 1, 2), item("dup", "book", 1, 2)])
check("far duplicate", [item("a1", "book", 1, 2), item("a2", "dvd", 1, 2),
                        item("a3", "reference", 1, 2), item("a1", "reference", 9, 90)])
check("triple duplicate", [item("z", "dvd", 0, 1), item("z", "dvd", 0, 1), item("z", "dvd", 0, 1)])
check("duplicate of a number-like id", [item("10", "book", 0, 50), item("10", "dvd", 0, 50)])

# A type that is not exactly book, dvd or reference.
for bad in ("DVD", "Book", "BOOK", "Reference", " book", "book ", "dvd\n", "ref", "references",
            "books", "cd", "magazine", "", "b"):
    check(f"type {bad!r}", [item("m4", bad, 5, 15)])
for label, bad in {"null": None, "number": 1, "list": ["book"], "object": {"type": "dvd"},
                   "true": True}.items():
    check(f"type {label}", [item("m5", bad, 5, 15)])

finish(problems, f"item refusals ok: {count} requests")
