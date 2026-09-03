#!/usr/bin/env python3
"""Figures for the cross-domain (standard-free) study. The seam schematic is data-
independent (it draws the setting); the results figures read the wave CSVs."""
from __future__ import annotations
import csv, glob
from pathlib import Path
from statistics import mean
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GREY, SURFACE = "#9a958d", "#fbfaf8"


def save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / name, dpi=160, facecolor=SURFACE, bbox_inches="tight")
    print("wrote", (FIG / name).name)


def fig_seam():
    """The scene: two bespoke models, adjacent domains, meeting at one seam."""
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off"); ax.set_facecolor(SURFACE)

    # domain headers
    ax.add_patch(FancyBboxPatch((0.3, 8.2), 3.7, 1.1, boxstyle="round,pad=0.08",
                                fc="#eaf1fb", ec=BLUE, lw=1.5))
    ax.text(2.15, 8.75, "Agent X — Meridian", ha="center", va="center", fontsize=11.5,
            weight="bold", color="#14314f")
    ax.text(2.15, 8.4, "bespoke transport OSS", ha="center", va="center", fontsize=9, color="#555")
    ax.add_patch(FancyBboxPatch((6.0, 8.2), 3.7, 1.1, boxstyle="round,pad=0.08",
                                fc="#eafbf3", ec=AQUA, lw=1.5))
    ax.text(7.85, 8.75, "Agent Y — Cascade", ha="center", va="center", fontsize=11.5,
            weight="bold", color="#14314f")
    ax.text(7.85, 8.4, "bespoke IP/VPN controller", ha="center", va="center", fontsize=9, color="#555")

    # the five seam correspondences (aligned rows), the grade false cognate, then native gaps
    rows = [
        ("circuit", "underlay", "seam: the underlay", "corr"),
        ("hand-off", "attachment", "one demarcation", "corr"),
        ("rate", "rate", "committed payload, not line rate", "corr"),
        ("latency", "latency", "a bound: ms  ==  tier", "corr"),
        ("protection", "protection", "against a path failure", "corr"),
        ("grade", "grade", "UNRELATED: transport class  vs  IP class", "false"),
    ]
    y = 7.3
    for a, b, note, kind in rows:
        col = ORANGE if kind == "false" else AQUA
        ax.add_patch(FancyBboxPatch((0.5, y - 0.28), 3.0, 0.56, boxstyle="round,pad=0.04",
                                    fc="white", ec=BLUE, lw=1.1))
        ax.text(2.0, y, a, ha="center", va="center", fontsize=10, color="#14314f")
        ax.add_patch(FancyBboxPatch((6.5, y - 0.28), 3.0, 0.56, boxstyle="round,pad=0.04",
                                    fc="white", ec=AQUA, lw=1.1))
        ax.text(8.0, y, b, ha="center", va="center", fontsize=10, color="#14314f")
        if kind == "false":
            ax.plot([3.5, 6.5], [y, y], color=col, lw=1.6, ls=(0, (4, 3)))
            ax.text(5.0, y + 0.16, "false cognate", ha="center", va="bottom", fontsize=8,
                    color=col, weight="bold")
            ax.text(5.0, y - 0.2, "✗", ha="center", va="center", fontsize=13, color=col)
        else:
            ax.plot([3.5, 6.5], [y, y], color=col, lw=1.8)
            ax.text(5.0, y + 0.14, note, ha="center", va="bottom", fontsize=7.6, color="#555")
        if kind == "false":
            ax.text(5.0, y - 0.36, note, ha="center", va="top", fontsize=7.2, color=col)
        y -= 0.92

    # native gaps
    ax.text(2.0, 1.2, "native only:  bearer / wavelength", ha="center", fontsize=8.5, color=GREY, style="italic")
    ax.text(8.0, 1.2, "native only:  service, vlan", ha="center", fontsize=8.5, color=GREY, style="italic")

    ax.text(5.0, 0.35, "Two home-grown models, no public standard. The worlds overlap only at "
            "the seam; everything else is native to one side.", ha="center", fontsize=9.2, color="#333")
    ax.set_title("The cross-domain setting — two home-grown models meeting where a Cascade "
                 "service rides a Meridian circuit", fontsize=12, y=1.0)
    save(fig, "fig_crossdomain_seam.png")


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load(pat):
    rows = []
    for f in glob.glob(str(ROOT / "results" / pat)):
        rows += list(csv.DictReader(open(f)))
    return rows


def fig_mirror():
    """Omission vs commission: resolved fraction against precision, reference off -> on."""
    rows = [r for r in load("config_cross_domain.csv") if r["stack"].startswith("openai-agent")]
    if not rows:
        print("skip fig_crossdomain_mirror: no wave-1 data"); return
    MODELS = ["gpt-5.6-sol", "gpt-5-mini", "gpt-5-nano"]
    LAB = {"gpt-5.6-sol": "sol (strong)", "gpt-5-mini": "mini", "gpt-5-nano": "nano (weak)"}
    COL = {"gpt-5.6-sol": BLUE, "gpt-5-mini": ORANGE, "gpt-5-nano": AQUA}

    def mean(rs, k):
        xs = [fl(r[k]) for r in rs if fl(r[k]) is not None]
        return sum(xs) / len(xs) if xs else 0.0

    fig, ax = plt.subplots(figsize=(7.6, 6.0))
    for md in MODELS:
        pts = {}
        for ref in ("False", "True"):
            sel = [r for r in rows if r["model"] == md and r["uses_reference"] == ref]
            pts[ref] = (mean(sel, "recall"), mean(sel, "precision"))
        (x0, y0), (x1, y1) = pts["False"], pts["True"]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="->", color=COL[md], lw=2, alpha=0.9))
        ax.scatter([x0], [y0], s=120, facecolor="white", edgecolor=COL[md], lw=2, zorder=3)
        ax.scatter([x1], [y1], s=150, color=COL[md], zorder=3)
        ax.text(x1 + 0.012, y1, LAB[md], fontsize=9.5, color=COL[md], va="center")
    ax.scatter([], [], s=120, facecolor="white", edgecolor="#555", lw=2, label="no reference")
    ax.scatter([], [], s=150, color="#555", label="constructed reference")
    ax.set_xlabel("resolved fraction  (how much the binding pass commits)")
    ax.set_ylabel("precision  (how much of it is right)")
    ax.set_xlim(0.35, 1.06); ax.set_ylim(0.45, 1.06)
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.set_title("Mirror-image shortfalls, one cure. Without the constructed reference the "
                 "strong\nagent under-commits (omission, top-left) and the weak one mis-commits\n"
                 "(commission, lower-right); the reference pulls both to the corner.", fontsize=10.5)
    _clean(ax) if False else None
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "fig_crossdomain_mirror.png")


if __name__ == "__main__":
    fig_seam()
    fig_mirror()
