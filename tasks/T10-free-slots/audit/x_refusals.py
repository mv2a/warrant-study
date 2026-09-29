"""X11 (C4): invalid requests are refused, and valid requests right next to them are answered.

A refusal here means exit status 2 with no answer on standard output. The exact form of a
refusal (nothing at all on standard output, a reason on standard error) is checked by X1.
"""

import json

from _cmd import call, finish

BASE = {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660]], [[700, 760]]]}
TEXT = json.dumps(BASE)


def with_(**fields):
    """BASE with some fields replaced. A replaced busy list gets quorum 1, which any group of
    at least one person allows, unless the quorum is given too, so that the refusal is for
    the field under test."""
    request = dict(BASE)
    if "busy" in fields and "quorum" not in fields:
        request["quorum"] = 1
    request.update(fields)
    return json.dumps(request)


def without(field):
    return json.dumps({k: v for k, v in BASE.items() if k != field})


REFUSE = []  # (label, raw text)

# Not JSON, or not one JSON object.
for label, text in [
    ("empty input", ""),
    ("blank input", " \n\t\n"),
    ("a plain word", "slots"),
    ("an unclosed object", '{"workday": [540, 1020]'),
    ("a truncated request", TEXT[:-1]),
    ("single quotes", TEXT.replace('"', "'")),
    ("a trailing comma", TEXT[:-1] + ", }"),
    ("text after the object", TEXT + " please"),
    ("two objects", TEXT + "\n" + TEXT),
    ("NaN as a start", '{"workday": [NaN, 1020], "min_length": 30, "busy": [[]]}'),
    ("Infinity as min_length", '{"workday": [540, 1020], "min_length": Infinity, "busy": [[]]}'),
    ("a JSON list holding the request", json.dumps([BASE])),
    ("an empty JSON list", "[]"),
    ("a JSON string", json.dumps(TEXT)),
    ("a JSON number", "42"),
    ("JSON null", "null"),
    ("JSON true", "true"),
]:
    REFUSE.append((label, text))

# Missing fields.
for field in ("workday", "min_length", "quorum", "busy"):
    REFUSE.append((f"no {field}", without(field)))
REFUSE.append(("an empty object", "{}"))
REFUSE.append(("the fields nested one level down", json.dumps({"request": BASE})))
REFUSE.append(("misspelled field names", json.dumps({"Workday": [540, 1020], "min_length": 30, "quorum": 1, "busy": [[]]})))
REFUSE.append(("quorum spelled as the number of people required", json.dumps({"workday": [540, 1020], "min_length": 30, "required": 1, "busy": [[]]})))

# Bad [start, end] values, tried both as the workday and as a busy interval.
BAD_INTERVALS = [
    ("null", None),
    ("a number", 600),
    ("text", "600-660"),
    ("an object", {"start": 600, "end": 660}),
    ("an empty list", []),
    ("one number", [600]),
    ("three numbers", [600, 660, 700]),
    ("a start with a decimal point", [600.0, 660]),
    ("an end with a decimal point", [600, 660.0]),
    ("a fractional start", [600.5, 660]),
    ("text numbers", ["600", "660"]),
    ("true as a start", [True, 660]),
    ("false as a start", [False, 660]),
    ("true as an end", [0, True]),
    ("null as a start", [None, 660]),
    ("a reversed interval", [660, 600]),
    ("an empty interval", [600, 600]),
    ("an empty interval at 0", [0, 0]),
    ("an empty interval at 1440", [1440, 1440]),
    ("a negative start", [-1, 660]),
    ("both ends negative", [-60, -30]),
    ("an end past 1440", [600, 1441]),
    ("a start at 1440", [1440, 1441]),
    ("a huge end", [0, 10 ** 18]),
    ("nested lists", [[600], [660]]),
    ("a list holding the interval", [[600, 660]]),
]
for label, bad in BAD_INTERVALS:
    REFUSE.append((f"workday is {label}", with_(workday=bad)))
    REFUSE.append((f"a busy interval is {label}", with_(busy=[[[600, 660]], [[700, 760], bad]])))
# A bad interval refuses the request even when it sits outside the working hours or
# when nothing could be long enough anyway.
REFUSE.append(("a reversed interval before the working hours", with_(busy=[[[100, 50]], []])))
REFUSE.append(("an interval past 1440 after the working hours", with_(busy=[[], [[1400, 1500]]])))
REFUSE.append(("a negative interval before the working hours", with_(busy=[[[-30, 30]]])))
REFUSE.append(("a bad interval with a huge min_length", with_(min_length=5000, busy=[[[660, 600]]])))
REFUSE.append(("a bad interval behind many good ones", with_(busy=[[[s, s + 5]] for s in range(0, 1400, 10)] + [[[700, 700.5]]])))

# Bad min_length values.
for label, bad in [
    ("0", 0), ("-1", -1), ("-30", -30), ("30.0", 30.0), ("1.0", 1.0), ("29.5", 29.5), ("0.5", 0.5),
    ("text", "30"), ("true", True), ("false", False), ("null", None), ("a list", [30]), ("an object", {"minutes": 30}),
]:
    REFUSE.append((f"min_length is {label}", with_(min_length=bad)))

# Bad quorum values: not a whole number, below 1, or more people than busy lists.
for label, bad, busy in [
    ("0", 0, None), ("-1", -1, None), ("-2", -2, None), ("3, with two people", 3, None),
    ("2, with one person", 2, [[[600, 660]]]), ("4, with three people", 4, [[], [], []]),
    ("2, with one person free all day", 2, [[]]), ("a huge number", 10 ** 12, None),
    ("2.0", 2.0, None), ("1.0", 1.0, None), ("1.5", 1.5, None), ("text", "2", None), ("true", True, None),
    ("false", False, None), ("null", None, None), ("a list", [2], None), ("an object", {"people": 2}, None),
    ("a list of names", ["ana", "bo"], None),
]:
    fields = {"quorum": bad} if busy is None else {"quorum": bad, "busy": busy}
    REFUSE.append((f"quorum is {label}", with_(**fields)))

# Bad busy values and bad entries for a person.
for label, bad in [
    ("null", None), ("an object", {"ana": [[600, 660]]}), ("text", "busy"), ("a number", 5), ("true", True),
    ("an empty list, naming no one", []),
    ("a person who is null", [None]),
    ("a person who is an object", [{"busy": [[600, 660]]}]),
    ("a person who is text", ["600-660"]),
    ("a person who is a number", [5]),
    ("a person who is true", [True]),
    ("a second person who is null", [[], None]),
    ("a third person who is an object", [[[600, 660]], [], {"start": 700, "end": 760}]),
    ("one interval without the person list around it", [[600, 660]]),
    ("two intervals without the person list around them", [[600, 660], [700, 760]]),
    ("intervals nested one level too deep", [[[[600, 660]]]]),
]:
    REFUSE.append((f"busy is {label}", with_(busy=bad)))

# Valid requests at the edges of what C4 allows: these are answered.
ANSWER = [
    ("the whole day as working hours", with_(workday=[0, 1440])),
    ("working hours of one minute at the start of the day", with_(workday=[0, 1], min_length=1)),
    ("working hours of one minute at the end of the day", with_(workday=[1439, 1440], min_length=1)),
    ("busy intervals at minute 0 and minute 1440", with_(busy=[[[0, 1]], [[1439, 1440]]])),
    ("a busy interval covering the whole day", with_(busy=[[[0, 1440]]])),
    ("busy intervals entirely outside the working hours", with_(busy=[[[0, 60]], [[1300, 1440]]])),
    ("min_length 1", with_(min_length=1)),
    ("min_length 1440", with_(min_length=1440)),
    ("min_length 1441", with_(min_length=1441)),
    ("min_length of a million", with_(min_length=10 ** 6)),
    ("min_length of 10**18", with_(min_length=10 ** 18)),
    ("one person with no busy intervals", with_(busy=[[]])),
    ("three people with no busy intervals", with_(busy=[[], [], []])),
    ("repeated and nested intervals", with_(busy=[[[600, 700], [600, 700], [620, 640]]])),
    ("quorum 1", with_(quorum=1)),
    ("quorum equal to the number of people", with_(quorum=2)),
    ("quorum equal to a group of five, three free all day", with_(quorum=5, busy=[[], [[600, 660]], [], [[0, 1440]], []])),
    ("quorum 1 of a hundred people", with_(quorum=1, busy=[[[600, 660]]] * 100)),
]

problems = []
for label, text in REFUSE:
    status, body = call(raw=text)
    if status != 2 or (isinstance(body, dict) and "slots" in body):
        problems.append(f"{label}: expected a refusal (status 2, no answer), got status {status} and {str(body)[:60]}")
for label, text in ANSWER:
    status, body = call(raw=text)
    if status != 0 or not (isinstance(body, dict) and isinstance(body.get("slots"), list)):
        problems.append(f"{label} is valid: expected an answer with status 0, got status {status} and {str(body)[:60]}")

finish(problems, f"refusals ok: {len(REFUSE)} invalid requests refused, {len(ANSWER)} valid ones answered")
