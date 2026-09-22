# The results — a completed four-scenario study

*The empirical realisation of the [research programme](../proposal/) in
[ad hoc semantic reconciliation](../). Four operational scenarios, built, run against a validated gold
standard, and reported, with a master report drawing them into one synthesis.*

> Part of the larger project — the theory and programme that motivate this study are in
> [`../proposal/`](../proposal/); the interactive demonstrations are in [`../demos/`](../demos/).

The central finding, established across all four scenarios: **it is cognition that completes a
reconciliation.** Descriptor methods — matching names, then names plus a gloss — carry it to a ceiling
and stop, historically leaving the rest to a standard or a person. Where both systems can reason, the
remainder is closed **autonomously**, with no model agreed in advance and no human in the loop, and
only as cognition recedes does a residual have to be referred onward. A thin, published **reference**
can substitute for cognition, or supply an inert side the facts it lacks — but its reach ends there:
it hands over information, never the **authority** to decide, whose value governs or whether a
trade-off is acceptable. And the **pragmatic** layer — what a reconciled thing is *for*,
whether it matters, who decides — is the frontier the descriptor methods never reach: decisive for
meaning, and itself bounded by the agent's capability.

## Start here — the master report

**[reports/MASTER_REPORT.md](reports/MASTER_REPORT.md)** &nbsp;·&nbsp;
**[PDF](reports/MASTER_REPORT.pdf)** &nbsp;·&nbsp;
**[slides (PDF)](reports/MASTER_REPORT_Deck.pdf)** — the synthesis that sits atop the four scenarios. It
introduces the idea once (the lift, portable semantic models, the family of reconciliation operations,
and the cognition spectrum), distils each scenario to its essentials, and then gathers the findings so
they can be read as one result: what works and how far, the **six theses** the scenarios establish, the
evidence behind them along a set of cross-cutting readings (cognitive load, model power, the reference,
placement and failure, reach, the pragmatic layer, and what it takes to **produce the inputs** the whole
thing runs on), two tables mapping every finding to its placement and to the process stage it acts on,
the surprises, and the scope. The slide deck carries the same synthesis for readers who prefer slides.

![The lift — a data model becomes a portable, self-describing semantic model.](figures/fig_master_lift.png)

![Reconciliation over two lifted models — grounded correspondences bound through a thin reference, a rejected cognate, and what is honestly left unbound (no counterpart, or the residual referred onward).](figures/fig_master_reconcile.png)

## The four scenarios

Each scenario takes the same frame to a new operation. Each has a report (renders inline), a
print-ready **PDF**, and an interactive **demo** (opens in your browser; see [`../demos/`](../demos/)
for download links too).


**1/4 · [Configuration](reports/REPORT_1of4_configuration.md)** &nbsp;·&nbsp;
[PDF](reports/REPORT_1of4_configuration.pdf) &nbsp;·&nbsp;
▶ [demo](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/configuration.html) —
two standard models of one network. ONF **TAPI** ↔ IETF **TEAS/ACTN**, seeded with false cognates and
opaque items. The founding scenario: it shows the thin reference **substituting for cognition**, the
benefit **capability-dependent**, verification catching the traps, and work scaling **linearly** with a
reference against quadratically without. Its four sub-studies are folded into the report and preserved
as method notes under `notes/studies/`.

**2/4 · [Intent](reports/REPORT_2of4_intent.md)** &nbsp;·&nbsp;
[PDF](reports/REPORT_2of4_intent.pdf) &nbsp;·&nbsp;
▶ [demo](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/intent.html) —
refinement, negotiation, and a service that renegotiates itself. A customer's intent reconciled against
an operator's catalogue by **refinement**, not equivalence; verification becomes a **satisfaction**
check; a **negotiation** appears; the pragmatic operation enters as a portable **movable
policy**; and the exchange **recurs across a service's life**. Grounded in the IRTF NMRG draft
*draft-janz-nmrg-naas-agentic-negotiation*.

**3/4 · [Standard-free](reports/REPORT_3of4_standard_free.md)** &nbsp;·&nbsp;
[PDF](reports/REPORT_3of4_standard_free.pdf) &nbsp;·&nbsp;
▶ [demo](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/cross_domain.html) —
reconciling with no public standard. Two **home-grown, private** models meet at one seam. The central
result is a **mirror**: without the constructed reference the strong agent **under-commits** (defers at
perfect precision) and the weak agent **mis-commits** (binds wrongly). A single descriptive field
unlocks a capable agent; a bare shared pointer is worse than nothing. Building the shared ground is the
work — and, run end to end, an agent that builds it itself lifts from **0.20 to 0.80** (0.90 with a
decisive virtual experiment).

**4/4 · [Observability](reports/REPORT_4of4_observability.md)** &nbsp;·&nbsp;
[PDF](reports/REPORT_4of4_observability.pdf) &nbsp;·&nbsp;
▶ [demo](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/anomaly.html) —
an alarm is not an anomaly. A legacy fault manager and an IETF **NMOP** agent (RFC 9940) reconcile two
observability worlds, carrying the programme's deepest false cognate and a one-to-many decomposition.
The **pragmatics carry the operative verdict** — but only for an agent able to carry them; while
**correlation**, a structural pragmatic, is robust across the whole ladder.

The reconciling agents are one **model ladder** for the whole study: `gpt-5.6-sol` (**strong**),
`gpt-5-mini` (**mid**), `gpt-5-nano` (**weak**) — "sol / mini / nano" — chosen so the ladder isolates
model strength rather than provider or architecture.

## How it works

The **lift** is the move from a *data model* (a schema and its records: already a partial semantic
picture, but a fixed one, with much of its meaning left implicit) to a *semantic model* that carries
its meaning explicitly. A semantic model has three
parts: an **ontology**, including its **lexicon**, with a schematic layer (concepts, their kinds and
relations, and the labels and synonyms that name them: the **TBox**) and a concrete layer (the
instances that populate them: the **ABox**); **pragmatics**, the contextual information a consumer needs
(what a thing is for, whose authority governs it, in what context it holds), obtained not by lookup but
by judgement; and **provenance** (who asserted each part, by what method, how firmly). The lift itself is a cognitive act, aided by supports that are not parts of the
model: definitions, worked examples, a canonical example, and an optional link to a shared reference.
Being self-describing, a lifted model is **portable**: any cognitive consumer can pick it up with no
pre-agreed standard. Reconciliation runs over these lifted models, not over labels.

Drawn out, the ontology and its instances are a **knowledge graph**: the schematic layer is its schema
(typed concepts and permitted relations) and the concrete layer is its assertions (typed individuals
and the edges among them). Reconciliation divides the same way — aligning concepts is ontology
matching, and co-referencing individuals is entity resolution over the graph — which is where the
community's knowledge-graph work for network operations meets this approach. The pragmatics and
provenance are what the semantic model adds beyond a bare graph, and they are exactly what a thin
reference cannot supply.

A **case** is two lifted semantic models plus a gold standard *derived from the models and validated*,
so it cannot drift. A **reasoning stack** reconciles them — deterministic controls and a language-model
agent run at each point on the **cognition spectrum** (both live, one inert, both inert). At the
fully-cognitive end the two live sides reconcile as two separate agents under information asymmetry, each
holding only its own lifted model and a surface catalogue of the other's, proposing correspondences and
ratifying the other's, with the option of a decisive virtual experiment to settle a hard pair; as a side
goes inert a single agent reconstructs it. The
**harness** scores the output against the gold and records quality — *precision*, *resolved fraction*,
*surviving false cognates*, and the *residual* — and, for the agent, cognitive effort (reasoning
tokens, latency). A resolved fraction below one is deferral, not error: the residual is the shortfall
from full cognition's reach, and it grows as cognition recedes.

## What's new (2026-09-22)

A **conceptual sharpening** of the master report, and a new experimental direction, drawn from a
working exchange on how the lift actually works. The findings, theses, and results are unchanged; what
is added is a clearer account of *how the lift produces meaning* and *what would prove it on real
systems*. A companion synopsis of related work is added under `reports/`.

- **The lift and its placement, made precise (§4).** Two axes now organise where cognition sits:
  **access** (situated, able to consult the running system, or un-situated, holding only the artefact)
  and **product** (an internal understanding, or an externalised, self-standing model). The lift is the
  situated-and-externalising corner; a new figure, the **quadrangle**
  (`figures/fig_master_quadrangle.png`), places it against the three others. The section states the
  placement as a **hand-off** — cognition situated once, as the lift, so that an un-situated consumer
  needs only the artefact — and reframes the hard limit of a static artefact as, most often, a
  **missing-lift gap** (a fact present in the system that a situated lift reaches) rather than a true
  frontier. What a concept needs then partitions in three: what is implicit but present (grounded
  generation), what is present but elsewhere (situated access), and what is neither (the residue).

- **The lift generates, within a bound (§3).** Producing a semantic model is not transcription: the
  lift writes glosses where the surface gave none, makes implicit meaning explicit, infers untyped
  relations, and articulates tacit pragmatics. The bound is **grounded generation against
  confabulation** — content synthesised from structure, instances and state and checkable against them,
  not a sense invented for a bare name.

- **The decisive next experiments (§23).** The most consequential open step, and one only an operator
  can take, is a **situated lift on a live system**: attach cognition to a controller or datastore, have
  it perform the lift in place with real access to state, instances and pragmatics, and measure
  portability against the un-lifted baseline. The section gives a concrete protocol — how to attach
  cognition, how it pursues the lift, how portability is measured, a situatedness dial from emulator to
  self-lift — and names the prize: only a situated study can measure the true **residue**. It also names
  the **observability case, run with NMOP**, as the readiest host: significance verdicts that carry only
  when the pragmatics are present make it where a situated lift matters most, and the NMOP anomaly work
  and its hackathons already supply the data, the term ladder, and the venue. A prioritized
  recommendations list heads the future work.

- **A companion synopsis** of an independent YANG-description-quality study is added at
  `reports/companion_yang_description_synopsis.md` (with PDF). It is referenced as the **un-lifted
  baseline** against which the lift's value is the distance travelled up the quadrangle's diagonal.

- **The quadrangle related to the cognition spectrum (§4).** A short passage now ties the two devices
  rather than leaving them side by side: the spectrum grades the quadrangle's *access* axis (as a
  per-party dial, from self-lift or both-cognitive through to inert), while the quadrangle's *product*
  axis — externalise a self-standing model, or keep the understanding internal — is the distinction the
  spectrum lacks and the one that names the lift. They stay distinct: the quadrangle names which
  cognitive act; the spectrum grades how far it reaches.

## What's new (2026-09-20)

A small **wording pass** on the master report, sharpening three phrasings. The findings, theses, and structure are unchanged; only the prose is tightened.

- **The central question is phrased more honestly.** It now asks whether pre-agreement is "still required *or useful*" once the systems can reason, not merely whether it is "required" — the softer framing better captures what is actually at stake.

- **A cognition-spectrum sentence reads more naturally** — "a gap cognition *gets* stuck on."

- **The intent scenario's reproduction result is stated more clearly** — "accuracy over the full multi-step service lifecycle falls with agent capability," in place of the terser "the multi-hop lifecycle grades with capability."

The master report PDF is rebuilt to match.

## What's new (2026-09-17)

Mostly a **reframing** of the whole account, together with the **portability** experiments the reframing rests on. The findings are unchanged; what changed is the frame around them, the evidence under one half of it, and the deck.

- **The concept is reoriented around the lift.** The material now flows from the **lift** first — the cognitive act that turns a system's data into a semantic model — developed on its own terms, and only then to **reconciliation**, presented as a *key example* of cognition-based use of a lifted model rather than as the point of the exercise. The object comes before its uses; reconciliation is the flagship one.

- **Portability is now the defining attribute of a "complete" model — and it is measured directly.** A lifted model is *portable* when any sufficiently-reasoning agent can pick it up and use it from the package alone, with no pre-agreed standard, and we treat that as what makes an ad hoc semantic model complete. A block of **new experimental work** assesses it head-on rather than inferring it through a downstream task: comprehensibility across the capability ladder and across model families, what a meaning-poor surface does to it and how a reference used in the lift repairs it, and a judge-independence check. Portability comes out real, capability-banded, a property of the lift, and measured by a judge that does not favour its own family.

- **The deck is a different animal.** It is no longer a slide-by-slide mirror of the master report but a concise **enticer** — its job is to make the reader want to open the report, not to reproduce it.

- **Consistent terminology and a truer title.** The four cases are now **scenarios** throughout (master report, sub-reports, deck), and the master report is retitled ***Portable semantic models and ad hoc reconciliation by cognitive agents***, naming the object first and its flagship use second.

The master report and the four sub-reports are rebuilt to match. The portability drivers, results, and figures live under `pipeline/`, `results/`, and `figures/`.

## What's new (2026-09-15)

A focused programme drilling into the one question the four-scenario study leaves open at its own
boundary: whether the semantic and pragmatic **inputs** a reconciliation runs on can be *produced*
from the thin, real interface models a deployment actually meets — careless YANG, or REST whose data
is present but whose meaning is implicit in the application — without becoming a heavy design-time
process. Five experiments (E16–E20) settle a position, drawn together in a standalone note:

**[reports/NOTE_producing_the_inputs.md](reports/NOTE_producing_the_inputs.md)** — *Producing the
inputs: a three-route decision for thin sources.*

The position, in one line: producing the inputs is a **route decision** — lift, governed overlay, or
live elicitation, selected by whether the source is inert or cognitive — and the **governed overlay is
the robust, capability-independent route**, with the design-time burden bounded and, on this evidence,
small. What the experiments establish:

- **The overlay is the robust route (E16).** Over a deliberately thin source, a governed overlay lifts
  every tier of the capability ladder to a full close (resolved fraction to 1.00, both hard seams
  recovered, the false cognate blocked); without it the strong model defers rather than guess. Live
  elicitation is a substitute only within the band that can use it — and on a surface-similar case it is
  *less* sufficient, so the overlay is the more clearly decisive lever.
- **You cannot lift what isn't there, and confident invention is a mid-capability hazard (E17).**
  A cold-start lift recovers well while the surface carries meaning — down to keys and data with names
  and types stripped — but where the meaning is genuinely absent the strong model defers, the weak model
  abstains, and the **mid** model confidently invents. The dangerous lifter is the capable-but-uncalibrated
  middle, so an explicit insufficient-evidence path matters most there.
- **The minimum viable overlay is a name per seam (E18).** One descriptive field per entry — even just a
  name — is enough to bind; a one-line gloss earns its place only where a weaker model needs it to block a
  cognate; and coverage must be complete over the seams but not universal. The authored artefact is a short
  glossary, not a re-modelling.
- **The design-time / run-time split is drawable and bounded, and provenance is a distinct layer (E19).**
  Freeze the schema and the **provenance** — what a thing is, and who to ask; resolve live the instances and
  the pragmatics — what they currently say, and what a thing is for. Over half the seam's facts freeze,
  capable agents recover the split reliably, and they separate provenance (the source of record) from
  pragmatics (governance) cleanly — a distinction the earlier framing had blurred.
- **It is an architecture, not a YANG quirk (E20).** The same results reproduce on a case built from two
  independently published REST standards — a product-ordering interface reconciled against a
  service-ordering one — against a false cognate identical in name *and* enumerated values. The concept
  surfaces are lifted from the real specifications; only the answer key is authored.

New drivers under `pipeline/` (`inert_vs_cognitive`, `cold_start_lift`, `minimum_overlay`,
`design_run_split`, with figure scripts), a new REST case `config_rest` built from the two real
specifications, and results and figures under `results/` and `figures/`.

## What's new (2026-09-14)

This revision extends the study at the experimental end with a substantial programme of further
experiments, biting into the harder half of the problem — *producing and aligning the inputs*, not only
reconciling models that already share a reference — and replicating the sharp findings across additional
model families. The central findings are unchanged and deepened: the new results are woven into the
master report's synthesis (including a reading on producing the inputs, §13.10), and each scenario report
gains a **Further experiments** section (report 1/4 §5, report 2/4 §5, report 3/4 §6, report 4/4 §5).

- **The harder half, tested.** Independent-lexicon alignment is tractable for a capable agent
  (precision 1.00) but capability-gated — weaker models take cross-lexicon false cognates *confidently*;
  the dependency map and cross-domain authority are each shown *derivable* (from inventory, and from an
  external artefact), and reuse onboarding a new system is linear, 2.0–2.7× cheaper *and* more accurate.
  The reference's descriptive fields turn out **not** to be the precision driver — the real axis is
  lexicon divergence.
- **Cross-family replication that corrected a claim.** Replicated across three model families and two
  tiers (gpt-5.x, DeepSeek, Qwen-2.5-7B) through a JSON-mode compatibility shim: the verifier's apparent
  "capability-independent ceiling" was a gpt-5.x-family habit, while the grader's cross-framing hardness
  is family-independent. Replication told a disposition from a law.
- **Confidence made a first-class metric.** A confident-error rate, calibration gap and Brier are now
  scored and reported apart from honest deferrals; the confident wrong correspondence — the dangerous
  failure — is real, concentrated at the weak end, and confidence alone cannot filter it. An explicit
  abstain path is the remedy.
- **Robustness and honest nulls.** Cognition absorbs real vendor structural messiness (surface matching
  collapses to recall 0.33; agents recover to 0.89–1.00 at precision 1.00); contradictory authority
  sources are surfaced, not silently resolved; and, where the provider's side reduces to selecting from
  a fixed catalogue, a real second reasoning agent in the intent negotiation changes almost nothing — a
  null that scopes the "two-sided negotiation" language to scenarios where the provider must weigh its own
  deliverability, rather than retiring it.
- **The lexicon-divergence sweep.** Following up the field-ablation result, a sweep that progressively
  independently lexicalises the two sides — from a fully shared reference to two independent lexicons —
  finds **no break for a capable agent**: precision holds at 1.00 across the whole sweep, no model takes
  a planted cross-lexicon cognate at any level, and what divergence moves is only the weak model's
  confident-error rate (it roughly triples). Lexicon divergence, on this case, is not the axis that
  defeats a capable agent's alignment; a hard break, if one exists, is a question for more divergent
  domains (report 1/4 §5.7).
- **New code and cases.** New harness: `src/reconcile/compat.py` (a JSON-mode structured-output shim so
  any OpenAI-compatible provider can drive the harness) and confidence-sensitive metrics. New drivers
  under `pipeline/` (onboarding, verify_divergence, operation_necessity, escalation_analysis,
  correlation_generalization, deps_derivation, authority_derivation and authority_conflict,
  targeted_request, two_agent_intent, independent_grader, divergence_sweep, deliverability_negotiation,
  and a local/DeepSeek setup checker). New cases `config_evpn_indeplex`, `correlation_config`,
  `derive_deps_config`, `config_vendor_messy`, an `authority_source` artefact under `config_cross_domain`,
  and `underspecified_pairs`, with their builders and gold derivations. Results land under `results/` and
  the leaderboard.

## What's new (2026-09-10)

This revision brings the **pragmatic layer** to the front, shows the **lift itself** as an act of
cognition, and makes the agent-performed lift **replicable from the command line**. The central findings
are unchanged; the reports carry the results in place.

- **Pragmatics across the lifecycle — new master-report §13.9.** The report now separates the three
  layers of a lifted model by *how each is obtained from it*. The ontology's schematic layer (the
  **TBox**) and its instances (the **ABox**) are both *observed in the lifted model*: a determinate
  lookup any consumer, even a non-cognitive one, can do. Each is the frozen output of the cognitive lift
  that made it explicit, not a picture the source data model hands over ready-made; the cognition is
  front-loaded, not absent. The **pragmatics** (whether a state matters, whether an offer is acceptable,
  who decides) are *judged*, from schema, instances and context, and are defeasible and context-relative.
  The asymmetry is the point: TBox and ABox need cognition once, at lift time, and then freeze cleanly
  and read as lookup forever; pragmatics cannot be frozen cleanly and must be re-judged against the live
  context at each use.
  A static model, ours or an OWL export, holds the TBox in full and the ABox as a refreshable snapshot,
  but can only *describe* pragmatics, never carry them resolved; the section shows the OWL mapping and its
  limit. A live operation supplies them through four general mechanisms: pulling a pragmatic fact *in* by
  interrogating a live peer, *refreshing* it against the current context, *creating certainty* by a
  decisive virtual experiment, and *resolving* the verdict itself by judgement, the last being the
  capability-gated frontier. The static artefacts a system carries turn out to be *frozen outputs* of
  these mechanisms (a published reference is a frozen pull-in, a snapshot a frozen refresh, a pre-placed
  policy a frozen resolve), each valid only until the context it assumed drifts; and the mechanisms are
  gated by two things at once, liveness (which recedes across the cognition spectrum, so the mechanisms
  fall away in order as sides go inert) and capability (which bites hardest on resolution). This is why
  the framework does not merely extend beyond reconciliation but predicts the other scenarios' signatures,
  the observability verdict being capability-gated while its correlation, a structural test, holds across
  the ladder. The point is carried through the rest of the report: §14's second map gains a note tying its
  **Lift** and **Pragmatic-resolution** rows to §13.8 and §13.9, and the one-paragraph close (§17) now
  states it.
- **The lift, shown and performed — extended §13.8.** Three things land in the lift section. A *concrete
  lifted model* is now printed in full (§2 shows one complete concept as JSON, with a note that the shape
  is encoding-agnostic), so "what exactly is in a lifted model?" has a definite answer. A *lift-in-the-act*
  trace box shows the agent naming its own per-concept evidence on the relabelled control, where the
  recognisable names are replaced by invented ones so only the structure remains: the agent names the
  surface signals it used and the look-alikes it ruled out, confirming the reading is structural, not
  recalled. And the agent-performed lift is run *lift-only across eleven schema cases and the whole model
  ladder*: coverage is complete and structure intact at every rung, every false-cognate trap is caught
  (the relabelled control included), and the differences are of verbosity, not accuracy — so §16 gains a
  clause that lift correctness is robust across the ladder.
- **New code, and the replicable work it supports.** The agent-performed lift is now a first-class,
  reproducible entry point. `pipeline/lift_study.py` gains `--lift-only` (produce the lift without running
  reconciliation), `--cases all` (discover and run every schema case), and `--trace` (record the agent's
  stated per-concept evidence); `src/reconcile/lift.py` gains the trace mode, and `src/reconcile/model.py`
  a `to_dict()` that serialises a lifted model back to the case JSON shape, with offline tests added under
  `tests/`. Running `pipeline/lift_study.py --lift-only --cases all` over the three-model ladder is what
  produced the eleven-case result above; the lifted models it emits are committed under
  `results/agent_lifted_models/` so the finding can be inspected and rebuilt.
- **Figures and deck updated to match.** Figure 1 now labels the ontology's schematic and concrete layers
  as the **TBox** and the **ABox**, tying the opening picture to §13.9. The constructed scaling chart
  (former Figure 11) is dropped — it was not a peer to the measured figures and its point is made in the
  text — and the later figures are renumbered. The master slide deck carries the new material: the
  pragmatics-across-the-lifecycle distinction, the four operation-time mechanisms, and the lift in the act.

## What's new (2026-09-08)

This revision deepens the fully-cognitive end and adds two controls. As before, the central findings are
unchanged and the reports carry the results in place; this note is for readers tracking what moved.

- **Completion by decisive experiment, shown end to end.** At the fully-cognitive end, when the two agents
  cannot settle a correspondence by discussion, either can provision the candidate in a private virtual copy
  of the network, operate it, and read back whether it holds; the verdict binds or refutes. With this, two
  agents reach the reference's close on three of the four schema scenarios with no reference at all, and the
  master report now includes verbatim transcripts of the negotiation and of the experiment. (See §13.7.)
- **The lift, performed by an agent.** The study reconciles lifted models whose explanation layer, each
  concept's gloss and worked example, had been supplied ready-made. An agent is now asked to produce that
  layer itself from a side's bare schema, and reconciliation over the agent's own lift matches the
  ready-made one: identical for the capable agent binding through a reference, across all four scenarios. So
  the results do not depend on the lift being authored in advance; what stays open is the lift from raw,
  messy schema and a cold start before any instances exist. (See §13.8.)
- **A memorisation control.** The flagship TAPI/TEAS case is re-run with the public-standard identities
  stripped and relabelled, to separate reasoning from recall of a known standard: reasoning alone reaches a
  resolved fraction of about 0.67 where the recognisable case reaches 1.00, and a shared reference restores
  1.00 either way. (See §16.)
- **Slide deck refreshed** to carry the negotiation, the decisive experiment, and the lift study.

## What's new (2026-09-05)

This revision strengthens the study in-house — the central findings are unchanged and hold — and
closes the in-house gaps the first cut left open, leaving only the genuinely external one (real
network data). The reports carry the results in place; this summary is here for readers tracking what
moved between revisions.

- **Construct-then-bind, end to end (scenario 3).** The standard-free scenario previously handed the
  agents the shared reference and scored the binding alone. The agents now **build that reference
  themselves** from the two models and then bind through it, with nothing pre-given. The strong agent
  lifts from a no-reference resolved fraction of **0.20 to 0.80** (0.90 with a decisive experiment), near
  the reference-given 1.00, at perfect precision and with no false cognate. Constructing the shared ground
  works, and building it is the work.
- **A six-model capability sweep.** Swept across six models at both-cognitive, two-agent negotiation
  **compresses** the capability gradient: bilateral ratification holds precision high and drives false
  cognates to zero across almost the whole ladder, while resolution is uniformly lower. The discipline a
  lone weak agent would lack is supplied by the negotiation structure itself.
- **Instance co-reference measured beyond scenario 1.** Entity-level co-reference is now measured in
  scenarios 2 and 4 as well, reproducing the budget-limited-then-structural pattern: capable agents
  resolve fully where a live side can be interrogated, the weakest only partially. (A fix to the
  interrogation path — letting an agent ask which attributes exist rather than guess field names —
  moved scenario 4 from a floor to full resolution.)
- **A classical descriptor baseline.** A non-cognitive matcher (labels, glosses, structure) is included
  as an explicit baseline, confirming that descriptor methods carry a reconciliation to a ceiling that
  cognition then passes.
- **A reach study — what an agent can see and what it can ask.** Holding the strong agent at its best,
  we vary two things independently: how much of a record it may *see* (from a bare key up to full
  topology) and what it may *ask* of the live system (nothing; a named attribute; the open question
  "what facts do you have?"; a full virtual experiment). Seeing more, on its own, caps the hardest
  cases at one-half. The hinge is the open question: being able to ask what exists — rather than having
  to name the field in advance — takes the reconciliation to a full, correct close. Run down the model
  ladder, the same access lands by capability: the strong agent converts it to a full close, the mid
  plateaus, and the weakest posts high resolved fraction but with slipping precision. (See §13.5 of the master
  report, Figure 14.)
- **Breadth — every signature reproduced on new cases.** Each of the four scenarios is now exercised on
  **three independently-built cases, not one** — two new ones per scenario, in different domains, with
  different vocabularies and different traps. Every signature reappears: cognition completes the match
  while the reference mainly prevents the weaker agents' errors (configuration); the strong-omit /
  weak-commit mirror, repaired by a thin reference (standard-free); refinement and negotiation completing
  while the multi-hop lifecycle grades with capability (intent); and the alarm-is-not-an-anomaly
  look-alike reliably told apart (observability). This closes the "you only showed it on one case"
  worry as far as in-house work can. (See §16 of the master report, Figure 16.)
- **The economics of the reference — when constructing it is worth the cognition.** Building the shared
  reference is itself an act of cognition, so we measured its cost against what it buys. The rule: it is
  load-bearing only where **no standard exists and the agent is capable** (standard-free, strong agent:
  resolved fraction 0.20 → 0.80, and 0.90 with a decisive experiment, for a little extra spend); where a
  reference already exists (configuration,
  observability) the **given** reference reaches the same close for a fraction of the cognition, so
  constructing one is **redundant**; and for a **weak agent it is counterproductive** — construction cost
  explodes (to tens of thousands of reasoning tokens) for a worse close, not a better one. So construct-then-
  bind is not a blanket default: build the reference where there is none to bind through and the agent can
  build a good one; otherwise use the one that exists. (See §13.6 of the master report, Figure 15.)
- **Benchmark packaged.** The cases, harness, and leaderboard are packaged under `benchmark/` for
  external use — now eighteen cases across the four scenarios.

What remains is now genuinely external: larger and more varied cases drawn from real networks, and the
real-data grounding that only carrier and standards-body collaboration can supply. The breadth cases
above are still authored by the same hand, so they test robustness to *variation*, not to *real* data —
which is exactly the gap that external collaboration exists to close.

## Repository layout (`study/`)

```
reports/                      the deliverables
    MASTER_REPORT.md              the synthesis — start here
    REPORT_1of4_configuration.md  scenario 1 · configuration (TAPI ↔ TEAS)
    REPORT_2of4_intent.md         scenario 2 · intent (refinement, negotiation, lifecycle)
    REPORT_3of4_standard_free.md  scenario 3 · standard-free (no standard)
    REPORT_4of4_observability.md  scenario 4 · observability (alarm ≠ anomaly)
notes/
    studies/                  scenario-1 method notes (lift baseline, reference anatomy,
                              instance disambiguation, verification modes)
    design/                   design notes of record, per scenario
    archive/                  superseded working notes
    SETUP_OPENAI.md           how to supply the API key (kept out of the repo)
figures/                      all report figures (regenerated by pipeline/figures*.py)
src/reconcile/                the harness: models, reference, metrics, stacks, oracles
benchmark/                    case builders and cases/ (two lifted models, reference, traps, gold)
results/                      the exact per-run data behind every figure and table
pipeline/                     all runner, figure, and build scripts
tests/                        offline tests of the stacks and scoring (no API)
pyproject.toml
```

## Quick start

Run from the `study/` directory. The controls, gold derivations, offline tests, figures, and PDF build
need no model access (standard-library Python plus `matplotlib`/`markdown`/`wkhtmltopdf`). The
language-model runs need `openai` and an API key — see
[notes/SETUP_OPENAI.md](notes/SETUP_OPENAI.md) — and reach `api.openai.com`, so they run where that is
available.

```bash
cd study

# deterministic, no API:
python pipeline/run.py --case config_big_hard --no-write     # controls only
python pipeline/scaling.py --max-n 12                         # the scaling result
python -m pytest tests/                                       # offline tests
python pipeline/figures_master.py                             # regenerate the master figures
python pipeline/build_pdfs.py                                 # rebuild every report PDF

# the language-model studies (need OpenAI; run where api.openai.com is reachable):
python pipeline/run.py --case config_big_hard --agent --trials 4 \
  --placement both_cognitive,one_inert,both_inert \
  --model gpt-5.6-sol,gpt-5-mini,gpt-5-nano
python pipeline/intent_study.py     --model gpt-5.6-sol,gpt-5-mini,gpt-5-nano
python pipeline/pragmatics_study.py --model gpt-5.6-sol,gpt-5-mini,gpt-5-nano
python pipeline/observability_study.py --model gpt-5.6-sol,gpt-5-mini,gpt-5-nano

# the agent-performed lift, on its own, across every schema case (dumps each lifted model to JSON;
# add --trace to record the agent's stated evidence per concept):
python pipeline/lift_study.py --lift-only --cases all --model gpt-5.6-sol,gpt-5-mini,gpt-5-nano
```

Per-scenario run commands are in each report's Reproducibility section, and the method notes under
`notes/studies/` carry the sub-study commands.

## Grounding and scope

The study operationalizes and empirically tests the claims of the [proposal](../proposal/): the IRTF
NMRG work on agentic network-as-a-service negotiation, the cross-domain provisioning demonstration, and
the IETF NMOP anomaly/alarm model (RFC 9940). The claims are **existential and mechanistic** — *this is
how ad hoc reconciliation works, and here it is working* — established on single, seeded cases built to
exercise each mechanism and prove each trap, across the model ladder; they are not population estimates.
What remains is now external: larger and more varied cases drawn from real networks, and the real-data
grounding that only carrier and standards-body collaboration can supply.

*Choose a license before publishing.*
