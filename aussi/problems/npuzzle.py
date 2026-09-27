"""N-Puzzle (8-puzzle, 15-puzzle, ...).

État : tuple de n² entiers lus ligne par ligne, 0 = case vide.
But : 1, 2, ..., n²-1, 0.

Les instances difficiles (15-puzzle profond) dépassent vite la mémoire : le
moteur s'arrête alors de lui-même grâce à ses limites (« arrêt de travail »).
La parité est vérifiée avant la recherche : la moitié des configurations
n'ont pas de solution.
"""

from __future__ import annotations

import random
from bisect import bisect_left

from ..core.problem import Problem

DIRS = {"haut": (-1, 0), "bas": (1, 0), "gauche": (0, -1), "droite": (0, 1)}


class NPuzzle(Problem):
    name = "npuzzle"
    heuristics = {
        "manhattan": "somme des distances de Manhattan des tuiles — admissible, consistante",
        "mal_placees": "nombre de tuiles mal placées — admissible, moins informée",
        "conflits_lineaires": "Manhattan + 2 × conflits linéaires — admissible, plus informée",
        "zero": "h = 0",
    }
    default_heuristic = "manhattan"

    def __init__(self, tiles, heuristic=None, label="personnalisé"):
        tiles = tuple(int(t) for t in tiles)
        n = int(round(len(tiles) ** 0.5))
        if n * n != len(tiles) or sorted(tiles) != list(range(n * n)):
            raise ValueError("Il faut une permutation de 0..n²-1 (0 = case vide)")
        self.n, self.tiles, self.label = n, tiles, label
        self.goal = tuple(range(1, n * n)) + (0,)
        self.goal_pos = {t: divmod(i, n) for i, t in enumerate(self.goal)}
        super().__init__(heuristic)

    @property
    def initial_state(self):
        return self.tiles

    def is_goal(self, state):
        return state == self.goal

    def actions(self, state):
        r, c = divmod(state.index(0), self.n)
        for name, (dr, dc) in DIRS.items():
            if 0 <= r + dr < self.n and 0 <= c + dc < self.n:
                yield name

    def result(self, state, action):
        i = state.index(0)
        dr, dc = DIRS[action]
        j = i + dr * self.n + dc
        s = list(state)
        s[i], s[j] = s[j], s[i]
        return tuple(s)

    # --- solvabilité ------------------------------------------------------
    def precheck(self):
        if not solvable(self.tiles, self.n):
            return "parité des inversions incompatible avec la configuration but"
        return None

    # --- heuristiques -----------------------------------------------------
    def h_mal_placees(self, s):
        return sum(1 for t, g in zip(s, self.goal) if t and t != g)

    def h_manhattan(self, s):
        n, gp, total = self.n, self.goal_pos, 0
        for i, t in enumerate(s):
            if t:
                r, c = divmod(i, n)
                gr, gc = gp[t]
                total += abs(r - gr) + abs(c - gc)
        return total

    def h_conflits_lineaires(self, s):
        n, gp = self.n, self.goal_pos
        extra = 0
        for k in range(n):
            row = [gp[t][1] for t in s[k * n:(k + 1) * n] if t and gp[t][0] == k]
            col = [gp[t][0] for t in s[k::n] if t and gp[t][1] == k]
            extra += (len(row) - _lis(row)) + (len(col) - _lis(col))
        return self.h_manhattan(s) + 2 * extra

    # --- présentation -----------------------------------------------------
    def describe_action(self, state, action, next_state):
        tile = state[next_state.index(0)]
        opposite = {"haut": "bas", "bas": "haut", "gauche": "droite", "droite": "gauche"}
        return f"tuile {tile} vers le {opposite[action]}" if action in ("haut", "bas") \
            else f"tuile {tile} vers la {opposite[action]}"

    def render(self, state):
        w = len(str(self.n * self.n - 1))
        return "\n".join(" ".join((str(t) if t else "_").rjust(w)
                                  for t in state[r * self.n:(r + 1) * self.n]) for r in range(self.n))

    def to_view(self, state):
        return list(state)

    def view_meta(self):
        return {"type": "puzzle", "n": self.n}

    def summary(self):
        return f"{self.n * self.n - 1}-Puzzle {self.label}"


def _lis(seq) -> int:
    """Longueur de la plus longue sous-suite croissante."""
    tails = []
    for x in seq:
        i = bisect_left(tails, x)
        tails[i:i + 1] = [x]
    return len(tails)


def solvable(tiles, n) -> bool:
    flat = [t for t in tiles if t]
    inv = sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) if flat[i] > flat[j])
    if n % 2 == 1:
        return inv % 2 == 0
    blank_row_from_bottom = n - tiles.index(0) // n
    return (inv + blank_row_from_bottom) % 2 == 1


def scramble(n: int, moves: int, seed: int = 0) -> tuple:
    """Marche aléatoire depuis le but (donc toujours soluble)."""
    rng = random.Random(seed)
    p = NPuzzle(tuple(range(1, n * n)) + (0,))
    s, last = p.goal, None
    back = {"haut": "bas", "bas": "haut", "gauche": "droite", "droite": "gauche"}
    for _ in range(moves):
        acts = [a for a in p.actions(s) if a != back.get(last)]
        last = rng.choice(acts)
        s = p.result(s, last)
    return s


PRESETS = {
    "facile": "8-puzzle, 8 coups de mélange",
    "moyen": "8-puzzle, 40 coups de mélange",
    "difficile": "8-puzzle le plus dur (31 coups)",
    "15_facile": "15-puzzle, 30 coups de mélange",
    "15_difficile": "15-puzzle mélangé 400 coups — dépasse les limites (arrêt de travail)",
    "insoluble": "8-puzzle impossible (deux tuiles échangées)",
}


def _preset(name):
    return {
        "facile": lambda: scramble(3, 8, seed=1),
        "moyen": lambda: scramble(3, 40, seed=4),
        "difficile": lambda: (8, 6, 7, 2, 5, 4, 3, 0, 1),
        "15_facile": lambda: scramble(4, 30, seed=2),
        "15_difficile": lambda: scramble(4, 400, seed=5),
        "insoluble": lambda: (1, 2, 3, 4, 5, 6, 8, 7, 0),
    }[name]()


def from_params(p: dict) -> NPuzzle:
    tiles = p.get("tiles")
    if tiles:
        if isinstance(tiles, str):
            tiles = tiles.replace(",", " ").split()
        return NPuzzle(tiles, p.get("heuristic"))
    if p.get("scramble"):
        n = int(p.get("size", 3))
        return NPuzzle(scramble(n, int(p["scramble"]), int(p.get("seed", 0))), p.get("heuristic"),
                       label=f"mélangé {p['scramble']} coups")
    preset = p.get("preset", "facile")
    if preset not in PRESETS:
        raise ValueError(f"Préréglage inconnu '{preset}'. Choix : {', '.join(PRESETS)}")
    return NPuzzle(_preset(preset), p.get("heuristic"), label=preset)
