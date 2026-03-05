#!/usr/bin/env python3
"""
Generate a cool multi-panel figure from the LLM survey data.
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_PATH = PROJECT_ROOT / "data" / "data.csv"
OUTPUT_PATH = PROJECT_ROOT / "output"

# Column indices
COL_GRADE = 3
COL_SCHOOL = 22
COL_PERSONAL = 23
COL_FORCE_BEGIN = 10
COL_FORCE_END = 27
COL_UNDERSTAND_POLICIES = 18
COL_PROFS_UNDERSTAND = 19
COL_LLM_USES = 9


def load_data():
    """Load survey data."""
    rows = []
    with open(DATA_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        raw_rows = list(reader)
    for row in raw_rows[1:]:
        if len(row) >= 2 and "Yes" in str(row[1]):
            rows.append(row)
    return rows


def safe_int(val, default=None):
    if val is None or val == "":
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def create_figure():
    rows = load_data()
    n = len(rows)

    COLORS = {
        "navy": "#0C2340",
        "gold": "#C99700",
        "light_gold": "#E8C547",
        "slate": "#4A5F7F",
        "cream": "#F5F0E6",
        "coral": "#C45C4A",
        "teal": "#3D7B80",
    }

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 5))
    fig.patch.set_facecolor(COLORS["navy"])
    fig.suptitle(
        "LLMs at Notre Dame & St. Mary's",
        fontsize=18,
        fontweight="bold",
        color=COLORS["cream"],
        y=1.02,
    )

    # --- Panel 1: Yes/No School vs Personal ---
    school_yes = sum(1 for r in rows if len(r) > COL_SCHOOL and "Yes" in str(r[COL_SCHOOL]))
    school_no = n - school_yes
    personal_yes = sum(1 for r in rows if len(r) > COL_PERSONAL and "Yes" in str(r[COL_PERSONAL]))
    personal_no = n - personal_yes

    x = np.arange(2)
    width = 0.35

    bars1 = ax1.bar(x - width / 2, [school_yes, personal_yes], width, label="Yes", color=COLORS["coral"], edgecolor=COLORS["light_gold"], linewidth=1.2)
    bars2 = ax1.bar(x + width / 2, [school_no, personal_no], width, label="No", color=COLORS["teal"], edgecolor=COLORS["light_gold"], linewidth=1.2)

    ax1.set_ylabel("Count", color=COLORS["cream"])
    ax1.set_title("Used LLMs when you shouldn't have", color=COLORS["gold"], fontsize=13)
    ax1.set_xticks(x)
    ax1.set_xticklabels(["School", "Personal"], color=COLORS["cream"])
    ax1.legend(loc="upper right", facecolor=COLORS["navy"], edgecolor=COLORS["slate"], labelcolor=COLORS["cream"])
    ax1.set_facecolor(COLORS["navy"])
    ax1.spines[:].set_color(COLORS["slate"])
    ax1.tick_params(colors=COLORS["cream"])
    ax1.bar_label(bars1, color=COLORS["cream"], fontsize=11)
    ax1.bar_label(bars2, color=COLORS["cream"], fontsize=11)

    # --- Panel 2: Force for good — Beginning vs End (overlaid) ---
    begin_scores = []
    end_scores = []
    for r in rows:
        b = safe_int(r[COL_FORCE_BEGIN]) if len(r) > COL_FORCE_BEGIN else None
        e = safe_int(r[COL_FORCE_END]) if len(r) > COL_FORCE_END else None
        if b and 1 <= b <= 5:
            begin_scores.append(b)
        if e and 1 <= e <= 5:
            end_scores.append(e)

    bins = np.arange(0.5, 6.5, 1)
    hist_begin, _ = np.histogram(begin_scores, bins=bins)
    hist_end, _ = np.histogram(end_scores, bins=bins)

    x_pos = np.arange(1, 6)
    bar_width = 0.35

    bars_begin = ax2.bar(x_pos - bar_width / 2, hist_begin, bar_width, label="Beginning of survey", color=COLORS["gold"], edgecolor=COLORS["light_gold"], linewidth=1.2)
    bars_end = ax2.bar(x_pos + bar_width / 2, hist_end, bar_width, label="End of survey", color=COLORS["teal"], edgecolor=COLORS["light_gold"], linewidth=1.2, alpha=0.9)

    ax2.set_xlabel("Rating (1 = not at all, 5 = very much)", color=COLORS["cream"])
    ax2.set_ylabel("Count", color=COLORS["cream"])
    ax2.set_title("'Are LLMs a force for good?' — Before vs After", color=COLORS["gold"], fontsize=13)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(["1", "2", "3", "4", "5"], color=COLORS["cream"])
    ax2.legend(loc="upper right", facecolor=COLORS["navy"], edgecolor=COLORS["slate"], labelcolor=COLORS["cream"])
    ax2.set_facecolor(COLORS["navy"])
    ax2.spines[:].set_color(COLORS["slate"])
    ax2.tick_params(colors=COLORS["cream"])

    # --- Panel 3: Understanding gap — Students vs Professors ---
    understand_policies = []
    profs_understand = []
    for r in rows:
        if len(r) > COL_PROFS_UNDERSTAND:
            up = safe_int(r[COL_UNDERSTAND_POLICIES])
            pu = safe_int(r[COL_PROFS_UNDERSTAND])
            if up and pu and 1 <= up <= 5 and 1 <= pu <= 5:
                understand_policies.append(up)
                profs_understand.append(pu)
    avg_students = sum(understand_policies) / len(understand_policies) if understand_policies else 0
    avg_profs = sum(profs_understand) / len(profs_understand) if profs_understand else 0

    bars3a = ax3.bar(0, avg_students, 0.5, label="Students understand prof policies", color=COLORS["gold"], edgecolor=COLORS["light_gold"], linewidth=1.2)
    bars3b = ax3.bar(1, avg_profs, 0.5, label="Profs understand student use", color=COLORS["teal"], edgecolor=COLORS["light_gold"], linewidth=1.2)

    ax3.set_ylabel("Mean rating (1-5)", color=COLORS["cream"])
    ax3.set_title("Understanding gap: Who knows what?", color=COLORS["gold"], fontsize=13)
    ax3.set_xticks([0, 1])
    ax3.set_xticklabels(["Students\nunderstand\nprofs' policies", "Profs understand\nstudent LLM use"], color=COLORS["cream"], fontsize=10)
    ax3.set_ylim(0, 5.5)
    ax3.legend(loc="upper right", facecolor=COLORS["navy"], edgecolor=COLORS["slate"], labelcolor=COLORS["cream"])
    ax3.set_facecolor(COLORS["navy"])
    ax3.spines[:].set_color(COLORS["slate"])
    ax3.tick_params(colors=COLORS["cream"])
    ax3.bar_label(bars3a, labels=[f"{avg_students:.2f}"], color=COLORS["cream"])
    ax3.bar_label(bars3b, labels=[f"{avg_profs:.2f}"], color=COLORS["cream"])

    # Footer
    fig.text(0.5, -0.02, f"n = {n} college students | Notre Dame & St. Mary's", ha="center", fontsize=10, color=COLORS["slate"])

    plt.tight_layout()
    out_path = OUTPUT_PATH / "llm_survey_figure.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=COLORS["navy"])
    plt.close()
    print(f"Figure saved to {out_path}")
    return out_path


def create_uses_chart():
    """Bar chart of what people use LLMs for, ranked highest to lowest, >=10% only."""
    rows = load_data()
    n = len(rows)

    from collections import Counter
    counts = Counter()
    for r in rows:
        if len(r) <= COL_LLM_USES:
            continue
        uses = r[COL_LLM_USES].strip()
        for item in uses.split(","):
            u = item.strip()
            if "coding" in u.lower() or "programming" in u.lower():
                u = "Coding"
            if u:
                counts[u] += 1

    # Filter >= 10%, sort ascending so highest is at top (barh index -1 = top)
    filtered = [(k, v) for k, v in counts.items() if 100 * v / n >= 10]
    filtered.sort(key=lambda x: x[1])
    labels = [x[0] for x in filtered]
    vals = [x[1] for x in filtered]
    pcts = [100 * v / n for v in vals]

    COLORS = {
        "navy": "#0C2340",
        "gold": "#C99700",
        "light_gold": "#E8C547",
        "slate": "#4A5F7F",
        "cream": "#F5F0E6",
    }

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(COLORS["navy"])
    y_pos = range(len(labels))
    bars = ax.barh(y_pos, vals, height=0.5, color=COLORS["gold"], edgecolor=COLORS["light_gold"], linewidth=1.2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=COLORS["cream"], fontsize=11)
    ax.set_xlabel("Number of respondents", color=COLORS["cream"])
    ax.set_xlim(0, n)
    ticks = [0, 10, 20, 30, 40, 50]
    if n not in ticks:
        ticks.append(n)
        ticks.sort()
    ax.set_xticks(ticks)
    ax.set_title("What Notre Dame Students Use LLMs for?", color=COLORS["gold"], fontsize=14)
    ax.set_facecolor(COLORS["navy"])
    ax.spines[:].set_color(COLORS["slate"])
    ax.tick_params(colors=COLORS["cream"])
    ax.bar_label(bars, labels=[f"{v} ({p:.0f}%)" for v, p in zip(vals, pcts)], color=COLORS["cream"], fontsize=10, padding=12)

    plt.tight_layout()
    out_path = OUTPUT_PATH / "llm_uses_chart.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=COLORS["navy"])
    plt.close()
    print(f"Figure saved to {out_path}")
    return out_path


def create_principle_practice_figure():
    """Typography-driven figure: principle vs practice, no bars, no overlaps."""
    rows = load_data()
    n = len(rows)

    ethical_yes = sum(1 for r in rows if len(r) > 20 and "Yes" in str(r[20]))
    school_yes = sum(1 for r in rows if len(r) > COL_SCHOOL and "Yes" in str(r[COL_SCHOOL]))
    personal_yes = sum(1 for r in rows if len(r) > COL_PERSONAL and "Yes" in str(r[COL_PERSONAL]))
    understand = []
    profs = []
    for r in rows:
        if len(r) > COL_PROFS_UNDERSTAND:
            up = safe_int(r[COL_UNDERSTAND_POLICIES])
            pu = safe_int(r[COL_PROFS_UNDERSTAND])
            if up and pu and 1 <= up <= 5 and 1 <= pu <= 5:
                understand.append(up)
                profs.append(pu)
    avg_stud = sum(understand) / len(understand) if understand else 0
    avg_prof = sum(profs) / len(profs) if profs else 0

    pct_ethical = 100 * ethical_yes / n
    pct_misuse = 100 * school_yes / n
    pct_personal = 100 * personal_yes / n

    # Grade counts for footer
    grade_map = {"Freshman": "FR", "Sophomore": "SO", "Junior": "JR", "Senior": "SR", "Graduate Student": "GR"}
    grades = {}
    for r in rows:
        if len(r) > COL_GRADE:
            g = str(r[COL_GRADE]).strip()
            short = grade_map.get(g, g[:2].upper() if g else "")
            if short:
                grades[short] = grades.get(short, 0) + 1
    grade_order = ["FR", "SO", "JR", "SR", "GR"]
    grade_str = "  ".join(f"{k}={grades.get(k, 0)}" for k in grade_order)

    COLORS = {
        "navy": "#0C2340",
        "gold": "#C99700",
        "light_gold": "#E8C547",
        "slate": "#4A5F7F",
        "cream": "#F5F0E6",
    }

    fig, ax = plt.subplots(figsize=(7, 5.5))
    fig.patch.set_facecolor(COLORS["navy"])
    ax.set_facecolor(COLORS["navy"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Title — bold, distinctive
    ax.text(5, 7.6, "Principle vs Practice", color=COLORS["gold"], fontsize=24, fontweight="bold", ha="center", va="top")
    ax.text(5, 7.0, "Notre Dame Students' Views on LLMs", color=COLORS["light_gold"], fontsize=14, fontweight="bold", ha="center", va="top")

    # Lightning-bolt divider (starts below title, jagged for "vs" effect)
    zig_y = np.linspace(6.3, 0.6, 12)
    zig_x = 5 + 0.4 * np.array([0, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, 0])
    ax.plot(zig_x, zig_y, color=COLORS["light_gold"], linewidth=1.5, alpha=0.7, zorder=0)

    # Left column: BELIEF
    ax.text(2.25, 6.0, "BELIEF", color=COLORS["cream"], fontsize=11, fontweight="bold", ha="center", va="top")
    ax.text(2.25, 4.9, f"{pct_ethical:.0f}%", color=COLORS["light_gold"], fontsize=42, fontweight="bold", ha="center", va="center")
    ax.text(2.25, 3.8, "Believe LLMs Can Be Used\nEthically (Catholic Mission)", color=COLORS["cream"], fontsize=11, ha="center", va="center", linespacing=1.4)

    # Right column: BEHAVIOR
    ax.text(7.75, 6.0, "BEHAVIOR", color=COLORS["cream"], fontsize=11, fontweight="bold", ha="center", va="top")
    ax.text(7.75, 5.4, f"{pct_misuse:.0f}%", color=COLORS["gold"], fontsize=26, fontweight="bold", ha="center", va="center")
    ax.text(7.75, 4.9, "Admit Misuse for School", color=COLORS["cream"], fontsize=11, ha="center", va="center")
    ax.text(7.75, 4.0, f"{pct_personal:.0f}%", color=COLORS["gold"], fontsize=26, fontweight="bold", ha="center", va="center")
    ax.text(7.75, 3.5, "Admit Misuse for Personal", color=COLORS["cream"], fontsize=11, ha="center", va="center")

    # Bottom: Understanding — Title Case
    ax.axhline(y=2.4, color=COLORS["light_gold"], linewidth=0.5, alpha=0.4, xmin=0.1, xmax=0.9)
    ax.text(2.5, 1.7, "I Understand My Professors'\nAI Policies", color=COLORS["cream"], fontsize=10, ha="center", va="center", linespacing=1.3)
    ax.text(2.5, 0.9, f"{avg_stud:.1f} / 5", color=COLORS["gold"], fontsize=13, fontweight="bold", ha="center", va="center")
    ax.text(7.5, 1.7, "Professors Understand How\nStudents Use AI", color=COLORS["cream"], fontsize=10, ha="center", va="center", linespacing=1.3)
    ax.text(7.5, 0.9, f"{avg_prof:.1f} / 5", color=COLORS["gold"], fontsize=13, fontweight="bold", ha="center", va="center")

    # Sample info at bottom — more spacing above, closer to bottom
    ax.text(5, 0.15, f"n={n}:  {grade_str}", color=COLORS["cream"], fontsize=12, ha="center", va="center")

    plt.tight_layout(pad=0.8)
    out_path = OUTPUT_PATH / "principle_practice_figure.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=COLORS["navy"])
    plt.close()
    print(f"Figure saved to {out_path}")
    return out_path


if __name__ == "__main__":
    create_figure()
    create_uses_chart()
    create_principle_practice_figure()
