#!/usr/bin/env python3
"""Generate the two translators from a saved instance-matching run and carry instructions across.

No model is called. The settled correspondences of the run are read from its saved transcript,
turned into a translator for each side, and one instruction per operable component is carried
from agent A to agent B and executed on the shared virtual network.

  python pipeline/carry_instructions.py --case instance_ipnet_medium \\
      --run results/instance_transcripts/<saved run>.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)

from reconcile.instance import load_instance_case                                   # noqa: E402
from matching.carry import carry, correspondences_from_transcript, generate   # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--run", required=True, help="saved run (transcript JSON)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    case = load_instance_case(CASES / args.case)
    run = json.loads(Path(args.run).read_text())
    corr = correspondences_from_transcript(case, run["transcript"])
    want = run.get("row", {}).get("proposed")
    if want is not None and int(want) != len(corr):
        print(f"! the run recorded {want} correspondences, the transcript yields {len(corr)}", file=sys.stderr)
        return 1
    tr = generate(case, corr)
    res = carry(case, tr)
    out = Path(args.out) if args.out else Path(args.run).with_name(Path(args.run).stem + "_carry.json")
    out.write_text(json.dumps({"case": args.case, "run": Path(args.run).name, "translators": tr, **res}, indent=2))
    print(f"{args.case}: {len(corr)} correspondences -> translators; {res['instructions']} instructions, "
          f"{res['carried']} carried, {res['same_component']} on the same component, "
          f"{res['wrong_component']} on a different component, round trip returns the original for "
          f"{res['round_trip_ok']}")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
