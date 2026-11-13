"""Minimax à approfondissement itératif, avec élagage alpha-bêta.

Générique : ne connaît que le contrat `Game`. Aucune règle de jeu ici.

Point de vue : toutes les valeurs sont exprimées du point de vue du joueur au
trait à la racine (`player`), celui pour qui AUSSI cherche un coup. Un nœud est
MAX quand `player` y est au trait, MIN sinon (on interroge `to_move` plutôt que
de supposer l'alternance).

Échelle des valeurs :
  * état terminal : u × (WIN − ply), où u = utility / max_utility ∈ [-1, 1] et
    ply = nombre de demi-coups depuis la racine. Une victoire vaut donc ~1000,
    d'autant plus que elle est proche ; une défaite, d'autant moins grave
    qu'elle est lointaine ; une nulle, 0 ;
  * profondeur limite : évaluation(state, player), ramenée dans [-1, 1].
Une valeur |v| > WIN/2 signifie donc un résultat PROUVÉ (victoire ou défaite
forcée), une valeur dans [-1, 1] une estimation.

Profondeur : 1 = un coup d'un joueur (un demi-coup).

Compteur de nœuds : nombre d'appels à la fonction de valeur, c.-à-d. nombre
d'états visités (feuilles comprises, racine non comprise), cumulé sur toutes
les itérations, y compris l'itération interrompue par le temps.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any

from .game import Evaluation, Game

WIN = 1000.0
PROVEN = WIN / 2


class _Timeout(Exception):
    pass


@dataclass
class Iteration:
    depth: int
    nodes: int
    time_s: float
    action: Any
    value: float


@dataclass
class MinimaxResult:
    action: Any
    player: Any
    value: float | None = None          # valeur du coup choisi (point de vue de `player`)
    completed_depth: int = 0            # dernière profondeur entièrement terminée
    nodes: int = 0                      # nœuds visités, toutes itérations confondues
    time_s: float = 0.0
    timed_out: bool = False             # une itération a été interrompue par le temps
    exhaustive: bool = False            # l'arbre complet a été exploré (aucune coupure en profondeur)
    fallback: bool = True               # aucune itération terminée : coup de secours
    # (action, valeur, exacte) pour la dernière itération terminée ; avec alpha-bêta,
    # une valeur non exacte est une borne supérieure (« ≤ v ») : le coup est moins bon.
    root_values: list[tuple[Any, float, bool]] = field(default_factory=list)
    iterations: list[Iteration] = field(default_factory=list)


def describe_value(v: float | None) -> str:
    if v is None:
        return "?"
    if v > PROVEN:
        return f"victoire forcée en {round(WIN - v)} demi-coup(s)"
    if v < -PROVEN:
        return f"défaite forcée en {round(WIN + v)} demi-coup(s)"
    return f"{v:+.3f} (estimation)" if v else "0 (nulle ou indécis)"


class IterativeDeepeningMinimax:
    """Recherches successives aux profondeurs 1, 2, 3, ... sous une limite de temps.

    time_limit  : secondes par coup (None = aucune limite de temps)
    max_depth   : profondeur maximale (None = jusqu'à l'exploration complète ;
                  sans limite de temps, à réserver aux petits jeux)
    evaluation  : f(state, player) pour les états non terminaux à la profondeur
                  limite (None = évaluation neutre, 0)
    alpha_beta  : active l'élagage alpha-bêta
    """

    def __init__(self, time_limit: float | None = 1.0, max_depth: int | None = None,
                 evaluation: Evaluation | None = None, alpha_beta: bool = True):
        self.time_limit = time_limit
        self.max_depth = max_depth
        self.evaluate = evaluation or (lambda state, player: 0.0)
        self.alpha_beta = alpha_beta

    # ------------------------------------------------------------------ #
    def search(self, game: Game, state) -> MinimaxResult:
        start = time.perf_counter()
        self._deadline = math.inf if self.time_limit is None else start + self.time_limit
        self._game = game
        self._player = player = game.to_move(state)
        self._scale = game.max_utility
        self._nodes = 0

        order = list(game.actions(state))
        if game.is_terminal(state) or not order:
            raise ValueError("Aucun coup possible : l'état est terminal.")
        # coup légal de secours si aucune itération ne se termine
        res = MinimaxResult(action=order[0], player=player)

        depth = 0
        while self.max_depth is None or depth < self.max_depth:
            depth += 1
            self._cutoff = False
            nodes_before = self._nodes
            try:
                values = self._root(state, order, depth)
            except _Timeout:
                res.timed_out = True
                break
            best_action, best_value, _ = max(values, key=lambda t: t[1])  # 1er maximum
            res.action, res.value, res.fallback = best_action, best_value, False
            res.completed_depth, res.root_values = depth, values
            res.iterations.append(Iteration(depth, self._nodes - nodes_before,
                                            time.perf_counter() - start, best_action, best_value))
            # ordre de la prochaine itération : meilleurs coups d'abord (tri stable)
            order = [a for a, _, _ in sorted(values, key=lambda t: -t[1])]
            if not self._cutoff:          # rien n'a été coupé : l'arbre est complet
                res.exhaustive = True
                break
            if best_value > PROVEN:       # victoire forcée trouvée : inutile d'aller plus loin
                break
            if all(v < -PROVEN for _, v, _ in values):  # tout perd : on retarde au maximum
                break

        res.nodes = self._nodes
        res.time_s = time.perf_counter() - start
        return res

    # ------------------------------------------------------------------ #
    def _root(self, state, order, depth):
        game, alpha = self._game, -math.inf
        values = []
        for a in order:
            v = self._value(game.result(state, a), depth - 1, alpha, math.inf, 1)
            # avec alpha-bêta, v <= alpha n'est qu'une borne supérieure
            exact = not self.alpha_beta or v > alpha
            values.append((a, v, exact))
            if self.alpha_beta and v > alpha:
                alpha = v
        return values

    def _value(self, state, depth, alpha, beta, ply):
        self._nodes += 1
        if time.perf_counter() > self._deadline:
            raise _Timeout
        game = self._game
        if game.is_terminal(state):
            return (game.utility(state, self._player) / self._scale) * (WIN - ply)
        if depth <= 0:
            self._cutoff = True
            return max(-1.0, min(1.0, float(self.evaluate(state, self._player))))

        if game.to_move(state) == self._player:   # nœud MAX
            v = -math.inf
            for a in game.actions(state):
                v = max(v, self._value(game.result(state, a), depth - 1, alpha, beta, ply + 1))
                if self.alpha_beta:
                    if v >= beta:
                        return v
                    alpha = max(alpha, v)
        else:                                      # nœud MIN
            v = math.inf
            for a in game.actions(state):
                v = min(v, self._value(game.result(state, a), depth - 1, alpha, beta, ply + 1))
                if self.alpha_beta:
                    if v <= alpha:
                        return v
                    beta = min(beta, v)
        return v
