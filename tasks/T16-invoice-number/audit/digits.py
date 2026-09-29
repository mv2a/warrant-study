"""X8 (C2): digits are only ASCII 0-9. Previous numbers whose year or sequence uses other
Unicode digits (Arabic-Indic, Persian, Devanagari, Bengali, Thai, fullwidth, mathematical,
superscript), or spellings a lenient integer parser would accept (underscores, signs,
inner whitespace), are refused with status 2 for all four branches, in the request's year
and one year earlier; sent as \\u escapes and, when dated in the request's year, also as
raw UTF-8."""

from _x import PREFIX, encode, expect_refusals, finish, well_formed

DIGIT_SETS = {
    "arabic-indic": "٠١٢٣٤٥٦٧٨٩",
    "persian": "۰۱۲۳۴۵۶۷۸۹",
    "devanagari": "०१२३४५६७८९",
    "bengali": "০১২৩৪৫৬৭৮৯",
    "thai": "๐๑๒๓๔๕๖๗๘๙",
    "fullwidth": "０１２３４５６７８９",
    "math bold": "".join(chr(0x1D7CE + i) for i in range(10)),
    "superscript": "⁰¹²³⁴⁵⁶⁷⁸⁹",
}


def translate(text, digits):
    return "".join(digits[int(c)] if c in "0123456789" else c for c in text)


def variants(p, y, s):
    out = []
    for digits in DIGIT_SETS.values():
        out.append(f"{p}-{y}-{translate(s, digits)}")            # whole sequence
        out.append(f"{p}-{translate(str(y), digits)}-{s}")       # whole year
        out.append(f"{p}-{y}-{s[:-1]}{translate(s[-1], digits)}")  # one digit only
        out.append(f"{p}-{str(y)[:-1]}{translate(str(y)[-1], digits)}-{s}")
    out += [
        f"{p}-{y}-{s[0]}_{s[2:]}", f"{p}-{y}-{s[:3]}_{s[4]}", f"{p}-{y}-+{s[1:]}",
        f"{p}-{y}- {s[1:]}", f"{p}-{y}-\t{s[1:]}", f"{p}-{y}-{s[1:]} ", f"{p}-{y}-{s[1:]}\n",
        f"{p}-{y}--{s[1:]}", f"{p}-{str(y)[0]}_{str(y)[1:]}-{s}", f"{p}-+{y}-{s}",
        f"{p}- {y}-{s}", f"{p}-{y} -{s}", f"{p}-{y}-{s[:2]} {s[3:]}", f"{p}-{y}-{s[:4]}́",
    ]
    return out


cases, raw = [], []
for year, seq, (branch, prefix) in zip((2044, 3303, 8765, 9999), ("01742", "00318", "56789", "00009"), PREFIX.items()):
    for dated in (year, year - 1):
        for previous in variants(prefix, dated, seq):
            assert not well_formed(previous, prefix), previous
            label, request = f"{branch} {year} previous {previous!r}", {"branch": branch, "year": year, "previous": previous}
            cases.append((label, encode(request)))
            if dated == year and not previous.isascii():  # also sent as raw UTF-8 rather than \u escapes
                raw.append((label + " (raw UTF-8)", encode(request, ascii_only=False)))

problems = []
n = expect_refusals(problems, cases + raw, "only ASCII digits make a well-formed number")
finish(problems, f"digits ok: {n} previous numbers with non-ASCII or lenient digits refused")
