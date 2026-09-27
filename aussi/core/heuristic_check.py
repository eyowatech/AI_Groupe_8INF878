"""Vérification empirique d'une heuristique (générique, pour tout Problem).

- Consistance : pour chaque arc exploré s -a-> s', h(s) <= c(s,a,s') + h(s'),
  et h(but) = 0. Consistance + h(but)=0  =>  admissibilité.
- Admissibilité : on calcule une solution optimale avec UCS et on vérifie
  h(n) <= C* - g(n) pour chaque nœud n du chemin optimal.

C'est un test (sur un échantillon d'états), pas une preuve ; il sert à
détecter rapidement une heuristique modifiée qui serait fautive.
"""

from __future__ import annotations

from collections import deque

from .problem import Problem
from .search import search, Limits

EPS = 1e-6


def check_heuristic(problem: Problem, max_states: int = 20_000, max_examples: int = 5) -> dict:
    start = problem.initial_state
    seen = {problem.state_key(start)}
    queue = deque([start])
    edges = 0
    consistency_violations, goal_violations = [], []

    while queue and len(seen) < max_states:
        s = queue.popleft()
        hs = problem.h(s)
        if problem.is_goal(s) and abs(hs) > EPS:
            goal_violations.append({"etat": problem.render(s), "h": hs})
        for a in problem.actions(s):
            s2 = problem.result(s, a)
            c = problem.step_cost(s, a, s2)
            edges += 1
            hs2 = problem.h(s2)
            if hs > c + hs2 + EPS and len(consistency_violations) < max_examples:
                consistency_violations.append({
                    "arc": problem.describe_action(s, a, s2),
                    "h(s)": round(hs, 3), "c": round(c, 3), "h(s')": round(hs2, 3),
                })
            k = problem.state_key(s2)
            if k not in seen:
                seen.add(k)
                queue.append(s2)

    admissibility_violations, optimal_cost = [], None
    ref = search(problem, "ucs", "graph", Limits(max_time=5, max_memory_nodes=max_states * 20))
    if ref.found:
        optimal_cost = ref.goal_node.g
        for n in ref.goal_node.path():
            h_true = optimal_cost - n.g
            hn = problem.h(n.state)
            if hn > h_true + EPS and len(admissibility_violations) < max_examples:
                admissibility_violations.append({
                    "etat": problem.render(n.state), "h": round(hn, 3), "h*": round(h_true, 3)})

    consistent = not consistency_violations and not goal_violations
    return {
        "heuristique": problem.heuristic_name,
        "etats_examines": len(seen),
        "arcs_examines": edges,
        "exhaustif": not queue,
        "consistante": consistent,
        "admissible_sur_chemin_optimal": None if optimal_cost is None else not admissibility_violations,
        "cout_optimal_reference": None if optimal_cost is None else round(optimal_cost, 6),
        "violations_consistance": consistency_violations,
        "violations_but": goal_violations[:max_examples],
        "violations_admissibilite": admissibility_violations,
        "conclusion": _conclusion(consistent, admissibility_violations, not queue),
    }


def _conclusion(consistent, adm_viol, exhaustive) -> str:
    scope = "sur tout l'espace d'états" if exhaustive else "sur l'échantillon exploré"
    if consistent:
        return f"Consistante (donc admissible) {scope} : A* en Graph-Search reste optimal."
    if not adm_viol:
        return (f"NON consistante {scope}, mais aucune surestimation détectée sur le chemin "
                "optimal : A* en Tree-Search reste optimal ; en Graph-Search, la réouverture "
                "des états d'AUSSI préserve l'optimalité au prix de plus d'expansions.")
    return "NON admissible : elle surestime le coût restant. A* peut rendre une solution sous-optimale."
