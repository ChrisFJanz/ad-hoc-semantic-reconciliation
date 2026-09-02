# The pre-lift lexical baseline — a study design

> **Status: run and reported.** This design note has been executed; the results are in
> [REPORT_prelift_lexical.md](../studies/lift-baseline.md). It is kept as the design of record —
> question, factors, predictions, and what was built. It reuses the harness, the hard TAPI/TEAS
> case, and the metrics of [REPORT.md](../../reports/REPORT_1of4_configuration.md); the motivating observation came from the
> reference-anatomy study ([REPORT_reference_anatomy.md](../studies/reference-anatomy.md) §2.2).

## Summary

The reference-anatomy study surfaced something the main study left implicit: the agent does
not reconcile two *lexica*, it reconciles two *lifted semantic models*, and the planted false
cognates are defeated on the **non-lexical** content the lift provides — a concept's class,
its structural relations, and its instances — not on the labels. A capable agent keeps
`signal-grade` and `service-grade` apart because they differ in class, in what they attach to,
and in their instances, even though they share the token "grade." This study measures that
directly: strip the lift's knowledge back to the lexical surface and add it back a layer at a
time, and read off how much each layer contributes — and, in particular, how far short pure
lexical matching falls.

It is also the study that makes our work **directly comparable to lexical-match evaluations**,
which compare matching *with and without explanatory support* on real data. That comparison is
a slice at the lexical layer (label-only versus label-plus-gloss); this study contains it and
adds the layer such evaluations do not vary — the structure and instances of the lift. The
expected headline in one line: *lexical-only < lexical + explanation < full lifted model*, with
the decisive jump at the lift, not at the explanation.

## 1. The question

Two questions, one nested in the other:

1. **What does the lift buy?** How much of correct reconciliation — and, sharply, how much of
   *defeating the planted false cognates* — comes from the lift's non-lexical content (class,
   relations, instances) as opposed to the lexical surface a classical matcher would use?
2. **Where does explanatory support sit?** A gloss attached to a term (whether the concept's own
   or supplied by the reference) is the "explanatory support" lexical-match studies toggle. Does
   it help, and does it help *as much* as the lift's structure and instances? Our prior is that
   explanation helps modestly while the lift is the real lever.

The answer bears on a practical caution the field will care about: one should not attempt to
reconcile by matching lexica in isolation, however much explanatory text is bolted on.

## 2. The task

The same hard TAPI/TEAS reconciliation and the same gold as the main study — but the **content
of each concept** is masked to a chosen subset of its lifted fields before the agent sees it.
Everything else (scoring, the planted traps, the residual expectations) is unchanged. This is
the mirror of the reference-field ablation, one layer down: there we masked the *reference
entry's* fields; here we mask the *model concept's* own fields.

## 3. Design

**The factor is model content.** A concept's lifted fields are grouped so that the always-present
base is its lexical identity (label + synonyms) — a term must at least be nameable, and the
label is also the trap surface — and the layers added on top are the factors:

| factor | concept fields it turns on |
|--------|-----------------------------|
| explanation | the concept's own gloss + worked example (its self-explanation) |
| class | the shallow kind |
| structure | the structural relations to other concepts |
| instances | the concrete instances (A-box data) |

The full $2^4 = 16$ subsets give each layer's main effect and the interactions (does structure
substitute for instances? does explanation still help once structure is present?). Two readings
fall straight out of the factorial:

- the **cumulative ladder** lexical-only → +explanation → +class → +structure → +instances,
  which shows where the false cognate is defeated and how big each step is; and
- the **lexical-match slice** lexical-only versus lexical+explanation, which is the direct
  analogue of a with/without-explanatory-support evaluation.

**Reference as a second arm.** Explanatory support can come from the concept's own gloss *or*
from the reference's definition. To keep the two straight, the core runs hold the **reference
off**, isolating the lift's own contribution; an optional second arm turns the reference on, to
see whether an external anchor can stand in for a missing lift (we expect it to compensate
partly — the reference's definition/example is explanatory support external to the model — but
not to replace structure and instances).

**Placements.** Primarily **both-cognitive**, which is the clean analogue of a lexical-match
setting and where the concept's own explanation is available. **One-inert** is included to show
the compounding effect: with the lift stripped *and* a side inert, there is almost nothing to
reconstruct meaning from, so lexical-only should be near-worst there. (Both-inert with
lexical-only is pure label-list matching — worth one confirming cell.)

**Models.** The strength ladder — `gpt-5.6-sol`, `gpt-5-mini`, `gpt-5-nano` — since the anatomy
study showed the effect of thin evidence is strongly capability-dependent.

**Trials.** ≥ 5 per condition. Completeness over velocity: both-cognitive lexical-only cells are
light (little to reason about), so this run should be cheaper per call than the opaque-id
ablation.

## 4. Metrics

The main-study metrics, unchanged: precision, resolved fraction, surviving false cognates, residual — and
per-trap attribution, since the sharpest signal is *which* planted trap survives at each content
level. The `signal-grade`/`service-grade` same-type trap is the diagnostic: we expect it to
survive under lexical-only and to be cleared once class/structure/instances are present.
Correctness is again the currency (length-independent); reasoning tokens recorded for description.

## 5. Connection to lexical-match evaluations

Existing lexical-match studies on real data typically report matching quality *with and without*
an explanatory gloss per term. In this design that is exactly the lexical-only versus
lexical+explanation contrast at both-cognitive with the reference off. Reproducing it situates
our result in that literature and lets the numbers be compared like-for-like. The contribution
is the added dimension: the lift's **structure and instances**, which those evaluations do not
vary, and which we expect to be the dominant lever — the thing that lets a reasoning agent see
past a shared label that lexical matching, explained or not, takes at face value. Stated as an
ordering the reader can hold onto: *lexical-only < lexical + explanation < full lifted model*.

## 6. Pre-registered predictions

1. **Lexical-only takes the traps.** With label + synonyms only, the same-type false cognate
   (`signal-grade`/`service-grade`) survives — the classical lexical-matching failure — and
   precision falls; resolved fraction on the easy, lexically-close pairs stays high.
2. **Explanation helps, modestly.** Adding the concept's own gloss (or, in the second arm, the
   reference's definition) recovers some precision, but less than the structural layers.
3. **The lift is the lever.** Adding class, and especially structure and instances, defeats the
   traps and drives precision up — the largest steps in the ladder.
4. **Structure and instances partly substitute.** Either the relations or the instances alone
   should carry much of the distinction (a negative interaction between them), since both encode
   what a concept *is* beyond its name.
5. **Capability-dependent throughout.** Stronger models extract more from each added layer;
   the weakest may still fail even with the full lift (as nano did under opaque ids).

## 7. What must be built

- A **model-content mask** — the concept-side mirror of the reference-field mask already in the
  harness — selecting which of {label+synonyms, explanation, class, structure, instances} each
  concept exposes. This is a small, well-contained addition to the prompt serialization.
- A driver, `lift_baseline.py`, structured like `field_ablation.py`, with **en-route row-by-row
  capture and resume** built in from the start (the standing rule now), a `--reference on/off`
  arm, and the model-content factorial.
- No new case or gold: the existing hard TAPI/TEAS case is reused; only concept content is
  masked, so scoring is unaffected.

## 8. Open questions

- **Label leakage.** The label itself carries partial signal (`signal-` vs `service-`), so
  lexical-only is not zero-information. A stricter lexical-only variant could collide the labels
  exactly (both literally "grade") to make the trap maximally hard; worth a small side condition.
- **Two sources of explanation.** Keeping the concept's own gloss distinct from the reference's
  definition matters for interpreting "explanatory support"; the two-arm design (reference off
  vs on) is there to separate them, and the write-up must not conflate them.
- **Joint view.** The deepest version runs the model-content mask and the reference-field mask
  together, mapping the whole evidence surface — the lift's own content and the reference on top —
  in one factorial. That is likely too large to run at full trials, but a fractional design over
  the combined factors would chart the entire space.
