"""X9 (C3): invalid requests are refused, never taxed: exit status 2, and no tax response on
standard output. Covers input that is not a JSON object, missing fields, fields that are
not JSON integers (floats, whole-valued floats, strings, booleans, null, lists, objects,
non-finite numbers), a negative income, and dependents below 0 or above 20. Whether a
refusal also keeps standard output empty is C4's business, checked by X1 on the same
requests."""

from _cmd import finish
from _invalid import TEXTS
from _model import looks_taxed, run_raw, short

problems = []
for text in TEXTS:
    status, out = run_raw(text)
    if status != 2 or looks_taxed(out):
        problems.append(f"{short(repr(text), 70)}: expected a refusal (exit status 2, not taxed), "
                        f"got status {status} and output {short(repr(out), 60)}")

finish(problems, f"refusals ok: {len(TEXTS)} invalid requests")
