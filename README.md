# Ad hoc semantic reconciliation between divergent network models

*Using machine cognition — a theory, a research programme, and a completed four-scenario study.*

## What's new (2026-11-25)

Housekeeping. Two internal working logs were removed from `study/_shelf/`, and a caveat in the YANG description
synopsis (`study/reports/`) and a message in `study/pipeline/check_local_model.py` were reworded. No results or
reports changed.

## What's new (2026-11-21)

**Keeping the bindings, added to the [instance matching](instance-matching/) case study.** Once two agents refer
to the same components, the network and the two systems go on changing: handles are renamed and re-keyed, ports
are decommissioned, addresses and cables move. Agents whose systems give them a change log kept every binding right
with no check against the network. Agents working from their own records alone ended with wrong bindings in three
runs of six; with one rule added, that a binding touched by a record change is observed and that the observation
closes it, every binding ended right in all six runs. The folder now also holds the study report "Making and
keeping instance bindings", Part 4 of the video series, a step-through page for the keeping, the code and the 24
recorded runs. Its note is at version 1.2.

## What's new (2026-11-20)

**A new case study: [instance matching](instance-matching/).** Two agents each hold their own model of one
network and their own names for its routers, ports and bundles. With no identifiers agreed in advance and no
external service binding one agent's names to the other's, the two agents matched every individual correctly in
every recorded run: all 658 in a 96-router network. With the method as tightened in this work, that takes two
conversations, about 140 checks against the network and about five minutes, where the method as it stood at
the start took twelve conversations, about 580 checks and 22 minutes for the same result. The folder
`instance-matching/` holds the note, a narrated video, step-through demonstrators, the harness and every
recorded run. It is a study of its own; nothing in `proposal/`, `study/` or `demos/` was changed.

Two software systems that must exchange information rarely share a model of the world. The classical
remedy is a standard agreed in advance. This project investigates the alternative that opens up once
the systems on each side can **reason**: they reconcile their divergent models **ad hoc**, for the
occasion, machine-to-machine, with no standard settled beforehand. The through-line is a single
thesis — **it is cognition that completes a reconciliation** — with a thin, published **reference** as
the practical anchor that reduces the work, and the **pragmatic** layer as the frontier that carries
the operative meaning. Drawn out, a lifted model is a **knowledge graph** — concepts and relations as
its schema, instances as its assertions — with pragmatics and provenance layered on; reconciliation is
then ontology matching plus entity resolution over that graph, and a thin shared reference is the
interoperable anchor such graphs can bind to.

The work is in two parts, with a separate case study. Pick a door:

### → [The proposal](proposal/) &nbsp;·&nbsp; the theory and the programme

`proposal/` — Part I develops the theory (semantic models, the lift, the cognition spectrum, shared
references) and Part II sets out the research programme (questions, hypotheses, method, benchmark,
plan). Both as papers and slide decks, with four interactive demonstrations.

### → [The results](study/) &nbsp;·&nbsp; the completed four-scenario study

`study/` — the empirical realisation of the programme across four operational scenarios (configuration,
intent, standard-free, observability), each built, run against a validated gold standard, and reported,
with a **master report** (and a companion slide deck) drawing them into one synthesis — plus the harness, benchmark, and per-run
data behind them.

### → [The demonstrations](demos/) &nbsp;·&nbsp; four interactive HTML studies

`demos/` — self-contained, interactive walk-throughs of the four scenarios (configuration, intent,
cross-domain, observability), referenced by both the proposal and the results. They run live once
GitHub Pages is enabled (see each door's README for the links).

### → [Instance matching](instance-matching/) &nbsp;·&nbsp; a case study: which router are we talking about?

`instance-matching/` — a separate, self-contained case study that applies the reconciliation method to one
question: how two agents, each with its own model and its own names for one network, come to refer to the same
components. A note, a narrated video, step-through demonstrators that open in any browser, the harness with its
tests, and every recorded run.

---

*Christopher Janz. The proposal papers build on work in the IETF/IRTF (NMOP, NMRG, TEAS/CCAMP),
the ONF Transport API, and TM Forum intent modelling; the study operationalizes and empirically tests
the programme's central claims.*
