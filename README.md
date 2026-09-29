# Warrant study: visible-test-only versus evidence-gated agent development

Private working repository for the pre-registered study in
`mv2a/warrant/docs/experiments/visible-vs-evidence-gated/PROTOCOL.md`.
Nothing here is published until all runs are complete: the audit suites (X) stay sealed
until then (protocol §4, §10).

- `tasks/Txx-slug/`: one task per directory (see `TASK_SPEC.md`).
- `harness/gates.py`: the validity gates of protocol §4, run before any builder run.
- `harness/`: the run harness (protocol §6), added before the freeze.
- `runs/`, `analysis/`: filled only after the protocol is frozen and deposited.
