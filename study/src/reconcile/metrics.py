"""Scoring a reconciliation against a gold standard.

The metric families follow Part II: reliability (precision, recall, surviving
false cognates), mechanical work, residual and closure, and scaling. Cognitive
effort is left blank here; it is filled in only when a language-model stack runs,
from the effort signals the model exposes.
"""
from __future__ import annotations

from reconcile.model import Gold
from reconcile.stacks.base import Reconciliation


def _safe_div(n: int, d: int) -> float:
    return n / d if d else 0.0


def score(rec: Reconciliation, gold: Gold) -> dict:
    proposed = set(rec.proposed)
    correct = gold.correct_pairs
    false_cog = gold.false_cognate_pairs

    tp = len(proposed & correct)
    fp = len(proposed - correct)
    fn = len(correct - proposed)
    surviving_fc = len(proposed & false_cog)

    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall) if (precision + recall) else 0.0

    scaling = "~N" if rec.uses_reference else "~N^2"
    effort = rec.effort or {}

    return {
        "stack": rec.stack,
        "uses_reference": rec.uses_reference,
        "placement": rec.placement,
        "proposed": len(proposed),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "surviving_false_cognates": surviving_fc,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "residual": len(rec.residual_a) + len(rec.residual_b),
        "candidates": rec.work.get("candidates", 0),
        "bilateral_checks": rec.work.get("bilateral_checks", 0),
        "binding_ops": rec.work.get("binding_ops", 0),
        "scaling": scaling,
        # cognitive effort: blank for model-agnostic stacks, filled by an LM stack
        "total_tokens": effort.get("total_tokens", ""),
        "reasoning_tokens": effort.get("reasoning_tokens", "") if effort.get("reasoning_tokens") is not None else "",
        "latency_s": effort.get("latency_s", ""),
        "model": effort.get("model", ""),
    }


METRIC_COLUMNS = [
    "case", "stack", "uses_reference", "placement",
    "proposed", "true_positives", "false_positives", "false_negatives",
    "surviving_false_cognates", "precision", "recall", "f1",
    "residual", "candidates", "bilateral_checks", "binding_ops", "scaling",
    "total_tokens", "reasoning_tokens", "latency_s", "model",
]
