"""Expériences du rapport TP2 :  python -m aussi experiences-jeux [--rapide]

Produit dans resultats/tp2/ :
    tactique.csv      victoire immédiate / blocage / menaces, par moteur et budget
    morpion.csv       validation au Tic-Tac-Toe (non-défaite, MCTS selon le budget)
    alphabeta.csv     nœuds avec et sans alpha-bêta (Tic-Tac-Toe, arbre complet)
    profondeur.csv    Puissance 4 : profondeur atteinte, nœuds, simulations selon le temps
    tournois.csv      Puissance 4 : évaluations, Minimax contre MCTS, constante c
    RESULTATS.md      toutes les tables

Les expériences tournent séquentiellement (les temps mesurés n'ont de sens que
sur une machine non chargée).
"""

from __future__ import annotations

import csv
import platform
import time
from pathlib import Path

from . import game_api
from .core import MCTS, IterativeDeepeningMinimax
from .experiments import _n
from .games.connect4 import Connect4
from .games.tictactoe import TicTacToe

TACTICS = [  # (jeu, coups joués, coups acceptés, description)
    ("tictactoe", "1 4 2 5", {"3"}, "morpion : gagner (au lieu de bloquer)"),
    ("tictactoe", "1 5 2", {"3"}, "morpion : bloquer"),
    ("tictactoe", "5 1 9", {"3", "7"}, "morpion : éviter la fourchette"),
    ("puissance4", "4 4 3 3 2 2", {"1", "5"}, "P4 : gagner (horizontal)"),
    ("puissance4", "1 2 1 2 1 3", {"1"}, "P4 : gagner (vertical)"),
    ("puissance4", "4 1 3 1 2", {"5"}, "P4 : bloquer (horizontal)"),
    ("puissance4", "1 2 1 2 1", {"1"}, "P4 : bloquer (vertical)"),
    ("puissance4", "4 4 3 3", {"2", "5"}, "P4 : créer un trois ouvert (gain en 3)"),
    ("puissance4", "4 7 3", {"2", "5"}, "P4 : empêcher un trois ouvert"),
]


class Connect4NaturalOrder(Connect4):
    """Puissance 4 avec les colonnes dans l'ordre 1..7 (pour mesurer l'effet de l'ordre des coups)."""
    def actions(self, state):
        if self.is_terminal(state):
            return []
        return [c for c in range(self.cols) if state.cells[c] == "."]


def table(rows: list[dict], cols: list[str]) -> str:
    """Table Markdown : nombres alignés à droite, texte à gauche."""
    def numeric(c):
        return all(isinstance(r[c], (int, float)) and not isinstance(r[c], bool) or r[c] is None for r in rows)

    def cell(v):
        if v is None:
            return "—"
        return _n(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v)

    head = "| " + " | ".join(cols) + " |"
    sep = "|" + "|".join("---:" if numeric(c) else "---" for c in cols) + "|"
    body = ["| " + " | ".join(cell(r[c]) for c in cols) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def _write(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def run_tactics(budgets, repeats):
    rows = []
    for engine, budget in [("minimax", b) for b in budgets] + [("mcts", b) for b in budgets]:
        for name, moves, ok, desc in TACTICS:
            game = game_api.build_game(name)
            s = game_api.replay(game, moves.split())
            hits = 0
            for seed in range(repeats if engine == "mcts" else 1):
                if engine == "minimax":
                    r = IterativeDeepeningMinimax(budget, evaluation=game.evaluation()).search(game, s)
                else:
                    r = MCTS(budget, seed=seed).search(game, s)
                hits += game.action_to_str(r.action) in ok
            n = repeats if engine == "mcts" else 1
            rows.append({"moteur": engine, "temps_s": budget, "position": desc, "reussite": f"{hits}/{n}",
                         "taux": hits / n})
    return rows


def run_tictactoe(n_random, mcts_sims, n_mcts):
    rows = []

    def add(a, b, n, openings=0):
        res = game_api.tournament({"game": "tictactoe", "a": a, "b": b, "n": n, "openings": openings, "seed": 1})
        s = res["score"]
        rows.append({"A": a, "B": b, "parties": n, "victoires_A": s["A"], "nulles": s["nulle"],
                     "victoires_B": s["B"], "temps_moyen_A_s": round(res["stats_A"]["temps_moyen_s"], 4)})
        print(f"  {a} contre {b} : {s}")

    add("minimax:temps=none", "aleatoire", n_random)
    add("minimax:temps=none", "minimax:temps=none", 2)
    for sims in mcts_sims:
        add(f"mcts:temps=none,sims={sims}", "aleatoire", n_mcts)
        add(f"mcts:temps=none,sims={sims}", "minimax:temps=none", n_mcts)
    return rows


def run_alphabeta():
    rows = []
    game = TicTacToe()
    for moves in ("", "1", "5"):
        s = game_api.replay(game, moves.split())
        for ab in (True, False):
            r = IterativeDeepeningMinimax(None, alpha_beta=ab).search(game, s)
            last = r.iterations[-1]
            rows.append({"position": f"après « {moves} »" if moves else "grille vide", "alpha_beta": ab,
                         "profondeur": r.completed_depth, "noeuds_derniere_iteration": last.nodes,
                         "noeuds_total": r.nodes, "temps_s": round(r.time_s, 3),
                         "coup": game.action_to_str(r.action), "valeur": r.value})
    return rows


def run_depth(budgets):
    rows = []
    positions = {"vide": "", "milieu": "4 3 4 4 5 3 3 5 2 6"}
    variants = [("alpha-bêta, centre d'abord", Connect4(), True),
                ("alpha-bêta, ordre 1..7", Connect4NaturalOrder(), True),
                ("sans alpha-bêta", Connect4(), False)]
    for pname, moves in positions.items():
        for t in budgets:
            for label, game, ab in variants:
                s = game_api.replay(game, moves.split())
                r = IterativeDeepeningMinimax(t, evaluation=game.evaluation(), alpha_beta=ab).search(game, s)
                rows.append({"position": pname, "temps_s": t, "moteur": f"minimax ({label})",
                             "profondeur": r.completed_depth, "noeuds": r.nodes,
                             "noeuds_par_s": round(r.nodes / r.time_s), "simulations": None,
                             "coup": game.action_to_str(r.action)})
            game = Connect4()
            s = game_api.replay(game, moves.split())
            r = MCTS(t, seed=0).search(game, s)
            rows.append({"position": pname, "temps_s": t, "moteur": "mcts (c=√2)", "profondeur": None,
                         "noeuds": r.tree_nodes, "noeuds_par_s": None, "simulations": r.simulations,
                         "coup": game.action_to_str(r.action)})
            print(f"  {pname} {t} s : fait")
    return rows


def run_tournaments(t_eval, t_versus, n, t_c, n_eval):
    rows = []

    def add(group, a, b, games=n):
        t0 = time.perf_counter()
        res = game_api.tournament({"game": "puissance4", "a": a, "b": b, "n": games, "openings": 2, "seed": 7})
        s, sa, sb = res["score"], res["stats_A"], res["stats_B"]
        row = {"groupe": group, "A": a, "B": b, "parties": games,
               "victoires_A": s["A"], "nulles": s["nulle"], "victoires_B": s["B"],
               "score_A": (s["A"] + s["nulle"] / 2) / games,
               "prof_moy_A": round(sa.get("profondeur_terminee_moyen", 0), 2) or None,
               "sims_moy_A": round(sa["simulations_moyen"]) if "simulations_moyen" in sa else None,
               "prof_moy_B": round(sb.get("profondeur_terminee_moyen", 0), 2) or None,
               "sims_moy_B": round(sb["simulations_moyen"]) if "simulations_moyen" in sb else None,
               "duree_s": round(time.perf_counter() - t0, 1)}
        rows.append(row)
        print(f"  [{group}] {a} contre {b} : {s} ({row['duree_s']} s)")

    add("contre aléatoire", f"minimax:temps={t_eval}", "aleatoire")
    add("contre aléatoire", f"mcts:temps={t_eval}", "aleatoire")
    for ev in ("neutre", "centre", "fenetres"):
        add("évaluations", f"minimax:temps={t_eval},eval=fenetres_centre", f"minimax:temps={t_eval},eval={ev}", n_eval)
    for t in t_versus:
        add("minimax contre mcts", f"minimax:temps={t}", f"mcts:temps={t}")
    for c in (0.5, 3.0):
        add("constante c", f"mcts:temps={t_c},c={c}", f"mcts:temps={t_c},c=1.414")
    return rows


def main(out_dir: str = "resultats/tp2", quick: bool = False):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    if quick:
        cfg = dict(tactic_budgets=[0.1], repeats=3, n_random=10, mcts_sims=[100, 1000], n_mcts=4,
                   depth_budgets=[0.1, 0.5], t_eval=0.05, t_versus=[0.05], n=4, t_c=0.05, n_eval=4)
    else:
        cfg = dict(tactic_budgets=[0.05, 0.2, 1.0], repeats=10, n_random=100, mcts_sims=[50, 200, 1000, 5000],
                   n_mcts=20, depth_budgets=[0.1, 0.5, 1.0, 2.0], t_eval=0.1, t_versus=[0.1, 0.5, 1.0], n=10,
                   t_c=0.2, n_eval=30)

    print("1. Tests tactiques")
    tactics = run_tactics(cfg["tactic_budgets"], cfg["repeats"])
    print("2. Validation au Tic-Tac-Toe")
    ttt = run_tictactoe(cfg["n_random"], cfg["mcts_sims"], cfg["n_mcts"])
    print("3. Alpha-bêta (Tic-Tac-Toe, arbre complet)")
    ab = run_alphabeta()
    print("4. Puissance 4 : profondeur et simulations selon le temps")
    depth = run_depth(cfg["depth_budgets"])
    print("5. Puissance 4 : tournois")
    tours = run_tournaments(cfg["t_eval"], cfg["t_versus"], cfg["n"], cfg["t_c"], cfg["n_eval"])

    for name, rows in [("tactique", tactics), ("morpion", ttt), ("alphabeta", ab), ("profondeur", depth),
                       ("tournois", tours)]:
        _write(out / f"{name}.csv", rows)

    # tactique : une ligne par position, une colonne par moteur × budget
    pivot = {}
    for r in tactics:
        pivot.setdefault(r["position"], {"position": r["position"]})[f"{r['moteur']} {r['temps_s']} s"] = r["reussite"]
    md = [
        "# AUSSI TP2 : résultats bruts",
        "",
        f"Généré par `python -m aussi experiences-jeux{' --rapide' if quick else ''}` "
        f"(Python {platform.python_version()}, {platform.machine()}), durée {time.perf_counter() - started:.0f} s.",
        "Les temps et les compteurs qui en dépendent (profondeur, nœuds, simulations) varient d'une machine à l'autre.",
        "",
        "## 1. Tests tactiques (coup correct / essais ; MCTS répété avec des graines différentes)",
        "", table(list(pivot.values()), list(next(iter(pivot.values())))), "",
        "## 2. Tic-Tac-Toe : validation",
        "", table(ttt, list(ttt[0])), "",
        "## 3. Alpha-bêta au Tic-Tac-Toe (exploration complète)",
        "", table(ab, list(ab[0])), "",
        "## 4. Puissance 4 : ce que le budget permet",
        "", table(depth, list(depth[0])), "",
        "## 5. Puissance 4 : tournois (ouvertures aléatoires de 2 demi-coups, couleurs alternées)",
        "", table(tours, list(tours[0])), "",
    ]
    (out / "RESULTATS.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nRésultats écrits dans {out}/ ({time.perf_counter() - started:.0f} s)")
