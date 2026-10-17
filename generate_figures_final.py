"""Generate the final benchmark figures from resultats_experiences.csv."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "resultats_experiences.csv"
FIGURES_DIR = ROOT / "figures"
STRATEGIES = ("BFS", "UCS", "GREEDY", "ASTAR")
STRATEGY_COLORS = {
    "BFS": "#1F77B4",
    "UCS": "#2CA02C",
    "GREEDY": "#FF7F0E",
    "ASTAR": "#D62728",
}
HEURISTICS = (
    ("8Puzzle_heuristique_zero", "Nulle (h=0)"),
    ("8Puzzle_heuristique_mal_placees", "Tuiles mal placées"),
    ("8Puzzle_heuristique_manhattan", "Manhattan"),
)


def _read_rows() -> list[dict[str, str]]:
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"Fichier de résultats introuvable : {CSV_PATH}")
    with CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))
    if not rows:
        raise ValueError(f"Le fichier de résultats est vide : {CSV_PATH}")
    return rows


def _select(
    rows: list[dict[str, str]], **criteria: str
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if all(row.get(key) == value for key, value in criteria.items())
    ]


def _one(
    rows: list[dict[str, str]], description: str, **criteria: str
) -> dict[str, str]:
    matches = _select(rows, **criteria)
    if len(matches) != 1:
        raise ValueError(
            f"Attendu un résultat pour {description}, trouvé(s) : {len(matches)}"
        )
    return matches[0]


def _annotate_bars(ax, bars, values: list[float], formatter=str) -> None:
    top = max(values, default=0)
    for bar, value in zip(bars, values):
        offset = max(top * 0.015, 0.01)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            formatter(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    if top > 0:
        ax.set_ylim(0, top * 1.18)


def _strategies_figure(rows: list[dict[str, str]]) -> None:
    selected = [
        _one(
            rows,
            f"{strategy} sur le labyrinthe pondéré",
            problem="Labyrinthe",
            instance="Pondere_Moyen",
            strategy=strategy,
            mode="Graph-Search",
        )
        for strategy in STRATEGIES
    ]
    values = [int(row["nodes_generated"]) for row in selected]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        STRATEGIES,
        values,
        color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
    )
    ax.set_xlabel("Stratégie")
    ax.set_ylabel("Nœuds générés")
    ax.set_title("Nœuds générés par stratégie — Labyrinthe pondéré")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    _annotate_bars(ax, bars, values, lambda value: f"{int(value)}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "strategies_noeuds.png", dpi=300)
    plt.close(fig)


def _tree_graph_figure(rows: list[dict[str, str]]) -> None:
    selected = {
        (strategy, mode): _one(
            rows,
            f"{strategy}, {mode} sur le labyrinthe pondéré",
            problem="Labyrinthe",
            instance="Pondere_Moyen",
            strategy=strategy,
            mode=mode,
        )
        for strategy in STRATEGIES
        for mode in ("Tree-Search", "Graph-Search")
    }
    x = list(range(len(STRATEGIES)))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9, 5))
    for offset, mode, hatch in (
        (-width / 2, "Tree-Search", "//"),
        (width / 2, "Graph-Search", ""),
    ):
        mode_values = [
            int(selected[(strategy, mode)]["nodes_generated"])
            for strategy in STRATEGIES
        ]
        bars = ax.bar(
            [position + offset for position in x],
            mode_values,
            width,
            color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
            hatch=hatch,
            edgecolor="black",
            label=mode,
        )
        for bar, value in zip(bars, mode_values):
            ax.annotate(
                f"{value}",
                (bar.get_x() + bar.get_width() / 2, value),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    ax.set_yscale("log")
    ax.set_xticks(x, STRATEGIES)
    ax.set_xlabel("Stratégie")
    ax.set_ylabel("Nœuds générés (échelle logarithmique)")
    ax.set_title("Tree-Search vs Graph-Search — Labyrinthe pondéré")
    ax.legend(handles=[
        Patch(facecolor="white", edgecolor="black", hatch="//", label="Tree-Search"),
        Patch(facecolor="white", edgecolor="black", label="Graph-Search"),
    ], loc="upper left")
    ax.grid(axis="y", which="both", linestyle="--", alpha=0.35)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "tree_vs_graph.png", dpi=300)
    plt.close(fig)


def _heuristic_figures(rows: list[dict[str, str]]) -> None:
    selected = [
        _one(
            rows,
            f"heuristique {label} pour A* sur le 8-Puzzle",
            problem="N-Puzzle-Heuristiques",
            instance=instance,
            strategy="ASTAR",
            mode="Graph-Search",
        )
        for instance, label in HEURISTICS
    ]
    labels = [label for _, label in HEURISTICS]

    fig, ax = plt.subplots(figsize=(8, 5))
    expanded = [int(row["nodes_expanded"]) for row in selected]
    bars = ax.bar(labels, expanded, color=["#7F7F7F", "#AEC7E8", "#D62728"])
    ax.set_xlabel("Heuristique utilisée par A*")
    ax.set_ylabel("Nœuds développés")
    ax.set_title("Nœuds développés selon l’heuristique — 8-Puzzle")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    _annotate_bars(ax, bars, expanded, lambda value: f"{int(value)}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "heuristiques_npuzzle.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    times = [float(row["time_seconds"]) for row in selected]
    bars = ax.bar(labels, times, color=["#7F7F7F", "#AEC7E8", "#D62728"])
    ax.set_xlabel("Heuristique utilisée par A*")
    ax.set_ylabel("Temps d’exécution (secondes)")
    ax.set_title("Temps d’exécution selon l’heuristique — 8-Puzzle")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    _annotate_bars(ax, bars, times, lambda value: f"{value:.4f}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "heuristiques_temps.png", dpi=300)
    plt.close(fig)


def _navigation_figure(rows: list[dict[str, str]]) -> None:
    selected = [
        _one(
            rows,
            f"{strategy} sur Gatineau–Baie-Comeau",
            problem="Navigation",
            instance="Gatineau_BaieComeau",
            strategy=strategy,
            mode="Graph-Search",
        )
        for strategy in STRATEGIES
    ]
    expanded = [int(row["nodes_expanded"]) for row in selected]
    costs = [float(row["cost"]) for row in selected]
    fig, (ax_nodes, ax_cost) = plt.subplots(1, 2, figsize=(11, 5))

    bars = ax_nodes.bar(
        STRATEGIES,
        expanded,
        color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
    )
    ax_nodes.set_xlabel("Stratégie")
    ax_nodes.set_ylabel("Nœuds développés")
    ax_nodes.set_title("Effort de recherche")
    ax_nodes.grid(axis="y", linestyle="--", alpha=0.4)
    _annotate_bars(ax_nodes, bars, expanded, lambda value: f"{int(value)}")

    bars = ax_cost.bar(
        STRATEGIES,
        costs,
        color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
    )
    ax_cost.set_xlabel("Stratégie")
    ax_cost.set_ylabel("Coût du trajet (km)")
    ax_cost.set_title("Qualité de la solution")
    ax_cost.grid(axis="y", linestyle="--", alpha=0.4)
    _annotate_bars(ax_cost, bars, costs, lambda value: f"{value:.1f}")

    fig.suptitle("Navigation Gatineau–Baie-Comeau : effort et coût")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "navigation_strategies.png", dpi=300)
    plt.close(fig)


def _npuzzle_strategy_figure(rows: list[dict[str, str]]) -> None:
    selected = [
        _one(
            rows,
            f"{strategy} sur le 8-Puzzle moyen",
            problem="N-Puzzle",
            instance="8Puzzle_Moyen",
            strategy=strategy,
            mode="Graph-Search",
        )
        for strategy in STRATEGIES
    ]
    expanded = [int(row["nodes_expanded"]) for row in selected]
    depths = [int(row["depth"]) for row in selected]
    fig, (ax_nodes, ax_depth) = plt.subplots(1, 2, figsize=(11, 5))

    bars = ax_nodes.bar(
        STRATEGIES,
        expanded,
        color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
    )
    ax_nodes.set_yscale("log")
    ax_nodes.set_xlabel("Stratégie")
    ax_nodes.set_ylabel("Nœuds développés (échelle logarithmique)")
    ax_nodes.set_title("Effort de recherche")
    ax_nodes.grid(axis="y", which="both", linestyle="--", alpha=0.4)
    for bar, value in zip(bars, expanded):
        ax_nodes.annotate(
            f"{value:,}",
            (bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    bars = ax_depth.bar(
        STRATEGIES,
        depths,
        color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
    )
    ax_depth.set_xlabel("Stratégie")
    ax_depth.set_ylabel("Profondeur de la solution (coups)")
    ax_depth.set_title("Longueur de la solution")
    ax_depth.grid(axis="y", linestyle="--", alpha=0.4)
    _annotate_bars(ax_depth, bars, depths, lambda value: f"{int(value)}")

    fig.suptitle("Stratégies sur le 8-Puzzle moyen")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "strategies_npuzzle.png", dpi=300)
    plt.close(fig)


def _tree_graph_reduction_figure(rows: list[dict[str, str]]) -> None:
    cases = (
        ("Simple_5x7", "Labyrinthe simple"),
        ("Pondere_Moyen", "Labyrinthe pondéré"),
    )
    reductions: dict[str, list[float]] = {label: [] for _, label in cases}
    for instance, label in cases:
        for strategy in STRATEGIES:
            tree = _one(
                rows,
                f"{strategy}, Tree-Search, {label}",
                problem="Labyrinthe",
                instance=instance,
                strategy=strategy,
                mode="Tree-Search",
            )
            graph = _one(
                rows,
                f"{strategy}, Graph-Search, {label}",
                problem="Labyrinthe",
                instance=instance,
                strategy=strategy,
                mode="Graph-Search",
            )
            tree_expanded = int(tree["nodes_expanded"])
            graph_expanded = int(graph["nodes_expanded"])
            reduction = (
                100 * (tree_expanded - graph_expanded) / tree_expanded
                if tree_expanded
                else 0
            )
            reductions[label].append(reduction)

    x = list(range(len(STRATEGIES)))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9, 5))
    for offset, (instance, label), hatch in zip(
        (-width / 2, width / 2), cases, ("//", "")
    ):
        bars = ax.bar(
            [position + offset for position in x],
            reductions[label],
            width,
            color=[STRATEGY_COLORS[strategy] for strategy in STRATEGIES],
            hatch=hatch,
            edgecolor="black",
        )
        for bar, value in zip(bars, reductions[label]):
            ax.annotate(
                f"{value:.1f}%",
                (bar.get_x() + bar.get_width() / 2, value),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    ax.set_xticks(x, STRATEGIES)
    ax.set_xlabel("Stratégie")
    ax.set_ylabel("Réduction des nœuds développés (%)")
    ax.set_title("Réduction Tree-Search → Graph-Search")
    ax.set_ylim(0, 110)
    ax.legend(handles=[
        Patch(facecolor="white", edgecolor="black", hatch="//", label=cases[0][1]),
        Patch(facecolor="white", edgecolor="black", label=cases[1][1]),
    ])
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "tree_graph_reduction.png", dpi=300)
    plt.close(fig)


def _heuristic_gain_figure(rows: list[dict[str, str]]) -> None:
    heuristic_rows = [
        _one(
            rows,
            f"A* avec l’heuristique {label}",
            problem="N-Puzzle-Heuristiques",
            instance=instance,
            strategy="ASTAR",
            mode="Graph-Search",
        )
        for instance, label in HEURISTICS
    ]
    baseline = int(heuristic_rows[0]["nodes_expanded"])
    labels = [label for _, label in HEURISTICS]
    reductions = [
        100 * (baseline - int(row["nodes_expanded"])) / baseline
        for row in heuristic_rows
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        labels,
        reductions,
        color=["#7F7F7F", "#AEC7E8", "#D62728"],
    )
    ax.set_xlabel("Heuristique utilisée par A*")
    ax.set_ylabel("Réduction des nœuds développés (%)")
    ax.set_title("Gain relatif à A* avec h=0 — 8-Puzzle moyen")
    ax.set_ylim(0, 105)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, value in zip(bars, reductions):
        ax.annotate(
            f"{value:.1f}%",
            (bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
        )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "heuristiques_gain.png", dpi=300)
    plt.close(fig)


def _arithmetic_figure(rows: list[dict[str, str]]) -> None:
    instances = (
        ("Cible_24", "Cible 24\n(solution trouvée)"),
        ("Impossible_99", "Cible 99\n(aucune solution)"),
    )
    x = list(range(len(instances)))
    width = 0.19
    fig, ax = plt.subplots(figsize=(9, 5))
    for index, strategy in enumerate(STRATEGIES):
        values = [
            int(
                _one(
                    rows,
                    f"{strategy} sur {instance}",
                    problem="Arithmetique",
                    instance=instance,
                    strategy=strategy,
                    mode="Graph-Search",
                )["nodes_expanded"]
            )
            for instance, _ in instances
        ]
        positions = [
            group + (index - (len(STRATEGIES) - 1) / 2) * width
            for group in x
        ]
        bars = ax.bar(
            positions,
            values,
            width,
            color=STRATEGY_COLORS[strategy],
            label=strategy,
        )
        for bar, value in zip(bars, values):
            ax.annotate(
                f"{value}",
                (bar.get_x() + bar.get_width() / 2, value),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    ax.set_xticks(x, [label for _, label in instances])
    ax.set_xlabel("Instance arithmétique")
    ax.set_ylabel("Nœuds développés")
    ax.set_title("Recherche arithmétique : solution et absence de solution")
    ax.legend(title="Stratégie")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "arithmetique_resultats.png", dpi=300)
    plt.close(fig)

def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    rows = _read_rows()
    _strategies_figure(rows)
    _tree_graph_figure(rows)
    _heuristic_figures(rows)
    _navigation_figure(rows)
    _npuzzle_strategy_figure(rows)
    _tree_graph_reduction_figure(rows)
    _heuristic_gain_figure(rows)
    _arithmetic_figure(rows)
    print(f"9 figures PNG générées dans {FIGURES_DIR}")


if __name__ == "__main__":
    main()
