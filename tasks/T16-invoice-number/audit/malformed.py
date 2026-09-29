"""X7 (C2): malformed previous numbers are refused with status 2, never continued or
restarted: every example the intent lists for lisbon, plus, for all four branches, other
branches' prefixes, wrong case, missing, doubled or substituted separators, wrong digit
counts, years outside 2000-9999 or not four digits, sequence 00000, and anything before,
after or in between. Each is sent both in the request's year and dated one year earlier,
so a restart must not skip the check."""

from _x import PREFIX, encode, expect_refusals, finish, well_formed

INTENT_EXAMPLES = [
    "OPO-2026-00041", "FAO-2026-00041", "BRG-2026-00041",
    "LIS-2026-42", "LIS-2026-000042", "lis-2026-00041", "LIS-26-00041",
    "LIS-1999-00041", "LIS-2026-00000", "LIS-2026-00041 ",
]

LOOKALIKE = {  # prefixes written with non-ASCII letters that look the same
    "LIS": ["LІЅ", "ＬＩＳ"],
    "OPO": ["ОРО", "ＯＰＯ"],
    "FAO": ["FАО", "ＦＡＯ"],
    "BRG": ["ВRG", "ＢＲＧ"],
}


def variants(p, y, s="00417"):
    """Malformed spellings of the well-formed number f"{p}-{y}-{s}"."""
    return [
        "", p, f"{p}-", f"{p}-{y}", f"{p}-{y}-", f"-{y}-{s}", f"{y}-{s}",
        f"{p}-{y}-0417", f"{p}-{y}-417", f"{p}-{y}-7", f"{p}-{y}-004170", f"{p}-{y}-{s}0",
        f"{p}{y}-{s}", f"{p}-{y}{s}", f"{p}{y}{s}", f"{p}--{y}-{s}", f"{p}-{y}--{s}",
        f"{p}_{y}_{s}", f"{p} {y} {s}", f"{p}/{y}/{s}", f"{p}.{y}.{s}",
        f"{p}–{y}–{s}", f"{p}‐{y}‐{s}", f"{p}−{y}−{s}",
        f" {p}-{y}-{s}", f"{p}-{y}-{s} ", f"\t{p}-{y}-{s}", f"{p}-{y}-{s}\n", f"\n{p}-{y}-{s}",
        f"{p}-{y}-{s}\r\n", f"{p}-{y}-{s} ", f"{p}-{y}-{s}​", f"﻿{p}-{y}-{s}",
        f"{p}-{y}-{s}-", f"-{p}-{y}-{s}", f"{p}-{y}-{s}/1", f"{p}-{y}-{s}{p}-{y}-{s}",
        f"{p}-{y}-{s},{p}-{y}-{s}", f"X{p}-{y}-{s}", f"{p}X-{y}-{s}", f"{p[:2]}-{y}-{s}",
        f"{p}{p[-1]}-{y}-{s}", f"{p.lower()}-{y}-{s}", f"{p.capitalize()}-{y}-{s}",
        f"{p[0].lower()}{p[1:]}-{y}-{s}", f"{p} -{y}-{s}", f"{p}- {y}-{s}", f"{p}-{y} -{s}",
        f"{p}-{y}-0041A", f"{p}-{y}-O0417", f"{p}-{y}-0041l", f"{p}-{y}-00 17", f"{p}-{y}-0x417",
        f"{p}-{y}-4.170", f"{p}-{y}-1e003", f"{p}-{y}-00000", f"{p}-{y}-0000",
        f"{p}-{str(y)[2:]}-{s}", f"{p}-0{y}-{s}", f"{p}-{y}0-{s}", f"{p}-{str(y)[:3]}-{s}",
        f"{p}-1999-{s}", f"{p}-0000-{s}", f"{p}-0999-{s}", f"{p}-1000-{s}", f"{p}-10000-{s}",
        *(f"{q}-{y}-{s}" for q in LOOKALIKE[p]),
        *(f"{q}-{y}-{s}" for q in PREFIX.values() if q != p),
    ]


cases = []
for previous in INTENT_EXAMPLES:
    cases.append((f"lisbon 2026 previous {previous!r}", {"branch": "lisbon", "year": 2026, "previous": previous}))
    if previous.startswith("LIS-2026"):  # the same malformations, dated one year earlier
        earlier = previous.replace("LIS-2026", "LIS-2025")
        cases.append((f"lisbon 2026 previous {earlier!r}", {"branch": "lisbon", "year": 2026, "previous": earlier}))

for year, (branch, prefix) in zip((2038, 2451, 7012, 9999), PREFIX.items()):
    for dated in (year, year - 1):
        for previous in variants(prefix, dated):
            assert not well_formed(previous, prefix), previous
            cases.append((f"{branch} {year} previous {previous!r}", {"branch": branch, "year": year, "previous": previous}))

payloads = [(label, encode(r)) for label, r in cases]
# the same requests with the text sent as raw UTF-8 rather than \u escapes
payloads += [(label + " (raw UTF-8)", encode(r, ascii_only=False)) for label, r in cases if not r["previous"].isascii()]

problems = []
n = expect_refusals(problems, payloads, "a malformed previous number must be refused")
finish(problems, f"malformed ok: {n} malformed previous numbers refused")
