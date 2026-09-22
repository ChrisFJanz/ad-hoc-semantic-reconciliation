# Brad's YANG Description Quality & Definitional Anchoring study — reading memo

**Prepared for:** Chris
**Date:** 22 September 2026
**Source:** Brad's "YANG Description Quality & Definitional Anchoring, Findings" (19 pp.)
**Purpose:** Make the study legible, reconcile it with the reconciliation framework, separate
what is solid from what is soft, and mark where it can strengthen the master report and a possible
NMRG Internet-Draft.

---

## 1. What the study is, in one paragraph

Brad is asking a question underneath our whole line of work: when two models describe
the same networking concepts in different words, is the *meaning text* attached to a node
(its YANG `description`) actually good enough, and actually necessary, for a machine to
recognise what that node is? He answers it in two phases. **Phase 1** audits the quality of
YANG description statements across seven modules (IETF and TAPI) — are they real definitions
or filler? **Phase 2** runs a blind experiment: it makes an LLM bind YANG nodes to concepts in
a small shared lexicon, once using only the node's *name and synonyms*, once using its
*description text*, and measures which does better. The name-only-vs-definition contrast is
a direct proxy for "do surface labels carry the meaning, or does the description?" — which is
the empirical heart of the portability and reconciliation argument.

The two corpora:

- **IETF:** 4 modules (`ietf-network`, `ietf-network-topology`, `ietf-te-topology`,
  `ietf-otn-topology`) — 2,279 scored data-nodes.
- **TAPI:** 3 modules (`tapi-topology`, `tapi-connectivity`, `tapi-common`) v2.5.2 —
  3,418 scored data-nodes.

---

## 2. Phase 1 — how good are the descriptions?

### 2.1 The rubric and the headline number

Descriptions were scored against an **ISO-704** definitional-quality rubric on a stratified
150-node sample (75 per corpus): is a description **intensional** (a genuine definition = a
genus plus a differentiating characteristic), or does it fail as **tautological/name-restating**,
**extensional-example-only**, or **empty/boilerplate**?

**Only ~44–45% of descriptions in either corpus are genuine definitions**, and the failure
modes differ by corpus:

| Corpus | intensional | tautological | example-only | empty/boilerplate |
|---|---|---|---|---|
| IETF | 44.0% | 49.3% | 6.7% | 0.0% |
| TAPI | 45.3% | 32.0% | 0.0% | 22.7% |

So IETF's characteristic failure is **tautology** — restating the node's own name (~49%) —
while TAPI's is **literal boilerplate**, mostly the literal string `"none"` (~23–31%, a
leftover from TAPI's UML→YANG code generation). The nuance Brad draws out: this refutes a
naive "IETF good, TAPI bad" prior. When TAPI *does* define, its descriptions are if anything
*slightly more* intensional than IETF's; TAPI just has more that are outright blank.

**Caveat on the number:** both the "manual" and "LLM" annotation passes were produced by the
same model (Claude) reading the text twice, so the reported Cohen's κ = 0.880 measures
*rubric self-consistency*, not agreement with an independent human. Treat it as a reliability
floor, not validation.

### 2.2 Duplicate descriptions — the concept is identical, the reuse site is not

There are **429 groups of byte-identical descriptions**, because YANG groupings are reused
across many structurally-repeated points (one IETF string appears 136 times; TAPI's generic
"The specific value." / "The specific unit of measurement of the capacity." patterns appear
60–120+ times each). This is *not* per se a defect — the concept genuinely is the same
everywhere the grouping is reused. But it means **description text alone often cannot
distinguish two different reuse sites of the same grouping.**

### 2.3 Same-corpus semantic collisions — an instance-level limit, named precisely

Within IETF, 214 node pairs have near-identical descriptions (TF-IDF cosine > 0.85) but sit
at different paths/scopes — same grouping content, different location. The cleanest example:
two nodes, one under `optimizations` in a configured connectivity-matrix and one under
`information-source-entry`, carry the *exact same* description ("The objective function
container that includes attributes to impose when computing a TE path.") but are legitimately
different things (different scope, lifecycle, potentially different values). **The description
was never going to distinguish them, because it is the same string in both places by design.**

Brad names the distinction this forces, and it is worth quoting because it is *our* distinction:

> Phase 2 asks a **concept-level** question — given a node's description, which lexicon concept
> does it represent? The collision finding asks an **instance-level** question — given two nodes
> correctly classified as the same concept, can the text tell you *which occurrence* you're
> looking at? Text structurally cannot, not because it's badly written but because it's
> byte-for-byte identical by construction. That information lives in the path (or another
> structural signal: parent context, containing list key, `when`/`augment` target), not in the
> prose.

His conclusion: **definitional anchoring needs both** — definitional text to resolve *what kind
of thing* a node is, and structural/path context to resolve *which one*. Treating text-only
anchoring as sufficient would silently conflate distinct instances that share a grouping. This
is a direct match to the reference's two roles in our framing.

### 2.4 Cross-corpus separability — lexical methods can't bridge, which is the whole point

Under TF-IDF (pure lexical overlap), **none** of the headline trap nodes find their true
cross-corpus counterpart above threshold — IETF and TAPI use **almost entirely disjoint
vocabulary for the same concepts** (IETF "termination point... a port or an interface" vs TAPI
"NEPs belonging to / owned by this Node"). This is a *negative* result for lexical methods
specifically, and it is exactly the gap an LLM's world knowledge — rather than surface token
overlap — has to close. It is empirical motivation for cognition over matching.

(Brad adds a careful scoping note: Phase 2's *aggregate* name-only score is not a clean test of
this cross-corpus claim, because the lexicon's synonym lists were deliberately built with
vocabulary from *both* corpora, so name-only often has the bridge pre-built. The one row that
genuinely isolates the claim is `owned-node-edge-point`, whose lexicon entry has IETF-only
synonyms — see §3.5.)

---

## 3. Phase 2 — name-only vs definition-based binding

### 3.1 The experiment

A **12-entry lexicon** of concepts (LEX-001 … LEX-012). A **gold standard** mapping YANG nodes
to the correct lexicon entry (or to `NONE` where no entry fits). An LLM "binder" is asked, per
node, which lexicon entry it is — in two modes:

- **name-only:** given the node name + the lexicon entries' names/synonyms.
- **definition-based:** given the node's actual `description` text.

Scored with precision / recall / F1 in the NER convention (a system must both *notice* a
concept exists and *get its label right*; a confidently-wrong non-`NONE` guess counts as both a
false positive and a false negative). Three scope filters are reported; the one Brad's
headline numbers cite is **`equivalence_plus_subsumption`**, which scores on lexicon id and
already folds in "subsumed-by" relations.

### 3.2 The blindness guarantee (this matters)

An earlier version of the study had the *same* agent author the gold standard and produce the
"blind" predictions in one conversation — a real contamination risk. **This version replaces
that with isolated tool-call invocations:** each prediction is a fresh model instance with no
filesystem access and no visibility into the gold standard or the conversation, given only the
literal prompt text. 144 scored calls in the core dataset (72 candidates × 2 modes), plus extra
diagnostic calls that are reported but not scored. **One call per decision, never re-rolled** —
a rule that does real work later (see §3.4). This is a genuine blind evaluation, not a demo.

### 3.3 The number keeps moving — and why that's the honest part

The aggregate F1 comparison changed *every time Brad corrected his own instrument* (the gold
standard and the lexicon), across six rounds:

| Round | n | name-only F1 | definition-based F1 | What changed |
|---|---|---|---|---|
| Uncorrected | 39 | **0.98** | 0.84 | first blind run |
| Corrected | 39 | 0.946 | **0.958** | fixed 2 wrong gold rows + a lexicon boundary |
| Expanded | 58 | **0.943** | 0.893 | + 19 rows; surfaced LEX-003 over-triggering |
| LEX-003 fixed | 58 | **0.935** | 0.923 | rewrote the over-triggering lexicon entry |
| Investigated | 58 | 0.935 | **0.942** | resolved a layer-protocol parent-context error |
| **Final** | **72** | **0.923** | **0.945** | + 14 rows |

The first-round headline (name-only *crushing* definition-based, 0.98 vs 0.84) was an
**artefact of a flawed instrument**, not a real result: two gold rows were simply wrong, and the
lexicon had a boundary problem that penalised the description reader. As the instrument was
corrected, the ranking inverted; and — the key point — **as the sample grew (39 → 58 → 72) the
definition-based lead widened rather than narrowed.** Brad's reading, which is correct: a
result that gets *more* pronounced with more data is the signature of a real effect, whereas
small-n noise shrinks or flips. He is equally clear that six rounds of a moving number on a
single-author gold standard means the *absolute* figures are still soft.

### 3.4 The finding that is actually robust: the *shape* of the errors, not the count

What is stable across every single round is **how each mode fails**, and the two modes fail in
categorically different places.

**Name-only always fails as a "false friend"** — a literal name or synonym match that means
something *different*, sometimes opposite, in context. The recurring cases, present in every
round:

- `nsrlg` matches a "shared-risk-group" synonym but denotes the semantic **opposite** (link
  groups that must be kept mutually *disjoint*).
- `lifecycle-state` matches a synonym but names a **different** concept (provisioning lifecycle)
  than the intended administrative in/out-of-service state.
- `owned-node-edge-point` / `parent-node-edge-point` get pulled to the wrong entry by a surface
  cue with no real synonym overlap.
- The cleanest case of all: **`/networks/network` itself**, with no description available,
  name-only infers "a network contains nodes, therefore network is broader than node" from the
  bare path and name — a plausible, name-shaped inference that is simply wrong, and there is no
  description text in name-only mode to correct it.

Every name-only error, across every round, fits this one description: **a name, synonym, or
name-shaped inference that turns out to be a false friend.**

**Definition-based's remaining errors collapse to essentially one category: the source text is
too terse to state the disambiguating fact.** Its cleanest examples:

- `cep-list` — full description "The list of supported ConnectionEndPoint (CEP) instances." It
  **genuinely never says** whether the CEP faces the client or the network side of an adaptation,
  so no reasoning and no lexicon rewording can recover the binding.
- `client-svc`, `supporting-termination-point` — same shape: four-word or relationally-phrased
  descriptions that don't contain the needed fact.

This is a property of the source **text**, not a failure of method: when the description doesn't
encode the fact, cognition can't manufacture it from the description alone, and would need
something outside the text (live system state at lift time, or an authority decision).
Definition-based fails *only* where there is nothing left in the description to reason from.

So: name-only fails where a name misleads; definition-based fails where the text runs out. The
second is the respectable kind of error, and it marks the limit of what the published text alone
can support. Whether each such case is a true frontier or a gap the lift would close is taken up
in §5.

### 3.5 The three problems Brad fixed (and how he told fixable from irreducible)

Across the correction rounds he found and disclosed three distinct instrument flaws, and — this
is the discipline worth noting — he kept them apart from each other and from noise:

1. **Two gold-standard rows were simply wrong** (`nsrlg`, `lifecycle-state`) — the human-authored
   labels contradicted the source text; the blind definition-based calls had actually answered
   correctly. Fixing gold converted two definition-based "errors" into correct answers with no
   re-test.
2. **Lexicon boundary / over-triggering problems** — LEX-002/003/007 had overlapping "boundary
   point" definitions; separately, LEX-003's definition text literally contained "TE tunnel" and
   "path computation", so it over-triggered on any node whose text mentioned those words even when
   it wasn't a tunnel/LSP endpoint. Rewriting the lexicon entries with explicit cross-references
   fixed these; re-tested via fresh isolated blind calls.
3. **A missing rule for attribute/template containers** — property-bag containers (e.g.
   `te-link-attributes`) were mis-scored; one explicit sentence added to the prompt resolved it.

And the honesty markers:

- **Selection-effect caveat, self-imposed.** The correction round only re-investigated rows where
  the binder *disagreed* with gold — a confirmation-bias risk (you find gold wrong only where it's
  convenient). He explicitly names this and runs a **symmetric re-audit of the 37 rows where
  definition-based already agreed with gold**, finding no lexicon id needed to change — which
  closes the selection gap.
- **Reported an unstable result rather than re-rolling it.** `client-svc` returned three
  *different* answers across three isolated calls. Per the one-call-per-decision rule, he kept the
  original call's result as recorded and *reported the instability itself* as further evidence
  that this description is too terse to bind reliably — instead of quietly re-running until a call
  landed on the "right" answer.
- **Distinguished single-call sampling noise from real defects.** `supporting-network` gave a
  hedged, internally-inconsistent answer once; a diagnostic re-check came back clean. He flags it
  as *likely noise on a genuinely borderline case*, does **not** substitute the nicer answer
  (again per the no-re-roll rule), and leaves it as a recorded error while saying so.
- **Revised three gold labels on *convergent* evidence, not his own say-so** — where both
  name-only and definition-based independently converged on the same alternative to his initial
  guess, he treated that convergence (not his authority) as reason to change gold, and documented
  the reasoning per row.

### 3.6 Where the final errors actually sit (72-row set)

- **name-only: 7 errors** (TP 60, FP 7, FN 3, TN 5). **All 7 are the false-friend pattern.**
- **definition-based: 5 errors** (TP 60, FP 4, FN 3, TN 7). 3 of the 5 are the terse-source
  limit (`supporting-termination-point`, `client-svc`, `cep-list`); the other two are a likely
  sampling-noise borderline (`supporting-network`) and one genuine out-of-scope edge-case
  judgement (`network-id`: does an identifier of a network inherit the network concept, or is it
  out of scope?).

Final F1: **name-only 0.923, definition-based 0.945**, gap wider than at 58 rows (0.935 vs
0.942) and much wider than the corrected 39-row near-tie (0.946 vs 0.958 had them close).

---

## 4. What is solid vs what is soft

**Solid (carry these):**

- The **error-shape asymmetry** — name-only = false friends, definition-based = source-text
  terseness — is stable across all six rounds and both expansions. This is the trustworthy
  finding, independent of the exact F1.
- **Phase 1's corpus-level quality numbers** (~44–45% intensional; IETF-tautology vs
  TAPI-boilerplate split) have *no blindness confound* — they don't depend on the gold standard
  — and Brad rightly calls this the more trustworthy half of the study on its own.
- The **instance-vs-concept** distinction and the **disjoint-cross-corpus-vocabulary** result are
  clean and well-argued.

**Soft (flag if cited):**

- Gold standard, lexicon, and Phase-1 rubric labels are all **single-agent** (κ = 0.880 and
  0.852 are *self-consistency*, not human validation). Brad states this himself; it's the one
  remaining contamination risk after the binder was isolated.
- **n = 72**, and the "widening trend" rests on two expansion points (39→58→72) — a small base to
  extrapolate from.
- The lexicon's synonyms were drawn from **both** corpora, which **inflates name-only's aggregate
  score** (its bridges are pre-built). The true name-only-vs-definition gap in the wild is
  therefore probably **larger** than 0.923-vs-0.945 shows; the `owned-node-edge-point` row
  (IETF-only synonyms) is the clean case where name-only fails as predicted and definition-based
  succeeds.

---

## 5. Reconciling this earlier work and the continuing study

This section reads the earlier study against the framework the continuing study has established,
and states how its results are best understood at this point.

**The framework established by the ongoing study, in brief.** The lift, the production of a
self-standing semantic model from a system's own representation, is a cognitive act performed by
an agent with access to more than the published text: the running system, its instances, its
configuration and operational context. Portability is comprehension by a cognitive agent that
holds only the lifted model. A thin shared reference carries concept-level anchors in two roles:
it names what kind of thing a node is, and it supplies facts an inert or terse counterpart cannot.
A residue of authority and underdetermination remains, to be referred to a person.

The points that follow set the earlier study against that framework, one element at a time.

**The binder is the portability test, run on un-lifted models.** The definition-based binder is
the portability test made concrete: a fresh, isolated cognition given only a node's published
description and a thin reference, asked to comprehend it well enough to bind it. The models it
reads were never lifted. A YANG description is authored by hand, frequently tautological or the
literal `"none"`, and never produced by a cognition whose task was to make the model stand on its
own. The study therefore measures the portability of the *un-lifted* model, and the wall it meets
is the portability deficit the lift exists to close.

**The wall is mostly a missing-lift gap.** The terse-source failures are the shape of that wall:
the CEP whose description ("the list of supported ConnectionEndPoint instances") never states
whether it faces the client or the network side. Most such failures are not the irreducible
frontier. Which side an endpoint faces is recorded in the running system, and a native cognition
reads it at lift time and carries it into the lifted model; the fact is missing from the text, not
from the system. The binder fails because it is handed an un-lifted artefact, and the reference
correctly does not carry the fact, since "this endpoint faces the client" is instance-specific and
belongs in that system's lifted model rather than in a shared reference. This is Phase 1's
instance-against-concept distinction on the producing side: instance-level facts into the lift,
concept-level facts into the reference. The genuinely irreducible residue is the smaller set of
facts recorded *nowhere* in the system, true authority or underdetermination calls. The strength
of this reading depends on how much of the terse-source set is latent in the system rather than
truly absent; the flagship cases, the CEP side and the layer-protocol parent-context case, are
latent, and each case is checkable directly.

**Placement is a hand-off, and the lift's value is measurable.** Cognition is placed within a
system once, as the lift, so that a consumer above the system, holding only the artefact and a
thin reference, can comprehend it. The lift carries the omitted facts from live state into the
self-standing model. The study measures the state before that step, which makes it a baseline. Its
modes fall on one value chain of increasing cognitive investment: names, authored description, and
the lifted model. Name-only against definition-based is measured here, 0.945 against 0.923 in F1
at 72 cases, the margin widening with scale; the lifted model is the next rung, above the
description the binder reads. The distance between the description-based ceiling and lifted-model
portability is a measurable quantity: what the lift adds.

**The floor, from the other side.** The name-only errors mark the bottom of that chain. Every one
of name-only's seven residual errors at 72 cases is a false friend, a name or synonym that matches
while the meaning differs; the clearest is `/networks/network` itself, bound wrongly from the bare
path on the inference that a network contains nodes and so is broader than one. Across the two
corpora the vocabulary is near-disjoint: no trap node finds its counterpart above the
lexical-similarity threshold. Surface matching cannot bridge that, which is the direct case for
cognition over lexical or ontology matching.

**What the raw material demands.** The audit quantifies why the machinery is needed. Across the
seven modules, only about 44 to 45 percent of description statements are genuine definitions; the
remainder are tautology on the IETF side and, on the TAPI side, frequently the literal `"none"`.
An agent reconciling real-world models works much of the time against text that carries little
meaning, which is where the lift, the reference, and pragmatic judgement earn their place.

**How the results read now.** At this point in the current work, the study is best read as a
measurement of the portability of the *un-lifted* model: a baseline for the lift, a map of the
facts a lift must supply, and a localization of the small residue no lift reaches. The name-only,
definition-based, and lifted-model levels are three points on one value chain; the study fixes the
first two, and the terse-source wall it meets marks the work the lift is defined to do rather than
a hard limit on comprehension.

## 6. Possible enhancements to the master report and a future NMRG I-D, from this study, for consideration

These are secondary to the reading in Section 5 and follow from it: candidate enhancements, drawn
specifically from this work, offered rather than committed to.

1. **Installed-base grounding for the motivation.** The audit's corpus-level numbers give the
   report, and an eventual NMRG Internet-Draft, a concrete answer to "why is ad hoc reconciliation
   needed" and "why not simply consume the published model": across the seven IETF and TAPI
   modules, only about 44–45% of description statements are genuine definitions, the IETF residue
   largely tautology and the TAPI residue frequently the literal string `"none"`. Candidate: a
   short empirical paragraph in the motivation.

2. **Cognition placement as a hand-off, centred on the lift.** Candidate: state the placement of
   cognition as the hand-off set out in Section 5 (cognition within a system once, as the lift, so
   that a consumer above the system needs only the artefact and a thin reference), with the
   installed base's defects read as a specification of what the lift must supply.

3. **The error taxonomy as evidence for the reference's two roles.** The false-friend (a name
   misleads) against terse-source (the description is exhausted) split, with the
   instance-against-concept distinction (text resolves what-kind, path resolves which-one),
   corroborates the reference's two roles from an independent direction. Candidate: cite as
   external corroboration where the reference is introduced.

4. **The un-lifted model as a measurable baseline for the lift.** Candidate: adopt the binder's
   published-model result as the un-lifted baseline against which the lift's value is measured
   (Section 5), as a tightened scenario in the study or a worked example in the I-D.

5. **Cross-corpus disjointness as motivation for cognition over matching.** The near-disjoint
   IETF/TAPI vocabulary, with no trap node finding its counterpart above the lexical-similarity
   threshold, is a crisp argument for world knowledge over lexical alignment. Candidate: a
   one-line empirical anchor.

6. **Citability.** Several of these become load-bearing only if the study exists in a citable
   form: a companion draft, a tech report, or a repository with a DOI. Worth deciding before an
   I-D leans on it.

A caution carried from §4: lean on the error-shape result and the corpus-level audit numbers,
which are the sturdy findings; treat the absolute F1 values as indicative rather than settled,
given the single-author gold standard and n = 72.
