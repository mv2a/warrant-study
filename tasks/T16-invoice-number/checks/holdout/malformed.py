"""H5: malformed previous numbers are refused, never continued."""

from _cmd import call, finish

PREFIXES = {"lisbon": "LIS", "porto": "OPO", "faro": "FAO", "braga": "BRG"}
ARABIC_41 = "٠٠٠٤١"  # 00041 in Arabic-Indic digits
FULLWIDTH_2026 = "２０２６"  # 2026 in fullwidth digits

# Every one of these is sent for lisbon with year 2026.
MALFORMED = [
    "LIS-2026-42", "LIS-2026-0041", "LIS-2026-000041", "LIS-2026-100000", "LIS-2026-1",
    "lis-2026-00041", "Lis-2026-00041", "LIs-2026-00041",
    "LIS-26-00041", "LIS-026-00041", "LIS-02026-00041", "LIS-1999-00041", "LIS-0000-00001", "LIS-1000-00001",
    "LIS-2026-00000", "LIS-2025-00000",
    " LIS-2026-00041", "LIS-2026-00041 ", "LIS-2026-00041\n", "\nLIS-2026-00041", "LIS-2026-00041\t",
    "LIS -2026-00041", "LIS-2026- 0041", "LIS-2026-0004 1", "LIS-2026-00041​",
    "LIS_2026_00041", "LIS/2026/00041", "LIS 2026 00041", "LIS.2026.00041", "LIS2026-00041", "LIS-202600041",
    "LIS2026000041", "LIS--2026-00041", "LIS-2026--00041", "LIS-2026-00041-", "-LIS-2026-00041",
    "LIS-2026-00041-2", "LIS-2026-00041LIS-2026-00042",
    "LIS-2026-+0041", "LIS-2026--0041", "LIS-+026-00041", "LIS-2026-0_041", "LIS-2_26-00041",
    "LIS-2026-0004a", "LIS-2O26-00041", "LIS-2026-O0041", "LIS-2026-0x041", "LIS-2026-1e003",
    "LIS-2026-" + ARABIC_41, "LIS-" + FULLWIDTH_2026 + "-00041", "ＬIS-2026-00041",
    # look-alike letters and dashes: Greek capital iota, fullwidth S, non-breaking hyphen,
    # fullwidth and small hyphen-minus, figure dash, soft hyphen
    "L\u0399S-2026-00041", "LI\uff33-2026-00041", "LIS\u20112026-00041", "LIS\uff0d2026\uff0d00041",
    "LIS-2026\ufe6300041", "LIS\u20122026-00041", "LIS\u00ad2026-00041",
    "", "LIS", "LIS-2026", "LIS-2026-", "2026-00041", "00041", "41", "-2026-00041", "LIS--00041",
    "XLIS-2026-00041", "LISB-2026-00041", "LI-2026-00041", "LIS-2026-00041 (copy)",
]
# Well-formed for lisbon in 2026: each must be accepted.
ACCEPTED = ["LIS-2026-00041", "LIS-2025-00001", "LIS-2025-99999", "LIS-2026-00001", "LIS-2026-10000", "LIS-2026-99998"]

cases = [("lisbon", previous) for previous in MALFORMED]
for branch in PREFIXES:
    for other, prefix in PREFIXES.items():
        if other != branch:
            cases.append((branch, f"{prefix}-2026-00041"))
            cases.append((branch, f"{prefix}-2025-00007"))

problems = []
for branch, previous in cases:
    status, body = call({"branch": branch, "year": 2026, "previous": previous})
    if status != 2 or body is not None:
        problems.append(f"{branch} after {previous!r}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for previous in ACCEPTED:
    status, body = call({"branch": "lisbon", "year": 2026, "previous": previous})
    if status != 0 or not isinstance(body, dict):
        problems.append(f"lisbon after {previous!r}: a well-formed number must be accepted, got {body!r} (status {status})")

finish(problems, f"malformed numbers ok: {len(cases)} refused, {len(ACCEPTED)} accepted")
