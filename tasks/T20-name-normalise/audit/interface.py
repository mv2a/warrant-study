"""X1 (C1): the command's interface for accepted and refused requests.

The display name is compared without regard to case, so a capitalisation fault does not
show up here."""

import json

from _cmd import call, finish

problems = []


def accepted(label, expect, request=None, raw=None):
    status, body = call(request, raw=raw)
    if status != 0:
        problems.append(f"{label}: expected exit status 0, got {status} with {body!r}")
    elif not isinstance(body, dict):
        problems.append(f"{label}: expected one JSON object on stdout, got {body!r}")
    elif set(body) != {"display", "key"}:
        problems.append(f"{label}: expected exactly the fields display and key, got {sorted(body)}")
    elif not all(isinstance(body[f], str) for f in ("display", "key")):
        problems.append(f"{label}: display and key must be strings, got {body!r}")
    elif body["display"].casefold() != expect["display"].casefold() or body["key"] != expect["key"]:
        problems.append(f"{label}: expected {expect!r}, got {body!r}")


def refused(label, request=None, raw=None):
    status, body = call(request, raw=raw)
    if status == 0 and isinstance(body, dict) and {"display", "key"} <= set(body):
        return  # normalised instead of refused: that is C2's business, checked elsewhere
    if status != 2 or body is not None:
        problems.append(f"{label}: expected status 2 and nothing on stdout, got status {status} and {body!r}")


plain = {"display": "Tobias Brandt", "key": "tobiasbrandt"}
accepted("a plain name", plain, {"name": "tobias brandt"})
accepted("other fields, including ones called display and key", plain,
         {"name": "tobias brandt", "display": "Someone Else", "key": "someoneelse",
          "honorific": "Dr", "age": 41, "tags": ["x"], "extra": {"name": 5}, "flag": None})
accepted("name as the last field", plain, {"list_id": 7, "opt_in": True, "name": "tobias brandt"})
accepted("whitespace around the JSON text", plain, raw='\n\t  {"name": "tobias brandt"}  \n\n')
accepted("UTF-8 text sent unescaped", {"display": "In\xeas Duarte", "key": "inesduarte"},
         raw='{"name":"In\xeas Duarte"}')
accepted("double quotes in the name", {"display": 'Ilse "lili" Keane', "key": "ilselilikeane"},
         {"name": 'ilse "lili" keane'})
accepted("a backslash in the name", {"display": "Ilse\\keane", "key": "ilsekeane"},
         raw=json.dumps({"name": "ilse\\keane"}))

refused("text that is not JSON", raw="tobias; brandt")
refused("an object without name", {"surname": "brandt"})
refused("a name that is a list", {"name": ["tobias"]})
refused("a name of 101 characters", {"name": "t" * 101})
refused("a name that is only an honorific", {"name": "Prof."})

finish(problems, "interface ok: 7 accepted, 5 refused")
