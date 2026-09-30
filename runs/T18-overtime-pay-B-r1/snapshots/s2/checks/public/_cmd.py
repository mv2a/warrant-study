"""Run the workspace's command the way the task's interface describes."""

import json
import os
import subprocess
import sys

COMMAND = "pay"
PATH = os.path.join(os.environ["WARRANT_WORKSPACE"], COMMAND)


def call(request=None, raw=None, timeout=10):
    """Send a request (or raw text) on stdin. Returns (exit status, parsed JSON output or None)."""
    if not os.access(PATH, os.X_OK):
        sys.exit(f"the workspace has no executable named pay")
    text = raw if raw is not None else json.dumps(request)
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, None
    output = done.stdout.strip()
    if not output:
        return done.returncode, None
    try:
        return done.returncode, json.loads(output)
    except json.JSONDecodeError:
        return done.returncode, output


def finish(problems, summary):
    if problems:
        shown = problems if len(problems) <= 12 else problems[:10] + [f"...and {len(problems) - 10} more"]
        print("\n".join(shown))
        sys.exit(1)
    print(summary)
