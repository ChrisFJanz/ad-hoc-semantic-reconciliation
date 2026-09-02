# Instance disambiguation across the cognition spectrum — a study design

> **Status: design / planned.** No experiments have been run. This is a plan, shelved
> alongside the completed studies so the next phase is ready to build. It reuses the
> framework, harness architecture, and metrics of [REPORT.md](../../reports/REPORT_1of4_configuration.md); read that
> first for the semantic-model definition, the cognition spectrum, and the resolvability
> argument this design leans on. It is deliberately scoped to exercise **all** of the
> instance-level mechanisms the MAGIC paper conceives — not only co-reference from static
> evidence, but interrogation, the **virtual operation on the knowledge graph** checked
> against semantic invariants, confidence-held proposals corroborated by regeneration, and
> the **invariant** and **instance** reference variants — so that the demonstration matches
> the framework rather than a subset of it.

## Summary

The schema-term studies ([REPORT.md](../../reports/REPORT_1of4_configuration.md), [REPORT_reference_anatomy.md](../studies/reference-anatomy.md))
reconcile the *vocabulary* of two models — which type denotes the same type as which. This
design turns to the **instance level**: co-reference of *individuals* across two populated
graphs — is this ROADM the same device as that te-node, this ODU2 service the same as that
te-tunnel. It is a separate exercise that *follows* schema alignment (once the types are
aligned, one can compare like with like) and runs on a different path: **entity resolution
over the data**, from keys, attributes, and topology, rather than meaning-comprehension over
the vocabulary.

Two things make it worth its own study, and both trace directly to the MAGIC paper. First, the
cognition spectrum bites **harder** here: for the genuinely hard individuals — two structurally
identical devices, or an individual with no shared key — the decisive evidence exists *only* by
acting on the live system, so that whole class of evidence is gated by live cognition, and the
residual-as-shortfall pattern becomes structural rather than incidental. Second, the paper's
central verification mechanism is itself an instance-level act: a proposed correspondence is
*exercised* by a **virtual operation on the knowledge graph** — provision a service through the
candidate and confirm the resulting objects *in place* against a fixed set of **semantic
invariants** (endpoint identity, connectivity, capacity, layer relationships, switching
constraints, multiplexing structure), not by byte equality. Instance disambiguation is therefore
both the cleanest test of the across-the-spectrum thesis and the natural home for the
correctness-by-construction claim. This design covers the full mechanism set the paper names:
co-reference from the static evidence hierarchy (key → attributes → topology), **interrogation**
of a live side, the **virtual manipulation** as a first-class invariant-checked verification
stage, **confidence-held proposals corroborated by regenerating native records**, the
confirm-versus-propose split that governs how resolved fraction is read, and the **instance** and
**invariant** reference variants of the reference family.

## 1. Motivation and relation to the schema studies

The main study established two things: that cognitive agents reconcile divergent models ad
hoc, and that the *placement* of cognition governs what reconciliation can resolve — complete
in principle between two fully-cognitive agents, with a growing residual (the shortfall from
full cognition's reach) as cognition recedes. Those results are about the schema. Real
interoperation also requires aligning the **individuals** the schemas classify, and that is a
different problem with a different failure surface. This study asks the same governing
question — how does the placement of cognition change what can be resolved, and what evidence
carries the weight — but for instance co-reference, and it brings the paper's verification
mechanism into the measurement rather than leaving it implicit.

## 2. The task

Given two populated graphs of one network and an **already-reconciled schema**, an agent must:

- decide which individual in graph A is the same real-world entity as which individual in B;
- hold each decision with a **confidence**, and corroborate it — by fit, by regenerating a
  native record, and, where cognition allows, by a virtual manipulation (§6);
- leave A-only and B-only individuals as **residual** (native gaps);
- **never merge two distinct individuals** (an instance false cognate);
- and, where identity cannot be settled or confirmed from the evidence available, refer the
  individual onward as residual rather than guess.

Scored against a validated **gold instance alignment**, derived from the case by construction
so it cannot drift, exactly as the schema gold is. The gold additionally encodes, per
individual and per candidate service, the **semantic invariants** a virtual manipulation is
expected to confirm (§4), and flags the **experiment-only** subset (§4).

## 3. Why the cognition spectrum bites harder here

In schema reconciliation an inert side still exposes its whole structure and data statically,
so the live agent can usually reconstruct a type's meaning from what is on the page; the
virtual experiment is a confirmation, not the only route. Instance co-reference is different.
Some individuals are distinguishable *only* by an active query or experiment against the live
system — "what is the serial of the device at this port?", or *provision through candidate
correspondence X and observe which real device lights up*. That class of evidence is available
only under live cognition. Consequently:

- **both-cognitive** — resolution is complete in principle: any individual's identity can be
  confirmed by interrogation or a decisive virtual manipulation, so the residual can in
  principle reach zero.
- **one-inert** — the live side can still be interrogated and manipulated; the inert side is a
  static snapshot. Some individuals on the inert side that are separable only by experiment
  become unresolvable — unless a published reference supplies what the side cannot volunteer.
- **both-inert** — no probing or manipulation at all; a third party co-refers from static
  evidence only and can only *propose* candidates, leaving every experiment-only individual
  residual.

The shortfall from full cognition is thus not only present but **structural and unavoidable**
for a definable subset of individuals — a sharper instance of the same law the schema study
measured, and the reason the experiment-only subset is broken out in the gold and the metrics.

## 4. Case construction (the seeded hard instance case)

A purpose-built populated transport network — a fresh case, in the same domain and over the
**already-reconciled TAPI/TEAS schema types** of the first case, so the "schema already
reconciled" premise holds and continuity with the programme's setting is preserved, while the
A-box topology is engineered to plant clean, *provable* traps. The individuals are deliberately
booby-trapped so that different evidence types are each made to matter:

- **Merge targets** — the same real device under different local ids/names in the two graphs;
  must be merged. Separable by attributes or topology, not by name.
- **Instance false cognates** — distinct individuals that share a local name (two `R1`s in
  different sub-domains; two `svc-100`s) or an attribute value; must **not** be merged.
- **Structurally symmetric pairs** — two individuals with identical local topology,
  distinguishable only by a global key or by a virtual manipulation. These are the
  experiment-only cases, engineered so that static evidence genuinely underdetermines them.
- **Native gaps** — A-only and B-only individuals; correctly residual.
- **Keyless ambiguous** — individuals with no shared key and under-determining attributes;
  residual unless interrogation or manipulation is available.

**Semantic invariants in the gold.** Because the paper's verification is confirmation against
invariants rather than byte equality, the case encodes, for each individual and for the
services that can be provisioned over it, the invariant values a correct correspondence must
preserve: **endpoint identity, connectivity, capacity, layer relationships, switching
constraints, and multiplexing structure**. A virtual provision through a candidate co-reference
(§6) is scored *confirmed* only if the resulting objects match these invariants in place, and
*refuted* if any diverges — which is exactly how a wrongly-merged structurally-symmetric pair is
caught. The gold records the correct co-reference pairs, the planted instance false cognates
that must not be merged, the native gaps expected as residual, the per-correspondence invariant
signature, and the subset flagged **experiment-only** (resolvable in principle solely by
interrogation or manipulation), which lets us measure the shortfall directly as cognition
recedes.

## 5. Evidence factors (what to ablate)

The instance analogue of the reference fields — the *static* evidence an agent may use to
co-refer individuals before any interrogation or manipulation. These are the factors of the
ablation:

- **Global key** — a shared identifier across both graphs; the instance analogue of the
  concept id anchor. It trivializes co-reference when present, so — heeding the id-slug lesson
  from the reference-anatomy study — keys are **opaque** (`k01`, …), never leaked descriptors,
  and their presence/absence is a factor.
- **Local name/label** — the trap surface; where the instance false cognates live.
- **Attribute vector** — properties such as rate, coordinates, address, admin-state.
- **Relational/topological signature** — the individual's edges and neighbours; the
  hypothesised workhorse among static features, since an individual is largely defined by what
  it connects to (the A-box parallel to *definition* for concepts).
- **Provenance / temporal** — source and timestamp; optional, a secondary factor.

## 6. Live cognition, operationalized: interrogation and the virtual manipulation

The genuinely new machinery, and the crux of the study. Live cognition acts on the knowledge
graph in two distinct ways, both of which the MAGIC paper uses and both of which the harness
must provide through a single **oracle** on a live side, with every call counted:

1. **Interrogation (evidence-gathering).** The agent asks an authoritative question about an
   individual on a live side — a single authoritative attribute, or the response to a candidate
   operation ("issue operation *o* and read how the system responds"). This *reconstructs
   evidence* where static features underdetermine identity. It returns only what a real
   interrogation would — one authoritative fact per call, not a full record.
2. **Virtual manipulation (verification).** The agent *exercises a proposed correspondence*: it
   provisions a service through the candidate co-reference on a live side and confirms the
   resulting objects **in place against the semantic invariants** (§4). This is the paper's
   correctness-by-construction step, and it either **confirms** a proposal (invariants
   preserved) or **refutes** it (some invariant diverges). It is the only mechanism that can
   settle a structurally-symmetric pair from the graph itself.

The two are separated on purpose — interrogation feeds the *propose* stage, manipulation drives
the *verify* stage (§7) — and their availability follows the spectrum:

- **both-cognitive** — both interrogation and manipulation answer about either side; a call
  budget (including *unbounded* as a limiting condition) is a variable.
- **one-inert** — the oracle serves only the live side; the inert side is static, so an
  experiment-only individual on the inert side is resolvable only if a published reference (§8)
  supplies its identity or its invariants.
- **both-inert** — the oracle is unavailable; static evidence only; the agent may only propose,
  and closure needs an external test or a human sign-off.

With an unbounded budget at both-cognitive the residual should vanish; constrain or remove the
oracle and the experiment-only individuals reappear in the residual — the measurable form of
"resolution complete in principle with full cognition."

## 7. The pipeline: propose → verify → refer, with confidence

Mirroring the schema study's proposal-then-verification-and-repair, and making the paper's
"held with a confidence … corroborated by regenerating native records" mechanical:

1. **Propose.** From the available static evidence (and interrogation, where allowed), the
   agent proposes co-reference pairs, **each with a confidence**, and marks the rest residual.
2. **Verify.** Each proposal is corroborated — minimally by regenerating a native record and
   checking fit, and, where cognition and budget allow, by a **virtual manipulation** against
   the invariants (§6). A proposal that survives is **confirmed**; one that is refuted is
   dropped (and its individuals returned to residual or re-proposed); one that can be neither
   confirmed nor refuted (no live access, underdetermined) is **referred onward**, not asserted.
3. **Refer.** The residual is reported and, crucially, **broken out** into native gap,
   experiment-only-unresolved, and low-confidence-unconfirmed — so the shortfall is attributable
   to its cause at each placement.

This makes the confirm-versus-propose distinction explicit, so resolved fraction is read exactly as in the
schema study: a confirmed co-reference is asserted; an unconfirmed one is deferral, not error.

## 8. The reference family at the instance level

The reference is not only the key anchor. The paper names an **instance** variant and an
**invariant** variant (among others), and both bear on this study, so the reference is an
**axis**, not a fixed input:

- **none** — no shared reference; static evidence and live cognition only.
- **instance reference** — shared **opaque keys** plus canonical instance descriptors; the
  family analogue of the lexical reference, and the direct test of whether a published key
  substitutes for cognition (holding co-reference even where probing is gone).
- **invariant reference** — a published anchor that pins the **semantic invariants** for the
  individuals/services in play. This is what a virtual manipulation checks *against* when a side
  is inert and cannot itself be exercised: it lets an inert-side individual be tested against
  published invariants without a live experiment, so it is the mechanism expected to *partly*
  recover the experiment-only subset in the one-inert regime — bounded, because a reference can
  state the invariants but cannot run the experiment.

Running none / instance / invariant as arms is what tells us whether each reference variant does
the work the paper claims, and separates the key anchor's contribution from the invariant
anchor's.

## 9. Metrics

Correctness is again the clean, length-independent currency for "which evidence and which
mechanism matters":

- **Instance precision / resolved fraction** over the co-reference pairing, against the gold alignment —
  reported both at *proposal* and after *verification* (confirmed precision/resolved fraction), as in the
  schema verify-and-repair result.
- **Surviving instance false cognates** — distinct individuals wrongly merged (and, post-verify,
  how many the virtual manipulation caught).
- **Merge / split errors** — the entity-resolution failure modes (a single individual split
  across two records left unmerged; two individuals merged into one).
- **Invariant-confirmation rate** — of the true co-references, the fraction *confirmable* by
  virtual manipulation at each placement; the direct handle on resolution-complete-in-principle.
- **Confidence calibration** — proposed confidence against realised correctness, by model and
  placement.
- **Residual, broken out** — native gaps, experiment-only-unresolved, low-confidence-unconfirmed
  — the per-cause measure of the shortfall.
- **Effort** — **interrogation count** and **manipulation count** (the new task-specific
  currencies) reported alongside reasoning tokens.

## 10. Experimental design

The same shape as the schema studies: a **cognition-spectrum × evidence-ablation ×
reference-variant × model-ladder** cross over the seeded hard case, with a validated gold and
the propose→verify→refer pipeline.

- **Placements**: both-cognitive, one-inert, both-inert (the spectrum is the primary axis).
- **Evidence ablation**: a factorial over {global key, name, attributes, topology} (provenance
  optional), the always-present anchor being the individual's own record identity within its
  graph. Full factorial if the run stays affordable, a fractional design if not.
- **Reference variant**: none / instance / invariant (§8).
- **Oracle budget**: at least {none, bounded, unbounded} at both-cognitive, to trace the
  shortfall against interrogation-and-manipulation cost.
- **Models**: the strength ladder (`gpt-5.6-sol`, `gpt-5-mini`, `gpt-5-nano`), for the
  capability interaction.
- **Trials**: enough for stable per-condition means given model variance (≥ 5).

The full cross is large; §on execution (to be settled) will fix which axes run at full
factorial and which are sampled, and the checkpoint/resume and en-route-capture discipline is a
build requirement from the start, as for the completed studies.

## 11. Pre-registered predictions

1. **Resolvability, sharper.** With an unbounded oracle at both-cognitive the residual → 0; as
   cognition recedes and interrogation/manipulation are lost, the experiment-only individuals
   become unresolvable and the residual grows — a **larger** shortfall than in schema
   reconciliation, because for some individuals acting on the graph is the *only* route.
2. **The virtual manipulation is what closes the hard cases.** Structurally-symmetric pairs are
   resolved neither by static evidence nor by attribute interrogation but by the
   provision-and-read-back against invariants; their confirmed-resolved fraction tracks manipulation
   availability almost exclusively.
3. **Topology is the workhorse static feature**; its removal most increases merge/split errors,
   most at the inert placements where manipulation cannot compensate.
4. **Names are the trap surface** — without disambiguating features, shared local names drive
   wrong merges (instance false cognates).
5. **A shared key substitutes for cognition; the invariant reference substitutes for the
   experiment — partly.** A present opaque key holds co-reference even where the oracle is gone
   (the instance-family analogue of the lexical-reference result). The invariant reference
   recovers *some* experiment-only cases in the one-inert regime by letting an inert-side
   individual be checked against published invariants — but not all, since a reference can state
   invariants and cannot run the experiment.
6. **Confidence calibration degrades with capability** — weaker agents are more often confidently
   wrong, and lean on names and keys while under-exploiting topology, interrogation, and the
   virtual manipulation.

## 12. What it reuses, and what must be built

Reused as-is: the case/gold/derive-and-validate pattern, the cognition-spectrum treatment, the
model ladder, the correctness-first measurement discipline, the proposal-then-verification shape
of `verify_experiment.py`, and most metrics.

To build:

- an **instance-reconcile task** in the harness (propose co-reference pairs with confidence +
  residual over individuals, scored against an instance gold);
- the **oracle** on a live side, providing both **interrogation** (one authoritative fact per
  call) and the **virtual manipulation** (provision-and-read-back confirmed against the invariant
  set), with separate call counters; this is the main lift and worth building carefully, since it
  is what makes the spectrum meaningful for individuals and carries the paper's verification
  claim;
- a **verify-and-repair stage** for instances: corroborate each proposal by native-record
  regeneration and, where allowed, virtual manipulation; split the residual by cause;
- a **seeded instance case** over the reconciled TAPI/TEAS types, with the trap taxonomy of §4,
  the per-correspondence **invariant signatures**, and an `experiment-only` flag in the gold;
- the **instance and invariant references** (shared opaque keys / canonical instance descriptors;
  and a published invariant anchor) as the family analogues of the lexical reference, for the
  reference-variant axis and the with/without-reference contrast;
- checkpoint/resume with en-route row-by-row capture, from the start.

## 13. Open design questions

- **Oracle fidelity, per mechanism.** Interrogation returns one authoritative fact per call;
  the virtual manipulation returns the invariant check on the provisioned objects — no more than
  a real provisioning-and-read-back would. Both are bounded to what a real operation reveals;
  the fidelity ceiling is set so that easy cases are not made trivial and symmetric cases are not
  made impossible.
- **Separating "confirm" from "propose".** The verify stage must distinguish a
  proposed-but-unconfirmed co-reference (referred onward) from an asserted one, so resolved fraction is read
  the same way as in the schema study; §7 makes this mechanical.
- **Schema coupling.** This study assumes the schema is already reconciled. A later, harder
  variant would run schema and instance reconciliation *jointly*, where a tentative type
  alignment and a tentative instance alignment inform each other.
- **Invariant reference authoring.** How much the invariant reference publishes (which of the
  six invariants, at what granularity) is itself an ablatable question; the first run fixes a
  sensible full-invariant anchor and leaves the finer ablation to a follow-up.
