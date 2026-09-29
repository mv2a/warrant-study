"""H5: the exact interface: fields and types on success, extra fields ignored, and the form of a refusal."""

import json
import subprocess

from _cmd import PATH, call, finish

FIELDS = {"room_cents", "discount_cents", "tax_cents", "total_cents"}
problems = []

valid = [
    {"check_in": "mon", "nights": 1, "rate_cents": 1},
    {"check_in": "fri", "nights": 3, "rate_cents": 13337},
    {"check_in": "sat", "nights": 30, "rate_cents": 250000},
    {"check_in": "wed", "nights": 7, "rate_cents": 9999},
]
for request in valid:
    status, body = call(request)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{request}: should exit 0 with one JSON object, got status {status} and {body!r}")
    elif set(body) != FIELDS:
        problems.append(f"{request}: fields should be exactly {sorted(FIELDS)}, got {sorted(body)}")
    elif not all(type(body[f]) is int for f in FIELDS):
        problems.append(f"{request}: every amount should be a JSON integer, got {body!r}")
    else:
        extra = dict(request, guest="room 12", currency="USD", nights_note=[1, 2], rate=5)
        status2, body2 = call(extra)
        if status2 != 0 or body2 != body:
            problems.append(f"{request}: extra fields should be ignored, but the answer changed to {body2!r} (status {status2})")

refusals = [
    ("text that is not JSON", "one room, two nights"),
    ("empty input", ""),
    ("a JSON list", json.dumps(["mon", 2, 10000])),
    ("no rate_cents", json.dumps({"check_in": "mon", "nights": 2})),
    ("0 nights", json.dumps({"check_in": "mon", "nights": 0, "rate_cents": 10000})),
    ("check_in Fri", json.dumps({"check_in": "Fri", "nights": 3, "rate_cents": 10000})),
    ("31 nights", json.dumps({"check_in": "mon", "nights": 31, "rate_cents": 10000})),
    ("a rate of 0", json.dumps({"check_in": "mon", "nights": 2, "rate_cents": 0})),
    ("a Saturday night in a 1-night stay", json.dumps({"check_in": "sat", "nights": 1, "rate_cents": 10000})),
]
for label, text in refusals:
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        problems.append(f"{label}: timed out")
        continue
    if done.returncode != 2:
        problems.append(f"{label}: a refusal should exit with status 2, got {done.returncode}")
    elif done.stdout.strip():
        problems.append(f"{label}: a refusal should write nothing on standard output, got {done.stdout.strip()[:60]!r}")
    elif not done.stderr.strip():
        problems.append(f"{label}: a refusal should say why on standard error")

finish(problems, f"interface ok: {len(valid)} valid requests, {len(refusals)} refusals")
