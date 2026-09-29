"""Shared plumbing for the three scenario checks: run one loan and compare stated facts."""

from _batch import raw
import json


def run(text):
    """Run a request written as text. Returns (body or None, problems)."""
    status, out = raw(text)
    try:
        body = json.loads(out) if out else None
    except json.JSONDecodeError:
        body = None
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("rows"), list) or not body["rows"]:
        return None, [f"expected a schedule for {text!r}, got status {status} and {out!r}"[:300]]
    return body, []


def row_field(rows, index, key):
    try:
        row = rows[index]
        return row.get(key) if isinstance(row, dict) else None
    except IndexError:
        return None
