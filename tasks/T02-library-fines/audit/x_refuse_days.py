"""X06 (C3): refusal when due_day or returned_day is not a JSON integer of 0 or more."""


from _audit import finish, item, refuse

problems = []
count = 0

BAD_VALUES = {
    "-1": -1, "-30": -30, "-1000000": -1000000, "0.0": 0.0, "4.0": 4.0, "12.5": 12.5,
    "0.25": 0.25, "string 9": "9", "string 0": "0", "empty string": "", "true": True,
    "false": False, "null": None, "list": [9], "object": {"day": 9},
}
for kind in ("book", "dvd", "reference"):
    for field in ("due_day", "returned_day"):
        for label, bad in BAD_VALUES.items():
            entry = item("n1", kind, 8, 20)
            entry[field] = bad
            count += 1
            refuse(problems, f"{kind} {field} {label}", {"items": [entry]})

# Numbers written with an exponent or a fraction are not JSON integers, even when whole-valued.
for field in ("due_day", "returned_day"):
    for literal in ("1e1", "2E2", "1e+1", "5.00", "-0.0"):
        other = "returned_day" if field == "due_day" else "due_day"
        text = '{"items": [{"id": "n2", "type": "book", "%s": %s, "%s": 3}]}' % (field, literal, other)
        count += 1
        refuse(problems, f"{field} written {literal}", raw=text)

# Both fields bad at once, and a bad field on a later item.
count += 2
refuse(problems, "both fields negative", {"items": [item("n3", "dvd", -5, -1)]})
refuse(problems, "bad day on a later item", {"items": [
    item("n4", "book", 1, 40), item("n5", "dvd", 1, 40), item("n6", "reference", 3.5, 40)]})

finish(problems, f"day refusals ok: {count} requests")
