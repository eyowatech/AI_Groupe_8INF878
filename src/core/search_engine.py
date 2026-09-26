import heapq
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, Set, Tuple, TypeVar

# Types génériques pour les états et les actions
S = TypeVar("S")  # State
A = TypeVar("A")  # Action


class SearchEngine:
    """Moteur de recherche générique unifié."""

    @staticmethod
    def search(
        problem: Problem[S, A], strategy: str, mode: str = "graph"
    ) -> Tuple[Optional[Node], SearchMetrics]:
        """
        Fonction unifiée SEARCH(problem, strategy, mode)
        Mode : 'tree' ou 'graph'
        Stratégie : 'bfs', 'ucs', 'greedy', 'astar'
        """
        start_time = time.perf_counter()
        metrics = SearchMetrics()

        root = Node.create_root(problem.get_start_state())

        # Initialisation de la frontière (OPEN)
        # Pour BFS, on utilise une deque pour respecter le FIFO strict
        if strategy == "bfs":
            open_container = deque([root])
        else:
            open_container = []
            heapq.heappush(open_container, root)

        metrics.nodes_generated = 1
        metrics.max_open_size = 1

        explored: Set[Any] = set()

        while open_container:
            # Mise à jour de la métrique de taille max de OPEN
            current_open_size = len(open_container)
            if current_open_size > metrics.max_open_size:
                metrics.max_open_size = current_open_size

            # Extraction du prochain nœud selon la structure de données
            if strategy == "bfs":
                current_node = open_container.popleft()
            else:
                current_node = heapq.heappop(open_container)

            # Test de but
            if problem.is_goal(current_node.state):
                metrics.execution_time_sec = time.perf_counter() - start_time
                return current_node, metrics

            # Gestion du mode Graph-Search (évite les boucles)
            if mode == "graph":
                # L'état doit être hashable (tuple, frozenset, etc.)
                state_key = current_node.state
                if state_key in explored:
                    continue
                explored.add(state_key)

            metrics.nodes_expanded += 1

            # Expansion des successeurs
            successors = current_node.expand(problem, strategy)
            for succ in successors:
                metrics.nodes_generated += 1
                if strategy == "bfs":
                    open_container.append(succ)
                else:
                    heapq.heappush(open_container, succ)

        # Si aucun plan n'est trouvé
        metrics.execution_time_sec = time.perf_counter() - start_time
        return None, metrics
