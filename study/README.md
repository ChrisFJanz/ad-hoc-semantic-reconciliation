# The results — a completed four-setting study

*The empirical realisation of the [research programme](../proposal/) in
[ad hoc semantic reconciliation](../). Four operational settings, built, run against a validated gold
standard, and reported, with a master report drawing them into one synthesis.*

> Part of the larger project — the theory and programme that motivate this study are in
> [`../proposal/`](../proposal/); the interactive demonstrations are in [`../demos/`](../demos/).

The central finding, established across all four settings: **it is cognition that completes a
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
**[slides (PDF)](reports/MASTER_REPORT_Deck.pdf)** — the synthesis that sits atop the four settings. It
introduces the idea once (the lift, portable semantic models, the family of reconciliation operations,
and the cognition spectrum), distils each setting to its essentials, and then gathers the findings so
they can be read as one result: what works and how far, the **six theses** the settings establish, the
evidence behind them along four cross-cutting axes (cognitive load, the reference, placement and
failure, and the pragmatic layer), two tables mapping every finding to its placement and to the process
stage it acts on, the surprises, and the scope. The slide deck carries the same synthesis for readers
who prefer slides.

![The lift — a data model becomes a portable, self-describing semantic model.](figures/fig_master_lift.png)

![Reconciliation over two lifted models — grounded correspondences bound through a thin reference, a rejected cognate, and what is honestly left unbound (no counterpart, or the residual referred onward).](figures/fig_master_reconcile.png)

## The four settings

Each setting takes the same frame to a new operation. Each has a report (renders inline), a
print-ready **PDF**, and an interactive **demo** (opens in your browser; see [`../demos/`](../demos/)
for download links too).


**1/4 · [Configuration](reports/REPORT_1of4_configuration.md)** &nbsp;·&nbsp;
[PDF](reports/REPORT_1of4_configuration.pdf) &nbsp;·&nbsp;
▶ [demo](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/configuration.html) —
two standard models of one network. ONF **TAPI** ↔ IETF **TEAS/ACTN**, seeded with false cognates and
opaque items. The founding setting: it shows the thin reference **substituting for cognition**, the
benefit **capability-dependent**, verification catching the traps, and work scaling **linearly** with a
reference against quadratically without. Its four sub-studies are folded into the report and preserved
as method notes under `notes/studies/`.

**2/4 · [Intent](reports/REPORT_2of4_intent.md)** &nbsp;·&nbsp;
[PDF](reports/REPORT_2of4_intent.pdf) &nbsp;·&nbsp;
▶ [demo](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/intent.html) —
refinement, negotiation, and a service that renegotiates itself. A customer's intent reconciled against
an operator's catalogue by **refinement**, not equivalence; verification becomes a **satisfaction**
check; a two-sided **negotiation** appears; the pragmatic operation enters as a portable **movable
policy**; and the exchange **recurs across a service's life**. Grounded in the IRTF NMRG draft
*draft-janz-nmrg-naas-agentic-negotiation*.

**3/4 · [Cross-domain](reports/REPORT_3of4_cross_domain.md)** &nbsp;·&nbsp;
[PDF](reports/REPORT_3of4_cross_domain.pdf) &nbsp;·&nbsp;
▶ [demo](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/cross_domain.html) —
reconciling with no public standard. Two **home-grown, private** models meet at one seam. The central
result is a **mirror**: without the constructed reference the strong agent **under-commits** (defers at
perfect precision) and the weak agent **mis-commits** (binds wrongly). A single descriptive field
unlocks a capable agent; a bare shared pointer is worse than nothing. Building the shared ground is the
work — and, run end to end, an agent that builds it itself lifts from **0.40 to 0.93**.

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
relations, and the labels and synonyms that name them) and a concrete layer (the instances that
populate them); **pragmatics**, the contextual information a consumer needs (what a thing is for, whose
authority governs it, in what context it holds); and **provenance** (who asserted each part, by what
method, how firmly). The lift itself is a cognitive act, aided by supports that are not parts of the
model: definitions, worked examples, a canonical example, and an optional link to a shared reference.
Being self-describing, a lifted model is **portable**: any cognitive consumer can pick it up with no
pre-agreed standard. Reconciliation runs over these lifted models, not over labels.

A **case** is two lifted semantic models plus a gold standard *derived from the models and validated*,
so it cannot drift. A **reasoning stack** reconciles them — deterministic controls and a language-model
agent run at each point on the **cognition spectrum** (both live, one inert, both inert). The
**harness** scores the output against the gold and records quality — *precision*, *resolved fraction*,
*surviving false cognates*, and the *residual* — and, for the agent, cognitive effort (reasoning
tokens, latency). A resolved fraction below one is deferral, not error: the residual is the shortfall
from full cognition's reach, and it grows as cognition recedes.

## What's new in this revision (2026-09-05)

This revision strengthens the study in-house — the central findings are unchanged and hold — and
closes the in-house gaps the first cut left open, leaving only the genuinely external one (real
network data). The reports carry the results in place; this summary is here for readers tracking what
moved between revisions.

- **Construct-then-bind, end to end (setting 3).** The standard-free setting previously handed the
  agents the shared reference and scored the binding alone. The agents now **build that reference
  themselves** from the two models and then bind through it, with nothing pre-given. The strong agent
  lifts from a no-reference resolved fraction of **0.40 to 0.93** — near the reference-given 1.00 — at
  perfect precision and with no false cognate. Constructing the shared ground works, and building it is
  the work.
- **A six-model capability sweep.** The omit-to-commit mirror — strong agents omitting, weak agents
  committing — resolves across six models into a **smooth gradient**, a continuous descent rather than a
  cliff between three points.
- **Instance co-reference measured beyond setting 1.** Entity-level co-reference is now measured in
  settings 2 and 4 as well, reproducing the budget-limited-then-structural pattern: capable agents
  resolve fully where a live side can be interrogated, the weakest only partially. (A fix to the
  interrogation path — letting an agent ask which attributes exist rather than guess field names —
  moved setting 4 from a floor to full resolution.)
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
- **Breadth — every signature reproduced on new cases.** Each of the four settings is now exercised on
  **three independently-built cases, not one** — two new ones per setting, in different domains, with
  different vocabularies and different traps. Every signature reappears: cognition completes the match
  while the reference mainly prevents the weaker agents' errors (configuration); the strong-omit /
  weak-commit mirror, repaired by a thin reference (cross-domain); refinement and negotiation completing
  while the multi-hop lifecycle grades with capability (intent); and the alarm-is-not-an-anomaly
  look-alike reliably told apart (observability). This closes the "you only showed it on one case"
  worry as far as in-house work can. (See §16 of the master report, Figure 16.)
- **The economics of the reference — when constructing it is worth the cognition.** Building the shared
  reference is itself an act of cognition, so we measured its cost against what it buys. The rule: it is
  load-bearing only where **no standard exists and the agent is capable** (cross-domain, strong agent:
  resolved fraction 0.50 → 0.93 for a little extra spend); where a reference already exists (configuration,
  observability) the **given** reference reaches the same close for a fraction of the cognition, so
  constructing one is **redundant**; and for a **weak agent it is counterproductive** — construction cost
  explodes (to ~14k reasoning tokens on average) for a worse close, not a better one. So construct-then-
  bind is not a blanket default: build the reference where there is none to bind through and the agent can
  build a good one; otherwise use the one that exists. (See §13.6 of the master report, Figure 15.)
- **Benchmark packaged.** The cases, harness, and leaderboard are packaged under `benchmark/` for
  external use — now eighteen cases across the four settings.

What remains is now genuinely external: larger and more varied cases drawn from real networks, and the
real-data grounding that only carrier and standards-body collaboration can supply. The breadth cases
above are still authored by the same hand, so they test robustness to *variation*, not to *real* data —
which is exactly the gap that external collaboration exists to close.

## Repository layout (`study/`)

```
reports/                      the deliverables
    MASTER_REPORT.md              the synthesis — start here
    REPORT_1of4_configuration.md  setting 1 · configuration (TAPI ↔ TEAS)
    REPORT_2of4_intent.md         setting 2 · intent (refinement, negotiation, lifecycle)
    REPORT_3of4_cross_domain.md   setting 3 · cross-domain (standard-free)
    REPORT_4of4_observability.md  setting 4 · observability (alarm ≠ anomaly)
notes/
    studies/                  setting-1 method notes (lift baseline, reference anatomy,
                              instance disambiguation, verification modes)
    design/                   design notes of record, per setting
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
```

Per-setting run commands are in each report's Reproducibility section, and the method notes under
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
