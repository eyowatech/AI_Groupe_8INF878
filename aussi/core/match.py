"""Boucle de partie : alterne les agents sur l'état RÉEL de la partie.

Aucun affichage ici : l'interface s'abonne aux événements via `on_decision`.
Chaque agent reçoit l'état courant (immuable) ; seul `play_match` fait avancer
la partie, après avoir vérifié que l'action rendue est légale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .agents import Agent, Decision
from .game import Game


class IllegalMove(ValueError):
    pass


@dataclass
class MatchResult:
    winner: Any                       # joueur gagnant, ou None (nulle / partie interrompue)
    final_state: Any
    plies: int
    finished: bool = True
    decisions: list[Decision] = field(default_factory=list)

    def outcome(self, game: Game) -> str:
        if not self.finished:
            return "partie interrompue"
        if self.winner is None:
            return "partie nulle"
        return f"{game.player_to_str(self.winner)} gagne"

    def to_dict(self, game: Game) -> dict:
        return {
            "issue": self.outcome(game),
            "gagnant": None if self.winner is None else game.player_to_str(self.winner),
            "demi_coups": self.plies,
            "coups": [d.action_str for d in self.decisions],
            "decisions": [d.to_dict() for d in self.decisions],
            "etat_final": game.render(self.final_state),
        }


def play_match(game: Game, agents: dict[Any, Agent], state=None,
               on_decision: Callable[[Game, Any, Decision, Any], None] | None = None,
               max_plies: int | None = None) -> MatchResult:
    """agents : {joueur: agent}. `state` permet de reprendre une position.
    on_decision(game, état_avant, décision, état_après) est appelé après chaque coup."""
    state = game.initial_state() if state is None else state
    decisions: list[Decision] = []
    while not game.is_terminal(state):
        if max_plies is not None and len(decisions) >= max_plies:
            return MatchResult(None, state, len(decisions), False, decisions)
        player = game.to_move(state)
        decision = agents[player].choose(game, state)
        if decision.action not in game.actions(state):
            raise IllegalMove(f"{agents[player].kind} a proposé un coup illégal : {decision.action_str}")
        new_state = game.result(state, decision.action)
        decisions.append(decision)
        if on_decision:
            on_decision(game, state, decision, new_state)
        state = new_state
    return MatchResult(game.winner(state), state, len(decisions), True, decisions)
