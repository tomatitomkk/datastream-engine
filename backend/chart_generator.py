"""
chart_generator.py — Generates publication-ready charts with Matplotlib/Seaborn.

Produces two charts:
  1. Bar chart: records per source
  2. Line chart: performance over time (30-day window)
Saves to temp/ for PDF injection.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime

sns.set_theme(style="darkgrid")

DARK_BG = "#0d0d1a"
CARD_BG = "#111122"
ACCENT_CYAN = "#00f0ff"
ACCENT_GREEN = "#00ff41"
ACCENT_PURPLE = "#7c3aed"
TEXT_COLOR = "#c8c8e0"
GRID_COLOR = "#1a1a3a"


def _style_ax(ax):
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for label in ax.get_xticklabels():
        label.set_fontfamily("monospace")
        label.set_fontsize(7)
    for label in ax.get_yticklabels():
        label.set_fontfamily("monospace")
        label.set_fontsize(7)


def generate_bar_chart(source_summary: list[dict], output_path: Path) -> Path:
    try:
        fig, ax = plt.subplots(figsize=(7, 3.5))
        fig.patch.set_facecolor(DARK_BG)

        names = [s["source"].split()[-1] if len(s["source"].split()) > 1 else s["source"] for s in source_summary]
        records = [s["records"] for s in source_summary]
        err_rate = [s["error_rate"] for s in source_summary]

        bars = ax.barh(names, records, color=ACCENT_CYAN, edgecolor="none", height=0.55, alpha=0.85)
        for i, (bar, err) in enumerate(zip(bars, err_rate)):
            ax.text(bar.get_width() + 8, bar.get_y() + bar.get_height() / 2,
                    f"{int(bar.get_width()):,}  |  err {err:.1f}%",
                    va="center", fontsize=7, fontfamily="monospace", color=TEXT_COLOR)

        ax.set_xlabel("Registros procesados", color=TEXT_COLOR, fontsize=8)
        ax.set_title("Registros por Fuente de Datos", color=ACCENT_CYAN, fontsize=11, fontweight="bold", pad=12)
        _style_ax(ax)
        ax.invert_yaxis()

        plt.tight_layout()
        fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Error generating bar chart: {e}") from e


def generate_line_chart(time_series: list[dict], output_path: Path) -> Path:
    try:
        fig, ax = plt.subplots(figsize=(7, 3.5))
        fig.patch.set_facecolor(DARK_BG)

        dates = [s["date"] for s in time_series]
        values = [s["records_processed"] for s in time_series]
        times = [s["avg_processing_ms"] for s in time_series]

        color2 = ACCENT_GREEN
        ax.fill_between(range(len(values)), values, alpha=0.08, color=ACCENT_CYAN)
        ax.plot(values, color=ACCENT_CYAN, linewidth=1.8, marker="o", markersize=3,
                markerfacecolor=ACCENT_CYAN, markeredgecolor="none")

        ax.set_ylabel("Registros procesados", color=TEXT_COLOR, fontsize=8)
        ax.set_title("Rendimiento del Pipeline (30 días)", color=ACCENT_CYAN, fontsize=11, fontweight="bold", pad=12)
        _style_ax(ax)

        tick_step = max(1, len(dates) // 6)
        ax.set_xticks(range(0, len(dates), tick_step))
        ax.set_xticklabels([dates[i].strftime("%d/%m") for i in range(0, len(dates), tick_step)],
                           rotation=30, ha="right")

        ax2 = ax.twinx()
        ax2.plot(times, color=color2, linewidth=1.2, linestyle="--", alpha=0.7)
        ax2.set_ylabel("Tiempo medio (ms)", color=color2, fontsize=8)
        ax2.tick_params(colors=color2, labelsize=7)
        ax2.spines["right"].set_color(GRID_COLOR)
        ax2.spines["top"].set_visible(False)

        plt.tight_layout()
        fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Error generating line chart: {e}") from e
