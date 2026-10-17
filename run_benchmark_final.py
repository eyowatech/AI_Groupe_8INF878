"""Run the AUSSI V2 search benchmark and export its results as CSV."""

from __future__ import annotations

import csv
from pathlib import Path

from aussi.core.search import search
from aussi.problems.arithmetic import Arithmetic
from aussi.problems.maze import Maze
from aussi.problems.navigation import RoadMap
from aussi.problems.npuzzle import NPuzzle, scramble


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "resultats_experiences.csv"
STRATEGIES = ("bfs", "ucs", "greedy", "astar")
CSV_FIELDS = (
    "problem",
    "instance",
    "difficulty",
    "strategy",
    "mode",
    "solved",
    "cost",
    "depth",
    "nodes_generated",
    "nodes_expanded",
    "max_open",
    "time_seconds",
)


def _benchmarks() -> list[dict]:
    simple_maze = [
        "#######",
        "#S...G#",
        "#.#...#",
        "#.....#",
        "#######",
    ]
    weighted_maze = [
        "########",
        "#S..~..#",
        "#.#.~#G#",
        "#...:..#",
        "########",
    ]
    medium_puzzle = scramble(3, 40, seed=4)

    return [
        {
            "problem": "Labyrinthe",
            "instance": "Simple_5x7",
            "difficulty": "Facile",
            "factory": lambda: Maze(simple_maze, label="simple"),
            "modes": ("graph", "tree"),
        },
        {
            "problem": "Labyrinthe",
            "instance": "Pondere_Moyen",
            "difficulty": "Moyenne",
            "factory": lambda: Maze(weighted_maze, label="pondéré"),
            "modes": ("graph", "tree"),
        },
        {
            "problem": "Navigation",
            "instance": "Gatineau_BaieComeau",
            "difficulty": "Moyenne",
            "factory": lambda: RoadMap(start="Gatineau", goal="Baie-Comeau"),
            "modes": ("graph",),
        },
        {
            "problem": "N-Puzzle",
            "instance": "8Puzzle_Moyen",
            "difficulty": "Moyenne",
            "factory": lambda: NPuzzle(medium_puzzle, heuristic="manhattan", label="moyen"),
            "modes": ("graph",),
        },
        {
            "problem": "Arithmetique",
            "instance": "Cible_24",
            "difficulty": "Moyenne",
            "factory": lambda: Arithmetic([2, 3, 5, 7], 24),
            "modes": ("graph",),
        },
        {
            "problem": "Arithmetique",
            "instance": "Impossible_99",
            "difficulty": "Difficile",
            "factory": lambda: Arithmetic([1, 1, 1, 1], 99),
            "modes": ("graph",),
        },
        *[
            {
                "problem": "N-Puzzle-Heuristiques",
                "instance": f"8Puzzle_heuristique_{heuristic}",
                "difficulty": "Moyenne",
                "factory": lambda heuristic=heuristic: NPuzzle(
                    medium_puzzle, heuristic=heuristic, label="moyen"
                ),
                "modes": ("graph",),
            }
            for heuristic in ("zero", "mal_placees", "manhattan")
        ],
    ]


def run_benchmarks() -> list[dict]:
    results = []
    for benchmark in _benchmarks():
        for strategy in STRATEGIES:
            for mode in benchmark["modes"]:
                result = search(benchmark["factory"](), strategy=strategy, mode=mode)
                stats = result.stats
                row = {
                    "problem": benchmark["problem"],
                    "instance": benchmark["instance"],
                    "difficulty": benchmark["difficulty"],
                    "strategy": strategy.upper(),
                    "mode": "Tree-Search" if mode == "tree" else "Graph-Search",
                    "solved": result.found,
                    "cost": result.cost,
                    "depth": result.depth,
                    "nodes_generated": stats.generated,
                    "nodes_expanded": stats.expanded,
                    "max_open": stats.max_frontier,
                    "time_seconds": round(stats.time_s, 6),
                }
                results.append(row)
                print(
                    f"{row['problem']} / {row['instance']} / {row['strategy']} / "
                    f"{row['mode']}: solved={row['solved']}, "
                    f"generated={row['nodes_generated']}, "
                    f"expanded={row['nodes_expanded']}, "
                    f"time={row['time_seconds']:.6f}s"
                )
    return results


def main() -> None:
    rows = run_benchmarks()
    with OUTPUT.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(rows)} résultats exportés vers {OUTPUT}")


if __name__ == "__main__":
    main()
