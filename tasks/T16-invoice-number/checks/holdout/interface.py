"""H8: the command follows the interface in C5."""

from _cmd import call, finish

VALID = [
    {"branch": "lisbon", "year": 2026, "previous": None},
    {"branch": "porto", "year": 2030, "previous": "OPO-2030-00099"},
    {"branch": "faro", "year": 2031, "previous": "FAO-2030-00500"},
    {"branch": "braga", "year": 9999, "previous": "BRG-9999-54321"},
]
EXTRA = {"note": "urgent", "currency": "EUR", "branch_name": "Porto", "previous_number": "XYZ", "sequence": 7, "number": "OPO-2030-00005", "year_end": True}
REFUSED = [
    ("an unknown branch", {"branch": "coimbra", "year": 2026, "previous": None}),
    ("another branch's number", {"branch": "lisbon", "year": 2026, "previous": "OPO-2026-00003"}),
    ("a missing previous field", {"branch": "lisbon", "year": 2026}),
    ("text that isn't JSON", "not json"),
]
problems = []
for request in VALID:
    answers = []
    for sent in (request, {**EXTRA, **request}):
        status, body = call(sent)
        answers.append(body)
        if status != 0:
            problems.append(f"{sent}: exited with status {status}, expected 0")
        elif not isinstance(body, dict) or set(body) != {"number", "sequence"}:
            problems.append(f"{sent}: expected one object with exactly number and sequence, got {body!r}")
        elif type(body["number"]) is not str or type(body["sequence"]) is not int:
            problems.append(f"{sent}: number must be text and sequence a whole number, got {body!r}")
    if answers[0] != answers[1]:
        problems.append(f"{request}: extra fields changed the answer from {answers[0]!r} to {answers[1]!r}")
for name, request in REFUSED:
    status, body = call(raw=request) if isinstance(request, str) else call(request)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected status 2 and nothing on standard output, got status {status} and {body!r}")

finish(problems, f"interface ok: {2 * len(VALID)} answered, {len(REFUSED)} refused")
