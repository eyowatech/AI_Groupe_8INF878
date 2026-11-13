"""Puissance 4 (généralisé : m lignes, n colonnes, aligner k). Une action =
l'index d'une colonne non pleine ; elle est affichée et saisie de 1 à n.

Ordre des actions : colonnes du centre vers les bords. C'est une connaissance
du JEU (les colonnes centrales participent à plus d'alignements) ; elle permet
à alpha-bêta d'élaguer beaucoup plus tôt sans rien changer à Minimax.
"""

from __future__ import annotations

import math

from .alignment import EMPTY, AlignmentGame


class Connect4(AlignmentGame):
    name = "puissance4"
    label = "Puissance 4"
    evaluations = {
        **AlignmentGame.evaluations,
        "fenetres_centre": "fenêtres + 3 points par pion dans la ou les colonnes centrales (moins ceux de l'adversaire)",
        "centre": "seulement les pions au centre (évaluation volontairement pauvre, pour comparaison)",
    }
    default_evaluation = "fenetres_centre"

    def __init__(self, rows: int = 6, cols: int = 7, k: int = 4):
        super().__init__(rows, cols, k)
        mid = (cols - 1) / 2
        self.column_order = sorted(range(cols), key=lambda c: abs(c - mid))
        self.center_cells = [r * cols + c for r in range(rows) for c in range(cols)
                             if abs(c - mid) < 1]

    def actions(self, state):
        if self.is_terminal(state):
            return []
        return [c for c in self.column_order if state.cells[c] == EMPTY]   # ligne du haut libre

    def _target_cell(self, state, col):
        for r in range(self.rows - 1, -1, -1):
            i = r * self.cols + col
            if state.cells[i] == EMPTY:
                return i
        raise ValueError(f"colonne {col + 1} pleine")

    def _center_score(self, cells, player):
        return sum((cells[i] == player) - (cells[i] not in (player, EMPTY)) for i in self.center_cells)

    def e_fenetres_centre(self, state, player):
        s = self.window_score(state.cells, player) + 3 * self._center_score(state.cells, player)
        return math.tanh(s / 4 ** (self.k - 1))

    def e_centre(self, state, player):
        return math.tanh(self._center_score(state.cells, player) / 4)

    def action_to_str(self, action):
        return str(action + 1)

    def render(self, state):
        lines = ["| " + " ".join(state.cells[r * self.cols:(r + 1) * self.cols]) + " |"
                 for r in range(self.rows)]
        lines.append("+" + "-" * (2 * self.cols + 1) + "+")
        lines.append("  " + " ".join(str(c + 1)[-1] for c in range(self.cols)))
        return "\n".join(lines)
