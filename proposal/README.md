# The proposal — Structuring Meaning for Machine Cognition

*Ad hoc semantic reconciliation between divergent network models, using machine cognition.*

A two-part research proposal with companion materials. It examines how networked systems that reason
for themselves need information structured as **meaning**, not merely form — and how two such systems
can reconcile their divergent models *ad hoc*, with no standard agreed in advance.

> The empirical realisation of this programme — four settings built, run, and reported — is in
> [`../study/`](../study/). The interactive demonstrations are in [`../demos/`](../demos/).

## Papers

**Part I — Structuring Meaning for Machine Cognition: Semantic Models, the Cognition Spectrum, and
Shared References.** Read inline: **[Part_I_Theory.md](Part_I_Theory.md)** · PDF:
**[Part_I_Theory.pdf](Part_I_Theory.pdf)** · slides: **[Part_I_Theory_Deck.pdf](Part_I_Theory_Deck.pdf)**.
Covers semantic models as completeness for comprehension, the **lift** that produces them,
semantic-level reconciliation, the **cognition spectrum**, shared references, and four worked
demonstrations.

**Part II — A Research Programme on Shared References for Ad Hoc Semantic Reconciliation.** Read inline:
**[Part_II_Programme.md](Part_II_Programme.md)** · PDF:
**[Part_II_Programme.pdf](Part_II_Programme.pdf)** · slides:
**[Part_II_Programme_Deck.pdf](Part_II_Programme_Deck.pdf)**. Sets out the research questions and
hypotheses, a two-track methodology, metrics including language-model-based cognitive-effort
measurement, a benchmark with datasets, a phased plan, and the contributions sought from operational
networks.

*(Each paper is provided both as markdown — which renders here on GitHub — and as the original PDF,
which is the faithful, printable version. The slide decks are PDF only.)*

## Interactive demonstrations

Four self-contained HTML studies, one per operational setting. Clicking an `.html` in the repo shows
its source — GitHub never renders HTML inline — so to see one run, use **view in browser** (opens it
rendered via htmlpreview, no setup) or **download** it and open the file locally. The source files are
in [`../demos/`](../demos/).

- **Configuration** — two peer models of one transport network (TAPI ↔ IETF TEAS); pre-empts false
  cognates through a thin reference, verified by round-trip on invariants.
  [▶ view in browser](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/configuration.html) ·
  [⤓ download](https://raw.githubusercontent.com/ChrisFJanz/ad-hoc-semantic-reconciliation/main/demos/configuration.html)
- **Intent** — a declarative, quantitative intent refined to a realisation (TM Forum intent ↔ IETF
  L1CSM); verification through **satisfaction** rather than equality.
  [▶ view in browser](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/intent.html) ·
  [⤓ download](https://raw.githubusercontent.com/ChrisFJanz/ad-hoc-semantic-reconciliation/main/demos/intent.html)
- **Cross-domain** — two bespoke systems in different domains with no shared standard; they build a
  minimal shared reference between themselves.
  [▶ view in browser](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/cross_domain.html) ·
  [⤓ download](https://raw.githubusercontent.com/ChrisFJanz/ad-hoc-semantic-reconciliation/main/demos/cross_domain.html)
- **Observability** — reconciles anomaly semantics across an incumbent fault model and the newer IETF
  NMOP model, where **pragmatics** carries most of the meaning.
  [▶ view in browser](https://htmlpreview.github.io/?https://github.com/ChrisFJanz/ad-hoc-semantic-reconciliation/blob/main/demos/anomaly.html) ·
  [⤓ download](https://raw.githubusercontent.com/ChrisFJanz/ad-hoc-semantic-reconciliation/main/demos/anomaly.html)

## Suggested reading order

Begin with **Part I** for the framing and terminology; explore one or two **demonstrations** to see
the method in action; then read **Part II** for the proposed research programme. From there, the
[`../study/`](../study/) reports show the programme carried out and measured.

## References

The standards, related community work, and foundational sources supporting the proposal are listed in
each paper's own reference section ([Part I](Part_I_Theory.md#references),
[Part II](Part_II_Programme.md#references)) — spanning IETF RFCs and drafts (NMOP fault/anomaly/incident
work, TE topology, L1CSM, the knowledge-graph and NAIM efforts), the ONF Transport API, TM Forum intent
models, and the theory of signs and the data-to-wisdom ladder.
