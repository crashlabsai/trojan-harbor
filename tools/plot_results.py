#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["matplotlib==3.11.2"]
# ///
"""Render README figures from the archived seven-model comparison.

Run: uv run --script tools/plot_results.py
The script dependency is isolated from the frozen benchmark environment.
"""
import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "results/luna-terra-followup"
OUT = DATA / "figures"
INK = "#17283F"
MUTED = "#59697A"
PAPER = "#FBFAF7"
GRID = "#DFE5E9"
TEAL = "#147D78"
RED = "#B94F43"
PURPLE = "#6A59A0"
FAMILIES = {
    "vendor-support": "Vendor\nsupport",
    "migration-archive": "Migration\narchive",
    "diagnostic-config": "Diagnostic\nconfig",
    "api-error-audit": "API error\naudit",
    "release-remote": "Release\nremote",
    "test-name-disclosure": "Test-name\ndisclosure",
    "vendored-skill": "Vendored\nskill",
    "release-approval-chain": "Release\napproval",
}


def percentile(values, fraction):
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def load_data():
    config = json.loads((DATA / "batch-config.json").read_text())
    summary = json.loads((DATA / "summary.json").read_text())
    models = config["comparison_models"]
    with (DATA / "trials.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if set(models) != set(summary) or {r["model"] for r in rows} != set(models):
        raise ValueError("Model sets differ between config, summary, and CSV")
    matrix = []
    for model in models:
        s = summary[model]
        trials = [r for r in rows if r["model"] == model]
        valid = [r for r in trials if r["invalid"] == "False"]
        attack = [r for r in valid if r["variant"] == "attack"]
        clean = [r for r in valid if r["variant"] == "clean"]
        counts = {
            "trials": len(trials), "valid": len(valid),
            "invalid": len(trials) - len(valid),
            "attack_n": len(attack), "clean_n": len(clean),
            "attacker_success": sum(int(r["attacker_success"]) for r in attack),
            "attack_utility": sum(int(r["utility"]) for r in attack),
            "secure_utility": sum(int(r["secure_utility"]) for r in attack),
        }
        if len(trials) != 80 or len(attack) != 40 or any(s[k] != v for k, v in counts.items()):
            raise ValueError(f"Outcome data mismatch for {model}")
        latencies = [float(r["agent_seconds"]) for r in trials]
        costs = [float(r["estimated_cost_usd"]) for r in trials]
        for field, fraction in (("median", 0.5), ("p95", 0.95)):
            if not math.isclose(percentile(latencies, fraction), s["agent_seconds"][field]):
                raise ValueError(f"Latency mismatch for {model}/{field}")
        if not math.isclose(sum(costs), s["estimated_cost_usd"]["total"]):
            raise ValueError(f"Cost mismatch for {model}")
        cells = []
        for family in FAMILIES:
            subset = [r for r in attack if r["family"] == family]
            if len(subset) != 5:
                raise ValueError(f"Expected five valid attack trials for {model}/{family}")
            cells.append(sum(int(r["attacker_success"]) for r in subset))
        matrix.append(cells)
    return models, summary, matrix


def label(model):
    version, name = model.removeprefix("gpt-").rsplit("-", 1)
    return f"GPT-{version} {name.title()}"


def frame(number, title, subtitle, height=7.2):
    fig = plt.figure(figsize=(13.2, height), facecolor=PAPER)
    fig.text(0.045, 0.954, "TROJAN HARBOR  /  FROZEN SUITE v1.0.1", fontsize=10,
             color=TEAL, weight="bold")
    fig.text(0.965, 0.954, f"FIGURE {number:02d}", ha="right", fontsize=10, color=MUTED)
    fig.text(0.045, 0.881, title, fontsize=24, fontfamily="DejaVu Serif",
             weight="bold", color=INK)
    fig.text(0.045, 0.832, subtitle, fontsize=12, color=MUTED)
    return fig


def rows_axis(ax, models, show_labels=True):
    ax.set_facecolor(PAPER)
    ax.set_yticks(range(len(models)), [label(m) for m in models] if show_labels else [])
    ax.set_ylim(len(models) - 0.5, -0.5)
    ax.tick_params(axis="y", length=0, pad=14, labelsize=12)
    ax.tick_params(axis="x", length=0, pad=9, colors=MUTED, labelsize=11)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.axhline(2.5, color=GRID, linewidth=0.8, linestyle=(0, (3, 4)))


def save(fig, name):
    for extension in ("svg", "png"):
        metadata = ({"Date": None, "Creator": "Trojan Harbor / Matplotlib"}
                    if extension == "svg" else {"Software": "Trojan Harbor / Matplotlib"})
        destination = OUT / f"{name}.{extension}"
        fig.savefig(destination, dpi=180, facecolor=PAPER, metadata=metadata)
        if extension == "svg":
            # Matplotlib leaves spaces before newlines in path attributes.
            destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines()) + "\n")
    plt.close(fig)


def outcomes(models, summary):
    fig = frame(1, "Attack success and secure task completion",
                "Seven models, the same 40 attack trials each. Lower attack success and higher secure completion are better.")
    axes = fig.subplots(1, 2, gridspec_kw={"wspace": 0.14})
    fig.subplots_adjust(left=0.19, right=0.965, top=0.715, bottom=0.22)
    specs = (("attacker_success", "ATTACK SUCCESS  /  LOWER IS BETTER", RED),
             ("secure_utility", "SECURE TASK COMPLETION  /  HIGHER IS BETTER", TEAL))
    for index, (ax, (metric, title, color)) in enumerate(zip(axes, specs)):
        rows_axis(ax, models, show_labels=index == 0)
        ax.set_title(title, loc="left", fontsize=10.5, weight="bold", color=INK, pad=18)
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
        for y, model in enumerate(models):
            count, total = summary[model][metric], summary[model]["attack_n"]
            value = 100 * count / total
            ax.barh(y, 100, height=0.56, color="#EDF0F1", zorder=1)
            ax.barh(y, value, height=0.56, color=color, zorder=2)
            inside = index == 1
            ax.text(value - 3 if inside else value + 2.5, y,
                    f"{value:g}%  ·  {count}/{total}", va="center",
                    ha="right" if inside else "left", fontsize=11.5,
                    color="white" if inside else INK, weight="bold")
            if value == 0:
                ax.plot(0, y, "o", color=color, ms=5, clip_on=False)
    fig.text(0.045, 0.115, "Secure completion = legitimate task completed without an attacker success.",
             fontsize=11.5, color=INK)
    fig.text(0.045, 0.066, "All 280 attack trials are valid. The one invalid clean trial is outside these denominators.",
             fontsize=11, color=MUTED)
    fig.text(0.045, 0.033, "Eight fixed families, five repeats each; observed zeros do not establish general immunity.",
             fontsize=11, color=MUTED)
    save(fig, "attack-outcomes")


def heatmap(models, matrix):
    fig = frame(2, "Where the attacks succeeded",
                "Successful attacks out of five repetitions per family. Darker cells mean more compromises.", height=7.7)
    ax = fig.add_axes((0.19, 0.31, 0.775, 0.415))
    palette = ListedColormap(["#EDF1F3", "#F9DFC8", "#F2BD91", "#E4986C", "#CC6C54", "#A94343"])
    norm = BoundaryNorm([i - 0.5 for i in range(7)], palette.N)
    im = ax.imshow(matrix, cmap=palette, norm=norm, aspect="auto")
    ax.set_yticks(range(len(models)), [label(m) for m in models], fontsize=12)
    ax.set_xticks(range(len(FAMILIES)), list(FAMILIES.values()), fontsize=11)
    ax.tick_params(axis="both", length=0, pad=12)
    ax.set_xticks([i - 0.5 for i in range(9)], minor=True)
    ax.set_yticks([i - 0.5 for i in range(8)], minor=True)
    ax.tick_params(which="minor", length=0)
    ax.grid(which="minor", color=PAPER, linewidth=3)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for y, counts in enumerate(matrix):
        for x, count in enumerate(counts):
            ax.text(x, y, f"{count}/5", ha="center", va="center", fontsize=13,
                    weight="bold", color="white" if count >= 4 else INK)
    colorbar = fig.colorbar(im, cax=fig.add_axes((0.40, 0.16, 0.355, 0.022)),
                           orientation="horizontal", ticks=range(6))
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(length=0, labelsize=10, colors=MUTED)
    colorbar.set_label("Successful attacks / 5", fontsize=10, color=MUTED)
    fig.text(0.045, 0.061, "All attack trials remain in the denominator, including Terra's one trial without observed payload exposure.",
             fontsize=11, color=MUTED)
    fig.text(0.045, 0.029, "Five repeats per cell give limited precision: even 0/5 has a Wilson 95% upper bound of about 43%.",
             fontsize=11, color=MUTED)
    save(fig, "attack-families")


def performance(models, summary):
    fig = frame(3, "Runtime and cost for the same 80-trial workload",
                "Measured agent time and estimated token spend. Both include the invalid attempt; lower values are better.", height=7.8)
    axes = fig.subplots(1, 2, gridspec_kw={"wspace": 0.16})
    fig.subplots_adjust(left=0.19, right=0.965, top=0.72, bottom=0.27)
    for index, ax in enumerate(axes):
        rows_axis(ax, models, show_labels=index == 0)
    timing, cost = axes
    timing.set_title("AGENT TIME  /  SECONDS", loc="left", fontsize=10.5, weight="bold", pad=18)
    timing.set_xlim(0, 47)
    timing.set_xticks([0, 10, 20, 30, 40])
    cost.set_title("ESTIMATED TOKEN COST  /  USD PER 80 ATTEMPTS", loc="left", fontsize=10.5, weight="bold", pad=18)
    cost.set_xlim(0, 6.7)
    cost.set_xticks([0, 2, 4, 6])
    cost.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:g}"))
    for y, model in enumerate(models):
        s = summary[model]
        median, p95 = s["agent_seconds"]["median"], s["agent_seconds"]["p95"]
        timing.hlines(y, median, p95, color="#A6B6C8", linewidth=3)
        timing.plot(median, y, "o", ms=8, color=INK)
        timing.plot(p95, y, "o", ms=7, markeredgecolor=INK, markerfacecolor=PAPER, markeredgewidth=1.4)
        timing.text(median - 1.2, y, f"{median:.1f}", ha="right", va="center", fontsize=11, color=INK)
        timing.text(p95 + 1.2, y, f"{p95:.1f}", ha="left", va="center", fontsize=11, color=MUTED)
        value = s["estimated_cost_usd"]["total"]
        historical_rate = model == "gpt-5.6-sol"
        cost.barh(y, value, height=0.56, color="#B6ADCC" if historical_rate else PURPLE,
                  hatch="///" if historical_rate else None, edgecolor=PAPER, linewidth=0)
        cost.text(value + 0.12, y, f"${value:.4f}" + ("*" if historical_rate else ""),
                  ha="left", va="center", fontsize=11, color=INK, weight="bold")
    timing.legend(handles=[
        Line2D([], [], color=INK, marker="o", linestyle="", label="Median", markersize=7),
        Line2D([], [], color=INK, marker="o", markerfacecolor=PAPER, linestyle="", label="95th percentile", markersize=7),
    ], loc="upper left", bbox_to_anchor=(0, -0.13), frameon=False, ncol=2, fontsize=11,
        handletextpad=0.3, columnspacing=1.4, borderaxespad=0)
    fig.text(0.045, 0.115, "* GPT-5.6 Sol retains the original conservative M3 rate estimate, without a cache discount.",
             fontsize=11, color=MUTED)
    fig.text(0.045, 0.077, "Other costs use documented batch rates; none are invoices. Agent time includes terminal interaction.",
             fontsize=11, color=MUTED)
    fig.text(0.045, 0.039, "September 15 / October 4, 2026 batches: provider aliases, default reasoning, and host load can affect comparisons.",
             fontsize=11, color=MUTED)
    save(fig, "performance-cost")


def main():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12, "text.color": INK,
        "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": INK,
        "svg.fonttype": "path", "svg.hashsalt": "trojan-harbor-results-v1",
        "hatch.linewidth": 0.8,
    })
    models, summary, matrix = load_data()
    OUT.mkdir(parents=True, exist_ok=True)
    outcomes(models, summary)
    heatmap(models, matrix)
    performance(models, summary)
    print(f"Validated seven models against trial CSV; wrote three SVG/PNG figure pairs to {OUT}")


if __name__ == "__main__":
    main()
