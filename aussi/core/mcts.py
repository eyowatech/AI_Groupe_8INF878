"""Monte Carlo Tree Search classique (UCT).

Générique : ne connaît que le contrat `Game`. Aucune règle de jeu ici.

Une simulation = une itération complète des quatre étapes :
  1. sélection     : depuis la racine, tant que le nœud est entièrement développé
                     et non terminal, descendre vers l'enfant qui maximise UCT ;
  2. expansion     : si le nœud a encore des actions non essayées, en retirer une
                     (au hasard) et créer l'enfant correspondant ;
  3. simulation    : depuis ce nœud, jouer des actions tirées uniformément parmi
                     les actions légales jusqu'à un état terminal ;
  4. rétropropagation : remonter le résultat jusqu'à la racine.

Enfants non visités : un enfant n'est créé qu'au moment où il reçoit sa
première simulation (étape 2). Tant qu'un nœud a des actions non essayées, on
l'expanse au lieu d'appliquer UCT ; UCT ne compare donc que des enfants avec
N ≥ 1 (pas de division par zéro) et chaque action est essayée au moins une
fois avant qu'on en privilégie une.

Récompenses : r(p) = (utility(terminal, p) / max_utility + 1) / 2 ∈ [0, 1]
(1 = victoire de p, 0,5 = nulle, 0 = défaite). Chaque nœud accumule la
récompense du joueur qui a joué le coup MENANT à ce nœud : c'est lui qui
choisit cet enfant lors de la sélection, donc UCT maximise toujours le point de
vue du joueur qui décide.

    UCT(enfant) = W/N + c · sqrt(ln N_parent / N)

Q = W/N d'un enfant de la racine est donc la récompense moyenne du joueur au
trait à la racine (AUSSI) quand il joue cette action.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Any

from .game import Game


class _Node:
    __slots__ = ("state", "parent", "action", "mover", "children", "untried", "visits", "reward")

    def __init__(self, state, parent, action, mover, untried):
        self.state = state
        self.parent = parent
        self.action = action          # action qui mène du parent à ce nœud
        self.mover = mover            # joueur qui a joué `action` (None à la racine)
        self.children: list[_Node] = []
        self.untried = untried        # actions pas encore développées
        self.visits = 0
        self.reward = 0.0             # somme des récompenses de `mover`


@dataclass
class RootChild:
    action: Any
    visits: int
    q: float          # récompense moyenne pour le joueur à la racine, dans [0, 1]


@dataclass
class MCTSResult:
    action: Any
    player: Any
    simulations: int = 0          # simulations complètes (4 étapes) terminées
    tree_nodes: int = 1           # nœuds de l'arbre (racine comprise)
    time_s: float = 0.0
    fallback: bool = True         # aucune simulation : coup de secours
    c: float = math.sqrt(2)
    root_children: list[RootChild] = field(default_factory=list)


class MCTS:
    """time_limit      : secondes par coup (None = aucune)
    max_simulations : nombre maximal de simulations (None = aucune limite)
    c               : constante d'exploration de UCT (√2 par défaut)
    seed            : graine du générateur (reproductibilité)
    On s'arrête dès que l'un des deux budgets est épuisé."""

    def __init__(self, time_limit: float | None = 1.0, max_simulations: int | None = None,
                 c: float = math.sqrt(2), seed: int | None = None):
        if time_limit is None and max_simulations is None:
            raise ValueError("MCTS a besoin d'un budget : temps et/ou nombre de simulations.")
        self.time_limit = time_limit
        self.max_simulations = max_simulations
        self.c = c
        self.rng = random.Random(seed)

    def _new_node(self, game: Game, state, parent, action, mover) -> _Node:
        untried = [] if game.is_terminal(state) else list(game.actions(state))
        self.rng.shuffle(untried)
        return _Node(state, parent, action, mover, untried)

    def search(self, game: Game, state) -> MCTSResult:
        start = time.perf_counter()
        deadline = math.inf if self.time_limit is None else start + self.time_limit
        max_sims = math.inf if self.max_simulations is None else self.max_simulations
        rng, c, scale = self.rng, self.c, game.max_utility
        players = game.players()

        if game.is_terminal(state) or not game.actions(state):
            raise ValueError("Aucun coup possible : l'état est terminal.")
        player = game.to_move(state)
        root = self._new_node(game, state, None, None, None)
        res = MCTSResult(action=game.actions(state)[0], player=player, c=c)  # coup de secours

        while res.simulations < max_sims and time.perf_counter() < deadline:
            node = root
            # 1. sélection
            while not node.untried and node.children:
                log_n = math.log(node.visits)
                node = max(node.children,
                           key=lambda ch: ch.reward / ch.visits + c * math.sqrt(log_n / ch.visits))
            # 2. expansion
            if node.untried:
                action = node.untried.pop()
                child = self._new_node(game, game.result(node.state, action), node, action,
                                       game.to_move(node.state))
                node.children.append(child)
                res.tree_nodes += 1
                node = child
            # 3. simulation (politique uniforme)
            s = node.state
            while not game.is_terminal(s):
                s = game.result(s, rng.choice(game.actions(s)))
            # 4. rétropropagation
            reward = {p: (game.utility(s, p) / scale + 1) / 2 for p in players}
            while node is not None:
                node.visits += 1
                if node.mover is not None:
                    node.reward += reward[node.mover]
                node = node.parent
            res.simulations += 1

        if root.children:
            # action la plus visitée ; à égalité, la meilleure moyenne
            best = max(root.children, key=lambda ch: (ch.visits, ch.reward / ch.visits))
            res.action, res.fallback = best.action, False
            res.root_children = sorted(
                (RootChild(ch.action, ch.visits, ch.reward / ch.visits) for ch in root.children),
                key=lambda rc: -rc.visits)
        res.time_s = time.perf_counter() - start
        return res
