"""X2 (C2): requests that are not JSON, not an object, lack "name" or have a non-string name."""

import json

from _audit import is_refusal, show
from _cmd import call, finish

NOT_JSON = [
    "",
    "   \n",
    "{",
    "}",
    "{'name': 'maren okafor'}",
    '{name: "maren okafor"}',
    "name=maren okafor",
    '{"name": "maren okafor",}',
    '{"name": "maren okafor"',
    '{"name": "maren okafor"} {"name": "kofi haddad"}',
    '{"name": "maren\x01okafor" x}',
]
NOT_OBJECT = ['"maren okafor"', '["maren okafor"]', '[{"name": "maren okafor"}]', "null", "42", "-1.5", "true", "false"]
BAD_FIELDS = [
    {},
    {"Name": "maren okafor"},
    {"NAME": "maren okafor"},
    {"names": "maren okafor"},
    {" name": "maren okafor"},
    {"first": "maren", "last": "okafor"},
    {"name": 42},
    {"name": 0},
    {"name": 4.5},
    {"name": None},
    {"name": True},
    {"name": False},
    {"name": []},
    {"name": ["maren", "okafor"]},
    {"name": {"first": "maren"}},
]

problems = []
cases = [(raw, raw) for raw in NOT_JSON + NOT_OBJECT] + [(json.dumps(req), req) for req in BAD_FIELDS]
for raw, label in cases:
    status, body = call(raw=raw)
    if not is_refusal(status, body):
        problems.append(f"{show(label)}: expected a refusal (status 2), got status {status} and {body!r}")

finish(problems, f"malformed requests ok: {len(cases)} refused")
