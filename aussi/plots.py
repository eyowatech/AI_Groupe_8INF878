"""Génération des graphiques comparatifs pour les expériences AUSSI."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
RESULTATS = ROOT / "resultats"
GRAPHIQUES = RESULTATS / "graphiques"

GRAPHIQUES.mkdir(parents=True, exist_ok=True)


def graphique_strategies():
    """Compare BFS, UCS, Greedy et A* sur le labyrinthe moyen."""

    df = pd.read_csv(RESULTATS / "strategies.csv")

    data = df[
        (df["probleme"] == "Labyrinthe moyen 21×21 (4 dir.)")
        & (df["mode"] == "graph")
        & (df["strategie"].isin(["bfs", "ucs", "greedy", "astar"]))
    ].copy()

    plt.figure(figsize=(8, 5))

    plt.bar(
        data["strategie"].str.upper(),
        data["developpes"],
    )

    plt.xlabel("Stratégie")
    plt.ylabel("Nœuds développés")
    plt.title("Comparaison des stratégies — Labyrinthe moyen")
    plt.tight_layout()

    plt.savefig(
        GRAPHIQUES / "strategies_noeuds.png",
        dpi=200,
    )

    plt.close()


def graphique_modes():
    """Compare Tree-Search et Graph-Search."""

    df = pd.read_csv(RESULTATS / "strategies.csv")

    data = df[
        (df["probleme"] == "Labyrinthe moyen 21×21 (4 dir.)")
        & (df["strategie"].isin(["bfs", "ucs", "greedy", "astar"]))
    ].copy()

    pivot = data.pivot_table(
        index="strategie",
        columns="mode",
        values="developpes",
        aggfunc="first",
    )

    ordre = [
        strategie
        for strategie in ["bfs", "ucs", "greedy", "astar"]
        if strategie in pivot.index
    ]

    pivot = pivot.reindex(ordre)

    ax = pivot.plot(
        kind="bar",
        figsize=(8, 5),
    )

    ax.set_xlabel("Stratégie")
    ax.set_ylabel("Nœuds développés")
    ax.set_title("Tree-Search vs Graph-Search")
    ax.tick_params(axis="x", rotation=0)

    plt.tight_layout()

    plt.savefig(
        GRAPHIQUES / "tree_vs_graph.png",
        dpi=200,
    )

    plt.close()


def graphique_heuristiques():
    """Compare les heuristiques A* sur le 8-Puzzle moyen."""

    df = pd.read_csv(RESULTATS / "heuristiques.csv")

    data = df[
        (df["probleme"] == "8-Puzzle moyen")
        & (df["strategie"] == "astar")
        & (df["mode"] == "graph")
    ].copy()

    plt.figure(figsize=(9, 5))

    plt.bar(
        data["heuristique"],
        data["developpes"],
    )

    plt.xlabel("Heuristique")
    plt.ylabel("Nœuds développés")
    plt.title("Impact de l'heuristique — A* sur le 8-Puzzle moyen")
    plt.xticks(rotation=20, ha="right")

    plt.tight_layout()

    plt.savefig(
        GRAPHIQUES / "heuristiques_npuzzle.png",
        dpi=200,
    )

    plt.close()


def graphique_temps_heuristiques():
    """Compare le temps d'exécution des heuristiques A*."""

    df = pd.read_csv(RESULTATS / "heuristiques.csv")

    data = df[
        (df["probleme"] == "8-Puzzle moyen")
        & (df["strategie"] == "astar")
        & (df["mode"] == "graph")
    ].copy()

    plt.figure(figsize=(9, 5))

    plt.bar(
        data["heuristique"],
        data["temps_s"],
    )

    plt.xlabel("Heuristique")
    plt.ylabel("Temps d'exécution (s)")
    plt.title("Temps d'exécution — A* sur le 8-Puzzle moyen")
    plt.xticks(rotation=20, ha="right")

    plt.tight_layout()

    plt.savefig(
        GRAPHIQUES / "heuristiques_temps.png",
        dpi=200,
    )

    plt.close()


def main():
    graphique_strategies()
    graphique_modes()
    graphique_heuristiques()
    graphique_temps_heuristiques()

    print(f"Graphiques générés dans : {GRAPHIQUES}")


if __name__ == "__main__":
    main()