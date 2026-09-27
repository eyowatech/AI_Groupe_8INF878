"""Moteur générique : SEARCH(problem, strategy, mode).

Un seul algorithme de recherche « meilleur d'abord ». La stratégie fournit la
priorité des nœuds ; le mode choisit Tree-Search (aucune mémoire des états
visités) ou Graph-Search (table `reached` : état -> meilleur coût g connu,
comme BEST-FIRST-SEARCH dans Russell & Norvig, 4e éd.).

Garde-fous (« arrêt de travail ») : temps, nœuds en mémoire, nœuds développés
et profondeur maximale. Si une limite est atteinte, AUSSI s'arrête proprement
et le dit, au lieu de saturer la mémoire.
"""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field, asdict
from .problem import Problem
from .strategies import Strategy, get_strategy

SUCCESS, FAILURE, CUTOFF = "succes", "echec", "arret"
MODES = ("graph", "tree")


class Node:
    __slots__ = ("state", "parent", "action", "g", "depth", "h")

    def __init__(self, state, parent=None, action=None, g=0.0, h=0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.depth = parent.depth + 1 if parent else 0
        self.h = h

    def path(self) -> list["Node"]:
        node, out = self, []
        while node is not None:
            out.append(node)
            node = node.parent
        return out[::-1]


@dataclass
class Limits:
    max_time: float | None = 10.0  # secondes
    max_memory_nodes: int | None = 2_000_000  # |frontière| + |reached|
    max_expanded: int | None = None
    max_depth: int | None = None

    @classmethod
    def from_dict(cls, d: dict | None) -> "Limits":
        d = d or {}
        known = {k: d[k] for k in cls.__dataclass_fields__ if k in d}
        return cls(**known)


@dataclass
class Stats:
    generated: int = 0
    expanded: int = 0
    max_frontier: int = 0
    max_memory_nodes: int = 0
    time_s: float = 0.0
    effective_branching: float | None = None


@dataclass
class SearchResult:
    status: str
    message: str
    problem: str
    strategy: str
    mode: str
    heuristic: str | None
    cost: float | None = None
    depth: int | None = None
    steps: list[dict] = field(default_factory=list)
    stats: Stats = field(default_factory=Stats)

    @property
    def found(self) -> bool:
        return self.status == SUCCESS

    def to_dict(self) -> dict:
        d = asdict(self)
        d["found"] = self.found
        return d

    def report(self, max_steps: int = 40) -> str:
        s = self.stats
        lines = [
            f"Problème   : {self.problem}",
            f"Stratégie  : {self.strategy}   Mode : {self.mode}"
            + (f"   Heuristique : {self.heuristic}" if self.heuristic else ""),
            f"Résultat   : {self.message}",
        ]
        if self.found:
            lines.append(f"Coût       : {_fmt(self.cost)}   Profondeur : {self.depth}")
        lines += [
            f"Nœuds générés : {s.generated}   développés : {s.expanded}",
            f"Taille max OPEN : {s.max_frontier}   max en mémoire : {s.max_memory_nodes}",
            f"Temps : {s.time_s:.3f} s"
            + (f"   b* ≈ {s.effective_branching:.2f}" if s.effective_branching else ""),
        ]
        if self.found:
            lines.append("Solution :")
            shown = self.steps[1:]
            if len(shown) > max_steps:
                head, tail = shown[: max_steps // 2], shown[-max_steps // 2:]
                shown = head + [None] + tail
            for st in shown:
                if st is None:
                    lines.append("   ...")
                else:
                    lines.append(f"  {st['depth']:>3}. {st['action']}   (g = {_fmt(st['g'])})")
        return "\n".join(lines)


def _fmt(x):
    if x is None:
        return "-"
    return str(int(x)) if float(x).is_integer() else f"{x:.2f}"


def effective_branching_factor(n_generated: int, depth: int) -> float | None:
    """b* tel que N + 1 = 1 + b* + b*² + ... + b*^d (R&N)."""
    if depth <= 0 or n_generated <= depth:
        return None
    target = n_generated + 1
    lo, hi = 1.0, float(n_generated)
    for _ in range(60):
        mid = (lo + hi) / 2
        total, term = 1.0, 1.0
        for _ in range(depth):
            term *= mid
            total += term
            if total >= target:
                break
        lo, hi = (mid, hi) if total < target else (lo, mid)
    return round((lo + hi) / 2, 3)


def search(
    problem: Problem,
    strategy: str | Strategy = "astar",
    mode: str = "graph",
    limits: Limits | dict | None = None,
    use_precheck: bool = True,
) -> SearchResult:
    """SEARCH(problem, strategy, mode) — le seul algorithme d'AUSSI."""
    strategy = get_strategy(strategy)
    if mode not in MODES:
        raise ValueError(f"Mode inconnu '{mode}'. Choix : {', '.join(MODES)}")
    if not isinstance(limits, Limits):
        limits = Limits.from_dict(limits)
    graph = mode == "graph"
    use_h = strategy.uses_heuristic
    stats = Stats()
    t0 = time.perf_counter()

    def finish(status, message, node=None) -> SearchResult:
        stats.time_s = time.perf_counter() - t0
        res = SearchResult(
            status, message, problem.summary(), strategy.label, mode,
            problem.heuristic_name if use_h else None, stats=stats,
        )
        res.goal_node = node  # hors JSON : accès programmatique au chemin
        if node is not None:
            res.cost, res.depth = round(node.g, 6), node.depth
            res.steps = _steps(problem, node)
            stats.effective_branching = effective_branching_factor(stats.generated, node.depth)
        return res

    if use_precheck:
        reason = problem.precheck()
        if reason:
            return finish(FAILURE, f"Aucune solution (analyse préalable) : {reason}")

    root_state = problem.initial_state
    root = Node(root_state, h=problem.h(root_state) if use_h else 0)
    stats.generated = 1
    if strategy.early_goal_test and problem.is_goal(root_state):
        return finish(SUCCESS, "Solution trouvée", root)

    frontier: list = []
    order = 0
    heapq.heappush(frontier, (strategy.priority(root, order), order, root))
    reached: dict = {problem.state_key(root_state): 0} if graph else {}
    depth_pruned = False

    try:
        while frontier:
            _, _, node = heapq.heappop(frontier)
            if graph and node.g > reached[problem.state_key(node.state)]:
                continue  # entrée périmée : un meilleur chemin a été trouvé depuis
            if not strategy.early_goal_test and problem.is_goal(node.state):
                return finish(SUCCESS, "Solution trouvée", node)

            # --- garde-fous -------------------------------------------------
            stats.expanded += 1
            mem = len(frontier) + len(reached)
            if limits.max_memory_nodes and mem > limits.max_memory_nodes:
                return finish(CUTOFF, f"Arrêt de travail : limite mémoire atteinte "
                                      f"({limits.max_memory_nodes:,} nœuds en mémoire)")
            if limits.max_expanded and stats.expanded > limits.max_expanded:
                return finish(CUTOFF, f"Arrêt de travail : {limits.max_expanded:,} nœuds développés")
            if limits.max_time and stats.expanded % 256 == 0 \
                    and time.perf_counter() - t0 > limits.max_time:
                return finish(CUTOFF, f"Arrêt de travail : temps limite de {limits.max_time} s dépassé")
            if limits.max_depth is not None and node.depth >= limits.max_depth:
                depth_pruned = True
                continue

            # --- expansion --------------------------------------------------
            for action in problem.actions(node.state):
                s2 = problem.result(node.state, action)
                g2 = node.g + problem.step_cost(node.state, action, s2)
                stats.generated += 1
                if graph:
                    key = problem.state_key(s2)
                    if key in reached and (not strategy.reopen or reached[key] <= g2):
                        continue
                    reached[key] = g2
                child = Node(s2, node, action, g2, problem.h(s2) if use_h else 0)
                if strategy.early_goal_test and problem.is_goal(s2):
                    return finish(SUCCESS, "Solution trouvée", child)
                order += 1
                heapq.heappush(frontier, (strategy.priority(child, order), order, child))

            if len(frontier) > stats.max_frontier:
                stats.max_frontier = len(frontier)
            if mem > stats.max_memory_nodes:
                stats.max_memory_nodes = mem
    except MemoryError:
        frontier.clear()
        reached.clear()
        return finish(CUTOFF, "Arrêt de travail : mémoire de la machine épuisée")

    if depth_pruned:
        return finish(CUTOFF, f"Aucune solution jusqu'à la profondeur {limits.max_depth}")
    return finish(FAILURE, "Aucune solution : espace d'états entièrement exploré")


def _steps(problem: Problem, goal: Node) -> list[dict]:
    steps = []
    for n in goal.path():
        steps.append({
            "depth": n.depth,
            "g": round(n.g, 6),
            "action": None if n.parent is None
            else problem.describe_action(n.parent.state, n.action, n.state),
            "view": problem.to_view(n.state),
        })
    return steps
