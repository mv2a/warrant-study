"""Helpers shared by the audit checks (X). Written from intent.md alone."""

import json
import os
import subprocess
import sys

from _cmd import PATH

CODES = ("missing", "type", "range", "allowed", "duplicate")


def e(row, field, code):
    return {"row": row, "field": field, "code": code}


def canon(value):
    """JSON text with sorted keys, so that 1 and true, or 0 and 0.0, never compare equal."""
    return json.dumps(value, sort_keys=True)


def request_text(schema, rows, literals=None, **extra):
    """The request as JSON text. A string value equal to a key of `literals` is replaced by that raw JSON text."""
    text = json.dumps({"schema": schema, "rows": rows, **extra})
    for marker, literal in (literals or {}).items():
        quoted = json.dumps(marker)
        if quoted not in text:
            raise ValueError(f"marker {marker} not used")
        text = text.replace(quoted, literal)
    return text


def run(text, timeout=10):
    """Send raw text on standard input. Returns (exit status, stdout, stderr)."""
    if not os.access(PATH, os.X_OK):
        sys.exit("the workspace has no executable named validate")
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
    return done.returncode, done.stdout, done.stderr


def shape_problem(body, nrows=None):
    """None when body has exactly the output shape of C1, else a short description."""
    if not isinstance(body, dict) or set(body) != {"valid", "errors"}:
        return f"output must be an object with exactly valid and errors, got {str(body)[:80]}"
    if type(body["valid"]) is not bool or type(body["errors"]) is not list:
        return f"valid must be true or false and errors a list, got {str(body)[:80]}"
    for error in body["errors"]:
        if not isinstance(error, dict) or set(error) != {"row", "field", "code"}:
            return f"each error needs exactly row, field and code, got {str(error)[:80]}"
        if type(error["row"]) is not int or type(error["field"]) is not str or error["code"] not in CODES:
            return f"badly typed error {canon(error)[:80]}"
        if nrows is not None and not 0 <= error["row"] < nrows:
            return f"error names a row outside the table: {canon(error)[:80]}"
    if body["valid"] != (body["errors"] == []):
        return f"valid must be true exactly when errors is empty, got valid={body['valid']} with {len(body['errors'])} errors"
    return None


def answer(text, nrows=None):
    """Run a request that must be accepted. Returns (body, problem)."""
    status, out, err = run(text)
    if status != 0:
        return None, f"exited with status {status}, expected 0 ({err.strip()[:70]!r})"
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        return None, f"standard output is not one JSON value: {out.strip()[:70]!r}"
    problem = shape_problem(body, nrows)
    return (None, problem) if problem else (body, None)


def _key(error):
    return (error["row"], error["field"], error["code"])


def differences(expected, got, ordered):
    if ordered and canon(expected) == canon(got):
        return None
    if not ordered and canon(sorted(expected, key=_key)) == canon(sorted(got, key=_key)):
        return None
    exp_set, got_set = [canon(x) for x in expected], [canon(x) for x in got]
    lost = [x for x in exp_set if x not in got_set]
    extra = [x for x in got_set if x not in exp_set]
    parts = []
    if lost:
        parts.append(f"missing {len(lost)} expected error(s), e.g. {', '.join(lost[:2])}")
    if extra:
        parts.append(f"{len(extra)} unexpected error(s), e.g. {', '.join(extra[:2])}")
    if not parts:
        if len(expected) != len(got):
            parts.append(f"expected {len(expected)} errors, got {len(got)} (some repeated)")
        else:
            first = next(i for i, (a, b) in enumerate(zip(expected, got)) if canon(a) != canon(b))
            parts.append(f"right errors in the wrong order; position {first} should be {canon(expected[first])}, got {canon(got[first])}")
    return "; ".join(parts)


def expect(problems, label, text, errors, ordered=False, nrows=None):
    """Check that the request is accepted and reports exactly `errors` (in this order when ordered)."""
    body, problem = answer(text, nrows)
    if problem:
        problems.append(f"{label}: {problem}")
        return None
    diff = differences(errors, body["errors"], ordered)
    if diff:
        problems.append(f"{label}: {diff}")
    return body


def refused(problems, label, text):
    """Check that the request is refused: exit status 2, nothing on stdout, a reason on stderr."""
    status, out, err = run(text)
    if status != 2:
        problems.append(f"{label}: must be refused with status 2, got status {status} and {out.strip()[:60]!r}")
    elif out != "":
        problems.append(f"{label}: a refusal must write nothing to standard output, got {out.strip()[:60]!r}")
    elif not err.strip():
        problems.append(f"{label}: a refusal must say why on standard error, but it was empty")


def expect_each(problems, label, schema_json, row_texts, expected):
    """For promises about single cells: try the whole table, and if it disagrees, judge each row on its own.

    `schema_json` and each of `row_texts` are raw JSON text; `expected` holds errors indexed by row position.
    A table that fails only as a whole is left to the checks of the multi-row promises (G4, G5, C3).
    """
    text = '{"schema": %s, "rows": [%s]}' % (schema_json, ", ".join(row_texts))
    trial = []
    expect(trial, label, text, expected, nrows=len(row_texts))
    if not trial:
        return
    for index, row_text in enumerate(row_texts):
        want = [e(0, err["field"], err["code"]) for err in expected if err["row"] == index]
        one = '{"schema": %s, "rows": [%s]}' % (schema_json, row_text)
        expect(problems, f"{label}, row {row_text[:48]}", one, want, nrows=1)
