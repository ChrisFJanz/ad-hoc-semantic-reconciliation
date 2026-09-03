#!/usr/bin/env python3
"""Schematic figures for the master report. All are data-independent concept drawings.
Fig A  the lift            — a bare data model becomes a portable, self-describing semantic model
Fig B  reconciliation      — two lifted models: correspondences, a rejected cognate, the residual,
                             and the thin reference as a flat identity bridge
Fig C  cross-domain        — Meridian <-> Cascade at one seam; a thin descriptive toehold unlocks it
Fig D  observability       — the overloaded legacy alarm lifted and decomposed against the NMOP ladder
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GREY, SURFACE = "#9a958d", "#fbfaf8"
INK = "#14314f"


def save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / name, dpi=160, facecolor=SURFACE, bbox_inches="tight")
    print("wrote", (FIG / name).name)


def box(ax, x, y, w, h, fc, ec, lw=1.4, pad=0.08, r=0.06):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad={pad},rounding_size={r}",
                                fc=fc, ec=ec, lw=lw))


def chip(ax, cx, cy, w, h, text, fc, ec, fs=8.6, weight="normal", tc=INK):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.05", fc=fc, ec=ec, lw=1.2))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, weight=weight, color=tc)


# --- Figure A: the lift -----------------------------------------------------------------------
def fig_lift():
    fig, ax = plt.subplots(figsize=(11.6, 5.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9); ax.axis("off"); ax.set_facecolor(SURFACE)

    # LEFT: bare data model
    box(ax, 0.4, 2.6, 3.0, 4.0, "#f3f1ee", GREY, lw=1.5)
    ax.text(1.9, 6.15, "data model", ha="center", fontsize=11, weight="bold", color=INK)
    ax.text(1.9, 5.7, "(schema + records)", ha="center", fontsize=8.4, color="#666", style="italic")
    rows = ["term:  och_grade", "rec:  {id: 0x7a, v: 3}",
            "rec:  {id: 0x7b, v: 1}", "— meaning only to", "   whoever wrote it"]
    for j, t in enumerate(rows):
        col = "#555" if j < 3 else "#8a8681"
        st = "normal" if j < 3 else "italic"
        ax.text(0.75, 5.25 - j * 0.5, t, ha="left", fontsize=8.1, color=col, style=st,
                family="monospace" if j < 3 else "sans-serif")

    # THE LIFT arrow
    ax.add_patch(FancyArrowPatch((3.65, 4.5), (5.0, 4.5), arrowstyle="-|>",
                                 mutation_scale=22, color=INK, lw=2.4))
    ax.text(4.32, 5.25, "the lift", ha="center", fontsize=10.5, weight="bold", color=INK)
    ax.text(4.32, 3.75, "(cognition above\ngrounds it)", ha="center", fontsize=7.6, color="#777")

    # RIGHT: lifted semantic model — central concept + component families
    cx, cy = 8.7, 4.5
    box(ax, 5.25, 1.15, 6.5, 6.9, "#ffffff", BLUE, lw=1.6)
    ax.text(8.5, 7.6, "ad hoc semantic model", ha="center", fontsize=11, weight="bold", color=INK)
    chip(ax, cx, cy, 1.7, 0.7, "concept", "#eaf1fb", BLUE, fs=9.5, weight="bold")

    comps = [
        (6.55, 6.55, "lexicon\nlabel + synonyms", AQUA, "#eafbf3"),
        (10.45, 6.55, "ontology\nkind + relations", BLUE, "#eaf1fb"),
        (6.4, 4.5, "definition\n+ worked example", BLUE, "#eaf1fb"),
        (10.5, 4.5, "instances\n(as evidence)", AQUA, "#eafbf3"),
        (8.5, 2.15, "reference binding  (optional identity anchor)", ORANGE, "#fdf1ea"),
    ]
    for (x, y, t, ec, fc) in comps[:4]:
        chip(ax, x, y, 1.95, 0.9, t, fc, ec, fs=8.1)
        ax.add_patch(FancyArrowPatch((cx, cy), (x, y), arrowstyle="-", color="#c7d3e2",
                                     lw=1.1, connectionstyle="arc3,rad=0.0"))
    x, y, t, ec, fc = comps[4]
    chip(ax, x, y, 5.6, 0.62, t, fc, ec, fs=8.1)
    ax.add_patch(FancyArrowPatch((cx, cy - 0.35), (x, y + 0.31), arrowstyle="-", color="#e6cbb9", lw=1.1))

    ax.text(6.0, 0.5, "self-describing  →  portable: any cognitive consumer can pick it up, "
            "with no pre-agreed standard", ha="center", fontsize=9.2, color=ORANGE, weight="bold")
    ax.set_title("The lift — a data model, meaningful only to its author, becomes an ad hoc semantic "
                 "model that carries its own meaning", fontsize=11, y=1.02)
    save(fig, "fig_master_lift.png")


# --- Figure B: reconciliation over lifted models ----------------------------------------------
def fig_reconcile():
    fig, ax = plt.subplots(figsize=(11.8, 6.8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9.6); ax.axis("off"); ax.set_facecolor(SURFACE)

    lx, rx = 2.0, 10.0
    corr = [("service", "tunnel"), ("demarcation", "termination"),
            ("committed-rate", "committed-rate")]
    cys = [7.9, 6.85, 5.8]

    ax.text(lx, 8.9, "lifted model A", ha="center", fontsize=10.5, weight="bold", color=INK)
    ax.text(rx, 8.9, "lifted model B", ha="center", fontsize=10.5, weight="bold", color=INK)

    # thin reference bridge (spans the correspondence rows); title above the box
    box(ax, 5.2, 5.35, 1.6, 3.15, "#fdf1ea", ORANGE, lw=1.5)
    ax.text(6.0, 8.62, "thin reference", ha="center", fontsize=9.2, weight="bold", color=ORANGE)
    ax.text(6.0, 8.28, "(flat identity bridge)", ha="center", fontsize=7.4, color=ORANGE, style="italic")

    for (a, b), y in zip(corr, cys):
        chip(ax, lx, y, 2.5, 0.72, a, "#eaf1fb", BLUE, fs=8.6)
        chip(ax, rx, y, 2.5, 0.72, b, "#eaf1fb", BLUE, fs=8.6)
        ax.add_patch(FancyBboxPatch((5.5, y - 0.15), 1.0, 0.3, boxstyle="round,pad=0.01",
                                    fc="white", ec=ORANGE, lw=0.9))
        ax.add_patch(FancyArrowPatch((lx + 1.3, y), (5.48, y), arrowstyle="-", color=AQUA, lw=1.9))
        ax.add_patch(FancyArrowPatch((6.52, y), (rx - 1.3, y), arrowstyle="-", color=AQUA, lw=1.9))
    ax.text(6.0, 4.95, "resolved correspondences — drawn on grounded evidence, "
            "bound through the reference", ha="center", fontsize=8.3, color="#1b8f63", weight="bold")

    # rejected false cognate — clear below the reference box
    yR = 3.85
    chip(ax, lx, yR, 2.5, 0.72, "grade\n(protection class)", "#fdf1ea", ORANGE, fs=7.8)
    chip(ax, rx, yR, 2.5, 0.72, "grade\n(class of service)", "#fdf1ea", ORANGE, fs=7.8)
    ax.add_patch(FancyArrowPatch((lx + 1.3, yR), (rx - 1.3, yR), arrowstyle="-", color=ORANGE,
                                 lw=1.6, linestyle=(0, (4, 3))))
    ax.text(6.0, yR + 0.02, "✗", ha="center", va="center", fontsize=15, color=ORANGE, weight="bold")
    ax.text(6.0, yR - 0.62, "false cognate rejected — same surface word, different kind",
            ha="center", fontsize=8.0, color=ORANGE, weight="bold")

    # natives with no counterpart -> residual bucket
    yN = 2.4
    chip(ax, lx, yN, 2.5, 0.6, "vlan  (native)", "#f0eeeb", GREY, fs=7.8, tc="#5a564f")
    chip(ax, rx, yN, 2.5, 0.6, "wavelength  (native)", "#f0eeeb", GREY, fs=7.8, tc="#5a564f")
    box(ax, 4.5, 0.45, 3.0, 1.0, "#f0eeeb", GREY, lw=1.3)
    ax.text(6.0, 0.95, "residual", ha="center", fontsize=9.0, weight="bold", color="#5a564f")
    ax.text(6.0, 0.62, "referred onward", ha="center", fontsize=7.6, color="#6a655e", style="italic")
    for sx in (lx + 1.3, rx - 1.3):
        ax.add_patch(FancyArrowPatch((sx, yN - 0.1), (6.0, 1.5), arrowstyle="-|>", mutation_scale=10,
                                     color=GREY, lw=1.1, connectionstyle="arc3,rad=0.0"))
    ax.text(6.0, 1.95, "native gaps · opaque items · what evidence cannot yet confirm",
            ha="center", fontsize=7.4, color="#8a857d", style="italic")

    ax.set_title("Reconciliation over two lifted models — grounded correspondences bound through a "
                 "thin reference, a rejected cognate, and the residual referred onward",
                 fontsize=10.6, y=1.02)
    save(fig, "fig_master_reconcile.png")


# --- Figure C: cross-domain, instantiated -----------------------------------------------------
def fig_crossdomain():
    fig, ax = plt.subplots(figsize=(11.6, 5.9))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9); ax.axis("off"); ax.set_facecolor(SURFACE)

    ax.text(2.0, 8.4, "Meridian — transport OSS", ha="center", fontsize=10.2, weight="bold", color=INK)
    ax.text(10.0, 8.4, "Cascade — IP / VPN", ha="center", fontsize=10.2, weight="bold", color=INK)
    ax.text(6.0, 8.62, "(both home-grown; no public standard beneath either)", ha="center",
            fontsize=8.3, color="#777", style="italic")

    pairs = [   # (meridian, cascade, kind)
        ("circuit", "underlay", "bind"),
        ("hand-off", "attachment", "bind"),
        ("rate  (committed payload)", "rate  (committed payload)", "pin"),
        ("latency  (bound)", "latency  (bound)", "pin"),
        ("protection  (path failure)", "protection  (path failure)", "pin"),
        ("grade  (protection class)", "grade  (class of service)", "reject"),
    ]
    ys = [7.4, 6.35, 5.3, 4.25, 3.2, 1.95]
    lx, rx = 2.0, 10.0
    for (ml, cl, kind), y in zip(pairs, ys):
        ec = ORANGE if kind == "reject" else BLUE
        fc = "#fdf1ea" if kind == "reject" else "#eaf1fb"
        chip(ax, lx, y, 2.9, 0.72, ml, fc, ec, fs=7.7)
        chip(ax, rx, y, 2.9, 0.72, cl, fc, ec, fs=7.7)
        if kind == "reject":
            ax.add_patch(FancyArrowPatch((lx + 1.5, y), (rx - 1.5, y), arrowstyle="-", color=ORANGE,
                                         lw=1.5, linestyle=(0, (4, 3))))
            ax.text(6.0, y + 0.02, "✗", ha="center", va="center", fontsize=13, color=ORANGE, weight="bold")
        else:
            ax.add_patch(FancyArrowPatch((lx + 1.5, y), (rx - 1.5, y), arrowstyle="-", color=AQUA, lw=1.8))
            tag = "same object,\ntwo names" if kind == "bind" else "one meaning,\npinned"
            ax.text(6.0, y + 0.34, tag, ha="center", va="center", fontsize=6.7, color="#6a6a6a")

    ax.text(6.0, 0.95, "constructed reference: a single descriptive field (label · class · "
            "definition · example) unlocks the strong agent — a bare shared pointer does not",
            ha="center", fontsize=8.4, color=ORANGE, weight="bold")
    ax.text(6.0, 0.45, "the seam — five bindings to make, one look-alike ('grade') to reject",
            ha="center", fontsize=8.2, color="#5a564f", style="italic")
    ax.set_title("Cross-domain, instantiated — one order across the Meridian/Cascade seam, "
                 "with no standard to appeal to", fontsize=10.8, y=1.02)
    save(fig, "fig_master_crossdomain.png")


# --- Figure D: observability, instantiated ----------------------------------------------------
def fig_observability():
    fig, ax = plt.subplots(figsize=(11.6, 6.1))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9.4); ax.axis("off"); ax.set_facecolor(SURFACE)

    # legacy overloaded alarm
    box(ax, 0.4, 3.3, 3.0, 3.0, "#fdf1ea", ORANGE, lw=1.6)
    ax.text(1.9, 6.0, "legacy  ALARM", ha="center", fontsize=10.2, weight="bold", color=INK)
    ax.text(1.9, 5.55, "one object, bundling:", ha="center", fontsize=8.2, color="#555", style="italic")
    for j, t in enumerate(["· event", "· undesirable state", "· fixed severity", "· probable-cause"]):
        ax.text(1.15, 5.1 - j * 0.42, t, ha="left", fontsize=8.3, color="#555")

    # lift + decompose arrow
    ax.add_patch(FancyArrowPatch((3.55, 4.8), (4.9, 4.8), arrowstyle="-|>", mutation_scale=20,
                                 color=INK, lw=2.2))
    ax.text(4.2, 5.35, "lift +\ndecompose", ha="center", fontsize=7.8, color="#777")

    # NMOP ladder rungs (targets)
    rungs = [
        ("alarm  (a State)", AQUA, "#eafbf3", "correct core"),
        ("fault", AQUA, "#eafbf3", "+ decomposition"),
        ("anomaly  (a deviation)", ORANGE, "#fdf1ea", "TRAP: not a state"),
        ("symptom · problem · cause · incident", BLUE, "white", ""),
    ]
    x0 = 5.15
    ys = [6.55, 5.5, 4.45, 3.3]
    for (t, ec, fc, note), y in zip(rungs, ys):
        w = 4.2 if "symptom" not in t else 5.7
        chip(ax, x0 + w / 2, y, w, 0.72, t, fc, ec, fs=8.4,
             weight="bold" if ec in (AQUA, ORANGE) else "normal")
        if note:
            ax.text(x0 + w + 0.35, y, note, ha="left", va="center", fontsize=7.6,
                    color=ec if ec != AQUA else "#1b8f63", weight="bold" if "TRAP" in note else "normal")
    # decomposition braces from alarm box to the two aqua rungs
    for y in ys[:2]:
        ax.add_patch(FancyArrowPatch((4.95, 4.8), (x0 + 0.1, y), arrowstyle="-|>", mutation_scale=12,
                                     color=AQUA, lw=1.5, connectionstyle="arc3,rad=0.12"))
    # trap line to anomaly (rejected)
    ax.add_patch(FancyArrowPatch((4.95, 4.6), (x0 + 0.1, ys[2]), arrowstyle="-|>", mutation_scale=12,
                                 color=ORANGE, lw=1.4, linestyle=(0, (3, 2)), connectionstyle="arc3,rad=0.05"))

    ax.text(7.3, 7.5, "NMOP  (RFC 9940 ladder)", ha="left", fontsize=9.6, weight="bold", color=INK)

    # anomaly-semantics annotations chip (the lifted content)
    box(ax, 4.9, 0.55, 6.7, 1.7, "#eaf1fb", BLUE, lw=1.4)
    ax.text(8.25, 1.9, "anomaly-semantics annotations  —  the lifted content the verdict runs on",
            ha="center", fontsize=8.2, weight="bold", color=INK)
    ann = "concern · confidence · plane · pattern · lifecycle · season   →   act / watch / suppress"
    ax.text(8.25, 1.15, ann, ha="center", fontsize=8.0, color="#33506e")
    ax.add_patch(FancyArrowPatch((7.2, 3.0), (8.25, 2.3), arrowstyle="-", color="#c7d3e2", lw=1.1))

    ax.text(1.9, 2.4, "an alarm is\nnot an anomaly", ha="center", fontsize=8.6, color=ORANGE,
            weight="bold")
    ax.set_title("Observability, instantiated — the overloaded legacy alarm lifted and decomposed "
                 "one-to-many into the NMOP ladder; the deep cognate is alarm ≠ anomaly",
                 fontsize=10.6, y=1.02)
    save(fig, "fig_master_observability.png")


if __name__ == "__main__":
    fig_lift()
    fig_reconcile()
    fig_crossdomain()
    fig_observability()
