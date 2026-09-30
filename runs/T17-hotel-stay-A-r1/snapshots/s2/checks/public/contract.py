"""P1: the stay command's interface."""

from _cmd import call, finish

FIELDS = {"room_cents", "discount_cents", "tax_cents", "total_cents"}
problems = []

status, body = call({"check_in": "tue", "nights": 4, "rate_cents": 9900})
if status != 0:
    problems.append(f"a valid request should exit 0, got status {status}")
if not isinstance(body, dict):
    problems.append(f"a valid request should print one JSON object, got {body!r}")
elif set(body) != FIELDS:
    problems.append(f"the response should have exactly the fields {sorted(FIELDS)}, got {sorted(body)}")
elif not all(type(body[field]) is int for field in FIELDS):
    problems.append(f"every amount should be a whole number of cents, got {body!r}")

for label, request, raw in [
    ("0 nights", {"check_in": "tue", "nights": 0, "rate_cents": 9900}, None),
    ("text that is not JSON", None, "two nights please"),
]:
    status, body = call(request, raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: should be refused with status 2 and nothing on standard output, got status {status} and {body!r}")

finish(problems, "contract ok")
