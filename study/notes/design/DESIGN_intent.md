# Intent reconciliation: refining a quantitative demand, verified by satisfaction — a study design

> **Status: design / planned.** The second operational setting of the programme. It reuses the
> framework, harness architecture, cognition-spectrum treatment, and metrics discipline of
> [REPORT.md](../../reports/REPORT_1of4_configuration.md), and the instance oracle of
> [REPORT_instance_disambiguation.md](../studies/instance-disambiguation.md) for endpoint
> co-reference. Grounded in the IRTF NMRG Internet-Draft *Dynamic Network-as-a-Service
> Life-Cycle Automation Using End-to-End Agent Negotiation*
> (draft-janz-nmrg-naas-agentic-negotiation, Janz, Rahimi and Yu), whose consumer
> Policy-and-Wallet agent, agent-to-agent negotiation, and closed-loop lifecycle
> renegotiation sharpen the negotiation and pragmatics of this setting.

## Summary

The first setting reconciled two structural models of one network — an equivalence between
schema terms. This setting reconciles a **declarative intent against a concrete realisation**,
and the reconciliation is a **refinement, not an equivalence**: a bound such as *bandwidth ≥ 8
Gbit/s* is not equal to an ODU2, it is *satisfied by* one, and the provider chooses among many
realisations that would serve. Four things follow that the first setting did not force, and each
is a deliberate object of this study.

First, **verification is by satisfaction, not round-trip**: the chosen realisation is checked
against every stated bound, because a lossy, under-determined refinement cannot be checked by
returning the original demand. This is the "satisfaction" verification mode the verification
study named and deferred; here it is primary.

Second, where a component cannot be satisfied outright the provider returns a **best-achievable
offer** — an alternative realisation, possibly degraded on some bound and carrying its own cost —
and an **intent judge** accepts it against declared **priorities**, or rejects. This is a
two-sided negotiation reached, in the fully-cognitive case, with no human in the loop. This
negotiation is where the cognition spectrum bites hardest.

Third, the setting has **two directions that are not inverses**: *refine-down* (intent → a
realisation that satisfies it, one-to-many, carrying the provider's choice) and *assure-up*
(operational state → **fulfilment**: met, at-risk margin, or breach). And assure-up is not a
single classification but a **lifecycle loop**: a change on either side re-triggers the
refinement-and-satisfaction reconciliation, which recurs across the life of the service — the
**consumer initiates when it needs something different**, the **provider initiates when it can no
longer satisfy an aspect it had been delivering under the agreement**. **The cause behind either
trigger is a driver, not an object of study**; what the study measures is the reconciliation the
trigger sets off, whichever side it comes from. (The draft's scarcity-driven repricing is
one such provider-side driver among many, and the study does not privilege it.)

Fourth, the consumer's acceptance policy is a **movable, portable artefact** — a spending wallet
and decision policy the consumer carries (a verifiable-credential wallet in the draft)
that codifies its **priorities, its affordability floor, and its per-flow-class rules**, and lets
the consumer agent auto-accept or reject offers by pre-placed judgement. This matters for
the spectrum directly: a codified portable policy is neither a live reasoner nor a mute
description but a **pre-placed decision surface**, so decisions the consumer pre-authorised close
autonomously even when no consumer agent reasons in the moment. It is a concrete mechanism for
*pushing the hand-off boundary* the programme's central insight identifies — pre-placing consumer
cognition so more of the reconciliation completes before hand-off to a live person.

Per the agreed scope, this study takes the **full** setting — refine-down, the best-achievable
negotiation, and the assure-up lifecycle loop — exercises **two thin-reference variants as
arms** (unit/value-set and invariant), and makes the **pragmatic dimension a studied axis** (realm,
authority, priorities, state), carried concretely by the movable policy, which the demo shows
carries this case and which the main report deferred.

**A note on emphasis.** As in the first setting, this study is as much about **explaining and
illustrating the concept in action** — and showing **what is new or incremental against the first
case** — as it is about deep findings or exhaustive proof. Refinement rather than equivalence,
verification by satisfaction, the two non-inverse directions, the best-achievable negotiation, the
movable policy, the pre-placed-policy point on the cognition spectrum, and the **multi-hop
lifecycle** are all new here. The design therefore foregrounds a small number of richly worked,
legible scenarios — a **multi-hop lifecycle set-piece** among them, in the spirit of the instance
study's worked transcript — over a large factorial, and reports the cognition-spectrum effects as
illustration of the mechanism rather than as the whole point. The measured cross-product is kept
modest on purpose; the worked scenarios do the explaining.

## 1. The setting, and why it differs

Agent **O** is a TM Forum Intent-interface OSS (TMF921 / IG 1253): declarative expectations with
quantitative bounds — bandwidth ≥, latency ≤, availability ≥, protection required — plus a
declared **priority ordering** over them and a **flow class** (order execution, market data, risk
sync, bulk) that governs whether a service holds its SLA or steps aside to save money under
renegotiation. Agent **N** speaks an IETF Layer-1 connectivity service
(draft-ietf-ccamp-l1csm-yang + teas service-mapping) over the OTN/optical network of the first
case: discrete client signals (ODU*k*), routes, wavelengths, protection schemes, and the cost of a
realisation. The two differ in **nature** (a predicate versus a value), in **scope** (consumer
realm versus provider realm), and in **abstraction** (*what* to deliver versus *how* it is
delivered). Neither merges the other's schema; both are competent, interrogable agents that work
out the mapping between themselves. The reconciliation target is the mapping, and it is a
refinement: each expectation is *satisfied by*, not equal to, a construct on the other side, and
the provider chooses among satisfying realisations — so when a component cannot be met outright the
"best-achievable offer" is an alternative realisation, weighed on its bounds and its cost, not a
single scalar.

## 2. The task

Four components, run as phases (§8):

- **Refine-down + satisfaction.** For each expectation, derive a concrete realisation and check
  by **satisfaction** — the realisation meets the bound. Refinement is one-to-many; the provider
  picks in its realm. Scored: does the chosen realisation satisfy *every* bound (against a
  validated satisfaction oracle), and is it a valid member of the realisation catalogue (not
  fabricated).
- **Feasibility and the judge (the negotiation).** Where the bounds cannot all be met at once, the
  network computes feasibility and returns a **best-achievable offer** — an alternative
  realisation, possibly degraded on some bound and carrying its own cost; the intent judge
  evaluates it against the acceptance criteria carried in the **movable policy** — the declared
  **priorities**, the **affordability floor**, and the **flow-class rule** — and **accepts or
  rejects**. Scored: the correct best-achievable offer, and the correct accept/reject decision
  *given the policy in force*. Deterministic guardrails (affordability, SLA floor) bound the judge;
  the cognition is spent in the grey area of weighing a degraded-but-cheaper against a
  costlier-but-fuller offer.
- **Endpoint co-reference.** Which delivery points and access points are the same entity, from
  evidence (service-order key → UNI id → location). This is instance-level co-reference and
  reuses the machinery of the instance study; it is a supporting step, scored with the instance
  metrics, not the headline.
- **Assure-up (the fulfilment lifecycle loop).** Operational state flows up; map each measured
  value to the fulfilment of its expectation — **met / at-risk margin / breach** — by the same
  satisfaction predicate on live data. A change on either side then **re-enters the negotiation** —
  the **consumer** initiates when it needs something different, the **provider** when it can no
  longer satisfy an aspect it had been delivering under the agreement: a best-achievable offer is
  put, the movable policy decides (accept, or refer to the consumer), and a later change may restore
  an earlier realisation. This runs as a **multi-hop lifecycle** across the life of a service —
  several such hops in sequence, the trigger alternating origin (a consumer-initiated change at one
  hop, a provider-initiated one at another), each hop a fresh reconciliation event carrying state
  forward from the last. The cause behind any trigger is not modelled or scored; the reconciliation
  it sets off is. Scored: fulfilment-status accuracy, the correctness of each lifecycle decision
  against the policy, and the classification of a breach as **self-remediable** (an alternative the
  policy can auto-accept) or **needs a consumer decision**.

The two directional mappings (refine-down, assure-up) are **not inverses** and are scored
separately; the reconciliation is where the cognition is spent, runtime then applies the mappings
with no inference per message.

## 3. The cognition spectrum, for intent

The negotiation makes the spectrum bite on a new quantity. Best-achievable acceptance needs the
**provider live** to compute feasibility and put an offer, and consumer judgement to weigh it —
but consumer judgement can be **live** *or* **pre-placed in the movable policy**, and that
distinction is exactly what this setting adds to the spectrum:

- **both-cognitive** — provider computes feasibility and offers; a live consumer judge (or its
  movable policy) accepts a degraded offer or rejects; the refinement completes autonomously,
  graceful degradation and lifecycle renegotiation included.
- **one-inert** — one side is a static description. The subtlety the wallet introduces: a
  consumer that is not live *as a reasoner* may still carry a **codified movable policy**, a
  pre-placed decision surface that closes the decisions it was authorised for and refers only the
  rest. So "one-inert" splits into *mute description* (refers almost everything) and *pre-placed
  policy* (closes the pre-authorised envelope, refers the residual) — a direct measurement of how
  far pre-placed cognition pushes the hand-off boundary. On the provider side, an inert capability
  catalogue that cannot compute a fresh best-achievable offer forces the live side to reason about
  what it would offer.
- **both-inert** — a third party refines and checks satisfaction from static descriptions and can
  only *propose* a realisation and *flag* infeasibility; every acceptance decision beyond a
  fixed policy's envelope is referred to the consumer.

So the residual here is **negotiated satisfaction the agents cannot close** — the same
resolvability-shortfall shape as the first two studies, now on the best-achievable
negotiation and the lifecycle loop rather than on co-reference. The prediction is that
outright-satisfiable intents resolve across much of the spectrum; the degraded-acceptance
cases collapse toward the residual as a side goes inert — but a movable policy **recovers the part
of that residual it was pre-authorised to decide**, and no budget of effort recovers the rest.

## 4. The reference: two arms

The demo's reference does something specific and worth measuring: it **separates
expectation-kind entries (a bound: ≥, ≤) from realisation-kind entries (a discrete value or
resource)**, connected by a *refinement* relation rather than by equality, and so pre-empts the
**nature false cognate** — an expectation and a metric that share a word, so "latency ≤ 5 ms" is
never mistaken for a measured latency. The reference here "does not just save conversation — it
saves *verification*." Two variants are run as arms, plus a no-reference control:

- **unit / value-set** — pins the quantitative semantics: what a unit means on each side, the
  discrete value hierarchies (ODU rates, protection classes, the B/L/A grade axes), and the
  expectation-vs-realisation kind separation. Guards the unit-scale and nature traps directly.
- **invariant** — publishes the invariants a realisation must preserve for satisfaction to hold,
  the anchor a satisfaction check evaluates against when a side is inert.

The with/without and unit-versus-invariant contrasts, across the spectrum and model ladder, are
how each variant's contribution is read.

## 5. Pragmatics as a studied axis — carried by the movable policy

The demo is explicit that **pragmatics carry this case**: *realm* (consumer expectation versus
provider realisation — who decides), *state* (intended versus operational — the assurance loop),
and *authority* (who judges an offer). This study makes them a factor rather than a fixed backdrop,
and the NMRG draft gives the factor a concrete carrier — the **movable consumer policy held in the
wallet**:

- **priorities / affordability / flow-class (the movable policy)** — the same infeasible or degraded
  intent is run under different **portable policies**: different priority orderings, different
  affordability floors, and different flow-class rules (an order-execution flow holds its SLA at
  almost any price; a bulk flow steps aside to save money). The correct accept/reject *changes with
  the policy in force*. A reconciliation that ignores which priority ranks higher, what the wallet
  can afford, or what the flow class dictates gets the acceptance decision wrong. This is
  the first direct measurement of the pragmatic component the main report held fixed — and it is
  measured by *varying a portable artefact*, not by re-authoring the agents.
- **authority / pre-placement** — the judging authority is placed differently across runs
  (consumer-side live judge, the pre-placed movable policy, a provider-side or shared-reference
  rule), letting us read how far a pre-placed policy substitutes for live consumer cognition and
  where it must hand off.
- **state (intended vs operational)** — the same value means fulfilment or breach depending on
  whether it is read as the intended target or the operational reading; the assure-up loop must
  keep the two straight (a pragmatic distinction, not a lexical one).

## 6. The case (seeded, validated oracle)

A set of **intents** crossed with a **realisation catalogue** over the first case's OTN/optical
network, seeded so each mechanism is exercised and each trap is provable. The network offers each
destination by more than one realisation (e.g. a **direct** or a **diverse/protected** path), each
with its own bounds and cost; each intent carries a **flow class**:

- **fully-satisfiable** intents — all bounds met outright by some affordable catalogue realisation.
- **degraded-accept** intents — no realisation meets every bound at once; a best-achievable
  alternative exists and is *accepted* under the movable policy (its priorities, affordability
  floor, and flow-class rule).
- **degraded-reject / unsatisfiable** intents — the best-achievable offer violates a
  higher-priority bound or the affordability floor and must be *rejected* and referred onward.
- **nature-false-cognate** trap — an expectation and a metric sharing a word (a *latency ≤*
  expectation versus a measured *latency* value); must not be conflated. The reference guards it.
- **unit-scale** trap — a bound stated in units a naive agent mis-scales (Gbit/s vs the ODU
  payload/line-rate distinction the draft flags).
- **assure-up lifecycle** — seeded **multi-hop** renegotiation trajectories running across the life
  of a service, alternating trigger origin hop by hop: a consumer-initiated change (it now needs
  something different) at one, a provider-initiated change (it can no longer satisfy an aspect it
  had been delivering) at another; at each hop a best-achievable offer is available, the policy
  decides, and a later hop may restore an earlier realisation. State carries forward across hops.
  At least one trajectory is authored as a **worked lifecycle set-piece** — a full, legible
  transcript of the service renegotiating itself across its life — to be the report's illustration
  of the concept in action. The cause behind each trigger is left unmodelled. Hops seeded to land
  as met / at-risk / self-remediable breach / consumer-decision breach.
- **policy variants** — each degraded or infeasible intent authored with two or more portable
  policies (priority ordering / affordability / flow-class / authority placement), so the correct
  decision varies with the movable policy.

A deterministic **satisfaction–feasibility–policy–fulfilment oracle** derives the gold — the
satisfying realisations, the correct best-achievable offer and accept/reject per policy, the
co-reference truth, and the fulfilment/remediation verdicts across the lifecycle — and validates it
(refusing, for instance, a "degraded-accept" case whose offer actually violates a higher-priority
bound or the affordability floor), so the gold cannot drift.

## 7. Metrics

Correctness-first, per phase:

- **Satisfaction correctness** — of the bounds, the fraction the chosen realisation actually
  satisfies (against the oracle); and **refinement validity** — the realisation is a real
  catalogue member.
- **Negotiation correctness** — the best-achievable offer matches the oracle's, and the
  accept/reject decision matches the policy-correct verdict; **surviving nature/unit cognates** —
  expectation/metric or unit mismatches wrongly asserted.
- **Lifecycle-decision accuracy** — across the assure-up loop (breach detection, offer
  acceptance, restore), each decision correct against the policy; and **remediation-class
  accuracy** — self-remediable (auto-accept within the policy envelope) vs consumer-decision.
- **Policy-recovery on the spectrum** — of the decisions a mute description refers onward, the
  fraction a **pre-placed movable policy** closes autonomously (how far pre-placement pushes the
  hand-off boundary), and the residual it still refers.
- **Residual by cause and placement** — acceptance and satisfaction decisions referred
  onward, broken out, as the measure of the shortfall down the spectrum.
- **Reference effect** — the with/without and unit-vs-invariant deltas on the above.
- **Pragmatic sensitivity** — does the decision track the movable policy in force (it should), and
  does a reference/agent that ignores the policy get it wrong (the failure mode).
- **Effort** — reasoning tokens, and a new currency, **negotiation rounds** (offer/counter turns
  to reach a decision).

## 8. The run plan: one command, staged phases, launch-and-leave

A single `intent_study.py --stage all` runs the phases in sequence, each writing its own
**segmented CSV** and printing a **phase banner with live progress**, checkpointed and resumable:

```
=== Phase 1/4 · refine-down + satisfaction ===              [ 48/108 ]
=== Phase 2/4 · feasibility & the judge (negotiation) ===   [ 12/144 ]
=== Phase 3/4 · endpoint co-reference ===                   [  6/54  ]
=== Phase 4/4 · assure-up (fulfilment lifecycle) ===        [  9/108 ]
```

Each phase crosses the **cognition spectrum** (3, with one-inert split into mute-description vs
pre-placed-policy where it applies) × **reference arm** (none / unit / invariant) × the relevant
**policy variants** × **model ladder** (`gpt-5.6-sol`, `gpt-5-mini`, `gpt-5-nano`) × trials, over
the seeded case. The negotiation and lifecycle phases run a bounded tool-use loop (feasibility
oracle + judge), as in the instance study, so the run is sized and the weak model is given
a generous-but-bounded budget from the start to keep it tractable; trials are chosen so the whole
thing is a launch-and-leave of a few hours, not a nano marathon. Consistent with the
illustration-first emphasis, phases 1–3 run the modest measured cross-product, while **phase 4 runs
a few crafted multi-hop lifecycle scenarios end to end with full transcripts retained** — worked
set-pieces, not a large trial count. The exact per-phase run counts and total are fixed when the
case is built and reported back before launch.

## 9. Pre-registered predictions

1. **Satisfaction holds under full cognition; degraded-acceptance is where the spectrum
   bites.** Outright-satisfiable intents refine and verify across much of the spectrum; the
   best-achievable negotiation completes only with the provider live and consumer judgement
   present (live or pre-placed), and collapses toward the residual as a side goes inert — no budget
   of effort recovers a decision that needs the mute side's authority.
2. **A movable policy recovers part of the residual by pre-placement.** Where a mute consumer
   description refers a decision onward, a pre-placed wallet policy closes the pre-authorised
   envelope autonomously and refers only the rest — a measurable push of the hand-off boundary, and
   a concrete instance of the programme's central insight (pre-placed cognition completing more
   before hand-off).
3. **The reference saves verification, not just conversation**, and its correctness value
   concentrates at the weak end and the inert placements — the unit/value-set arm pre-empts the
   nature and unit traps a weak or inert agent otherwise takes; the invariant arm gives the
   satisfaction check something to evaluate against when a side cannot be asked.
4. **The decision tracks the movable policy.** The correct accept/reject changes with the priority
   ordering, affordability floor, and flow-class in force; a capable agent follows it, and the
   characteristic weak failure is deciding by the bound alone, ignoring the policy.
5. **Assure-up is robust in status but capability-gated in the lifecycle decision** — met/at-risk/
   breach is largely read correctly, while the offer-acceptance and self-remediable-vs-consumer
   decisions (pragmatic, policy-laden judgements) degrade with capability and as cognition recedes.
6. **Capability gradient throughout**, as in the first setting: the strong agent negotiates
   and defers cleanly; weaker agents mis-scale units, mis-weigh priorities, misjudge
   affordability, and are confident when wrong.

## 10. What it reuses, and what must be built

Reused: the cognition-spectrum treatment, the model ladder, the correctness-first discipline, the
bounded tool-use loop and its checkpoint/resume, the instance oracle (endpoint co-reference), and
the reference-arm and figure/PDF tooling.

To build:
- the **intent case** — intents (with priority orderings and flow classes), a **realisation
  catalogue** (each realisation with its bounds and cost), portable-policy variants, **multi-hop
  assure-up lifecycle trajectories** (state carried across hops, trigger origin alternating, at
  least one authored as the worked set-piece), the two references — over the first case's network,
  with a build-and-derive script and a validating oracle (satisfaction, feasibility, policy judge,
  fulfilment, and per-hop gold across a trajectory);
- the **intent agent** — a bounded tool-use loop with a **feasibility oracle** (does a
  realisation satisfy the bounds; what is the best achievable) and a **judge**
  step that evaluates an offer against the **movable policy**, emitting the refine-down
  realisation, the negotiated decision, and the assure-up lifecycle verdicts, with a legible
  transcript;
- the **movable-policy artefact** — a small, portable, machine-checkable policy (priorities,
  affordability floor, flow-class rule, authority placement) that the judge consults, and that the
  spectrum's "pre-placed policy" arm exercises;
- the **satisfaction / feasibility / fulfilment scorers**, the pragmatic-sensitivity
  metric, and the policy-recovery metric;
- `intent_study.py` — the single-command staged driver of §8, with segmented per-phase CSVs, the
  phase banner and progress display, and resume;
- offline tests (no API) of the oracle and the loop, as for the instance study, before any spend.
