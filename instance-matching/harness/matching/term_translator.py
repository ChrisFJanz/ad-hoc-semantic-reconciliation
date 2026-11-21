"""Generate, at the level of the models: a translator for the terms, and its use on observations.

Reconciliation settles WHICH concept of one model corresponds to which concept of the other. To
carry a value across, the translator also has to say HOW a value of the one is written as a value
of the other (unchanged, or rescaled between units). That is the generate step. As in the ONSEN
demonstrator, one call produces a table, and the table is applied deterministically thereafter.

  generate_term_rules   one model call: the settled correspondences and both lifted models in, one
                        value rule per correspondence out.
  carry_observations    no model call: each value agent B holds about a component is rewritten in
                        agent A's term, unit and individual, using the term rules and the matched
                        individuals, and compared with what agent A itself records for that component.

An observation about an individual that has no counterpart on the other side (a link object, in a
model that has none) is restated on the counterparts of the individuals it points to (its two end
ports). This is the instance-level form of the correspondence between a link and an adjacency
learned on a port.
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel

from reconcile.instance import InstanceCase

GENERATE_SYSTEM = (
    "You are generating a translator between two data models of ONE network, model A and model B. The "
    "correspondences between their concepts are already settled and are given to you, with both lifted "
    "models (each concept's label, kind, gloss, example, relations and instances). For EACH settled "
    "correspondence, state how a VALUE of the A concept is rewritten as a value of the B concept: "
    "'identity' if the value is carried unchanged; 'scale' if both are quantities in different units, "
    "giving a_to_b_factor such that B value = A value x a_to_b_factor, and naming each unit; "
    "'not-a-value' if the concepts are entities or relations and carry no value of their own. Take the "
    "units from the models as given; do not assume a unit that a model does not state or show. Return "
    "one rule for every correspondence, using the same concept ids.")


class TermRule(BaseModel):
    a_id: str
    b_id: str
    value_rule: Literal["identity", "scale", "not-a-value"]
    a_to_b_factor: float
    a_unit: str
    b_unit: str
    note: str


class TermRules(BaseModel):
    rules: list[TermRule]


def _concepts(model) -> list[dict]:
    return [{"id": c.id, "label": c.label, "kind": c.kind, "gloss": c.gloss, "example": c.example,
             "relations": list(c.relations), "instances": list(c.instances)} for c in model.concepts]


def generate_term_rules(model_a, model_b, correspondences, model: str, client=None) -> tuple[list[dict], dict]:
    if client is None:
        from openai import OpenAI
        client = OpenAI()
    a_ids = {c.id for c in model_a.concepts}
    pairs = [{"a_id": next(x for x in p if x in a_ids), "b_id": next(x for x in p if x not in a_ids)}
             for p in sorted(map(sorted, correspondences))]
    payload = {"model_A": _concepts(model_a), "model_B": _concepts(model_b), "settled_correspondences": pairs}
    comp = client.chat.completions.parse(
        model=model,
        messages=[{"role": "system", "content": GENERATE_SYSTEM},
                  {"role": "user", "content": json.dumps(payload, indent=2)}],
        response_format=TermRules)
    rules = [r.model_dump() for r in comp.choices[0].message.parsed.rules]
    want = {(p["a_id"], p["b_id"]) for p in pairs}
    rules = [r for r in rules if (r["a_id"], r["b_id"]) in want]
    usage = getattr(comp, "usage", None)
    return rules, {"total_tokens": getattr(usage, "total_tokens", 0) or 0, "rules": len(rules), "asked": len(pairs)}


def _to_a(value, rule):
    if rule["value_rule"] == "identity":
        return value
    if rule["value_rule"] == "scale" and rule["a_to_b_factor"]:
        v = float(value) / rule["a_to_b_factor"]
        return int(round(v)) if abs(v - round(v)) < 1e-6 else v
    return None


def carry_observations(case: InstanceCase, rules: list[dict], translators: dict, binding: dict) -> dict:
    """Agent B reports each value it holds; the translators restate it for agent A; compare with A's record."""
    b2a = translators["b_to_a"]
    a_by, b_by = case.a_by_id, case.b_by_id
    rule_for_b = {r["b_id"]: r for r in rules}
    rows = []
    for b_concept, where in binding["b"].items():
        rule = rule_for_b.get(b_concept)
        a_where = binding["a"].get(rule["a_id"]) if rule else None
        for ind in case.b:
            if ind["type"] not in where["types"] or where["field"] not in ind["attrs"]:
                continue
            value = ind["attrs"][where["field"]]
            row = {"observed": {"concept": b_concept, "on": ind["id"], "value": value, "unit": where["unit"]}}
            if not rule or not a_where or rule["value_rule"] == "not-a-value":
                row.update(status="not carried: no value rule for this term", agrees=False, carried=None)
                rows.append(row); continue
            subjects = [b2a[ind["id"]]] if ind["id"] in b2a else \
                [b2a[r["target"]] for r in ind["rels"] if r["target"] in b2a]
            subjects = [s for s in subjects if a_by[s]["type"] in a_where["types"]]
            if not subjects:
                row.update(status="not carried: no matched individual to state it on", agrees=False, carried=None)
                rows.append(row); continue
            a_value = _to_a(value, rule)
            recorded = [a_by[s]["attrs"].get(a_where["field"]) for s in subjects]
            agrees = all(str(x) == str(a_value) for x in recorded)
            row.update(carried={"concept": rule["a_id"], "on": subjects, "value": a_value, "unit": a_where["unit"]},
                       recorded_by_a=recorded, agrees=agrees,
                       status="agrees with agent A's own record" if agrees else "differs from agent A's own record")
            rows.append(row)
    by = {}
    for r in rows:
        k = r["observed"]["concept"]
        d = by.setdefault(k, {"observations": 0, "carried": 0, "agree": 0})
        d["observations"] += 1; d["carried"] += bool(r["carried"]); d["agree"] += bool(r["agrees"])
    return {"observations": len(rows), "carried": sum(1 for r in rows if r["carried"]),
            "agree": sum(1 for r in rows if r["agrees"]),
            "differ": sum(1 for r in rows if r["carried"] and not r["agrees"]), "by_term": by, "rows": rows}
