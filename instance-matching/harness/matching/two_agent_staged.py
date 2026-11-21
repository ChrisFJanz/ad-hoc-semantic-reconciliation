"""Staged two-agent instance reconciliation: devices first, then the components of each
settled device, in batches of bounded size.

The unstaged negotiation (``agent_twoagent_instance.TwoAgentInstanceStack``) puts every
individual of both graphs into one dialogue. That is the method in full, and it stops scaling
when a graph no longer fits one turn. This stack keeps the same agents, the same turn
structure (ask, answer, propose, ratify, interrogate, experiment), the same oracle and the
same confirmation rule, and changes one thing: the ORDER in which individuals come up.

  stage 1   one dialogue over the anchor individuals only (the network devices). Each agent's
            device record carries a summary computed from ITS OWN graph: what the device owns,
            and which of the agent's devices it neighbours.
  stage 2   the settled device pairs are taken in batches. Each batch is one dialogue over the
            individuals that the batch's devices own (ports, bundles) or that attach to them
            (links). Each agent also sees, from its own graph, the individuals outside the
            batch that its batch individuals refer to, with the device that owns each, and the
            correspondences settled so far.

Scoping uses only each side's own graph: an individual belongs to the devices it points at
directly, and otherwise to the devices of the individuals it points at. No truth, no key and
no cross-side information enters the scoping. Individuals of devices left unbound in stage 1
stay in the residual.
"""
from __future__ import annotations

from collections import Counter

from matching.two_agent import (TwoAgentInstanceStack, InstanceReconciliation,
                                                      _private_view)

ANCHOR_TYPE = "network-device"

STAGE_NOTE_DEVICES = (
    "STAGE: devices. This dialogue covers network devices only. 'your_device_summaries' gives, for "
    "each of your devices, a summary from your own graph: what the device owns ('owns') and which of "
    "your devices it neighbours ('neighbour_devices'). Ports, bundles and links are handled in later dialogues, "
    "device by device; do not propose them here.")

STAGE_NOTE_BATCH = (
    "STAGE: components of settled devices. The device correspondences are settled; they are listed "
    "under 'settled' (yours <-> theirs), together with any other correspondences settled in earlier "
    "dialogues. This dialogue covers only the individuals owned by, or attached to, the devices "
    "listed under 'batch_devices'. 'context' lists individuals outside this dialogue that yours refer "
    "to, each with the device that owns it. Propose, ratify and test only individuals of this "
    "dialogue: yours, and those in the other's catalogue.")


STAGE_NOTE_ANCHORED = (
    " Some of your individuals on these devices are already settled by a shared identifier; your own records "
    "of them are under 'your_settled_records', and their correspondences are in 'settled'. They are not up "
    "for discussion; use them as fixed points when you reason about the rest.")


class _Scope:
    """Ownership and neighbourhood on ONE side, from that side's graph alone."""

    def __init__(self, individuals: list[dict]):
        self.inds = individuals
        self.by_id = {i["id"]: i for i in individuals}
        self.anchors = [i["id"] for i in individuals if i["type"] == ANCHOR_TYPE]
        anchor_set = set(self.anchors)
        direct = {i["id"]: {r["target"] for r in i["rels"] if r["target"] in anchor_set}
                  for i in individuals if i["id"] not in anchor_set}
        self.owners: dict[str, set] = {}
        for i in individuals:
            iid = i["id"]
            if iid in anchor_set:
                continue
            if direct[iid]:
                self.owners[iid] = set(direct[iid])
            else:   # attached: belongs to the devices of the individuals it points at
                self.owners[iid] = set().union(*[direct.get(r["target"], set()) for r in i["rels"]]) \
                    if i["rels"] else set()
        self.members: dict[str, list] = {a: [] for a in self.anchors}
        for iid, devs in self.owners.items():
            for d in devs:
                self.members[d].append(iid)
        self.neighbours: dict[str, set] = {a: set() for a in self.anchors}
        for iid, devs in self.owners.items():
            reach = set(devs)
            for r in self.by_id[iid]["rels"]:
                reach |= self.owners.get(r["target"], set())
            for d in devs:
                self.neighbours[d] |= reach - {d}

    def device_records(self, evidence) -> list[dict]:
        out = []
        for rec in _private_view([self.by_id[a] for a in self.anchors], evidence):
            d = rec["id"]
            rec["owns"] = dict(Counter(self.by_id[m]["type"] for m in self.members[d]))
            rec["neighbour_devices"] = sorted(self.neighbours[d])
            out.append(rec)
        return out

    def batch(self, devices: list[str]) -> list[dict]:
        seen, out = set(), []
        for d in devices:
            for m in self.members[d]:
                if m not in seen:
                    seen.add(m); out.append(self.by_id[m])
        return out

    def context(self, batch_inds: list[dict]) -> list[dict]:
        inside = {i["id"] for i in batch_inds}
        out, seen = [], set()
        for i in batch_inds:
            for r in i["rels"]:
                t = r["target"]
                if t in inside or t in seen or t not in self.by_id or self.by_id[t]["type"] == ANCHOR_TYPE:
                    continue
                seen.add(t)
                out.append({"id": t, "type": self.by_id[t]["type"], "name": self.by_id[t].get("name"),
                            "owned_by": sorted(self.owners.get(t, set()))})
        return out


class StagedTwoAgentInstanceStack(TwoAgentInstanceStack):
    """Devices first, then the components of the settled devices in batches. A batch takes
    neighbouring devices until their components on side A would exceed ``batch_size`` (a device
    larger than that forms a batch on its own), so dialogues stay near one size whatever the
    devices' port counts."""

    def __init__(self, *args, batch_size: int = 60, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = max(1, int(batch_size))
        self.name += f"+staged{self.batch_size}"

    def _device_view(self, client, st, sa: _Scope, sb: _Scope):
        """Stage 1: the unstaged dialogue restricted to devices, each carrying its own-graph summary."""
        dev_a = [sa.by_id[a] for a in sa.anchors]
        dev_b = [sb.by_id[b] for b in sb.anchors]
        st["rec"].transcript.append({"step": "stage", "stage": 0, "kind": "devices",
                                     "n_a": len(dev_a), "n_b": len(dev_b)})
        summ_a = {r["id"]: {"owns": r["owns"], "neighbour_devices": r["neighbour_devices"]}
                  for r in sa.device_records(self.evidence)}
        summ_b = {r["id"]: {"owns": r["owns"], "neighbour_devices": r["neighbour_devices"]}
                  for r in sb.device_records(self.evidence)}
        self._dialogue(client, st, dev_a, dev_b,
                       extra_a={"your_device_summaries": summ_a}, extra_b={"your_device_summaries": summ_b},
                       stage_note=STAGE_NOTE_DEVICES, stage=0)

    @staticmethod
    def _order(pairs: dict, sa: _Scope) -> list[str]:
        """Bound A devices, neighbours kept together (breadth-first over A's own adjacency)."""
        todo, order, seen = [a for a in sa.anchors if a in pairs], [], set()
        for start in todo:
            if start in seen:
                continue
            queue = [start]; seen.add(start)
            while queue:
                d = queue.pop(0); order.append(d)
                for n in sorted(sa.neighbours[d]):
                    if n in pairs and n not in seen:
                        seen.add(n); queue.append(n)
        return order

    def _negotiate(self) -> InstanceReconciliation:
        client, case = self._get_client(), self.case
        st = self._new_state()
        sa, sb = _Scope(case.a), _Scope(case.b)
        a_ids = set(case.a_by_id)
        anch_a, anch_b = set(self.anchors), set(self.anchors.values())

        def split(pairs):
            return [(next(x for x in p if x in a_ids), next(x for x in p if x not in a_ids)) for p in pairs]

        # ---- devices: those an identity anchor already settled need no conversation
        if not (set(sa.anchors) <= anch_a and set(sb.anchors) <= anch_b):
            if self.anchors:
                dev_a = [sa.by_id[a] for a in sa.anchors if a not in anch_a]
                dev_b = [sb.by_id[b] for b in sb.anchors if b not in anch_b]
                st["rec"].transcript.append({"step": "stage", "stage": 0, "kind": "devices",
                                             "n_a": len(dev_a), "n_b": len(dev_b)})
                self._dialogue(client, st, dev_a, dev_b, stage_note=STAGE_NOTE_DEVICES, stage=0,
                               extra_a={"settled": [{"yours": a, "theirs": b} for a, b in split(self._confirmed(st))]},
                               extra_b={"settled": [{"yours": b, "theirs": a} for a, b in split(self._confirmed(st))]})
            else:
                self._device_view(client, st, sa, sb)
        dev_pairs = {a: b for a, b in split(self._confirmed(st)) if a in sa.members and b in sb.members}

        # ---- components: only what no anchor settled comes up in conversation
        def open_a(d):
            return [m for m in sa.members[d] if m not in anch_a]

        order = [d for d in self._order(dev_pairs, sa) if open_a(d)]
        batches, cur, size = [], [], 0
        for d in order:
            m = len(open_a(d))
            if cur and size + m > self.batch_size:
                batches.append(cur); cur, size = [], 0
            cur.append(d); size += m
        if cur:
            batches.append(cur)
        for k, devs_a in enumerate(batches, start=1):
            devs_b = [dev_pairs[a] for a in devs_a]
            all_a, all_b = sa.batch(devs_a), sb.batch(devs_b)
            inds_a = [i for i in all_a if i["id"] not in anch_a]
            inds_b = [i for i in all_b if i["id"] not in anch_b]
            settled = split(self._confirmed(st))
            ctx_a, ctx_b = sa.context(all_a), sb.context(all_b)
            keep_a = set(sa.anchors) | {c["id"] for c in ctx_a} | {i["id"] for i in all_a}
            keep_b = set(sb.anchors) | {c["id"] for c in ctx_b} | {i["id"] for i in all_b}
            st["rec"].transcript.append({"step": "stage", "stage": k, "kind": "batch",
                                         "devices_a": devs_a, "devices_b": devs_b,
                                         "n_a": len(inds_a), "n_b": len(inds_b)})
            xa = {"batch_devices": devs_a, "context": ctx_a,
                  "settled": [{"yours": a, "theirs": b} for a, b in settled if a in keep_a]}
            xb = {"batch_devices": devs_b, "context": ctx_b,
                  "settled": [{"yours": b, "theirs": a} for a, b in settled if b in keep_b]}
            if self.anchors:   # the agent's own records of what is already settled on these devices
                xa["your_settled_records"] = _private_view([i for i in all_a if i["id"] in anch_a], self.evidence)
                xb["your_settled_records"] = _private_view([i for i in all_b if i["id"] in anch_b], self.evidence)
            self._dialogue(client, st, inds_a, inds_b, extra_a=xa, extra_b=xb,
                           stage_note=STAGE_NOTE_BATCH + (STAGE_NOTE_ANCHORED if self.anchors else ""), stage=k)
        rec = self._finish(st)
        rec.transcript.append({"step": "staging", "stages": len([x for x in rec.transcript if x.get("step") == "stage"]),
                               "devices_bound": len(dev_pairs), "batch_size": self.batch_size,
                               "anchored": len(self.anchors),
                               "lookalikes_a": sum(len(g) for g in self.lookalikes["A"]),
                               "lookalikes_b": sum(len(g) for g in self.lookalikes["B"])})
        return rec
