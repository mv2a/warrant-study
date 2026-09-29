"""X01 (C1): the interface. A priced answer exits 0 with exactly one JSON object holding the four
integer fields, with total = base + surcharge; a refusal exits 2 with nothing at all on standard
output; no other exit status is allowed. The request's JSON layout (whitespace, key order) does
not change the answer. Which requests are priced and at what price is left to the other
promises: only the plain, valid parcels below must be priced."""

import json

from _audit import check, interface, parcel, parse, run_many, finish

PLAIN = (
    parcel(2, 3120, 28, 22, 14),     # weight-billed
    parcel(4, 640, 45, 35, 25),      # dimension-billed
    parcel(1, 18750, 104, 30, 12),   # heavy and oversize
    parcel(3, 1, 1, 1, 1),           # smallest valid parcel
)
LAYOUT = parcel(3, 4411, 33, 27, 19)
LAYOUTS = [
    ("indented JSON", json.dumps(LAYOUT, indent=2)),
    ("no spaces", json.dumps(LAYOUT, separators=(",", ":"))),
    ("surrounding whitespace", "\n\t  " + json.dumps(LAYOUT) + "  \n\n"),
    ("keys in reverse order", json.dumps(dict(reversed(list(LAYOUT.items()))))),
    ("sides listed first", '{"height_cm": 19, "length_cm": 33, "width_cm": 27, "weight_g": 4411, "zone": 3}'),
]
# Requests the intent refuses, one of each kind. If one is refused it must exit 2 and write nothing
# at all on standard output, not even a newline (C1); whether it is refused is C2's and C3's business.
REFUSALS = [
    ("text that is not JSON", "rate please"),
    ("an empty request", ""),
    ("a JSON list", "[3, 1200, 30, 20, 10]"),
    ("a missing field", '{"zone": 2, "weight_g": 900, "length_cm": 20, "width_cm": 20}'),
    ("zone 6", parcel(6, 1000, 10, 10, 10)),
    ("zone as text", parcel("2", 1000, 10, 10, 10)),
    ("a negative weight", parcel(1, -40, 10, 10, 10)),
    ("a zero side", parcel(2, 700, 0, 10, 10)),
    ("a fractional side", parcel(3, 700, 12.5, 10, 10)),
    ("a weight of true", parcel(4, True, 10, 10, 10)),
    ("a weight of 31,000 g", parcel(1, 31000, 20, 20, 20)),
    ("a dimensional weight of 40,000 g", parcel(2, 900, 100, 50, 40)),
    ("a side of 160 cm", parcel(3, 900, 160, 10, 10)),
    ("length plus girth of 320 cm", parcel(4, 900, 120, 90, 10)),
]

cases = [(f"plain {request}", request, interface(must_price=True)) for request in PLAIN]
cases += [(f"layout: {name}", text, interface(must_price=True)) for name, text in LAYOUTS]
cases += [(f"refusal: {name}", request, interface()) for name, request in REFUSALS]

# The same parcel sent in different layouts gets the same answer as the compact request.
layout_results = run_many([json.dumps(LAYOUT)] + [text for _, text in LAYOUTS])
compact = parse(layout_results[0][1])
problems = [
    f"layout: {name}: expected the same answer as the compact request ({compact}), got {parse(result[1])!r}"
    for (name, _), result in zip(LAYOUTS, layout_results[1:])
    if result[0] != layout_results[0][0] or parse(result[1]) != compact
]
if problems:
    finish(problems, "")

check(cases, "interface ok")
