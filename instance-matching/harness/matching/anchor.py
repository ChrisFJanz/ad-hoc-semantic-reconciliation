"""Anchor first, and know the look-alikes: two mechanical steps before any conversation.

  anchor_join         Identity anchors. The model step settled which terms correspond and which of them
                      carry a value unchanged (the term rules). Where such a term is an identifier
                      that each side records for its individuals, and a value occurs exactly once on
                      each side, on individuals of the same reconciled type, the two individuals are
                      matched. No model call, no conversation.
  lookalike_classes   Look-alikes, on ONE side's own graph. Colour refinement: every individual starts
                      with what is recorded about it apart from its own local name and id (which do
                      not cross to the other side), anchored individuals start with their identity,
                      and each round adds the colours of what it is related to. Individuals that end
                      with the same colour cannot be told apart by any recorded fact. A match for one
                      of them is UNDERDETERMINED by the evidence: it needs an experiment or an
                      observation. Everything else is determined by evidence.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict

from reconcile.instance import InstanceCase


def anchor_join(case: InstanceCase, term_rules: list[dict], binding: dict) -> tuple[dict, list[dict]]:
    """-> ({a_id: b_id}, [why each pair was made])."""
    pairs, why = {}, []
    taken_b = set()
    for rule in term_rules:
        if rule.get("value_rule") != "identity":
            continue
        wa, wb = binding["a"].get(rule["a_id"]), binding["b"].get(rule["b_id"])
        if not wa or not wb:
            continue                                   # a term neither graph records a value for
        va, vb = defaultdict(list), defaultdict(list)
        for ind in case.a:
            if ind["type"] in wa["types"] and wa["field"] in ind["attrs"]:
                va[(ind["type"], str(ind["attrs"][wa["field"]]))].append(ind["id"])
        for ind in case.b:
            if ind["type"] in wb["types"] and wb["field"] in ind["attrs"]:
                vb[(ind["type"], str(ind["attrs"][wb["field"]]))].append(ind["id"])
        for key, a_ids in va.items():
            b_ids = vb.get(key, [])
            if len(a_ids) == 1 and len(b_ids) == 1 and a_ids[0] not in pairs and b_ids[0] not in taken_b:
                pairs[a_ids[0]] = b_ids[0]; taken_b.add(b_ids[0])
                why.append({"a": a_ids[0], "b": b_ids[0], "term_a": rule["a_id"], "term_b": rule["b_id"], "value": key[1]})
    return pairs, why


def _h(x) -> str:
    return hashlib.sha1(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()[:16]


def lookalike_classes(individuals: list[dict], anchored: set | None = None, rounds: int = 6) -> list[list[str]]:
    """Groups (size > 1) of this side's individuals that no recorded fact tells apart."""
    anchored = anchored or set()
    by_id = {i["id"]: i for i in individuals}
    incoming = defaultdict(list)
    for i in individuals:
        for r in i["rels"]:
            if r["target"] in by_id:
                incoming[r["target"]].append((r["rel"], i["id"]))
    colour = {i["id"]: (_h(("anchored", i["id"])) if i["id"] in anchored
                        else _h((i["type"], sorted(i["attrs"].items())))) for i in individuals}
    for _ in range(rounds):
        new = {}
        for i in individuals:
            iid = i["id"]
            if iid in anchored:
                new[iid] = colour[iid]; continue
            out = sorted((r["rel"], colour[r["target"]]) for r in i["rels"] if r["target"] in by_id)
            inc = sorted((rel, colour[src]) for rel, src in incoming[iid])
            new[iid] = _h((colour[iid], out, inc))
        if len(set(new.values())) == len(set(colour.values())):
            colour = new; break
        colour = new
    groups = defaultdict(list)
    for iid, c in colour.items():
        if iid not in anchored:
            groups[c].append(iid)
    return sorted([sorted(g) for g in groups.values() if len(g) > 1])


def withhold(case: InstanceCase, fields_a=("ipv4-address",), fields_b=("ip-address",)) -> InstanceCase:
    """A copy of the case in which neither graph records the given identifier fields. Truth is untouched."""
    import copy
    c = copy.deepcopy(case)
    for ind in c.a:
        for f in fields_a:
            ind["attrs"].pop(f, None)
    for ind in c.b:
        for f in fields_b:
            ind["attrs"].pop(f, None)
    return c


def shuffled(case: InstanceCase, seed: int) -> InstanceCase:
    """A copy of the case in which each side lists its individuals, and each individual its relations,
    in an order drawn at random. Nothing recorded changes; only the order things happen to be listed in."""
    import copy
    import random
    c = copy.deepcopy(case)
    rng = random.Random(seed)
    for side in (c.a, c.b):
        rng.shuffle(side)
        for ind in side:
            rng.shuffle(ind["rels"])
    return c
