# Working notes for the instance report (interpretive threads to carry into the write-up)

Not the report — a running capture of framings and observations to weave in, per the
standing intent that this study *demonstrates and explains the collective use of the
means* across the cognition spectrum, as much as it measures them.

## Threads to develop

- **Probe effort as a signature of the mechanisms at work.** Heavy interrogation at
  both_cognitive (sol Stage-1 mean ~16.6 interrogate calls, ~2.6 provisions) is not
  overhead — it is the agent *working the oracle* to pin exactly the hard cases the case
  was built around: the structurally-symmetric nodes and the keyless OMS pair (interrogation)
  and the service correspondences incl. the svc-100 name trap (virtual provision). The
  interrogation count is therefore a readout of where the static evidence ran out and live
  cognition took over. Report the probe counts alongside correctness, not as a cost line but
  as evidence of the division of labour between static evidence and live cognition.

- **The worked demonstration (a transcript, shown).** The both_cognitive smoke transcript is
  the clean set-piece: interrogate all four symmetric-node serials → match by serial;
  interrogate the four OMS fibre-ids → match by fibre-id; virtual_provision to *confirm* the
  two real services and to *refute* svc-100 on diverging capacity/endpoints; leave the three
  native gaps (incl. the R1 name-collision device) residual. Precision 1.0, recall 1.0,
  experiment-only recall 1.0, zero surviving false cognates. Use this as the report's worked
  example — the means in concert — before the aggregate tables.

- **The resolvability collapse, quantified.** experiment-only recall 1.00 (both_cognitive) →
  ~0.15 (one_inert) → ~0.18 (both_inert) for sol; recall 0.98 → 0.65 → 0.64; precision ~1.0
  and surviving FC 0 throughout. The experiment-only cases are exactly the ones that fall into
  the residual as the oracle is lost — the *structural* shortfall, sharper than the schema
  study's. The one_inert case is the subtle one: the live side can be interrogated but the
  inert side cannot, so the symmetric/keyless pairs cannot be *compared* and are correctly
  deferred (interrogation on the live side alone doesn't close them).

- **Precision holds where cognition recedes — deferral, not error.** The weak-cognition
  placements lose *recall* (deferred experiment-only cases) but keep precision ~1.0 and take
  no false cognates: the agent refers onward rather than guessing. This is the instance-level
  echo of the recall-is-deferral-not-failure point from the pre-lift report, and it is where
  the residual-closure-by-placement framing lands: at both_cognitive the residual is closed by
  more cognition (more probing); as cognition recedes the same residual can only be closed by
  human effort or external verification.

- **Confirm vs propose, mechanically.** provision-confirmed pairs are the mechanically
  *confirmed* correspondences; interrogation-resolved ones are evidence-backed proposals. Keep
  the distinction visible when reading recall (a confirmed co-reference is asserted; an
  unconfirmed one is deferral).

- **Capability interaction (pending mini/nano).** Watch whether the weak models over-probe
  (many interrogations, little resolution), mis-merge (surviving instance FCs > 0), or
  mis-calibrate confidence (confident on wrong merges). The sol run is clean; the ladder is
  where the capability story will come from.

## Draft passage — the budget sweep (Stage 3), the study's sharpest result (Chris: "exactly the kind of thing the report needs to describe")

Keep close to verbatim in the report:

> That contrast is exactly the sharper claim the study was built to make. At both_cognitive,
> "resolution complete in principle with full cognition" becomes a *measured curve*: give the
> agent more probes and the experiment-only cases resolve monotonically (0.00 → 0.38 → 1.00),
> residual → 0. At one_inert, the same unbounded budget barely moves it (→ 0.08) — because you
> can interrogate the live side but the inert side can't answer, so the symmetric/keyless pairs
> can't be *compared* at any budget. The shortfall stops being a matter of effort and becomes
> structural the moment a side goes inert. Precision stays 1.0 and surviving false cognates 0
> across every cell — it never buys resolution with error.

Supporting numbers (sol Stage 3): both_cognitive eo-recall by budget 0/3/unbounded = 0.00/0.38/
1.00 (resid_eo 4.0/2.5/0.0); one_inert = 0.00/0.00/0.08 (resid_eo 4.0/4.0/3.7). Frame the two
tables side by side: the residual is *budget-limited* at both_cognitive (drives to zero) and
*structurally* limited at one_inert (no budget helps). This is the money figure — plot eo-recall
vs budget, two lines (both_cognitive climbing to 1.0, one_inert flat near 0).

## Metric-reading reminders (for consistency with the other reports)

- recall < 1.0 is deferral to the residual, not error (define instance precision/recall/
  surviving-instance-FC/residual, as we did in the other reports).
- residual_total is a raw individual count (both members of each deferred pair + native gaps);
  the meaningful cuts are residual_experiment_only (deferred correspondences) and
  residual_native (gaps). Lead with those, not residual_total.
- effort currencies unique to this study: interrogation count and manipulation (provision)
  count, reported alongside reasoning tokens.
