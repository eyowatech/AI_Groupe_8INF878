"""Couche d'API d'AUSSI : tout passe par des dictionnaires JSON.

L'interface web, la ligne de commande et les expériences appellent
uniquement `catalog()`, `solve()`, `compare()` et `check()`. Un LLM pourra
remplacer l'interface en appelant ces mêmes fonctions comme « outils » :
`tool_definitions()` fournit leur description au format JSON Schema.

Ajouter un problème = l'enregistrer dans PROBLEMS ; rien d'autre ne change.
"""

from __future__ import annotations

from .core import search, check_heuristic, Limits, STRATEGIES, MODES
from .problems import maze, navigation, npuzzle, arithmetic, equation

PROBLEMS = {
    "labyrinthe": {
        "label": "Labyrinthe", "module": maze, "cls": maze.Maze,
        "description": "Trouver un chemin de S à G dans une grille avec murs, terrains à coût variable et portails.",
        "params": {
            "preset": {"type": "string", "enum": list(maze.PRESETS), "default": "simple", "description": "instance prédéfinie"},
            "grid": {"type": "string", "description": "grille texte personnalisée (# mur, S, G, . : ~ ^ terrains, 1-9 portails)"},
            "diagonal": {"type": "boolean", "description": "autoriser les 8 directions"},
        },
    },
    "navigation": {
        "label": "Navigation (mini Google Maps)", "module": navigation, "cls": navigation.RoadMap,
        "description": "Itinéraire le plus court entre deux villes du Québec sur un réseau routier pondéré (km).",
        "params": {
            "start": {"type": "string", "enum": sorted(navigation.CITIES), "default": "Chicoutimi", "description": "ville de départ"},
            "goal": {"type": "string", "enum": sorted(navigation.CITIES), "default": "Montréal", "description": "ville d'arrivée"},
        },
    },
    "npuzzle": {
        "label": "N-Puzzle", "module": npuzzle, "cls": npuzzle.NPuzzle,
        "description": "Remettre en ordre les tuiles d'un taquin n×n (0 = case vide).",
        "params": {
            "preset": {"type": "string", "enum": list(npuzzle.PRESETS), "default": "facile", "description": "instance prédéfinie"},
            "tiles": {"type": "string", "description": "tuiles ligne par ligne, ex. '1 2 3 4 5 6 0 7 8'"},
            "size": {"type": "integer", "description": "taille n pour un mélange aléatoire"},
            "scramble": {"type": "integer", "description": "nombre de coups de mélange aléatoire"},
            "seed": {"type": "integer", "description": "graine du mélange"},
        },
    },
    "arithmetique": {
        "label": "Jeu arithmétique (24 / compte est bon)", "module": arithmetic, "cls": arithmetic.Arithmetic,
        "description": "Combiner des nombres avec + − × ÷ pour atteindre une cible ; trace du raisonnement.",
        "params": {
            "preset": {"type": "string", "enum": list(arithmetic.PRESETS), "default": "24_2357", "description": "instance prédéfinie"},
            "numbers": {"type": "string", "description": "nombres séparés par des espaces, ex. '2 3 5 7'"},
            "target": {"type": "number", "description": "valeur cible"},
            "use_all": {"type": "boolean", "description": "obliger à utiliser tous les nombres"},
        },
    },
    "equation": {
        "label": "Équation linéaire", "module": equation, "cls": equation.LinearEquation,
        "description": "Résoudre a·x + b = c·x + d par transformations algébriques successives.",
        "params": {
            "preset": {"type": "string", "enum": list(equation.PRESETS), "default": "simple", "description": "instance prédéfinie"},
            "equation": {"type": "string", "description": "équation, ex. '5x - 7 = 2x + 8'"},
        },
    },
}

COMPARE_STRATEGIES = ["bfs", "ucs", "greedy", "astar"]


def catalog() -> dict:
    return {
        "problems": {
            name: {
                "label": spec["label"],
                "description": spec["description"],
                "params": spec["params"],
                "presets": getattr(spec["module"], "PRESETS", {}),
                "heuristics": spec["cls"].heuristics,
                "default_heuristic": spec["cls"].default_heuristic,
            }
            for name, spec in PROBLEMS.items()
        },
        "strategies": {k: s.to_dict() for k, s in STRATEGIES.items()},
        "modes": {"graph": "Graph-Search (mémorise les états atteints)",
                  "tree": "Tree-Search (aucune mémoire des états répétés)"},
        "limits": Limits().__dict__,
    }


def build_problem(name: str, params: dict | None = None, heuristic: str | None = None):
    if name not in PROBLEMS:
        raise ValueError(f"Problème inconnu '{name}'. Choix : {', '.join(PROBLEMS)}")
    params = dict(params or {})
    if heuristic:
        params["heuristic"] = heuristic
    return PROBLEMS[name]["module"].from_params(params)


def solve(req: dict) -> dict:
    """req = {problem, params?, strategy?, mode?, heuristic?, limits?}"""
    problem = build_problem(req["problem"], req.get("params"), req.get("heuristic"))
    res = search(problem, req.get("strategy", "astar"), req.get("mode", "graph"), req.get("limits"))
    out = res.to_dict()
    out["report"] = res.report()
    out["meta"] = problem.view_meta()
    out["initial"] = problem.render(problem.initial_state)
    if res.found:
        final = res.goal_node.state
        out["final"] = problem.render(final)
        if hasattr(problem, "solution_expression"):
            out["expression"] = problem.solution_expression(final)
    return out


def compare(req: dict) -> dict:
    """Toutes les stratégies × modes sur le même problème (même heuristique)."""
    rows = []
    for strategy in req.get("strategies", COMPARE_STRATEGIES):
        for mode in req.get("modes", MODES):
            problem = build_problem(req["problem"], req.get("params"), req.get("heuristic"))
            r = search(problem, strategy, mode, req.get("limits"))
            rows.append({
                "strategy": strategy, "mode": mode, "status": r.status, "message": r.message,
                "cost": r.cost, "depth": r.depth, **r.stats.__dict__,
            })
    problem = build_problem(req["problem"], req.get("params"), req.get("heuristic"))
    return {"problem": problem.summary(), "heuristic": problem.heuristic_name, "rows": rows}


def check(req: dict) -> dict:
    problem = build_problem(req["problem"], req.get("params"), req.get("heuristic"))
    return check_heuristic(problem, max_states=int(req.get("max_states", 20_000)))


def tool_definitions() -> list[dict]:
    """Descriptions d'outils prêtes pour un LLM (format « tools » de l'API Claude)."""
    cat = catalog()
    problem_desc = "; ".join(f"{k}: {v['description']} Paramètres: "
                             + ", ".join(v["params"]) for k, v in cat["problems"].items())
    common = {
        "problem": {"type": "string", "enum": list(PROBLEMS), "description": problem_desc},
        "params": {"type": "object", "description": "paramètres propres au problème (voir description)"},
        "heuristic": {"type": "string", "description": "nom d'une heuristique du problème (optionnel)"},
    }
    return [
        {
            "name": "aussi_solve",
            "description": "Résout un problème avec une stratégie et un mode donnés ; renvoie solution, coût, profondeur et statistiques.",
            "input_schema": {"type": "object", "required": ["problem"], "properties": {
                **common,
                "strategy": {"type": "string", "enum": list(STRATEGIES)},
                "mode": {"type": "string", "enum": list(MODES)},
                "limits": {"type": "object", "description": "max_time (s), max_memory_nodes, max_expanded, max_depth"},
            }},
        },
        {
            "name": "aussi_compare",
            "description": "Compare BFS, UCS, Greedy et A* en Tree- et Graph-Search sur un même problème.",
            "input_schema": {"type": "object", "required": ["problem"], "properties": common},
        },
        {
            "name": "aussi_check_heuristic",
            "description": "Vérifie empiriquement qu'une heuristique est admissible et consistante.",
            "input_schema": {"type": "object", "required": ["problem"], "properties": common},
        },
    ]


TOOLS = {"aussi_solve": solve, "aussi_compare": compare, "aussi_check_heuristic": check}
