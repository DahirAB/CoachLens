import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def plot_feasibility_heatmap(rows):
    goals = sorted(set(r["goal"] for r in rows))
    equips = sorted(set(r["equipment"] for r in rows))

    matrix = np.zeros((len(goals), len(equips)))
    counts = np.zeros((len(goals), len(equips)))

    for r in rows:
        gi = goals.index(r["goal"])
        ei = equips.index(r["equipment"])
        counts[gi][ei] += 1
        if r["feasible"] == "False":
            matrix[gi][ei] += 1

    for i in range(len(goals)):
        for j in range(len(equips)):
            if counts[i][j] > 0:
                matrix[i][j] = 100 * matrix[i][j] / counts[i][j]

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(matrix, cmap="RdYlGn_r", aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(equips)))
    ax.set_xticklabels(equips, rotation=45, ha="right")
    ax.set_yticks(range(len(goals)))
    ax.set_yticklabels(goals)
    ax.set_xlabel("Equipment")
    ax.set_ylabel("Training Goal")
    ax.set_title("Infeasibility Rate by Goal and Equipment (%)")

    for i in range(len(goals)):
        for j in range(len(equips)):
            ax.text(j, i, f"{matrix[i][j]:.0f}%", ha="center", va="center",
                    color="white" if matrix[i][j] > 50 else "black", fontsize=11)

    plt.colorbar(im, label="Infeasibility Rate (%)")
    plt.tight_layout()
    plt.savefig("fig_feasibility_heatmap.png", dpi=150)
    plt.close()
    print("Saved: fig_feasibility_heatmap.png")


def plot_feasibility_by_days(rows):
    by_days = defaultdict(lambda: {"total": 0, "infeasible": 0})
    for r in rows:
        d = int(r["n_days"])
        by_days[d]["total"] += 1
        if r["feasible"] == "False":
            by_days[d]["infeasible"] += 1

    days = sorted(by_days.keys())
    rates = [100 * by_days[d]["infeasible"] / by_days[d]["total"] for d in days]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(days, rates, color="#e74c3c", edgecolor="black", width=0.6)
    ax.set_xlabel("Number of Training Days")
    ax.set_ylabel("Infeasibility Rate (%)")
    ax.set_title("Infeasibility Rate by Number of Training Days")
    ax.set_xticks(days)
    ax.set_ylim(0, max(rates) * 1.2 if rates else 100)

    for i, (d, r) in enumerate(zip(days, rates)):
        ax.text(d, r + 1, f"{r:.0f}%", ha="center", fontsize=10)

    plt.tight_layout()
    plt.savefig("fig_feasibility_by_days.png", dpi=150)
    plt.close()
    print("Saved: fig_feasibility_by_days.png")


def plot_solve_times(rows):
    feasible = [r for r in rows if r["status"] == "feasible"]
    if not feasible:
        print("No feasible rows for solve time chart")
        return

    days = [int(r["n_days"]) for r in feasible]
    times = [float(r["solve_time_s"]) for r in feasible]
    equips = [r["equipment"] for r in feasible]

    equip_colors = {"full_gym": "#3498db", "bodyweight_only": "#2ecc71", "dumbbell": "#e67e22"}

    fig, ax = plt.subplots(figsize=(8, 5))
    for eq in sorted(set(equips)):
        eq_days = [d for d, e in zip(days, equips) if e == eq]
        eq_times = [t for t, e in zip(times, equips) if e == eq]
        ax.scatter(eq_days, eq_times, label=eq, alpha=0.5, s=20,
                   color=equip_colors.get(eq, "gray"))

    by_day = defaultdict(list)
    for d, t in zip(days, times):
        by_day[d].append(t)
    avg_days = sorted(by_day.keys())
    avg_times = [sum(by_day[d]) / len(by_day[d]) for d in avg_days]
    ax.plot(avg_days, avg_times, "k-o", linewidth=2, markersize=6, label="mean", zorder=5)

    ax.set_xlabel("Number of Training Days")
    ax.set_ylabel("Solve Time (seconds)")
    ax.set_title("CP-SAT Solve Time vs Plan Complexity")
    ax.legend()
    ax.set_xticks(sorted(set(days)))
    plt.tight_layout()
    plt.savefig("fig_solve_times.png", dpi=150)
    plt.close()
    print("Saved: fig_solve_times.png")


def plot_baseline_comparison(rows):
    valid = [r for r in rows if r["solver_score"] != "infeasible"]
    if not valid:
        print("No valid rows for baseline comparison chart")
        return

    goals = sorted(set(r["goal"] for r in valid))
    solver_avgs = []
    baseline_avgs = []

    for g in goals:
        g_rows = [r for r in valid if r["goal"] == g]
        s_avg = sum(float(r["solver_score"]) for r in g_rows) / len(g_rows)
        b_avg = sum(float(r["baseline_avg_score"]) for r in g_rows) / len(g_rows)
        solver_avgs.append(s_avg)
        baseline_avgs.append(b_avg)

    x = np.arange(len(goals))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width / 2, solver_avgs, width, label="CP-SAT Solver", color="#3498db", edgecolor="black")
    bars2 = ax.bar(x + width / 2, baseline_avgs, width, label="Random Baseline", color="#e74c3c", edgecolor="black")

    ax.set_xlabel("Training Goal")
    ax.set_ylabel("Average Plan Quality Score")
    ax.set_title("CP-SAT Solver vs Random Baseline")
    ax.set_xticks(x)
    ax.set_xticklabels(goals, rotation=20, ha="right")
    ax.legend()
    ax.set_ylim(0, 1.0)

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{bar.get_height():.2f}", ha="center", fontsize=9)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{bar.get_height():.2f}", ha="center", fontsize=9)

    plt.tight_layout()
    plt.savefig("fig_baseline_comparison.png", dpi=150)
    plt.close()
    print("Saved: fig_baseline_comparison.png")


def plot_score_breakdown(rows):
    valid = [r for r in rows if r["solver_score"] != "infeasible"]
    if not valid:
        return

    goals = sorted(set(r["goal"] for r in valid))

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(goals))

    improvements = []
    for g in goals:
        g_rows = [r for r in valid if r["goal"] == g]
        imps = []
        for r in g_rows:
            if r["improvement_pct"] != "n/a":
                imps.append(float(r["improvement_pct"]))
        improvements.append(sum(imps) / len(imps) if imps else 0)

    colors = ["#2ecc71" if v > 0 else "#e74c3c" for v in improvements]
    ax.bar(x, improvements, color=colors, edgecolor="black", width=0.5)
    ax.set_xlabel("Training Goal")
    ax.set_ylabel("Improvement over Baseline (%)")
    ax.set_title("Solver Improvement over Random Baseline by Goal")
    ax.set_xticks(x)
    ax.set_xticklabels(goals, rotation=20, ha="right")
    ax.axhline(y=0, color="black", linewidth=0.5)

    for i, v in enumerate(improvements):
        ax.text(i, v + (1 if v >= 0 else -3), f"{v:.1f}%", ha="center", fontsize=10)

    plt.tight_layout()
    plt.savefig("fig_improvement_by_goal.png", dpi=150)
    plt.close()
    print("Saved: fig_improvement_by_goal.png")


def run_all_charts():
    try:
        feasibility_rows = load_csv("feasibility_matrix.csv")
        plot_feasibility_heatmap(feasibility_rows)
        plot_feasibility_by_days(feasibility_rows)
    except FileNotFoundError:
        print("feasibility_matrix.csv not found, skipping feasibility charts")

    try:
        solve_rows = load_csv("solve_times.csv")
        plot_solve_times(solve_rows)
    except FileNotFoundError:
        print("solve_times.csv not found, skipping solve time chart")

    try:
        baseline_rows = load_csv("baseline_comparison.csv")
        plot_baseline_comparison(baseline_rows)
        plot_score_breakdown(baseline_rows)
    except FileNotFoundError:
        print("baseline_comparison.csv not found, skipping baseline charts")

    print("\nAll charts generated.")


if __name__ == "__main__":
    run_all_charts()
