"""H7: invalid requests are refused as a whole, with no fines worked out (C3)."""

from _cmd import call, finish

GOOD = '{"id": "ok", "type": "book", "due_day": 1, "returned_day": 9}'


def with_item(fields):
    """A request holding one valid item and then the given item text."""
    return '{"items": [' + GOOD + ", " + fields + "]}"


INVALID = [
    ("text that isn't JSON", "three books and a DVD"),
    ("empty input", ""),
    ("a list instead of an object", "[" + GOOD + "]"),
    ("a number instead of an object", "42"),
    ("null instead of an object", "null"),
    ("no items field", '{"books": []}'),
    ("items that is an object", '{"items": ' + GOOD + "}"),
    ("items that is null", '{"items": null}'),
    ("items that is text", '{"items": "ok"}'),
    ("an item that is text", with_item('"b2"')),
    ("an item that is a list", with_item('["b2", "book", 1, 9]')),
    ("an item without id", with_item('{"type": "book", "due_day": 1, "returned_day": 9}')),
    ("an item without type", with_item('{"id": "b2", "due_day": 1, "returned_day": 9}')),
    ("an item without due_day", with_item('{"id": "b2", "type": "book", "returned_day": 9}')),
    ("an item without returned_day", with_item('{"id": "b2", "type": "book", "due_day": 1}')),
    ("an empty id", with_item('{"id": "", "type": "book", "due_day": 1, "returned_day": 9}')),
    ("a numeric id", with_item('{"id": 7, "type": "book", "due_day": 1, "returned_day": 9}')),
    ("a null id", with_item('{"id": null, "type": "book", "due_day": 1, "returned_day": 9}')),
    ("two items with the same id", with_item('{"id": "ok", "type": "dvd", "due_day": 1, "returned_day": 9}')),
    ('a type of "DVD"', with_item('{"id": "b2", "type": "DVD", "due_day": 1, "returned_day": 9}')),
    ('a type of "Book"', with_item('{"id": "b2", "type": "Book", "due_day": 1, "returned_day": 9}')),
    ('a type of "magazine"', with_item('{"id": "b2", "type": "magazine", "due_day": 1, "returned_day": 9}')),
    ("an empty type", with_item('{"id": "b2", "type": "", "due_day": 1, "returned_day": 9}')),
    ("a null type", with_item('{"id": "b2", "type": null, "due_day": 1, "returned_day": 9}')),
    ("a due_day of -1", with_item('{"id": "b2", "type": "book", "due_day": -1, "returned_day": 9}')),
    ("a returned_day of -5", with_item('{"id": "b2", "type": "book", "due_day": 1, "returned_day": -5}')),
    ("a due_day of 3.0", with_item('{"id": "b2", "type": "book", "due_day": 3.0, "returned_day": 9}')),
    ("a returned_day of 2.5", with_item('{"id": "b2", "type": "book", "due_day": 1, "returned_day": 2.5}')),
    ('a due_day of "7"', with_item('{"id": "b2", "type": "book", "due_day": "7", "returned_day": 9}')),
    ("a due_day of true", with_item('{"id": "b2", "type": "book", "due_day": true, "returned_day": 9}')),
    ("a returned_day of false", with_item('{"id": "b2", "type": "book", "due_day": 0, "returned_day": false}')),
    ("a returned_day of true", with_item('{"id": "b2", "type": "dvd", "due_day": 0, "returned_day": true}')),
    ("a due_day of null", with_item('{"id": "b2", "type": "book", "due_day": null, "returned_day": 9}')),
    ("a returned_day that is a list", with_item('{"id": "b2", "type": "book", "due_day": 1, "returned_day": [9]}')),
]

problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    priced = isinstance(body, dict) and ("total_cents" in body or "items" in body)
    if status != 2 or priced:
        problems.append(f"{name}: expected a refusal (status 2, no fines), got status {status} and {body!r}")

finish(problems, f"refusals ok: {len(INVALID)} invalid requests")
