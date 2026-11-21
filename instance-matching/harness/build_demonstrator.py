#!/usr/bin/env python3
"""Build the step-through demonstrator page from a case and one recorded run. Needs no API key.

Everything shown comes from the case files and the run's transcript: the identity anchors are recomputed by the
same join the run used, and every turn, question, proposal, ratification and check is read from the transcript.

  python harness/build_demonstrator.py --case instance_ipnet_small --run results/small/experiment/run1.json \
         --out demonstrator.html
  (add --withheld for a run made with addresses withheld)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CASES, RESULTS, HARNESS      # noqa: E402
from reconcile.instance import load_instance_case      # noqa: E402
from matching.anchor import anchor_join, lookalike_classes, withhold      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--case", required=True)
ap.add_argument("--run", required=True, help="a recorded transcript, results/<network>/<configuration>/runN.json")
ap.add_argument("--out", required=True)
ap.add_argument("--withheld", action="store_true", help="the run was made with every IP address withheld")
args = ap.parse_args()
case_dir, tpath, out = CASES / args.case, Path(args.run), Path(args.out)
cpath = tpath.with_name(tpath.stem + "_carry.json")
carry = json.loads(cpath.read_text()) if cpath.exists() else None
case = load_instance_case(case_dir)
if args.withheld:
    case = withhold(case)
A, B = case.a, case.b
run = json.loads(tpath.read_text())
T, row = run["transcript"], run.get("row", {})
STACK = next((x.get("stack", "") for x in T if x["step"] == "prompt"), "")
LIVE = "+live" in STACK
CHECK = "live observation" if LIVE else "experiment on the digital twin"
rules = json.loads((RESULTS / "model-step" / "term_rules.json").read_text())["rules"]
binding = json.loads((CASES / "config_ipnet" / "data_binding.json").read_text())
ANCH = anchor_join(case, rules, binding)[0] if "+anchors" in STACK else {}
LOOK = {"A": lookalike_classes(case.a, set(ANCH)), "B": lookalike_classes(case.b, set(ANCH.values()))}
a_ids = {i["id"] for i in A}
byid = {i["id"]: i for i in A + B}


def owner(i, inds):
    dev = {x["id"] for x in inds if x["type"] == "network-device"}
    for r in i["rels"]:
        if r["target"] in dev:
            return r["target"]
    return None


def pack(inds):
    res = []
    for i in inds:
        at = i["attrs"]
        bits = [f"{k}={v}" for k, v in at.items()]
        res.append({"id": i["id"], "type": i["type"], "name": i["name"], "truth": i["_truth"],
                    "dev": owner(i, inds), "attrs": "; ".join(bits),
                    "member": any(r["rel"] in ("higher-layer-if",) for r in i["rels"])})
    return res


PA, PB = pack(A), pack(B)
# B marks membership on the bundle, not the port: derive it for display
memb = {r["target"] for i in B for r in i["rels"] if r["rel"] == "member-link-tp"}
for p in PB:
    p["member"] = p["id"] in memb

# the network itself (ground truth, for the centre picture only)
devs = [{"t": i["_truth"], "rid": i["attrs"].get("router-id", "")} for i in A if i["type"] == "network-device"]
wires = []
for i in B:
    if i["_truth"].startswith("wire:"):
        x, y = i["_truth"][5:].split("~")
        wires.append({"a": x, "b": y})
bund = {}
for i in A:
    if i["type"] == "link-bundle":
        for r in i["rels"]:
            if r["rel"] == "lower-layer-if":
                bund[byid[r["target"]]["_truth"]] = i["_truth"]
for w in wires:
    w["ba"], w["bb"] = bund.get(w["a"], ""), bund.get(w["b"], "")

# ---- steps from the transcript -------------------------------------------------------
steps = []
bound, pending, tested = set(), set(), {}


def pair(side, my, their):
    a, b = (my, their) if side == "A" else (their, my)
    return (a, b) if a in a_ids and b in byid and b not in a_ids else None


def snap(**kw):
    s = {"bound": sorted(map(list, bound)), "pending": sorted(map(list, pending)),
         "refuted": [list(k) for k, v in tested.items() if v is False]}
    s.update(kw)
    steps.append(s)


def short(x, n=210):
    x = " ".join(str(x).split())
    return x if len(x) <= n else x[:n - 1] + "…"


nA = len(A); nB = len(B)
snap(kind="intro", focus="net", title="One network, two agents",
     note=f"One network of {len(devs)} routers and {len(wires)} wires. Agent A holds a graph of it with "
          f"{nA} individuals; Agent B holds its own graph with {nB}. Each graph was built independently, "
          "so the two agents use different names for the same things.", talk=[])
d0 = devs[0]["t"]
snap(kind="names", focus="net", title="Same router, two descriptions", hi=d0,
     note="Take one router. Agent A knows it by a device name and device-issued interface names. "
          "Agent B knows it as a node with opaque termination-point ids. Nothing in the names says they "
          "are the same router. The task: match every individual on one side to the individual on the "
          "other side that is the same component.", talk=[])
if ANCH:
    for a_, b_ in ANCH.items():
        bound.add((a_, b_))
    shown = list(ANCH.items())[:5]
    snap(kind="anchor", focus="net", title=f"Identity anchor: {len(ANCH)} of {nA} settled by identifier",
         note="Before any conversation, the individuals are joined on the identifiers that the model step found to "
              "correspond with their values carried unchanged" + (": here the router identifier, since every address "
              "is withheld. " if args.withheld else ": the router identifier and the IP address. ")
              + "A value that occurs once on each side identifies one individual. This is a join on values: it takes "
              f"no conversation and no judgment, and it settles {len(ANCH)} of the {nA} individuals.",
         talk=[{"who": "P", "kind": "joined", "text": f"{x} ↔ {y}"} for x, y in shown],
         more=max(0, len(ANCH) - 5), new=[[x, y] for x, y in ANCH.items()])
    n_la = sum(len(g) for g in LOOK["A"])
    if n_la:
        g0 = LOOK["A"][0]
        snap(kind="lookalikes", focus="a", title=f"Look-alikes: {n_la} individuals that no recorded fact tells apart",
             note="Each agent works out, from its own graph and before any conversation, which of its individuals no "
                  f"recorded fact tells apart. On agent A's side there are {n_la}, in {len(LOOK['A'])} groups: the member "
                  "ports of the bundles, two parallel wires between the same two routers at the same speed. Topology can "
                  "narrow such a port to a few candidates and cannot choose between them. A match that involves a "
                  f"look-alike counts only when it has been checked against the network, by {CHECK}.",
             talk=[{"who": "A", "kind": "look-alike group", "text": " · ".join(g)} for g in LOOK["A"][:4]],
             more=max(0, len(LOOK["A"]) - 4))

turn_no = 0
i = 0
exps = []
while i < len(T):
    s = T[i]
    if s["step"] != "turn":
        i += 1
        continue
    turn_no += 1
    side, other, t = s["from"], ("B" if s["from"] == "A" else "A"), s["turn"]
    stage = s.get("stage")
    # experiments and interrogations logged just before this turn entry belong to it
    j = i - 1
    mine = []
    while j >= 0 and T[j]["step"] in ("virtual_provision", "interrogate"):
        mine.insert(0, T[j]); j -= 1
    who = f"Agent {side}"
    if t["answers"] or t["questions"]:
        talk = []
        for a in t["answers"][:3]:
            talk.append({"who": side, "kind": "answers", "text": short(f"{a['my_id']}: {a['attributes']}. {a['topology']}")})
        for q in t["questions"][:3]:
            talk.append({"who": side, "kind": "asks", "text": short(f"about {q['their_id']}: {q['ask']}")})
        bits = []
        if t["answers"]:
            bits.append(f"answers {len(t['answers'])} question{'s' if len(t['answers']) != 1 else ''} from its own graph")
        if t["questions"]:
            bits.append(f"asks {len(t['questions'])} about Agent {other}'s individuals")
        snap(kind="talk", focus="talk", turn=turn_no, title=f"Turn {turn_no}: {who} " + " and ".join(
            (["answers"] if t["answers"] else []) + (["asks"] if t["questions"] else [])),
             note=f"{who} " + " and ".join(bits) + ". Each agent sees only its own graph and the other's "
             "catalogue of ids; evidence crosses only in these answers.", talk=talk,
             more=max(0, len(t["answers"]) - 3) + max(0, len(t["questions"]) - 3))
    rats = [(pair(side, x["my_id"], x["their_id"]), x["accept"]) for x in t["ratifications"]]
    rats = [(p, ok) for p, ok in rats if p]
    if rats:
        acc = [p for p, ok in rats if ok]
        for p in acc:
            if p in pending or tested.get(p) is not False:
                pending.discard(p)
                if tested.get(p) is not False:
                    bound.add(p)
        talk = [{"who": side, "kind": "ratifies", "text": short(f"{x['their_id']} ↔ {x['my_id']}: {x['reason']}")}
                for x in t["ratifications"][:4]]
        nc = len(t.get("no_counterpart", []))
        snap(kind="ratify", focus="b" if side == "B" else "a", turn=turn_no,
             title=f"Turn {turn_no}: {who} ratifies {len(acc)} matches",
             note=f"{who} checks each proposal against its own graph and accepts {len(acc)}"
                  + (f", rejecting {len(rats) - len(acc)}" if len(rats) != len(acc) else "")
                  + ". These matches are now settled."
                  + (f" It also declares {nc} of its individuals to have no counterpart: the link objects, "
                     "which exist only in its model." if nc else ""),
             talk=talk, more=max(0, len(t["ratifications"]) - 4), new=[list(p) for p in acc])
    props = [p for p in (pair(side, x["my_id"], x["their_id"]) for x in t["proposals"]) if p]
    if props:
        for p in props:
            if p not in bound:
                pending.add(p)
        talk = [{"who": side, "kind": "proposes", "text": short(f"{x['my_id']} ↔ {x['their_id']}: {x['rationale']}")}
                for x in t["proposals"][:4]]
        snap(kind="propose", focus="a" if side == "A" else "b", turn=turn_no,
             title=f"Turn {turn_no}: {who} proposes {len(props)} matches",
             note=f"{who} proposes {len(props)} matches on the evidence gathered, each with a rationale. "
                  f"They are shown as pending until Agent {other}, the authority on its own side, ratifies them.",
             talk=talk, more=max(0, len(t["proposals"]) - 4), new=[list(p) for p in props])
    ex = [m for m in mine if m["step"] == "virtual_provision" and m.get("by") != "protocol"]
    px = [m for m in mine if m["step"] == "virtual_provision" and m.get("by") == "protocol"]
    ig = [m for m in mine if m["step"] == "interrogate"]
    if ig:
        talk = [{"who": side, "kind": "asks its device", "text": short(f"{m['args']['individual_id']} → {json.dumps(m['result']['answer'])}")}
                for m in ig[:4]]
        snap(kind="interrogate", focus="talk", turn=turn_no, title=f"Turn {turn_no}: {who} asks {len(ig)} of its own devices for an identifier",
             note=f"{who} asks {len(ig)} of its own devices for an identifier that only the device can report, such as a hardware address. The answers go to both agents.",
             talk=talk, more=max(0, len(ig) - 4))
    single = len(ex) <= 4
    if single:
        groups = [[m] for m in ex]
    else:   # show one refuted experiment on its own, then the rest together
        okx = [m for m in ex if m["result"]["ok"]]
        lead = next((m for m in okx if not m["result"]["answer"].get("confirmed")), None)
        groups = ([[lead]] if lead else []) + [[m for m in ex if m is not lead]]
    groups = [(g, False) for g in groups] + ([(px, True)] if px else [])
    for g, proto in groups:
        res = []
        for m in g:
            a, b = m["args"]["a_id"], m["args"]["b_id"]
            ok = m["result"]["answer"].get("confirmed")
            if not m["result"]["ok"]:
                continue
            tested[(a, b)] = ok
            pending.discard((a, b))
            if ok:
                bound.add((a, b))
            else:
                bound.discard((a, b))
            res.append({"a": a, "b": b, "ok": bool(ok), "ta": byid[a]["_truth"], "tb": byid[b]["_truth"]})
        if not res:
            continue
        nc = sum(1 for r in res if r["ok"]); nr = len(res) - nc
        if proto:
            title = f"Turn {turn_no}: the protocol checks the agreed look-alike matches" + (f": {nr} refuted" if nr else "")
            note = (f"Agreement does not settle a match that involves a look-alike. The protocol puts each of the {len(res)} "
                    f"agreed look-alike matches to the check, by {CHECK}: {nc} confirmed"
                    + (f", {nr} refuted. The two agents had agreed on those, and the check showed two different components. "
                       "They are withdrawn, and the agents must propose again."
                       if nr else ". Every one is the same component on both sides."))
            res.sort(key=lambda r: r["ok"])
        elif len(res) == 1:
            r = res[0]
            title = f"Turn {turn_no}: {who} checks one match by {CHECK}"
            note = (f"{who} cannot tell from its records which of {other}'s look-alike ports matches its own. It checks one "
                    "candidate: " + ("the data recorded for the component is read through A's handle and through B's handle, and compared. Nothing on the network is touched. " if LIVE else "on the digital twin, the component is taken out of service through A's handle and through B's handle. ")
                    + (("The same data comes back through both handles" if LIVE else "The same component responded on both sides")
                       + ": the match is confirmed." if r["ok"] else
                       ("Different data comes back through the two handles" if LIVE else "A different component responded on each side")
                       + ": these two are not the same component. The match is refuted, so it must be the other look-alike."))
        else:
            title = f"Turn {turn_no}: {who} makes {len(res)} checks by {CHECK}"
            note = (f"{who} puts {len(res)} matches to the check: " + ("the data recorded for the component is read through A's handle and through B's handle, and compared. Nothing on the network is touched. " if LIVE else "on the digital twin, the component is taken out of service through A's handle and through B's handle. ")
                    + f"{nc} confirmed"
                    + (f", {nr} refuted" if nr else "") + ". A confirmed match is settled without further ratification.")
        talk = [{"who": "P" if proto else side, "kind": "confirms" if proto else "tests", "text": f"{r['a']} ↔ {r['b']}: " +
                 (("the same recorded data through both handles" if LIVE else "the same component responded on both sides") if r["ok"]
                  else ("different recorded data through the two handles" if LIVE else "a different component responded on each side"))}
                for r in res[:5]]
        snap(kind="experiment", focus="net", turn=turn_no, title=title, note=note, talk=talk,
             more=max(0, len(res) - 5), exps=res)
    i += 1

ok_all = all(byid[a]["_truth"] == byid[b]["_truth"] for a, b in bound)
snap(kind="result", focus="net", title="Instance matching complete",
     note=f"{len(bound)} of {len(A)} individuals in A's graph are matched to their counterparts in B's graph"
          + (", with no wrong match" if ok_all else "")
          + f". Settled by identifier: {len(ANCH)}. Checks against the network: {sum(1 for v in tested.values())}. "
          "Click any component on either side: its counterpart and the component in the network light up.", talk=[])
if carry:
    rows = [r for r in carry["rows"] if r["carried"]]
    memb_a = {p["id"] for p in PA if p["member"]}
    pick = next((r for r in rows if not r["same_component"]), None) or \
        next((r for r in rows if r["instruction"]["on"] in memb_a), rows[0])
    a, b = pick["instruction"]["on"], pick["carried"]["on"]
    snap(kind="generate", focus="talk", title="Generate: a translator for each side",
         note=f"The {len(bound)} matched individuals are recorded as a table. Read from A to B it is agent A's "
              "translator; read from B to A it is agent B's. From here on nothing is inferred: the table is applied as it stands.",
         talk=[{"who": "A", "kind": "table row", "text": f"{x} → {y}"} for x, y in sorted(bound)[:5]],
         more=max(0, len(bound) - 5))
    snap(kind="carry", focus="net", title="Carry: an instruction crosses",
         note="Agent A issues an instruction naming a component by its own id. The translator rewrites it in "
              "agent B's id, and it is executed on the network through B's handle. "
              + ("The component that goes out of service is the one A named." if pick["same_component"] else
                 "A different component goes out of service: the match was wrong, and the round trip did not show it."),
         talk=[{"who": "A", "kind": "instructs", "text": f"{pick['instruction']['operation']}: {a}"},
               {"who": "B", "kind": "receives", "text": f"{pick['carried']['operation']}: {b}"}],
         carry={"a": a, "b": b, "ok": pick["same_component"], "ta": byid[a]["_truth"], "tb": byid[b]["_truth"]})
    snap(kind="carried", focus="net", title="Every instruction lands on the component it names",
         note=f"{carry['instructions']} instructions carried, one for every port and bundle agent A can name: "
              f"{carry['same_component']} landed on the same component"
              + (f", {carry['wrong_component']} on a different one" if carry["wrong_component"] else "")
              + f". The round trip returned the original for {carry['round_trip_ok']}"
              + (", including the wrong ones." if carry["wrong_component"] else "."),
         talk=[], allcarry=[{"ta": byid[r["instruction"]["on"]]["_truth"], "ok": r["same_component"]} for r in rows])

PHASE = {"intro": -1, "names": -1, "generate": 3, "carry": 4, "carried": 4}
for s_ in steps:
    s_["phase"] = PHASE.get(s_["kind"], 4)
    s_["sub"] = "" if s_["kind"] in PHASE else "instance matching"
data = {"A": PA, "B": PB, "devs": devs, "wires": wires, "steps": steps,
        "meta": {"live": LIVE, "model": run.get("model", ""), "case": case_dir.name, "tokens": row.get("total_tokens", ""),
                 "turns": row.get("turns", "")}}
html = (HARNESS / "demonstrator_template.html").read_text().replace("/*DATA*/", json.dumps(data))
out.write_text(html)
print(out, len(html), "bytes;", len(steps), "steps;", len(bound), "bound")
