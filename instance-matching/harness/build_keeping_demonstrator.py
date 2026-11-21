#!/usr/bin/env python3
"""Build the step-through page for KEEPING bindings from recorded runs. Needs no API key.

One episode of changes (the same in both runs) is stepped through twice: once with two agents that work from
their own records alone, and once with the required check, where an observation closes the binding. Everything
shown is read from the case and the two recorded runs; the table of bindings is replayed turn by turn and the
replay is checked against the table each run recorded at its end.

  python harness/build_keeping_demonstrator.py --size small --run 1 --out more-demonstrators/keeping-bindings.html
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CASES, RESULTS, HARNESS      # noqa: E402
from reconcile.instance import load_instance_case      # noqa: E402
from matching import keeping as D      # noqa: E402
from matching import keeping_agents as G      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--size", default="small")
ap.add_argument("--run", type=int, default=1)
ap.add_argument("--out", required=True)
args = ap.parse_args()
case = load_instance_case(CASES / ("instance_ipnet_%s" % args.size))
trial = args.run - 1
ep = G.build_episode(case, trial)
runs = {c: json.loads((RESULTS / args.size / d / ("run%d.json" % args.run)).read_text())
        for c, d in (("record", "keeping-record-only"), ("check", "keeping-record-required-check"))}
for r in runs.values():
    assert [e["components"] for e in r["events"]] == [e["components"] for e in ep["events"]], "run is of another episode"

sh = lambda h: h.split(".", 1)[1]                      # a handle without its side prefix


# ---- the states after each change, by applying the changes again one at a time
def inst_of(ev):
    k = ev["kind"]
    if k == "rename":
        return (ev["side"], ev["handles_before"][ev["side"]][0])
    if k in ("rekey_distinct", "rekey_lookalike"):
        return (ev["side"],) + tuple(ev["components"])
    return tuple(ev["components"])


states = [D.initial_state(case)]
for ev in ep["events"]:
    states.append(D.apply_to(states[-1], ev["kind"], inst_of(ev)))
assert D.published(states[-1].a) == D.published(ep["after"].a) and D.published(states[-1].b) == D.published(ep["after"].b)


def row_state(st, a, b):
    t = st.truth()
    if a not in t or b not in t:
        return "dead"
    return "valid" if t[a] == t[b] else "void"


# ---- replay a run: the table after every turn
def replay(run, check):
    rows = [[a, b] for a, b in ep["before"].bindings.items()]
    settled, prov, snaps = set(), set(), []
    now = {x: {i["id"] for i in ep["after"].side(x)} for x in ("a", "b")}
    for t in run["transcript"]:
        col = 0 if t["from"] == "A" else 1
        m = {c["old_handle"]: c["new_handle"] for c in t["my_handle_changes"]}
        for r in rows:
            if r[col] in m and (r[0], r[1]) not in settled:
                r[col] = m[r[col]]
        gone = set(t["my_removed"])
        rows[:] = [r for r in rows if (r[0], r[1]) in settled or (r[0] not in gone and r[1] not in gone)]
        if check:
            for o in t.get("observation_results", []):
                a, b = o["A_handle"], o["B_handle"]
                if o["result"].startswith("same") and (a, b) not in settled:
                    left_b = [r[1] for r in rows if r[0] == a and r[1] != b]
                    left_a = [r[0] for r in rows if r[1] == b and r[0] != a]
                    rows[:] = [r for r in rows if r[0] != a and r[1] != b]
                    rows.append([a, b]); settled.add((a, b)); prov.discard((a, b))
                    la, lb = [h for h in left_a if h in now["a"]], [h for h in left_b if h in now["b"]]
                    if len(la) == 1 and len(lb) == 1 and not any(r[0] == la[0] or r[1] == lb[0] for r in rows):
                        rows.append([la[0], lb[0]]); prov.add((la[0], lb[0]))
        snaps.append({"rows": [list(r) for r in rows], "settled": sorted(settled), "prov": sorted(prov)})
    assert sorted(map(tuple, rows)) == sorted(map(tuple, run["final_bindings"])), "replay differs from the recorded table"
    return snaps


snaps = {c: replay(runs[c], c == "check") for c in runs}

# ---- which bindings to show: every one that a change, a rewrite or an observation touches, at any time
H = set()
for ev in ep["events"]:
    H |= set(ev["handles_before"]["a"]) | set(ev["handles_before"]["b"])
    if ev.get("new_handle"):
        H.add(ev["new_handle"])
for c in runs:
    for t in runs[c]["transcript"]:
        H |= {x for ch in t["my_handle_changes"] for x in (ch["old_handle"], ch["new_handle"])} | set(t["my_removed"])
        H |= {x for o in t.get("observation_results", []) for x in (o["A_handle"], o["B_handle"])}
comp_event = {}
for n, ev in enumerate(ep["events"]):
    for t in ev["components"]:
        comp_event[t] = n
truth0 = states[0].truth()


def show(rows, st, extra=None):
    out = []
    for a, b in rows:
        if a in H or b in H:
            ta = st.truth().get(a) or truth0.get(a) or st.truth().get(b) or truth0.get(b)
            ev = comp_event.get(st.truth().get(a, truth0.get(a)), comp_event.get(st.truth().get(b, truth0.get(b)), 99))
            out.append({"a": a, "b": b, "state": row_state(st, a, b), "ev": ev})
    out.sort(key=lambda r: (r["ev"], r["a"]))
    rest = [r for r in rows if not (r[0] in H or r[1] in H)]
    assert all(row_state(st, a, b) == "valid" for a, b in rest)
    return out, len(rest)


WHAT = {
    "rename": ("A handle is renamed", "{S}'s system gives a port a new handle. The old handle no longer resolves.", "voids 1 binding"),
    "rekey_distinct": ("Two handles are re-keyed (ports with addresses)", "{S}'s system re-keys two of its handles: each now denotes the port the other denoted. Both handles still resolve.", "voids 2 bindings, silently"),
    "rekey_lookalike": ("Two handles are re-keyed (look-alike ports)", "{S}'s system re-keys two of its handles: each now denotes the port the other denoted. The two ports are members of one bundle and carry no address.", "voids 2 bindings, silently"),
    "decommission": ("A port is decommissioned", "The port leaves the network. Both records drop it.", "voids 1 binding"),
    "readdress": ("An address is changed", "A port gets a new address. Its handles still denote it.", "voids nothing"),
    "move_address": ("Two ports exchange addresses", "An identifier moves from one port to another. Every handle still denotes the port it did.", "voids nothing"),
    "cable_swap": ("Two cables are exchanged", "The cables on two member ports of one bundle are exchanged. Each port is still the port it was.", "voids nothing"),
}
SEEN = {
    "rename": {"own": "one handle gone, one new handle with the same facts", "other": "no change"},
    "rekey_distinct": {"own": "the two handles show each other's address and connections", "other": "no change"},
    "rekey_lookalike": {"own": "the two handles show each other's connections", "other": "no change"},
    "decommission": {"both": "one handle gone"},
    "readdress": {"both": "the address of one handle changed"},
    "move_address": {"both": "the two handles show each other's address"},
    "cable_swap": {"both": "the two handles show each other's connections"},
}
events = []
for n, ev in enumerate(ep["events"]):
    title, text, effect = WHAT[ev["kind"]]
    S = (ev["side"] or "").upper()
    seen = SEEN[ev["kind"]]
    events.append({"n": n, "kind": ev["kind"], "side": S, "title": title, "text": text.replace("{S}", S), "effect": effect,
                   "voids": not effect.endswith("nothing"),
                   "a": ev["handles_before"]["a"], "b": ev["handles_before"]["b"], "new": ev.get("new_handle"),
                   "sees": ({"A": seen["both"], "B": seen["both"]} if "both" in seen else
                            {S: seen["own"], ("B" if S == "A" else "A"): seen["other"]})})

# ---- steps
common = []
rows0 = [[a, b] for a, b in ep["before"].bindings.items()]
t, rest = show(rows0, states[0])
common.append({"title": "The bindings as they were made",
               "note": "Every router, port and bundle of the network is bound: one of A's handles and one of B's, for one component. All %d bindings are valid. "
                       "The table shows the %d that the coming changes will touch or that the agents will look at; the other %d stay valid throughout." % (len(rows0), len(t), rest),
               "table": t, "rest": rest, "focus": "pt", "ev": None, "turn": None})
for n, ev in enumerate(events):
    t, rest = show(rows0, states[n + 1])
    void = sum(1 for r in t if r["state"] != "valid")
    common.append({"title": "Change %d of %d: %s" % (n + 1, len(events), ev["title"].lower()),
                   "note": ev["text"] + (" This %s." % ev["effect"]) + " Void bindings so far: %d. The agents do not see this list of changes or the column “in truth”." % void,
                   "table": t, "rest": rest, "focus": "pe", "ev": n, "turn": None})
rk = next(e["n"] for e in events if e["kind"] == "rekey_lookalike")
cs = next(e["n"] for e in events if e["kind"] == "cable_swap")
side_rk = events[rk]["side"]
common.append({"title": "What each agent can see",
               "note": "No system gives its agent a change log here. Each agent can only compare its own record before and after. In %s's record, the re-keying of the two look-alike ports "
                       "and the exchange of two cables look the same: two handles show each other's connections. The first voided two bindings and the second voided none." % side_rk,
               "table": common[-1]["table"], "rest": common[-1]["rest"], "focus": "pe", "ev": [rk, cs], "turn": None, "sees": True})


def turn_view(t):
    acts = []
    for c in t["my_handle_changes"]:
        acts.append({"k": "rewrite", "text": "rewrites its handle: %s → %s" % (sh(c["old_handle"]), sh(c["new_handle"]))})
    for h in t["my_removed"]:
        acts.append({"k": "remove", "text": "reports gone: %s" % sh(h)})
    for o in t.get("observation_results", []):
        same = o["result"].startswith("same")
        acts.append({"k": "same" if same else "diff", "a": o["A_handle"], "b": o["B_handle"],
                     "text": "observes %s with %s: %s" % (sh(o["A_handle"]), sh(o["B_handle"]), "one component" if same else "two components")})
    for c in t.get("closed_by_observation", []):
        if "provisional" in c:
            acts.append({"k": "prov", "text": "left over, paired provisionally and still to observe: %s with %s" % (sh(c["provisional"][0]), sh(c["provisional"][1]))})
    if t.get("was_reminded_of"):
        acts.insert(0, {"k": "remind", "text": "reminded of bindings still to observe: " + ", ".join(sh(h) for h in t["was_reminded_of"])})
    for h in t["cannot_tell"]:
        acts.append({"k": "open", "text": "cannot tell: %s" % sh(h)})
    return {"from": t["from"], "say": t["say"], "acts": acts, "done": t["done"]}


conds = {}
for c, label in (("record", "Records only"), ("check", "With the required check")):
    run, steps = runs[c], []
    for k, t in enumerate(run["transcript"]):
        sn = snaps[c][k]
        tab, rest = show(sn["rows"], states[-1])
        for r in tab:
            r["settled"] = (r["a"], r["b"]) in set(map(tuple, sn["settled"]))
            r["prov"] = (r["a"], r["b"]) in set(map(tuple, sn["prov"]))
        tv = turn_view(t)
        nobs = sum(1 for a in tv["acts"] if a["k"] in ("same", "diff"))
        closed = sum(1 for cc in t.get("closed_by_observation", []) if "settled" in cc)
        bits = []
        if nobs:
            bits.append("%d observation%s" % (nobs, "" if nobs == 1 else "s"))
        if t["my_handle_changes"]:
            bits.append("%d handle%s rewritten" % (len(t["my_handle_changes"]), "" if len(t["my_handle_changes"]) == 1 else "s"))
        if t["my_removed"]:
            bits.append("%d reported gone" % len(t["my_removed"]))
        note = "Agent %s's turn: %s." % (t["from"], ", ".join(bits) if bits else "nothing more to do")
        if c == "check" and closed:
            note += " Each pair observed to be one component is set as the binding and settled, whichever side's handles moved."
        steps.append({"title": "Turn %d: agent %s" % (k + 1, t["from"]), "note": note, "table": tab, "rest": rest,
                      "focus": "pc", "ev": None, "turn": k})
    sc = run["score"]
    last = steps[-1]
    wrong = [r for r in last["table"] if r["state"] != "valid"]
    if wrong:
        out = ("Both agents declared done. %d of %d bindings are right and %d are wrong: %s. Neither agent knows it. %s's record showed the connections of its two handles exchanged, %s did not put those bindings to an observation, and %s's record showed nothing there."
               % (sc["bindings_right"], sc["bindings_expected"], sc["bindings_wrong"], "; ".join("%s with %s" % (sh(r["a"]), sh(r["b"])) for r in wrong), side_rk, side_rk, "A" if side_rk == "B" else "B"))
        hb = next(e for e in ep["events"] if e["kind"] == "rekey_lookalike")["handles_before"]
        assert not any(o["A_handle"] in hb["a"] or o["B_handle"] in hb["b"] for t in run["transcript"] for o in t.get("observation_results", [])), "the note says these were never observed"
    else:
        out = ("Both agents declared done. All %d bindings are right, and each one that a change touched was observed to be one component. %d observations in all."
               % (sc["bindings_expected"], run["effort"]["observations"]))
    steps.append({"title": "Outcome: " + ("%d wrong bindings" % sc["bindings_wrong"] if wrong else "every binding right"), "note": out,
                  "table": last["table"], "rest": last["rest"], "focus": "pt", "ev": None, "turn": len(run["transcript"]) - 1, "end": True})
    conds[c] = {"label": label, "steps": steps, "turns": [turn_view(t) for t in run["transcript"]],
                "right": sc["bindings_right"], "expected": sc["bindings_expected"], "wrong": sc["bindings_wrong"],
                "observations": run["effort"]["observations"], "tokens": run["effort"]["total_tokens"]}

data = {"meta": {"network": args.size, "run": args.run, "model": runs["check"].get("model", ""), "bindings": len(rows0)},
        "events": events, "common": common, "conds": conds}
tpl = (HARNESS / "keeping_demonstrator_template.html").read_text()
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
Path(args.out).write_text(tpl.replace("/*DATA*/", json.dumps(data)))
print("wrote", args.out, "| steps:", len(common), "+", {c: len(v["steps"]) for c, v in conds.items()},
      "| rows shown:", len(common[0]["table"]), "| replay checked against both recorded tables")
