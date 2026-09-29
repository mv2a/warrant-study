"""X11 (C4): invalid requests are refused with status 2: text that is not JSON, JSON that
is not an object, a missing branch, year or previous (a missing previous is not null), a
branch that is not exactly lisbon, porto, faro or braga, a year that is not a JSON whole
number from 2000 to 9999, and a previous that is neither text nor null. Every other field
of each request is valid, so the one invalid part is the only reason to refuse."""

import json

from _x import encode, expect_refusals, finish

NOT_JSON = [
    "", " ", "\n\n", "faro", "{", "}", "{}}", "[", "{branch: faro, year: 2075, previous: null}",
    "{'branch': 'faro', 'year': 2075, 'previous': None}",
    '{"branch": "faro", "year": 2075, "previous": None}',
    '{"branch": "faro", "year": 2075, "previous": undefined}',
    '{"branch": "faro", "year": 2075, "previous": null,}',
    '{"branch": "faro", "year": 2075, "previous": null',
    '{"branch": "faro" "year": 2075 "previous": null}',
    '{"branch": "faro", "year": 2075, "previous": null}}',
    '{"branch": "faro", "year": 2075, "previous": null} {"branch": "porto"}',
    '{"branch": "faro", "year": 2075, "previous": nul}',
    '{"branch": \'faro\', "year": 2075, "previous": null}',
    '{"branch": "faro", "year": 0x81B, "previous": null}',
    '{"branch": "faro", "year": 02075, "previous": null}',
    '{"branch": "faro", "year": +2075, "previous": null}',
    "branch=faro&year=2075&previous=",
]

NOT_OBJECT = [
    "null", "true", "false", "2075", '"faro"', "[]", '["faro", 2075, null]',
    '[{"branch": "faro", "year": 2075, "previous": null}]',
    '"{\\"branch\\": \\"faro\\", \\"year\\": 2075, \\"previous\\": null}"',
]

VALID = [
    {"branch": "porto", "year": 2075, "previous": "OPO-2075-00150"},
    {"branch": "faro", "year": 2076, "previous": None},
    {"branch": "braga", "year": 2077, "previous": "BRG-2070-00003"},
    {"branch": "lisbon", "year": 2078, "previous": "LIS-2078-00999"},
]

BAD_BRANCHES = [
    "Lisbon", "LIS", "coimbra", "LISBON", "Porto", "PORTO", "FARO", "Faro", "brAga", "Braga",
    "OPO", "FAO", "BRG", "lis", "opo", "lisboa", "oporto", "faro ", " faro", "porto\n", "\tbraga",
    "lis bon", "lisbon.", "lisbonn", "", "coimbra", "setubal", "evora", "lisbon,porto", "porto\u0000",
    "ｌｉｓｂｏｎ", "fаro", "bragа", "lisbón", "porto​",
    None, 1, 0, True, False, 2.5, [], ["porto"], {}, {"name": "porto"},
]

BAD_YEARS = [
    "2026", 2026.0, True, "2076", 2076.0, 2076.5, False, None, 1999, 10000, 0, -2076, 1, 99999,
    -1, 20760, 1000, 10 ** 30, -(10 ** 30), [2076], {"year": 2076}, "", "MMLXXVI", "2076 ",
    1999.9999, 9999.5, 1e4,
]
RAW_BAD_YEARS = ["2076.00", "2.076e3", "2076e0", "2076E0", "20760e-1", "NaN", "Infinity", "-Infinity", "-0", "1999", "10000"]

BAD_PREVIOUS = [41, 0, 1, 150, -1, True, False, 150.0, 2.5, [], ["OPO-2075-00150"], {}, {"number": "OPO-2075-00150"}]

cases = []
for text in NOT_JSON:
    cases.append((f"not JSON: {text!r}", text.encode("utf-8")))
for text in NOT_OBJECT:
    cases.append((f"JSON that is not an object: {text!r}", text.encode("utf-8")))
for request in VALID:
    for field in ("branch", "year", "previous"):
        missing = {k: v for k, v in request.items() if k != field}
        cases.append((f"missing {field}: {json.dumps(missing)}", encode(missing)))
    for only in ("branch", "year", "previous"):
        cases.append((f"only {only}", encode({only: request[only]})))
cases.append(("empty object", b"{}"))
cases.append(("missing previous, other fields present", encode({"branch": "faro", "year": 2076, "prev": None})))
for i, branch in enumerate(BAD_BRANCHES):
    base = VALID[i % len(VALID)]
    cases.append((f"branch {branch!r}", encode({**base, "branch": branch})))
    cases.append((f"branch {branch!r} with previous null", encode({"branch": branch, "year": 2079, "previous": None})))
for i, year in enumerate(BAD_YEARS):
    cases.append((f"year {year!r}", encode({"branch": "porto", "year": year, "previous": None})))
    cases.append((f"year {year!r} with a previous", encode({"branch": "lisbon", "year": year, "previous": "LIS-2076-00012"})))
for text in RAW_BAD_YEARS:
    cases.append((f"year written {text}", f'{{"branch": "braga", "year": {text}, "previous": null}}'.encode()))
for previous in BAD_PREVIOUS:
    for request in VALID[:2]:
        cases.append((f"previous {previous!r} for {request['branch']}", encode({**request, "previous": previous})))

problems = []
n = expect_refusals(problems, cases, "invalid request")
finish(problems, f"requests ok: {n} invalid requests refused")
