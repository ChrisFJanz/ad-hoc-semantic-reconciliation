#!/usr/bin/env python3
"""Construct an instance case for one IP network seen through two independent models.

    python benchmark/build_instance_ipnet_case.py --size small
    python benchmark/build_instance_ipnet_case.py --size small --views names-only

Writes benchmark/cases/<case>/{individuals_a,individuals_b,instance_traps,
instance_reference,instance_gold}.json in the same format as instance_hard, so the
existing instance harness (reconcile.instance, stacks/agent_instance.py,
pipeline/instance_reconcile.py) runs on it unchanged. The gold is derived and validated
by the existing derive_instance_gold.py from each individual's hidden `_truth`.

The case (after an exchange on the NMOP list, November 2026): one network, two agents,
each holding its own model of that network with its own instance names. "If two routers
both report ifIndex 17, which router are we talking about?" There is no shared key.

  graph A  an interfaces view in the shape of RFC 8343 with RFC 8344 addresses and LLDP
           neighbours: devices, interfaces named by the device (so the same interface
           name recurs on every device), aggregate interfaces with their members.
  graph B  a topology view in the shape of RFC 8345 with the layer 2 and layer 3
           augmentations: nodes, termination points and links under identifiers that
           the topology system issues itself.
  names-only  graph B uses the same model as graph A, with its own device names.

The network is generated from a seed (ipnet_netgen.py): core, aggregation and access
routers, dual homing, parallel wires and link bundles. Types are given in an
already-reconciled vocabulary, as in instance_hard. Attribute names and units stay each
model's own. `--b-holds` sets which intrinsic facts graph B records statically
(ip, mac, ifname); what it does not record can still be had by interrogating a live side.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)
import ipnet_netgen as netgen                                    # noqa: E402
import derive_instance_gold as derive                            # noqa: E402

DEV, PORT, BUNDLE, LINK = "network-device", "physical-port", "link-bundle", "link"
SIZE = {"small": dict(n_core=3, n_aggpairs=1, n_access=3),
        "medium": dict(n_core=4, n_aggpairs=3, n_access=12),
        "large": {}}
SITES = ["yow", "yul", "yyz", "yvr", "yyc", "yeg", "ywg", "yhz", "yqb", "yxe"]


def structure(G):
    owner, peer, lag, members = {}, {}, {}, {}
    for u, v, d in G.edges(data=True):
        if d["rel"] == "has":
            r, i = (u, v) if G.nodes[u]["kind"] == "router" else (v, u)
            owner[i] = r
        elif d["rel"] == "wire":
            peer[u] = v; peer[v] = u
        elif d["rel"] == "member":
            l, m = (u, v) if G.nodes[u]["kind"] == "lag" else (v, u)
            lag[m] = l; members.setdefault(l, []).append(m)
    return owner, peer, lag, members


def ifname(G, i):
    p = int(i.split(":")[1].lstrip("pae"))
    return ("ae%d" % p) if G.nodes[i]["kind"] == "lag" else ("et-%d/0/%d" % (p // 8, p % 8))


def serial(r):
    return "SN-" + hashlib.sha1(r.encode()).hexdigest()[:8].upper()


def interfaces_view(G, seed, side, style, holds):
    """Individuals in the shape of an interfaces model. Returns (individuals, id_of)."""
    rnd = random.Random("ifv-%s-%s" % (seed, style))
    owner, peer, lag, members = structure(G)
    routers = [n for n, d in G.nodes(data=True) if d["kind"] == "router"]
    rnd.shuffle(routers)
    host = {}
    for k, r in enumerate(routers):
        host[r] = ("%s-%s-%02d" % (rnd.choice(SITES), {"core": "cr", "agg": "ar", "access": "er"}[G.nodes[r]["tier"]], k)
                   if style == "junos" else "NE%05d" % (10007 + 13 * k))
    idx = {}
    for r in routers:
        ifs = [i for i in G[r] if G[r][i]["rel"] == "has"]
        for i, n in zip(ifs, rnd.sample(range(500, 900), len(ifs))):
            idx[i] = n
    id_of = {r: "%s.%s" % (side, host[r]) for r in routers}
    for i in owner:
        id_of[i] = "%s.%s/%s" % (side, host[owner[i]], ifname(G, i))
    out = []
    for r in routers:
        attrs = {}
        if "ip" in holds:
            attrs["router-id"] = G.nodes[r]["loopback"]
        out.append({"id": id_of[r], "type": DEV, "name": host[r], "key": None, "attrs": attrs, "rels": [], "_truth": r})
        ifs = [i for i in G[r] if G[r][i]["rel"] == "has"]
        rnd.shuffle(ifs)
        for i in ifs:
            d = G.nodes[i]
            attrs = {"speed": d["speed"] * 10**9,
                     "if-type": "ieee8023adLag" if d["kind"] == "lag" else "ethernetCsmacd"}
            if d["kind"] == "iface" and "mac" in holds:
                attrs["phys-address"] = d["mac"]
            if d.get("ip") and "ip" in holds:
                attrs["ipv4-address"] = d["ip"]
            rels = [{"rel": "on-device", "target": id_of[r]}]
            if d["kind"] == "lag":
                rels += [{"rel": "lower-layer-if", "target": id_of[m]} for m in sorted(members[i], key=lambda m: id_of[m])]
            else:
                if i in lag:
                    rels.append({"rel": "higher-layer-if", "target": id_of[lag[i]]})
                if i in peer:
                    rels.append({"rel": "lldp-neighbour", "target": id_of[peer[i]]})
            out.append({"id": id_of[i], "type": BUNDLE if d["kind"] == "lag" else PORT, "name": ifname(G, i),
                        "key": None, "attrs": attrs, "rels": rels, "_truth": i})
    return out, id_of


def topology_view(G, seed, side, holds):
    """Individuals in the shape of a topology model, under identifiers it issues itself."""
    rnd = random.Random("topo-%s" % seed)
    owner, peer, lag, members = structure(G)
    uid = lambda p: "%s-%s" % (p, hashlib.sha1(("%s%s" % (seed, rnd.random())).encode()).hexdigest()[:8])
    routers = [n for n, d in G.nodes(data=True) if d["kind"] == "router"]
    rnd.shuffle(routers)
    nm = {}
    for r in routers:
        nm[r] = uid("node")
        for i in G[r]:
            if G[r][i]["rel"] == "has":
                nm[i] = uid("tp")
    id_of = {k: "%s.%s" % (side, v) for k, v in nm.items()}
    out = []
    for r in routers:
        attrs = {}
        if "ip" in holds:
            attrs["router-id"] = G.nodes[r]["loopback"]
        out.append({"id": id_of[r], "type": DEV, "name": nm[r], "key": None, "attrs": attrs, "rels": [], "_truth": r})
        ifs = [i for i in G[r] if G[r][i]["rel"] == "has"]
        rnd.shuffle(ifs)
        for i in ifs:
            d = G.nodes[i]
            attrs = {"lag": d["kind"] == "lag"}
            if "ifname" in holds:
                attrs["interface-name"] = ifname(G, i)
            if d["kind"] == "iface" and "mac" in holds:
                attrs["mac-address"] = d["mac"]
            if d.get("ip") and "ip" in holds:
                attrs["ip-address"] = d["ip"]
            rels = [{"rel": "in-node", "target": id_of[r]}]
            if d["kind"] == "lag":
                rels += [{"rel": "member-link-tp", "target": id_of[m]} for m in sorted(members[i], key=lambda m: id_of[m])]
            out.append({"id": id_of[i], "type": BUNDLE if d["kind"] == "lag" else PORT, "name": nm[i],
                        "key": None, "attrs": attrs, "rels": rels, "_truth": i})
    # links are individuals in this model and have no counterpart in an interfaces model
    wires = [(u, v) for u, v, d in G.edges(data=True) if d["rel"] == "wire"]
    rnd.shuffle(wires)
    seen = set()
    for u, v in wires:
        if rnd.random() < 0.5:
            u, v = v, u
        ends = [(u, v, "wire:%s" % "~".join(sorted((u, v))))]
        if u in lag and frozenset((lag[u], lag[v])) not in seen:
            seen.add(frozenset((lag[u], lag[v])))
            ends.append((lag[u], lag[v], "baglink:%s" % "~".join(sorted((lag[u], lag[v])))))
        for s, t, truth in ends:
            n = uid("link")
            out.append({"id": "%s.%s" % (side, n), "type": LINK, "name": n, "key": None,
                        "attrs": {"rate-kbps": G.nodes[s]["speed"] * 10**6},
                        "rels": [{"rel": "source-tp", "target": id_of[s]}, {"rel": "dest-tp", "target": id_of[t]}],
                        "_truth": truth})
    return out, id_of


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", default="small", choices=list(SIZE))
    ap.add_argument("--views", default="models", choices=["models", "names-only"],
                    help="models: interfaces model against topology model; names-only: one model, two namings")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--a-holds", default="ip", help="intrinsic facts graph A records statically")
    ap.add_argument("--b-holds", default="ip", help="intrinsic facts graph B records statically (ip, mac, ifname)")
    ap.add_argument("--case", default=None)
    a = ap.parse_args()
    ah = {x for x in a.a_holds.split(",") if x}
    bh = {x for x in a.b_holds.split(",") if x}
    name = a.case or "instance_ipnet_%s%s" % (a.size, "_namesonly" if a.views == "names-only" else "")
    cdir = CASES / name
    cdir.mkdir(parents=True, exist_ok=True)

    G = netgen.build(a.seed, **SIZE[a.size])
    A, _ = interfaces_view(G, a.seed, "a", "junos", ah)
    if a.views == "models":
        B, _ = topology_view(G, a.seed, "b", bh)
        dialect_b = "topology view (RFC 8345 with L2 and L3 augmentations), own identifiers"
    else:
        B, _ = interfaces_view(G, a.seed + 1000, "b", "vrp", bh | ({"mac"} if "mac" in bh else set()))
        dialect_b = "interfaces view (RFC 8343, RFC 8344, LLDP), own device names"

    # which correspondences does static evidence underdetermine? Same test as the gold derivation.
    id2truth = {i["id"]: i["_truth"] for i in A + B}
    a_of = {i["_truth"]: i for i in A}
    b_of = {i["_truth"]: i for i in B}
    shared = sorted(set(a_of) & set(b_of))
    sa = {t: derive.static_sig(a_of[t], id2truth) for t in shared}
    sb = {t: derive.static_sig(b_of[t], id2truth) for t in shared}
    by = {}
    for t in shared:
        by.setdefault((sa[t], sb[t]), []).append(t)
    experiment_only, false_cognates = [], []
    for group in by.values():
        if len(group) > 1:
            experiment_only += group
            for t, u in zip(group, group[1:] + group[:1]):
                false_cognates.append({"a": a_of[t]["id"], "b": b_of[u]["id"],
                                       "why": "static twins: same type, attributes and neighbours on both sides, "
                                              "but different real components; only an authoritative fact separates them."})
    if a.views == "names-only":
        byname = {}
        for i in B:
            byname.setdefault((i["type"], i["name"]), []).append(i)
        for i in A:
            for j in byname.get((i["type"], i["name"]), []):
                if j["_truth"] != i["_truth"] and i["type"] != DEV:
                    false_cognates.append({"a": i["id"], "b": j["id"],
                                           "why": "same interface name on a different device."})
                    break
    false_cognates = false_cognates[:60]

    # authoritative facts a live side can be interrogated for
    interrogate = {}
    for i in A + B:
        d = G.nodes.get(i["_truth"])
        if d is None:
            continue
        if d["kind"] == "router":
            interrogate[i["id"]] = {"serial": serial(i["_truth"])}
        elif d["kind"] == "iface":
            interrogate[i["id"]] = {"hardware-address": d["mac"]}
    # invariant signatures for the virtual operation "take this component out of service and read
    # the network back": by hidden truth, for every port and bundle. Stated without either side's names.
    owner, peer, lag, members = structure(G)
    R = netgen.router_graph(G)
    rid = lambda r: G.nodes[r]["loopback"]
    invariants = {}
    for t in shared:
        d = G.nodes.get(t)
        if d is None or d["kind"] == "router":
            continue
        ports = members.get(t, [t])
        far = sorted({rid(owner[peer[p]]) for p in ports if p in peer})
        u, v = owner[t], owner[peer[ports[0]]]
        a_, b_ = sorted((u, v))
        total = len(R[a_][b_]["wires"])
        invariants[t] = {
            "owner": rid(owner[t]),
            "endpoint-identity": sorted([rid(owner[t])] + far),
            "connectivity": "%d of %d wires between the two devices remain" % (total - len(ports), total),
            "capacity": d["speed"] * 10**9,
            "layer-relationships": ("bundle of %d member ports" % len(ports) if d["kind"] == "lag" else
                                    "member port of a bundle" if t in lag else "standalone port"),
        }
    gaps = len(set(a_of) ^ set(b_of))
    traps = {
        "case": name,
        "operational_case": "configuration (instance level): one network, two independently named models, no shared key",
        "seed": "generated network, seed %d, size %s, views %s, A holds %s, B holds %s"
                % (a.seed, a.size, a.views, sorted(ah), sorted(bh)),
        "false_cognates": false_cognates,
        "experiment_only": sorted(experiment_only),
        "oracle": {"interrogate": interrogate, "invariants": invariants},
        "residual_by_placement": {"both_cognitive": gaps, "one_inert": gaps + len(experiment_only),
                                  "both_inert": gaps + len(experiment_only)},
        "invariants": ["owner", "endpoint-identity", "connectivity", "capacity", "layer-relationships"],
        "verification_by_placement": {
            "both_cognitive": "interrogation on either side; virtual operation on a candidate pair",
            "one_inert": "interrogation on the live side only",
            "both_inert": "static evidence only; propose for external adjudication"},
    }
    (cdir / "individuals_a.json").write_text(json.dumps(
        {"system": "Agent A", "dialect": "interfaces view (RFC 8343, RFC 8344, LLDP)", "individuals": A}, indent=1) + "\n")
    (cdir / "individuals_b.json").write_text(json.dumps(
        {"system": "Agent B", "dialect": dialect_b, "individuals": B}, indent=1) + "\n")
    (cdir / "instance_traps.json").write_text(json.dumps(traps, indent=1) + "\n")
    (cdir / "instance_reference.json").write_text(json.dumps(
        {"note": "No published reference for this case: there is no shared key.", "instance": [], "invariant": []}, indent=1) + "\n")

    # derive and validate the gold with the existing script, pointed at this case
    derive.CDIR = cdir
    rc = derive.main()
    if rc == 0:
        g = json.loads((cdir / "instance_gold.json").read_text())
        g["case"] = name
        (cdir / "instance_gold.json").write_text(json.dumps(g, indent=2) + "\n")
        shared_names = {i["name"] for i in A} & {i["name"] for i in B}
        print("  case: %s" % name)
        print("  names shared between the two graphs: %d%s" % (len(shared_names), " (device-issued interface names)" if shared_names else ""))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
