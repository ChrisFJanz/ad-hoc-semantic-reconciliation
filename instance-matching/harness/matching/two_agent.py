"""Two-agent instance reconciliation: the two-agent negotiation, extended to individuals.

The schema two-agent stack (``agent_twoagent.TwoAgentStack``) has two agents reconcile
*concepts* under real information asymmetry. The instance stack (``agent_instance``) has a
single agent, shown both populated graphs, work the live-cognition oracle. This module joins
the two: Agent A holds ONLY graph A's individuals, Agent B holds ONLY graph B's, and they
reconcile *individuals* with the same turn structure as the schema negotiation.

Neither agent sees the other's individuals except:

  * a public catalogue each agent advertises for its own side, carrying record id, type and
    local name only (the surface, so an instance false cognate can still be proposed and must
    be caught by evidence); and
  * what the other agent says in answers (attributes, topology) and what the oracle returns.

On its turn an agent may:
  * answer the other's outstanding questions about its own individuals, from its private graph
    (and volunteer descriptions of its own individuals unasked);
  * ask about the other's individuals when it needs their evidence to decide;
  * propose correspondences (my individual <-> one of yours) with a confidence and rationale;
  * ratify or reject proposals the other made about MY individuals (each side is the authority
    on its own side);
  * interrogate ITS OWN individuals through the oracle for one authoritative fact (a serial, a
    hardware address); the answer is returned to both agents, as an experiment verdict is in
    the schema stack;
  * run a virtual provision on a candidate pair of services, confirmed or refuted against the
    semantic invariants (the oracle's ``virtual_provision``); and
  * mark its own individuals it believes have no counterpart.

A correspondence is CONFIRMED only when one side proposes it and the owning side ratifies it,
or when both sides propose it independently, and it is never rejected; a virtual provision
verdict overrides, as in the schema stack. Neither side alone decides a cross-graph
correspondence.

Placements: both_cognitive -> the negotiation above. one_inert / both_inert -> there is no
partner to negotiate with, so these delegate to the single-agent ``InstanceAgentStack``.

The result is an ``InstanceReconciliation``, so the existing scoring (``score_row`` in
pipeline/instance_reconcile.py) applies unchanged. The client is injectable for offline tests.
"""
from __future__ import annotations

import json
import time

from pydantic import BaseModel, Field, create_model

from reconcile.instance import InstanceCase, Oracle, SVC_TYPE
from matching.network_check import OperationOracle
from reconcile.stacks.agent_instance import (EVIDENCE_ALL, InstanceAgentStack,
                                             InstanceReconciliation, _view)

CLOSING_NOTE = ("CLOSING CHECK: both agents declared done, but the individuals listed under "
                "'your_unaccounted_individuals' are yours, are part of this conversation, and are neither in a "
                "settled correspondence nor declared by you to have no counterpart. Account for each one now: "
                "propose its correspondence (and check it where a check is required), or list it under "
                "no_counterpart if the other agent holds nothing that answers to it.")

DEFAULT_MAX_ROUNDS = 8   # one round = A then B; the loop stops early when both declare done


# ---- the structured turn an agent returns ------------------------------------------------
class Answer(BaseModel):
    my_id: str
    attributes: str = ""
    topology: str = ""


class Question(BaseModel):
    their_id: str
    ask: str


class Proposal(BaseModel):
    my_id: str
    their_id: str
    confidence: float
    rationale: str


class Ratification(BaseModel):
    their_id: str   # the proposer's individual id
    my_id: str      # my individual the proposer paired it with
    accept: bool
    reason: str


class Interrogation(BaseModel):
    my_id: str            # one of YOUR OWN individuals
    attribute: str = ""   # the fact wanted; empty to receive all available facts


class Experiment(BaseModel):
    my_id: str      # your service individual
    their_id: str   # the other's service individual to provision it against


class Turn(BaseModel):
    """The full reply format: every tool available."""
    answers: list[Answer]
    questions: list[Question]
    proposals: list[Proposal]
    ratifications: list[Ratification]
    interrogations: list[Interrogation] = Field(default_factory=list)
    experiments: list[Experiment] = Field(default_factory=list)
    no_counterpart: list[str]
    done: bool


def turn_model(interrogation: bool, experiments: bool, live: bool = False):
    """The reply format for a run. It carries a field for a tool only when the agents have that
    tool, so the format, like the prompt, advertises exactly what is available. With live
    observation the field for a test is called 'observations', since nothing is operated."""
    if interrogation and experiments and not live:
        return Turn
    fields = {"answers": (list[Answer], ...), "questions": (list[Question], ...),
              "proposals": (list[Proposal], ...), "ratifications": (list[Ratification], ...)}
    if interrogation:
        fields["interrogations"] = (list[Interrogation], Field(default_factory=list))
    if experiments:
        fields["observations" if live else "experiments"] = (list[Experiment], Field(default_factory=list))
    fields["no_counterpart"] = (list[str], ...)
    fields["done"] = (bool, ...)
    return create_model("Turn", **fields)


def _system(side: str, other: str, operations: bool = False, interrogation: bool = True,
            services: bool = True, stage_note: str = "", confirm=False, live: bool = False) -> str:
    """The system prompt. Each tool is described only if the agents have it in this run."""
    parts = [
        f"You are Agent {side}, the sole authority on graph {side} of ONE network. You are "
        f"reconciling INDIVIDUALS (specific entities) with Agent {other}, who holds graph {other} "
        f"of the same network. The schema is already reconciled, so types are comparable. You see "
        f"your OWN individuals in full; you learn about {other}'s individuals only from its "
        "advertised catalogue (record id, type and local name) and from its answers to your "
        "questions. Decide identity by EVIDENCE, not by name: two individuals can share a local "
        "name and be different entities (do NOT merge them), and two individuals that look "
        "identical in their static record may be different entities.\n\n"
        "Each turn, return: answers to the other's outstanding questions about YOUR individuals "
        "(their attributes, and a short summary of their topology from your graph); you may also "
        "volunteer such descriptions unasked, when that helps the other find the counterpart. "
        f"Questions about {other}'s individuals when you need their evidence to decide. Proposals "
        f"(your individual id <-> one of {other}'s ids) with a confidence in [0,1] and a rationale. "
        "Ratifications of proposals the OTHER made about YOUR individuals: accept only if the "
        "other's individual is truly the same real-world entity as yours, checked against your own "
        "graph -- you are the authority on your side. And the ids of your individuals you believe "
        "have no counterpart."
    ]
    if interrogation:
        parts.append(
            "\n\nYou have live access to your OWN side. List under 'interrogations' any of your own "
            "individuals for which you want one authoritative fact (name the attribute, e.g. serial or "
            "hardware-address, or leave it empty to receive all available facts); the answer is "
            "returned to BOTH of you before the next turn. Use it to separate individuals whose static "
            "records are identical, and ask the other agent to do the same on its side.")
    if operations and live:
        parts.append(
            "\n\nYou may make a DECISIVE LIVE OBSERVATION on any candidate correspondence between ports or "
            f"bundles: list it under 'observations' (your individual id and one of {other}'s ids). An observation "
            "does nothing to the network: nothing is provisioned, changed or taken out of service. The data that "
            "the running network has already recorded for the component (its traffic counters over the same "
            f"intervals) is read through your handle and through {other}'s, and the two readings are compared. "
            "The verdict -- confirmed (the same recorded data: one component), or refuted (different recorded "
            "data: a look-alike, or no counterpart) -- is returned to BOTH of you with the readings before the "
            "next turn and is DECISIVE: trust it over surface judgement. Use it to CONFIRM a correspondence and "
            "to catch look-alike individuals that are actually different. A candidate listed under "
            "'observations' is a test, not a proposal and not a guess: where the static records leave two or "
            "more of the other's individuals equally possible for one of yours, observe one candidate pairing; a "
            "refutation tells you it is another. A correspondence the observation confirms is settled without "
            "further ratification.")
    elif operations:
        # wording follows the schema two-agent stack's decisive-experiment paragraph
        # (agent_twoagent._system, has_oracle), adapted from concepts to individuals.
        parts.append(
            "\n\nYou may run a DECISIVE VIRTUAL EXPERIMENT on any candidate correspondence between ports or "
            f"bundles: list it under 'experiments' (your individual id and one of {other}'s ids). The shared "
            "virtual network will OPERATE that pairing -- take the component out of service through your "
            f"handle and through {other}'s -- and read back whether the SAME real component responded and "
            "whether the invariants a correct correspondence must preserve (owning device, endpoint identity, "
            "connectivity, capacity, layering) hold. The verdict -- confirmed (same component), or refuted (a "
            "look-alike, or no counterpart) -- is returned to BOTH of you before the next turn and is DECISIVE: "
            "trust it over surface judgement. Use it to CONFIRM a correspondence and to catch look-alike "
            "individuals that are actually different. A candidate listed under 'experiments' is a test, not a "
            "proposal and not a guess: where the static records leave two or more of the other's individuals "
            "equally possible for one of yours, test one candidate pairing; a refutation tells you it is "
            "another. A correspondence the experiment confirms is settled without further ratification.")
    elif services:
        parts.append(
            "\n\nFor service individuals you may list a candidate pair under 'experiments': the pairing is "
            "provisioned and read back against the semantic invariants, and the verdict, confirmed or "
            "refuted, is returned to both and is decisive.")
    acts = "answer, ask, propose, ratify" + (", interrogate" if interrogation else "") + \
           ((" or test by observation" if (operations and live) else " or test by experiment") if (operations or services) else "")
    if operations:
        # follows the single-agent instance stack's closer (agent_instance.CLOSER_TOOLS)
        how = "observation" if live else "experiment"
        guess = (f"where identity cannot be settled from the static evidence, test the candidate by "
                 f"{how} rather than guess, and leave it unproposed only if no {how} settles it. "
                 f"Work by proposing, then verifying by {how} where you can; prefer a confirmed "
                 "correspondence to a guessed one.")
    else:
        guess = ("where identity cannot be settled from the evidence, leave the individual unproposed "
                 "rather than guess.")
    parts.append(
        f"\n\nRules: never merge two distinct individuals; {guess} Propose a correspondence at "
        "most once, and use only ids that exist (yours, and the other's advertised ids). Set "
        f"done=true only when nothing remains to {acts}.")
    test = "live observation" if live else "virtual experiment"
    if confirm == "lookalikes":
        parts.append(
            "\n\nLOOK-ALIKES: 'your_lookalikes' lists groups of YOUR individuals that no recorded fact tells "
            "apart (they differ only in local names and ids, which mean nothing to the other agent). The order "
            "in which things are listed is not evidence. A correspondence for any of these individuals is not "
            f"settled by agreement: the protocol puts it to the {test} as soon as it is proposed and ratified, "
            "and returns the verdict to BOTH of you under 'confirmation_results' before the next turn. A refuted "
            "correspondence is withdrawn: the two are not the same component, so propose the alternative.")
    elif confirm:
        parts.append(
            "\n\nCONFIRMATION: agreement between the two of you does not settle a correspondence between "
            "ports or bundles. As soon as one is proposed and ratified, the protocol puts it to the "
            f"{test}, and the verdict is returned to BOTH of you under 'confirmation_results' before the "
            "next turn. A confirmed correspondence is settled. A refuted one is withdrawn: the two are not "
            "the same component, so propose the alternative.")
    if stage_note:
        parts.append("\n\n" + stage_note)
    return "".join(parts)


def _catalogue(individuals: list[dict], evidence: set) -> list[dict]:
    """The public advertisement: surface only (record id, type, and the local name if shown)."""
    out = []
    for i in individuals:
        d = {"id": i["id"], "type": i["type"]}
        if "name" in evidence:
            d["name"] = i["name"]
        out.append(d)
    return out


def _private_view(individuals: list[dict], evidence: set) -> list[dict]:
    out = []
    for i in individuals:
        d = _view(i, evidence)
        d["type"] = i["type"]
        out.append(d)
    return out


def _effort_from_usage(usage) -> dict:
    details = getattr(usage, "completion_tokens_details", None)
    return {
        "total_tokens": getattr(usage, "total_tokens", 0) or 0,
        "reasoning_tokens": (getattr(details, "reasoning_tokens", 0) or 0) if details else 0,
    }


class TwoAgentInstanceStack:
    """Two agents negotiating an instance alignment under information asymmetry."""

    def __init__(self, case: InstanceCase, model: str, evidence: set | None = None,
                 inert_side: str = "b", budget: int | None = None,
                 max_rounds: int = DEFAULT_MAX_ROUNDS, client=None, operations: bool | None = None,
                 interrogation: bool = True, confirm: bool = False, experiment: str = "twin", closing_check: bool = True):
        self.case = case
        self.model = model
        self.evidence = set(EVIDENCE_ALL if evidence is None else evidence)
        self.inert_side = inert_side
        self.budget = budget
        self.max_rounds = max_rounds
        self.closing_check = closing_check    # no conversation closes while an individual in it is unaccounted for
        self.closing_reminders = 2
        self._client = client
        # The virtual operation on ports and bundles is available when the case carries invariant
        # signatures for individuals that are not services (see matching.network_check).
        type_by_truth = {i["_truth"]: i["type"] for i in case.a + case.b}
        has_ops = any(type_by_truth.get(t) != SVC_TYPE
                      for t in case.traps.get("oracle", {}).get("invariants", {}))
        self.operations = has_ops if operations is None else (operations and has_ops)
        # services can be provisioned with the plain oracle wherever the case carries their invariants
        self.services = any(type_by_truth.get(t) == SVC_TYPE
                            for t in case.traps.get("oracle", {}).get("invariants", {}))
        self.interrogation = interrogation   # False withholds interrogation, leaving the operation
        self.experiments = self.operations or self.services
        self.turn_model = None   # built after the experiment kind is known (see below)
        # confirm: every agreed correspondence between operable components is put to the virtual
        # experiment by the protocol before it counts as settled (agreement is not confirmation)
        # experiment: "twin" = a virtual operation on a digital twin; "live" = a non-disruptive comparison
        # of the data the running network has recorded for the component, read through each handle
        self.experiment = experiment if self.operations else "twin"
        assert self.experiment in ("twin", "live")
        # confirm: False | True (every agreed port/bundle correspondence) | "lookalikes" (only those that
        # involve an individual its own side cannot tell apart from another: see matching.anchor)
        self.confirm = (confirm if confirm == "lookalikes" else bool(confirm)) if self.operations else False
        self.test_field = "observations" if self.experiment == "live" else "experiments"
        self.turn_model = turn_model(self.interrogation, self.experiments, live=self.experiment == "live")
        self.anchors: dict = {}            # a_id -> b_id, settled before any conversation (identity anchors)
        self.lookalikes = {"A": [], "B": []}
        self.name = ("two-agent-instance" + ("+op" if self.operations else "") + ("" if interrogation else "-noint")
                     + ("+live" if self.experiment == "live" else "")
                     + ("+confirm-lookalikes" if self.confirm == "lookalikes" else "+confirm" if self.confirm else ""))

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def _turn(self, client, side, other, private, their_catalogue, transcript, extra=None, stage_note=""):
        payload = {
            "your_individuals": private,
            f"agent_{other}_catalogue": their_catalogue,
        }
        if extra:
            payload.update(extra)
        payload["transcript_so_far"] = transcript
        t0 = time.time()
        completion = client.chat.completions.parse(
            model=self.model,
            messages=[{"role": "system", "content": _system(
                          side, other, operations=self.operations,
                          interrogation=self.interrogation, services=self.services,
                          stage_note=stage_note, confirm=self.confirm,
                          live=self.experiment == "live")},
                      {"role": "user", "content": json.dumps(payload, indent=2)}],
            response_format=self.turn_model,
        )
        turn = completion.choices[0].message.parsed
        eff = _effort_from_usage(getattr(completion, "usage", None))
        eff["latency_s"] = round(time.time() - t0, 2)
        return turn, eff

    def use_anchors(self, pairs: dict):
        """Identity anchors, settled before any conversation; and each side's look-alike groups given them."""
        from matching.anchor import lookalike_classes
        self.anchors = dict(pairs)
        self.lookalikes = {"A": lookalike_classes(self.case.a, set(self.anchors)),
                           "B": lookalike_classes(self.case.b, set(self.anchors.values()))}
        self.name += "+anchors"
        return self

    def _new_state(self):
        """Everything a negotiation accumulates; shared across the dialogues of a staged run."""
        case = self.case
        oracle_cls = OperationOracle if self.operations else Oracle
        rec = InstanceReconciliation(placement="both_cognitive", reference_variant="none")
        rec.transcript.append({"step": "prompt", "placement": "both_cognitive",
                               "stack": self.name, "evidence": sorted(self.evidence)})
        oracle = oracle_cls(case, "both_cognitive", inert_side=self.inert_side, budget=self.budget)
        if self.operations:
            oracle.live = self.experiment == "live"
        return {"oracle": oracle,
                "proposed_by": {}, "proposed_conf": {}, "accepts": set(), "rejects": set(),
                "total": {"total_tokens": 0, "reasoning_tokens": 0, "latency_s": 0.0},
                "turns": 0, "rec": rec, "transcripts": [],
                "anchored": {frozenset(p) for p in self.anchors.items()},
                "la": {x for side in ("A", "B") for g in self.lookalikes[side] for x in g}}

    def _dialogue(self, client, st, inds_a, inds_b, extra_a=None, extra_b=None, stage_note="", stage=None):
        """One ask/answer/propose/ratify dialogue over the given individuals of each side."""
        oracle, rec, total = st["oracle"], st["rec"], st["total"]
        proposed_by, proposed_conf = st["proposed_by"], st["proposed_conf"]
        accepts, rejects = st["accepts"], st["rejects"]
        cat_a, cat_b = _catalogue(inds_a, self.evidence), _catalogue(inds_b, self.evidence)
        priv_a, priv_b = _private_view(inds_a, self.evidence), _private_view(inds_b, self.evidence)
        a_ids, b_ids = {i["id"] for i in inds_a}, {i["id"] for i in inds_b}
        own = {"A": a_ids, "B": b_ids}
        transcript: list[dict] = []
        tag = {} if stage is None else {"stage": stage}
        if self.confirm == "lookalikes":      # each agent is told which of ITS OWN individuals are look-alikes
            la_a = [g for g in self.lookalikes["A"] if set(g) & a_ids]
            la_b = [g for g in self.lookalikes["B"] if set(g) & b_ids]
            extra_a = {**(extra_a or {}), "your_lookalikes": la_a}
            extra_b = {**(extra_b or {}), "your_lookalikes": la_b}

        def pair_of(side, my_id, their_id):
            if side == "A":
                return frozenset((my_id, their_id)) if my_id in a_ids and their_id in b_ids else None
            return frozenset((their_id, my_id)) if my_id in b_ids and their_id in a_ids else None

        last_done = {"A": False, "B": False}
        declared_none = {"A": set(), "B": set()}     # individuals an owner has said have no counterpart
        reminders = 0
        extra_a, extra_b = dict(extra_a or {}), dict(extra_b or {})
        for _ in range(self.max_rounds + self.closing_reminders):
            reopened = False   # a refuted confirmation gives the agents another round
            for side, other, private, their_cat, extra in (
                    ("A", "B", priv_a, cat_b, extra_a), ("B", "A", priv_b, cat_a, extra_b)):
                turn, eff = self._turn(client, side, other, private, their_cat, transcript,
                                       extra=extra, stage_note=stage_note)
                st["turns"] += 1
                total["total_tokens"] += eff["total_tokens"]
                total["reasoning_tokens"] += eff["reasoning_tokens"]
                total["latency_s"] += eff["latency_s"]
                for p in turn.proposals:
                    pair = pair_of(side, p.my_id, p.their_id)
                    if pair:
                        proposed_by.setdefault(pair, set()).add(side)
                        proposed_conf[pair] = max(proposed_conf.get(pair, 0.0),
                                                  float(getattr(p, "confidence", 0.0) or 0.0))
                for r in turn.ratifications:
                    pair = pair_of(side, r.my_id, r.their_id)
                    if pair:
                        (accepts if r.accept else rejects).add(pair)
                # live cognition: an agent interrogates its OWN side; both agents see the answer
                interrogation_results = []
                for q in getattr(turn, "interrogations", []):
                    if not self.interrogation:
                        res = {"id": q.my_id, "ok": False, "answer": {},
                               "message": "interrogation is not available in this run"}
                    elif q.my_id not in own[side]:
                        res = {"id": q.my_id, "ok": False, "answer": {},
                               "message": "you may interrogate only your own individuals"}
                    else:
                        r = oracle.interrogate(q.my_id, q.attribute or None)
                        res = {"id": q.my_id, "ok": r.ok, "answer": r.answer, "message": r.message}
                    interrogation_results.append(res)
                    rec.transcript.append({"step": "interrogate", "by": side, **tag,
                                           "args": {"individual_id": q.my_id, "attribute": q.attribute},
                                           "result": res})
                experiment_results = []
                for e in getattr(turn, self.test_field, []):
                    a_id, b_id = (e.my_id, e.their_id) if side == "A" else (e.their_id, e.my_id)
                    if a_id in a_ids and b_id in b_ids:
                        r = oracle.virtual_provision(a_id, b_id)
                        res = {"a_id": a_id, "b_id": b_id, "ok": r.ok, "answer": r.answer, "message": r.message}
                    else:
                        res = {"a_id": a_id, "b_id": b_id, "ok": False, "answer": {},
                               "message": "an experiment needs one of your individuals and one of the other's "
                                          "advertised individuals"}
                    experiment_results.append(res)
                    rec.transcript.append({"step": "virtual_provision", "by": side, **tag,
                                           "args": {"a_id": a_id, "b_id": b_id},
                                           "result": {"ok": res["ok"], "answer": res["answer"],
                                                      "message": res["message"]}})
                confirmation_results = []
                if self.confirm:
                    agreed = [pr for pr, sides in proposed_by.items()
                              if (pr in accepts or len(sides) == 2) and pr not in rejects
                              and pr not in oracle.confirmed_pairs and pr not in oracle.refuted_pairs
                              and pr <= (a_ids | b_ids)]
                    for pr in sorted(agreed, key=sorted):
                        a_id = next(x for x in pr if x in a_ids); b_id = next(x for x in pr if x in b_ids)
                        if not (oracle.operable(a_id) and oracle.operable(b_id)):
                            continue
                        if self.confirm == "lookalikes" and not (a_id in st["la"] or b_id in st["la"]):
                            continue        # determined by evidence: agreement settles it
                        r = oracle.virtual_provision(a_id, b_id)
                        res = {"a_id": a_id, "b_id": b_id, "ok": r.ok, "answer": r.answer, "message": r.message}
                        confirmation_results.append(res)
                        rec.transcript.append({"step": "virtual_provision", "by": "protocol", **tag,
                                               "args": {"a_id": a_id, "b_id": b_id},
                                               "result": {"ok": r.ok, "answer": r.answer, "message": r.message}})
                        if r.ok and not r.answer.get("confirmed"):
                            reopened = True
                entry = {"from": side, **turn.model_dump()}
                if interrogation_results:
                    entry["interrogation_results"] = interrogation_results
                if experiment_results:
                    entry["experiment_results"] = experiment_results
                if confirmation_results:
                    entry["confirmation_results"] = confirmation_results
                transcript.append(entry)
                rec.transcript.append({"step": "turn", "from": side, **tag, "turn": turn.model_dump()})
                last_done[side] = turn.done
                declared_none[side] |= set(turn.no_counterpart) & own[side]
            if last_done["A"] and last_done["B"] and not reopened:
                # closing check: every individual of this conversation must be accounted for by its owner,
                # either in a settled correspondence or declared to have no counterpart
                settled = set().union(*self._confirmed(st)) if self._confirmed(st) else set()
                open_ids = {sd: sorted(own[sd] - settled - declared_none[sd]) for sd in ("A", "B")}
                if not self.closing_check or reminders >= self.closing_reminders or not (open_ids["A"] or open_ids["B"]):
                    extra_a.pop("closing_check", None); extra_b.pop("closing_check", None)
                    if open_ids["A"] or open_ids["B"]:
                        rec.transcript.append({"step": "left_open", **tag, "a": open_ids["A"], "b": open_ids["B"]})
                    break
                reminders += 1
                for sd, ex in (("A", extra_a), ("B", extra_b)):
                    ex["closing_check"] = {
                        "note": CLOSING_NOTE, "your_unaccounted_individuals": open_ids[sd]}
                rec.transcript.append({"step": "closing_check", **tag, "reminder": reminders,
                                       "a": open_ids["A"], "b": open_ids["B"]})
            else:
                extra_a.pop("closing_check", None); extra_b.pop("closing_check", None)
        st["transcripts"].append(transcript)
        if getattr(self, "progress", None):      # one line per finished dialogue, for long runs
            self.progress({"stage": stage, "turns": st["turns"], "total_tokens": total["total_tokens"],
                           "settled": len(self._confirmed(st)), "experiments": oracle.calls["provision"]})

    def _confirmed(self, st) -> set:
        """Proposed AND (ratified by the owner, or proposed by both sides), never rejected; a
        virtual-experiment verdict overrides, as in the schema stack."""
        oracle = st["oracle"]
        confirmed = {pair for pair, sides in st["proposed_by"].items()
                     if (pair in st["accepts"] or len(sides) == 2) and pair not in st["rejects"]}
        confirmed |= set(oracle.confirmed_pairs)
        confirmed -= set(oracle.refuted_pairs)
        return confirmed | st.get("anchored", set())

    def _finish(self, st) -> InstanceReconciliation:
        case, oracle, rec, total = self.case, st["oracle"], st["rec"], st["total"]
        a_ids, b_ids = set(case.a_by_id), set(case.b_by_id)
        confirmed = self._confirmed(st)
        matched = set().union(*confirmed) if confirmed else set()
        rec.submitted = True
        rec.proposed = list(confirmed)
        rec.confidence = {pair: (1.0 if pair in oracle.confirmed_pairs else st["proposed_conf"].get(pair, 0.5))
                          for pair in confirmed}
        rec.residual_a = [i for i in a_ids if i not in matched]
        rec.residual_b = [i for i in b_ids if i not in matched]
        rec.confirmed_pairs = set(oracle.confirmed_pairs)
        rec.oracle_calls = dict(oracle.calls)
        rec.interrogated = set(oracle.interrogated)
        rec.effort = {"total_tokens": total["total_tokens"], "reasoning_tokens": total["reasoning_tokens"],
                      "latency_s": round(total["latency_s"], 2), "model": self.model, "turns": st["turns"],
                      "bilateral_checks": len(st["accepts"]) + len(st["rejects"]),
                      "proposals": len(st["proposed_by"])}
        self.last_transcript = st["transcripts"][-1] if st["transcripts"] else []
        return rec

    def _negotiate(self) -> InstanceReconciliation:
        st = self._new_state()
        self._dialogue(self._get_client(), st, self.case.a, self.case.b)
        return self._finish(st)

    def reconcile(self, placement: str = "both_cognitive") -> InstanceReconciliation:
        if placement == "both_cognitive":
            return self._negotiate()
        # no partner to negotiate with: reconstruct the mute side(s) with the single agent.
        single = InstanceAgentStack(self.case, model=self.model, evidence=self.evidence,
                                    inert_side=self.inert_side, budget=self.budget, client=self._client)
        return single.reconcile(placement=placement)
