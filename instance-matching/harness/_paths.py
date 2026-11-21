"""Paths for the instance-matching harness. It is built on the study harness in ../../study and uses it in place:
the case format and scoring (reconcile.instance), the base stacks, and the study's test helpers."""
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
REPO = HARNESS.parents[1]
STUDY = REPO / "study"
CASES = HARNESS.parent / "cases"            # the networks and the two models of this case study
RESULTS = HARNESS.parent / "results"        # recorded runs
STUDY_CASES = STUDY / "benchmark" / "cases"
for p in (STUDY / "tests", STUDY / "benchmark", STUDY / "pipeline", STUDY / "src", HARNESS, HARNESS / "tests"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
