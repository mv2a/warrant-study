"""H6: the command's interface (C1): request and response shape, order, ignored fields, refusal format."""

import random
import subprocess

from _cmd import PATH, call, finish
from _model import TYPES

rng = random.Random(1213)
TOP = {"items", "total_cents"}
LINE = {"id", "days_late", "fine_cents"}
problems = []


def shape_problem(body, ids):
    if not isinstance(body, dict) or set(body) != TOP:
        return f"expected an object with exactly {sorted(TOP)}, got {body!r}"
    if type(body["total_cents"]) is not int:
        return f"total_cents must be an integer, got {body['total_cents']!r}"
    if not isinstance(body["items"], list) or len(body["items"]) != len(ids):
        return f"expected {len(ids)} entries in items, got {body['items']!r}"
    for line in body["items"]:
        if not isinstance(line, dict) or set(line) != LINE:
            return f"each entry needs exactly {sorted(LINE)}, got {line!r}"
        if type(line["days_late"]) is not int or type(line["fine_cents"]) is not int:
            return f"days_late and fine_cents must be integers, got {line!r}"
    if [line["id"] for line in body["items"]] != ids:
        return f"entries must repeat the request's ids in the request's order, got {[l['id'] for l in body['items']]!r}"
    return None


# Shape and order, with unusual but valid ids, for several generated requests.
odd_ids = ["0", "with space", "Ünïcode ✓", 'quote"inside', "z", "A", "b-10", "b-2", "x" * 60]
for round_number in range(8):
    ids = rng.sample(odd_ids, rng.randint(3, len(odd_ids))) + [f"r{round_number}-{n}" for n in range(rng.randint(0, 6))]
    rng.shuffle(ids)
    items = [
        {"id": ident, "type": rng.choice(TYPES), "due_day": rng.randint(0, 50), "returned_day": rng.randint(0, 80)}
        for ident in ids
    ]
    status, body = call({"items": items})
    problem = shape_problem(body, ids) if status == 0 else f"exited with status {status}, expected 0"
    if problem:
        problems.append(f"request {round_number}: {problem}")

# Valid edge requests succeed with a response of the documented shape.
EDGE = [
    {"items": []},
    {"items": [{"id": "e1", "type": "book", "due_day": 0, "returned_day": 0}]},
    {"items": [{"id": "e2", "type": "reference", "due_day": 9, "returned_day": 2}]},
    {"items": [{"id": "e3", "type": "dvd", "due_day": 1_000_000_000, "returned_day": 1_000_000_010}]},
]
for request in EDGE:
    status, body = call(request)
    ids = [i["id"] for i in request["items"]]
    problem = shape_problem(body, ids) if status == 0 else f"exited with status {status}, expected 0"
    if problem:
        problems.append(f"{request}: {problem}")
status, body = call({"items": []})
if status != 0 or body != {"items": [], "total_cents": 0}:
    problems.append(f"an empty item list must give {{'items': [], 'total_cents': 0}}, got status {status} and {body!r}")

# Fields other than the documented ones are ignored, at both levels: the answer is the same as without them.
plain = [{"id": "k1", "type": "dvd", "due_day": 3, "returned_day": 12},
         {"id": "k2", "type": "book", "due_day": 3, "returned_day": 30},
         {"id": "k3", "type": "reference", "due_day": 8, "returned_day": 4}]
extra = [{**plain[0], "title": "Night Train", "fine_cents": 1, "days_late": 99},
         {**plain[1], "branch": "north", "rate": 1000},
         {**plain[2], "grace": 30, "cap": 1}]
plain_status, plain_body = call({"items": plain})
status, body = call({"items": extra, "account": "A-17", "total_cents": 5, "note": None})
if plain_status != 0 or status != 0 or body != plain_body:
    problems.append(
        f"extra fields must be ignored: without them got status {plain_status} and {plain_body!r}, "
        f"with them got status {status} and {body!r}"
    )

# A refusal writes nothing on standard output, a short reason on standard error (at most 200
# characters, not a traceback), and exits with status 2, however long the offending value is.
LONG = "z" * 450
REFUSED = [
    "not json at all",
    '{"items": [{"id": "q", "type": "vinyl", "due_day": 1, "returned_day": 9}]}',
    '{"items": [{"id": "q", "type": "book", "due_day": -2, "returned_day": 9}]}',
    '{"items": [{"id": "q", "type": "book", "due_day": 1, "returned_day": 9}, {"id": "q", "type": "dvd", "due_day": 1, "returned_day": 9}]}',
    '{"items": [{"id": "%s", "type": "reference", "due_day": 2, "returned_day": 4}, {"id": "%s", "type": "reference", "due_day": 2, "returned_day": 4}]}' % (LONG, LONG),
    '{"items": [{"id": "q", "type": "%s", "due_day": 1, "returned_day": 9}]}' % LONG,
]
for raw in REFUSED:
    done = subprocess.run([PATH], input=raw, capture_output=True, text=True, timeout=10)
    reason = done.stderr.strip()
    if (done.returncode != 2 or done.stdout.strip() or not reason
            or len(reason) > 200 or "Traceback" in done.stderr):
        problems.append(
            f"{raw[:60]}: a refusal needs status 2, empty standard output and a reason of 1 to 200 characters, "
            f"not a traceback, on standard error; got status {done.returncode}, stdout {done.stdout.strip()[:60]!r}, "
            f"stderr of {len(reason)} characters {reason[:60]!r}"
        )

finish(problems, f"interface ok: 8 generated requests, 4 edge requests, ignored fields, {len(REFUSED)} refusals")
