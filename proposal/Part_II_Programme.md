# Structuring Meaning for Machine Cognition
## Part II — A Research Programme on Shared References for Ad Hoc Semantic Reconciliation

*Christopher Janz · Working paper. Part II of two; it assumes the framing and terms of Part I.*

> *A print-ready PDF of this paper is alongside it: [Part_II_Programme.pdf](Part_II_Programme.pdf). Its companion slide deck is [Part_II_Programme_Deck.pdf](Part_II_Programme_Deck.pdf). Part I is [Part_I_Theory.md](Part_I_Theory.md).*

## Abstract

Part I argued that machine cognitive systems need information made complete, structured as meaning, so that a machine can comprehend it without a human supplying what the form omits. That completion is a semantic model, an ontology, including its lexicon, together with pragmatics, carried over a base of provenance. Producing one is the lift, and it is required to feed a single system before any second system is in view. Reconciliation is the distinct operation of making two such models correspond, for instance to bridge two modelling bases. It is carried out at the level of the semantic models themselves; where systems must exchange native data, translators between their data models are generated as artefacts of the single reconciled model. Part I argued further that divergent models can be reconciled ad hoc; that the placement of machine cognition relative to the systems being reconciled, a cognition spectrum, governs what reconciliation costs; and that thin shared references reduce the work of reconciliation and, where machine cognition is scarce, the load on human supervision. This part develops a research programme to test and quantify those claims. It states the questions and hypotheses. It sets out a method with two measurement tracks, an analytic cost model and a code-backed empirical study, and describes the benchmark, the metrics, and the experimental design that connect them. It treats verification as a method that shifts with the cognition placement, and it measures cognitive effort empirically, with language models in the workflow, rather than by counting operations alone. It then names the artifacts the programme will use, generate, and share, among them a demonstration suite, an analytic instrument, a reference-reconciliation benchmark with gold-standard mappings, an evaluation harness, and the reasoning stack that runs against them. It sets out a phased plan with deliverables. And it asks what data and what experiments, drawn from operating networks, would let the questions be answered well.

## 1 Goals, thesis, and questions

Part I fixed the terms this programme uses. A semantic model is an ontology, including its lexicon, together with pragmatics, carried over a base of provenance. It is what a representation needs to be complete enough for a machine to comprehend. The lift completes each side into such a model. Reconciliation is the separate act of making two of them correspond, carried out at the level of the semantic models; where native data must be exchanged, translators between the data models are generated as artefacts of the reconciled model. The cognition spectrum, whether two, one, or none of the systems being reconciled are interrogable machine-cognitive agents, is the axis along which the work, the confidence, and the residual all change, and Part I introduces it early. The programme takes up the goals stated at the close of Part I: to find the shared references that are most effective; to quantify that effectiveness and its benefit in realistic cases and across the cognition spectrum; to delineate the cognitive workflows of reconciliation and quantify their intensity; and to understand where a reference reduces the requirement for human supervision. The central claim to be tested, stated as the first hypothesis, is that a reference partially substitutes for cognition. Its marginal benefit grows as machine cognition recedes from the systems being reconciled. Around it sit supporting hypotheses that sharpen and test it, including one on how verification itself shifts along the spectrum. Table 1 collects them.

| | Hypothesis |
|---|---|
| **H1** | A reference partially substitutes for cognition: its marginal benefit increases as machine cognition recedes from the endpoints (fully cognitive, to one inert, to both inert). |
| **H2** | A thin lexical reference reduces reconciliation work and the rate of surviving false cognates, in every cognition placement. The effect size is worth measuring, not only the sign. |
| **H3** | Different reference types help different operational cases differentially: units for quantitative intent, enumerations for observability, structural references for granularity-heavy configuration, and pragmatic references for intent and observability. |
| **H4** | Reference benefit shows diminishing returns with richness. Thin references capture most of the benefit, and richer ones add cost without proportional gain. This is the quantitative case for references that are ad hoc, not universal. |
| **H5** | References improve the calibration of confidence and shrink the residual and the human-ratification burden, most in the inert cases. |
| **H6** | The verification available to automation depends on the cognition placement. Closed-loop self-verification is available when both sides are cognitive; as cognition recedes, assurance shifts to invariant round-trips and then to external adjudication, and the cognitive effort of verification, measured with the reasoning systems in the loop, rises accordingly. |

*Table 1. The central hypothesis (H1) and its supporting hypotheses.*

## 2 Method

The method is the one exercised in the demonstrations. It lifts each model into a semantic model, reconciles the two meanings onto a shared reference to yield a single reconciled model, and, where native data must be exchanged, generates translators between the data models as artefacts of it. The study measures this method under controlled variation, along two tracks that answer to different standards of evidence.

The **analytic track** counts operations. It is given the structural parameters of a case: the number of correspondences to establish, the ambiguities to pin, the planted false cognates, the opaque items, and a measure of divergence. Given also a reference's coverage and a placement's confirmation regime, an explicit cost model computes the mechanical work, the scaling with the number of systems, the residual, and the predicted reliability and confidence. Its structural outputs follow mechanically from the method and are dependable. Its probabilistic outputs encode the hypotheses, and are exposed as adjustable parameters. The analytic track is cheap and deterministic, and it fixes the shape of the metrics. It counts operations; it does not pretend to measure the cognitive effort those operations demand, which is left to the empirical track. And it cannot, on its own, confirm a hypothesis it has been built to express, and it is not asked to.

The **empirical track** runs reasoning systems on real and synthetic model pairs, with and without each reference, at each cognition placement. It measures what actually happens: the correspondences proposed and the false cognates that survive, the precision and recall against a known-correct mapping, the calibration of the confidence the system reports, the verification method the case admits, and the cognitive effort the system expends, all as defined in Section 3. This is where the hypotheses are genuinely tested, and where cognitive effort and effectiveness, which the analytic track can only predict, are actually observed. It depends on a benchmark that supplies model pairs with gold-standard reconciliations, and on an evaluation harness that scores a run against them. Both are described in Section 4. Because a reasoning system's behaviour varies from run to run, the empirical track reports distributions over repeated trials rather than single figures.

## 3 Investigation design

### Factor space

Four factors are varied. The **reference** ranges from none, through a thin lexical anchor, to a thin anchor combined with one further type, to a richer bundle. That range is a graded dose for the diminishing-returns question. The **cognition placement** ranges over the fully cognitive case, the two one-inert cases, and the both-inert case. The **operational case** ranges over configuration, intent, cross-domain provisioning, and observability. **Divergence**, the number of planted false cognates and opaque items, and the number of systems are turned as difficulty and scale knobs. A full crossing is infeasible. The design is anchored on a baseline cell per case and varies one factor at a time, with targeted cells filled in for the interactions the hypotheses require: the reference-by-placement grid for the central substitution claim, H1; the type-by-case grid for H3; the richness dose for H4; a sweep in the number of systems for scaling; and, because it too varies with placement, the verification-by-placement grid for H6.

### Metrics

Benefit is measured in families of metrics, each defined so that it can be computed or observed rather than asserted. **Mechanical work** is the countable part: turns, messages, candidates, checks, and operations. **Cognitive effort** is the measured part, treated in the next subsection: for a language-model stack, the tokens and reasoning tokens consumed, the tool calls, the retries and self-corrections, the latency, and a graded difficulty judgement where one can be defined. **Scaling** is cost as a function of the number of systems. **Reliability** is the surviving false-cognate rate, precision and recall against the gold standard, silent errors, and the pass rate of round-trip or satisfaction checks, recorded together with the verification method each case admitted. **Uncertainty and closure** is mean confidence, its calibration, the residual, and the number of items that require human ratification. The headline result is a single figure: reference benefit plotted against cognition placement, one line per reference type. That figure is the direct test of H1 and H3.

### Verification and cognitive effort

Verification is not one method but a family, and which members are available to automation depends on the cognition placement. This is the substance of H6. With both sides cognitive, the strongest option is closed-loop self-verification: the live agents run a worked exchange between themselves and each ratifies its own side, so the check is internal and self-certifying. With one side inert, self-verification is only half available; the live agent corroborates by evidence, regenerating the inert side's native records and cross-checking them against its own observations, while round-trip on semantic invariants carries much of the remaining assurance. With neither side cognitive, no party can confirm, and verification falls to external adjudication or to a downstream test that exercises the mapping. The programme therefore treats the verification method as a measured variable, recording which method each case admits and how much of the assurance it can carry, rather than assuming a single test.

These methods differ in cognitive effort, and cognitive effort is the harder thing to measure. Counting operations captures the mechanical work well, but it does not capture the effort a reasoning system actually expends, especially once language models are in the workflow, where the same nominal step may be trivial or may demand extended deliberation. Effort must therefore be observed, not only counted. When the reasoning stack is a language model, the empirical track records the effort signals the model exposes: the tokens and reasoning tokens, the tool calls, the retries and self-corrections, the latency, and, where a rubric can be defined, a graded difficulty judgement on each stage. Effectiveness is paired with effort throughout, so that a reference or a verification method is judged not only by whether it reaches a correct result but by how much cognition it takes to get there. Delineating the cognitive workflow and quantifying its intensity, a goal stated in Part I, is in this sense an empirical measurement, made with the language models in the loop, and not a matter of counting alone.

## 4 Artifacts: used, generated, and shared

The programme rests on a set of artifacts, some drawn from existing work and some to be built. It is worth naming them, both to make the plan concrete and to be clear about what will be produced and what could be shared.

| Role | Artifact | Notes |
|---|---|---|
| **Used / consumed** | Published standards and models: the Transport API [8]; IETF TE topology [4] and the L1 connectivity and TE service-mapping models [9]; TM Forum intent models [11]; the alarm model [5]; and the NMOP fault-management terminology [7] and anomaly-semantics and incident work [10]. | the divergent models the cases are built from |
| | Operator-supplied models and data (Section 6): real, often bespoke, model pairs; alarm and telemetry streams; intent and service definitions; and ground-truth reconciliations where they can be had. | external validity |
| **Generated (code)** | The demonstration suite: four operational-case reconciliations and two that vary the cognition placement, each an interactive, self-contained study of the method. | exists; the ground for the argument |
| | The analytic cost-model instrument: the operation-counting model of Section 2, interactive, with derived and assumed outputs kept distinct. | exists; the analytic track |
| | The evaluation harness: scores a reconciliation run against a gold standard and emits the metric families. It offers a defined interface, so any reasoning stack, and a baseline matcher, can be plugged in. | to build |
| | The reasoning stack under test: the agents that lift, bind, align, and pin over model pairs, configurable for each cognition placement, together with a classical-matcher baseline. | to build; the empirical track |
| **Generated (data)** | The reference-reconciliation benchmark: a corpus of model pairs, part drawn from real standards and part synthetic, each with a gold-standard reconciliation. The gold standard gives the correct correspondences, the known false cognates, the residual expected at each cognition placement, the invariants a correct translation preserves, and the verification method the case admits. A generator produces synthetic pairs with ground truth known by construction, so that difficulty can be turned cleanly. | to build; the key new asset |
| | The reference-type artifact set: thin references of each type, authored to a fixed protocol and at graded richness. | to build |
| | Result datasets: one row per experimental cell, carrying every metric family, the mechanical work and the measured cognitive effort, the reliability and calibration figures, the residual and ratification counts, and the verification method used, each with its repeated-trial distribution; and the analysis that turns them into effect sizes and the headline figure. | generated by the study |
| **Shared** | For discussion and reproduction: the demonstration suite and the analytic instrument; the metric definitions and the cost model; and, as a candidate for open release, the benchmark and the result datasets, so that others can reproduce and extend the measurements. | openness to be decided |

*Table 2. Artifacts the programme uses, generates, and could share.*

### The datasets, concretely

It is worth being concrete about the datasets themselves. The benchmark begins from the four demonstration settings, each contributing a seed pair of real models: the configuration pair, a Transport API topology and an IETF TE topology; the intent pair, a TM Forum intent model and the IETF L1 connectivity service model; the cross-domain pair, a bespoke transport model and a bespoke IP-service model; and the observability pair, an incumbent alarm model and the NMOP anomaly and incident models. Around each seed the generator produces a family of synthetic pairs whose ground truth is known by construction, with divergence, the count of planted false cognates, and the count of opaque items turned as parameters. Every pair, real or synthetic, carries a gold-standard record in a fixed schema: the correct correspondences, the known false cognates, the residual expected at each cognition placement, the invariants a correct translation must preserve, and the verification method the case admits. The reference-type artifact set supplies, for each pair, a thin lexical anchor and graded richer variants of each reference type, authored to a fixed protocol. The result datasets record one row per experimental cell, carrying the mechanical work and the measured cognitive effort, the reliability and calibration figures, the residual and ratification counts, and the verification method used, each as a distribution over repeated trials. The formats are plain and documented, so that the benchmark and the results can be read, checked, and extended without the harness.

## 5 Phased plan and deliverables

The work falls into phases. Each phase has a deliverable that stands on its own, so that value accrues before the whole is complete.

| Phase | Focus | Deliverable |
|---|---|---|
| **0–1** | Metrics and the analytic experiment | Fixed metric definitions and cost model; the analytic instrument, giving an inspectable first read on the reference-by-placement and richness questions and fixing the shape of the metrics. Largely in hand. |
| **2** | Benchmark | The corpus, the gold standards including the verification method and the residual expected by placement, the synthetic generator, and the reference-type artifacts, per the contract the harness expects. A minimal first cut, one synthetic family and one real pair per case, is enough to begin. |
| **3** | Empirical runs | The evaluation harness and the reasoning stack; measured runs across the fractional grid, with repeated trials, capturing cognitive effort and verification method as well as work and reliability; the result datasets. |
| **4** | Analysis | Effect sizes and interaction plots: the headline figure of reference benefit against placement, the type-by-case grid, the scaling curves, and the calibration results. Also a comparison of the measured results against the analytic predictions, which validates or corrects the cost model. |

*Table 3. Phases and deliverables.*

## 6 What real networks could contribute

The synthetic part of the benchmark gives clean effect sizes, because its ground truth is planted. The real part gives external validity, and it is where an operator's contribution matters most. Several kinds of contribution would help, in rough order of value:

- **Real, bespoke model pairs**, especially vendor or operator models with opaque or under-documented fields. These are exactly the material the one-inert and both-inert cases turn on, because they are where inference without confirmation is hardest and the residual is real rather than contrived.
- **Alarm, event, and telemetry streams**, with enough context to reconstruct meaning: resource identity, timing, and, where they exist, maintenance windows and seasonal baselines. The observability case depends on this, and its pragmatics cannot be studied from schemas alone.
- **Intent and service definitions** as operators actually express them, so that the refinement and satisfaction cases are exercised against demands with real quantitative content.
- **Ground-truth reconciliations or adjudications.** Where an operator already maintains a mapping between two of its models, or can adjudicate a proposed one, it supplies the gold standard that the real part of the benchmark otherwise lacks.
- **A setting in which to run the reasoning stack against operator data**, under whatever handling constraints apply, so that the measured results reflect real models rather than only public ones.

Experiments, rather than data alone, would also help. A useful early one is to take a pair of an operator's own models, run the reconciliation at each cognition placement, and measure the work, the residual, and the human-ratification burden, with and without a thin reference authored for the pair. That single experiment, repeated across a few operators and a few model pairs, would speak directly to H1, H2, H5, and the verification claim H6, on models that matter to the operators themselves.

## 7 Validity, handling, and scope

Several risks are worth stating. The analytic model must not be mistaken for evidence. It predicts, and the empirical track tests. Gold standards for real model pairs are a matter of judgement. Where they are constructed, they will be adjudicated and documented, with the synthetic pairs carrying the weight of the exact effect sizes. Reasoning systems vary from run to run, so results are reported as distributions, with repeated trials and fixed conditions. Cognitive-effort measurements are, in addition, model-dependent: they are reported per model, and comparisons hold the model and the conditions fixed, so that effort is read as a relative signal across treatments rather than an absolute cost. A reference authored to flatter the treatment would bias the study, so references are authored to a fixed, thin protocol, and, where feasible, without sight of the test pairs. Public standards may have been seen by a reasoning system before, so conclusions are weighted toward the synthetic material, where memorisation is not a concern. Operator data will be handled under whatever terms its source requires, and the programme is content to work with de-identified or synthesised derivatives where that is what can be shared.

The programme is deliberately bounded. It studies references and the cognition spectrum for semantic reconciliation. It does not attempt a universal model, nor a general treatment of agent governance, security, or authorisation, which are real problems and are left to companion work. Its relation to current standards activity is close. The observability case builds directly on recent fault-management and anomaly work [7], [10], and the results, in particular the effect of shared references on human-supervision requirements, are intended to be useful to that activity. The programme also runs alongside related community efforts to represent network operations as knowledge graphs [12], [16] and to give AI systems a canonical interface to network models [13], [14], [15]. Shared references are intended to be the kind of thin, interoperable anchor to which such knowledge graphs and interfaces could bind, and the benchmark and metrics developed here could serve to evaluate them.

## References

[1] C. W. Morris, *Foundations of the Theory of Signs*, University of Chicago Press, 1938.
[2] R. L. Ackoff, "From Data to Wisdom," *Journal of Applied Systems Analysis*, vol. 16, 1989.
[3] RFC 8342, *Network Management Datastore Architecture (NMDA)*, IETF, 2018.
[4] RFC 8795, *YANG Data Model for Traffic Engineering (TE) Topologies*, IETF, 2020.
[5] RFC 8632, *A YANG Data Model for Alarm Management*, IETF, 2019.
[6] RFC 9232, *Network Telemetry Framework*, IETF, 2022.
[7] RFC 9940, *Some Key Terms for Network Fault and Problem Management*, IETF, 2026.
[8] ONF TR-547, *Transport API (TAPI) Reference Implementation Agreement*, Open Networking Foundation.
[9] draft-ietf-ccamp-l1csm-yang; draft-ietf-teas-te-service-mapping-yang, IETF, work in progress.
[10] draft-ietf-nmop-network-anomaly-semantics; draft-ietf-nmop-network-incident-yang; draft-ietf-nmop-network-anomaly-architecture, IETF, work in progress.
[11] TM Forum TR290, *Intent Common Model*; IG1253, *Intent Management*; TMF921, *Intent Management API*.
[12] B. Peters, *Network Ontology Knowledge Graphs*, open-source project, github.com/bradspau/Network-Ontology-Knowledge-Graphs.
[13] draft-feng-netmod-naim, *NAIM: A Canonical Data Format for AI-Assisted YANG Modeling*, IETF, work in progress.
[14] draft-feng-netconf-naim-op, *NAIM Operations (companion to the NAIM data format)*, IETF, work in progress.
[15] draft-feng-nmop-naim-mcp, *NAIM with the Model Context Protocol (companion to the NAIM data format)*, IETF, work in progress.
[16] draft-mackey-nmop-kg-for-netops, *Knowledge Graph Framework for Network Operations*, IETF, work in progress.
