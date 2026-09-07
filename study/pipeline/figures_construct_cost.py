#!/usr/bin/env python3
"""Construct-cost / redundancy figure (Track A6): when is building the shared reference
worth the cognition it costs? Left: the strong agent's close by condition across the three
schema settings, with the cognition spent written on each bar — construction is load-bearing
only where no standard exists (cross-domain), and redundant where a given reference already
does the job cheaply. Right: construction cost down the model ladder — it explodes for weak
agents and buys a worse close, not a better one.

Reads results/construct_cost_config_{big_hard,cross_domain,observability}.csv.
Writes figures/fig_construct_cost.png (light background).
"""
from __future__ import annotations
import csv, statistics as st
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
BLUE, ORANGE, GREY, AQUA = "#2a78d6", "#eb6834", "#b8c2cc", "#1baf7a"
NAVY, SURFACE, INK, FAINT = "#14314f", "#fbfaf8", "#1a1a1a", "#6a655e"
SETTINGS = [("config_big_hard", "Setting 1\nconfiguration\n(a standard exists)"),
            ("config_cross_domain", "Setting 3\ncross-domain\n(no standard)"),
            ("config_observability", "Setting 4\nobservability\n(RFC anchor)")]
CONDS = [("no-ref", "no reference", GREY), ("constructed", "constructed", ORANGE),
         ("given-ref", "given reference", BLUE)]


def load(c):
    return list(csv.DictReader(open(ROOT / "results" / f"construct_cost_{c}.csv")))


def mean(rows, k):
    v = [float(r[k]) for r in rows if r.get(k) not in ("", None)]
    return st.mean(v) if v else float("nan")


def main():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.2, 5.4), gridspec_kw={"width_ratios": [1.7, 1]})

    # ---- Left: strong agent (sol), recall by condition per setting, spend annotated ----
    x = np.arange(len(SETTINGS)); w = 0.26
    for i, (cond, clabel, color) in enumerate(CONDS):
        recs, spends = [], []
        for c, _ in SETTINGS:
            rc = [r for r in load(c) if r["condition"] == cond and r["model"] == "gpt-5.6-sol"]
            recs.append(mean(rc, "recall")); spends.append(mean(rc, "total_reasoning_tokens"))
        xs = x + (i - 1) * w
        bars = axL.bar(xs, recs, w, color=color, label=clabel, zorder=3)
        for xi, r, s in zip(xs, recs, spends):
            sp = f"{s / 1000:.1f}k" if s >= 1000 else f"{s:.0f}"
            axL.annotate(f"{r:.2f}\n{sp} tok", (xi, r), textcoords="offset points", xytext=(0, 3),
                         ha="center", va="bottom", fontsize=7.2, color=INK,
                         bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    axL.set_title("The strong agent: resolved fraction by condition, with the cognition spent (tokens)\n"
                  "construction is load-bearing only where no standard exists (Setting 3);\n"
                  "elsewhere a given reference matches it far more cheaply",
                  fontsize=10, color=NAVY)
    axL.set_ylabel("resolved fraction  (share of true matches found)", fontsize=9.5)
    axL.set_xticks(x); axL.set_xticklabels([s[1] for s in SETTINGS], fontsize=9)
    axL.set_ylim(0, 1.28); axL.axhline(1.0, color=NAVY, ls=":", lw=1)
    axL.legend(frameon=True, framealpha=0.9, edgecolor="none", facecolor=SURFACE,
               fontsize=9, loc="upper center", ncol=3)
    axL.annotate("no standard →\nbuilding it pays\n(0.50 → 0.93)", xy=(1 - 0.26, 0.50),
                 xytext=(1 - 0.72, 0.30), fontsize=8.2, color=ORANGE, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.3))

    # ---- Right: construction cost explodes down the ladder, close gets worse ----
    models = [("gpt-5.6-sol", "sol\n(strong)"), ("gpt-5-mini", "mini\n(mid)"), ("gpt-5-nano", "nano\n(weak)")]
    spend, rec = [], []
    for m, _ in models:
        rows = [r for c, _ in SETTINGS for r in load(c) if r["condition"] == "constructed" and r["model"] == m]
        spend.append(mean(rows, "total_reasoning_tokens")); rec.append(mean(rows, "recall"))
    xm = np.arange(len(models))
    bars = axR.bar(xm, spend, 0.6, color=[AQUA, ORANGE, "#b23a48"], zorder=3)
    for xi, s, r in zip(xm, spend, rec):
        axR.annotate(f"{s:,.0f} tok", (xi, s), textcoords="offset points", xytext=(0, 14),
                     ha="center", va="bottom", fontsize=8.5, color=INK, fontweight="bold")
        axR.annotate(f"resolved fraction {r:.2f}", (xi, s), textcoords="offset points", xytext=(0, 3),
                     ha="center", va="bottom", fontsize=7.6, color=FAINT)
    axR.set_title("Cost of CONSTRUCTING the reference, down the ladder\n"
                  "(mean over the three settings): it explodes for weaker\n"
                  "agents and buys a worse close, not a better one",
                  fontsize=10, color=NAVY)
    axR.set_ylabel("reasoning tokens to construct + bind", fontsize=9.5)
    axR.set_xticks(xm); axR.set_xticklabels([m[1] for m in models], fontsize=9)
    axR.set_ylim(0, max(spend) * 1.30)

    for ax in (axL, axR):
        ax.set_facecolor(SURFACE)
        for sname in ("top", "right"):
            ax.spines[sname].set_visible(False)
        ax.grid(axis="y", ls=":", alpha=0.5); ax.set_axisbelow(True)
    fig.suptitle("When is constructing the shared reference worth the cognition it costs?",
                 fontsize=12.5, fontweight="bold", color=NAVY, y=1.005)
    fig.tight_layout()
    fig.savefig(FIG / "fig_construct_cost.png", dpi=150, facecolor=SURFACE, bbox_inches="tight")
    print("wrote", (FIG / "fig_construct_cost.png").name)


if __name__ == "__main__":
    main()
