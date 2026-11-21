"""Keeping bindings: what happens to a binding already made when the network or a record changes.

A binding says that A's handle and B's handle denote one component. It is VALID while both handles
exist and denote the same component, and VOID otherwise. This module holds, with no model call:

  the events      changes applied to a bound network. Some void bindings (a handle is renamed, two
                  handles are re-keyed, a component is decommissioned). Some leave every binding
                  valid and only change what is recorded (an address is changed or moved, two cables
                  are exchanged). The second kind is there to count false alarms.
  the mechanisms  ways to find a void binding that need no reasoning:
                    on_use      a handle that no longer resolves is noticed when it is next used
                    identifiers the identity anchor is run again on the current records
                    relations   the relations each side records are carried across the bindings and
                                compared (A's neighbour relation against B's links)
                  Each of the three sweeps also notices a handle that no longer resolves.
                    observation data the network has recorded is read through both handles of every
                                binding and compared
  own_record_change  what the side where an event happened can see in its own record, which is all
                     that side can announce when its system gives it no change log.

Truth (which component a handle denotes) is used only to apply events and to score. The mechanisms
read the published records, and the observation reads the network through a handle.
"""
from __future__ import annotations

import copy
import hashlib
import json
import random
from dataclasses import dataclass, field, replace

from reconcile.instance import InstanceCase

from matching.anchor import anchor_join

IP = {"a": "ipv4-address", "b": "ip-address"}
PORT, BUNDLE, DEVICE, LINK = "physical-port", "link-bundle", "network-device", "link"


# ------------------------------------------------------------------------------------------ state
@dataclass
class State:
    a: list[dict]
    b: list[dict]
    bindings: dict[str, str]                      # A handle -> B handle, as made at matching time
    log: list[dict] = field(default_factory=list)  # events applied, with what each side's system knows

    def side(self, s: str) -> list[dict]:
        return self.a if s == "a" else self.b

    def by_id(self, s: str) -> dict:
        return {i["id"]: i for i in self.side(s)}

    def truth(self) -> dict:
        return {i["id"]: i["_truth"] for i in self.a + self.b}

    def handle_of(self, s: str, truth: str) -> str | None:
        for i in self.side(s):
            if i["_truth"] == truth:
                return i["id"]
        return None


def initial_state(case: InstanceCase) -> State:
    """The network as matched: every individual bound, correctly (the recorded runs all ended there)."""
    return State(copy.deepcopy(case.a), copy.deepcopy(case.b),
                 {c["a"]: c["b"] for c in case.gold["correspondences"]})


def void_bindings(st: State) -> set[str]:
    """A handles of bindings that are void in this state."""
    t, out = st.truth(), set()
    for a, b in st.bindings.items():
        if a not in t or b not in t or t[a] != t[b]:
            out.add(a)
    return out


def true_rebinding(st: State) -> dict[str, str]:
    """For every component both sides still record: the binding that is right now, keyed by A handle."""
    tb = {i["_truth"]: i["id"] for i in st.b}
    return {i["id"]: tb[i["_truth"]] for i in st.a if i["_truth"] in tb}


def published(individuals: list[dict]) -> list[dict]:
    """A record as its side publishes it: no hidden truth, and in an order that carries no information."""
    out = []
    for i in individuals:
        j = {k: v for k, v in i.items() if k != "_truth"}
        j["rels"] = sorted(j["rels"], key=lambda r: (r["rel"], r["target"]))
        out.append(j)
    return sorted(out, key=lambda i: i["id"])


# ----------------------------------------------------------------------------------------- events
def _retarget(individuals: list[dict], mapping: dict[str, str]) -> None:
    for i in individuals:
        for r in i["rels"]:
            r["target"] = mapping.get(r["target"], r["target"])


def _mint(s: str, old: str, n: int) -> str:
    h = hashlib.sha1(("%s:%d" % (old, n)).encode()).hexdigest()[:8]
    if s == "b":
        return old.split("-")[0] + "-" + h          # b.tp-xxxxxxxx, b.node-xxxxxxxx
    head, _, tail = old.rpartition("/")
    return (head + "/" if head else "") + tail + "-r" + h[:3]


def ev_rename(st: State, s: str, hid: str) -> State:
    """One side gives an individual a new handle. The old handle no longer resolves. VOIDS 1 binding."""
    st = copy.deepcopy(st)
    new = _mint(s, hid, len(st.log))
    ind = st.by_id(s)[hid]
    ind["id"], ind["name"] = new, new.split(".", 1)[1].rpartition("/")[2] if s == "a" else new.split(".", 1)[1]
    _retarget(st.side(s), {hid: new})
    st.log.append({"kind": "rename", "side": s, "old": hid, "new": new})
    return st


def ev_rekey(st: State, s: str, h1: str, h2: str) -> State:
    """One side's system re-keys: the two handles exchange the components they denote (an index is
    renumbered, identifiers are minted again in another order). Both handles still resolve. VOIDS 2
    bindings, silently."""
    st = copy.deepcopy(st)
    by = st.by_id(s)
    i1, i2 = by[h1], by[h2]
    for k in ("type", "key", "attrs", "rels", "_truth"):
        i1[k], i2[k] = i2[k], i1[k]
    others = [i for i in st.side(s)]
    _retarget(others, {h1: h2, h2: h1})
    # the two exchanged their own relation lists above, and the line before swapped h1/h2 inside them
    # too, which is right: a relation that pointed from one to the other now points the other way
    st.log.append({"kind": "rekey", "side": s, "map": {h1: h2, h2: h1}})
    return st


def ev_decommission(st: State, truth: str) -> State:
    """A port is taken out of the network. Both records drop it. VOIDS 1 binding (both handles gone)."""
    st = copy.deepcopy(st)
    for s in ("a", "b"):
        hid = st.handle_of(s, truth)
        gone = {hid}
        if s == "b":                                 # a link with a removed end is removed with it
            gone |= {i["id"] for i in st.b if i["type"] == LINK and any(r["target"] == hid for r in i["rels"])}
        keep = [i for i in st.side(s) if i["id"] not in gone]
        for i in keep:
            i["rels"] = [r for r in i["rels"] if r["target"] not in gone]
        if s == "a":
            st.a = keep
        else:
            st.b = keep
    st.log.append({"kind": "decommission", "component": truth})
    return st


def ev_readdress(st: State, truth: str, new_ip: str, stale: str | None = None) -> State:
    """A component's address is changed. No binding is void. ``stale`` names a side whose record has
    not been refreshed yet."""
    st = copy.deepcopy(st)
    for s in ("a", "b"):
        if s != stale:
            st.by_id(s)[st.handle_of(s, truth)]["attrs"][IP[s]] = new_ip
    st.log.append({"kind": "readdress", "component": truth, "stale": stale})
    return st


def ev_move_address(st: State, t1: str, t2: str, stale: str | None = None) -> State:
    """Two components exchange their addresses. No binding is void."""
    st = copy.deepcopy(st)
    for s in ("a", "b"):
        if s != stale:
            by = st.by_id(s)
            i1, i2 = by[st.handle_of(s, t1)], by[st.handle_of(s, t2)]
            i1["attrs"][IP[s]], i2["attrs"][IP[s]] = i2["attrs"][IP[s]], i1["attrs"][IP[s]]
    st.log.append({"kind": "move_address", "components": [t1, t2], "stale": stale})
    return st


def ev_cable_swap(st: State, t1: str, t2: str, stale: str | None = None) -> State:
    """The cables on two ports of one router are exchanged at that end. Each port is still the port it
    was, so no binding is void; what changes is what each is connected to."""
    st = copy.deepcopy(st)
    if stale != "a":
        by = st.by_id("a")
        m1, m2 = by[st.handle_of("a", t1)], by[st.handle_of("a", t2)]
        n1 = next(r for r in m1["rels"] if r["rel"] == "lldp-neighbour")
        n2 = next(r for r in m2["rels"] if r["rel"] == "lldp-neighbour")
        r1, r2 = by[n1["target"]], by[n2["target"]]
        n1["target"], n2["target"] = r2["id"], r1["id"]
        for far, near in ((r1, m2), (r2, m1)):
            next(r for r in far["rels"] if r["rel"] == "lldp-neighbour")["target"] = near["id"]
    if stale != "b":
        h1, h2 = st.handle_of("b", t1), st.handle_of("b", t2)
        for i in st.b:
            if i["type"] == LINK:
                for r in i["rels"]:
                    if r["target"] in (h1, h2):
                        r["target"] = h2 if r["target"] == h1 else h1
    st.log.append({"kind": "cable_swap", "components": [t1, t2], "stale": stale})
    return st


# ------------------------------------------------------------------------------------- mechanisms
@dataclass
class Finding:
    flagged: set[str]                                  # A handles of bindings reported as suspect
    repairs: dict[str, str] = field(default_factory=dict)   # A handle -> B handle proposed in its place
    cost: dict = field(default_factory=dict)


def _dangling(st: State) -> set[str]:
    a_ids, b_ids = set(st.by_id("a")), set(st.by_id("b"))
    return {a for a, b in st.bindings.items() if a not in a_ids or b not in b_ids}


def on_use(st: State) -> Finding:
    """A handle that no longer resolves is noticed the next time the binding is used."""
    return Finding(_dangling(st))


def identifiers(st: State, case: InstanceCase, term_rules: list[dict], data_binding: dict) -> Finding:
    """The identity anchor, run again on the current records. A binding is suspect when the identifiers
    now pair one of its handles with a different handle. The new pairs are proposed as repairs."""
    pairs, _ = anchor_join(replace(case, a=st.a, b=st.b), term_rules, data_binding)
    by_b = {b: a for a, b in pairs.items()}
    flagged, repairs = set(), {}
    a_ids = set(st.by_id("a"))
    for a, b in st.bindings.items():
        if a in pairs and pairs[a] != b:
            flagged.add(a); repairs[a] = pairs[a]
        elif b in by_b and by_b[b] != a:
            flagged.add(a)
    for a, b in pairs.items():                         # a handle the bindings do not know, paired by identifier
        if a not in st.bindings and a in a_ids:
            repairs[a] = b
    return Finding(flagged | _dangling(st), repairs, {"values_compared": len(st.a) + len(st.b)})


def relations(st: State) -> Finding:
    """Carry A's neighbour relation across the bindings and look for it among B's links, and the
    reverse. Where the two records disagree, the bindings at both ends are suspect: the disagreement
    says that something is wrong there and does not say which binding."""
    a_ids, b_ids = set(st.by_id("a")), set(st.by_id("b"))
    links = {frozenset(r["target"] for r in i["rels"] if r["rel"] in ("source-tp", "dest-tp"))
             for i in st.b if i["type"] == LINK}
    inv = {b: a for a, b in st.bindings.items()}
    flagged, checked = set(), 0
    a_pairs = set()
    for i in st.a:
        for r in i["rels"]:
            if r["rel"] == "lldp-neighbour":
                a_pairs.add(frozenset((i["id"], r["target"])))
    for pair in a_pairs:
        checked += 1
        ends = list(pair)
        mapped = [st.bindings.get(e) for e in ends]
        if None in mapped or any(m not in b_ids for m in mapped):
            continue                                   # a dangling handle is the business of on_use
        if frozenset(mapped) not in links:
            flagged |= set(ends)
    port_type = {i["id"]: i["type"] for i in st.b}
    for link in links:
        if any(port_type.get(e) != PORT for e in link):
            continue                                   # a link between bundles: A records no relation for it
        checked += 1
        ends = [inv.get(e) for e in link]
        if None in ends or any(e not in a_ids for e in ends):
            continue
        if frozenset(ends) not in a_pairs:
            flagged |= set(ends)
    return Finding({a for a in flagged if a in st.bindings} | _dangling(st), {}, {"relations_compared": checked})


def recorded(st: State, hid: str):
    """What the running network has recorded for the component behind a handle (the stand-in used
    for a live observation in the matching runs: it belongs to the component)."""
    t = st.truth().get(hid)
    return None if t is None else hashlib.sha256(("recorded:" + t).encode()).hexdigest()


def observation(st: State, only: set[str] | None = None, repair: bool = True) -> Finding:
    """Read recorded data through both handles of each binding (all of them, or only those named) and
    compare. A binding whose two readings differ is void. Then, for the void ones, read through the
    handles left open on the other side to find where each belongs."""
    flagged, n = set(), 0
    for a, b in st.bindings.items():
        if only is not None and a not in only:
            continue
        ra, rb = recorded(st, a), recorded(st, b)
        if ra is None or rb is None:
            flagged.add(a); continue
        n += 1
        if ra != rb:
            flagged.add(a)
    repairs, m = {}, 0
    if repair and flagged:
        a_ids = st.by_id("a")
        bound_ok = {b for a, b in st.bindings.items() if a not in flagged}
        open_b = [i for i in st.b if i["id"] not in bound_ok and i["type"] != LINK]
        open_a = [a for a in flagged if a in a_ids] + [i["id"] for i in st.a if i["id"] not in st.bindings]
        for a in open_a:
            for cand in open_b:
                if cand["type"] != a_ids[a]["type"] or cand["id"] in repairs.values():
                    continue
                m += 1
                if recorded(st, a) == recorded(st, cand["id"]):
                    repairs[a] = cand["id"]; break
    return Finding(flagged, repairs, {"observations": n, "observations_to_repair": m})


def own_record_change(before: State, after: State, s: str) -> dict:
    """What side ``s`` can see by comparing its own record before and after: handles gone, handles new,
    and handles whose recorded facts changed. This is all it can announce without a change log."""
    b0 = {i["id"]: i for i in published(before.side(s))}
    b1 = {i["id"]: i for i in published(after.side(s))}
    return {"gone": sorted(set(b0) - set(b1)), "new": sorted(set(b1) - set(b0)),
            "changed": sorted(h for h in set(b0) & set(b1) if b0[h] != b1[h])}


# -------------------------------------------------------------------------------- event instances
def candidates(case: InstanceCase, kind: str, rng: random.Random, n: int) -> list[tuple]:
    """Up to ``n`` instances of an event kind, drawn from everything the network allows."""
    st = initial_state(case)
    ta = {i["id"]: i for i in st.a}
    members = {}                                       # bundle truth -> member truths (ports with no address)
    for i in st.a:
        if i["type"] == BUNDLE:
            members[i["_truth"]] = [ta[r["target"]]["_truth"] for r in i["rels"] if r["rel"] == "lower-layer-if"]
    addressed = {}                                     # device handle -> truths of addressed standalone ports
    for i in st.a:
        if i["type"] == PORT and IP["a"] in i["attrs"]:
            dev = next(r["target"] for r in i["rels"] if r["rel"] == "on-device")
            addressed.setdefault(dev, []).append(i["_truth"])
    out = []
    if kind == "rename":
        out = [(s, st.handle_of(s, i["_truth"])) for i in st.a for s in ("a", "b")]
    elif kind == "rekey_distinct":
        out = [(s, t1, t2) for ts in addressed.values() for x, t1 in enumerate(ts) for t2 in ts[x + 1:] for s in ("a", "b")]
    elif kind in ("rekey_lookalike", "cable_swap"):
        out = [(s, t1, t2) for ts in members.values() for x, t1 in enumerate(ts) for t2 in ts[x + 1:] for s in ("a", "b")]
        if kind == "cable_swap":
            out = [o[1:] for o in out if o[0] == "a"]
    elif kind in ("decommission", "readdress"):
        out = [(t,) for ts in addressed.values() for t in ts]
    elif kind == "move_address":
        out = [(t1, t2) for ts in addressed.values() for x, t1 in enumerate(ts) for t2 in ts[x + 1:]]
    else:
        raise ValueError(kind)
    rng.shuffle(out)
    return out[:n]


def apply(case: InstanceCase, kind: str, inst: tuple, stale: str | None = None) -> State:
    return apply_to(initial_state(case), kind, inst, stale)


def apply_to(st: State, kind: str, inst: tuple, stale: str | None = None) -> State:
    if kind == "rename":
        return ev_rename(st, *inst)
    if kind in ("rekey_distinct", "rekey_lookalike"):
        s, t1, t2 = inst
        return ev_rekey(st, s, st.handle_of(s, t1), st.handle_of(s, t2))
    if kind == "decommission":
        return ev_decommission(st, *inst)
    if kind == "readdress":
        return ev_readdress(st, inst[0], "10.9.%d.%d" % (len(inst[0]) % 250, sum(map(ord, inst[0])) % 250), stale)
    if kind == "move_address":
        return ev_move_address(st, *inst, stale=stale)
    if kind == "cable_swap":
        return ev_cable_swap(st, *inst, stale=stale)
    raise ValueError(kind)


def score(st: State, f: Finding) -> dict:
    void, right = void_bindings(st), true_rebinding(st)
    wrong = {a for a, b in f.repairs.items() if right.get(a) != b}
    return {"void": len(void), "found": len(void & f.flagged), "missed": len(void - f.flagged),
            "false_alarms": len(f.flagged - void), "repaired": len({a for a in f.repairs if a in void or a not in st.bindings} - wrong),
            "wrong_repairs": len(wrong), **f.cost}


def digest(x) -> str:
    return hashlib.sha1(json.dumps(x, sort_keys=True).encode()).hexdigest()[:12]
