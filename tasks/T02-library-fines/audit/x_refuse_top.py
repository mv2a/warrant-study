"""X04 (C3): refusal when the request is not a JSON object, or items is missing or not a list."""

from _audit import finish, item, refuse

problems = []

good = item("k1", "book", 2, 12)

# Not a JSON object (including text that is not JSON at all).
not_objects = {
    "array of items": '[{"id": "k1", "type": "book", "due_day": 2, "returned_day": 12}]',
    "empty array": "[]",
    "string": '"items"',
    "number": "17",
    "null": "null",
    "true": "true",
    "whitespace only": "   \n",
    "truncated object": '{"items": [',
    "single quotes": "{'items': []}",
    "trailing garbage": '{"items": []} {"items": []}',
    "bare word": "items",
    "NaN day (not JSON)": '{"items": [{"id": "k1", "type": "book", "due_day": NaN, "returned_day": 12}]}',
}
for label, text in not_objects.items():
    refuse(problems, label, raw=text)

# items missing or not a list.
refuse(problems, "empty object", {})
refuse(problems, "items misspelled", {"item": [good]})
refuse(problems, "items in capitals", {"ITEMS": [good]})
refuse(problems, "items null", {"items": None})
refuse(problems, "items object", {"items": {"k1": good}})
refuse(problems, "items is an item", {"items": good})
refuse(problems, "items string", {"items": "k1"})
refuse(problems, "items number", {"items": 0})
refuse(problems, "items false", {"items": False})

finish(problems, f"top-level refusals ok: {len(not_objects) + 9} requests")
