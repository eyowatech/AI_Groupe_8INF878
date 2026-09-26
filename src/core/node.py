import heapq
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, Set, Tuple, TypeVar

# Types génériques pour les états et les actions
S = TypeVar("S")  # State
A = TypeVar("A")  # Action


@dataclass(order=True)
class Node(Generic[S, A]):
    """Représente un nœud dans l'espace de recherche."""

    priority: float
    cost: float = field(compare=False)
    state: S = field(compare=False)
    parent: Optional["Node[S, A]"] = field(compare=False, default=None)
    action: Optional[A] = field(compare=False, default=None)
    depth: int = field(compare=False, default=0)

    @classmethod
    def create_root(cls, state: S) -> "Node[S, A]":
        return cls(priority=0.0, cost=0.0, state=state, depth=0)

    def expand(self, problem: Problem[S, A], strategy: str) -> List["Node[S, A]"]:
        """Génère les nœuds successeurs."""
        successors = []
        for action in problem.get_actions(self.state):
            next_state = problem.result(self.state, action)
            new_cost = problem.path_cost(self.cost, self.state, action, next_state)
            new_depth = self.depth + 1

            # Calcul de la priorité selon la stratégie
            priority = self._calculate_priority(problem, next_state, new_cost, strategy)

            node = Node(
                priority=priority,
                cost=new_cost,
                state=next_state,
                parent=self,
                action=action,
                depth=new_depth,
            )
            successors.append(node)
        return successors

    def _calculate_priority(
        self, problem: Problem[S, A], state: S, cost: float, strategy: str
    ) -> float:
        if strategy == "bfs":
            return self.depth + 1  # FIFO géré via compteur externe ou profondeur
        elif strategy == "ucs":
            return cost
        elif strategy == "greedy":
            return problem.heuristic(state)
        elif strategy == "astar":
            return cost + problem.heuristic(state)
        raise ValueError(f"Stratégie inconnue : {strategy}")

    def extract_path(self) -> Tuple[List[A], List[S]]:
        """Remonte l'arbre pour extraire le plan d'actions et les états."""
        actions = []
        states = [self.state]
        node = self
        while node.parent is not None:
            actions.append(node.action)
            states.append(node.parent.state)
            node = node.parent
        actions.reverse()
        states.reverse()
        return actions, states
