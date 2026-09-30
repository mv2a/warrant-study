"""P1: `fine` follows the interface in C1."""

from _cmd import call, finish

TOP = {"items", "total_cents"}
LINE = {"id", "days_late", "fine_cents"}
problems = []

requests = [
    {"items": [
        {"id": "b9", "type": "book", "due_day": 3, "returned_day": 12},
        {"id": "d2", "type": "dvd", "due_day": 3, "returned_day": 9},
    ]},
    {"items": []},
]
for request in requests:
    status, body = call(request)
    ids = [item["id"] for item in request["items"]]
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != TOP:
        problems.append(f"{request}: expected an object with exactly {sorted(TOP)}, got {body!r}")
    elif type(body["total_cents"]) is not int:
        problems.append(f"{request}: total_cents must be an integer, got {body['total_cents']!r}")
    elif not isinstance(body["items"], list) or len(body["items"]) != len(ids):
        problems.append(f"{request}: expected {len(ids)} entries in items, got {body['items']!r}")
    else:
        for line in body["items"]:
            if not isinstance(line, dict) or set(line) != LINE:
                problems.append(f"{request}: each entry needs exactly {sorted(LINE)}, got {line!r}")
            elif type(line["days_late"]) is not int or type(line["fine_cents"]) is not int:
                problems.append(f"{request}: days_late and fine_cents must be integers, got {line!r}")
        if not problems and [line["id"] for line in body["items"]] != ids:
            problems.append(f"{request}: entries must repeat the request's ids in order, got {body['items']!r}")
        if not ids and body["total_cents"] != 0:
            problems.append(f"an empty item list must owe 0, got {body['total_cents']!r}")

status, body = call({"items": [{"id": "c1", "type": "cd", "due_day": 1, "returned_day": 8}]})
if status != 2 or body is not None:
    problems.append(f"an item of type \"cd\" must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "contract ok: 3 requests")
