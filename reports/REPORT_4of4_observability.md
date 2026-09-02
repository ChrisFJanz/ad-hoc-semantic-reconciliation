# 4/4 · Reconciling observability: an alarm is not an anomaly, and what a page and an incident really mean

> *Programme status — the **fourth and last of the programme's four operational settings**
> (observability). The first three settings reconciled structural models, refined a declarative
> intent, and bridged two private domains; this one reconciles two **observability** worlds — a
> legacy fault manager and an IETF NMOP agent — and completes the programme's pragmatics thread.
> Here the pragmatic component, deferred in the first setting and studied as a movable policy and
> then as authority in the next two, carries the **operative meaning** of what the systems observe:
> whether an anomaly warrants a page, and how separate symptoms are one incident. It is grounded in
> the NMOP work — RFC 9940 terminology, the anomaly-semantics annotation set, and the
> incident-yang correlation model — with the standards grounding kept exact and the scoring falling
> out of a validated deterministic oracle.*

## Summary

Two systems watch the same network and disagree about what they see. **Agent F** is a legacy fault
manager: to it, an *alarm* is a catch-all — an event, an undesirable state, a fixed severity, and a
static probable-cause, all bundled and hard-coded at emission. **Agent G** is an IETF NMOP agent:
it speaks the RFC 9940 term ladder, which separates what legacy conflates — event, anomaly, symptom,
fault, alarm, problem, cause, incident — and annotates each anomaly with the semantic metadata of
the anomaly-semantics draft (a concern score, a confidence score, a network plane, a pattern, a
lifecycle stage, a season). The two must share an understanding of anomalies with no common model.
(Throughout, a **page** is an alert raised to an on-call human operator — the thing a false alarm
wastes and a missed one is measured against.)

The setting runs in two acts, and the study measures both. **Act 1 reconciles the two models** — a
schema binding, like the earlier settings, but carrying the programme's deepest false cognate: a
legacy *alarm* is not an NMOP *anomaly*. RFC 9940 is exact about why — an alarm is *"an undesirable
State … a State in its own right,"* an anomaly is *"an unusual or unexpected event or pattern that
deviates from normal expected behaviour,"* a deviation that may be perfectly benign. The intuition
"something is abnormal" fits both; they are different *kinds of thing*, and conflating them is not a
mislabel but a category error. Act 1 also asks the overloaded legacy alarm to be **decomposed** into
the several NMOP concepts it bundles. **Act 2 runs a live anomaly through**, and lets the pragmatics
decide: a rising pre-FEC BER deviation on a wavelength means nothing *in the data* — whether it
warrants a page depends on its concern and confidence and on its context (a planned maintenance
window makes the same deviation expected), and whether it is one incident or many depends on
correlating it, across layers, with the symptoms it causes.

Three results complete the programme's arc. First, the **ontological cognate is a clean three-rung
capability gradient**: the strong agent never conflates an alarm with an anomaly; the mid agent does,
as cognition recedes, and the RFC 9940-anchored reference **rescues** it; the weak agent conflates
them with or without the reference — beyond rescue. The lexicon pins the ontology for the middle of
the ladder, not the bottom. Second, in Act 2 the **pragmatics carry the operative verdict** — with
the semantics on, the agents suppress correctly during maintenance and the false-page storm
disappears; with them off, the legacy pipeline pages nearly everything — **but the payoff is itself
capability-gated**: handed the same annotations, the weak agent still cannot produce the verdict.
Third, **correlation is different**: given the resource-dependency structure, *every* model — the weak
one included — folds an optical degradation and the IP loss it causes into one incident, and without
that structure every model fails. Where a pragmatic is a *structural input*, even a weak agent applies
it; where it demands *judgement*, only a capable agent can.

So the programme's through-line reaches its end and gains its final clause. Cognition completes a
reconciliation; a thin reference supplies the information a reconciliation needs and stops at what it
does not; and the pragmatic frontier the descriptor methods never reach is real, decisive for
meaning — and itself bounded by capability. Meaning (what an anomaly *is*, pinned by the reference)
and significance (whether it warrants a page and how it correlates, carried by the pragmatics) are
separable, both necessary, and each gated in its own way.

## 1. The setting: two observability worlds, and one live anomaly

Picture the two agents (Figure 1). **Agent F**, the legacy fault manager, emits an *alarm*: one
object that bundles the event that fired it, the undesirable state it represents, a fixed severity
label (critical / major / minor / warning), and a static X.733 probable-cause code. **Agent G**, the
NMOP agent, does not have that object; it has the RFC 9940 ladder, which pulls those apart into an
event, a fault, an alarm (a *State*), and — concepts legacy has no first-class equivalent for — an
anomaly, a symptom, a problem, a cause established by correlation, and an incident, each anomaly
carrying its anomaly-semantics annotations.

![The observability setting](../figures/fig_obs_scene.png)

*Figure 1. The overloaded legacy alarm decomposes, one-to-many, into the NMOP ladder. Its correct
core is the NMOP alarm-State (and a fault); the trap is the anomaly — a deviation, not a state. An
alarm is not an anomaly.*

Follow one live anomaly, the study's worked example. A pre-FEC bit-error-rate reading on wavelength
λ1 begins to rise — an *anomaly*, a deviation from normal. In the legacy world this would fire an
alarm and a page. In the NMOP world nothing is decided yet: the anomaly is annotated (a concern
score, a confidence score, a plane, a pattern), and what it *means* is then a pragmatic question.
Is the concern high and the detector confident? Then act. Is a planned maintenance window in effect
on λ1? Then the very same deviation is expected — suppress; a page now would be a false alarm. And
if, moments later, an IP link that rides λ1 shows packet loss, that is not a second, separate page:
it is the *same* incident, the optical degradation being the probable cause of the IP loss, and the
two symptoms correlate into one. The whole difference between an alarm storm and a single, correctly
attributed incident lives in those pragmatic judgements.

## 2. What is on the bench

The setting runs in two acts, and the study measures each with the machinery it needs.

**Act 1 — reconcile the models.** This is a schema binding, and it reuses the harness of the earlier
settings unchanged: two lifted models, a constructed reference anchored to the RFC 9940 ladder, and a
gold of correspondences and false cognates, scored across the **cognition spectrum** (both-cognitive,
one-inert, both-inert) with the reference present or absent. Two things make it harder than a plain
binding. The gold correspondences include a **one-to-many decomposition** — the legacy alarm maps to
*both* the NMOP alarm-State and the fault it implies — and the headline false cognate is the
**ontological** one, alarm↔anomaly, which no structural cue separates. A second, bracketed phase
co-refers *instances* — which legacy alarm and which NMOP anomaly are the same underlying condition
(by resource and time) — reusing the instance machinery; as in the earlier settings it reproduces the
first study's behaviour and is not the headline.

**Act 2 — run the anomaly, and let the pragmatics decide.** Two tasks, each measured with the
semantics-and-pragmatics turned **ON** and **OFF** — the demonstration's toggle, and the study's
central contrast. The **verdict** task: given a set of anomalies under a context, decide each one's
operative verdict — *act*, *watch*, or *suppress*. With pragmatics ON the agent has the anomaly-
semantics annotations and the context (whether a maintenance window is in effect, whether it is a
workday or a holiday); with pragmatics OFF it has only a legacy alarm view — a severity, no scores,
no context — the legacy pipeline. The **correlation** task: given symptoms across layers with a
resource-dependency map, group them into incidents and name each incident's probable cause; OFF, the
legacy console has no dependencies and reports each symptom as its own page.

**The verdict gold is a deliberate, explicit modelling choice.** The oracle derives *act / watch /
suppress* deterministically — a maintenance window suppresses; an expected seasonal shift in its
season suppresses; otherwise high concern with high confidence acts, moderate concern watches, low
concern suppresses (with thresholds on the anomaly-semantics 0–100 scales). We state the thresholds
openly rather than bury them: they are exactly the kind of operational calibration this setting
exists to expose, and a concrete artefact for discussion rather than a hidden assumption. The
correlation gold is derived from the resource-dependency graph and time-proximity, with the probable
cause the root symptom (lowest layer, earliest). The derivation refuses to write an inconsistent gold
and proves the pragmatic axis is real — the same anomaly reaches different verdicts under different
contexts.

Correctness is the currency throughout: for Act 1, resolved fraction, precision, and surviving false
cognates; for Act 2, verdict accuracy and false-page count, and incident-partition and cause accuracy.
The model ladder is the programme's — sol (strong, `gpt-5.6-sol`), mini (mid, `gpt-5-mini`), nano (weak, `gpt-5-nano`).

## 3. Results

### 3.1 Act 1: the ontological cognate is a three-rung capability gradient

An alarm is a State; an anomaly is a deviation. Holding that distinction — the deepest false cognate
the programme has posed — turns out to depend sharply on capability, and it is where the RFC 9940
reference earns its place (Figure 2).

![The ontological cognate across the ladder](../figures/fig_obs_ontology.png)

*Figure 2. Survival of the alarm↔anomaly cognate at the inert placements, without and with the
reference. The strong agent never takes it; the reference drives the mid agent's bar to zero; the
weak agent's bar barely moves.*

The **strong** agent never conflates them — surviving cognates zero, with or without the reference,
at every placement. It knows the ontology intrinsically. The **mid** agent takes the cognate once a
side goes inert and no reference is present (precision falls to about 0.69), and the RFC 9940-anchored
reference **rescues it completely** — the cognate vanishes and precision returns to 1.0. This is the
reference doing exactly the job the setting was built to test: pinning, by definition and canonical
example, the categorical distinction a mid agent otherwise collapses. The **weak** agent takes the
cognate with or without the reference — its survival barely moves when the reference is added. Handed
the standard that separates a state from a deviation, nano cannot use it to hold the two apart.

So the lexicon pins the ontology for the middle of the ladder, not the bottom: intrinsic mastery, then
reference-rescuable, then beyond rescue. (All three agents bind the easy correspondences with perfect
precision; where they fall short of a full close is the **one-to-many decomposition** — even the
strong agent tends to map the legacy alarm to the NMOP alarm-State but miss the fault constituent, so
the resolved fraction sits near 0.75. Decomposing an overloaded concept into its several parts is the
honest hard edge of Act 1.)

### 3.2 Act 2, the verdict: the pragmatics collapse the false-page storm — for agents that can carry them

Turn to the live anomaly. With the semantics and pragmatics **ON**, the strong and mid agents reach
the operative verdict and, crucially, stay quiet when they should: in a maintenance window they
suppress correctly (verdict accuracy 1.0 and 0.83) and raise essentially no false pages. With the
pragmatics **OFF** — the legacy pipeline — the same maintenance window is a false-page catastrophe:
accuracy collapses to 0.17 and 0.08, with roughly four and three-and-a-half false pages raised where
the answer was to stay silent (Figure 3, left). This is the legacy alarm storm during planned
maintenance, measured against the context-aware agent that knows the deviation is expected.

![Pragmatics ON vs OFF](../figures/fig_obs_pragmatics.png)

*Figure 3. Left: verdict accuracy, pragmatics OFF (pale) vs ON (solid). The strong and mid agents
gain sharply; the weak agent barely moves — ON ≈ OFF. Right: incidents correlated exactly. Every
model correlates with the dependency map and fails without it.*

But the payoff is **capability-gated**, and the weak agent draws the line. Handed the identical
annotations and context, nano shows almost no ON/OFF difference — accuracy 0.53 with pragmatics
versus 0.50 without, and only 0.17 even in the maintenance window it was told about. The pragmatics
are there; nano cannot reason over them to produce the verdict. So "the pragmatics carry the operative
meaning" is true only for an agent capable enough to carry them; below that floor, the annotations
are inert.

### 3.3 Act 2, the correlation: the dependency map turns a storm into an incident — for everyone

Correlation behaves differently, and the contrast is the subtle heart of the setting (Figure 3,
right). Given the resource-dependency map — that wavelength λ1 underlies the IP link — **every** model,
the weak one included, folds the optical BER symptom and the IP loss it causes into a single incident,
rooted correctly at the optical cause: all three reach a perfect incident partition with pragmatics
ON. Without the dependency map, all three fail — the mid and weak agents fragment every scenario into
a storm of separate pages, and even the strong agent, which half-infers the correlation from the
symptom labels alone, does not get it right. One correlated incident with the pragmatics; an alarm
storm without.

The difference between the verdict and the correlation is the lesson. The correlation's pragmatic is a
**structural input** — a dependency graph — and applying it is mechanical enough that even a weak agent
succeeds once handed it. The verdict's pragmatic demands **judgement** — weighing concern against
confidence against context — and there capability decides. Both are pragmatics; both are decisive; but
they place very different demands on the agent that must use them.

### 3.4 Effort

The effort gradient is the steepest in the programme: to reach its Act 2 verdicts the strong agent
spent about 60 reasoning tokens, the mid agent about 520, and the weak agent about 1,200 — twenty
times the strong agent's effort, to reach a verdict no better than chance on the cases that mattered.
Capability buys economy and correctness together, and the standard-free, pragmatics-laden observability
task exposes the gap most starkly.

## 4. Discussion

**The programme's arc, completed.** Across four settings the pragmatic component has moved from the
wings to the centre. In the first setting it was deferred, and schema structure and a lexical reference
did the work. In the second (intent) it entered as a **movable policy** — the consumer's priorities and
affordability deciding whether a degraded offer is accepted. In the third (cross-domain) it was
**authority** — whose realm owns a shared field — and the reference was shown to reach meaning but not
authority. Here, in observability, it carries the **operative meaning**: whether an anomaly warrants a
page, and how symptoms are one incident. The claim the programme has built toward — that pragmatics are
the frontier the descriptor methods never reach — is strongest here, because here the descriptor level
(what an anomaly *is*) is settled and the entire operational question is pragmatic.

**Meaning and significance are separable, and both are needed.** The setting cleanly divides two things
that a single "meaning" would blur. What an anomaly *is* — a deviation, not a state — is a matter of
ontology, and the RFC 9940 reference pins it (for agents able to use it). Whether an anomaly *matters* —
act, watch, or suppress — and how it *composes* — one incident or many — is a matter of pragmatics, and
the annotations and dependency structure carry it. Strip the ontology and a mid agent conflates an
alarm with an anomaly; strip the pragmatics and even a strong agent floods the console with false pages
and uncorrelated storms. The observability reconciliation needs both, and they are supplied by different
means.

**The pragmatic frontier has a capability floor.** The programme's thesis is that cognition completes a
reconciliation; this setting adds a boundary condition that the earlier ones only hinted at. The value
of the pragmatics — like the value of the reference on the ontological cognate — is realised only by an
agent capable enough to use them. Below that floor the weak agent cannot hold the ontology even with the
reference, and cannot produce the verdict even with the annotations. What it *can* still do is apply a
structural pragmatic it is handed outright — the correlation dependency map — which is why correlation is
the one Act 2 task robust across the whole ladder. The frontier is real and decisive; it is also gated,
and the gate is capability.

**A note for calibration.** The verdict oracle's thresholds are a modelling choice, stated openly (§2).
The strong and mid agents' imperfect scores on the fine concern/confidence gradations in the non-
maintenance contexts are as much a reflection of where a qualitative judgement meets a numeric threshold
as of any agent shortcoming; the unambiguous, context-driven cases (suppress during maintenance) are
where the ON/OFF contrast is cleanest and least contestable. This is exactly the kind of operational
calibration the anomaly-semantics work exists to standardise, and the study offers it as a concrete
artefact to refine, not a settled answer.

## 5. Threats to validity

The case is single and seeded, built to exercise each mechanism and prove each trap, not sampled; it
establishes how the observability reconciliation behaves and why, not how often. The verdict gold rests
on an explicit threshold model, reported as such; different thresholds would move the fine-gradation
scores though not the maintenance-window contrast. The pragmatics-OFF baseline is a stylised legacy
pipeline (page on severity, no correlation), faithful to the legacy pathology but not a specific
product. Trials are few, so single-cell numbers carry noise; the reported patterns are the ones stable
across the model ladder and the ON/OFF toggle. The instance-level alarm/anomaly co-reference is
bracketed on the same grounds as in the earlier settings — it reproduces the first study's mechanism —
rather than run as a headline. And the correlation model is a resource-dependency-and-time abstraction
of the incident-yang correlation, not its full machinery.

## 6. Reproducibility

The seeded observability case (both lifted models, the RFC 9940-anchored reference, the annotated
anomalies, the pragmatic contexts, and the cross-layer correlation scenarios), the verdict and
correlation oracles, the derive-and-validate step, the four-phase runner, and the figure scripts are in
the repository, with the recorded per-model results. The build, the gold derivation, and the offline
tests run with no API and no network; the runs are a single launch-and-leave command, segmented by phase
and model and resumable. The worked contrasts are reproduced from the recorded CSVs.
