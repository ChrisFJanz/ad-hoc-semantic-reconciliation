# Producing the inputs: a three-route decision for meaning-poor sources

This note addresses the one question the reconciliation study leaves open at its own boundary. The
study shows that a cognitive agent completes an ad hoc reconciliation *given* the lifted semantic
models it reconciles. It does not, on its own, settle whether those inputs — the semantic and, where
it matters, the pragmatic content — can be *produced* reliably from the meaning-poor, real interface
models a deployment actually meets, and whether producing them is a bounded step or a heavy design-time
undertaking. Real interface models are often meaning-poor: YANG with careless or convention-bound
descriptions, and REST whose payload is present but whose meaning lives in the application and the
operators rather than in the interface representation. If the deployment story were "statically lift
every interface, in full, ahead of use," the worry would be well founded, because no extraction
recovers what a representation does not contain. This note sets out the position the study's own
architecture implies, and reports the experiments that test it. The short form: producing the inputs
for a meaning-poor source is a **route decision** — surface lift, reference, or live elicitation — and
the **reference** is the robust, capability-independent route, with the design-time burden bounded and,
on the evidence here, small — and the reference itself is, where no standard exists, buildable by
cognition rather than only authored by hand.

## The lifted model is not one thing

The premise that the production question is heavy rests on treating the lift as a single design-time
extraction of "the complete semantic and pragmatic input." The semantic-model architecture does not
treat it that way, and the distinction is what dissolves the worry. A lifted model has four layers:
the **schematic** ontology (concepts, kinds, relations — the TBox), the **instances** that populate
it (the ABox), **provenance** (who asserts, realises or measures each part — the authoritative source
of record), and **pragmatics** (what a thing is for, whether it can be delivered now, the use-context).
Two of these are fixed in the representations and can be extracted once, ahead of use, and relied on:
the schema and the provenance — *what a thing is*, and *who to ask*. Two are not fixed and must be
resolved at run time: the current instance values, which drift, and the pragmatics, which reflect
present state, capacity and intent. The "significant design-time process" is only unavoidable if one
demands that the run-time layers be frozen into a static artefact, which the architecture holds one
neither can nor should do. Producing the inputs is therefore not a single excavation; it is a
design-time part that is genuinely bounded, over a run-time part that is genuinely live.

A word on provenance, because the study's earlier framing blurred it. What was described as pragmatic
"authority" — whose realm governs a seam field — bundles two different things. Which realm has the
*right* to set a value is governance, a pragmatic question; but which system is the *authoritative
source of record* for it, who realises or measures it, is provenance. The two coincide in cases where
the realm that governs a field is also the one that realises it, which is why the distinction went
unremarked; they are not the same, and the source-of-record half is what freezes. The confidence
apparatus the study already reports — the confident-error rate, the calibration gap, honest deferral —
is the other slice of provenance, the "how firmly" a thing is asserted. Provenance, in short, is not
an untouched layer but a half-built one; naming it sharpens the design-time / run-time line to its
final form: **freeze the schema and the provenance; resolve live the instances and the pragmatics.**

## Where the meaning is absent: two goods, three routes

Where the meaning a reconciliation needs is genuinely not in the meaning-poor representation, no
extraction recovers it — and the routes to supplying it divide cleanly once one sees that a
reconciliation needs **two different goods**, not one. Keeping them apart is what makes the route
decision legible.

The first is **(A) each side's own meaning**: what a given concept denotes, on its own terms. The
second is **(B) the shared category that authorises a cross-side binding**: the connective tissue that
licenses "this thing here *is* that thing there" and, in the same act, blocks the false cognate. These
are different goods, and the study's own results already separate them — a shared reference was found
to do two jobs at once, *supplying meaning* and *pre-empting false cognates by shared identity*. Those
two jobs are (A) and (B).

Two of the three routes supply good (A), and differ only in where they read it from. **Surface lift**
recovers each side's meaning from the inert representation directly — names, keys, structure, whatever
descriptions exist — with the reconciler getting no help from a live source; it is the route for a side
that is inert but whose surface happens to carry enough. **Live elicitation** recovers the same good (A)
by interrogating a live agent behind the interface, where the system is itself cognitive; the meaning is
supplied on demand and never needed to sit in the static representation. Which of the two is available is
fixed by whether a side is inert or cognitive — elicitation needs an agent to ask — but both deliver the
same thing: the source's own meaning.

The third route, the **reference**, is the only one that supplies good (B). The missing shared category
is authored once, as a bounded external artefact both sides bind to — the study's thin published
reference, generalised. Because it is a third thing, external to both sides, its availability does not
depend on whether the sources are inert or cognitive; and because it carries the shared identity, it
supplies the authorisation that neither surface lift nor elicitation provides. (It also carries
descriptive fields, so it supplies part of good (A) as well; but its load-bearing, distinctive
contribution is (B).)

So the cognitive spectrum — both sides cognitive, one inert, both inert — gates only *which route
delivers good (A)*: elicit both sides when both are cognitive; elicit the live side and surface-lift
the inert one when one is inert; surface-lift both when both are inert, with honest deferral where a
meaning-poor surface yields too little. **Good (B) sits outside that spectrum**: the reference supplies
it in every placement, a reconciler strong enough may in some cases infer it, and — as the experiments
show — cognition can in some cases *build* it. The rest of this note makes those precise.

## The supporting experiments

The results below are drawn from a battery built for this question; a reader meeting the labels for the
first time can take them as follows. **E16** is the direct test: it reconciles a deliberately
meaning-poor source in three conditions — inert (structure and data only), cognitive (the same source
plus meaning elicited from the system that owns it), and rich (fully described, an upper bound) —
crossed with the reference present or absent, across a capability ladder of a strong, a mid, and a weak
reconciler. **E17** is the surface-lift probe: a schema is stripped of its names, then its types, then
its concrete data, and an agent is asked to recover the meaning from what remains, allowed to abstain,
and graded by a strong judge against the truth. The **construct-then-bind** experiments ask the
related question from the other direction — whether the agents can *build* the shared reference
themselves from the two models and bind through it, and where doing so is load-bearing rather than
redundant spend. **E18** prices the reference: how little each entry can carry, and how few entries are
needed. **E19** tests whether an agent can draw the design-time / run-time line itself, sorting a seam's
facts onto their layers and marking each freezable or live. **E20** rebuilds the whole battery on two
independently published REST standards, to show the findings are not an artefact of one interface
language. And **E21**, in progress, puts two fully cognitive systems in direct negotiation and lets them
run decisive virtual experiments on candidate bindings — testing whether peers can manufacture the
shared authorisation live, without an authored reference, and whether they can do it at every capability
tier.

## What can and cannot be surface-lifted, and the mid-capability hazard

The first end of the route decision is surface lift itself: what a meaning-poor real schema yields when
an agent is asked to lift it from the surface and is allowed to abstain (E17). Stripped of names, then
of types, then of the concrete data, and graded by a strong judge against the true meaning, the finding
is twofold. Where the surface carries meaning — good (A) — recovery is high, and it survives the loss of
names and types, holding on the keys and data alone. Where the meaning is genuinely absent, an agent
that cannot lift it should say so, and the danger is the agent that instead invents. That danger is
**not** worst at the weak end. It is a mid-capability hazard: the strong model, faced with a bare
structural skeleton, defers completely; the weak model mostly abstains; the mid model — capable enough
to confabulate a fluent gloss, not calibrated enough to stop — confidently invents a meaning the surface
does not support.

This bears on good (B), and a second line of work sharpens it. Surface lift shows cognition can generate
the (A) content of a reference from a surface that carries it. The construct-then-bind experiments ask
whether it can build the *shared* artefact — the (B) scaffold — from the two models together, and it can,
where the shared category is latent in their combined meaning. On the standard-free cross-domain seam,
where no published reference exists and (B) must be *made*, agents that construct a thin reference and
bind through it lift the resolved fraction from about 0.8, unaided, to about 0.96 — close to the
reference-given ceiling. But the construction is neither free nor universal: it spends real cognition to
author the entries; it is *redundant* where an effective reference already exists, matching the unaided
close and buying nothing; and the self-built category is a *weaker cognate guard* than an authored one,
its precision easing and its surviving cognates rising. So cognition manufactures much of good (B),
exactly where it is most needed — and authoring still earns its keep as the stronger guard.

What cognition cannot manufacture is the residue: the part of (B) that is a governance decision — which
realm's category *governs* — rather than a fact derivable from the two sides, and (B) for an inert,
meaning-poor side whose meaning is not there to abstract from. The mid-capability hazard is what
fabricating that absent content looks like, so an explicit insufficient-evidence output matters most
exactly where a "good enough" mid-tier lifter would otherwise invent. "You cannot surface-lift what isn't
there" survives, narrowed to its true target: where both sides are inert and meaning-poor and no
reference exists or can be built, one is at the true limit, and honest deferral to a person is the correct
output.

## The reference is the robust route

With what cognition can and cannot produce in view, the experiments locate the routes against each other,
and their result is that the three are not equal. The reference is the **robust, capability-independent**
route, and the reason is the (A)/(B) split: the reference supplies good (B), and good (B) is the usual
bottleneck.

The direct test (E16) reconciles a deliberately meaning-poor source in three conditions — inert
(structure and data only, no explanatory meaning), cognitive (the same source plus a per-concept
explanation elicited once from the system that owns it), and rich (the source fully described, an upper
bound) — crossed with the reference present or absent, across a capability ladder. With no reference, a
strong reconciler meets a meaning-poor source by *deferring*: it proposes only what it can independently
justify — a resolved fraction of about a fifth of the correspondences, at full precision, and it never
takes a false cognate. The shortfall is not incapacity, and it is not ignorance of what the fields
*mean*; it is the absence of a shared category that would *authorise* a cross-domain binding it cannot
otherwise justify — good (B) is missing. Turn the reference on and its resolved fraction goes to one,
precision holds, the cognate stays blocked, and the same holds across the ladder. The reference is the
lever that converts honest deferral into a full, correct close, at every tier, because it supplies
exactly the good the deferral is waiting on.

Elicitation, by contrast, supplies only good (A), and so it helps only where more meaning is the binding
constraint — a capability band. On a moderately divergent case the elicited meaning rescues the mid-tier
model's false-cognate error and tracks the rich upper bound; it barely moves the deferring strong model,
which does not lack meaning but *license*; and it does not save the weakest, which takes the cognate
whether or not the meaning is supplied. On a harder, surface-similar case it is *less* sufficient still.
The lesson is that pouring more (A) onto a problem whose bottleneck is (B) helps only the middle.

One boundary on this result must be drawn honestly, because it marks the study's edge and the experiment
still running. E16's cognitive condition supplies meaning **passively**: a live source volunteers one
explanation per concept, folded into the reconciler's input. It is elicitation, not negotiation. It is
emphatically *not* what two fully cognitive systems can do when they interact — propose a candidate
binding, exchange concrete instances, probe each other's behaviour, and converge on a *verified*
correspondence. That **active verification** is a different and more powerful thing, and it bears
directly on good (B). Take the sharpest false cognate the study builds: two fields identical in name
*and* in enumerated values, denoting different things. A static reference blocks it by fiat; but two
cognitive systems exchanging instances could discover empirically that the two do not co-refer, and
reject the cognate on evidence — supplying the **(B1)** false-cognate half of good (B) that passive
elicitation misses. The positive half, **(B2)** — the licence to bind across the seam — active
verification can also manufacture where the authorisation reduces to behaviour; where it is instead a
governance decision about *which realm's category governs*, no mutual probing between the endpoints
conjures it, and that residue is the irreducible authoritative act.

So the truthful claim is bounded. For any inert side, and for the passive-elicitation slice of cognitive
sources, the reference is the robust route: it alone supplies good (B), independent of reconciler
capability. Between two fully cognitive systems, the reference may be *substitutable*, because peers have
two ways to make (B) themselves. One is already demonstrated: they can *construct* the shared artefact, as
the construct-then-bind experiments show, and on the no-standard seam that construction is load-bearing —
though, as noted, a weaker cognate guard than an authored reference. The other is *active verification* —
settling candidates on decisive evidence rather than building a standard first — and that the study does
not yet test for schematic binding, because E16's cognitive arm only elicited meaning passively. The one
place active verification is tested — the observability setting, where an agent escalates to a decisive
probe when cheap evidence is withheld — it works but is itself **capability-gated**: the strong model
triples its probing and recovers, the weak one will not escalate. E21 runs the missing test directly: two
cognitive endpoints, a negotiation with decisive virtual experiments, the hard cross-domain seam, and the
question of whether the experiment closes the construction's cognate-guard gap and matches an authored
reference at every tier.

## The design-time burden, priced

If the reference is the route a meaning-poor source most often needs, its cost is the crux of the
production worry, and it is measurable. Two questions bound it: how much must each reference entry carry,
and how many entries are needed?

On the first, a reference entry does two jobs with different minimums (E18). For *binding* — recovering
the correspondence, good (A) — a single field, even just the entry's name, is sufficient; an identity
anchor with no description is worse than nothing, but one descriptive field lifts the resolved fraction to
one. For *blocking a false cognate* on a weaker reconciler — good (B1) — a name is not enough, and a
one-line gloss earns its place. So the authored artefact is a short glossary — a name per seam, with a
gloss where cognate-safety demands it — not a re-modelling. On the second, coverage must be broad over the
seams but not universal: the load-bearing entries are the ambiguous seams, a partial reference can mislead
a less-cautious model, and the practical rule is to cover the seams completely and cheaply rather than to
author an entry per concept.

More broadly, the design-time / run-time split is itself drawable and bounded (E19). Asked to sort the
facts a reconciliation needs onto their layers and to mark each as design-time-freezable or run-time-live,
capable agents recover the split reliably and separate provenance from pragmatics cleanly — the
source-of-record facts are pulled out as frozen, distinct from the live values and use-intent. Over half
the seam's facts freeze; the live remainder is targeted — current values, deliverability, intent — not a
re-model. The design-time part is finite, mostly the schema and a source-of-record map, and a capable
agent can draw the line. And the reference need not always be authored ahead of time: where the shared
category is latent in the two models, cognition can construct it in the moment, moving even part of the
reference from the design-time column into the run-time one — though, as the construct-then-bind result
shows, authoring remains the stronger cognate guard where cognate-safety is what matters.

## Not a quirk of one interface language

The architecture is not an artefact of YANG. Built from two independently published REST standards — a
product-ordering interface and a service-ordering interface that share a common framework and so look
structurally alike while denoting different things across a commercial/technical seam — the same results
reproduce (E20). The reference rescues every tier; the strong model defers without it; a cognate identical
in both name and enumerated values is nonetheless blocked by the reference; and surface lift shows the same
recovery and the same mid-capability hazard. Because the concept surfaces are lifted from the real
specifications and only the answer key is authored, the reproduction is on real, independent inputs. What
holds for YANG holds for REST: the meaning is implicit in the application in both, and the same routes
produce the inputs in both.

## The claim, restated

Cognition completes reconciliation given the inputs, and the inputs are producible whenever one of these
holds: the source carries enough signal to surface-lift; a reference supplies the shared category the sides
lack — and that reference can be authored, or, where the shared category is latent in the two models,
*built by cognition itself*, at a cost that is load-bearing only where no standard exists; or the system is
cognitive enough to elicit, or between peers to actively verify, the implicit meaning live. Producing the
inputs is that route decision, and the reference — authored or constructed — is the robust route, because
it alone carries the shared authorisation a hard seam turns on, at every tier: authoring buys the strongest
cognate guard, construction supplies most of it where no standard exists, and active verification is the
open candidate to supply it live. Where none of these holds — both sides inert and meaning-poor, the shared
category neither present, buildable, nor elicitable, living only in a person's head — one is at the true
limit, and honest deferral to a person is the correct output, not a failure of the approach.

## Honest limits

The cases are authored, and although E20's concept surfaces are lifted from real published specifications,
its answer key is still ours; the natural next step is a genuinely unrelated interface pair with an
external ground truth. Cognition's construction of the reference is shown on compact seams, is redundant
where a standard already exists, and yields a cognate guard measurably weaker than an authored one; whether
a decisive-experiment loop closes that gap — the E21 question — is in progress, not yet settled. The
reference's dominance is otherwise shown against *passive* elicitation; whether *active verification*
between two cognitive systems can manufacture the shared authorisation live is the same open probe, the more
so since the study's one active-verification result, in the observability setting, is itself
capability-gated. The capability ladder spans three tiers of one model family in the core runs; the study's
cross-family work covers the sharp results but not the whole battery. The reference's cost is priced on
compact seams; a production interface has more concepts, though the finding that only the ambiguous seams
are load-bearing is what would keep the cost sub-linear. And the provenance/pragmatics separation is
demonstrated on a case where source-of-record and governing realm nearly coincide; a case that separates
them is the natural probe of that layer. None of these changes the architectural finding; each marks where
external data — real interface corpora, and carrier or standards-body collaboration — would carry it
further.
