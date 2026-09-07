#!/usr/bin/env python3
"""Six-model capability gradient (master Figure 8 / the omit-to-commit gradient).

The raw six-model run behind the original figure was a scratch run whose CSVs were not kept;
the values below are transcribed from the published master-report figure (confirmed with the
author) so the figure matches the report by construction. Reader-facing labels say
"resolved fraction" (not "recall"); no em-dashes.

Writes figures/fig_ladder_gradient.png (light background).
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
NAVY, INK, SURFACE, FAINT = "#14314f", "#1a1a1a", "#fbfaf8", "#6a655e"
TEAL, RED, ORANGE = "#1baf7a", "#b23a48", "#eb6834"

MODELS = ["5.6\nSol", "5.6\nTerra", "5.6\nLuna", "5.4\nSol", "5.4\nMini", "5.4\nNano"]
PRECISION = [0.98, 1.00, 1.00, 0.94, 0.90, 0.83]
RESOLVED  = [0.78, 0.72, 0.73, 0.83, 0.91, 0.94]
SURV_FC   = [0.00, 0.00, 0.00, 0.25, 0.12, 0.75]


def main():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.2, 5.2), gridspec_kw={"width_ratios": [1.25, 1]})
    x = np.arange(len(MODELS))

    # ---- Left: precision vs resolved fraction, down the ladder ----
    axL.plot(x, PRECISION, "-o", color=NAVY, lw=2.2, markersize=7, label="precision", zorder=3)
    axL.plot(x, RESOLVED, "-s", color=TEAL, lw=2.2, markersize=7, label="resolved fraction", zorder=3)
    axL.annotate("omit", (x[0], RESOLVED[0]), textcoords="offset points", xytext=(-2, -16),
                 ha="center", fontsize=10.5, color=NAVY, fontweight="bold")
    axL.annotate("commit", (x[4], RESOLVED[4]), textcoords="offset points", xytext=(0, 10),
                 ha="center", fontsize=10.5, color=TEAL, fontweight="bold")
    axL.set_title("Precision falls, resolved fraction rises as capability drops",
                  fontsize=11, color=NAVY)
    axL.set_ylim(0.5, 1.03)
    axL.set_xticks(x); axL.set_xticklabels(MODELS, fontsize=9)
    axL.legend(frameon=False, fontsize=9.5, loc="lower left")

    # ---- Right: surviving false cognates rise at the weak end ----
    axR.bar(x, SURV_FC, 0.62, color=RED, zorder=3)
    axR.set_title("Surviving false cognates rise at the weak end", fontsize=11, color=NAVY)
    axR.set_ylim(0.0, 1.0)
    axR.set_xticks(x); axR.set_xticklabels(MODELS, fontsize=9)

    for ax in (axL, axR):
        ax.set_facecolor(SURFACE)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.grid(axis="y", ls=":", alpha=0.5); ax.set_axisbelow(True)

    fig.suptitle("Six-model capability gradient (no reference, both-cognitive, mean over 4 cases)",
                 fontsize=12.5, color=NAVY, y=1.0)
    fig.text(0.5, -0.02,
             "Strong end (5.6 tier) defers at perfect precision; weak end (5.4 nano) commits freely "
             "and takes the traps.",
             ha="center", fontsize=9.5, color=ORANGE, style="italic")
    fig.tight_layout()
    fig.savefig(FIG / "fig_ladder_gradient.png", dpi=150, facecolor=SURFACE, bbox_inches="tight")
    print("wrote", (FIG / "fig_ladder_gradient.png").name)


if __name__ == "__main__":
    main()
