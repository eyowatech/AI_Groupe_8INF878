"""Agents : qui choisit le coup d'un joueur.

Un agent reçoit (jeu, état) et rend une `Decision` : l'action, le temps de
réflexion et une explication (données structurées + texte). Il ne fait aucun
affichage ni aucune lecture au clavier : un humain, ou un LLM, est branché via
`ExternalAgent` et une fonction fournie par l'interface.

Spécification textuelle d'un agent (CLI, API JSON, LLM) :
    "minimax:temps=1,profondeur=8,eval=fenetres,alphabeta=oui"
    "mcts:temps=1,sims=5000,c=1.41,graine=7"
    "aleatoire:graine=3"
    "humain"
"""

from __future__ import annotations

import math
import random
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from .game import Evaluation, Game
from .mcts import MCTS
from .minimax import IterativeDeepeningMinimax, describe_value


@dataclass
class Decision:
    action: Any
    action_str: str
    player: str
    agent: str
    time_s: float
    details: dict = field(default_factory=dict)   # compteurs propres à l'algorithme
    explanation: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("action")
        return d


class Agent(ABC):
    kind: str = "agent"

    @abstractmethod
    def choose(self, game: Game, state) -> Decision: ...

    def describe(self) -> str:
        return self.kind


# ---------------------------------------------------------------------- #
class RandomAgent(Agent):
    """Choisit uniformément parmi les actions légales (adversaire de référence)."""
    kind = "aleatoire"

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def choose(self, game, state):
        t0 = time.perf_counter()
        actions = game.actions(state)
        a = self.rng.choice(actions)
        return Decision(a, game.action_to_str(a), game.player_to_str(game.to_move(state)), self.kind,
                        time.perf_counter() - t0, {"coups_legaux": len(actions)},
                        [f"coup tiré au hasard parmi {len(actions)} coups légaux"])


class ExternalAgent(Agent):
    """Le coup vient de l'extérieur : humain au clavier, interface web, LLM...
    `ask(game, state) -> action` est fourni par l'interface ; l'action est
    validée par la boucle de partie."""
    kind = "humain"

    def __init__(self, ask: Callable[[Game, Any], Any], kind: str = "humain"):
        self.ask, self.kind = ask, kind

    def choose(self, game, state):
        t0 = time.perf_counter()
        a = self.ask(game, state)
        return Decision(a, game.action_to_str(a), game.player_to_str(game.to_move(state)), self.kind,
                        time.perf_counter() - t0)


class MinimaxAgent(Agent):
    kind = "minimax"

    def __init__(self, time_limit: float | None = 1.0, max_depth: int | None = None,
                 evaluation: str | Evaluation | None = None, alpha_beta: bool = True):
        self.time_limit, self.max_depth = time_limit, max_depth
        self.evaluation, self.alpha_beta = evaluation, alpha_beta

    def _eval(self, game) -> tuple[Evaluation, str]:
        if callable(self.evaluation):
            return self.evaluation, getattr(self.evaluation, "__name__", "personnalisee")
        name = self.evaluation or game.default_evaluation
        if name not in game.evaluations:   # jeu inconnu : on retombe sur l'évaluation neutre
            name = "neutre"
        return game.evaluation(name), name

    def describe(self):
        return (f"minimax(temps={self.time_limit}, profondeur max={self.max_depth or '∞'}, "
                f"eval={self.evaluation or 'défaut'}, alpha-bêta={'oui' if self.alpha_beta else 'non'})")

    def choose(self, game, state):
        evaluate, eval_name = self._eval(game)
        engine = IterativeDeepeningMinimax(self.time_limit, self.max_depth, evaluate, self.alpha_beta)
        r = engine.search(game, state)
        who = game.player_to_str(r.player)
        roots = [{"action": game.action_to_str(a), "valeur": round(v, 4), "exacte": ex}
                 for a, v, ex in sorted(r.root_values, key=lambda t: -t[1])]
        details = {
            "profondeur_terminee": r.completed_depth,
            "noeuds": r.nodes,
            "noeuds_par_s": round(r.nodes / r.time_s) if r.time_s > 0 else None,
            "valeur": r.value,
            "point_de_vue": who,
            "evaluation": eval_name,
            "temps_ecoule": r.timed_out,
            "arbre_complet": r.exhaustive,
            "coup_de_secours": r.fallback,
            "valeurs_racine": roots,
            "iterations": [asdict(it) | {"action": game.action_to_str(it.action)} for it in r.iterations],
        }
        if r.fallback:
            lines = ["aucune itération terminée dans le temps imparti : coup légal de secours"]
        else:
            stop = ("arbre complet exploré" if r.exhaustive else
                    "temps écoulé pendant la profondeur suivante" if r.timed_out else
                    "résultat prouvé" if r.value is not None and abs(r.value) > 500 else
                    "profondeur maximale atteinte")
            lines = [f"profondeur terminée : {r.completed_depth} ({stop}) · nœuds visités : {r.nodes:,}".replace(",", " "),
                     f"valeur du coup (point de vue de {who}) : {describe_value(r.value)} · évaluation : {eval_name}",
                     "valeurs à la racine (≤ : borne alpha-bêta, V/D n : victoire/défaite forcée en n demi-coups) :",
                     "  " + "  ".join(
                         f"{x['action']}:{'' if x['exacte'] else '≤'}{_short(x['valeur'])}" for x in roots)]
        return Decision(r.action, game.action_to_str(r.action), who, self.kind, r.time_s, details, lines)


class MCTSAgent(Agent):
    kind = "mcts"

    def __init__(self, time_limit: float | None = 1.0, max_simulations: int | None = None,
                 c: float = math.sqrt(2), seed: int | None = None):
        self.engine = MCTS(time_limit, max_simulations, c, seed)

    def describe(self):
        e = self.engine
        return f"mcts(temps={e.time_limit}, sims max={e.max_simulations or '∞'}, c={e.c:.2f})"

    def choose(self, game, state):
        r = self.engine.search(game, state)
        who = game.player_to_str(r.player)
        roots = [{"action": game.action_to_str(rc.action), "visites": rc.visits, "q": round(rc.q, 4)}
                 for rc in r.root_children]
        details = {
            "simulations": r.simulations,
            "simulations_par_s": round(r.simulations / r.time_s) if r.time_s > 0 else None,
            "noeuds_arbre": r.tree_nodes,
            "c": r.c,
            "point_de_vue": who,
            "coup_de_secours": r.fallback,
            "visites_racine": roots,
        }
        if r.fallback:
            lines = ["aucune simulation terminée : coup légal de secours"]
        else:
            lines = [f"simulations : {r.simulations:,} · nœuds de l'arbre : {r.tree_nodes:,} · c = {r.c:.2f}".replace(",", " "),
                     f"visites à la racine (Q = gain moyen de {who} : 1 victoire, 0,5 nulle, 0 défaite) :",
                     "  " + "  ".join(f"{x['action']}:{x['visites']} (Q={x['q']:.2f})" for x in roots)]
        return Decision(r.action, game.action_to_str(r.action), who, self.kind, r.time_s, details, lines)


def _short(v: float) -> str:
    if v > 500:
        return f"+V{round(1000 - v)}"     # victoire forcée en n demi-coups
    if v < -500:
        return f"-D{round(1000 + v)}"     # défaite forcée en n demi-coups
    return f"{v:+.2f}"


# ---------------------------------------------------------------------- #
# Construction à partir d'une spécification texte ou dict
# ---------------------------------------------------------------------- #
AGENT_KINDS = {
    "minimax": "Minimax à approfondissement itératif + alpha-bêta. Options : temps (s), profondeur, eval, alphabeta (oui/non)",
    "mcts": "Monte Carlo Tree Search (UCT). Options : temps (s), sims, c, graine",
    "aleatoire": "coup uniforme parmi les coups légaux. Options : graine",
    "humain": "coup saisi par l'utilisateur",
}

_KEYS = {"temps": "time_limit", "time": "time_limit", "profondeur": "max_depth", "depth": "max_depth",
         "eval": "evaluation", "evaluation": "evaluation", "alphabeta": "alpha_beta",
         "sims": "max_simulations", "simulations": "max_simulations", "c": "c",
         "graine": "seed", "seed": "seed"}


def parse_spec(spec: str | dict) -> dict:
    """'mcts:temps=0.5,c=1' -> {'kind': 'mcts', 'time_limit': 0.5, 'c': 1.0}"""
    if isinstance(spec, dict):
        raw = dict(spec)
        kind = raw.pop("kind", raw.pop("type", None))
    else:
        kind, _, rest = spec.strip().partition(":")
        raw = dict(kv.split("=", 1) for kv in rest.split(",") if kv.strip())
    kind = (kind or "").strip().lower()
    if kind not in AGENT_KINDS:
        raise ValueError(f"Agent inconnu '{kind}'. Choix : {', '.join(AGENT_KINDS)}")
    out = {"kind": kind}
    for k, v in raw.items():
        key = _KEYS.get(k.strip().lower(), k.strip())
        if isinstance(v, str):
            v = v.strip()
            if v.lower() in ("none", "aucun", "inf", ""):
                v = None
            elif key == "alpha_beta":
                v = v.lower() in ("oui", "true", "1", "yes")
            elif key in ("max_depth", "max_simulations", "seed"):
                v = int(v)
            elif key in ("time_limit", "c"):
                v = float(v)
        out[key] = v
    return out


def make_agent(spec: str | dict, ask: Callable | None = None) -> Agent:
    cfg = parse_spec(spec)
    kind = cfg.pop("kind")
    if kind == "minimax":
        return MinimaxAgent(**cfg)
    if kind == "mcts":
        return MCTSAgent(**cfg)
    if kind == "aleatoire":
        return RandomAgent(**cfg)
    if ask is None:
        raise ValueError("L'agent humain a besoin d'une interface pour saisir les coups.")
    return ExternalAgent(ask)
