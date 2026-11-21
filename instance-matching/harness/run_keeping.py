"""Keeping bindings, with no model call: for each kind of change, what each mechanism finds.

    python harness/run_keeping.py                      # small and medium networks, the table
    python harness/run_keeping.py --size small --n 40 --json results/keeping-without-agents/coverage_small.json

Every instance starts from the network as matched (every individual bound correctly), applies ONE change,
and asks each mechanism which bindings it reports. Scoring is against the truth the case carries.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

import _paths  # noqa: F401
from _paths import CASES, RESULTS
from reconcile.instance import load_instance_case

from matching import keeping as D

# kind, stale side (a record not refreshed yet), does it void bindings, what it is
EVENTS = [
    ("rename", None, True, "a handle is renamed"),
    ("rekey_distinct", None, True, "two handles re-keyed, ports with addresses"),
    ("rekey_lookalike", None, True, "two handles re-keyed, look-alike ports"),
    ("decommission", None, True, "a port is decommissioned"),
    ("readdress", None, False, "an address is changed"),
    ("readdress", "b", False, "an address is changed, B's record not refreshed"),
    ("move_address", None, False, "two ports exchange addresses"),
    ("move_address", "b", False, "two ports exchange addresses, B's record not refreshed"),
    ("cable_swap", None, False, "two cables exchanged on look-alike ports"),
    ("cable_swap", "b", False, "two cables exchanged, B's record not refreshed"),
]
MECHS = ["on_use", "identifiers", "relations", "observation", "relations+observation"]


def run(size: str, n: int, seed: int) -> dict:
    case = load_instance_case(CASES / ("instance_ipnet_%s" % size))
    rules = json.loads((RESULTS / "model-step" / "term_rules.json").read_text())["rules"]
    binding = json.loads((CASES / "config_ipnet" / "data_binding.json").read_text())
    rows = []
    for kind, stale, voids, what in EVENTS:
        insts = D.candidates(case, kind, random.Random(seed), n)
        agg = {m: defaultdict(int) for m in MECHS}
        own_visible = 0
        for inst in insts:
            st = D.apply(case, kind, inst, stale)
            f = {"on_use": D.on_use(st), "identifiers": D.identifiers(st, case, rules, binding),
                 "relations": D.relations(st)}
            f["observation"] = D.observation(st)
            narrowed = D.observation(st, only=f["relations"].flagged | f["on_use"].flagged)
            narrowed.cost["relations_compared"] = f["relations"].cost["relations_compared"]
            f["relations+observation"] = narrowed
            for m in MECHS:
                for k, v in D.score(st, f[m]).items():
                    agg[m][k] += v
            side = inst[0] if kind in ("rename", "rekey_distinct", "rekey_lookalike") else "a"
            ch = D.own_record_change(D.initial_state(case), st, side)
            own_visible += bool(ch["gone"] or ch["new"] or ch["changed"])
        rows.append({"kind": kind, "stale": stale, "voids": voids, "what": what, "instances": len(insts),
                     "own_record_changed": own_visible, "by_mechanism": {m: dict(agg[m]) for m in MECHS}})
    return {"network": size, "individuals": len(case.gold["correspondences"]), "seed": seed, "rows": rows}


def table(res: dict) -> str:
    out = ["", "%s network, %d bindings. Each cell: void bindings found / void bindings, then false alarms "
           "(valid bindings reported) and wrong repairs proposed, summed over the instances." % (res["network"], res["individuals"]), "",
           "| Change | Instances | " + " | ".join(MECHS) + " |", "|---|---|" + "---|" * len(MECHS)]
    for r in res["rows"]:
        cells = []
        for m in MECHS:
            a = r["by_mechanism"][m]
            c = "%d/%d" % (a.get("found", 0), a.get("void", 0))
            extra = []
            if a.get("false_alarms"):
                extra.append("%d false" % a["false_alarms"])
            if a.get("wrong_repairs"):
                extra.append("%d wrong repairs" % a["wrong_repairs"])
            if a.get("repaired"):
                extra.append("%d repaired" % a["repaired"])
            cells.append(c + (" (" + ", ".join(extra) + ")" if extra else ""))
        out.append("| %s | %d | %s |" % (r["what"], r["instances"], " | ".join(cells)))
    obs = res["rows"][0]["by_mechanism"]
    per = {m: {k: round(v / res["rows"][0]["instances"], 1) for k, v in obs[m].items()
               if k in ("values_compared", "relations_compared", "observations", "observations_to_repair")} for m in MECHS}
    out += ["", "Work per sweep (first row, per instance): " + json.dumps(per)]
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", choices=["small", "medium", "large"], action="append")
    ap.add_argument("--n", type=int, default=40, help="instances per kind of change")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--json")
    args = ap.parse_args()
    allres = []
    for size in args.size or ["small", "medium"]:
        res = run(size, args.n, args.seed)
        allres.append(res)
        print(table(res))
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(allres, indent=1))
