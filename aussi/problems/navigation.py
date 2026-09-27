"""Navigation routière — le « mini Google Maps » d'AUSSI.

Villes du Québec (latitude/longitude approximatives) reliées par des routes.
La longueur d'une route = distance orthodromique × facteur de détour (≥ 1),
ce qui garantit que la distance à vol d'oiseau est admissible ET consistante
(inégalité triangulaire).

L'heuristique est interchangeable ; `check_heuristic` permet de vérifier
qu'une nouvelle heuristique respecte encore ces propriétés.
"""

from __future__ import annotations

import math

from ..core.problem import Problem

# ville : (latitude, longitude)
CITIES = {
    "Chicoutimi": (48.428, -71.068), "Jonquière": (48.416, -71.249),
    "Alma": (48.550, -71.649), "Roberval": (48.519, -72.224),
    "Saint-Félicien": (48.650, -72.449), "Dolbeau-Mistassini": (48.878, -72.231),
    "Chibougamau": (49.913, -74.379), "La Tuque": (47.437, -72.786),
    "Trois-Rivières": (46.343, -72.543), "Québec": (46.813, -71.208),
    "Montréal": (45.502, -73.567), "Sherbrooke": (45.404, -71.893),
    "Drummondville": (45.883, -72.484), "Gatineau": (45.477, -75.701),
    "Mont-Laurier": (46.551, -75.498), "Val-d'Or": (48.097, -77.783),
    "Rouyn-Noranda": (48.236, -79.023), "Tadoussac": (48.147, -69.717),
    "Saint-Siméon": (47.843, -69.878), "La Malbaie": (47.654, -70.153),
    "Baie-Saint-Paul": (47.441, -70.498), "Rivière-du-Loup": (47.829, -69.534),
    "Rimouski": (48.449, -68.524), "Forestville": (48.738, -69.085),
    "Baie-Comeau": (49.221, -68.150), "Gaspé": (48.831, -64.487),
    "Matane": (48.846, -67.531), "Îles-de-la-Madeleine": (47.380, -61.860),
}

# (ville A, ville B, facteur de détour) — routes à double sens
ROADS = [
    ("Chicoutimi", "Jonquière", 1.10), ("Jonquière", "Alma", 1.15),
    ("Alma", "Roberval", 1.25), ("Roberval", "Saint-Félicien", 1.15),
    ("Saint-Félicien", "Dolbeau-Mistassini", 1.20), ("Dolbeau-Mistassini", "Alma", 1.30),
    ("Saint-Félicien", "Chibougamau", 1.25), ("Chibougamau", "Val-d'Or", 1.30),
    ("Val-d'Or", "Rouyn-Noranda", 1.15), ("Val-d'Or", "Mont-Laurier", 1.20),
    ("Mont-Laurier", "Gatineau", 1.35), ("Mont-Laurier", "Montréal", 1.25),
    ("Gatineau", "Montréal", 1.15), ("Rouyn-Noranda", "Gatineau", 1.40),
    ("Chicoutimi", "Québec", 1.30), ("Chicoutimi", "Tadoussac", 1.35),
    ("Chicoutimi", "Baie-Saint-Paul", 1.40), ("Roberval", "La Tuque", 1.25),
    ("La Tuque", "Trois-Rivières", 1.25), ("Trois-Rivières", "Québec", 1.10),
    ("Trois-Rivières", "Montréal", 1.10), ("Trois-Rivières", "Drummondville", 1.15),
    ("Drummondville", "Montréal", 1.10), ("Drummondville", "Québec", 1.10),
    ("Drummondville", "Sherbrooke", 1.10), ("Sherbrooke", "Montréal", 1.15),
    ("Québec", "Baie-Saint-Paul", 1.20), ("Baie-Saint-Paul", "La Malbaie", 1.25),
    ("La Malbaie", "Saint-Siméon", 1.25), ("Saint-Siméon", "Tadoussac", 1.20),
    ("Tadoussac", "Forestville", 1.20), ("Forestville", "Baie-Comeau", 1.20),
    ("Saint-Siméon", "Rivière-du-Loup", 1.60),  # traversier
    ("Québec", "Rivière-du-Loup", 1.10), ("Rivière-du-Loup", "Rimouski", 1.10),
    ("Rimouski", "Baie-Comeau", 1.80),  # traversier
    ("Rimouski", "Matane", 1.10), ("Matane", "Gaspé", 1.35),
    # Îles-de-la-Madeleine : aucune route -> exemple sans solution
]

EARTH_R = 6371.0


def haversine(a, b) -> float:
    (la1, lo1), (la2, lo2) = (map(math.radians, a), map(math.radians, b))
    x = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(x))


class RoadMap(Problem):
    name = "navigation"
    heuristics = {
        "vol_oiseau": "distance orthodromique (haversine) — admissible et consistante",
        "vol_oiseau_x2": "2 × vol d'oiseau — NON admissible (démonstration)",
        "longitude": "écart en longitude seulement (km) — admissible, moins informée",
        "zero": "h = 0",
    }
    default_heuristic = "vol_oiseau"

    def __init__(self, start: str, goal: str, heuristic=None,
                 cities: dict | None = None, roads: list | None = None):
        self.cities = cities or CITIES
        self.graph: dict[str, dict[str, float]] = {c: {} for c in self.cities}
        for a, b, detour in roads or ROADS:
            d = round(haversine(self.cities[a], self.cities[b]) * detour, 1)
            self.graph[a][b] = self.graph[b][a] = d
        for c in (start, goal):
            if c not in self.cities:
                raise ValueError(f"Ville inconnue '{c}'. Choix : {', '.join(sorted(self.cities))}")
        self.start, self.goal = start, goal
        super().__init__(heuristic)

    @property
    def initial_state(self):
        return self.start

    def is_goal(self, state):
        return state == self.goal

    def actions(self, state):
        return self.graph[state].keys()

    def result(self, state, action):
        return action

    def step_cost(self, state, action, next_state):
        return self.graph[state][next_state]

    def h_vol_oiseau(self, s):
        return haversine(self.cities[s], self.cities[self.goal])

    def h_vol_oiseau_x2(self, s):
        return 2 * self.h_vol_oiseau(s)

    def h_longitude(self, s):
        # corde projetée sur le plan équatorial, rayon min R·cos(latitude max) :
        # arc >= corde >= projection  =>  minorant de la distance réelle
        (la1, lo1), (la2, lo2) = self.cities[s], self.cities[self.goal]
        rho = EARTH_R * math.cos(math.radians(max(abs(la1), abs(la2))))
        return 2 * rho * math.sin(abs(math.radians(lo1 - lo2)) / 2)

    def describe_action(self, state, action, next_state):
        return f"{state} → {next_state} ({self.graph[state][next_state]} km)"

    def to_view(self, state):
        return state

    def view_meta(self):
        edges = sorted({tuple(sorted((a, b))) for a in self.graph for b in self.graph[a]})
        return {"type": "map", "cities": self.cities,
                "roads": [[a, b, self.graph[a][b]] for a, b in edges],
                "start": self.start, "goal": self.goal}

    def summary(self):
        return f"Navigation {self.start} → {self.goal}"


def from_params(p: dict) -> RoadMap:
    return RoadMap(p.get("start", "Chicoutimi"), p.get("goal", "Montréal"), p.get("heuristic"))
