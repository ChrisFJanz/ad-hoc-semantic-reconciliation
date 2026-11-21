#!/usr/bin/env python3
"""The recorded runs of the instance-matching case study, as one resumable queue.

Each line below is one configuration of run_matching.py: a network, a name, and the options that define it. A
configuration already recorded is skipped, so the queue can be stopped (Ctrl-C) and started again with the same
command. Progress is appended, one line per finished conversation, to results/progress.log.

  python harness/record_runs.py --list                 # print the configurations and stop
  python harness/record_runs.py --set two-agents       # the rows of the note's Table 1
  python harness/record_runs.py --set inert            # the inert placements of Table 3
  python harness/record_runs.py --set same-names       # the same-name variant
  python harness/record_runs.py --only medium          # only configurations whose network or name contains "medium"

Cost, with gpt-5.6-sol and three runs each (tokens per run): small 0.1 to 0.2 million; medium 0.2 to 0.6 million;
large 1.1 to 1.4 million with addresses present and 2.6 to 2.8 million with addresses withheld (about 22 minutes
a run). The inert placements cost 0.02 to 0.3 million per run.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import RESULTS, HARNESS      # noqa: E402

MODEL = "gpt-5.6-sol"
RULES = str(RESULTS / "model-step" / "term_rules.json")     # the value rules from the model step (generate_and_carry.py)
ANCHORS = ["--anchors", RULES]
TWO = ANCHORS + ["--confirm-lookalikes", "--staged", "60"]   # two agents: anchors first, checks for look-alikes, bounded conversations
WITHHELD = ["--withhold-addresses"]

TWO_AGENTS = [(f"instance_ipnet_{n}", name, opts) for n in ("small", "medium", "large") for name, opts in (
    ("experiment",          TWO),                              # the check is an experiment on a digital twin
    ("observation",         TWO + ["--experiment", "live"]),   # the check is a live observation
    ("withheld-experiment", TWO + WITHHELD))]                  # every IP address withheld from both agents

INERT = [(f"instance_ipnet_{n}", name, ANCHORS + opts) for n in ("small", "medium") for name, opts in (
    ("both-inert",          ["--placement", "both_inert"]),
    ("one-inert",           ["--placement", "one_inert"]),
    ("withheld-both-inert", ["--placement", "both_inert"] + WITHHELD),
    ("withheld-one-inert",  ["--placement", "one_inert"] + WITHHELD))]

SAME_NAMES = [("instance_ipnet_small_namesonly", "withheld-experiment", TWO + WITHHELD)]

SETS = {"two-agents": TWO_AGENTS, "inert": INERT, "same-names": SAME_NAMES}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--set", choices=list(SETS) + ["all"], default="all", help="which configurations to run")
    ap.add_argument("--only", default="", help="run only configurations whose network or name contains this text")
    args = ap.parse_args()
    queue = [c for k, v in SETS.items() if args.set in (k, "all") for c in v]
    log = RESULTS / "progress.log"
    for case, name, extra in queue:
        if args.only and args.only not in case + " " + name:
            continue
        cmd = [sys.executable, str(HARNESS / "run_matching.py"), "--case", case, "--model", MODEL,
               "--only-stack", "two-agent", "--trials", str(args.trials), "--config", name, "--all-transcripts",
               "--progress-log", str(log)] + extra
        print(" ".join(cmd[1:]), flush=True)
        if args.list:
            continue
        rc = subprocess.call(cmd)
        if rc != 0:
            print(f"! stopped: {case} {name} returned {rc}", file=sys.stderr)
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
