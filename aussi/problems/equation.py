"""Équations linéaires à une inconnue : a·x + b = c·x + d.

AUSSI résout comme un élève : chaque action est une transformation
algébrique appliquée aux deux membres (soustraire un terme, diviser par le
coefficient de x). La solution est la trace du raisonnement.

But : « x = k » ou « k = x ». Une équation sans solution (2x+3 = 2x+5) ou
avec une infinité de solutions (2x+3 = 2x+3) n'atteint jamais ce but : la
recherche épuise l'espace d'états et AUSSI le signale.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction

from ..core.problem import Problem


def _f(v: Fraction) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def _side(a: Fraction, b: Fraction) -> str:
    parts = []
    if a:
        parts.append("x" if a == 1 else "-x" if a == -1 else f"{_f(a)}x")
    if b or not parts:
        parts.append(_f(b) if not parts else (f"+ {_f(b)}" if b > 0 else f"- {_f(-b)}"))
    return " ".join(parts)


def parse_side(text: str) -> tuple[Fraction, Fraction]:
    t = text.replace(" ", "").replace("*", "").replace("−", "-")
    if not t:
        raise ValueError("Membre vide")
    t = re.sub(r"(?<=[^+\-])-", "+-", t)
    a = b = Fraction(0)
    for term in filter(None, t.split("+")):
        if term.endswith("x"):
            coef = term[:-1]
            a += Fraction(1 if coef in ("", "+") else -1 if coef == "-" else Fraction(coef))
        else:
            b += Fraction(term)
    return a, b


def parse(equation: str):
    if equation.count("=") != 1:
        raise ValueError("L'équation doit contenir exactement un '='")
    left, right = equation.split("=")
    return (*parse_side(left), *parse_side(right))


class LinearEquation(Problem):
    name = "equation"
    heuristics = {
        "defauts_div2": "⌈défauts/2⌉ — admissible et consistante (une action corrige ≤ 2 défauts)",
        "defauts": "nombre de termes mal placés — NON admissible (bonne pour Greedy)",
        "zero": "h = 0",
    }
    default_heuristic = "defauts_div2"

    def __init__(self, equation: str, heuristic=None):
        self.text = equation
        self.start = parse(equation)
        super().__init__(heuristic)

    @property
    def initial_state(self):
        return self.start

    def is_goal(self, s):
        a, b, c, d = s
        return (a == 1 and b == 0 and c == 0) or (a == 0 and c == 1 and d == 0)

    def precheck(self):
        a, b, c, d = self.start
        if a == c:
            return ("les x s'annulent et il reste une contradiction (b ≠ d)" if b != d
                    else "identité : tout x est solution, pas de valeur unique")
        return None

    def actions(self, s):
        a, b, c, d = s
        if c:
            yield ("sub_x", c)
        if a:
            yield ("sub_x", a)
        if b:
            yield ("sub_k", b)
        if d:
            yield ("sub_k", d)
        if a not in (0, 1) and c == 0:
            yield ("div", a)
        if c not in (0, 1) and a == 0:
            yield ("div", c)

    def result(self, s, action):
        a, b, c, d = s
        kind, v = action
        if kind == "sub_x":
            return (a - v, b, c - v, d)
        if kind == "sub_k":
            return (a, b - v, c, d - v)
        return (a / v, b / v, c / v, d / v)

    # --- heuristiques -----------------------------------------------------
    def _defects(self, s):
        a, b, c, d = s
        left = (a != 1) + (b != 0) + (c != 0)   # viser x = k
        right = (c != 1) + (d != 0) + (a != 0)  # viser k = x
        return min(left, right)

    def h_defauts(self, s):
        return self._defects(s)

    def h_defauts_div2(self, s):
        return math.ceil(self._defects(s) / 2)

    # --- présentation -----------------------------------------------------
    def describe_action(self, s, action, s2):
        kind, v = action
        if kind == "sub_x":
            what = f"soustraire {_side(v, Fraction(0))}"
        elif kind == "sub_k":
            what = f"soustraire {_f(v)}"
        else:
            what = f"diviser par {_f(v)}"
        return f"{what} des deux côtés   ⇒   {self.render(s2)}"

    def render(self, s):
        a, b, c, d = s
        return f"{_side(a, b)} = {_side(c, d)}"

    def to_view(self, s):
        return self.render(s)

    def view_meta(self):
        return {"type": "equation"}

    def summary(self):
        return f"Équation {self.render(self.start)}"


PRESETS = {
    "simple": "3x + 5 = 20",
    "deux_membres": "5x - 7 = 2x + 8",
    "fractions": "4x + 1 = 7x - 3/2",
    "x_a_droite": "12 = 3x - 6",
    "sans_solution": "2x + 3 = 2x + 5",
    "infinie": "4x - 2 = 4x - 2",
}


def from_params(p: dict) -> LinearEquation:
    eq = p.get("equation") or PRESETS.get(p.get("preset", "simple"))
    if eq is None:
        raise ValueError(f"Préréglage inconnu. Choix : {', '.join(PRESETS)}")
    return LinearEquation(eq, p.get("heuristic"))
