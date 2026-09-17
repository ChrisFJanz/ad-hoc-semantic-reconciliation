#!/usr/bin/env python3
"""SCAFFOLD (portability program, E22 Phase 3) -> pipeline/portability_degraded.py when finalised.

Degrade the LIFT (thin surface, +/- reference during lifting), produce a model, then measure its
comprehensibility across the reasoning ladder (+/- reference at consumption). This is where the reference's
PRODUCTION-side role (reference-in-lift) and the confabulation hazard live. See _shelf/PORTABILITY_program.md
"E22 Phase 3 — detailed design".

Pipeline (all halves already exist — reuse):
  thin surface (E17 ladder) -> lift_model() produces a degraded SemanticModel -> comprehension harness.

TWO integration points to finalise WITH Chris (marked TODO below):
  (1) thin_model(sm, rung) -> (thinned SemanticModel, idmap): a thinned MODEL (not just a surface dict) so
      lift_model can lift it. Mirror cold_start_lift.thin()'s stripping; verify against it before running.
  (2) reference-IN-lift: lift_model() has no reference param. Add one (include reference entries in the lift
      payload + a system-prompt line) OR write a thin wrapper. This is the production-side reference variable.

Metric refinement (Phase 3 ONLY; the live src/reconcile/comprehension.py is left untouched until the Phase
1-2 run is reviewed): judge verdict is faithful / partial / abstained / invented. On a degraded model
ABSTENTION is a virtue ("cannot determine from the package"); INVENTION is the hazard.

    python pipeline/portability_degraded.py --validate    # offline: thinning + scoring, no API
    python pipeline/portability_degraded.py --lifter gpt-5.6-sol --consumers gpt-5.6-sol,gpt-5-mini,gpt-5-nano \\
        --rungs named,typed,data --trials 3
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import dataclasses
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # -> study/ once moved to pipeline/
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "pipeline"))

from reconcile.model import Case, SemanticModel                          # noqa: E402
from reconcile.lift import lift_model                                    # noqa: E402
from reconcile.comprehension import (load_comprehension, comprehend,      # noqa: E402
                                     score_comprehension, ConsumerAnswer, Verdict)

CASES = ["config_cross_domain", "config_big_hard", "config_rest"]
RUNGS = ["named", "typed", "data", "topology"]   # E17 ladder; named = rich control
JUDGE_MODEL = "gpt-5.6-sol"

COLS = ["case", "rung", "ref_in_lift", "lifter", "consumer", "ref_at_consumption", "trial",
        "meaning_score", "abstention_rate", "confabulation_rate", "use_recall", "use_precision",
        "lift_coverage", "total_tokens", "reasoning_tokens"]


# ---- (1) TODO: thin a MODEL (mirror cold_start_lift.thin's per-rung stripping) ---------------------
def thin_model(sm: SemanticModel, rung: str):
    """Return (thinned SemanticModel, idmap real<-opaque). Per E17: names stripped for typed/data/topology,
    types for data/topology, data for topology. VERIFY field-for-field against cold_start_lift.thin() before
    running — this is a faithful sketch, not yet cross-checked."""
    names = rung == "named"
    types = rung in ("named", "typed")
    data = rung in ("named", "typed", "data")
    idmap = {}
    new = []
    for i, c in enumerate(sm.concepts):
        opaque = c.id if names else f"c{i}"          # hide names behind opaque ids at thinner rungs
        idmap[opaque] = c.id
        new.append(dataclasses.replace(
            c,
            id=opaque,
            label=(c.label if names else opaque),
            synonyms=(list(c.synonyms) if names else []),
            kind=(c.kind if types else "leaf"),
            instances=(list(c.instances) if data else []),
            gloss="", example="",                     # never hand meaning to the lift
        ))
    thinned = SemanticModel(system=sm.system, dialect=sm.dialect, modules=sm.modules, concepts=new)
    return thinned, idmap


# ---- (2) TODO: lift WITH optional reference (reference-in-lift) ------------------------------------
def lift_degraded(sm: SemanticModel, lifter: str, reference, *, ref_in_lift: bool, client=None):
    """Lift the thinned surface, optionally with the reference available to the lifter. For now delegates
    to lift_model (ref_in_lift OFF). ref_in_lift ON needs lift_model to accept a reference (add reference
    entries to the lift payload + a system line) — small change, do WITH Chris."""
    if ref_in_lift and reference is not None:
        # TODO: lift_model(sm, lifter, reference=reference, client=client)  -- after lift_model gains the arg
        raise NotImplementedError("reference-in-lift pending lift_model reference support")
    return lift_model(sm, lifter, client=client)


def _remap(sm: SemanticModel, idmap: dict) -> SemanticModel:
    """Map opaque ids in a lifted thinned model back to the real ids the gold uses."""
    out = [dataclasses.replace(c, id=idmap.get(c.id, c.id)) for c in sm.concepts]
    return SemanticModel(system=sm.system, dialect=sm.dialect, modules=sm.modules, concepts=out)


# ---- refined judge + scoring (faithful / partial / abstained / invented) --------------------------
_JUDGE_SYSTEM_P3 = (
    "You grade a consumer's stated meaning for each concept against an authored answer key, over a possibly "
    "DEGRADED model. For each question return a verdict: 'faithful' (matches the key), 'partial' (right "
    "direction, hedged/incomplete), 'abstained' (the consumer honestly says it cannot determine the meaning "
    "from what it was given — NOT a guess), or 'invented' (asserts a meaning the key does not support). "
    "Abstaining when the meaning is absent is correct, not a failure; inventing is the failure."
)  # DRAFT — used instead of the Phase 1-2 judge only here.


def score_degraded(gold, answer: ConsumerAnswer, verdicts) -> dict:
    """faithful = comprehended from the package; abstained = honest deferral (virtue on a degraded model);
    invented = confabulation (the hazard). Reuses the use-task scoring from score_comprehension."""
    v = {x.qid: x.label for x in verdicts}
    n = max(1, len(gold.meaning_questions))
    cnt = lambda lab: sum(1 for q in gold.meaning_questions if v.get(q.id) == lab)
    base = score_comprehension(gold, answer, [Verdict(qid=q.id,
                    label=("invented" if v.get(q.id) == "invented" else "faithful"))
                    for q in gold.meaning_questions])  # reuse use_recall/precision only
    return {
        "meaning_score": round(cnt("faithful") / n, 3),
        "abstention_rate": round(cnt("abstained") / n, 3),
        "confabulation_rate": round(cnt("invented") / n, 3),
        "use_recall": base["use_recall"],
        "use_precision": base["use_precision"],
    }


def validate() -> int:
    ok = True
    for case_name in CASES:
        cdir = ROOT / "benchmark" / "cases" / case_name
        if not (cdir / "comprehension.json").exists():
            print(f"  {case_name:20} (no comprehension.json)"); continue
        case = Case.load(cdir)
        prev = len(case.model_a.concepts)
        for rung in RUNGS:
            thinned, idmap = thin_model(case.model_a, rung)
            same_ct = len(thinned.concepts) == prev
            remapped = _remap(thinned, idmap)
            ids_ok = {c.id for c in remapped.concepts} == {c.id for c in case.model_a.concepts}
            ok = ok and same_ct and ids_ok
        print(f"  {case_name:20} thinning OK across rungs; ids round-trip = {ids_ok}")
    print("validate:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lifter", default="gpt-5.6-sol", help="tier that performs the lift (fixed by default)")
    ap.add_argument("--consumers", default="gpt-5.6-sol,gpt-5-mini,gpt-5-nano")
    ap.add_argument("--judge", default=JUDGE_MODEL)
    ap.add_argument("--rungs", default="named,typed,data")
    ap.add_argument("--ref-in-lift", default="both", choices=["0", "1", "both"])
    ap.add_argument("--ref-at-consumption", default="both", choices=["0", "1", "both"])
    ap.add_argument("--cases", default=",".join(CASES))
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "results" / "portability_degraded.csv"))
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if args.validate:
        return validate()
    print("SCAFFOLD: resolve the two TODOs (thin_model cross-check; lift_model reference-in-lift) with Chris "
          "before the API run. Structure is in place; --validate exercises the offline half.", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
