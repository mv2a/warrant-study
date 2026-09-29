# Pilot runs (non-study task T00-pricing, excluded from the results)

T00-pricing is Warrant's `examples/pricing` converted to the task format. Each folder holds
the run records (`run.json`) and, for the final pilot, the builder's session logs.

- `pilot1-qwen3-14b/`: qwen3:14b, 32k window, 200k total-token cap. The builder failed
  every visible check in all three conditions. Model replaced.
- `pilot2-gptoss-32k-total-token-cap/`: gpt-oss:20b, 32k window, 1M total-token cap,
  read-first prompt line. B and C stopped at the token cap (input tokens re-sent every call).
- `pilot2b-gptoss-32k-output-token-cap/`: B and C re-run with the output-token cap. The
  32k window overflowed, a timed-out builder container kept running, and token counts were
  lost for a timed-out turn. The A record is a copy of pilot 2's.
- `pilot3-gptoss-64k-final/`: the final configuration (64k window, Claude Code told a
  60,000-token window, containers killed on timeout, tokens from session logs). All three
  conditions accepted with no promise broken; longest prompts 24,610 (A), 36,202 (B) and
  26,973 (C) input tokens.
