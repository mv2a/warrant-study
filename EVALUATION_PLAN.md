# Evaluation plan (exploratory)

Written 29 September 2026, before any run on a study task. This replaces the larger
pre-registered design in Warrant's `docs/experiments/visible-vs-evidence-gated/PROTOCOL.md`
(v0.1 draft), which was never frozen or registered and is not being run as written. This
evaluation is exploratory: it is not pre-registered, it is small, and it will be reported
as such.

## Question

When a coding agent builds a small program against promises written in plain language,
does Warrant's gate (hidden checks, promise-level feedback, a deterministic merge gate)
ship fewer broken promises than accepting whatever passes the visible tests?

## Part 1: seeded defects (no agent)

`harness/eval_mutants.py` judges each task's reference implementation and every
deliberately broken implementation three ways: visible-only acceptance (all V checks
pass), Warrant (`warrant verify`, then `warrant gate merge`), and the independent audit
suite X (ground truth). Reported: how many defective implementations each rule accepts,
whether any reference is rejected, and Warrant's verification time.

Caveat reported with it: the same AI agent wrote each task's hidden checks (H) and planted
its broken implementations; a separate AI agent wrote X. Part 1 is a sanity check on the
suites, not an estimate of how often hidden checks catch defects an independent builder
makes. Part 2 is the evidence for that.

## Part 2: agent runs

- Tasks: the 20 tasks in `tasks/` (T01 to T20), all gated by `harness/gates.py`.
- Conditions: A (visible-only acceptance; feedback is the visible results) and B (Warrant;
  feedback adds the IDs of promises the hidden checks found unmet). Condition C and
  replicates are dropped to keep the run short. One run per task and condition: 40 runs,
  order randomised per task, `run_study.py plan --seed 20260929 --conditions A B --replicates 1`.
- Builder: Claude Code 2.1.252 driving gpt-oss:20b (Ollama tag digest 17052f91a42e,
  num_ctx 65536, temperature 1) on the verification host's GPU, with the configuration in
  `harness/run_study.py` at the commit that starts the runs. Prompt identical in A and B.
- Limits per run: 5 submissions, 45 minutes, 200,000 output tokens.
- Scored after the run with X against the accepted candidate (or the last submission).

Measures per run: accepted; escaped defects (promises X finds broken in the accepted
candidate, 0 if none accepted); false pass; correct delivery; submissions; wall-clock
minutes; input and output tokens.

Reporting: per-task table and totals by condition. Paired comparisons of false pass and
correct delivery with exact McNemar tests, and of escaped defects with a Wilcoxon
signed-rank test, all labelled exploratory; with 20 pairs only large effects can show.
Results are reported whatever their direction.

## Disclosed with the results

- The tasks, checks, reference and broken implementations were written by AI agents
  (Anthropic's Claude) at the author's request, and reviewed by an AI model (Claude
  Sonnet), not by an independent person. Review records are in `review/`.
- One builder configuration, a 20B-parameter open-weights model; results may not transfer
  to stronger models.
- The pilot history on a non-study task (T00-pricing) and every change it caused: model
  replaced (qwen3:14b failed every visible check), a read-first line added to the prompt,
  the token cap moved to output tokens, the context window raised to 64k with Claude Code
  told its size, timed-out containers killed, tokens counted from session logs. Pilot runs
  are excluded from the results.
- The author designed Warrant and has an interest in its looking effective.
