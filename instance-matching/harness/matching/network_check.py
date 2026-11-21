"""The virtual operation, extended from services to any operable individual.

``reconcile.instance.Oracle.virtual_provision`` exercises a candidate correspondence between
two *services* by a provision-and-read-back against semantic invariants. This module keeps
that mechanism and lifts the one restriction: an individual of any type can be exercised if
the case carries an invariant signature for it. The operation is the instance-level form of
"an instruction issued on either side must act on the same component": the candidate pair is
operated in the shared virtual network through A's handle and through B's, the objects are
read back, and the pairing is confirmed only if the same real component responded and every
invariant holds in place.

Nothing else changes: availability follows the cognition placement, every call is counted
under ``provision``, confirmed and refuted pairs are tracked, and the hidden truth and the
invariant signatures stay inside the oracle.
"""
from __future__ import annotations

from reconcile.instance import Oracle, OracleResult


class OperationOracle(Oracle):
    """``live`` selects what an experiment IS. False (the default): a virtual operation on a digital
    twin of the network, where the component is taken out of service through each handle. True: a
    live, non-disruptive experiment on the running network, where nothing is provisioned or
    operated and the data the network has recorded for the component is read through each handle
    and compared."""

    live = False

    def operable(self, ind_id: str) -> bool:
        return self.truth.get(ind_id) in self.invariants

    def recorded(self, ind_id: str) -> dict:
        """What the running network has recorded for the component behind this handle: traffic
        counters over the same three intervals. It belongs to the component, so it reads the same
        through either agent's handle, and differs between components, look-alikes included."""
        import hashlib
        h = hashlib.sha256(("recorded:" + str(self.truth.get(ind_id))).encode()).digest()
        octets = [int.from_bytes(h[i:i + 5], "big") % 9_000_000_000 + 1_000_000_000 for i in (0, 5, 10)]
        return {"in-octets": octets, "intervals": ["t-2", "t-1", "t"]}

    def compare_recorded(self, a_id: str, b_id: str) -> OracleResult:
        self.calls["provision"] += 1
        ra, rb = self.recorded(a_id), self.recorded(b_id)
        pair = frozenset((a_id, b_id))
        same = ra == rb
        (self.confirmed_pairs if same else self.refuted_pairs).add(pair)
        res = OracleResult(True, "provision",
                           answer={"confirmed": same, "recorded_through_A": ra, "recorded_through_B": rb},
                           message=("the data recorded through both handles is the same: one component" if same else
                                    "the data recorded through the two handles differs: two different components"))
        self.log.append({"call": "compare_recorded", "a_id": a_id, "b_id": b_id, "answer": res.answer})
        return res

    def virtual_provision(self, a_id: str, b_id: str) -> OracleResult:
        if not self._budget_left():
            return OracleResult(False, "provision", message="oracle budget exhausted")
        if a_id not in self.a_ids or b_id not in self.b_ids:
            return OracleResult(False, "provision",
                                message="a virtual operation needs one id from each side (a_id from A, b_id from B)")
        if self.placement == "both_inert":
            return OracleResult(False, "provision", message="both sides inert: no live system to operate on")
        if not (self.operable(a_id) and self.operable(b_id)):
            return OracleResult(False, "provision",
                                message="no virtual operation is defined for one of these individuals; "
                                        "interrogate it instead")
        if self.live:
            return self.compare_recorded(a_id, b_id)
        self.calls["provision"] += 1
        ta, tb = self.truth.get(a_id), self.truth.get(b_id)
        inv_a, inv_b = self.invariants.get(ta, {}), self.invariants.get(tb, {})
        diverging = sorted(k for k in set(inv_a) | set(inv_b) if inv_a.get(k) != inv_b.get(k))
        pair = frozenset((a_id, b_id))
        if ta == tb and not diverging:
            self.confirmed_pairs.add(pair)
            res = OracleResult(True, "provision", answer={"confirmed": True, "invariants_preserved": True},
                               message="the same component responded on both sides; all invariants preserved in place")
        else:
            self.refuted_pairs.add(pair)
            detail = {k: {"A": inv_a.get(k), "B": inv_b.get(k)} for k in diverging}
            res = OracleResult(True, "provision",
                               answer={"confirmed": False, "diverging_invariants": detail},
                               message=("invariants diverge: the two are not the same component" if diverging else
                                        "a different component responded on each side: the two are not the same "
                                        "component, although their invariants agree"))
        self.log.append({"call": "virtual_provision", "a_id": a_id, "b_id": b_id, "answer": res.answer})
        return res
