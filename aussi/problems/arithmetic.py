"""Jeu arithmétique (« Le compte est bon », jeu du 24).

À partir d'une liste de nombres et des opérations + − × ÷, construire une
expression qui vaut la cible. Chaque action combine deux nombres en un seul :
la trace de la solution est donc directement le raisonnement d'AUSSI.

État : tuple trié de paires (valeur exacte `Fraction`, expression texte).
Clé de Graph-Search : le multiensemble des VALEURS seulement — deux états
avec les mêmes nombres restants sont équivalents, peu importe comment on les
a obtenus. Si aucune expression n'existe, la recherche épuise l'espace
d'états et AUSSI répond « aucune solution ».
"""

from __future__ import annotations

from fractions import Fraction

from ..core.problem import Problem

OPS = {"+": lambda a, b: a + b, "−": lambda a, b: a - b,
       "×": lambda a, b: a * b, "÷": lambda a, b: a / b}


def _fmt(v: Fraction) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def _strip(expr: str) -> str:
    return expr[1:-1] if expr.startswith("(") and expr.endswith(")") else expr


class Arithmetic(Problem):
    name = "arithmetique"
    heuristics = {
        "operations_restantes": "nb d'opérations minimum restantes — admissible, consistante",
        "ecart_cible": "opérations restantes + écart relatif à la cible — NON admissible (pour Greedy)",
        "zero": "h = 0",
    }
    default_heuristic = "operations_restantes"

    def __init__(self, numbers, target, use_all: bool = True, heuristic=None):
        if len(numbers) < 1:
            raise ValueError("Il faut au moins un nombre")
        self.numbers = [Fraction(n) for n in numbers]
        self.target = Fraction(target)
        self.use_all = use_all
        super().__init__(heuristic)

    @property
    def initial_state(self):
        return tuple(sorted((v, _fmt(v)) for v in self.numbers))

    def state_key(self, state):
        return tuple(v for v, _ in state)

    def is_goal(self, state):
        if self.use_all:
            return len(state) == 1 and state[0][0] == self.target
        return any(v == self.target for v, _ in state)

    def actions(self, state):
        k = len(state)
        for i in range(k):
            for j in range(i + 1, k):
                a, b = state[i][0], state[j][0]
                yield (i, j, "+")
                yield (i, j, "×")
                yield (j, i, "−") if a < b else (i, j, "−")  # résultat ≥ 0
                if b != 0:
                    yield (i, j, "÷")
                if a != 0 and a != b:
                    yield (j, i, "÷")

    def result(self, state, action):
        i, j, op = action
        (a, ea), (b, eb) = state[i], state[j]
        new = (OPS[op](a, b), f"({ea} {op} {eb})")
        rest = [x for k, x in enumerate(state) if k not in (i, j)]
        return tuple(sorted(rest + [new]))

    # --- heuristiques -----------------------------------------------------
    def h_operations_restantes(self, s):
        if self.use_all:
            return len(s) - 1
        return 0 if self.is_goal(s) else 1

    def h_ecart_cible(self, s):
        gap = min(abs(v - self.target) for v, _ in s) / (abs(self.target) + 1)
        return self.h_operations_restantes(s) + float(gap)

    # --- présentation -----------------------------------------------------
    def describe_action(self, state, action, next_state):
        i, j, op = action
        a, b = state[i][0], state[j][0]
        res = OPS[op](a, b)
        rest = ", ".join(_fmt(v) for v, _ in next_state)
        return f"{_fmt(a)} {op} {_fmt(b)} = {_fmt(res)}   → reste [{rest}]"

    def render(self, state):
        return ", ".join(f"{_fmt(v)} = {_strip(e)}" if "(" in e else _fmt(v) for v, e in state)

    def to_view(self, state):
        return [{"valeur": _fmt(v), "expression": _strip(e)} for v, e in state]

    def solution_expression(self, state) -> str | None:
        for v, e in state:
            if v == self.target:
                return f"{_strip(e)} = {_fmt(v)}"
        return None

    def view_meta(self):
        return {"type": "arithmetic", "target": _fmt(self.target)}

    def summary(self):
        nums = ", ".join(_fmt(v) for v in self.numbers)
        mode = "tous les nombres" if self.use_all else "sous-ensemble permis"
        return f"Arithmétique [{nums}] → {_fmt(self.target)} ({mode})"


PRESETS = {
    "24_2357": "2, 3, 5, 7 → 24",
    "24_fractions": "1, 5, 5, 5 → 24 (nécessite des fractions)",
    "24_3388": "3, 3, 8, 8 → 24 (difficile)",
    "24_impossible": "1, 1, 1, 1 → 24 (aucune solution)",
    "compte_est_bon": "1, 3, 7, 10, 25, 50 → 765 (sous-ensemble permis)",
    "compte_impossible": "1, 1, 2, 2, 3 → 250 (aucune solution)",
}

_PRESETS = {
    "24_2357": ([2, 3, 5, 7], 24, True),
    "24_fractions": ([1, 5, 5, 5], 24, True),
    "24_3388": ([3, 3, 8, 8], 24, True),
    "24_impossible": ([1, 1, 1, 1], 24, True),
    "compte_est_bon": ([1, 3, 7, 10, 25, 50], 765, False),
    "compte_impossible": ([1, 1, 2, 2, 3], 250, False),
}


def from_params(p: dict) -> Arithmetic:
    if p.get("numbers"):
        nums = p["numbers"]
        if isinstance(nums, str):
            nums = nums.replace(",", " ").split()
        return Arithmetic([Fraction(x) for x in nums], Fraction(str(p.get("target", 24))),
                          bool(p.get("use_all", True)), p.get("heuristic"))
    preset = p.get("preset", "24_2357")
    if preset not in _PRESETS:
        raise ValueError(f"Préréglage inconnu '{preset}'. Choix : {', '.join(PRESETS)}")
    nums, target, use_all = _PRESETS[preset]
    return Arithmetic(nums, target, use_all, p.get("heuristic"))
