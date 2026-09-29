"""X2 (C5): the command reads the request as a JSON object, so key order, whitespace,
layout and escape sequences do not change the answer, and extra fields are ignored.
Each variant must get exactly the answer the command gives for the plain request."""

import itertools
import json

from _x import encode, finish, invoke_all, parse, show

BASES = [
    {"branch": "porto", "year": 2045, "previous": "OPO-2045-00613"},
    {"branch": "braga", "year": 2046, "previous": None},
    {"branch": "lisbon", "year": 2050, "previous": "LIS-2049-00420"},
    {"branch": "faro", "year": 2600, "previous": "FAO-2600-09999"},
]

EXTRAS = [
    {"number": "OPO-2045-99999"},
    {"sequence": 7},
    {"prefix": "XYZ"},
    {"Branch": "coimbra"},
    {"branch ": "coimbra"},
    {"YEAR": 1999},
    {"Previous": "garbage"},
    {"note": None},
    {"lines": [1, 2, 3], "customer": {"name": "Tasca do Ze", "vat": "PT000000000"}},
    {"issued_by": "rui", "draft": True, "total": 1520.75},
]


def layouts(request):
    """The same JSON object written in other valid ways."""
    out = []
    for keys in itertools.permutations(request):
        out.append(json.dumps({k: request[k] for k in keys}))
    out.append(json.dumps(request, indent=2))
    out.append(json.dumps(request, indent="\t") + "\n")
    out.append("\n\t  " + json.dumps(request) + "  \n\n")
    out.append(json.dumps(request, separators=(",", ":")))
    out.append(json.dumps(request, indent=1).replace("\n", "\r\n") + "\r\n")
    # every character of the keys and of the text values written as \u escapes
    parts = []
    for k, v in request.items():
        key = "".join(f"\\u{ord(c):04x}" for c in k)
        val = '"' + "".join(f"\\u{ord(c):04x}" for c in v) + '"' if isinstance(v, str) else json.dumps(v)
        parts.append(f'"{key}": {val}')
    out.append("{" + ", ".join(parts) + "}")
    return out


problems = []
cases = []
for base in BASES:
    for text in layouts(base):
        cases.append((base, "layout " + show(text, 60), text.encode("utf-8")))
    for extra in EXTRAS:
        cases.append((base, "extra fields " + show(extra, 60), encode({**base, **extra})))
        cases.append((base, "extra fields first " + show(extra, 50), encode({**extra, **base})))

plain = dict(zip(map(json.dumps, BASES), invoke_all([encode(b) for b in BASES])))
for base in BASES:
    status, out = plain[json.dumps(base)]
    if status != 0 or parse(out) is None:
        problems.append(f"plain request {show(base)} did not succeed (status {status}, stdout {show(out)})")

results = invoke_all([payload for _, _, payload in cases])
for (base, label, _), (status, out) in zip(cases, results):
    want_status, want_out = plain[json.dumps(base)]
    if want_status != 0:
        continue
    if status != 0 or parse(out) != parse(want_out):
        problems.append(f"{base['branch']} {label}: got status {status} {show(out, 60)}, expected {show(want_out, 60)}")

finish(problems, f"encodings ok: {len(cases)} variants of {len(BASES)} requests")
