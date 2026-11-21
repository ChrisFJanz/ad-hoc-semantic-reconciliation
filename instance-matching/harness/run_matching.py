#!/usr/bin/env python3
"""Run instance matching on one case and score it.

One command runs one configuration of the method on one network, a number of times, and scores each run against
the ground truth that the case carries (the scoring is the study harness's own, reconcile.instance and
instance_reconcile.score_row). It writes, under results/<network>/<configuration>/:

  summary.csv          one row per run: individuals matched, precision, recall, checks made, tokens, time
  runN.json            the full transcript of run N: every turn of the conversation and every check
  runN_carry.json      the carry check for run N: instructions carried through the matched individuals

  python harness/run_matching.py --case instance_ipnet_small --config experiment \
         --anchors results/model-step/term_rules.json --confirm-lookalikes --staged 60 --trials 3

Placements: with --placement both_cognitive (the default) two agents converse; with both_inert or one_inert a
single reasoner runs the same sequence over the records (matching/single_reasoner.py).
Resumable: runs already in summary.csv are skipped. Needs OPENAI_API_KEY (see ../../study/SETUP_OPENAI.md).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)

from reconcile.instance import load_instance_case                                   # noqa: E402
from reconcile.stacks.agent_instance import InstanceAgentStack                      # noqa: E402
from matching.two_agent import TwoAgentInstanceStack          # noqa: E402
from matching.two_agent_staged import StagedTwoAgentInstanceStack   # noqa: E402
from matching.carry import carry, generate                                # noqa: E402
from matching.anchor import anchor_join, shuffled, withhold               # noqa: E402
from matching.single_reasoner import SequencedReasonerStack        # noqa: E402
from instance_reconcile import COLUMNS, FULL_EVIDENCE, score_row, trap_names        # noqa: E402
from run import load_dotenv                                                         # noqa: E402

COLS = ["stack"] + COLUMNS


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", default="instance_hard")
    ap.add_argument("--model", default="gpt-5.6-sol")
    ap.add_argument("--trials", type=int, default=1)
    ap.add_argument("--max-rounds", type=int, default=8, help="two-agent negotiation round cap")
    ap.add_argument("--budget", default=None, help="oracle budget: an int, or omit for unbounded")
    ap.add_argument("--only-stack", choices=["single", "two-agent", "both"], default="both")
    ap.add_argument("--placement", choices=["both_cognitive", "one_inert", "both_inert"], default="both_cognitive",
                    help="which sides are cognitive; with an inert side there is no partner, so the single reasoner runs")
    ap.add_argument("--no-operations", action="store_true",
                    help="withhold the virtual operation on ports and bundles even if the case defines it")
    ap.add_argument("--no-interrogation", action="store_true",
                    help="withhold interrogation (two-agent stack), leaving only the virtual operation")
    ap.add_argument("--staged", type=int, default=0, metavar="N",
                    help="two-agent stack, staged: devices first, then the components of the settled "
                         "devices in batches of at most N side-A components (0 = unstaged, the method in full)")
    ap.add_argument("--confirm", action="store_true",
                    help="two-agent stack: the protocol puts every agreed port/bundle correspondence to the "
                         "virtual experiment before it counts as settled")
    ap.add_argument("--experiment", choices=["twin", "live"], default="twin",
                    help="what an experiment is: a virtual operation on a digital twin (default), or a live, "
                         "non-disruptive comparison of the data recorded for the component through each handle")
    ap.add_argument("--anchors", default=None, metavar="TERM_RULES.json",
                    help="anchor first: settle by identity anchors (a join on the identity-valued terms of the "
                         "given term rules) before any conversation; only the rest comes up in conversation")
    ap.add_argument("--schema-case", default="config_ipnet", help="where the data binding for --anchors lives")
    ap.add_argument("--confirm-lookalikes", action="store_true",
                    help="require a test only for correspondences that involve a look-alike (needs --anchors)")
    ap.add_argument("--withhold-addresses", action="store_true",
                    help="variant: neither graph records port or bundle addresses")
    ap.add_argument("--shuffle", action="store_true",
                    help="variant: each trial lists individuals and relations in a fresh random order")
    ap.add_argument("--config", default="run", help="name of this configuration; results go to results/<network>/<config>/")
    ap.add_argument("--out", default=None)
    ap.add_argument("--save-transcripts", action="store_true")
    ap.add_argument("--all-transcripts", action="store_true",
                    help="save the transcript of every trial (file name carries the trial), and carry "
                         "instructions on each result (no model call)")
    ap.add_argument("--progress-log", default=None, help="append one line per finished dialogue to this file")
    args = ap.parse_args()

    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set; see SETUP_OPENAI.md", file=sys.stderr)
        return 2
    case = load_instance_case(CASES / args.case)
    if args.withhold_addresses:
        case = withhold(case)
    term_rules = binding = None
    if args.anchors:
        term_rules = json.loads(Path(args.anchors).read_text())["rules"]
        binding = json.loads((CASES / args.schema_case / "data_binding.json").read_text())
    names = trap_names(case)
    budget = None if args.budget in (None, "unbounded") else int(args.budget)
    network = args.case.replace("instance_ipnet_", "").replace("small_namesonly", "small-same-names")
    tdir = RESULTS / network / args.config
    tdir.mkdir(parents=True, exist_ok=True)
    out = Path(args.out) if args.out else tdir / "summary.csv"
    out.parent.mkdir(exist_ok=True)
    done = set()
    if out.exists():
        with out.open(newline="") as f:
            done = {(r["stack"], r["model"], r["trial"]) for r in csv.DictReader(f)}
    fh = out.open("a", newline="")
    w = csv.DictWriter(fh, fieldnames=COLS)
    if not done and out.stat().st_size == 0:
        w.writeheader(); fh.flush()

    stacks = ["single", "two-agent"] if args.only_stack == "both" else [args.only_stack]
    sequenced = args.placement != "both_cognitive" and bool(args.anchors)
    if sequenced:      # an inert side: the same sequence, with one reasoner over the records
        stacks = ["reasoner"]
    models = [m.strip() for m in args.model.split(",") if m.strip()]
    for model in models:
        for stack in stacks:
            for t in range(max(1, args.trials)):
                if (stack, model, str(t)) in done:
                    print(f"{stack}/{model}/trial {t+1}  (captured, skip)", file=sys.stderr)
                    continue
                print(f"{stack}/{model}/trial {t+1} ...", file=sys.stderr, flush=True)
                if sequenced:
                    run_case = shuffled(case, 1000 + t) if args.shuffle else case
                    pairs, why = anchor_join(run_case, term_rules, binding)
                    s = SequencedReasonerStack(run_case, model, args.placement, pairs)
                    print(f"      anchors: {len(pairs)} of {len(run_case.a)} settled by identifier; look-alikes: "
                          f"{sum(len(g) for g in s.lookalikes['A'])} on A, {sum(len(g) for g in s.lookalikes['B'])} on B",
                          file=sys.stderr, flush=True)
                elif stack == "single":
                    s = InstanceAgentStack(case, model=model, budget=budget)
                else:
                    kw = dict(model=model, budget=budget, max_rounds=args.max_rounds,
                              operations=False if args.no_operations else None,
                              interrogation=not args.no_interrogation, confirm=args.confirm, experiment=args.experiment)
                    run_case = shuffled(case, 1000 + t) if args.shuffle else case
                    if args.confirm_lookalikes:
                        kw["confirm"] = "lookalikes"
                    s = (StagedTwoAgentInstanceStack(run_case, batch_size=args.staged, **kw) if args.staged
                         else TwoAgentInstanceStack(run_case, **kw))
                    if args.anchors:
                        pairs, why = anchor_join(run_case, term_rules, binding)
                        s.use_anchors(pairs)
                        print(f"      anchors: {len(pairs)} of {len(run_case.a)} settled by identifier; look-alikes: "
                              f"{sum(len(g) for g in s.lookalikes['A'])} on A, {sum(len(g) for g in s.lookalikes['B'])} on B",
                              file=sys.stderr, flush=True)
                if args.progress_log:
                    def _progress(d, _label=f"{network}/{args.config} {stack}/{model} run {t + 1}"):
                        with open(args.progress_log, "a") as pf:
                            pf.write(f"{time.strftime('%H:%M:%S')} {_label}: dialogue {d['stage'] if d['stage'] is not None else 1}"
                                     f" done, {d['settled']} settled, {d['experiments']} experiments, "
                                     f"{d['turns']} turns, {d['total_tokens']} tokens\n")
                    s.progress = _progress
                try:
                    rec = s.reconcile(placement=args.placement)
                except Exception as e:
                    print(f"      ! error: {e}", file=sys.stderr, flush=True)
                    continue
                r = score_row(case, rec, model, budget, t, names, FULL_EVIDENCE)
                r["refuted_provision"] = sum(1 for x in rec.transcript if x.get("step") == "virtual_provision"
                                             and x["result"]["answer"].get("confirmed") is False)
                r["stack"] = stack
                w.writerow(r); fh.flush()
                if args.all_transcripts:
                    tp = tdir / f"run{t + 1}.json"
                    tp.write_text(json.dumps({"model": model, "stack": stack, "row": r,
                                              "transcript": rec.transcript}, indent=2))
                    cres = carry(case, generate(case, set(rec.proposed)))
                    tp.with_name(tp.stem + "_carry.json").write_text(json.dumps(cres, indent=2))
                    print(f"      carry: {cres['instructions']} instructions, {cres['same_component']} same component, "
                          f"{cres['wrong_component']} different, round trip {cres['round_trip_ok']}", file=sys.stderr, flush=True)
                    if args.progress_log:
                        with open(args.progress_log, "a") as pf:
                            pf.write(f"{time.strftime('%H:%M:%S')} {network}/{args.config} {stack}/{model} run {t + 1} FINISHED: "
                                     f"{r['proposed']} proposed, precision {r['precision']}, recall {r['recall']}, "
                                     f"carry {cres['same_component']}/{cres['instructions']} same component\n")
                if args.save_transcripts and t == 0:
                    (tdir / "last_transcript.json").write_text(
                        json.dumps({"model": model, "stack": stack, "row": r, "transcript": rec.transcript}, indent=2))
                print(f"      prec {r['precision']} rec {r['recall']} fc {r['surviving_instance_fc']} "
                      f"resid {r['residual_total']} probes[i{r['interrogate_calls']}/p{r['provision_calls']}] "
                      f"turns {r['turns']} tokens {r['total_tokens']}", file=sys.stderr, flush=True)
    fh.close()
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
