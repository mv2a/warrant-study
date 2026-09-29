"""X1 (C1): the policy command's interface, checked on the raw bytes of standard output."""

import json

from _audit import finish, run_bytes_all, shape_problem, short

FIELDS = {"ok", "violations"}

VALID = [
    ("a password that keeps every rule", {"password": "Wd5#orchard-Pk", "username": "ingrid", "banned": ["apple"]}),
    ("a password that breaks one rule", {"password": "Wd5#orchard", "username": "ingrid", "banned": []}),
    ("a password that breaks several rules", {"password": "ingridddd", "username": "INGRID", "banned": ["rid"]}),
    ("an empty password", {"password": "", "username": "ingrid", "banned": []}),
    ("a very long password", {"password": "Wd5#orchard-Pk" * 40, "username": "ingrid", "banned": []}),
    ("a password with non-ASCII characters",
     {"password": "Wd5#\u00f6rch\u00e4rd-\U0001F600", "username": "ingrid", "banned": ["\u00e4"]}),
]
RAW_VALID = [
    ("raw UTF-8 JSON on several lines",
     json.dumps({"password": "Wd5#\u00f6rch\u00e4rd-P\u00e9k", "username": "ingrid", "banned": []},
                ensure_ascii=False, indent=2) + "\n"),
]
REFUSED = [
    ("text that is not JSON", b"password=Wd5#orchard-Pk"),
    ("a JSON list", b'["Wd5#orchard-Pk", "ingrid", []]'),
    ("a missing field", b'{"password": "Wd5#orchard-Pk", "username": "ingrid"}'),
    ("an extra field", b'{"password": "Wd5#orchard-Pk", "username": "ingrid", "banned": [], "mode": "strict"}'),
    ("a username with a space", b'{"password": "Wd5#orchard-Pk", "username": "in grid", "banned": []}'),
    ("a password that is a number", b'{"password": 5501, "username": "ingrid", "banned": []}'),
]

blobs = [json.dumps(r).encode("utf-8") for _, r in VALID] + [t.encode("utf-8") for _, t in RAW_VALID]
labels = [(label, short(r)) for label, r in VALID] + [(label, short(t)) for label, t in RAW_VALID]
blobs += [b for _, b in REFUSED]

results = run_bytes_all(blobs)
problems = []
for (label, shown), (status, out) in zip(labels, results[:len(labels)]):
    try:
        text = out.decode("utf-8")
    except UnicodeDecodeError:
        problems.append(f"{label} {shown}: standard output is not UTF-8 text")
        continue
    if not text.strip():
        problems.append(f"{label} {shown}: status {status} and nothing on standard output, expected a JSON object")
        continue
    try:
        body = json.loads(text)
    except json.JSONDecodeError:
        problems.append(f"{label} {shown}: standard output is not exactly one JSON value: {short(text, 70)}")
        continue
    reason = shape_problem(status, body)
    if reason:
        problems.append(f"{label} {shown}: {reason}")

for (label, data), (status, out) in zip(REFUSED, results[len(labels):]):
    if status != 2 or out != b"":
        problems.append(f"{label}: expected status 2 and no output, got status {status} "
                        f"and {short(out.decode('utf-8', 'replace'), 60)}")

finish(problems, f"interface ok: {len(labels)} valid requests answered, {len(REFUSED)} refused")
