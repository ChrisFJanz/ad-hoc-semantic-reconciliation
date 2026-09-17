# Part 1 — The lift, and the portable model it produces

*(Draft to replace the current Part I. Portability-first spine, per the rewrite plan: the lift is
treated whole here, and reconciliation follows in Part 2 as its hard dyadic use. Narrative mechanics
follow the report-narrative brief — question-headed sections, one-line stakes, headline findings set
off as pull-quotes, two reading depths. Numbers are final as of the completed Part-1 evidence set.)*

---

## 1. The burden, and a question worth asking

Two software systems that must exchange information rarely share a model of the world. The scope a
model must cover is not fixed, the useful level of abstraction depends on the task, and capable
engineers, working independently, produce different but defensible models of the same network. The
classical remedy is a universal standard agreed ahead of time: everyone adopts one vocabulary, and the
reconciliation is done once, by committee, before the systems ever meet. That remedy is expensive,
slow, and permanently behind the systems it tries to govern — a standards quest that never quite ends,
because the world it models keeps moving.

So it is worth asking a question that, until recently, would have sounded naive: **do two sufficiently
capable systems need a data model agreed in advance at all — or can they produce a suitable one
themselves, for the occasion?** The question is not whether models stop mattering. It is whether the
*pre-agreement* — the part that is slow and expensive — is still required now that the systems on each
side can **reason**.

This has to be asked with both feet on the floor. The installed base is enormous and mostly inert:
decades of systems that cannot explain themselves, data of mixed and often poor quality, and
high-reliability operations that must keep working in all circumstances. Nothing here proposes razing
that. The claim this programme investigates is narrower and, we will argue, more useful: that
production of a shared understanding, and agreement upon it, can increasingly be done **ad hoc** —
between the systems, for the task at hand, machine-to-machine — lifting the pre-agreement burden while
coexisting with the legacy it cannot replace. The answer we reach is *yes, with nuance*, and the
nuance is where the credibility lives.

Everything in Part 1 is about the object that makes an affirmative answer possible: a semantic model
that can stand on its own. We first say precisely what "stand on its own" means, then how such a model
is produced, then whether it actually holds up when handed to a cold reader. Part 2 takes up the hard
case — two such models that must be made to work together — and shows it to be the same story under
strain.

## 2. What would it mean for a model to stand on its own? Portability

The concept the whole programme now turns on is **portability**, and it is worth defining before
anything else, because everything downstream is either its production, its measurement, or its repair.

> **A lifted model is *portable* when any agent of sufficient reasoning power — reasoning, not prior
> domain knowledge of the system — can make arbitrary use of it without seeking clarification that does
> not lie within the package, allowing that live parts (current values, present state) may need
> refreshing.**

Four things in that definition carry weight, and each draws a boundary the programme keeps running
into.

Portability is **monadic** — a property of *one* lifted model, produced by *one* lift. Model A is
portable if an arbitrary cognitive agent can comprehend and use it; that is true or false about A on
its own, before any second system exists. Testing it needs a consumer, but the consumer is any
*separate* agent brought in only to probe A — a planner, an auditor, a human — not a peer that also
carries a model. This matters because it locates the primary object. The two-system dance most of this
programme's prior work studied belongs to *reconciliation*, a downstream operation; portability is
what each side brings to it.

"Reasoning, not knowledge" is what keeps the definition from collapsing into circularity. A
sufficiently-reasoning agent *derives* the model's meaning from the package; it does not check the
model against pre-held concepts of *this* system, because it holds none. The bar is a reasoning
*threshold*, universal above it, not a store of insider familiarity. This is the *ad hoc* point of the
entire study restated as a property: no pre-shared standard is required, only a competent reader.

"Without clarification outside the package" carves off the one thing portability honestly does not
cover. Updating a value the package already declares — reading a live counter, refreshing present
state — is not external clarification; a portable model can have live parts. But an **authority fact**
— *whose right it is* to set a contested value — is a clarification that genuinely does not lie within
the package. It is a fact about the world's governance, not about what the model means, and it stays
where the owning authority lives. The frame has a clean edge: it is self-sufficient for what a model
*means* and how to *use* it, and rightly not self-sufficient for who *governs* it.

The payoff of defining portability this way is that it reframes capability. Anchoring a model does not
add knowledge to the reader; it **lowers the reasoning threshold** needed to use the model. A
self-anchored package is usable by a modest reasoner; a bare one demands a strong reasoner to
reconstruct the meaning — and, as the measurements will show, a middling reasoner will confabulate it.
The whole capability story of this programme becomes one statement about portability: the better the
lift, the less reasoning the consumer must supply.

## 3. How is a portable model produced? The lift

Portability is produced by the **lift**, the move the whole programme turns on (Figure 1).

A system usually holds its content as a **data model**: a schema and its records as they sit in a
database or a controller. That content is already a partial semantic picture, but a fixed one, frozen
by the format it uses: a field named `och_grade` with values `1`, `2`, `3` is legible to the software
and engineers built around its schema, yet says nothing, on its own, to a consumer that was not told
what it means; the meaning lives in a specification and in shared convention, outside the data itself.
The **lift** is the move from that to a **semantic model**: the same content given grounded, explicit
meaning, structured as three parts. First, an **ontology**, which includes its **lexicon**: a
schematic layer (the concepts, their kinds and relations, and the preferred labels and synonyms that
name them) and a concrete layer (the individual instances that populate those concepts). Second,
**pragmatics**: the contextual information a consumer needs (what a thing is for, whose authority
governs it, in what context it holds). Third, **provenance**: who asserted each part, by what method,
and how firmly. The lift itself is a **cognitive act**, helped along by a few **supports** that are
aids to that cognition rather than parts of the model: definitions, worked examples, a canonical
example, and an optional link to a shared reference. Who performs that cognitive act — and what
happens to the lift as the available cognition shifts — is a spectrum in its own right, taken up in §4.

![The lift — a data model becomes a portable, self-describing semantic model.](../figures/fig_master_lift.png)

*Figure 1. The lift. A data model (schema plus records) is a partial semantic picture, fixed by its
format, with much of its meaning left implicit: in specifications, convention, and the engineers who
built around it. The lift is a cognitive act, aided by a few supports (definitions, worked examples, a
canonical example, an optional linked reference), that turns the data model into an ad hoc semantic
model built from three parts: an ontology including its lexicon (a schematic layer of concepts, kinds
and relations, the TBox, and the concrete instances that populate them, the ABox), pragmatics (use,
authority, context), and provenance. Being self-describing, the result is portable: any cognitive
consumer can pick it up and understand it, with no pre-agreed standard.*

The payload of the picture is the word **portable**. A lifted semantic model is **self-describing**,
and being self-describing is exactly what lets any cognitive consumer — this agent, another agent, a
human — pick it up and understand it without a prior agreement. That is not a convenience; it is the
precondition for the whole approach. Every cognitive use of a model — reasoning over it, planning with
it, auditing it, reconciling it with another — requires meaning made explicit, and the lift is how
meaning is made explicit on demand rather than by standardisation. Reconciliation, the subject of Part
2, is one such use; the settings that follow also refine an intent against a catalogue and read an
anomaly for its significance, all over the same lifted substrate. Get the lift, and the rest is
operations over portable semantic models.

To make this concrete, here is one concept of a lifted model, the TAPI connectivity-service from the
flagship configuration case (a model is the list of such concepts under a short header):

```json
{ "id": "t.cs", "label": "connectivity-service", "kind": "service",
  "synonyms": ["service"], "ref": "connection-service",
  "gloss": "an end-to-end connectivity service across the network",
  "example": "the A1-A3 ODU2 service",
  "relations": [ {"rel": "uses", "target": "t.sip"},
                 {"rel": "realized-by", "target": "t.cep"},
                 {"rel": "over", "target": "t.topo"} ],
  "instances": ["cs-a1a3-odu2 (ODU2, A1 to A3)"] }
```

The fields carry the lexicon (label, synonyms), the ontology (kind, relations), the concrete layer
(instances), the explanation supports (gloss, example), and the binding to a shared reference (ref); a
live side volunteers gloss and example, an inert side exposes only the structural fields. The content
is independent of its serialisation: shown here as JSON, the same model emits just as readily as
OWL/RDF, which is also how a deterministic pipeline that compiles a formal schema (such as YANG) to an
ontology carries it. What such a compiler cannot supply, and what the cognitive lift adds, is the
pragmatic and explanation layer the schema does not contain.

One framing connects this work to a fast-growing body of practice. The ontology and the individuals
that populate it are, together, a **knowledge graph**: the ontology is its schema (the typed concepts
and the relations permitted among them) and the instances are its assertions. This is why the
community's knowledge-graph work for network operations, and the AI-facing modelling interfaces now
emerging, meet this approach squarely: a lifted semantic model is a knowledge graph a machine can
consume, and a thin shared reference is exactly the kind of interoperable anchor such graphs can bind
to. What the semantic model adds beyond the bare graph is the pragmatic layer and the provenance base —
and, as the findings will show, exactly the facets a thin reference cannot supply on its own.

## 4. The lift is a cognitive act — where that cognition lies, and what limits it

Calling the lift a cognitive act forces the question of *whose* cognition performs it, and what
happens to the lift as that cognition thins. This is a spectrum on the **production** side — distinct
from the cognition spectrum that governs reconciliation in Part 2 — and it decides both how the lift is
done and how far it reaches.

At the richest end, the source system is itself live and cognitive and **lifts itself**. It authors
its own meaning — volunteering glosses, worked examples, the intent behind a field — because it is the
authority on what it holds. A self-lift depends least on anything outside it: the meaning is put in at
the source, by the party that knows it.

Where the source is **inert** — a mute schema and its records, unable to explain itself — the cognition
must come from **a machine agent that reads it**, reconstructing meaning from the surface: labels,
kinds, structural relations, and instances. This is not hypothetical. §13.8 has an agent produce the
lift from the schema surface alone, and the downstream results hold where the study leans on them: a
capable reader recovers a portable model from an inert source. But this reading is **bounded by what
the surface carries**, and §6 measures that bound directly — as the surface goes meaning-poor, the
portability of the recovered model falls, and, in the sharpest form of the finding, a surface that
keeps a concept's *name* but not its meaning is no safer than an anonymous one, because a bare name
invites the reader to confabulate a sense for it.

At the far end — wherever machine cognition is absent, insufficient, or facing a question it cannot
settle — **a human** performs or completes the lift, as engineers have always modelled systems by hand.
And one part of the lift never leaves the human at all: the **authority layer**, who has the right to
set a contested value, is not a meaning to be recovered but a fact about governance, so even a fully
automated lift defers there. It is the same residue §2's definition carved off, now seen on the
production side.

The through-line is a single limit: **the lift recovers as much meaning as the cognition performing it
can bring to bear on the material in front of it** — abundant when a live source explains itself, ample
when a strong agent reads a rich surface, thinning as the source goes inert, the surface goes
meaning-poor, or the agent goes weak. Where the recovery falls short, the shortfall must be supplied
from somewhere. That somewhere is the reference.

## 5. The reference: how critical it is, and where it comes from

A reference is what supplies the meaning a lift cannot recover on its own. Part 1 insists on reframing
what it *is*: not a **reconciliation device** but a **common-ground anchoring device** — it ties a
model's local terms to ground a competent reader already holds, which is useful to *any* consumer, not
only to a second model. It is deliberately small: a flat set of entries, each an identity anchor plus a
few descriptive fields (a label and synonyms, a shallow class, a one-line definition, a canonical
example). It has no ontology of its own — giving it one would turn it back into the universal standard
the approach exists to avoid — and it is **parasitic** on the grounded models it anchors, which is
exactly why it can be so thin. Two independent things about it then matter, and conflating them has
caused confusion before: *how critical* it is, and *where it comes from*.

**How critical it is — and this tracks the lift-cognition spectrum of §4.** The reference is not
uniformly important; its criticality is highest exactly where cognition is weakest. When a strong agent
lifts a rich source, the model comes out self-describing and the reference is nearly redundant — the
baseline in §6 shows a solid lift staying portable with the reference *withheld* at consumption. When
the source is inert or its surface is meaning-poor, the reference becomes the thing that makes the lift
portable at all — §6's degradation result has a reference used *in the lift* pulling a broken lift back
from 0.64–0.74 to 0.79–0.85. The same shape appears on the consumption side across the reasoning
ladder: a strong reader needs no glossary, a weak one is rescued by it. One anchor, its value
concentrated wherever the cognition around it runs thin.

**Where it comes from — a second, independent spectrum.** A reference may be *pre-existing* — an
authored standard taken off the shelf — or *constructed by cognition as part of the lift itself*, where
no standard exists (the construct-then-bind result, §13.6), with the middle ground of adapting or
extending an existing reference to fit. That cognition can manufacture common ground at all is not
mysterious once portability is the frame: common ground is not a formal shared ontology but what
competent agents already hold in common, and they hold a great deal. This is also why anchoring is
**capability-independent** in a way live elicitation is not — it meets a reader where it already stands
rather than requiring it to be clever — and why the constructed reference is load-bearing precisely in
the standard-free settings where nothing is on the shelf to reach for.

**When it acts** brings the two spectra together, and here one apparently natural case drops out. A
reference can act at *production* (used by the lifter, while the model is built) or at *consumption*
(handed to the reader alongside the finished model), giving three meaningful conditions — no reference
at all; a reference used *in the lift only* and withheld at consumption; and a reference *in the lift
and at consumption*. The fourth — a reference at consumption but not used in the lift — has no
capability-independent value: it would help only a reader strong enough to reconcile the raw model
against the reference itself, and such a reader did not need help. A reference earns its keep at
**production**. This sharpens the portability criterion into something testable: a good lift
**dissolves** the reference into each concept's own description — the concepts become self-describing,
so the reference need not travel with the model — whereas a poor lift leaves only dangling pointers
that go slack the moment the glossary is withheld. The middle condition succeeding, the model
comprehensible with the reference used in the lift but *withheld* at consumption, is precisely the test
that portability was baked in rather than bolted on. It is the measurement Part 1 turns on next.

## 6. Does it actually work? Assessing comprehensibility

A claim that lifts produce portable models is empty unless portability can be measured directly,
decoupled from any downstream use. It can, and the rest of this section is the evidence.

**The instrument.** We turn the definition into a measurement by assessing **comprehensibility**: the
share of a model's concepts that an independent agent can correctly explain *from the package alone*.
One lifted model is handed to a **consumer agent** of a specified reasoning tier that did not author
it and holds no insider knowledge of the system. The consumer explains each probed concept in its own
words; it is explicitly permitted to answer that it *cannot determine* the meaning from what it was
given, because an honest abstention is a desired response, not a forced guess. A fixed strong **judge**
— one model held constant across the study — grades each explanation by *meaning, not wording* against
an authored answer key, returning one of four verdicts: **faithful** (captures the true meaning),
**partial** (right direction, hedged), **abstained** (honestly declared undeterminable — a virtue when
the meaning is genuinely absent), or **invented** (asserts a meaning the key does not support, for
instance by taking a planted cognate — the confabulation hazard the measure exists to catch). From the
per-concept verdicts we report three fractions: **meaning_score** (fraction faithful — the
comprehensibility measure), **abstention_rate** (honest deferral), and **confabulation_rate** (the
hazard). The consumer runs across a **reasoning ladder** — a strong (`sol`), a mid (`mini`), and a
weak (`nano`) model — chosen to isolate reasoning strength rather than provider or architecture. The
full protocol, ground-truth authoring, and worked examples are in the methods section.

The findings below are stated once as headlines, then supported. Read the headlines for the story; the
paragraphs beneath carry the evidence.

> **A solidly lifted model is comprehensible to strong, middle, and even weak reasoners from the
> package alone.**

On a solid lift with no reference at consumption, meaning_score across the ladder is near the ceiling
and softens only on the hardest material: on the cross-domain seam, `sol` 1.00 / `mini` 0.87 / `nano`
0.73; on the large, deliberately hard case, 1.00 / 0.94 / 0.89; on the routine case, 1.00 / 1.00 /
1.00. Even the weak reasoner comprehends a good lift from the package alone — perfectly on routine
material, around 0.9 on hard material, softening to 0.73 only on the very hardest. Portability holds
nearly capability-independently, a soft gradient on hard material rather than a floor. The consumption-
time reference, added on top, is a small and capability-dependent top-up exactly where the bare lift
fell short (cross-domain `mini` 0.87→1.00, `nano` 0.73→0.93) and does nothing where the lift already
sufficed. The reference did its real work at lift time.

> **The result holds across six independent domains, not one.**

The same assessment run over three further settings — carrier-Ethernet service, fault/observability,
and L3VPN — returns bare meaning_score 0.98 and anchored 1.00 in every one, with confabulation near
zero, matching the original three. "Solid lifts are portable" rests on six domains spanning
configuration, cross-domain, and observability, not on a single worked case.

> **Portability is not an artefact of one model family — it tracks reasoning, not lineage.**

The most direct objection to a within-family result is that a model is simply reading its own kind of
output. To close it, we held the *judge* fixed on the original family and varied only the *consumer's*
family. A foreign strong model (DeepSeek) comprehends the same lift cold — bare 0.98, anchored 0.96,
confabulation near zero — matching the in-family strong tier and beating the in-family weak tier's
bare 0.87. An open weak model (Qwen-2.5-7B) does markedly worse — bare 0.56, anchored 0.69 — and
confabulates: its per-trial scores are bimodal, either nailing a case or missing it entirely. That
contrast is the point, not an embarrassment. Portability is **capability-banded**, and the band is set
by reasoning power, not by family: a foreign *strong* reasoner ports as well as the home strong
reasoner, while a *weak* reasoner is unreliable regardless of lineage — exactly what the operational
definition predicts, and the honest floor beneath the claim.

> **Portability is a property of the lift: a meaning-poor surface breaks it, and a reference used in
> the lift repairs it.**

Holding the lifter fixed (so any change is the surface, not the lifter), we lift from progressively
poorer surfaces and re-assess. Against a solid-lift baseline of 0.94, stripping the meaning-bearing
surface and lifting without a reference drops comprehensibility to 0.64–0.74 — the negative control
that keeps the claim honest: lifts *can* fail to be portable, and we can say when. Lifting the same
poor surface *with* a reference restores it to 0.79–0.85 at every level of degradation, and having the
reference again at consumption adds almost nothing beyond that — the reference does its work at
production, once more. This is portability repair on the production side: where the surface is too thin
to carry meaning, cognition rebuilds the common ground from the reference during the lift and bakes it
into the result.

One degradation finding is sharp enough to keep visible, because it corrects an intuition:

> **A bare name is a trap. It is not the *amount* of surface that makes a lift portable, but whether
> the surface carries meaning.**

The degradation is *not* monotonic in how thin the surface is. A surface that keeps concept *names*
but strips their glosses is no safer than a fully opaque surface of anonymous identifiers and raw
instances — if anything slightly worse (0.64 versus 0.74), consistently across all three reasoning
tiers. The reason is clean: a bare name with no meaning behind it *invites confabulation* — the lifter
reads a plausible-but-wrong sense off the label — whereas opaque identifiers with concrete instances
give the lifter grounding and no misleading name to over-read. A name is not meaning; a name without
meaning behind it is a hazard.

Finally, the measure itself must not be a house artefact:

> **The comprehensibility metric is judge-independent.**

Freezing each consumer answer and grading it with *two* judges — the home strong model and a
cross-family model — leaves the reported meaning_score identical (0.900 versus 0.900). The judges agree
on 90% of individual faithful/not-faithful calls and never once disagree on the clear cases (no answer
one judge calls faithful the other calls a fabrication); the residual disagreement falls entirely on
the weakest consumer's hedged, borderline answers and cancels in aggregate. (A raw four-label Cohen's
κ of 0.27 looks low but is the well-known κ-paradox of a 90%-prevalent label; the binary κ is 0.44,
and the identical scores and absence of clear-case disagreement are the load-bearing evidence.) The
metric is not lenient toward its own family — neither on the consumer side nor on the judge side.

Taken together, the picture is deliberately unglamorous where glamour would cost credibility.
Portability is real (the baseline), broad (six domains), family-independent (the foreign strong
reader), capability-banded with an honest floor (the weak open model) and an honest failure mode (the
meaning-poor surface), repairable by a reference baked into the lift, and measured by a
judge-independent metric. Every limit doubles as a credibility signal: cognition here is powerful and
bounded, and knowing exactly where it is bounded is what makes the powerful part usable.

## 7. When is a portable model hard to reuse? The bridge to reconciliation

If a single lift can be made portable, the obvious next question is what happens when *two* portable
models must be made to work together across a seam — the same product modelled commercially on one
side and technically on the other, a circuit that underlies a service, an alarm that is not quite an
anomaly. That is **reconciliation**, and it is the subject of Part 2.

The through-line that keeps this one argument rather than two is worth stating here, because it is what
Part 2 rests on. Reconciliation is a **dyadic operation** — each system consumes the other's model, and
each remains the authority over its own — but the consumption underneath is the *same monadic
portability* measured in this Part, applied twice and coupled by authority. And it is hard in a very
specific way:

> **Reconciliation is hard exactly to the degree the lifts fell short of full portability. The
> reconciliation machinery — the reference, construct-then-bind, active verification — is portability
> repair.**

Two *fully* portable models would reconcile almost trivially: each consumes the other, finds the shared
ground already present in the self-describing concepts, and the binding falls out with nothing to
negotiate. Difficulty appears precisely where the lifts are meaning-poor, locally anchored, unbridged —
and the machinery this programme built for reconciliation is, seen from Part 1, the same repair that a
reference-in-the-lift performs, now carried out interactively between two systems. That reframing makes
portability *more* primary, not less: the difficulty of the dyadic operation is a diagnostic of a
monadic shortfall. It also locates the one thing repair cannot reach — the authority to decide *whose*
value governs — which is the governance residue Part 1's definition already carved off, now appearing
as the irreducible human or authoritative act at the end of an otherwise autonomous process.

Part 2 opens with the landscape of reconciliation uses — where models diverge, and what each kind of
divergence needs — and then works through the operations and the evidence, over the same instrument and
the same reasoning ladder established here.
