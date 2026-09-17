# Study conventions (standing preferences — apply to ALL drivers/exercises)

Working note. Consult when writing or editing any experiment driver.

## Progress index on every pass (Chris, 2026-09-16)
Every running exercise must print a completion index on each per-row line, e.g. `[1/540] …`, `[2/540] …`,
so progress is visible at a glance. Implementation: compute `total` (the full planned matrix for this
invocation, counting only cases that will actually run) up front; keep an `idx` counter incremented once per
innermost unit of work (increment even on resume-skips so the shown position stays true); print `[idx/total]`
as the prefix of each row's stderr line. Applied to: active_verification.py, comprehension_portability.py,
portability_degraded.py (and all future drivers).

## Other established conventions (already in force)
- **Resumable CSV**: append + flush per row; skip rows already present (keyed on the run's identity tuple).
- **`--validate`**: an offline path (no API) that checks construction/scoring, runnable before any paid run.
- **Commands with `cd` + venv**: every command block handed to Chris starts with
  `cd ~/Documents/GitHub/ad-hoc-semantic-reconciliation/study && source .venv/bin/activate`.
- **Terminology**: user-facing text/figures/metrics say "resolved fraction", never "recall" (internal
  reconciliation metric key may stay `recall`). Comprehension metrics: meaning_score / abstention_rate /
  confabulation_rate — no "recall".
- **No repo references** to the assistant/vendor or reviewer names in committed content, commits, or figures.
- **Figures**: house style (NAVY/TEAL/ORANGE/…, SURFACE bg, dpi 160); no internal experiment labels (e.g.
  "E16") in report-bound figure titles.
- **Staging workflow**: stage files to the device clone for GitHub Desktop review; never commit/push.
