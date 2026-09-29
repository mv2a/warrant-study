"""X-C3: invalid requests are refused (status 2, nothing on standard output), never charged.

Covers input that is not one JSON object (empty, blank, plain text, JavaScript or Python
style objects, arrays, strings, numbers, null, truncated text, trailing text or a second
object after the first); a missing entry, exit or lost_ticket (including misspelled or
differently cased keys); an entry or exit that is not a JSON integer (booleans, null,
decimals such as 3725.0, exponents such as 4e3, strings, arrays, objects, NaN, Infinity)
or lies outside 0 to 10079; and a lost_ticket that is not true or false. A refusal is
status 2 with nothing on standard output; if the command refuses a request with no
lost_ticket with some other non-zero status, that status is accepted here too, because
the exact status and the message on standard error are C1's contract, checked by C1.
It also covers what C3 does not refuse: an entry or exit written -0 is the integer 0, and
fields other than entry, exit and lost_ticket are ignored, so such a request gets exactly
the same answer as the plain request with 0 or without the extra fields.
"""

import json

from _audit import run_many_raw
from _cmd import finish

GOOD = {"entry": "3725", "exit": "3990", "lost_ticket": "false"}


def body(**changes):
    values = {**GOOD, **changes}
    return "{" + ", ".join(f'"{k}": {v}' for k, v in values.items() if v is not None) + "}"


def without(name):
    return body(**{name: None})


cases = [
    ("empty input", ""),
    ("blank input", " \n\t \n"),
    ("plain text", "entry 3725 exit 3990"),
    ("unquoted keys", "{entry: 3725, exit: 3990, lost_ticket: false}"),
    ("Python-style object", "{'entry': 3725, 'exit': 3990, 'lost_ticket': False}"),
    ("an empty array", "[]"),
    ("an array of values", "[3725, 3990, false]"),
    ("an array holding the object", "[" + body() + "]"),
    ("a JSON string", '"' + body().replace('"', '\\"') + '"'),
    ("a number", "3725"),
    ("null", "null"),
    ("true", "true"),
    ("an opening brace", "{"),
    ("a truncated object", body()[:-1]),
    ("an extra closing brace", body() + "}"),
    ("text after the object", body() + " thanks"),
    ("two objects", body() + "\n" + body(entry="10", exit="20")),
    ("missing commas", '{"entry": 3725 "exit": 3990 "lost_ticket": false}'),
    ("a trailing comma", '{"entry": 3725, "exit": 3990, "lost_ticket": false,}'),
    ("an entry with a leading zero", body(entry="03725")),
    ("an entry with a plus sign", body(entry="+3725")),
    ("a hexadecimal entry", body(entry="0xE8D")),
    ("an empty object", "{}"),
    ("no entry", without("entry")),
    ("no exit", without("exit")),
    ("no lost_ticket", without("lost_ticket")),
    ("only lost_ticket", '{"lost_ticket": true}'),
    ("Entry instead of entry", '{"Entry": 3725, "exit": 3990, "lost_ticket": false}'),
    ("EXIT instead of exit", '{"entry": 3725, "EXIT": 3990, "lost_ticket": false}'),
    ("lostTicket instead of lost_ticket", '{"entry": 3725, "exit": 3990, "lostTicket": false}'),
    ("a key with a trailing space", '{"entry ": 3725, "exit": 3990, "lost_ticket": false}'),
    ("fields nested one level down", '{"stay": ' + body() + "}"),
]

NOT_INTEGER = ["true", "false", "null", "3725.0", "3725.5", "0.0", "-0.0", "10079.0", "37.25e2", "3.725E3",
               "4e3", "4E+3", "1e2", "2e-1", '"3725"', '""', '"0"', "[3725]", "[]", '{"minutes": 3725}',
               "NaN", "Infinity", "-Infinity", "1e400"]
OUT_OF_RANGE = ["-1", "-1440", "10080", "10081", "20159", "99999999999999999999", "-99999999999999999999"]
for name in ("entry", "exit"):
    for value in NOT_INTEGER:
        cases.append((f"{name} {value}", body(**{name: value})))
    for value in OUT_OF_RANGE:
        cases.append((f"{name} {value}", body(**{name: value})))

for value in ["0", "1", "null", '"no"', '"yes"', '"true"', '"false"', '""', "0.0", "1.0", "-1", "2",
              "[]", "{}", "[false]", '"False"', '"TRUE"']:
    cases.append((f"lost_ticket {value}", body(lost_ticket=value)))

cases += [
    ("every field invalid", '{"entry": -1, "exit": 10080, "lost_ticket": "no"}'),
    ("a valid entry but an exit of true", body(exit="true")),
    ("both times as strings", body(entry='"3725"', exit='"3990"')),
]

# Not refused: -0 is the integer 0, and fields other than entry, exit and lost_ticket are
# ignored. Each request must get exactly the answer (status and output) of its plain form.
# Comparing the command with itself keeps this part free of the money rules.
same = [
    ("an entry of -0", body(entry="-0"), body(entry="0")),
    ("an exit of -0", body(exit="-0"), body(exit="0")),
    ("entry and exit of -0", body(entry="-0", exit="-0"), body(entry="0", exit="0")),
    ("an extra text field", body(note='"back row"'), body()),
    ("extra fields of every JSON type, first and in between",
     '{"zone": "B2", "entry": 3725, "vip": true, "exit": 3990, "rate": 2.5, "lost_ticket": false, '
     '"tags": [1, "a"], "stay": {"exit": 1}, "memo": null}', body()),
    ("extra fields named like the output fields",
     body(total_cents="0", minutes="5", time_cents='"free"'), body()),
    ("differently cased and spelled copies of the fields with invalid values",
     body(Entry="99999", EXIT="-1", lostTicket='"no"'), body()),
    ("an extra field with a lost ticket", body(lost_ticket="true", receipt="false"), body(lost_ticket="true")),
]

texts = [without("lost_ticket")] + [text for _, text in cases]
for _, text, plain in same:
    texts += [text, plain]
answers = run_many_raw(texts)
refused = {2}
if answers[0][0] != 0 and not answers[0][1].strip():
    refused.add(answers[0][0])

problems = []
for (name, text), (status, out, _) in zip(cases, answers[1:]):
    if status not in refused or out.strip():
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {out.strip()[:80]!r}")


def answer(status, out):
    try:
        return status, json.loads(out)
    except ValueError:
        return status, out.strip()


at = 1 + len(cases)
for name, text, plain in same:
    got_it, want = answer(*answers[at][:2]), answer(*answers[at + 1][:2])
    at += 2
    if got_it != want:
        problems.append(f"{name}: expected the same answer as {plain} ({want[1]!r}, status {want[0]}), "
                        f"got status {got_it[0]} and {got_it[1]!r}"[:240])

finish(problems, f"C3 ok: {len(cases)} invalid requests refused and {len(same)} requests with -0 or extra "
                 f"fields answered like their plain form")
