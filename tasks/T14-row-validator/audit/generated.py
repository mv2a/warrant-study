"""X15 (G1-G5, C2, C3): seeded random schemas and tables, compared exactly, in order, with an independent model of intent.md."""

import random
import sys

from _audit import expect, request_text
from _cmd import finish
from _oracle import expected_errors, gen_rows, gen_schema

SEEDS = [int(s) for s in sys.argv[1:]] or [5_210_914, 8_830_266, 9_417_003]
PER_SEED = 60

problems = []
tables = rows_seen = errors_seen = 0
for seed in SEEDS:
    rng = random.Random(seed)
    for case in range(PER_SEED):
        schema = gen_schema(rng)
        rows = gen_rows(rng, schema)
        want = expected_errors(schema, rows)
        tables += 1
        rows_seen += len(rows)
        errors_seen += len(want)
        before = len(problems)
        expect(problems, f"seed {seed} table {case}", request_text(schema, rows), want, ordered=True, nrows=len(rows))
        if len(problems) > before and len(problems) == 1:
            # Show the smallest failing request once, to make the failure easy to reproduce.
            problems.append(f"  request: {request_text(schema, rows)[:240]}")
    if len(problems) > 10:
        break

finish(problems, f"generated ok: {tables} tables, {rows_seen} rows, {errors_seen} errors, seeds {SEEDS}")
