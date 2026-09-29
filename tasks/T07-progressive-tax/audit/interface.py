"""X1 (C4): the interface. Several spellings of the same valid request give exit status 0
and exactly one JSON object with the six integer fields, the same object each time: key
order, whitespace and extra fields make no difference. A refused request exits with
status 2 and writes nothing at all on standard output: two refusals are checked for both,
and every invalid request of X9 that the command does not tax is checked for silence
(whether it is refused at all is C3's business, checked by X9)."""

import json

from _cmd import finish
from _invalid import TEXTS as INVALID
from _model import FIELDS, run_raw, short

problems = []


def strict(text, label):
    status, out = run_raw(text)
    if status != 0:
        problems.append(f"{label}: exit status {status}, expected 0")
        return None
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        problems.append(f"{label}: standard output is not one JSON object: {short(repr(out), 80)}")
        return None
    if not isinstance(body, dict) or set(body) != set(FIELDS):
        problems.append(f"{label}: expected exactly the fields {list(FIELDS)}, got {short(repr(body), 100)}")
        return None
    wrong = [f for f in FIELDS if type(body[f]) is not int]
    if wrong:
        problems.append(f"{label}: {wrong} are not JSON integers: {short(repr(body), 100)}")
        return None
    return body


FILERS = [(5_555_500, 4), (23_456_789, 7), (987_654, 2), (0, 0), (160_000_000, 20)]
count = 0
for income, deps in FILERS:
    request = {"income_cents": income, "dependents": deps}
    plain = strict(json.dumps(request), f"{request}")
    count += 1
    variants = {
        "keys in the other order": json.dumps({"dependents": deps, "income_cents": income}),
        "pretty-printed on several lines": "\n" + json.dumps(request, indent=4) + "\n\n",
        "compact, no spaces": json.dumps(request, separators=(",", ":")),
        "with extra fields": json.dumps({"filer": "N-0042", "income_cents": income, "year": 2025,
                                         "dependents": deps, "tax_cents": -1, "allowance_cents": "none",
                                         "spouse": None, "notes": {"list": [1, 2.5, None, True]}}),
    }
    for name, text in variants.items():
        body = strict(text, f"{request} ({name})")
        count += 1
        if plain is not None and body is not None and body != plain:
            problems.append(f"{request} ({name}): response {body} differs from the plain request's {plain}")

for text in ('[5555500, 4]', json.dumps({"income_cents": 5_555_500, "dependents": -3})):
    status, out = run_raw(text)
    count += 1
    if status != 2 or out != "":
        problems.append(f"refused request {text}: expected exit status 2 and no output, "
                        f"got status {status} and output {short(repr(out), 60)}")

silent = 0
for text in INVALID:
    status, out = run_raw(text)
    if status == 0:
        continue  # taxed although invalid: a C3 failure, reported by X9
    silent += 1
    if out != "":
        problems.append(f"refused request {short(repr(text), 60)}: exit status {status} but standard "
                        f"output is not empty: {short(repr(out), 60)}")

finish(problems, f"interface ok: {count} requests, {silent} refusals silent")
