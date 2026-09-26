from typing import List

from src.core.problem import Problem


class ExampleProblem(Problem):
    """EXEMPLE DE TEST - Problème simple sur une ligne de 0 à 10.
    Ce code est un exemple factice destiné à valider le fonctionnement
    du moteur de recherche (BFS, A*, etc.) avant d'implémenter les vrais problèmes.

    Le départ est à 0, l'objectif est d'atteindre 7.
    Actions : avancer (+1) ou reculer (-1).
    """

    def __init__(self, start: int = 0, goal: int = 7):
        self._start = start
        self._goal = goal

    def get_start_state(self) -> int:
        return self._start

    def is_goal(self, state: int) -> bool:
        return state == self._goal

    def get_actions(self, state: int) -> List[str]:
        return ["RIGHT", "LEFT"]

    def result(self, state: int, action: str) -> int:
        return state + 1 if action == "RIGHT" else state - 1

    def path_cost(self, c: float, state1: int, action: str, state2: int) -> float:
        return c + 1.0

    def heuristic(self, state: int) -> float:
        return abs(self._goal - state)
