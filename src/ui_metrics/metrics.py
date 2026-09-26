import heapq
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, Set, Tuple, TypeVar

# Types génériques pour les états et les actions
S = TypeVar("S")  # State
A = TypeVar("A")  # Action


@dataclass
class SearchMetrics:
    """Gère l'observabilité et les métriques du moteur de recherche."""

    nodes_generated: int = 0
    nodes_expanded: int = 0
    max_open_size: int = 0
    execution_time_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes_generated": self.nodes_generated,
            "nodes_expanded": self.nodes_expanded,
            "max_open_size": self.max_open_size,
            "time_sec": round(self.execution_time_sec, 4),
        }
