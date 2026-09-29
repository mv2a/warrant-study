"""H9 (S1-S4): the four scenarios in the intent, exactly as written, including the exit status."""

import subprocess

from _cmd import PATH, call, finish

SCENARIOS = [
    ("S1", {"password": "Bell-Book-77", "username": "rebel", "banned": ["books"]},
     {"ok": True, "violations": []}),
    ("S2", {"password": "maria.silva2024", "username": "MSILVA", "banned": ["2024"]},
     {"ok": False, "violations": ["banned", "username"]}),
    ("S3", {"password": "kim111", "username": "kim", "banned": ["11"]},
     {"ok": False, "violations": ["banned", "classes", "repeat", "too_short"]}),
]
problems = []
for sid, request, expected in SCENARIOS:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{sid}: expected status 0 and {expected}, got status {status} and {body!r}")

S4 = '{"password": "Harbor-Lamp-42", "username": "ana smith", "banned": []}'
try:
    done = subprocess.run([PATH], input=S4, capture_output=True, text=True, timeout=10)
    if done.returncode != 2 or done.stdout != "":
        problems.append(f"S4: expected status 2 and no output, got status {done.returncode} and {done.stdout[:60]!r}")
except subprocess.TimeoutExpired:
    problems.append("S4: timed out")

finish(problems, "scenarios ok: S1, S2, S3, S4")
