"""H8 (C2): invalid requests are refused with status 2 and no output; the length limit is
100 characters counted before tidying; any name with a letter left is accepted."""

from _cmd import call, finish

REFUSED = [
    ("text that is not JSON", "anna weber"),
    ("empty input", ""),
    ("truncated JSON", '{"name": "anna weber"'),
    ("single-quoted pseudo-JSON", "{'name': 'anna weber'}"),
    ("a JSON string", '"anna weber"'),
    ("a JSON list", '["anna weber"]'),
    ("JSON null", "null"),
    ("a JSON number", "42"),
    ("JSON true", "true"),
    ("an empty object", "{}"),
    ("a capitalised field name", '{"Name": "anna weber"}'),
    ("a differently named field", '{"full_name": "anna weber"}'),
    ("a null name", '{"name": null}'),
    ("a numeric name", '{"name": 42}'),
    ("a boolean name", '{"name": true}'),
    ("a list name", '{"name": ["anna", "weber"]}'),
    ("an object name", '{"name": {"first": "anna"}}'),
]
NO_LETTERS = ["", "   ", "\t\n\r", " ", "Dr.", "mr", "Mr. Mrs.", "sir DAME rev.",
              "Mr. 42", "007", "---", "...", "Prof. Dr. -", "Dr. . .", "'", "12 34", "Mx. 3.14"]
TOO_LONG = [
    ("101 letters", "a" * 101),
    ("150 letters", "b" * 150),
    ("a short name padded to 101 characters", "anna" + " " * 97),
    ("101 accented letters", "é" * 101),
    ("a 101-character name of words", ("anna weber " * 10)[:101]),
]
ACCEPTED = [
    ("100 letters", "a" * 100, "A" + "a" * 99),
    ("a short name padded to 100 characters", "anna" + " " * 96, "Anna"),
    ("100 characters of whitespace and name", " " * 50 + "anna weber" + "\t" * 40, "Anna Weber"),
    ("100 accented letters", "é" * 100, "É" + "é" * 99),
    ("a single letter after an honorific", "Mr. a", "A"),
    ("a letter outside a to z after an honorific", "Ms. ø", "Ø"),
    ("a Chinese name after an honorific", "Dr. 李", "李"),
    ("a letter among digits", "Mr. 4b2", "4b2"),
]

problems = []
for label, raw in REFUSED:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for name in NO_LETTERS:
    status, body = call({"name": name})
    if status != 2 or body is not None:
        problems.append(f"no letters in {name!r}: expected a refusal, got status {status} and {body!r}")
for label, name in TOO_LONG:
    status, body = call({"name": name})
    if status != 2 or body is not None:
        problems.append(f"{label} ({len(name)}): expected a refusal, got status {status} and {body!r}")
for label, name, display in ACCEPTED:
    status, body = call({"name": name})
    got = body.get("display") if isinstance(body, dict) else None
    if status != 0 or got != display:
        problems.append(f"{label}: expected display {display!r}, got {got!r} (status {status})")

total = len(REFUSED) + len(NO_LETTERS) + len(TOO_LONG)
finish(problems, f"refusals ok: {total} refused, {len(ACCEPTED)} accepted at the edges")
