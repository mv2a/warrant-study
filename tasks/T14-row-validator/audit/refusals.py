"""X10 (C4): every kind of malformed request listed in C4 is refused: status 2, nothing on stdout, a reason on stderr."""

import copy
import json

from _audit import refused
from _cmd import finish

# A well-formed schema and rows that hold errors, so validating instead of refusing would show up as output.
BASE = [
    {"name": "plot", "type": "integer", "required": True, "min": 1, "max": 400},
    {"name": "crop", "type": "string", "allowed": ["kale", "leek"]},
    {"name": "organic", "type": "boolean", "unique": False},
    {"name": "yield_kg", "type": "number", "min": 0},
]
ROWS = [{"plot": 3, "crop": "leek", "organic": True, "yield_kg": 12.5}, {"plot": 0, "crop": "Kale"}]


def with_rule(index, **changes):
    """BASE with one rule changed; a value of ... removes the key."""
    schema = copy.deepcopy(BASE)
    for key, value in changes.items():
        if value is ...:
            schema[index].pop(key, None)
        else:
            schema[index][key] = value
    return json.dumps({"schema": schema, "rows": ROWS})


def request(**parts):
    body = {"schema": BASE, "rows": ROWS}
    for key, value in parts.items():
        if value is ...:
            body.pop(key)
        else:
            body[key] = value
    return json.dumps(body)


GOOD = request()
CASES = {
    # text that isn't a JSON object
    "empty input": "",
    "only spaces and newlines": "  \n\t\n",
    "plain text": "validate these rows please",
    "truncated JSON": GOOD[: len(GOOD) // 2],
    "a JSON array": json.dumps([{"schema": BASE, "rows": ROWS}]),
    "a JSON string": json.dumps(GOOD),
    "a JSON number": "17",
    "JSON null": "null",
    "JSON true": "true",
    "an object followed by more text": GOOD + " trailing",
    "two objects in a row": GOOD + GOOD,
    "single-quoted pseudo-JSON": GOOD.replace('"', "'"),
    "NaN in a row, which JSON does not have": GOOD.replace("12.5", "NaN"),
    "Infinity in a row, which JSON does not have": GOOD.replace("12.5", "Infinity"),
    "-Infinity as a max, which JSON does not have": GOOD.replace('"max": 400', '"max": -Infinity'),
    "a comment inside the JSON": GOOD.replace('"rows":', '/* rows */ "rows":'),
    "a trailing comma": GOOD[:-1] + ", }",
    # a missing schema or rows, or any other top-level key
    "an empty object": "{}",
    "no schema": request(schema=...),
    "no rows": request(rows=...),
    "an extra top-level key": request(options={"strict": True}),
    "an extra top-level key set to null": request(comment=None),
    "Schema with a capital S instead of schema": json.dumps({"Schema": BASE, "rows": ROWS}),
    "rows spelled row": json.dumps({"schema": BASE, "row": ROWS}),
    # a schema that isn't a non-empty list of field rules
    "an empty schema": request(schema=[]),
    "a schema that is one rule, not a list": request(schema=BASE[0]),
    "a schema that is a string": request(schema="plot:integer"),
    "a schema that is null": request(schema=None),
    "a schema holding null": request(schema=[BASE[0], None]),
    "a schema holding a number": request(schema=[BASE[0], 4]),
    "a schema holding a string": request(schema=["plot"]),
    "a schema holding a list": request(schema=[BASE[0], [BASE[1]]]),
    "a schema holding an empty object": request(schema=[BASE[0], {}]),
    # a field rule with a missing, empty or repeated name
    "a rule without a name": with_rule(1, name=...),
    "a rule with an empty name": with_rule(1, name=""),
    "a rule whose name is null": with_rule(1, name=None),
    "a rule whose name is a number": with_rule(1, name=7),
    "a rule whose name is a list": with_rule(1, name=["crop"]),
    "a repeated name with the same type": request(schema=BASE + [dict(BASE[1])]),
    "a repeated name with another type": request(schema=BASE + [{"name": "plot", "type": "string"}]),
    # a missing or unknown type
    "a rule without a type": with_rule(2, type=...),
    "type date": with_rule(1, type="date"),
    "type Integer": with_rule(0, type="Integer"),
    "type int": with_rule(0, type="int"),
    "type float": with_rule(3, type="float"),
    "type bool": with_rule(2, type="bool"),
    "type str": with_rule(1, type="str"),
    "type with a trailing space": with_rule(1, type="string "),
    "an empty type": with_rule(1, type=""),
    "type null": with_rule(1, type=None),
    "type as a number": with_rule(1, type=1),
    "type as a list": with_rule(1, type=["string"]),
    # a key other than the seven named in C1
    "a rule with a pattern key": with_rule(1, pattern="^[a-z]+$"),
    "a rule with a default key": with_rule(3, default=0),
    "a rule with Required capitalised": with_rule(2, Required=True),
    "a rule with a description": with_rule(0, description="plot number"),
    "a rule with an unknown key set to null": with_rule(0, note=None),
    "a rule with maxLength": with_rule(1, maxLength=10),
    # a required or unique that isn't true or false
    "required 1": with_rule(1, required=1),
    "required 0": with_rule(1, required=0),
    "required as the text true": with_rule(1, required="true"),
    "required null": with_rule(1, required=None),
    "required as a list": with_rule(1, required=[True]),
    "unique 1": with_rule(0, unique=1),
    "unique as the text false": with_rule(0, unique="false"),
    "unique null": with_rule(0, unique=None),
    "unique 0.0": with_rule(0, unique=0.0),
    # a min or max that isn't a number
    "min as text": with_rule(0, min="1"),
    "max as text": with_rule(3, max="100"),
    "min true": with_rule(3, min=True),
    "max false": with_rule(0, max=False),
    "min null": with_rule(0, min=None),
    "max null": with_rule(3, max=None),
    "min as a list": with_rule(0, min=[1]),
    "max as an object": with_rule(3, max={"value": 9}),
    # a min or max on a string or boolean field
    "min on a string field": with_rule(1, min=0),
    "max on a string field": with_rule(1, max=10),
    "min on a boolean field": with_rule(2, min=0),
    "max on a boolean field": with_rule(2, max=1),
    "min and max on a string field": with_rule(1, min=1, max=5),
    # a min greater than its max
    "min 5 above max 4": with_rule(0, min=5, max=4),
    "min 401 above max 400": with_rule(0, min=401),
    "min 2.5 above max 2.4999": with_rule(3, min=2.5, max=2.4999),
    "min 0 above max -1": with_rule(3, max=-1),
    "min 1e300 above max 1e299": with_rule(3, min=1e300, max=1e299),
    # an allowed that isn't a non-empty list of values of the field's type
    "an empty allowed list": with_rule(1, allowed=[]),
    "allowed as a single string": with_rule(1, allowed="kale"),
    "allowed null": with_rule(1, allowed=None),
    "allowed as an object": with_rule(1, allowed={"kale": True}),
    "allowed string list holding a number": with_rule(1, allowed=["kale", 1]),
    "allowed string list holding null": with_rule(1, allowed=["kale", None]),
    "allowed string list holding true": with_rule(1, allowed=[True, "kale"]),
    "allowed string list holding a list": with_rule(1, allowed=[["kale"]]),
    "allowed integer list holding 2.5": with_rule(0, allowed=[1, 2.5]),
    "allowed integer list holding text": with_rule(0, allowed=[1, "2"]),
    "allowed integer list holding true": with_rule(0, allowed=[True]),
    "allowed integer list holding false and 0": with_rule(0, allowed=[0, False]),
    "allowed number list holding true": with_rule(3, allowed=[1.5, True]),
    "allowed number list holding text": with_rule(3, allowed=["1.5"]),
    "allowed number list holding null": with_rule(3, allowed=[None]),
    "allowed boolean list holding 1": with_rule(2, allowed=[1]),
    "allowed boolean list holding 0 and true": with_rule(2, allowed=[True, 0]),
    "allowed boolean list holding text": with_rule(2, allowed=["true"]),
    # rows that isn't a list of objects
    "rows as an object": request(rows=ROWS[0]),
    "rows as a string": request(rows="plot,crop"),
    "rows null": request(rows=None),
    "rows as a number": request(rows=2),
    "rows holding a number": request(rows=ROWS + [5]),
    "rows holding null": request(rows=[None] + ROWS),
    "rows holding a list": request(rows=[ROWS[0], [3, "kale"]]),
    "rows holding a string": request(rows=ROWS + ["plot=4"]),
    "rows holding true": request(rows=[True]),
}

problems = []
for label, text in CASES.items():
    refused(problems, label, text)

finish(problems, f"refusals ok: {len(CASES)} malformed requests refused")
