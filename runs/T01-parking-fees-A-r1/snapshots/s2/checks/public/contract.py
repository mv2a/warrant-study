"""P1: the fee command follows the interface in C1."""

from _cmd import call, finish

FIELDS = ("minutes", "time_cents", "overnight_cents", "lost_ticket_cents", "total_cents")
VALID = [
    ({"entry": 600, "exit": 700, "lost_ticket": False}, 100),
    ({"entry": 4000, "exit": 4400, "lost_ticket": True}, 400),
    ({"entry": 7300, "exit": 7310, "lost_ticket": False}, 10),
]
problems = []
for request, minutes in VALID:
    status, body = call(request)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{request}: expected status 0 and a JSON object, got status {status} and {body!r}")
        continue
    bad = [f for f in FIELDS if type(body.get(f)) is not int]
    if bad:
        problems.append(f"{request}: missing or non-integer field(s) {', '.join(bad)} in {body}")
        continue
    if body["minutes"] != minutes:
        problems.append(f"{request}: expected minutes {minutes}, got {body['minutes']}")
    parts = body["time_cents"] + body["overnight_cents"] + body["lost_ticket_cents"]
    if body["total_cents"] != parts:
        problems.append(f"{request}: total_cents {body['total_cents']} is not the sum of the charges ({parts})")

status, body = call({"entry": 600, "lost_ticket": False})
if status != 2 or body is not None:
    problems.append(f"a request with no exit: expected a refusal (status 2, no output), got status {status} and {body!r}")

finish(problems, f"contract ok: {len(VALID)} valid requests and one refusal")
