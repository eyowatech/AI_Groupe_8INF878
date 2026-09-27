"""Stratégies d'exploration.

Une stratégie n'est qu'une FONCTION DE PRIORITÉ sur les nœuds de la frontière
(plus petit = développé en premier). Le moteur `search` est unique ; BFS, UCS,
Greedy et A* ne diffèrent que par cette fonction.

Ajouter une stratégie = écrire une petite classe et la décorer avec
`@register`. Voir DFS et Weighted A* en bas du fichier : 5 lignes chacune.
"""

from __future__ import annotations

from typing import Any

STRATEGIES: dict[str, "Strategy"] = {}


def register(cls):
    STRATEGIES[cls.name] = cls()
    return cls


def get_strategy(name: "str | Strategy") -> "Strategy":
    if isinstance(name, Strategy):
        return name
    try:
        return STRATEGIES[name.lower()]
    except KeyError:
        raise ValueError(
            f"Stratégie inconnue '{name}'. Choix : {', '.join(STRATEGIES)}"
        ) from None


class Strategy:
    name = "abstraite"
    label = "Stratégie abstraite"
    #: la stratégie a-t-elle besoin de h(n) ? (évite de la calculer sinon)
    uses_heuristic = False
    #: tester le but à la génération plutôt qu'à l'expansion (BFS classique)
    early_goal_test = False
    #: Graph-Search : rouvrir un état déjà atteint si un chemin de coût g
    #: inférieur est trouvé (UCS, A*...). Sinon la première atteinte gagne (BFS).
    reopen = True

    def priority(self, node, order: int) -> Any:
        """`order` = numéro d'insertion dans la frontière (0, 1, 2, ...)."""
        raise NotImplementedError

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "uses_heuristic": self.uses_heuristic,
            "doc": (self.__doc__ or "").strip(),
        }


@register
class BreadthFirst(Strategy):
    """File FIFO : développe le nœud le moins profond. Optimal si coûts uniformes."""
    name, label = "bfs", "Largeur d'abord (BFS)"
    early_goal_test = True
    reopen = False

    def priority(self, node, order):
        return order  # premier entré, premier sorti


@register
class UniformCost(Strategy):
    """Développe le nœud de coût g(n) minimal. Optimal pour coûts positifs."""
    name, label = "ucs", "Coût uniforme (UCS)"

    def priority(self, node, order):
        return node.g


@register
class Greedy(Strategy):
    """Développe le nœud qui semble le plus proche du but : h(n). Non optimal."""
    name, label = "greedy", "Glouton (Greedy best-first)"
    uses_heuristic = True

    def priority(self, node, order):
        return node.h


@register
class AStar(Strategy):
    """f(n) = g(n) + h(n). Optimal si h admissible (tree) / consistante (graph)."""
    name, label = "astar", "A*"
    uses_heuristic = True

    def priority(self, node, order):
        # à f égal, on préfère le nœud le plus avancé (h plus petit)
        return (node.g + node.h, node.h)


# ---------------------------------------------------------------------- #
# Extensions : démonstration qu'une stratégie s'ajoute en quelques lignes
# ---------------------------------------------------------------------- #
@register
class DepthFirst(Strategy):
    """Pile LIFO : développe le nœud le plus récent. Ni complet ni optimal."""
    name, label = "dfs", "Profondeur d'abord (DFS) — extension"
    early_goal_test = True
    reopen = False

    def priority(self, node, order):
        return -order


@register
class WeightedAStar(Strategy):
    """f(n) = g(n) + w·h(n), w = 2. Plus rapide, coût ≤ w × optimal."""
    name, label = "wastar", "Weighted A* (w=2) — extension"
    uses_heuristic = True
    weight = 2.0

    def priority(self, node, order):
        return (node.g + self.weight * node.h, node.h)
