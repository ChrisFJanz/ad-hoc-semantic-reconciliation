# Measuring comprehensibility — methods (report/paper-ready draft)

*Working draft for Part 1 of the reports, deck, and journal paper. Prose is intended to drop into a methods
section with light editing. Terminology settled: metrics are meaning_score / abstention_rate /
confabulation_rate (no "recall"); verdicts are faithful / partial / abstained / invented.*

## What is measured, and why it measures portability

We define a lifted semantic model as **portable** when a sufficiently-reasoning agent can make arbitrary use
of it without seeking clarification that does not lie within the package. To turn that definition into a
measurement, we assess **comprehensibility**: the share of a model's concepts that an independent agent can
correctly explain *from the package alone*. The agent is given only the model — its concepts with their
labels, kinds, structural relations, instances, and glosses — and, crucially, nothing else: no answer key,
no counterpart model, and no insider knowledge of the system the model describes. Because the agent has only
the package to work from, a correct explanation is direct evidence that the meaning was recoverable from the
package by reasoning rather than supplied from outside it. Comprehensibility, so measured, is portability
made observable.

This assessment is deliberately *decoupled from reconciliation*. Prior work measured a lift's quality only
indirectly, through a downstream reconciliation of two models; here a single model is assessed on its own,
against a fixed ground truth, so that lift quality is measured directly.

## The instrument

For each assessment we hand one lifted model to a **consumer agent** of a specified reasoning tier (we use a
strong, a mid, and a weak model — the *reasoning ladder*) that did not author the model. The consumer is
asked to do three things, of which one is scored as the comprehensibility measure and two are secondary:

1. **Explain each probed concept** — for each concept in an authored question set, state, in its own words,
   what the concept denotes in the domain. The consumer is explicitly permitted to answer that it *cannot
   determine* the meaning from what it was given; an honest abstention is an allowed and desired response,
   not a forced guess. *(This is the scored task.)*
2. **Use the model for a stated goal** — identify which concepts are relevant to a task. *(Secondary and
   de-weighted: on our compact cases the relevance golds proved too narrow to score cleanly, so this task is
   reported only as coarse context, not as a portability metric.)*
3. **Flag what it cannot safely understand** — list concepts it judges under-specified or liable to be
   misread. *(Secondary; informs the honesty analysis.)*

Each explanation is then graded by a fixed **judge** — a single strong model held constant across the study —
against an authored **answer key** for that concept. The judge grades by *meaning, not wording*: two
differently phrased explanations that capture the same denotation are both correct. It returns one verdict
per concept:

- **faithful** — the explanation captures the concept's true meaning.
- **partial** — right direction, but hedged or incomplete.
- **abstained** — the consumer honestly declared it could not determine the meaning from the package (a
  *virtue* when the meaning is genuinely absent — it is the honest alternative to guessing).
- **invented** — the consumer asserted a meaning the key does not support (for example, taking a planted
  cognate). This is the confabulation hazard, and the failure the measure is built to catch.

The judge replaces a lexical similarity threshold, which is too coarse to separate a faithful explanation
from an invented one (two correct one-sentence glosses typically overlap only slightly by shared words).

## Metrics

From the per-concept verdicts we report three fractions over the question set:

- **meaning_score** = fraction *faithful* — the comprehensibility measure.
- **abstention_rate** = fraction *abstained* — honest deferral.
- **confabulation_rate** = fraction *invented* — the hazard.

A portable package yields a high meaning_score across the whole reasoning ladder. A package whose meaning is
partly absent should yield honest abstention rather than confabulation; the dangerous signature is a high
confabulation_rate, and we track it by tier because it is the mid-capability agent — fluent enough to
confabulate, not calibrated enough to abstain — that is most exposed to it.

## The ground truth

The answer keys, the concepts probed, and the planted cognate traps are authored per case as a
**comprehension gold** (`benchmark/cases/<case>/comprehension.json`): for each probed concept a plain-language
answer key stating its true meaning, and, where a concept has a misleading look-alike, an explicit note of
the concept it must not be confused with (so the judge can catch the trap). The keys state meanings a domain
engineer would recognise; the judge grades against them.

## Degrading the lift, and hiding descriptive identifiers

To measure how comprehensibility depends on the *quality of the lift*, we degrade the surface the model is
lifted from along a monotone ladder — full surface, then names removed, then types removed — and have a lift
agent recover a gloss per concept from each degraded surface, with or without a shared reference available
during lifting. The resulting (degraded) model is then assessed exactly as above. Because concept identifiers
in our cases are themselves descriptive (an id such as `m.circuit` would leak the meaning), the identifiers
are made opaque when the surface is thinned, and the question set is translated to the opaque identifiers the
consumer actually sees and scored back — so the consumer cannot read a concept's meaning off its id.

Three reference conditions are compared (a fourth is incoherent and omitted): no reference at all; a
reference used during the lift but not given to the consumer; and a reference used during the lift and also
given to the consumer. This separates the reference's role at *production* (does lifting with a reference
bake comprehensibility into the model?) from its role at *consumption*.

## A worked example

On the inter-carrier REST case, the concept `state` denotes the lifecycle state of a *commercial* order, and
looks identical to a *technical* service state in the counterpart model — a planted cognate. A consumer that
answers "the commercial-fulfilment lifecycle state of the order, not technical activation" is scored
**faithful**; one that answers "the activation state of the service in the network" has taken the trap and is
scored **invented**; one that answers "I cannot tell from this package whether this is commercial or
technical" is scored **abstained**. The three verdicts are exactly the three outcomes the measure is designed
to separate.

## Validity and limitations

The judge is itself a strong language model, so grading is model-adjudicated rather than oracular; we mitigate
this by holding the judge fixed, grading by meaning against explicit authored keys, and naming the cognate
traps in the gold so the judge is cued to the specific errors that matter. We also tested the judge directly:
freezing each consumer answer and grading it with two judges — the fixed judge and a cross-family model — left
the reported meaning_score identical (0.900 vs 0.900), with 90% per-item agreement on faithful-vs-not and no
disagreement on the clear cases (the residual falling on the weakest consumer's hedged answers, where it
cancels in aggregate). The measure is not an artefact of the particular judge's family. (Raw four-label
Cohen's kappa is deflated by the high prevalence of "faithful" — the kappa paradox — so we report the
identical scores, the binary kappa, and the raw kappa together rather than the raw kappa alone.) The answer keys are authored, so
comprehensibility is measured against stated meanings rather than an external corpus. The consumer receives
only the package and no insider knowledge, which is the point: it is what makes a faithful answer evidence of
portability rather than of prior familiarity with the domain. And abstention is scored as success, not
failure, because the operational definition rewards a model that lets a consumer *know what it cannot know*
over one that invites a confident wrong answer.
