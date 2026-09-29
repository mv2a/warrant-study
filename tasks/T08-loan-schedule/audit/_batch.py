"""Run many requests against the workspace's command at once, and read refusals exactly."""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from _cmd import COMMAND, PATH, call


def call_all(requests):
    """call() for every request, in parallel; results come back in the same order."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(call, requests))


def raw(text, timeout=10):
    """Send text on stdin. Returns (exit status, stdout exactly as written)."""
    if not os.access(PATH, os.X_OK):
        sys.exit(f"the workspace has no executable named {COMMAND}")
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, None
    return done.returncode, done.stdout


def raw_all(texts):
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(raw, texts))


def dumps(request):
    return request if isinstance(request, str) else json.dumps(request)
