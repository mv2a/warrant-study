# Warrant study: visible-test-only versus evidence-gated agent development

Working repository for an exploratory evaluation of Warrant. The design is in
`EVALUATION_PLAN.md`. It replaced a larger design drafted for pre-registration in
`mv2a/warrant/docs/experiments/visible-vs-evidence-gated/PROTOCOL.md` (v0.1), which was
never frozen or registered and was not run.

All runs are complete, so the audit suites (X) are published with everything else.
Licence: Apache-2.0 (see `LICENSE`). To cite these materials, see `CITATION.cff`.

- `tasks/Txx-slug/`: the 20 study tasks, one per directory (see `TASK_SPEC.md`). Each has
  its intent, visible checks (V), hidden checks (H), audit checks (X), a reference and
  deliberately broken implementations.
- `harness/gates.py`: validity gates run on every task before any builder run.
- `harness/eval_mutants.py`: Part 1, the seeded-defect evaluation (no builder).
- `harness/run_study.py`: Part 2, the agent runs. `harness/analyse.py`: the Part 2 analysis.
- `results/`: Part 1 and Part 2 results.
- `review/`: the AI review record for each task (see `review/README.md`).
- `pilots/`: run records from the pilots on a non-study task (see `pilots/README.md`).

The tasks, checks and implementations were written by AI agents (Anthropic's Claude) at
the author's request and reviewed by an AI model, not by an independent person.
