"""Nim (version normale) : on retire autant d'objets qu'on veut d'UN tas ;
celui qui prend le dernier objet gagne.

Ce jeu sert de « jeu inconnu » : il ne fournit AUCUNE évaluation (seulement
l'évaluation neutre héritée de Game). Il montre qu'un nouveau jeu conforme au
contrat est jouable par Minimax et MCTS sans modifier les moteurs. La théorie
(Bouton, 1901) donne la réponse exacte pour vérifier : le joueur au trait
gagne si et seulement si le XOR des tailles des tas est non nul.
"""

from __future__ import annotations

from typing import NamedTuple

from ..core.game import Game


class NimState(NamedTuple):
    piles: tuple[int, ...]
    player: int        # 0 ou 1


class Nim(Game):
    name = "nim"
    label = "Nim"

    def __init__(self, piles: tuple[int, ...] = (1, 3, 5)):
        self.piles = tuple(int(p) for p in piles)

    def initial_state(self):
        return NimState(self.piles, 0)

    def players(self):
        return (0, 1)

    def to_move(self, state):
        return state.player

    def actions(self, state):
        return [(i, n) for i, p in enumerate(state.piles) for n in range(p, 0, -1)]

    def result(self, state, action):
        i, n = action
        piles = list(state.piles)
        piles[i] -= n
        return NimState(tuple(piles), 1 - state.player)

    def is_terminal(self, state):
        return not any(state.piles)

    def utility(self, state, player):
        # le joueur qui vient de jouer a pris le dernier objet : il gagne
        return 1 if player != state.player else -1

    def action_to_str(self, action):
        return f"{action[0] + 1}:{action[1]}"

    def player_to_str(self, player):
        return f"J{player + 1}"

    def render(self, state):
        return "\n".join(f"tas {i + 1} : {'|' * p} ({p})" for i, p in enumerate(state.piles))

    def summary(self):
        return f"Nim (tas {' '.join(map(str, self.piles))})"
