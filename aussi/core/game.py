"""Formulation abstraite d'un jeu à deux joueurs.

C'est le SEUL contrat entre les moteurs de décision (Minimax, MCTS) et un jeu.
Périmètre : jeux finis, deux joueurs, tours alternés, déterministes, à
information parfaite et à somme nulle.

Règles du contrat :
  * un état est une valeur IMMUABLE (tuple, NamedTuple, ...) : `result`
    retourne un NOUVEL état et ne modifie jamais celui qu'on lui donne. Les
    moteurs peuvent donc explorer sans toucher à l'état réel de la partie ;
  * une action est opaque pour les moteurs : ils ne font que la recevoir de
    `actions` et la redonner à `result` ;
  * `utility(s, p)` est dans [-max_utility, +max_utility] et la somme est
    nulle : utility(s, p) = -utility(s, adversaire(p)).

Évaluations : une sous-classe déclare `evaluations = {"nom": "description"}` et
fournit une méthode `e_<nom>(state, player)` pour chacune. Une évaluation
estime un état NON terminal du point de vue de `player`, dans [-1, 1]
(+1 : très favorable à `player`). On peut aussi donner n'importe quelle
fonction `f(state, player)` au moteur.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Sequence

#: f(state, player) -> estimation dans [-1, 1] du point de vue de `player`
Evaluation = Callable[[Any, Any], float]


class Game(ABC):
    #: identifiant court du jeu (registre / interface)
    name: str = "jeu"
    label: str = "Jeu"
    #: évaluations disponibles : nom -> description
    evaluations: dict[str, str] = {"neutre": "0 pour tout état non terminal (aucune connaissance du jeu)"}
    default_evaluation: str = "neutre"
    #: borne de |utility| (sert à normaliser les récompenses de MCTS)
    max_utility: float = 1.0

    # ------------------------------------------------------------------ #
    # Règles (à implémenter)
    # ------------------------------------------------------------------ #
    @abstractmethod
    def initial_state(self) -> Any: ...

    @abstractmethod
    def players(self) -> tuple[Any, Any]:
        """Les deux joueurs, dans l'ordre de jeu (le premier commence)."""

    @abstractmethod
    def to_move(self, state) -> Any:
        """Joueur au trait dans `state`."""

    @abstractmethod
    def actions(self, state) -> Sequence[Any]:
        """Actions légales. L'ordre est celui que les moteurs explorent en
        premier : un bon ordre (ex. le centre d'abord) accélère alpha-bêta."""

    @abstractmethod
    def result(self, state, action) -> Any:
        """Nouvel état après `action` ; `state` n'est jamais modifié."""

    @abstractmethod
    def is_terminal(self, state) -> bool: ...

    @abstractmethod
    def utility(self, state, player) -> float:
        """Utilité exacte d'un état TERMINAL pour `player`."""

    # ------------------------------------------------------------------ #
    # Outils génériques
    # ------------------------------------------------------------------ #
    def opponent(self, player):
        a, b = self.players()
        return b if player == a else a

    def winner(self, state):
        """Gagnant d'un état terminal, ou None pour une partie nulle."""
        for p in self.players():
            if self.utility(state, p) > 0:
                return p
        return None

    # ------------------------------------------------------------------ #
    # Évaluation
    # ------------------------------------------------------------------ #
    def evaluation(self, name: str | None = None) -> Evaluation:
        name = name or self.default_evaluation
        if name not in self.evaluations:
            raise ValueError(f"Évaluation inconnue '{name}' pour {self.name}. "
                             f"Choix : {', '.join(self.evaluations)}")
        return getattr(self, f"e_{name}")

    def e_neutre(self, state, player) -> float:
        return 0.0

    # ------------------------------------------------------------------ #
    # Présentation (jamais utilisée par les moteurs)
    # ------------------------------------------------------------------ #
    def action_to_str(self, action) -> str:
        return str(action)

    def parse_action(self, state, text: str):
        """Action légale correspondant au texte `text` (sinon ValueError)."""
        text = text.strip()
        for a in self.actions(state):
            if self.action_to_str(a) == text:
                return a
        raise ValueError(f"Coup illégal '{text}'. Coups légaux : "
                         + ", ".join(self.action_to_str(a) for a in self.actions(state)))

    def player_to_str(self, player) -> str:
        return str(player)

    def render(self, state) -> str:
        return str(state)

    def summary(self) -> str:
        return self.label
