"""P1: the command's interface, with one accepted and two refused requests."""

from _cmd import call, finish

problems = []

status, body = call({"name": "anna weber"})
if status != 0:
    problems.append(f"a plain name: expected exit status 0, got {status}")
elif not isinstance(body, dict) or set(body) != {"display", "key"}:
    problems.append(f"a plain name: expected an object with exactly display and key, got {body!r}")
elif not all(isinstance(body[field], str) for field in ("display", "key")):
    problems.append(f"a plain name: display and key must both be strings, got {body!r}")
elif body != {"display": "Anna Weber", "key": "annaweber"}:
    problems.append(f"a plain name: expected Anna Weber / annaweber, got {body!r}")

for label, raw in [("an empty name", '{"name": ""}'), ("text that is not JSON", "anna weber")]:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected a refusal (status 2, no output), got status {status} and {body!r}")

finish(problems, "interface ok: 1 accepted, 2 refused")
