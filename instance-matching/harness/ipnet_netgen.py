"""Ground-truth network generator for the instance-binding study.

A three-tier IP network (core / aggregation / access) with the features that
make instance binding hard: dual homing, parallel links, and link bundles.
Everything is derived from one seed.

The ground truth is a typed graph:
  router  --has-->  iface (physical)  --wire--  iface (physical)  <--has-- router
  router  --has-->  lag (logical)     --member-->  iface (physical)
An L3 adjacency lives either on a physical interface pair or on a lag pair.
"""
import random
import networkx as nx


def build(seed=1, n_core=8, n_aggpairs=12, n_access=64):
    rnd = random.Random(seed)
    G = nx.Graph()
    port = {}          # next free port index per router
    subnet = [0]

    def router(name, tier):
        G.add_node(name, kind="router", tier=tier,
                   loopback="10.255.%d.%d" % (len(port) // 250, len(port) % 250 + 1))
        port[name] = 0
        return name

    def phys(r, speed):
        i = port[r]; port[r] += 1
        n = "%s:p%d" % (r, i)
        G.add_node(n, kind="iface", speed=speed,
                   mac="02:%02x:%02x:%02x:%02x:%02x" % tuple(rnd.randrange(256) for _ in range(5)),
                   traffic=0.0)
        G.add_edge(r, n, rel="has")
        return n

    def l3pair(a, b):
        s = subnet[0]; subnet[0] += 1
        base = "10.%d.%d.%d" % (s // 32768, (s // 128) % 256, (s % 128) * 2)
        hi = base.rsplit(".", 1)[0] + "." + str(int(base.rsplit(".", 1)[1]) + 1)
        G.nodes[a]["ip"] = base; G.nodes[b]["ip"] = hi
        G.nodes[a]["l3"] = True; G.nodes[b]["l3"] = True

    def wire(r1, r2, speed):
        a, b = phys(r1, speed), phys(r2, speed)
        G.add_edge(a, b, rel="wire")
        return a, b

    def connect(r1, r2, speed, n=1, bundle=False):
        """n parallel wires; as one lag (bundle) or as n separate L3 links."""
        ends = [wire(r1, r2, speed) for _ in range(n)]
        if bundle:
            lags = []
            for r, side in ((r1, 0), (r2, 1)):
                i = port[r]; port[r] += 1
                lg = "%s:ae%d" % (r, i)
                G.add_node(lg, kind="lag", speed=speed * n)
                G.add_edge(r, lg, rel="has")
                for e in ends:
                    G.add_edge(lg, e[side], rel="member")
                lags.append(lg)
            l3pair(*lags)
        else:
            for a, b in ends:
                l3pair(a, b)

    cores = [router("C%d" % i, "core") for i in range(n_core)]
    pairs = set()
    for i in range(n_core):                      # ring
        pairs.add(tuple(sorted((i, (i + 1) % n_core))))
    while len(pairs) < min(n_core + n_core // 2, n_core * (n_core - 1) // 2):     # chords
        i, j = rnd.sample(range(n_core), 2)
        pairs.add(tuple(sorted((i, j))))
    for i, j in sorted(pairs):
        n = rnd.choice([1, 2, 2, 4])
        connect(cores[i], cores[j], 100, n=n, bundle=(n > 1 and rnd.random() < 0.5))

    aggs = []
    for p in range(n_aggpairs):
        a1, a2 = router("G%da" % p, "agg"), router("G%db" % p, "agg")
        aggs.append((a1, a2))
        c1, c2 = rnd.sample(cores, 2) if len(cores) > 1 else (cores[0], cores[0])
        for a in (a1, a2):
            for c in (c1, c2):
                n = rnd.choice([1, 1, 2])
                connect(a, c, 100, n=n, bundle=(n > 1))
        connect(a1, a2, 100)

    for k in range(n_access):
        x = router("X%d" % k, "access")
        a1, a2 = aggs[rnd.randrange(n_aggpairs)]
        for a in (a1, a2):
            n = rnd.choice([1, 1, 1, 2])
            connect(x, a, 10, n=n, bundle=(n > 1 and rnd.random() < 0.5))

    # live traffic: a random demand between access routers, routed on hop count
    R = router_graph(G)
    acc = [n for n, d in G.nodes(data=True) if d["kind"] == "router" and d["tier"] == "access"]
    for _ in range(4 * len(acc) if len(acc) > 1 else 0):
        s, t = rnd.sample(acc, 2)
        vol = rnd.uniform(0.05, 1.0)
        path = nx.shortest_path(R, s, t)
        for u, v in zip(path, path[1:]):
            wires = R[u][v]["wires"]
            a, b = wires[rnd.randrange(len(wires))]   # per-flow hashing onto one wire
            G.nodes[a]["traffic"] += vol; G.nodes[b]["traffic"] += vol
    return G


def router_graph(G):
    """Router-level graph; each edge lists the physical wires that realise it."""
    R = nx.Graph()
    for n, d in G.nodes(data=True):
        if d["kind"] == "router":
            R.add_node(n)
    owner = {}
    for u, v, d in G.edges(data=True):
        if d["rel"] == "has":
            r, i = (u, v) if G.nodes[u]["kind"] == "router" else (v, u)
            owner[i] = r
    for u, v, d in G.edges(data=True):
        if d["rel"] == "wire":
            r1, r2 = owner[u], owner[v]
            pair = (u, v) if r1 <= r2 else (v, u)
            a, b = sorted((r1, r2))
            if R.has_edge(a, b):
                R[a][b]["wires"].append(pair)
            else:
                R.add_edge(a, b, wires=[pair])
    return R


if __name__ == "__main__":
    G = build(1)
    from collections import Counter
    print(Counter(d["kind"] for _, d in G.nodes(data=True)))
    print("wires", sum(1 for *_, d in G.edges(data=True) if d["rel"] == "wire"))
