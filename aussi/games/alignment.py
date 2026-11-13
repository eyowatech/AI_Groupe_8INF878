"""Base commune des jeux d'alignement : aligner k pions sur une grille m × n.

Tic-Tac-Toe (3×3, k=3) et Puissance 4 (6×7, k=4) ne diffèrent que par la façon
de poser un pion (n'importe quelle case vide, ou la case libre la plus basse
d'une colonne). Cette factorisation concerne les RÈGLES ; les moteurs de
décision, eux, ne voient que le contrat `Game`.

État : NamedTuple immuable (cases, joueur au trait, gagnant, cases vides).
Le gagnant est calculé une seule fois dans `result`, en ne vérifiant que les
fenêtres qui passent par la case jouée : `is_terminal` est en O(1).
"""

from __future__ import annotations

import math
from typing import NamedTuple

from ..core.game import Game

EMPTY = "."
PLAYERS = ("X", "O")
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))   # →, ↓, ↘, ↙


class GridState(NamedTuple):
    cells: tuple[str, ...]    # ligne par ligne, ligne 0 en haut
    player: str               # joueur au trait
    winner: str | None
    empty: int                # nombre de cases vides


class AlignmentGame(Game):
    evaluations = {
        "neutre": "0 pour tout état non terminal",
        "fenetres": "fenêtres de k cases encore gagnables, pondérées par le nombre de pions (4^(n-1)) : les miennes moins celles de l'adversaire",
    }
    default_evaluation = "fenetres"

    def __init__(self, rows: int, cols: int, k: int):
        if not (1 <= k <= max(rows, cols)):
            raise ValueError("k doit être compris entre 1 et la plus grande dimension de la grille")
        self.rows, self.cols, self.k = rows, cols, k
        # toutes les fenêtres de k cases alignées, et celles qui passent par chaque case
        self.windows: list[tuple[int, ...]] = []
        for r in range(rows):
            for c in range(cols):
                for dr, dc in DIRECTIONS:
                    end_r, end_c = r + dr * (k - 1), c + dc * (k - 1)
                    if 0 <= end_r < rows and 0 <= end_c < cols:
                        self.windows.append(tuple((r + dr * i) * cols + c + dc * i for i in range(k)))
        self.windows_through = [[w for w in self.windows if i in w] for i in range(rows * cols)]
        self.weights = [0] + [4 ** (n - 1) for n in range(1, k + 1)]

    # ------------------------------------------------------------------ #
    # Contrat Game
    # ------------------------------------------------------------------ #
    def initial_state(self) -> GridState:
        n = self.rows * self.cols
        return GridState((EMPTY,) * n, PLAYERS[0], None, n)

    def players(self):
        return PLAYERS

    def to_move(self, state):
        return state.player

    def is_terminal(self, state):
        return state.winner is not None or state.empty == 0

    def utility(self, state, player):
        if state.winner is None:
            return 0
        return 1 if state.winner == player else -1

    def result(self, state, action):
        idx = self._target_cell(state, action)
        cells = list(state.cells)
        cells[idx] = state.player
        cells = tuple(cells)
        winner = state.player if any(all(cells[i] == state.player for i in w)
                                     for w in self.windows_through[idx]) else None
        other = PLAYERS[1] if state.player == PLAYERS[0] else PLAYERS[0]
        return GridState(cells, other, winner, state.empty - 1)

    def _target_cell(self, state, action) -> int:
        """Index de la case où l'action pose un pion."""
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Évaluation
    # ------------------------------------------------------------------ #
    def window_score(self, cells, player) -> int:
        """Σ poids(mes pions) sur mes fenêtres encore gagnables − idem pour l'adversaire."""
        w, s = self.weights, 0
        for win in self.windows:
            mine = theirs = 0
            for i in win:
                c = cells[i]
                if c == player:
                    mine += 1
                elif c != EMPTY:
                    theirs += 1
            if not theirs:
                s += w[mine]
            elif not mine:
                s -= w[theirs]
        return s

    def e_fenetres(self, state, player) -> float:
        # tanh ramène le score dans ]-1, 1[ ; une fenêtre à k-1 pions vaut ~0,76
        return math.tanh(self.window_score(state.cells, player) / 4 ** (self.k - 1))

    # ------------------------------------------------------------------ #
    # Présentation
    # ------------------------------------------------------------------ #
    def summary(self):
        return f"{self.label} ({self.rows}×{self.cols}, aligner {self.k})"
