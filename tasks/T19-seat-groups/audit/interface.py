"""C1: the interface. For hand-written and generated requests (seed 43019): exit status 0;
exactly seated, refused and free; seated entries hold exactly id and seats, refused entries
exactly id and reason; every group is answered once, in booking order within each list;
seat names are written like B7 and listed in seating order; free is a whole number.
Also: fields not named in the intent are ignored, a missing may_split means false, ids
come back exactly as sent, and a refused request gets exit status 2 with nothing at all
on standard output."""

import json

from _audit import brief, call_all, generated, parse, raw_all
from _cmd import finish

REASONS = {"not_enough_seats", "not_together"}

HAND = [
    {"rows": [3, 5], "groups": [{"id": "Kato", "size": 4}, {"id": "Lee", "size": 3}]},
    {"rows": [4], "groups": [{"id": "Ma", "size": 2}, {"id": "Nu", "size": 5}, {"id": "Ox", "size": 1},
                             {"id": "Py", "size": 3, "may_split": True}, {"id": "Qi", "size": 1}]},
    {"rows": [12, 3], "blocked": [f"A{n}" for n in range(1, 9)] + ["A11"], "groups": [{"id": "Rho", "size": 4, "may_split": True}]},
    {"rows": [14], "blocked": [f"A{n}" for n in range(7, 0, -1)], "groups": [{"id": "Sig", "size": 5}]},
    {"rows": [2], "groups": [{"id": "Tau", "size": 3}, {"id": "Ups", "size": 4, "may_split": True}]},
    {"rows": [1] * 26, "groups": [{"id": "Phi", "size": 26, "may_split": True}]},
    {"rows": [9, 9, 9], "blocked": ["A5", "B5", "C5"], "groups": [
        {"id": "Chi", "size": 5, "may_split": True}, {"id": "Psi", "size": 4}, {"id": "Omega", "size": 9},
        {"id": "Alpha", "size": 6, "may_split": True}, {"id": "Beta", "size": 2, "may_split": False}]},
]
REQUESTS = HAND + generated(43019, 50)
problems = []


def structure(request, status, body):
    if status != 0:
        return [f"exit status {status}, expected 0"]
    if not isinstance(body, dict):
        return [f"standard output is not one JSON object: {str(body)[:80]!r}"]
    if set(body) != {"seated", "refused", "free"}:
        return [f"response fields are {sorted(body)}, expected exactly free, refused, seated"]
    bad = []
    if type(body["free"]) is not int:
        bad.append(f"free is {body['free']!r}, not a whole number")
    if not isinstance(body["seated"], list) or not isinstance(body["refused"], list):
        return bad + ["seated and refused must be lists"]
    order = [g["id"] for g in request["groups"]]
    for entry in body["seated"]:
        if not isinstance(entry, dict) or set(entry) != {"id", "seats"}:
            bad.append(f"seated entry {str(entry)[:60]} must hold exactly id and seats")
        elif not isinstance(entry["seats"], list) or not all(isinstance(s, str) for s in entry["seats"]):
            bad.append(f"seats of {entry['id']!r} must be a list of seat names")
        else:
            parsed = [parse(s) for s in entry["seats"]]
            if None in parsed:
                bad.append(f"{entry['id']!r} has seat names not written like B7: {entry['seats']}")
            elif any(b <= a for a, b in zip(parsed, parsed[1:])):
                bad.append(f"seats of {entry['id']!r} are not in seating order: {entry['seats']}")
    for entry in body["refused"]:
        if not isinstance(entry, dict) or set(entry) != {"id", "reason"}:
            bad.append(f"refused entry {str(entry)[:60]} must hold exactly id and reason")
        elif entry["reason"] not in REASONS:
            bad.append(f"reason {entry['reason']!r} is neither not_enough_seats nor not_together")
    if bad:
        return bad
    seated_ids = [e["id"] for e in body["seated"]]
    refused_ids = [e["id"] for e in body["refused"]]
    if not all(isinstance(i, str) for i in seated_ids + refused_ids):
        bad.append(f"ids must be text as sent: seated {seated_ids}, refused {refused_ids}")
    elif sorted(seated_ids + refused_ids) != sorted(order) or len(set(seated_ids + refused_ids)) != len(order):
        bad.append(f"every group must be answered once: seated {seated_ids}, refused {refused_ids}")
    else:
        for which, ids in (("seated", seated_ids), ("refused", refused_ids)):
            if ids != [i for i in order if i in ids]:
                bad.append(f"{which} is not in booking order: {ids}")
    return bad


for request, (status, body) in zip(REQUESTS, call_all(REQUESTS)):
    for message in structure(request, status, body)[:2]:
        problems.append(f"{message} | {brief(request)}")

# An empty booking list is a handled request.
status, body = call_all([{"rows": [3, 3], "groups": []}])[0]
if status != 0 or body != {"seated": [], "refused": [], "free": 6}:
    problems.append(f"no groups: expected status 0 and seated [], refused [], free 6, got {status} and {body!r}")

# Fields the intent does not name are ignored: the answer equals the answer without them.
WITH_EXTRAS = [
    {"rows": [5, 5], "Rows": [1], "free": 99, "seated": "none", "note": None, "show": {"title": "Uncle Vanya", "night": 3},
     "blocked": ["A3"], "groups": [
         {"id": "Wolff", "size": 3, "seats": ["B5", "B4", "B3"], "reason": "vip", "phone": "0000"},
         {"id": "Yager", "size": 3, "may split": True, "Size": 1, "may_Split": True},
         {"id": "Zorin", "size": 2, "may_split": True, "paid": 12.5, "blocked": ["A1"]}]},
    {"rows": [3], "groups": [], "groups_extra": [{"id": "", "size": 0}], "blocked_seats": ["A1", "a1"], "size": -1},
    {"rows": [2, 2], "groups": [{"id": "Arne", "size": 3, "note": {"nested": [1, 2.5, None]}}], "id": 7, "may_split": True},
]


def strip(request):
    out = {k: request[k] for k in ("rows", "groups", "blocked") if k in request}
    out["groups"] = [{k: g[k] for k in ("id", "size", "may_split") if k in g} for g in request["groups"]]
    return out


pairs = [(r, strip(r)) for r in WITH_EXTRAS]
# A missing may_split means false: the answer equals the answer with "may_split": false written out.
for request in HAND + generated(43019, 50)[:20]:
    if any("may_split" not in g for g in request["groups"]):
        explicit = {**request, "groups": [{"may_split": False, **g} for g in request["groups"]]}
        pairs.append((request, explicit))
results = call_all([p for pair in pairs for p in pair])
for i, (a, b) in enumerate(pairs):
    (sa, ba), (sb, bb) = results[2 * i], results[2 * i + 1]
    if sa != 0 or sb != 0 or ba != bb:
        what = "extra fields" if i < len(WITH_EXTRAS) else "a missing may_split"
        problems.append(f"{what} changed the answer: {str(ba)[:90]} vs {str(bb)[:90]} | {brief(a)}")

# Ids come back exactly as sent, whether the input is raw UTF-8 or uses \u escapes.
IDS = ["Łucja", "李", "O'Brien \"Jr\"", "🎭 club", "tab\tid", "Ámbar", "A1"]
unicode_request = {"rows": [10], "groups": [{"id": i, "size": 1} for i in IDS]}
texts = [json.dumps(unicode_request, ensure_ascii=False), json.dumps(unicode_request, ensure_ascii=True)]
for text, (status, body) in zip(texts, call_all(texts)):
    seated = body.get("seated") if isinstance(body, dict) else None
    ids = [e.get("id") if isinstance(e, dict) else e for e in seated] if isinstance(seated, list) else None
    if status != 0 or ids != IDS:
        problems.append(f"ids must come back exactly as sent: got status {status} and ids {ids!r}")

# A refused request: exit status 2 and nothing written to standard output.
REFUSED = [
    "{not json",
    '[{"rows": [4], "groups": []}]',
    '{"rows": [], "groups": []}',
    '{"rows": [4], "groups": [{"id": "Dunn", "size": 2.5}]}',
    '{"rows": [4], "groups": [{"id": "Ames", "size": 1}, {"id": "Ames", "size": 1}]}',
]
for text, (status, out) in zip(REFUSED, raw_all(REFUSED)):
    if status != 2 or out != "":
        problems.append(f"refused request {text!r}: expected status 2 and no output, got {status} and {out[:60]!r}")

finish(problems, f"interface ok: {len(REQUESTS)} requests checked for shape, {len(pairs)} pairs compared")
