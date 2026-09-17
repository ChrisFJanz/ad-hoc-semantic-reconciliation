# Work-log / shelf note — NOTE_producing_the_inputs.md

**Working document. Not a repo deliverable — do not commit to the published tree.**
(It will show as untracked in GitHub Desktop; leave it unstaged or add `_shelf/` to .gitignore.)

---

## >>> RESUME PROMPT (read this first when we return to the note) <<<

We paused mid-refinement of `reports/NOTE_producing_the_inputs.md` to run a **new experiment**: whether
**active verification between two fully cognitive systems** can manufacture the shared cross-side binding
authorisation ("good (B)" below) as reliably as an **authored reference** hands it over — on the **hard
cross-domain seam**. When you come back after those runs:

1. Re-read this whole file before touching the note. The note's §"The reference is the robust route" and
   its "Honest limits" currently state the active-verification question as **open/untested**. The new runs
   are what close it.
2. Fold the new result into: (a) §"The reference is the robust route" (the bounded-claim paragraph), (b)
   §"The claim, restated" (final sentence), and (c) "Honest limits" (the passive-vs-active limit). If active
   verification **does** substitute for the reference between cognitive peers, the headline softens from
   "the reference is *the* robust route" to "the reference is the robust route *for any inert side and the
   passive slice*; between cognitive peers, active verification is an equal route." If it does **not**
   (e.g. it's capability-gated like the observability probe result), the reference's dominance strengthens.
3. Then apply the still-pending downstream edits (README dated section — see bottom of this file).

---

## E21 RESULTS — preliminary read (snapshot 2026-09-16; base ladder complete, frame arms sol + mini)

RUN STATUS (FINAL for this batch): **sol** complete (all 7 arms × 3 cases × 3 trials). **mini** complete
(all 7 arms). **nano** base ladder complete (5 arms); nano frame arms **DELIBERATELY SKIPPED** (interrupted)
— low value / extreme cost (hits the 12-turn cap every run, 170–266k tokens, ~10–15 min; weak-tier frame
failure predictable from the base arms). Resumable per-row; revisit cheaply later with `--max-rounds 3
--trials 1` only if ever wanted. Figure: `figures/fig_active_verification.png` (single/ref = true flat
ceiling; two-agent/ref = "reference in negotiation", sags at nano).

HEADLINE (answers the note's E21 open question):
- **Authored reference (`single/ref`) = capability-INDEPENDENT + cheap**: RF 1.0 / prec 1.0 / sfc 0 at EVERY
  tier on EVERY case, ~2.6k tokens (sol), seconds.
- **Active verification (`two-agent+exp`, no ref) = capability-BANDED**: rescues MID (mini → 1.0 on
  cross_domain & big_hard), barely moves STRONG (sol still DEFERS, RF ~0.27 on cross_domain & rest even with
  the experiment; spends ~1 exp), WEAK can't use it (nano sfc ~0.7 despite spending all experiments).
  ⇒ active verification NARROWS but does NOT match the reference at every tier. The reference stays THE
  robust route. Bonus: peer negotiation is ~10–100× costlier than handing over the bridge.
- **Constructed frame (`two-agent+frame`)**: MID-tier positive — mini reaches RF 1.0 on cross_domain (all 3
  trials) unaided by any authored standard (peers build + use their own frame). sol: helps big_hard (0.97;
  +exp → 1.0), partial on cross_domain (0.67 → 0.87 with exp), NOTHING on rest (0.20 = bare; the
  identical-name-AND-enum cognate defeats a self-built frame).
- **Portability-repair reading**: hand-over-the-bridge (reference) beats peer-repair (negotiate / verify /
  construct) on BOTH capability-independence AND cost. Repair works only in a band, expensively. Clean,
  sharpened support for "the reference is the robust route": even between cognitive peers who can verify,
  only the pre-declared bridge is universal.

CAVEAT: read RF WITH precision + sfc — the weak model's high RF is over-commitment (takes the cognate), not
competence; the strong model's low RF is honest deferral. n=3, high variance; don't bank single cells.

ANOMALIES to verify when convenient: `two-agent/ref` nano big_hard RF ~0.25 (below its own no-ref; weak
model may mishandle a handed reference inside negotiation); nano `+exp` keeps taking cognates while spending
all experiments (confirm it actually reads the decisive verdicts).

COMPLETE-DATA UPDATE (sol + mini frame arms done): the picture sharpened three ways.
1. **Peer self-repair PEAKS IN THE MIDDLE.** Repair arms make an inverted-V across the ladder, highest at
   mini. `two-agent+frame+exp`: mini → RF 1.0 on ALL THREE cases; sol defers (0.20 on cross/rest), nano can't.
   The strong tier won't self-repair (defers until a reference is DECLARED); the weak tier fails/takes
   cognates; the mid tier constructs + verifies + commits. Peer self-repair is a mid-band phenomenon.
2. **The decisive experiment closes the identical-enum cognate that construction alone misses.** REST:
   `+constructed frame` flat 0.20 at every tier (surface-identical cognate defeats a self-built frame);
   `+frame+experiment` → mini 1.0. Provisioning the pair and watching it behave reveals non-co-reference.
   Clean (B1) evidence.
3. **The reference's power is in the BRIDGE, not the bargaining.** `single/ref` (reference to a single agent)
   = flat 1.0 at EVERY tier/case, cheap — the true ceiling. `two-agent/ref` (same reference inside a
   negotiation) SAGS for weaker tiers (nano 0.25 on big_hard). Negotiation machinery is a liability; don't
   make weak models negotiate — hand them the bridge and let them reconcile directly.

FOLD-IN DRAFT (ready to insert — into the current note's §"The reference is the robust route" replacing the
open-question framing, OR into the portability rewrite; HELD, not yet applied, pending the rewrite decision):

> That question now has an answer. Two fully cognitive peers were put in direct negotiation and allowed to
> settle candidate bindings by decisive experiment — provisioning a pair and reading back whether it behaves
> — and to construct their own shared reference from the two models rather than being handed one, across the
> capability ladder, on the hard seams. Peer self-repair works, but it is capability-banded and peaks in the
> middle: the mid-tier pair constructs a reference and verifies it to a full, correct close on every case,
> including the surface-identical cognate — which construction alone misses and the decisive experiment
> catches — while the strong reconciler keeps deferring, unmoved by construction or experiment until a
> reference is declared, and the weak one fails and takes cognates whether it verifies or not. The whole
> apparatus costs an order of magnitude or two more than handing the reference over. The authored reference
> given to a single reconciler remains the robust, capability-independent route — a flat, full close at every
> tier at a fraction of the cost — while active verification and construction are a capable-middle, expensive
> substitute. Even a reference used inside the negotiation underperforms the same reference handed to a
> single agent for the weaker tiers: the value is in the bridge, not the bargaining.

Figure done: `figures/fig_active_verification.png` (regenerated with single/ref as the true flat ceiling).

## SEE ALSO — the portability program (the bigger reframe)
`_shelf/PORTABILITY_program.md` — portability-as-primary / reconciliation-as-one-consumer. Chris considers
it a breakthrough; we run it down experimentally (E22 keystone + E23/E24/E25) then rewrite the corpus on
it. Scaffold code drafted & offline-tested under `_shelf/code/`. The note's "producing the inputs" becomes
a subcase of "producing a portable model." Fold in AFTER the E21 runs + E22 land.

## STATUS (latest revision — read before editing)

Applied to the note so far (DONE): terminology sweep; §2–§3 (A)/(B) restructure; **section reorder**
(now: Supporting experiments → Surface lift → Reference is the robust route); new **"The supporting
experiments"** section defining E16–E21 + construct-then-bind; **construct-then-bind (Track A) folded in**
with the corrected (A)/(B) claim (cognition CAN build (B) where latent; ~0.8→0.96 on the no-standard seam;
redundant where a standard exists; weaker cognate guard; residue = governance fiat + inert side).
PENDING (waiting on runs): fold E21 decisive-experiment RESULTS into §"The reference is the robust route"
(bounded-claim para), §"The claim, restated", §"Honest limits". Follow-up runs agreed: E21 `+frame` and
`+frame+exp` synthesis arms (peers construct their own frame AND verify by experiment), plus anything the
first E21 batch shows is short. Then the README downstream edits (bottom of file).

## What was done today (note rewrite already applied)

Full rewrite of the note applied and PDF rebuilt. Changes:
- **Terminology.** "overlay" → "reference" throughout; "governed" dropped entirely; deficient sources →
  "meaning-poor" (with "thin" reserved for the reference in its small-but-sufficient sense); title now
  "…a three-route decision for **meaning-poor** sources"; metric term is "resolved fraction" (not recall).
- **Route #1 renamed** "lift" → "**surface lift**", DEFINED up front where the routes are introduced, and
  used in the E17 write-up too (E17 == surface lift; "cold-start" dropped as a term). Code identifiers
  (`cold_start_lift.py`, `results/cold_start_lift*.csv`, `fig_cold_start_lift*.png`) intentionally unchanged.
- **§2–§3 restructured around the two-goods distinction** (the core sharpening — see next section).
- Section "The lift is not one thing" → "**The lifted model is not one thing**" (avoids colliding with the
  general "cognitive lift" concept now that the route is "surface lift").

## The core conceptual reframe (the knife we sharpened)

A reconciliation needs **two different goods**, and the old note ran them together as "the missing meaning":

- **(A) each side's own meaning** — what a concept denotes on its own terms.
- **(B) the shared category that authorises a cross-side binding** — licenses "this is that" AND blocks the
  false cognate. (This is the study's own §5.1 finding: the reference does two jobs — supplies meaning AND
  pre-empts false cognates by shared identity. Those two jobs are (A) and (B).)

Map of routes → goods:
- **surface lift** and **live elicitation** are two ways to get **(A)**, differing only in source (inert
  surface vs. live agent). Which is available is gated by the cognition placement (inert vs. cognitive).
- the **reference** is the ONLY route that supplies **(B)** (plus part of (A) via its descriptive fields).
  Its availability is **placement-independent** — it's an external third artefact.

Therefore the cognition spectrum (both_cognitive / one_inert / both_inert) gates only the (A) row. (B) sits
outside it → why the reference is the **robust, capability-independent** route: (B) is the usual bottleneck,
and only the reference (or a strong-enough reconciler, or — untested — active verification) supplies it.

## The active-verification boundary (Chris's catch — the reason for the new runs)

Do NOT overclaim "even fully cognitive systems still defer." E16's **cognitive arm is PASSIVE**: a live
source volunteers ONE `explanation` gloss per concept, folded into the reconciler's input (driver
`pipeline/inert_vs_cognitive.py`, lines ~25–28). That is elicitation of (A), not negotiation. It is NOT
active verification: propose a binding → exchange instances → probe behaviour → converge on a *verified*
correspondence. Active verification bears on **(B)**:
- **(B1) false-cognate guard** — active verification is potentially STRONGER than the reference here: two
  systems exchanging instances can discover the E20 identical-name-AND-enum cognate does not co-refer, and
  reject it on evidence, where the reference only blocks by fiat.
- **(B2) positive binding licence** — verifiable where authorisation reduces to behaviour; NOT where it is a
  pure governance decision (which realm's category governs). That governance residue is the irreducible
  authoritative act = the both_inert-&-meaning-poor limit.

Balance (keep this honesty in the note): the ONLY active-verification evidence we have is observability E4′
(escalate-to-decisive-probe) — it works but is **capability-gated** (strong triples probing, recovers to
0.97; weak won't escalate, collapses to 0.46), and it's a DIFFERENT layer (live instances, not schematic
binding). So expectation: active verification likely NARROWS the reference's edge without obviously erasing
its capability-independence. The new experiment settles it.

## Next experiment — BUILT & QUEUED: E21 `pipeline/active_verification.py`

Discovered the substrate already exists: `TwoAgentStack` (src/reconcile/stacks/agent_twoagent.py) does
two cognitive peers negotiating under information asymmetry (Q/A + propose + bilateral ratify), and it
already supports (a) a **decisive virtual experiment** via a generic `SchemaOracle` (provision a pair →
read back invariants → confirmed/refuted, grounded in the case gold, budget-capped) and (b) a constructed
`shared_frame`. The oracle IS the note's (B1) empirical co-reference test.

Existing data already partly answers this. `results/two_agent_full.csv` (base negotiation, NO decisive
experiment, ladder-averaged) on the hard seams:
  - config_cross_domain two-agent ref=OFF: RF≈0.48 (ref=ON only 0.72); single ref=OFF 0.76 / ref=ON 1.0
  - config_big_hard     two-agent ref=OFF: RF≈0.63 (ref=ON 0.87);  single ref=ON 1.0
  => negotiation-ALONE (exchange (A) + reason, no decisive test) does NOT manufacture (B) on hard seams,
     and asymmetry makes two-agent worse than single-shown-both. Good supporting datum for the note.

What's genuinely UNRUN = the decisive-experiment arm. E21 driver arms (both_cognitive):
  single | two-agent(no-ref,no-exp)=L1 | **two-agent+exp(no-ref)=L2, THE arm** | two-agent/ref (upper
  bound) | single/ref. Cases: config_cross_domain, config_big_hard, config_rest (sharpest cognate).
  Ladder sol/mini/nano, trials 3. Budget = |correct|+|false_cog| (forces choice; can't brute-force).
  Offline `--validate` PASSES (oracle vs gold on all three cases).

READOUT for the note: does two-agent+exp reach RF=1 & sfc=0 with NO reference, at EVERY tier
(capability-independent → reference is substitutable between cognitive peers, soften note) or only the
strong tier (capability-gated like observability E4′ → reference stays uniquely robust, strengthen note)?
Not-yet-built: a figures_active_verification.py + fold into note per the RESUME PROMPT. Constructed-frame
(+frame) arm left out for now (that's the "generate the reference with cognition" angle, already covered
conceptually by E17/surface lift).

## MAJOR GAP (Chris's catch): the note omits "agents construct the reference from scratch" (Track A)

There is a whole existing body of work the note ignores, and it is the single most relevant prior result
to "can the inputs be PRODUCED": cognition producing the *reference itself*.
- `pipeline/construct_then_bind.py` (Track A/A1): agents build a thin shared reference from the two models
  (`reconcile.construct.construct_reference` + `bind_through_reference`), then bind through it — the
  standard-free protocol. Docstring headline: "0.40 -> 0.93" on the standard-free case (VERIFY exact source
  arm before quoting).
- `pipeline/construct_cost_study.py` (Track A/A6): when is constructing load-bearing vs redundant. Results
  on disk: `results/construct_cost_{config_cross_domain,config_big_hard,config_observability}.csv` (54 rows each,
  full ladder). Ladder-avg, both_cognitive, condition = no-ref → constructed → given-ref:
    - config_cross_domain (NO standard): RF 0.82 → **0.96** → 1.0 ; prec 0.98 → 0.89 ; sfc 0.11 → **0.33**
      => construction is LOAD-BEARING (recovers most of (B)'s binding), BUT the self-built category is a
         WEAKER cognate guard than authored (precision drops, surviving cognates rise). Construct spend ~3.9k tok.
    - config_big_hard (effective ref exists): RF 0.91 ≈ constructed 0.89 (given-ref 1.0) => REDUNDANT, ~5.4k tok spent.
    - config_observability (effective ref exists): RF 0.69 ≈ constructed 0.69 (given-ref 0.75) => REDUNDANT.
- Also: `TwoAgentStack(shared_frame=...)` is this construct step injected INTO the negotiation loop (+frame).

**This REFINES the note's (A)/(B) claim — my "cognition cannot conjure (B)" is TOO STRONG.** Correct claim:
cognition CAN construct (B) where it is *latent in the two sides' combined meaning* (both_cognitive, mutual
evidence), and doing so is load-bearing exactly where no standard exists (cross-domain) and redundant where an
effective reference already exists. What cognition CANNOT build is (i) the governance-FIAT residue not derivable
from either side, and (ii) (B) for an inert/meaning-poor side whose meaning isn't available to abstract from.
And even where it can construct (B), the self-built version is a weaker (B1) cognate-guard than an authored one.

**Fold-in for the note (big):** producing the inputs has a STRONG affirmative answer for the reference itself —
cognition builds it (Track A), load-bearing on the no-standard seam, redundant where a standard exists, with a
residual cognate-guard gap that authoring (or — hypothesis — E21's decisive experiment) closes. This also
shrinks the design-time burden further: the reference need not be authored ahead of time where construction works.
Connect to E21: +frame arm == construct-then-bind in the loop; the decisive experiment is the candidate mechanism
to CLOSE the constructed reference's cognate-guard gap. OFFER TO CHRIS: add `two-agent+frame` and
`two-agent+frame+exp` arms to E21 so "peers construct the frame" and "peers verify by experiment" are tested
together (the compelling synthesis: do peers, unaided by any authored standard, match given-ref at every tier?).

## NOTE STRUCTURE requests (Chris) — DONE this revision
- [DONE] SWAP the two results sections: "What can and cannot be surface-lifted…" now precedes "The
  reference is the robust route".
- [DONE] ADD "The supporting experiments" section before both, defining E16–E21 + construct-then-bind.
- [DONE] construct-then-bind included in that description and folded into the surface-lift + reference
  sections and the claim/limits.
- Note: E21 appears as "in progress" in the experiments roster; swap to a result statement once runs land.

## NEXT BATCH — PREPARED & QUEUED (code ready; run after the in-flight E21 base runs finish)
- `pipeline/active_verification.py` extended: `--with-frame` flag adds two synthesis arms —
  `two-agent+frame` (peers construct their own shared reference via construct_reference, then negotiate,
  no authored standard) and `two-agent+frame+exp` (construct AND decisive experiment). Frame is built with
  the negotiating tier's own model, fresh per trial; its token cost is folded into the arm's totals so the
  CSV keeps ONE column set (compatible with the in-flight run's CSV). Base arms unchanged → in-flight run
  unaffected; running processes don't reload the file. Offline `--validate` PASS; arm-wiring dry-checked.
- `pipeline/figures_active_verification.py` written + smoke-tested (synthetic data, since real not in yet;
  fake PNG deleted). 2×3: resolved fraction (top) over surviving false cognates (bottom), one col per case,
  lines across the ladder. Flat-at-1 line = capability-independent; sloping = capability-gated. Skips arms
  absent from the CSV, so it renders at every stage.
- FOLLOW-UP RUN COMMANDS (one per terminal; resume skips the already-done base arms):
    cd ~/Documents/GitHub/ad-hoc-semantic-reconciliation/study && source .venv/bin/activate
    python pipeline/active_verification.py --models gpt-5.6-sol --trials 3 --with-frame
    python pipeline/active_verification.py --models gpt-5-mini  --trials 3 --with-frame
    python pipeline/active_verification.py --models gpt-5-nano  --trials 3 --with-frame
  then: python pipeline/figures_active_verification.py
- Analysis when data lands: per case, does two-agent+exp reach RF=1 & sfc=0 with NO ref at EVERY tier
  (capability-independent) or only strong (capability-gated)? Do +frame / +frame+exp match the reference
  ceiling? Does +exp close the constructed frame's cognate-guard gap (the mid-tier sfc)? → fold into note.

## Still-pending downstream edits (apply AFTER note is fully settled — NOT done yet)

Reports/README were checked; the ONLY downstream prose using our terms is the README dated 2026-09-15
section. Apply then:
- README.md L123 "the thin, real interface models…" → "the meaning-poor, real interface models…"
- README.md L128 note-title echo → sync to "…for meaning-poor sources."
- README.md L130–131 "lift, governed overlay, or live elicitation" / "the governed overlay is…" →
  "surface lift, reference, or live elicitation" / "the reference is…" (drop governed)
- README.md L135 "a governed overlay lifts…" + "a deliberately thin source" → "a reference lifts…" +
  "a deliberately meaning-poor source"
- README.md L139 "the overlay is the more clearly decisive lever" → "the reference is…"
- README.md L145 "The minimum viable overlay is a name per seam" → "The minimum viable reference is…"
- README.md L159 — LEAVE `minimum_overlay` (code/driver identifier)
- (Consider whether README's E16 bullet should also carry the active-verification caveat, once runs land.)

Checked, NO change needed (recorded so we don't re-open):
- MASTER_REPORT.md L579 "…is governed by where the cognition sits" — ordinary verb, not the term.
- REPORT_3of4 L425 "private overlay controller", L434 "fabric-to-overlay seam" — networking term (VLAN/VNI).
- REPORT_1of4, REPORT_2of4, REPORT_4of4 — no overlay/governed/source-sense-thin occurrences.

## Open items awaiting Chris
- Any further framing comments on the rewritten note.
- Confirm the next-experiment scope above before building it.
