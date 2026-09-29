"""X9 (C4): `split` reads one JSON object on standard input and writes one JSON object on
standard output, both as UTF-8 text, with exactly subtotal_cents, tip_cents and
total_cents (integers) and shares (an object from each diner's name to integer cents),
exiting 0; other fields in the request are ignored; a refused request exits 2 and writes
nothing at all on standard output."""

import json
import os
import subprocess

from _cmd import PATH, call, finish
from _model import bill

FIELDS = {"subtotal_cents", "tip_cents", "total_cents", "shares"}

VALID = [
    bill([("Nell", "own"), ("Oda", "share"), ("Pim", "share")], [("Nell", 2210), ("Oda", 1450), ("Pim", 333)], 18),
    bill([("Zoë", "share"), ("Björn", "share")], [("Zoë", 1999)], 9),
    bill([("Galo", "own")], [("Galo", 5)], 100),
    bill([("Tove", "own"), ("Suvi", "own"), ("Rune", "share")], [("Tove", 1), ("Suvi", 2)], 0),
]

problems = []


def raw_run(text):
    """Send text as UTF-8 bytes, whatever the locale. Returns (exit status, raw stdout bytes)."""
    if not os.access(PATH, os.X_OK):
        raise SystemExit("the workspace has no executable named split")
    try:
        done = subprocess.run([PATH], input=text.encode("utf-8"), capture_output=True, timeout=10)
    except subprocess.TimeoutExpired:
        return 124, b"(timed out)"
    return done.returncode, done.stdout


def utf8_call(text):
    """Send text as UTF-8 bytes and read standard output as UTF-8 JSON, whatever the locale."""
    status, out = raw_run(text)
    try:
        return status, json.loads(out.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return status, out


def shape(label, status, body, names):
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
    elif not isinstance(body, dict):
        problems.append(f"{label}: standard output is not one JSON object: {body!r}")
    elif set(body) != FIELDS:
        problems.append(f"{label}: expected exactly the fields {sorted(FIELDS)}, got {sorted(body)}")
    elif not all(type(body[f]) is int for f in FIELDS - {"shares"}):
        problems.append(f"{label}: subtotal_cents, tip_cents and total_cents must be integers, got {body!r}")
    elif not isinstance(body["shares"], dict) or sorted(body["shares"]) != sorted(names):
        problems.append(f"{label}: shares must map exactly the names {names}, got {body['shares']!r}")
    elif not all(type(v) is int for v in body["shares"].values()):
        problems.append(f"{label}: every share must be an integer, got {body['shares']!r}")
    else:
        return True
    return False


for k, request in enumerate(VALID, 1):
    names = [d["name"] for d in request["diners"]]
    status, body = call(request)
    if not shape(f"request {k}", status, body, names):
        continue

    # The same request written differently: pretty-printed with CRLF line ends, and with
    # non-ASCII names sent as raw UTF-8 bytes instead of \u escapes.
    pretty = json.dumps(request, indent=4, ensure_ascii=False).replace("\n", "\r\n")
    status2, body2 = utf8_call("\n  " + pretty + "\n\n")
    if status2 != 0 or body2 != body:
        problems.append(f"request {k} pretty-printed: expected {body!r}, got {body2!r} (status {status2})")

    # The same request with extra fields everywhere, which must be ignored.
    noisy = json.loads(json.dumps(request))
    noisy.update({"currency": "EUR", "table": 12, "tip_cents": 99999, "subtotal_cents": 1,
                  "shares": {names[0]: 1}, "note": {"pays": "own"}})
    for seat, d in enumerate(noisy["diners"]):
        d.update({"seat": seat, "allergies": ["nuts"], "price_cents": 5000})
    for i in noisy["items"]:
        i.update({"dish": "gnocchi", "qty": 3, "price": 123456, "pays": "share", "diners": names})
    status3, body3 = call(noisy)
    if status3 != 0 or body3 != body:
        problems.append(f"request {k} with extra fields: expected {body!r}, got {body3!r} (status {status3})")


REFUSED = [
    ("text that is not JSON", "one bill, three friends"),
    ("a missing tip_percent", json.dumps({"diners": [{"name": "Oda", "pays": "own"}],
                                          "items": [{"diner": "Oda", "price_cents": 700}]})),
    ("pays both", json.dumps({"diners": [{"name": "Oda", "pays": "both"}],
                              "items": [{"diner": "Oda", "price_cents": 700}], "tip_percent": 10})),
    ("a zero price", json.dumps({"diners": [{"name": "Oda", "pays": "own"}],
                                 "items": [{"diner": "Oda", "price_cents": 0}], "tip_percent": 10})),
]
for label, text in REFUSED:
    status, out = raw_run(text)
    if status != 2 or out != b"":
        problems.append(f"{label}: expected status 2 and an empty standard output, got status {status} and {out[:80]!r}")

finish(problems, f"interface ok: {len(VALID) * 3} requests split, {len(REFUSED)} refused")
