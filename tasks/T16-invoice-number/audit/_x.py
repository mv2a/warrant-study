"""Shared helpers for the audit checks (X), written from intent.md alone.

Calls the workspace's `next` at the byte level so a check can see exactly what
was written on standard output. Runs independent requests in parallel threads;
results come back in request order, so every check is deterministic.
"""

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from _cmd import finish  # noqa: F401  (re-exported for the check scripts)

COMMAND = "next"
PATH = os.path.join(os.environ["WARRANT_WORKSPACE"], COMMAND)
PREFIX = {"lisbon": "LIS", "porto": "OPO", "faro": "FAO", "braga": "BRG"}
BRANCHES = list(PREFIX)


def encode(request=None, raw=None, ascii_only=True):
    """The bytes sent on stdin: a JSON-encoded request, or raw text/bytes as given."""
    if raw is None:
        return json.dumps(request, ensure_ascii=ascii_only).encode("utf-8")
    if isinstance(raw, str):
        return raw.encode("utf-8")
    return raw


def invoke(data, timeout=30, extra_env=None):
    """Run `next` with these stdin bytes. Returns (exit status, stdout bytes).
    extra_env, when given, is added to the inherited environment for this run."""
    if not os.access(PATH, os.X_OK):
        sys.exit(f"the workspace has no executable named {COMMAND}")
    env = {**os.environ, **extra_env} if extra_env else None
    try:
        done = subprocess.run([PATH], input=data, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 124, b""
    return done.returncode, done.stdout


def invoke_all(payloads):
    """Run `next` once per payload (bytes), in parallel; results in payload order."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(invoke, payloads))


def parse(out):
    """The JSON object written on stdout, or None when stdout is not one JSON object."""
    try:
        value = json.loads(out.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def show(value, width=100):
    text = repr(value)
    return text if len(text) <= width else text[: width - 3] + "..."


def well_formed(previous, prefix):
    """intent C2, as an oracle: PREFIX-YYYY-NNNNN, ASCII digits, year 2000-9999, sequence not 00000."""
    if not isinstance(previous, str):
        return False
    m = re.fullmatch(r"([A-Z]{3})-([0-9]{4})-([0-9]{5})", previous)
    if not m or m.group(1) != prefix:
        return False
    return 2000 <= int(m.group(2)) <= 9999 and int(m.group(3)) != 0


def expect_refusals(problems, cases, what="refused"):
    """cases: list of (label, payload bytes). Each must exit with status 2 (a refusal)."""
    results = invoke_all([payload for _, payload in cases])
    for (label, _), (status, out) in zip(cases, results):
        if status != 2:
            extra = f", output {show(out)}" if out.strip() else ""
            problems.append(f"{label}: status {status}, expected 2 ({what}){extra}")
    return len(cases)
