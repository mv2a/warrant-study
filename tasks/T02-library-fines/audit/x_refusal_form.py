"""X03 (C1): the refusal side of the interface: status 2, nothing on stdout, a short reason on stderr
(at most 200 characters, not a traceback)."""


from _audit import finish, item, refuse

problems = []

# Clear-cut refusals of different kinds, each checked for the exact refusal form.
refuse(problems, "type 'tape'", {"items": [item("t1", "tape", 1, 9)]})
refuse(problems, "text that is not JSON", raw="items: none")
refuse(problems, "a JSON list at the top", [item("t2", "book", 1, 9)])
refuse(problems, "missing items", {"books": []})
refuse(problems, "empty id", {"items": [item("", "dvd", 1, 9)]})
refuse(problems, "negative returned_day", {"items": [item("t3", "book", 4, -2)]})
refuse(problems, "string due_day", {"items": [item("t4", "reference", "12", 20)]})
refuse(problems, "shared id", {"items": [item("t5", "book", 1, 9), item("t5", "dvd", 1, 9)]})

# A refusal in the middle of otherwise fine items still writes nothing at all on stdout.
refuse(problems, "late bad item", {"items": [
    item("u1", "book", 10, 90), item("u2", "dvd", 10, 90), item("u3", "reference", 10, 90),
    item("u4", "Reference", 10, 90),
]})

# Empty standard input is not a JSON object.
refuse(problems, "empty input", raw="")

# Long offending values: the reason stays within C1's 200 characters whatever the request holds.
long_id = "shelf-" + "q" * 294
refuse(problems, "shared 300-character id", {"items": [item(long_id, "dvd", 3, 8), item(long_id, "book", 3, 8)]})
refuse(problems, "300-character type", {"items": [item("t6", "periodical" * 30, 3, 8)]})
refuse(problems, "300-digit string due_day", {"items": [item("t7", "book", "9" * 300, 8)]})

finish(problems, "refusal form ok: status 2, no stdout, a reason of at most 200 characters on stderr")
