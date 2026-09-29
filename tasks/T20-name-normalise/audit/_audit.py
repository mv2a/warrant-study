"""Small helpers shared by the audit checks. The exact shape of output and of refusals is
C1's business and is checked in interface.py; the other checks look only at the part of
the answer their promise is about, so one broken promise does not fail every check."""

from _cmd import call


def ask(name):
    """Normalise one name. Returns (status, body)."""
    return call({"name": name})


def is_result(body):
    return isinstance(body, dict) and isinstance(body.get("display"), str) and isinstance(body.get("key"), str)


def is_refusal(status, body):
    """Refused (exit status 2) and not normalised."""
    return status == 2 and not is_result(body)


def display_of(name):
    """The display name, or a short description of what came back instead."""
    status, body = ask(name)
    if status == 0 and is_result(body):
        return body["display"], None
    return None, f"status {status}, {body!r}"


def key_of(name):
    status, body = ask(name)
    if status == 0 and is_result(body):
        return body["key"], None
    return None, f"status {status}, {body!r}"


def show(text, limit=60):
    """A short printable form of a possibly long or odd name."""
    text = ascii(text)
    return text if len(text) <= limit else text[: limit - 3] + "..."
