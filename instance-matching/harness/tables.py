#!/usr/bin/env python3
"""Rebuild the tables of the note from the recorded runs in results/. Needs no API key.

  python harness/tables.py

Table 1: two agents, how each individual was settled, by network and by whether addresses were present.
Table 3: individuals matched at each placement of cognition.
Every figure is read from the recorded summaries and transcripts; nothing is typed in.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import RESULTS      # noqa: E402

SIZE = {"small": 50, "medium": 150, "large": 658}


def runs(network: str, config: str) -> list[dict]:
    d = RESULTS / network / config
    out = []
    for row in csv.DictReader(open(d / "summary.csv")):
        t = json.loads((d / f"run{int(row['trial']) + 1}.json").read_text())["transcript"]
        row["_steps"] = {s["step"]: s for s in t if s["step"] in ("staging", "sequence")}
        row["_carry"] = json.loads((d / f"run{int(row['trial']) + 1}_carry.json").read_text())
        out.append(row)
    return out


def spread(values) -> str:
    v = sorted(set(values))
    return str(v[0]) if len(v) == 1 else f"{v[0]} to {v[-1]}"


def table1() -> None:
    print("Table 1. Two agents: how each individual was settled\n")
    print("| Network | Addresses | By identifier | By topology | Look-alikes, checked | Matched | Wrong | Runs | Checks made | Tokens per run (million) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for net in ("small", "medium", "large"):
        for label, configs in (("present", ("experiment", "observation")), ("withheld", ("withheld-experiment",))):
            rs = [r for c in configs for r in runs(net, c)]
            st = rs[0]["_steps"]["staging"]
            anch, la = st["anchored"], st["lookalikes_a"]
            assert all(r["_steps"]["staging"]["anchored"] == anch and r["_steps"]["staging"]["lookalikes_a"] == la for r in rs)
            wrong = sum(round(int(r["proposed"]) * (1 - float(r["precision"]))) for r in rs)
            print(f"| {net}, {SIZE[net]} individuals | {label} | {anch} | {SIZE[net] - anch - la} | {la} | "
                  f"{spread(int(r['proposed']) for r in rs)} of {SIZE[net]} | {wrong} | {len(rs)} | "
                  f"{spread(int(r['provision_calls']) for r in rs)} | "
                  f"{min(int(r['total_tokens']) for r in rs) / 1e6:.2f} to {max(int(r['total_tokens']) for r in rs) / 1e6:.2f} |")
    rs = runs("small-same-names", "withheld-experiment")
    print(f"\nSame-name variant (small network, addresses withheld): matched {spread(int(r['proposed']) for r in rs)} of 50 "
          f"in {len(rs)} runs; checks per run {spread(int(r['provision_calls']) for r in rs)}, "
          f"refuted {spread(int(r['refuted_provision']) for r in rs)}.")
    carried = {net: spread(f"{r['_carry']['same_component']} of {r['_carry']['instructions']}"
                           for c in ("experiment", "observation", "withheld-experiment") for r in runs(net, c))
               for net in SIZE}
    print("Instructions carried to the same component: " + "; ".join(f"{k}: {v}" for k, v in carried.items()) + ".\n")


def table3() -> None:
    print("Table 3. Individuals matched, by placement of cognition (three runs per cell)\n")
    print("| Network | Addresses | Both sides inert | One side inert | Both cognitive | Wrong, any cell | Look-alikes guessed by an inert placement |")
    print("|---|---|---|---|---|---|---|")
    for net in ("small", "medium"):
        for label, pre, two in (("present", "", ("experiment", "observation")), ("withheld", "withheld-", ("withheld-experiment",))):
            cells, wrong, guessed = [], 0, 0
            for cfg in (pre + "both-inert", pre + "one-inert"):
                rs = runs(net, cfg)
                cells.append(spread(int(r["proposed"]) for r in rs))
                wrong += sum(round(int(r["proposed"]) * (1 - float(r["precision"]))) for r in rs)
                guessed += sum(r["_steps"]["sequence"]["lookalike_matches_refused"] for r in rs)
            rs = [r for c in two for r in runs(net, c)]
            cells.append(spread(int(r["proposed"]) for r in rs))
            wrong += sum(round(int(r["proposed"]) * (1 - float(r["precision"]))) for r in rs)
            print(f"| {net}, {SIZE[net]} individuals | {label} | {cells[0]} | {cells[1]} | {cells[2]} | {wrong} | {guessed} |")
    rs = [r for net in ("small", "medium") for cfg in ("withheld-both-inert", "withheld-one-inert") for r in runs(net, cfg)]
    print(f"\nVerification pass (inert placements, addresses withheld): {sum(r['_steps']['sequence']['verifier_rejections'] for r in rs)} "
          f"proposed matches rejected across {len(rs)} runs.")


if __name__ == "__main__":
    table1()
    table3()
