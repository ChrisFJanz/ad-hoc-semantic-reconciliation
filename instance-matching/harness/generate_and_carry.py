#!/usr/bin/env python3
"""Generate and carry for the IP-network case, at the level of the models AND of the individuals.

  1. reads the correspondences a saved model reconciliation settled (a results/*transcript*.json
     with a 'confirmed' list);
  2. GENERATE: one model call turns them into value rules, the translator for the terms;
  3. reads the individuals a saved instance-matching run matched; they are the other half of the translator;
  4. CARRY (no model call): every value agent B holds about a component is restated for agent A in
     A's term, unit and individual, and compared with what agent A itself records.

  python pipeline/generate_and_carry_ipnet.py --reconciliation results/experiment_transcript_config_ipnet.json \\
      --instance-case instance_ipnet_medium --run results/instance_transcripts/<saved run>.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)

from reconcile.harness import Case                                                    # noqa: E402
from reconcile.instance import load_instance_case                                     # noqa: E402
from matching.carry import carry, correspondences_from_transcript, generate  # noqa: E402
from matching.term_translator import carry_observations, generate_term_rules          # noqa: E402
from run import load_dotenv                                                           # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--schema-case", default="config_ipnet")
    ap.add_argument("--reconciliation", required=True)
    ap.add_argument("--instance-case", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--model", default="gpt-5.6-sol")
    ap.add_argument("--rules", default=None, help="reuse a saved rules file instead of calling the model")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    sdir = CASES / args.schema_case
    schema = Case.load(sdir)
    binding = json.loads((sdir / "data_binding.json").read_text())
    rec = json.loads(Path(args.reconciliation).read_text())
    corr = [tuple(p) for p in rec["confirmed"]]
    out = Path(args.out) if args.out else RESULTS / f"generate_carry_{args.instance_case}_{Path(args.run).stem}.json"
    rules_path = Path(args.rules) if args.rules else RESULTS / f"term_rules_{args.schema_case}.json"
    if rules_path.exists():
        rules = json.loads(rules_path.read_text())["rules"]
        print(f"term rules: reusing {rules_path.name} ({len(rules)} rules)")
    else:
        load_dotenv()
        if not os.environ.get("OPENAI_API_KEY"):
            print("OPENAI_API_KEY not set; see notes/SETUP_OPENAI.md", file=sys.stderr)
            return 1
        rules, eff = generate_term_rules(schema.model_a, schema.model_b, corr, args.model)
        rules_path.write_text(json.dumps({"model": args.model, "from": Path(args.reconciliation).name,
                                          "effort": eff, "rules": rules}, indent=2))
        print(f"term rules: generated {eff['rules']} of {eff['asked']} ({eff['total_tokens']} tokens) -> {rules_path.name}")
    for r in rules:
        how = r["value_rule"] if r["value_rule"] != "scale" else f"scale x{r['a_to_b_factor']:g} ({r['a_unit']} -> {r['b_unit']})"
        print(f"   {r['a_id']:10s} <-> {r['b_id']:10s} {how}")

    case = load_instance_case(CASES / args.instance_case)
    run = json.loads(Path(args.run).read_text())
    tr = generate(case, correspondences_from_transcript(case, run["transcript"]))
    ops = carry(case, tr)
    obs = carry_observations(case, rules, tr, binding)
    out.write_text(json.dumps({"schema_case": args.schema_case, "instance_case": args.instance_case,
                               "run": Path(args.run).name, "term_rules": rules,
                               "individuals_matched": len(tr["a_to_b"]),
                               "operations": {k: v for k, v in ops.items() if k != "rows"},
                               "observations": obs}, indent=2))
    print(f"observations agent B holds: {obs['observations']}; carried to agent A: {obs['carried']}; "
          f"agree with A's own record: {obs['agree']}; differ: {obs['differ']}")
    for k, d in obs["by_term"].items():
        print(f"   {k:8s} {d['observations']:4d} observed, {d['carried']:4d} carried, {d['agree']:4d} agree")
    print(f"operations: {ops['instructions']} carried, {ops['same_component']} on the same component, "
          f"{ops['wrong_component']} on a different component")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
