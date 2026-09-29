# How to write one study task

Every task is a small command-line program, newly written for this study. It must not
copy a known kata, a textbook exercise or anything in the Warrant repository.

## Layout

```
tasks/T07-parking-fees/
  task.json            {"id": "T07", "slug": "parking-fees", "language": "python",
                        "command": "fee", "promises": ["G1", "G2", "C1", ...]}
  intent.md            the promises, in the format below
  warrant.toml         copy of harness/warrant.toml.template with the project name filled in
  checks/public/       V: visible checks, shown to the builder
    checks.toml
    _cmd.py            helper that calls the command (copy harness/_cmd.py.template)
    *.py               one script per check
  checks/holdout/      H: hidden checks, used only by Warrant's gate in conditions B and C
    checks.toml, _cmd.py, *.py
  audit/               X: audit checks, the ground truth for scoring; never run during development
    checks.toml, _cmd.py, *.py
  reference/<command>  a correct implementation, executable, Python 3 standard library only
  broken/<ID>/<command>  one deliberately wrong implementation per promise ID where feasible
  broken/README.md     which promises have no broken implementation, and why
```

## intent.md

Write it like `examples/pricing/intent.md` in the Warrant repository: a short title and
purpose, then 5 to 12 promises, each on its own line as `- ID: text`. Use `G` for goals,
`C` for constraints and `S` for concrete scenarios with exact inputs and outputs. Every
promise must be checkable by running the command. State the interface in one constraint:
the command's name, that it reads one JSON object on standard input and writes one JSON
object on standard output, the field names and types, the exit status for success (0) and
for a refused request (2).

## Checks

Every check file is a Python 3 script run with the checks folder as its working directory
and the environment variable `WARRANT_WORKSPACE` set to the folder holding the command.
It exits 0 when every case passes and 1 otherwise, printing at most a few short lines.
Each `checks.toml` entry has `id`, `covers` (promise IDs), `statement` (one plain
sentence saying exactly what is checked), `strength = "tested"` and `run`.

- **V (public)**: 2 to 4 checks. Cover the interface and the S scenarios, and at most a
  few other cases. Deliberately incomplete: a builder who satisfies only V can still break
  promises.
- **H (holdout)**: at least one check per promise, thorough: boundaries, rounding, invalid
  input, many generated cases with a fixed random seed.
- **X (audit)**: written independently of H, from intent.md alone. At least one check per
  promise, with different inputs and seeds from H.

## Validity gates (protocol §4)

`python3 harness/gates.py tasks/Txx-slug` must pass before the task is sealed:
the reference passes V, H and X; X covers every promise; each broken implementation fails
at least one X check that covers its promise; `warrant check` accepts the project.

## Honesty

No task may depend on network access, the clock, randomness without a fixed seed, or
files outside the workspace. Keep every task solvable by a competent engineer in under
an hour.
