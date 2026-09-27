"""Expérience comparative des stratégies et des heuristiques.

    python -m aussi experiences [--time 3] [--memory 500000]

Produit dans `resultats/` :
    strategies.csv      chaque instance × {BFS, UCS, Greedy, A*} × {graph, tree}
    heuristiques.csv    A* (graph) avec différentes heuristiques
    RESULTATS.md        tableaux de synthèse
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

from .api import build_problem
from .core import search, Limits, MODES

STRATEGIES = ["bfs", "ucs", "greedy", "astar"]

INSTANCES = [
    ("labyrinthe", {"preset": "simple"}),
    ("labyrinthe", {"preset": "moyen"}),
    ("labyrinthe", {"preset": "complexe"}),
    ("labyrinthe", {"preset": "pondere"}),
    ("labyrinthe", {"preset": "portails"}),
    ("labyrinthe", {"preset": "diagonal"}),
    ("labyrinthe", {"preset": "sans_solution"}),
    ("navigation", {"start": "Chicoutimi", "goal": "Montréal"}),
    ("navigation", {"start": "Rouyn-Noranda", "goal": "Gaspé"}),
    ("navigation", {"start": "Gatineau", "goal": "Baie-Comeau"}),
    ("navigation", {"start": "Gaspé", "goal": "Îles-de-la-Madeleine"}),
    ("npuzzle", {"preset": "facile"}),
    ("npuzzle", {"preset": "moyen"}),
    ("npuzzle", {"preset": "difficile"}),
    ("npuzzle", {"preset": "15_facile"}),
    ("npuzzle", {"preset": "15_difficile"}),
    ("arithmetique", {"preset": "24_2357"}),
    ("arithmetique", {"preset": "24_3388"}),
    ("arithmetique", {"preset": "24_impossible"}),
    ("arithmetique", {"preset": "compte_est_bon"}),
    ("equation", {"preset": "deux_membres"}),
    ("equation", {"preset": "fractions"}),
]

HEURISTIC_RUNS = [
    ("npuzzle", {"preset": "moyen"}, ["zero", "mal_placees", "manhattan", "conflits_lineaires"]),
    ("npuzzle", {"preset": "difficile"}, ["zero", "mal_placees", "manhattan", "conflits_lineaires"]),
    ("npuzzle", {"preset": "15_facile"}, ["mal_placees", "manhattan", "conflits_lineaires"]),
    ("labyrinthe", {"preset": "complexe"}, ["zero", "manhattan", "euclidienne"]),
    ("labyrinthe", {"preset": "portails"}, ["zero", "manhattan", "manhattan_naif"]),
    ("labyrinthe", {"preset": "diagonal"}, ["zero", "octile", "manhattan"]),
    ("navigation", {"start": "Rouyn-Noranda", "goal": "Gaspé"}, ["zero", "longitude", "vol_oiseau", "vol_oiseau_x2"]),
    ("arithmetique", {"preset": "24_3388"}, ["zero", "operations_restantes", "ecart_cible"]),
]

FIELDS = ["probleme", "strategie", "mode", "heuristique", "statut", "cout", "profondeur",
          "generes", "developpes", "max_open", "max_memoire", "temps_s", "b_effectif", "message"]


def _row(problem, res, strategy, mode):
    s = res.stats
    return {
        "probleme": problem.summary(), "strategie": strategy, "mode": mode,
        "heuristique": res.heuristic or "-", "statut": res.status, "cout": res.cost,
        "profondeur": res.depth, "generes": s.generated, "developpes": s.expanded,
        "max_open": s.max_frontier, "max_memoire": s.max_memory_nodes,
        "temps_s": round(s.time_s, 4), "b_effectif": s.effective_branching, "message": res.message,
    }


def run_strategies(limits: Limits, log=print) -> list[dict]:
    rows = []
    for name, params in INSTANCES:
        for strategy in STRATEGIES:
            for mode in MODES:
                problem = build_problem(name, params)
                res = search(problem, strategy, mode, limits)
                rows.append(_row(problem, res, strategy, mode))
                log(f"  {problem.summary():45.45} {strategy:6} {mode:5} {res.status:6} "
                    f"coût={res.cost} dév={res.stats.expanded} t={res.stats.time_s:.3f}s")
    return rows


def run_heuristics(limits: Limits, log=print) -> list[dict]:
    rows = []
    for name, params, hs in HEURISTIC_RUNS:
        for h in hs:
            problem = build_problem(name, params, h)
            res = search(problem, "astar", "graph", limits)
            rows.append(_row(problem, res, "astar", "graph"))
            log(f"  {problem.summary():45.45} h={h:22} {res.status:6} coût={res.cost} dév={res.stats.expanded}")
    return rows


def _write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def _n(x):
    if x is None or x == "":
        return "—"
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    if isinstance(x, float):
        return f"{x:,.3f}".replace(",", " ") if x < 10 else f"{x:,.1f}".replace(",", " ")
    return f"{x:,}".replace(",", " ")


def summarize(rows: list[dict]) -> str:
    """Synthèse par (stratégie, mode) sur les instances ayant une solution."""
    by_problem: dict[str, list[dict]] = {}
    for r in rows:
        by_problem.setdefault(r["probleme"], []).append(r)
    # instance soluble = au moins une exécution a trouvé une solution ;
    # coût optimal connu = meilleur coût trouvé par UCS ou A* (tous deux optimaux)
    solvable = {p for p, rs in by_problem.items() if any(r["statut"] == "succes" for r in rs)}
    ref = {}
    for p, rs in by_problem.items():
        opt = [r["cout"] for r in rs if r["statut"] == "succes" and r["strategie"] in ("ucs", "astar")]
        ref[p] = min(opt) if opt else None
    known = [p for p in ref if ref[p] is not None]

    out = ["| Stratégie | Mode | Résolues | Optimales | Arrêts (limite) | Développés (médiane) | Max mémoire (médiane) | Temps total (s) |",
           "|---|---|---:|---:|---:|---:|---:|---:|"]
    for st in STRATEGIES:
        for mode in MODES:
            rs = [r for r in rows if r["strategie"] == st and r["mode"] == mode]
            ok = [r for r in rs if r["statut"] == "succes"]
            optimal = [r for r in ok if r["probleme"] in known and abs(r["cout"] - ref[r["probleme"]]) < 1e-6]
            cut = [r for r in rs if r["statut"] == "arret"]
            med_exp = statistics.median([r["developpes"] for r in ok]) if ok else None
            med_mem = statistics.median([r["max_memoire"] for r in ok]) if ok else None
            out.append(f"| {st} | {mode} | {len(ok)}/{len(solvable)} | {len(optimal)}/{len(known)} | {len(cut)} "
                       f"| {_n(med_exp)} | {_n(med_mem)} | {sum(r['temps_s'] for r in rs):.2f} |")
    return "\n".join(out)


def table(rows: list[dict], cols: list[str]) -> str:
    head = "| " + " | ".join(cols) + " |"
    sep = "|" + "|".join("---" if c in ("probleme", "strategie", "mode", "heuristique", "statut") else "---:"
                         for c in cols) + "|"
    body = ["| " + " | ".join(_n(r[c]) if isinstance(r[c], (int, float)) and not isinstance(r[c], bool)
                              else str(r[c] if r[c] is not None else "—") for c in cols) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def main(time_limit: float = 3.0, memory: int = 500_000, out_dir: str = "resultats"):
    limits = Limits(max_time=time_limit, max_memory_nodes=memory)
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    print(f"Expérience 1 — stratégies × modes (limites : {time_limit} s, {memory:,} nœuds)")
    srows = run_strategies(limits)
    print("Expérience 2 — heuristiques (A*, Graph-Search)")
    hrows = run_heuristics(limits)
    _write_csv(out / "strategies.csv", srows)
    _write_csv(out / "heuristiques.csv", hrows)

    cols = ["probleme", "strategie", "mode", "statut", "cout", "profondeur", "generes",
            "developpes", "max_open", "max_memoire", "temps_s"]
    md = [
        "# AUSSI — résultats de l'expérience comparative",
        "",
        f"Limites par exécution : {time_limit} s, {memory:,} nœuds en mémoire. "
        "« arret » = AUSSI s'est mis en arrêt de travail (limite atteinte). "
        "Temps mesurés sur une seule exécution : ordre de grandeur seulement.",
        "",
        "## Synthèse par stratégie et mode",
        "",
        f"{len(INSTANCES)} instances. « Résolues » : sur les instances dont une solution a été trouvée par au moins "
        "une stratégie. « Optimales » : coût égal au coût optimal (UCS/A*), sur les instances où ce coût est connu.",
        "",
        summarize(srows),
        "",
        "## Expérience 2 — influence de l'heuristique (A*, Graph-Search)",
        "",
        table(hrows, ["probleme", "heuristique", "statut", "cout", "developpes", "max_memoire", "temps_s", "b_effectif"]),
        "",
        "## Détail — toutes les exécutions",
        "",
        table(srows, cols),
        "",
    ]
    (out / "RESULTATS.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nRésultats écrits dans {out.resolve()}")
    return srows, hrows
