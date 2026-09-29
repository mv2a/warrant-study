"""X7 (C2): violations lists each broken rule once, only the six codes, sorted; ok iff empty.

Hand-written requests that break several rules at once are compared in full. Generated
requests are judged on the form of the answer only (known codes, no code twice, ascending
order, ok exactly when the list is empty), so that a wrong rule is charged to its own goal.
"""

import random

from _audit import CODES, answer, call_all, finish, random_request, shape_problem, short

# Every rule here is broken (or kept) by a wide margin: lengths far from 12 and 64, runs
# of five or more, username windows and banned entries in the same case as the password,
# so only the form and completeness of the list decide the outcome.
HAND = [
    ("five rules at once, too_short",
     {"password": "aaaaaaaa", "username": "aaaaaa", "banned": ["aaaa", "aa", "a"]},
     ["banned", "classes", "repeat", "too_short", "username"]),
    ("five rules at once, too_long",
     {"password": "z" * 80, "username": "zzzzzz", "banned": ["zzzz", "zz"]},
     ["banned", "classes", "repeat", "too_long", "username"]),
    ("nothing broken", {"password": "Mq3!vB8-yW2=pT", "username": "odile", "banned": ["grape"]}, []),
    ("only banned", {"password": "Mq3!vB8-yW2=pT", "username": "odile", "banned": ["B8-y"]}, ["banned"]),
    ("only classes", {"password": "mq3vb8yw2rt5hk", "username": "odile", "banned": []}, ["classes"]),
    ("only repeat", {"password": "Mq3!vB8-yW22222pT", "username": "odile", "banned": []}, ["repeat"]),
    ("only too_long", {"password": "Mq3!vB8-yW2=pT" * 6, "username": "odile", "banned": []}, ["too_long"]),
    ("only too_short", {"password": "Mq3!vB8", "username": "odile", "banned": []}, ["too_short"]),
    ("only username", {"password": "Mq3!odile-yW2=pT", "username": "odile", "banned": []}, ["username"]),
    ("banned and username by the same text",
     {"password": "Mq3!odile-W2=pT", "username": "odile", "banned": ["odile"]}, ["banned", "username"]),
    ("many banned entries match, many username windows, long runs",
     {"password": "Rt5!kkkkkkk-harriet-harriet-Qm1", "username": "harriet",
      "banned": ["kk", "kkk", "harr", "riet", "t-h"]},
     ["banned", "repeat", "username"]),
    ("too_short and classes only", {"password": "q", "username": "a", "banned": []},
     ["classes", "too_short"]),
    ("empty password", {"password": "", "username": "odile", "banned": []}, ["classes", "too_short"]),
    ("repeat and too_short",
     {"password": "Ab1!!!!!", "username": "odile", "banned": []}, ["repeat", "too_short"]),
    ("classes and too_long",
     {"password": "mq3vb8yw2rt5hk" * 6, "username": "odile", "banned": []}, ["classes", "too_long"]),
    ("banned, classes, username",
     {"password": "odilebrightmoor", "username": "odile", "banned": ["moor"]}, ["banned", "classes", "username"]),
]

rng = random.Random(3360721)
GENERATED = [(f"generated #{i}", random_request(rng), None) for i in range(260)]
CASES = HAND + GENERATED

assert all(exp == answer(r)["violations"] for _, r, exp in HAND), "audit harness bug: expectation vs model"

problems = []
seen_codes = set()
multi = 0
for (label, request, expected), (status, body) in zip(CASES, call_all([r for _, r, _ in CASES])):
    want = answer(request) if expected is None else {"ok": not expected, "violations": expected}
    seen_codes.update(want["violations"])
    multi += len(want["violations"]) >= 2
    reason = shape_problem(status, body)
    if reason:
        problems.append(f"{label} {short(request)}: {reason}")
        continue
    got = body["violations"]
    unknown = sorted(set(got) - set(CODES))
    if unknown:
        problems.append(f"{label} {short(request)}: unknown codes {unknown} in {got}")
    elif len(set(got)) != len(got):
        problems.append(f"{label} {short(request)}: a code is listed twice in {got}")
    elif got != sorted(got):
        problems.append(f"{label} {short(request)}: codes not in ascending order: {got}")
    elif body["ok"] != (got == []):
        problems.append(f"{label} {short(request)}: ok is {body['ok']} but violations is {got}")
    elif expected is not None and body != want:
        problems.append(f"{label} {short(request)}: expected {want}, got {body}")

assert seen_codes == set(CODES), "audit harness bug: not every code is exercised"
finish(problems, f"violations ok: {len(HAND)} answers compared in full, {len(GENERATED)} checked for form"
                 f" ({multi} expected to break two or more rules)")
