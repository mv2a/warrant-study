"""X12 (C4): standard input that is not valid UTF-8 text is refused with status 2 rather
than crashing: stray bytes before or instead of the object, and invalid bytes inside the
branch, the year or the previous number (each of which is also invalid on its own).

How a Python program's standard input decodes such bytes depends on the caller's locale:
in a UTF-8 locale (LANG=en_US.UTF-8) reading it raises an error, while in the C locale
(LANG unset) the bytes arrive as surrogate escapes. So that the verdict never depends on
the machine that runs the audit, every case is sent under both conditions, pinned with
PYTHONIOENCODING, and must be refused under both."""

from concurrent.futures import ThreadPoolExecutor

from _x import finish, invoke, show

CASES = [
    ("bytes that are not text", b"\xff\xfe\xfd\x80"),
    ("an invalid byte before the object", b'\x80{"branch": "porto", "year": 2081, "previous": null}'),
    ("an invalid byte after the object", b'{"branch": "porto", "year": 2081, "previous": null}\xff'),
    ("an invalid byte inside the branch", b'{"branch": "por\xe9to", "year": 2081, "previous": null}'),
    ("an invalid byte inside the year", b'{"branch": "porto", "year": 20\xc081, "previous": null}'),
    ("an invalid byte inside the previous number", b'{"branch": "porto", "year": 2081, "previous": "OPO-2081-0003\xb3"}'),
    ("latin-1 text in the previous number", b'{"branch": "faro", "year": 2081, "previous": "FAO-2081-00\xb2\xb31"}'),
    ("a truncated UTF-8 sequence in the previous number", b'{"branch": "braga", "year": 2081, "previous": "BRG-2081-0001\xe2\x82"}'),
]

DECODING = {  # the two ways a Python program's standard input may be decoded
    "UTF-8 locale, strict decoding": {"PYTHONIOENCODING": "utf-8:strict"},
    "C locale, surrogate escapes": {"PYTHONIOENCODING": "utf-8:surrogateescape"},
}

runs = [(f"{label} ({mode})", payload, env) for mode, env in DECODING.items() for label, payload in CASES]
with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(lambda run: invoke(run[1], extra_env=run[2]), runs))

problems = []
for (label, _, _), (status, out) in zip(runs, results):
    if status != 2:
        extra = f", output {show(out)}" if out.strip() else ""
        problems.append(f"{label}: status {status}, expected 2 (undecodable input is an invalid request){extra}")

finish(problems, f"undecodable ok: {len(CASES)} requests with invalid UTF-8 refused under {len(DECODING)} decodings")
