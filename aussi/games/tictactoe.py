"""Tic-Tac-Toe (généralisé : grille m × n, aligner k). Une action = l'index
d'une case vide ; elle est affichée et saisie de 1 à m·n."""

from __future__ import annotations

from .alignment import EMPTY, AlignmentGame


class TicTacToe(AlignmentGame):
    name = "tictactoe"
    label = "Tic-Tac-Toe"
    evaluations = {
        **AlignmentGame.evaluations,
        "fenetres": "lignes encore gagnables (sans pion adverse), pondérées 1 (un pion) ou 4 (deux pions) : les miennes moins celles de l'adversaire",
    }

    def __init__(self, rows: int = 3, cols: int = 3, k: int = 3):
        super().__init__(rows, cols, k)

    def actions(self, state):
        if self.is_terminal(state):
            return []
        return [i for i, c in enumerate(state.cells) if c == EMPTY]

    def _target_cell(self, state, action):
        return action

    def action_to_str(self, action):
        return str(action + 1)

    def render(self, state):
        width = len(str(self.rows * self.cols))
        sep = "\n" + "+".join(["-" * (width + 2)] * self.cols) + "\n"
        rows = []
        for r in range(self.rows):
            cells = []
            for c in range(self.cols):
                i = r * self.cols + c
                v = state.cells[i]
                cells.append(f" {(str(i + 1) if v == EMPTY else v):>{width}} ")
            rows.append("|".join(cells))
        return sep.join(rows)
