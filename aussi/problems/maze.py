"""Labyrinthes.

Grille texte :
    #  mur (infranchissable)        S  départ        G  but
    .  sol, coût 1                  :  hautes herbes, coût 2
    ~  eau, coût 4                  ^  montagne, coût 8
    1..9  portail : case de coût 1 ; l'action « téléporter » (coût 1) mène
          à l'autre case portant le même chiffre.

Le coût d'un déplacement est celui de la case d'arrivée (× √2 en diagonale).
Les heuristiques de distance tiennent compte des portails pour rester
admissibles ; `manhattan_naif` les ignore volontairement (contre-exemple).
"""

from __future__ import annotations

import math
import random

from ..core.problem import Problem

TERRAIN = {".": 1, "S": 1, "G": 1, ":": 2, "~": 4, "^": 8}
TERRAIN_NAMES = {".": "sol", ":": "herbes", "~": "eau", "^": "montagne"}
MOVES4 = [(-1, 0, "↑"), (1, 0, "↓"), (0, -1, "←"), (0, 1, "→")]
MOVES8 = MOVES4 + [(-1, -1, "↖"), (-1, 1, "↗"), (1, -1, "↙"), (1, 1, "↘")]
SQRT2 = math.sqrt(2)


class Maze(Problem):
    name = "labyrinthe"
    heuristics = {
        "manhattan": "|Δx|+|Δy| × coût min (tient compte des portails) — 4 directions",
        "octile": "distance octile × coût min (portails) — admissible en 8 directions",
        "euclidienne": "distance à vol d'oiseau × coût min (portails)",
        "manhattan_naif": "Manhattan en ignorant les portails (NON admissible s'il y en a)",
        "zero": "h = 0",
    }
    default_heuristic = "manhattan"  # "octile" si diagonal (voir __init__)

    def __init__(self, grid: str | list[str], diagonal: bool = False,
                 heuristic=None, label: str = "personnalisé"):
        lines = grid.strip("\n").split("\n") if isinstance(grid, str) else list(grid)
        width = max(len(l) for l in lines)
        self.grid = [l.replace(" ", ".").ljust(width, "#") for l in lines]
        self.rows, self.cols = len(self.grid), width
        self.diagonal = diagonal
        self.label = label
        self.start = self.goal = None
        portals: dict[str, list] = {}
        for r, line in enumerate(self.grid):
            for c, ch in enumerate(line):
                if ch == "S":
                    self.start = (r, c)
                elif ch == "G":
                    self.goal = (r, c)
                elif ch.isdigit():
                    portals.setdefault(ch, []).append((r, c))
                elif ch not in TERRAIN and ch != "#":
                    raise ValueError(f"Caractère inconnu '{ch}' en ({r},{c})")
        if self.start is None or self.goal is None:
            raise ValueError("La grille doit contenir un S et un G")
        self.twin = {}
        for d, cells in portals.items():
            if len(cells) != 2:
                raise ValueError(f"Le portail {d} doit apparaître exactement deux fois")
            a, b = cells
            self.twin[a], self.twin[b] = b, a
        costs = [self.cost(r, c) for r in range(self.rows) for c in range(self.cols)
                 if self.grid[r][c] != "#"]
        self.min_cost = min(costs)
        self.default_heuristic = "octile" if diagonal else "manhattan"
        super().__init__(heuristic)

    def cost(self, r, c) -> float:
        ch = self.grid[r][c]
        return 1 if ch.isdigit() else TERRAIN[ch]

    # --- formulation ------------------------------------------------------
    @property
    def initial_state(self):
        return self.start

    def is_goal(self, state):
        return state == self.goal

    def actions(self, state):
        r, c = state
        for dr, dc, arrow in (MOVES8 if self.diagonal else MOVES4):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < self.rows and 0 <= nc < self.cols) or self.grid[nr][nc] == "#":
                continue
            if dr and dc and (self.grid[r][nc] == "#" or self.grid[nr][c] == "#"):
                continue  # pas de coupe de coin
            yield (dr, dc, arrow)
        if state in self.twin:
            yield "T"

    def result(self, state, action):
        if action == "T":
            return self.twin[state]
        return (state[0] + action[0], state[1] + action[1])

    def step_cost(self, state, action, next_state):
        if action == "T":
            return 1
        c = self.cost(*next_state)
        return c * SQRT2 if action[0] and action[1] else c

    # --- heuristiques -----------------------------------------------------
    def _with_portals(self, dist, s):
        best = dist(s, self.goal)
        if self.twin:
            to_portal = min(dist(s, p) for p in self.twin)
            from_portal = min(dist(q, self.goal) for q in self.twin)
            best = min(best, to_portal + 1 + from_portal)
        return best

    def _manhattan(self, a, b):
        return self.min_cost * (abs(a[0] - b[0]) + abs(a[1] - b[1]))

    def _octile(self, a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return self.min_cost * (max(dx, dy) + (SQRT2 - 1) * min(dx, dy))

    def _euclid(self, a, b):
        return self.min_cost * math.hypot(a[0] - b[0], a[1] - b[1])

    def h_manhattan(self, s):
        return self._with_portals(self._manhattan, s)

    def h_octile(self, s):
        return self._with_portals(self._octile, s)

    def h_euclidienne(self, s):
        return self._with_portals(self._euclid, s)

    def h_manhattan_naif(self, s):
        return self._manhattan(s, self.goal)

    # --- présentation -----------------------------------------------------
    def describe_action(self, state, action, next_state):
        if action == "T":
            return f"téléportation {state} → {next_state}"
        ch = self.grid[next_state[0]][next_state[1]]
        terrain = TERRAIN_NAMES.get(ch, "")
        return f"{action[2]} {next_state}" + (f" [{terrain}]" if ch in ":~^" else "")

    def to_view(self, state):
        return list(state)

    def render(self, state=None, path=None):
        rows = [list(l) for l in self.grid]
        for (r, c) in path or []:
            if rows[r][c] in ".:~^":
                rows[r][c] = "*"
        if state:
            rows[state[0]][state[1]] = "@"
        return "\n".join("".join(r) for r in rows)

    def view_meta(self):
        return {"type": "grid", "grid": self.grid, "start": self.start, "goal": self.goal}

    def summary(self):
        kind = "8 dir." if self.diagonal else "4 dir."
        return f"Labyrinthe {self.label} {self.rows}×{self.cols} ({kind})"


# ---------------------------------------------------------------------- #
# Générateur et instances prédéfinies
# ---------------------------------------------------------------------- #
def generate(rows: int, cols: int, seed: int = 0, braid: float = 0.0,
             terrain: float = 0.0) -> list[str]:
    """Labyrinthe par backtracking récursif. `braid` = proportion de culs-de-sac
    ouverts (crée des boucles, donc plusieurs chemins) ; `terrain` = densité de
    zones pondérées."""
    rows, cols = rows | 1, cols | 1  # dimensions impaires
    rng = random.Random(seed)
    g = [["#"] * cols for _ in range(rows)]
    stack = [(1, 1)]
    g[1][1] = "."
    while stack:
        r, c = stack[-1]
        nbrs = [(r + dr, c + dc, dr // 2, dc // 2) for dr, dc in ((2, 0), (-2, 0), (0, 2), (0, -2))
                if 0 < r + dr < rows - 1 and 0 < c + dc < cols - 1 and g[r + dr][c + dc] == "#"]
        if not nbrs:
            stack.pop()
            continue
        nr, nc, hr, hc = rng.choice(nbrs)
        g[r + hr][c + hc] = g[nr][nc] = "."
        stack.append((nr, nc))
    if braid:
        for r in range(1, rows - 1, 2):
            for c in range(1, cols - 1, 2):
                walls = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                         if g[r + dr][c + dc] == "#"]
                if len(walls) == 3 and rng.random() < braid:
                    cand = [(wr, wc) for wr, wc in walls if 0 < wr < rows - 1 and 0 < wc < cols - 1]
                    if cand:
                        wr, wc = rng.choice(cand)
                        g[wr][wc] = "."
    if terrain:
        open_cells = [(r, c) for r in range(rows) for c in range(cols) if g[r][c] == "."]
        for _ in range(int(len(open_cells) * terrain / 12)):
            cr, cc = rng.choice(open_cells)
            kind = rng.choice(":~~^")
            rad = rng.randint(1, 3)
            for r in range(cr - rad, cr + rad + 1):
                for c in range(cc - rad, cc + rad + 1):
                    if 0 <= r < rows and 0 <= c < cols and g[r][c] == ".":
                        g[r][c] = kind
    g[1][1] = "S"
    g[rows - 2][cols - 2] = "G"
    return ["".join(r) for r in g]


def _nearest_open(grid, target):
    tr, tc = target
    best = None
    for r, line in enumerate(grid):
        for c, ch in enumerate(line):
            if ch == "." and (best is None or abs(r - tr) + abs(c - tc) < best[0]):
                best = (abs(r - tr) + abs(c - tc), r, c)
    return best[1], best[2]


def _set(grid, cells, ch):
    g = [list(l) for l in grid]
    for r, c in cells:
        g[r][c] = ch
    return ["".join(l) for l in g]


SIMPLE = """
##########
#S..#....#
#.#.#.##.#
#.#...#..#
#.###.#.##
#...#...G#
##########
"""

OPEN_FIELD = """
####################
#S.......#.........#
#........#....^^^..#
#..####..#....^^^..#
#.....#..#.........#
#.....#.....~~~....#
#.....#######~.....#
#...........#~...:.#
#..::::.....#....:G#
####################
"""


def _preset(name: str) -> tuple[list[str] | str, bool]:
    if name == "simple":
        return SIMPLE, False
    if name == "moyen":
        return generate(21, 21, seed=3), False
    if name == "complexe":
        return generate(61, 61, seed=42, braid=0.3), False
    if name == "pondere":
        return generate(31, 31, seed=7, braid=0.6, terrain=0.5), False
    if name == "portails":
        g = generate(41, 41, seed=11, braid=0.1)
        a = _nearest_open(g, (5, 5))
        b = _nearest_open(g, (35, 35))
        return _set(g, [a, b], "1"), False
    if name == "diagonal":
        return OPEN_FIELD, True
    if name == "sans_solution":
        g = generate(21, 21, seed=3)
        gr, gc = 19, 19
        return _set(g, [(gr - 1, gc), (gr, gc - 1)], "#"), False
    raise ValueError(f"Préréglage inconnu '{name}'. Choix : {', '.join(PRESETS)}")


PRESETS = {
    "simple": "10×7, dessiné à la main",
    "moyen": "21×21 parfait (un seul chemin)",
    "complexe": "61×61 avec boucles (plusieurs chemins)",
    "pondere": "31×31, herbes/eau/montagne à coûts variables",
    "portails": "41×41 avec une paire de portails",
    "diagonal": "terrain ouvert, 8 directions, coûts variables",
    "sans_solution": "21×21, le but est emmuré",
}


def from_params(p: dict) -> Maze:
    grid = p.get("grid")
    if grid:
        return Maze(grid, bool(p.get("diagonal", False)), p.get("heuristic"))
    preset = p.get("preset", "simple")
    grid, diag = _preset(preset)
    if "diagonal" in p:
        diag = bool(p["diagonal"])
    return Maze(grid, diag, p.get("heuristic"), label=preset)
