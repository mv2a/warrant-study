"""X08 (C3): requests that are not JSON, JSON that is not an object, and objects missing any of
the five fields are refused (status 2, no price). What a refusal writes is C1's business."""

import json

from _audit import check, parcel, refused

GOOD = parcel(2, 1800, 30, 25, 20)
GOOD_TEXT = json.dumps(GOOD)

NOT_JSON = [
    "",
    "   \n\t ",
    "zone 2, 1800 g, 30 x 25 x 20",
    "zone=2&weight_g=1800&length_cm=30&width_cm=25&height_cm=20",
    "{zone: 2, weight_g: 1800, length_cm: 30, width_cm: 25, height_cm: 20}",
    str(GOOD),                                  # a Python dict literal with single quotes
    GOOD_TEXT[:-1],                             # closing brace missing
    GOOD_TEXT[: len(GOOD_TEXT) // 2],           # cut off half way
    GOOD_TEXT[:-1] + ",}",                      # trailing comma
    GOOD_TEXT + " thanks",                      # trailing text
    GOOD_TEXT + GOOD_TEXT,                      # two objects
    "<parcel zone='2' weight_g='1800'/>",
]
NOT_OBJECT = [
    "[]",
    "[" + GOOD_TEXT + "]",
    json.dumps([2, 1800, 30, 25, 20]),
    '"' + GOOD_TEXT.replace('"', '\\"') + '"',  # the object quoted as a JSON string
    "1800",
    "2.5",
    "null",
    "true",
    "false",
    '"rate"',
]

cases = [(f"not JSON: {text[:40]!r}", text, refused) for text in NOT_JSON]
cases += [(f"not an object: {text[:40]!r}", text, refused) for text in NOT_OBJECT]
for field in GOOD:
    missing = {k: v for k, v in GOOD.items() if k != field}
    cases.append((f"missing {field}", missing, refused))
    renamed = {**missing, field.upper(): GOOD[field]}
    cases.append((f"{field} only in upper case", renamed, refused))
cases.append(("empty object", {}, refused))
cases.append(("only extra fields", {"parcel": GOOD}, refused))
cases.append(("weight only", {"weight_g": 1800}, refused))

check(cases, "malformed requests refused")
