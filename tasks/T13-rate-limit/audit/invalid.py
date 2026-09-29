"""X2 (C4): invalid requests are refused with status 2 and no output; the valid boundaries are not."""

import json

from _cmd import call, finish
from _model import short

problems = []
ENTRY = '{"client": "kiosk", "at": 5}'


def doc(burst="2", rate="3", requests="[" + ENTRY + "]"):
    """Build request text by hand, so numbers can be written exactly as the case needs."""
    parts = []
    if burst is not None:
        parts.append(f'"burst": {burst}')
    if rate is not None:
        parts.append(f'"rate": {rate}')
    if requests is not None:
        parts.append(f'"requests": {requests}')
    return "{" + ", ".join(parts) + "}"


def entry(client='"kiosk"', at="5"):
    parts = []
    if client is not None:
        parts.append(f'"client": {client}')
    if at is not None:
        parts.append(f'"at": {at}')
    return "{" + ", ".join(parts) + "}"


cases = []
# Input that isn't a JSON object.
for label, raw in (("empty input", ""), ("only whitespace", "  \n "), ("an unfinished object", '{"burst": 2'),
                   ("plain words", "burst=2 rate=3"), ("an empty list", "[]"), ("a list holding a request", "[" + doc() + "]"),
                   ("null", "null"), ("a number", "7"), ("a string", '"{}"'), ("true", "true"),
                   ("single-quoted keys", "{'burst': 2, 'rate': 3, 'requests': []}"),
                   ("an object followed by other text", doc() + " trailing"),
                   ("two objects one after another", doc() + "\n" + doc())):
    cases.append((label, raw))

# burst and rate: missing, not an integer, or less than 1.
BAD_NUMBERS = [("null", "null"), ("a string", '"2"'), ("2.0", "2.0"), ("1.0", "1.0"), ("2.5", "2.5"),
               ("1e3", "1e3"), ("1E+2", "1E+2"), ("5e0", "5e0"), ("true", "true"), ("false", "false"),
               ("0", "0"), ("-4", "-4"), ("a list", "[2]"), ("an object", '{"n": 2}'),
               ("NaN", "NaN"), ("Infinity", "Infinity")]
for field in ("burst", "rate"):
    cases.append((f"{field} missing", doc(**{field: None})))
    for label, text in BAD_NUMBERS:
        cases.append((f"{field} {label}", doc(**{field: text})))

# requests: missing or not a list.
cases.append(("requests missing", doc(requests=None)))
for label, text in (("null", "null"), ("an object", ENTRY), ("an empty object", "{}"), ("a string", '"[]"'),
                    ("a number", "3"), ("true", "true")):
    cases.append((f"requests {label}", doc(requests=text)))

# An entry in requests that isn't an object, anywhere in the list.
for label, text in (("a number", "5"), ("a string", '"kiosk"'), ("null", "null"), ("a pair in a list", '["kiosk", 5]'),
                    ("true", "true")):
    cases.append((f"an entry that is {label}", doc(requests=f"[{ENTRY}, {text}]")))

# client: missing, not a string, or empty.
cases.append(("client missing", doc(requests=f"[{entry(client=None)}]")))
for label, text in (("null", "null"), ("empty", '""'), ("a number", "5"), ("zero", "0"), ("true", "true"),
                    ("a list", '["kiosk"]'), ("an object", '{"name": "kiosk"}')):
    cases.append((f"client {label}", doc(requests=f"[{entry(client=text)}]")))

# at: missing, not an integer, or negative.
cases.append(("at missing", doc(requests=f"[{entry(at=None)}]")))
for label, text in (("null", "null"), ("a string", '"5"'), ("5.0", "5.0"), ("0.0", "0.0"), ("5.5", "5.5"),
                    ("5e0", "5e0"), ("1e3", "1e3"), ("-1", "-1"), ("-1000", "-1000"), ("-0.5", "-0.5"),
                    ("true", "true"), ("false", "false"), ("a list", "[5]"), ("an object", '{"ms": 5}'),
                    ("NaN", "NaN")):
    cases.append((f"at {label}", doc(requests=f"[{entry(at=text)}]")))

# One bad entry late in an otherwise valid, time-ordered log refuses the whole log. The bad
# entry keeps the log in time order (entry #349 is at 1047 ms, #350 at 1050 ms), so only C4
# can be the reason for refusing it.
good = [{"client": f"svc{i % 7}", "at": i * 3} for i in range(400)]
for label, bad in (("at 1050.0", '{"client": "svc1", "at": 1050.0}'), ("at 1.05e3", '{"client": "svc1", "at": 1.05e3}'),
                   ("at \"1050\"", '{"client": "svc1", "at": "1050"}'), ("client false", '{"client": false, "at": 1050}'),
                   ("an empty client", '{"client": "", "at": 1050}'), ("an entry that is a list", '["svc1", 1050]')):
    body = ", ".join(json.dumps(e) for e in good[:350]) + ", " + bad + ", " + ", ".join(json.dumps(e) for e in good[350:])
    cases.append((f"entry #350 of 401 with {label}", doc(requests="[" + body + "]")))
# The same log without the bad entry is valid (a control for the cases just above).
controls_log = doc(requests="[" + ", ".join(json.dumps(e) for e in good) + "]")

for label, raw in cases:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: must be refused with status 2 and no output, got status {status} and {short(body, 50)}")

# The valid side of each boundary is not refused.
controls = [("burst 1 and rate 1 with no requests", doc(burst="1", rate="1", requests="[]")),
            ("at 0", doc(requests=f"[{entry(at='0')}]")),
            ("a client that is a single space", doc(requests=f"[{entry(client=chr(34) + ' ' + chr(34))}]")),
            ("very large integers", doc(burst=str(10**12), rate=str(10**9), requests=f"[{entry(at=str(10**15))}]")),
            ("the base request used above", doc()),
            ("the 400-entry log without its bad entry", controls_log)]
for label, raw in controls:
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{label}: is valid and must be answered with status 0 and an object, got status {status} and {short(body, 50)}")

finish(problems, f"invalid ok: {len(cases)} invalid requests refused, {len(controls)} valid boundaries answered")
