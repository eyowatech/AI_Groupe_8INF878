from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

# Types génériques pour les états et les actions
S = TypeVar("S")  # State
A = TypeVar("A")  # Action


class Problem(ABC, Generic[S, A]):
    """Interface abstraite (Contrat) que tout problème doit implémenter."""

    @abstractmethod
    def get_start_state(self) -> S:
        pass

    @abstractmethod
    def is_goal(self, state: S) -> bool:
        pass

    @abstractmethod
    def get_actions(self, state: S) -> List[A]:
        pass

    @abstractmethod
    def result(self, state: S, action: A) -> S:
        pass

    @abstractmethod
    def path_cost(self, c: float, state1: S, action: A, state2: S) -> float:
        pass

    def heuristic(self, state: S) -> float:
        """Heuristique par défaut (0 pour UCS/BFS)."""
        return 0.0
