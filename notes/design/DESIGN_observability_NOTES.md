# Observability (setting 4) — early design thinking

> Prep notes, not a design of record. Grounded in the `anomaly.html` demonstration and verified
> against the standards. To be turned into a full design + build after review. This is the
> setting Thomas Graf will scrutinise hardest, because it is, in effect, an empirical test of his
> own anomaly-semantics work — so the standards grounding must be exact, not decorative.

## The setting

One network, two observability worlds, no common model.

- **Agent F — legacy fault manager.** RFC 8632 alarms, syslog, SNMP traps, a vendor X.733
  probable-cause dictionary. In this world an *alarm* is a catch-all, bundling an event, a state,
  a **fixed severity** (critical / major / minor / warning) and a **static probable-cause code**,
  all hard-coded at emission.
- **Agent G — IETF NMOP agent.** RFC 9940 terminology; Thomas Graf's
  **draft-ietf-nmop-network-anomaly-semantics** (concern & confidence scores,
  action·reason·trigger, lifecycle stage, context — network plane, season, maintenance window);
  **draft-ietf-nmop-network-incident-yang** for correlation; the anomaly-architecture and
  anomaly-lifecycle drafts.

## Why this is the culmination — and the hardest

Three things make it the peak of the programme, and each is where Graf will press.

1. **The false cognate is ontological, not lexical.** Across the whole programme the traps have
   been lexical or structural. Here the headline trap is a category error, and RFC 9940 makes it
   precise: an **alarm is "an undesirable State … a State in its own right,"** while an **anomaly
   is a deviation — "an unusual or unexpected Event or pattern … that deviates from … normal,
   expected behavior,"** *not* defined as undesirable. A legacy alarm label-matches an NMOP
   anomaly, but one is an undesirable state and the other a deviation that may be perfectly
   benign. This is the deepest cognate we have posed: getting it wrong is not a mislabel, it is a
   wrong *kind of thing*.

2. **The mapping is a one-to-many decomposition, lossy upward.** The overloaded legacy alarm must
   be **decomposed** into the several NMOP concepts it conflates (event, anomaly, symptom, fault,
   alarm-as-State, problem, cause, incident). F→G lifts a legacy alarm into its NMOP constituents
   for correlation; G→F projects an NMOP symptom/incident back down to a single legacy alarm a
   legacy console can show — and these are **not inverses**, because legacy is lossy upward. This
   is harder than the 1:1 (setting 1) or partial-overlap-at-a-seam (setting 3) mappings.

3. **Pragmatics *are* the meaning.** In the first three settings pragmatics were deferred (1),
   introduced as a movable policy (2), or measured as authority (3). Here they carry the entire
   verdict. A rising pre-FEC BER anomaly on wavelength λ1 means nothing *in the data*; what it
   means depends on: its **significance and confidence** (act or watch), its **context** (a planned
   maintenance window makes the identical deviation benign), and its **causal role** (a symptom,
   correlated with an IP-layer symptom into **one incident** with a probable cause — not two
   uncorrelated pages). Turn the pragmatics off and you get the legacy result: an alarm storm, a
   false page during maintenance, no incident.

## The dangerous pins (each fixed by a canonical example)

- a **fixed severity label** (critical/major/…) is **not** a **dynamic concern score**;
- a **static probable-cause code** (X.733) is **not** a **cause derived by correlation**;
- the **overloaded alarm** must be **decomposed** into its NMOP constituents.

## How it reuses the harness

- **Act 1 — reconcile the models (schema binding).** Reuse the cross-domain / setting-1 schema
  harness. The shared reference is **anchored to the RFC 9940 ladder** and agreed by canonical
  example, exactly the constructed-reference machinery of setting 3 — but with an *ontological*
  false cognate (alarm≠anomaly) and a *one-to-many decomposition* rather than clean pairs. Measures
  as before: resolved fraction, precision, survival of the alarm/anomaly cognate, decomposition
  correctness, across the cognition spectrum × reference.
- **Instance co-reference.** Which legacy alarm and which NMOP anomaly are the *same underlying
  condition* (resource + time). Reuses the instance machinery; expected, as in settings 2–3, to
  reproduce setting 1 — so bracketed or run light.
- **Act 2 — the pragmatic verdict engine (the headline).** A **pragmatics matrix**: the *same*
  rising-BER anomaly under different pragmatic contexts (maintenance window on/off, network plane,
  concern/confidence levels, an IP-layer symptom present or absent) reaching *different* correct
  verdicts (act / watch / suppress; promote to symptom; correlate into one incident vs none). This
  is the intent setting's policy judgement and the cross-domain authority call, taken to their
  culmination: **verdict-under-context, plus correlation.** Reuses the pragmatics-stack pattern
  with a deterministic **pragmatic-and-correlation oracle**.

## Central hypothesis

In observability, **meaning is pragmatic**. Cognitive agents that carry the RFC 9940 + anomaly-
semantics annotations reach the correct act/watch/suppress verdict and correlate anomalies into
incidents; strip the pragmatics (the legacy pipeline, or pragmatics-off) and the identical data
yields alarm storms and false pages. And — echoing settings 2 and 3 — the **reference enables the
binding but the pragmatics are cognition's**: a shared reference settles what an anomaly *is*, but
whether it *matters* is a judgement the annotations inform and cognition makes. The reference
reaches meaning; significance is cognition's.

## The four-setting arc (the pragmatics thread, completed)

- **S1 configuration** — pragmatics deferred; schema/structural binding + verification.
- **S2 intent** — pragmatics enter as a movable policy (accept/reject a degraded offer under
  priorities).
- **S3 cross-domain** — pragmatics as authority (whose realm owns a field); the reference reaches
  meaning, not authority.
- **S4 observability** — pragmatics as **meaning itself** (significance, context, causal role
  decide what the data means). The thread's culmination, and the strongest statement of the
  programme's claim that pragmatics are the frontier the descriptor methods never reach.

## Graf-proofing checklist (non-negotiable, because this is the scrutinised one)

1. **Reference grounded verbatim on RFC 9940** — alarm = undesirable State; anomaly = deviation;
   event, symptom, fault, problem, cause, incident as defined, with the *actual* relationships
   (Event → Occurrence → Fault/Problem → Incident, with Symptom and Cause threaded), **not** a
   simplified linear ladder.
2. **Annotations verbatim from draft-ietf-nmop-network-anomaly-semantics** — the exact fields
   (concern, confidence, action·reason·trigger, lifecycle stage, context taxonomy). Pull them from
   the current draft, don't paraphrase.
3. **Correlation grounded in the incident-yang / anomaly-architecture / anomaly-lifecycle drafts** —
   the anomaly→symptom→incident promotion and the multi-symptom→one-incident correlation must
   follow the drafts' model, not an invented one.
4. **A validated pragmatic-and-correlation oracle** — the act/watch/suppress verdicts and the
   correlations must be *derived deterministically* from the annotations and context, and validated
   for internal consistency, exactly as the earlier settings derived their gold. If the verdicts
   look hand-assigned, the result is dismissible; if they fall out of a defensible oracle, it is
   not.
5. **A technically coherent worked anomaly** — pre-FEC BER on λ1 as an early optical-degradation
   signal, correlated with an IP-layer symptom into one cross-layer incident, suppressed under a
   maintenance window. It must read as real to an optical+IP observability engineer.
6. **Honest scope** — say what is modelled and what is bracketed, as in the other reports.

## Open questions for Chris (before building)

- **Weight of the study.** Full Act 1 (schema reconcile) *and* Act 2 (pragmatics), or put the
  study's weight on Act 2 — pragmatics-as-meaning, the novel and Graf-relevant core — with Act 1 as
  the enabling schema binding reported more briefly (as cross-domain treated instance)?
- **Correlation depth.** Single anomaly → incident, or genuine multi-symptom cross-layer
  correlation (optical + IP → one incident)? The latter is the real demo claim and the stronger
  result, but needs the correlation oracle.
- **Annotation coverage.** Model the full anomaly-semantics annotation set, or a focused subset
  (concern, confidence, context, causal role) that carries the verdict?
- **Graf himself.** Since the study effectively validates his anomaly-semantics draft with
  cognitive agents, is there value in previewing the design with him — turning the "most scrutiny"
  into a collaboration, and pre-empting the objections by having posed them first?
