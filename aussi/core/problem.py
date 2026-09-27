"""Formulation abstraite d'un problème de recherche.

C'est le SEUL contrat entre AUSSI et un problème : le moteur de recherche ne
connaît que ces méthodes. Pour ajouter un nouveau problème, on hérite de
`Problem` et on implémente les méthodes abstraites ; aucun algorithme n'est
modifié.

Heuristiques : une sous-classe déclare `heuristics = {"nom": "description"}`
et fournit une méthode `h_<nom>(state)` pour chacune. On peut aussi injecter
une fonction quelconque avec `set_heuristic(callable)`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Hashable, Iterable


class Problem(ABC):
    #: identifiant court du problème (utilisé par le registre / l'interface)
    name: str = "probleme"
    #: heuristiques disponibles : nom -> description
    heuristics: dict[str, str] = {"zero": "h(n) = 0 (aucune information)"}
    #: heuristique utilisée si aucune n'est précisée
    default_heuristic: str = "zero"

    def __init__(self, heuristic: str | Callable[[Any], float] | None = None):
        self.set_heuristic(heuristic)

    # ------------------------------------------------------------------ #
    # Formulation (à implémenter)
    # ------------------------------------------------------------------ #
    @property
    @abstractmethod
    def initial_state(self) -> Any: ...

    @abstractmethod
    def actions(self, state) -> Iterable[Any]: ...

    @abstractmethod
    def result(self, state, action) -> Any: ...

    @abstractmethod
    def is_goal(self, state) -> bool: ...

    def step_cost(self, state, action, next_state) -> float:
        return 1

    def state_key(self, state) -> Hashable:
        """Clé utilisée pour détecter les états répétés (Graph-Search).

        Par défaut l'état lui-même ; un problème peut regrouper des états
        équivalents (ex. : même multiensemble de nombres au jeu du 24)."""
        return state

    def precheck(self) -> str | None:
        """Analyse optionnelle avant la recherche. Retourne une raison si l'on
        peut PROUVER qu'il n'existe aucune solution (ex. parité du N-Puzzle)."""
        return None

    # ------------------------------------------------------------------ #
    # Heuristique
    # ------------------------------------------------------------------ #
    def set_heuristic(self, heuristic: str | Callable[[Any], float] | None):
        if heuristic is None:
            heuristic = self.default_heuristic
        if callable(heuristic):
            self.heuristic_name = getattr(heuristic, "__name__", "personnalisee")
            self._h = heuristic
            return
        if heuristic not in self.heuristics:
            raise ValueError(
                f"Heuristique inconnue '{heuristic}' pour {self.name}. "
                f"Choix : {', '.join(self.heuristics)}"
            )
        self.heuristic_name = heuristic
        self._h = getattr(self, f"h_{heuristic}")

    def h(self, state) -> float:
        return self._h(state)

    def h_zero(self, state) -> float:
        return 0

    # ------------------------------------------------------------------ #
    # Présentation (valeurs par défaut raisonnables)
    # ------------------------------------------------------------------ #
    def describe_action(self, state, action, next_state) -> str:
        return str(action)

    def render(self, state) -> str:
        return str(state)

    def to_view(self, state) -> Any:
        """Représentation JSON d'un état pour l'interface graphique."""
        return self.render(state)

    def view_meta(self) -> dict:
        """Données statiques pour l'affichage (grille, carte, ...)."""
        return {}

    def summary(self) -> str:
        return self.name
