"""The invalid requests of the audit, as raw standard-input texts. C3 says each of them must be
refused (X9 checks that); C4 says a refused request writes nothing on standard output (X1
checks that). Kept in one place so both checks send exactly the same requests."""

import json

INCOME, DEPS = 4_750_000, 3
TEXTS = [
    # not a JSON object
    "", "\n", "   \t ", "[]", "[4750000, 3]", '[{"income_cents": 4750000, "dependents": 3}]',
    '"income_cents"', "4750000", "null", "true", "false", "0",
    "{", '{"income_cents": 4750000, "dependents": 3', "{income_cents: 4750000, dependents: 3}",
    "{'income_cents': 4750000, 'dependents': 3}", '{"income_cents": 4750000, "dependents": 3,}',
    '{"income_cents": 4750000 "dependents": 3}', "income_cents=4750000&dependents=3",
    # one object followed by more than whitespace (C3: nothing but whitespace after it)
    '{"income_cents": 4750000, "dependents": 3} {"income_cents": 1, "dependents": 0}',
    '{"income_cents": 4750000, "dependents": 3} x',
    # non-finite numbers (not JSON, and not integers either)
    '{"income_cents": NaN, "dependents": 3}', '{"income_cents": Infinity, "dependents": 3}',
    '{"income_cents": 4750000, "dependents": -Infinity}',
]
_requests = [
    # missing fields
    {}, {"income_cents": INCOME}, {"dependents": DEPS}, {"income": INCOME, "dependents": DEPS},
    {"income_cents": INCOME, "dependent": DEPS}, {"Income_cents": INCOME, "dependents": DEPS},
    {"income_cents": INCOME, "Dependents": DEPS}, {"income_cents ": INCOME, "dependents": DEPS},
]
for bad in (4_750_000.5, 4_750_000.0, 0.0, 1200.5, 1200.0, "4750000", "1200", "", True, False, None,
            [INCOME], {"cents": INCOME}):
    _requests.append({"income_cents": bad, "dependents": DEPS})
for bad in (3.0, 0.0, 2.5, "3", "0", "", True, False, None, [DEPS], {"n": DEPS}):
    _requests.append({"income_cents": INCOME, "dependents": bad})
for income, deps in ((-1, DEPS), (-INCOME, DEPS), (-10 ** 15, 0), (INCOME, -1), (INCOME, -20),
                     (INCOME, 21), (INCOME, 22), (INCOME, 100), (0, 10 ** 9), (-5, -5), (10 ** 20, 21)):
    _requests.append({"income_cents": income, "dependents": deps})
# invalid fields are not rescued by valid-looking extra fields
_requests.append({"income_cents": INCOME, "dependents": 21, "dependents_override": 2})
_requests.append({"income_cents": "4750000", "income": INCOME, "dependents": DEPS})
TEXTS += [json.dumps(r) for r in _requests]
