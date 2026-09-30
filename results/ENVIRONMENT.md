# How the results files were produced

- `results/seeded_defects.json`: `python3 harness/eval_mutants.py --jobs 6`, run on the
  author's Mac (macOS, Python 3.13.3), without containers, with the vendored Warrant v0.1.1.
- `results/agent_runs.json`: `python3 harness/analyse.py runs`, run on the author's Mac
  (Python 3.13.3, scipy 1.16.3, numpy 2.4.0) on the run records copied from the verification
  host. Re-running it reproduces the file byte for byte.
- The agent runs themselves ran on the verification host (Ubuntu 24.04 under WSL2, Docker
  29.5.2, Ollama 0.24.0, NVIDIA RTX 5070 Ti 16 GB), one at a time, between
  2026-09-29T17:56:30Z and 2026-09-30T07:09:45Z.
