"""Generate and carry, for an instance-matched pair of graphs.

The last two steps of the method, applied to individuals. As in the ONSEN demonstrator's
translator, nothing here infers: the agents settled the correspondences once, and the table
they produced is applied deterministically thereafter.

  generate   a translator for each side: the settled correspondences between individuals,
             read A-to-B for agent A's translator and B-to-A for agent B's.
  carry      an instruction that names a component by one agent's record id is translated
             to the other agent's record id and executed on the shared virtual network
             through that agent's handle. The check is on the network, not on the names:
             did the component that went out of service through B's handle turn out to be
             the component that A's instruction named?

The round trip (A to B and back to A) is reported as well. It returns the original for any
one-to-one table, right or wrong, so it cannot show that the right individual was chosen;
only the operation on the network can.
"""
from __future__ import annotations

from reconcile.instance import InstanceCase
from matching.network_check import OperationOracle

OPERATION = "take-out-of-service"


def correspondences_from_transcript(case: InstanceCase, transcript: list[dict]) -> set[frozenset]:
    """The settled correspondences of a saved run, by the stack's own rule: proposed and
    (ratified by the owner, or proposed by both), never rejected; an experiment verdict overrides."""
    a_ids, b_ids = set(case.a_by_id), set(case.b_by_id)
    proposed_by, accepts, rejects, conf, ref = {}, set(), set(), set(), set()

    def pair(side, my, their):
        a, b = (my, their) if side == "A" else (their, my)
        return frozenset((a, b)) if a in a_ids and b in b_ids else None

    for s in transcript:
        if s.get("step") == "turn":
            for p in s["turn"]["proposals"]:
                pr = pair(s["from"], p["my_id"], p["their_id"])
                if pr:
                    proposed_by.setdefault(pr, set()).add(s["from"])
            for r in s["turn"]["ratifications"]:
                pr = pair(s["from"], r["my_id"], r["their_id"])
                if pr:
                    (accepts if r["accept"] else rejects).add(pr)
        elif s.get("step") == "virtual_provision" and s["result"]["ok"]:
            pr = frozenset((s["args"]["a_id"], s["args"]["b_id"]))
            (conf if s["result"]["answer"].get("confirmed") else ref).add(pr)
    out = {pr for pr, sides in proposed_by.items() if (pr in accepts or len(sides) == 2) and pr not in rejects}
    return (out | conf) - ref


def generate(case: InstanceCase, correspondences) -> dict:
    """The two translators: one table, read in each direction."""
    a_ids = set(case.a_by_id)
    a2b, b2a = {}, {}
    for pr in correspondences:
        a = next(x for x in pr if x in a_ids); b = next(x for x in pr if x not in a_ids)
        a2b[a] = b; b2a[b] = a
    return {"a_to_b": a2b, "b_to_a": b2a}


def carry(case: InstanceCase, translators: dict) -> dict:
    """Carry one instruction per operable component A can name, and execute it through B's handle."""
    net = OperationOracle(case, "both_cognitive")
    a2b, b2a = translators["a_to_b"], translators["b_to_a"]
    rows = []
    for ind in case.a:
        a = ind["id"]
        if not net.operable(a):
            continue                                     # no operation is defined on this kind of component
        instruction_a = {"operation": OPERATION, "on": a}
        b = a2b.get(a)
        if b is None:
            rows.append({"instruction": instruction_a, "carried": None, "same_component": False,
                         "round_trip": False, "status": "not carried: no correspondence"})
            continue
        instruction_b = {"operation": OPERATION, "on": b}
        named, responded = net.truth[a], net.truth[b]     # what A named; what went down through B's handle
        rows.append({"instruction": instruction_a, "carried": instruction_b,
                     "same_component": named == responded, "round_trip": b2a.get(b) == a,
                     "named_component": named, "responded_component": responded,
                     "status": "same component" if named == responded else "a different component responded"})
    n = len(rows)
    return {"instructions": n,
            "carried": sum(1 for r in rows if r["carried"]),
            "same_component": sum(1 for r in rows if r["same_component"]),
            "wrong_component": sum(1 for r in rows if r["carried"] and not r["same_component"]),
            "round_trip_ok": sum(1 for r in rows if r["round_trip"]),
            "rows": rows}
