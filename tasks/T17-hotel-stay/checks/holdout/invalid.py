"""H7: invalid requests are refused, never priced; the edges of the valid ranges are priced."""

import json
import os
import subprocess

from _cmd import PATH, call, finish
from _model import priced, refused

GOOD = {"check_in": "mon", "nights": 2, "rate_cents": 10000}


def with_(**changes):
    return json.dumps({**GOOD, **changes})


def without(field):
    return json.dumps({k: v for k, v in GOOD.items() if k != field})


INVALID = [
    ("empty input", ""),
    ("text", "a double room please"),
    ("cut-off JSON", '{"check_in": "mon", "nights": 2'),
    ("a JSON list", json.dumps([GOOD])),
    ("a JSON string", json.dumps("mon")),
    ("a JSON number", "42"),
    ("JSON null", "null"),
    ("a second object after the first", json.dumps(GOOD) + json.dumps(GOOD)),
    ("a number after the object", json.dumps(GOOD) + "\n7"),
    ("a word after the object", json.dumps(GOOD) + " please"),
    ("a stray closing brace after the object", json.dumps(GOOD) + "}"),
    ("no check_in", without("check_in")),
    ("no nights", without("nights")),
    ("no rate_cents", without("rate_cents")),
    ("an empty object", "{}"),
    ("check_in Mon", with_(check_in="Mon")),
    ("check_in FRI", with_(check_in="FRI")),
    ("check_in friday", with_(check_in="friday")),
    ("check_in monday", with_(check_in="monday")),
    ("check_in empty", with_(check_in="")),
    ("check_in with a space", with_(check_in=" mon")),
    ("check_in a number", with_(check_in=1)),
    ("check_in null", with_(check_in=None)),
    ("check_in a list", with_(check_in=["mon"])),
    ("nights 0", with_(nights=0)),
    ("nights -1", with_(nights=-1)),
    ("nights 31", with_(nights=31)),
    ("nights 365", with_(nights=365)),
    ("nights 2.5", with_(nights=2.5)),
    ("nights 2.0", with_(nights=2.0)),
    ("nights '3'", with_(nights="3")),
    ("nights true", with_(nights=True)),
    ("nights false", with_(nights=False)),
    ("nights null", with_(nights=None)),
    ("nights a list", with_(nights=[2])),
    ("nights 1e1", '{"check_in": "mon", "nights": 1e1, "rate_cents": 10000}'),
    ("rate 0", with_(rate_cents=0)),
    ("rate -500", with_(rate_cents=-500)),
    ("rate 99.5", with_(rate_cents=99.5)),
    ("rate 10000.0", with_(rate_cents=10000.0)),
    ("rate '10000'", with_(rate_cents="10000")),
    ("rate true", with_(rate_cents=True)),
    ("rate null", with_(rate_cents=None)),
    ("rate an object", with_(rate_cents={"cents": 10000})),
]
VALID_EDGES = [
    {"check_in": "mon", "nights": 1, "rate_cents": 10000},
    {"check_in": "tue", "nights": 30, "rate_cents": 10000},
    {"check_in": "mon", "nights": 2, "rate_cents": 1},
    {"check_in": "sun", "nights": 2, "rate_cents": 10 ** 9},
]
# Spaces, tabs and line breaks after the object are allowed, so these are priced too.
TRAILING_WHITESPACE = [json.dumps(GOOD) + "\n", json.dumps(GOOD) + " \t\r\n "]

# Requests whose bytes are not UTF-8 text. How a Python program decodes standard input
# depends on the locale (surrogateescape under POSIX "C", strict under a UTF-8 locale), so
# each is sent under two fixed settings rather than the host's own. A program that fails to
# decode exits 1 with a traceback, which is a crash, not a refusal, so these cases need the
# refusal status 2 itself.
NOT_UTF8 = [
    ("a Latin-1 byte in an ignored field",
     b'{"check_in": "mon", "nights": 2, "rate_cents": 10000, "guest": "Ren\xe9e"}'),
    ("a stray continuation byte before the object",
     b'\x80{"check_in": "mon", "nights": 2, "rate_cents": 10000}'),
]


def fixed_env(strict_utf8):
    env = {k: v for k, v in os.environ.items()
           if k not in ("LANG", "PYTHONIOENCODING", "PYTHONUTF8") and not k.startswith("LC_")}
    env["LC_ALL"] = "C"
    if strict_utf8:
        env["PYTHONIOENCODING"] = "utf-8:strict"
    return env


SETTINGS = [("the POSIX locale", fixed_env(False)),
            ("standard streams decoded strictly as UTF-8", fixed_env(True))]


def call_bytes(data, env):
    try:
        done = subprocess.run([PATH], input=data, capture_output=True, timeout=10, env=env)
    except subprocess.TimeoutExpired:
        return 124, ""
    return done.returncode, done.stdout.decode("utf-8", "replace").strip()


problems = []
for label, text in INVALID:
    status, body = call(raw=text)
    if not refused(status, body):
        problems.append(f"{label}: should be refused, got {body!r} (status {status})")
for request in VALID_EDGES:
    status, body = call(request)
    if not (priced(status, body) and "total_cents" in body):
        problems.append(f"{request}: is valid and should be priced, got {body!r} (status {status})")
for text in TRAILING_WHITESPACE:
    status, body = call(raw=text)
    if not (priced(status, body) and "total_cents" in body):
        problems.append(f"{text!r}: whitespace after the object is allowed, got {body!r} (status {status})")
for label, data in NOT_UTF8:
    for setting, env in SETTINGS:
        status, out = call_bytes(data, env)
        if status != 2 or "total_cents" in out:
            problems.append(f"{label}, under {setting}: should be refused with status 2, got status {status} and {out[:60]!r}")

finish(problems, f"invalid requests ok: {len(INVALID)} refused, {len(NOT_UTF8)} non-UTF-8 inputs refused under "
                 f"{len(SETTINGS)} settings, {len(VALID_EDGES) + len(TRAILING_WHITESPACE)} edge cases priced")
