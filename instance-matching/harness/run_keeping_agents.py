"""Keeping bindings, with agents (needs an OpenAI key).

    python harness/run_keeping_agents.py --size small                 # 3 conditions x 3 runs on the small network
    python harness/run_keeping_agents.py --size medium
    python harness/run_keeping_agents.py --size small --condition log --trials 1
    python harness/run_keeping_agents.py --tables                     # no key: the table from the recorded runs

Each run starts from the network as matched, applies one change of each kind, and lets the agents bring the
bindings up to date. Results go to results/<network>/keeping-<condition>/runN.json and summary.csv. A run that
is already recorded is skipped, so the command can be repeated.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import _paths  # noqa: F401
from _paths import CASES, RESULTS
from reconcile.instance import load_instance_case

from matching import keeping_agents as G

CONDITIONS = ["log", "record", "record_check", "one_inert"]
NAMES = {"log": "keeping-change-log", "record": "keeping-record-only", "record_check": "keeping-record-required-check",
         "one_inert": "keeping-one-inert"}
COLS = ["network", "condition", "run", "bindings_expected", "bindings_right", "bindings_left_open", "bindings_wrong",
        "rows_with_a_dead_handle", "observations", "turns", "total_tokens", "latency_s"] + G.KINDS


def row_of(size, cond, trial, r):
    sc, ef = r["score"], r["effort"]
    row = {"network": size, "condition": cond, "run": trial + 1, **{k: sc[k] for k in COLS[3:8]},
           "observations": ef["observations"], "turns": ef["turns"], "total_tokens": ef["total_tokens"],
           "latency_s": round(ef["latency_s"], 1)}
    row.update({e["kind"]: e["outcome"] for e in sc["per_event"]})
    return row


def tables() -> str:
    out = ["| Network | Condition | Runs | Changes handled right, of 7 | Bindings right | Left open | Wrong | Observations | Tokens per run |",
           "|---|---|---|---|---|---|---|---|---|"]
    detail = []
    for size in ("small", "medium"):
        for cond in CONDITIONS:
            d = RESULTS / size / NAMES[cond]
            runs = [json.loads(p.read_text()) for p in sorted(d.glob("run*.json"))]
            if not runs:
                continue
            sc = [r["score"] for r in runs]
            right = [sum(e["outcome"] == "right" for e in s["per_event"]) for s in sc]
            rng = lambda xs: ("%s" % xs[0]) if len(set(xs)) == 1 else "%s to %s" % (min(xs), max(xs))   # noqa: E731
            out.append("| %s | %s | %d | %s | %s of %d | %s | %s | %s | %s |" % (
                size, cond.replace("_", " "), len(runs), rng(right), rng([s["bindings_right"] for s in sc]),
                sc[0]["bindings_expected"], rng([s["bindings_left_open"] for s in sc]), rng([s["bindings_wrong"] for s in sc]),
                rng([r["effort"]["observations"] for r in runs]), rng([round(r["effort"]["total_tokens"] / 1000) * 1000 for r in runs])))
            for r in runs:
                bad = ["%s%s: %s" % (e["kind"], (" on " + e["side"].upper()) if e["side"] else "", e["outcome"])
                       for e in r["score"]["per_event"] if e["outcome"] != "right"]
                if bad:
                    detail.append("%s, %s, run %d: %s" % (size, cond.replace("_", " "), r["trial"] + 1, "; ".join(bad)))
    if len(out) == 2:
        return "No runs recorded yet."
    return "\n".join(out + [""] + (["Changes not handled right:"] + detail if detail else ["Every change was handled right in every run."]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", choices=["small", "medium"], default="small")
    ap.add_argument("--condition", choices=CONDITIONS, action="append")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--model", default="gpt-5.6-sol")
    ap.add_argument("--tables", action="store_true")
    args = ap.parse_args()
    if args.tables:
        print(tables())
        return 0
    from run import load_dotenv
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set; see ../study/notes/SETUP_OPENAI.md", file=sys.stderr)
        return 2
    case = load_instance_case(CASES / ("instance_ipnet_%s" % args.size))
    rules = json.loads((RESULTS / "model-step" / "term_rules.json").read_text())["rules"]
    binding = json.loads((CASES / "config_ipnet" / "data_binding.json").read_text())
    spent = 0
    for cond in args.condition or CONDITIONS:
        d = RESULTS / args.size / NAMES[cond]
        d.mkdir(parents=True, exist_ok=True)
        for trial in range(args.trials):
            f = d / ("run%d.json" % (trial + 1))
            if f.exists():
                print("recorded already: %s" % f.relative_to(RESULTS), flush=True)
                continue
            r = G.KeepBindings(case, args.model, cond, rules, binding).run(trial)
            r["network"], r["model"] = args.size, args.model
            tmp = f.with_suffix(".tmp")
            tmp.write_text(json.dumps(r, indent=1))
            tmp.rename(f)
            sc, ef = r["score"], r["effort"]
            spent += ef["total_tokens"]
            print("%s %-12s run %d: bindings right %d of %d, left open %d, wrong %d | observations %d, turns %d, "
                  "tokens %d, %.0f s | not right: %s" % (
                      args.size, cond, trial + 1, sc["bindings_right"], sc["bindings_expected"], sc["bindings_left_open"],
                      sc["bindings_wrong"], ef["observations"], ef["turns"], ef["total_tokens"], ef["latency_s"],
                      ", ".join("%s=%s" % (e["kind"], e["outcome"]) for e in sc["per_event"] if e["outcome"] != "right") or "none"),
                  flush=True)
        rows = [row_of(args.size, cond, json.loads(p.read_text())["trial"], json.loads(p.read_text())) for p in sorted(d.glob("run*.json"))]
        with open(d / "summary.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)
    print("tokens spent in this command: %d" % spent, flush=True)
    print(tables(), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
