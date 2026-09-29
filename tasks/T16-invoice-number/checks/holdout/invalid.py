"""H7: invalid requests are refused."""

import json
import os
import subprocess
import sys

from _cmd import PATH, call, finish

BASE = {"branch": "lisbon", "year": 2026, "previous": "LIS-2026-00041"}


def without(field):
    return json.dumps({key: value for key, value in BASE.items() if key != field})


def with_(field, raw_value):
    """The base request with one field replaced by raw JSON text."""
    parts = [f'"{key}": {raw_value if key == field else json.dumps(value)}' for key, value in BASE.items()]
    return "{" + ", ".join(parts) + "}"


INVALID = [
    ("text that isn't JSON", "next invoice please"),
    ("empty input", ""),
    ("truncated JSON", '{"branch": "lisbon", "year": 2026'),
    ("a list", '["lisbon", 2026, null]'),
    ("a string", '"lisbon"'),
    ("a number", "2026"),
    ("null", "null"),
    ("a missing branch", without("branch")),
    ("a missing year", without("year")),
    ("a missing previous", without("previous")),
    ("an empty object", "{}"),
]
for raw in ('"Lisbon"', '"LISBON"', '"LIS"', '"coimbra"', '" lisbon"', '"lisbon "', '""', "7", "null", "true", '["lisbon"]', '{"name": "lisbon"}'):
    INVALID.append((f"branch {raw}", with_("branch", raw)))
for raw in ('"2026"', "2026.0", "2026.5", "2.026e3", "true", "false", "null", "1999", "0", "-2026", "10000", "26", "[2026]", "1e400"):
    INVALID.append((f"year {raw}", with_("year", raw)))
for raw in ("41", "0", "true", "false", '["LIS-2026-00041"]', '{"number": "LIS-2026-00041"}'):
    INVALID.append((f"previous {raw}", with_("previous", raw)))

# Standard input that isn't valid UTF-8, sent as raw bytes. The last one is a valid request
# except for an ignored extra field, which must not rescue it.
GOOD = b'{"branch": "lisbon", "year": 2026, "previous": "LIS-2026-00041"'
UNDECODABLE = [
    ("a broken two-byte sequence", b"\xc3\x28"),
    ("the request in UTF-16 with a byte order mark", (GOOD.decode() + "}").encode("utf-16")),
    ("an overlong hyphen in previous", GOOD.replace(b"LIS-2026", b"LIS\xc0\xad2026") + b"}"),
    ("a stray continuation byte in previous", GOOD.replace(b"00041", b"0004\x811") + b"}"),
    ("an encoded surrogate in branch", GOOD.replace(b"lisbon", b"lisbon\xed\xa0\x80") + b"}"),
    ("a latin-1 byte in an ignored field", GOOD + b', "memo": "pago em d\xe9bito"}'),
]
# Python decodes text-mode stdin strictly in a UTF-8 locale and with surrogate escapes in
# the C locale; pin each so the verdict does not depend on this machine.
STDIN_MODES = ("utf-8:strict", "utf-8:surrogateescape")


def call_bytes(data, mode):
    if not os.access(PATH, os.X_OK):
        sys.exit("the workspace has no executable named next")
    env = {**os.environ, "PYTHONIOENCODING": mode}
    try:
        done = subprocess.run([PATH], input=data, capture_output=True, env=env, timeout=10)
    except subprocess.TimeoutExpired:
        return 124, b""
    return done.returncode, done.stdout


problems = []
for name, data in UNDECODABLE:
    for mode in STDIN_MODES:
        status, out = call_bytes(data, mode)
        if status != 2 or out.strip():
            problems.append(f"{name} ({mode}): expected a refusal (status 2, no output), got status {status} and {out[:60]!r}")
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for year, previous, expected in ((2000, None, 1), (9999, None, 1), (2026, "LIS-2026-00041", 42)):
    status, body = call({"branch": "lisbon", "year": year, "previous": previous})
    got = body.get("sequence") if isinstance(body, dict) else None
    if status != 0 or got != expected:
        problems.append(f"lisbon, {year}, {previous}: a valid request must give sequence {expected}, got {body!r} (status {status})")

finish(problems, f"invalid requests ok: {len(INVALID)} refused, {len(UNDECODABLE)} undecodable inputs refused")
