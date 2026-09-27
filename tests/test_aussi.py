"""Tests d'AUSSI :  python -m unittest discover tests"""

import unittest

from aussi.api import build_problem, solve, compare, check, catalog, tool_definitions
from aussi.core import search, Problem, Strategy, register, STRATEGIES, SUCCESS, FAILURE, CUTOFF

FAST = {"max_time": 5, "max_memory_nodes": 300_000}


def run(name, params, strategy="astar", mode="graph", heuristic=None, limits=FAST):
    return search(build_problem(name, params, heuristic), strategy, mode, limits)


class TestOptimality(unittest.TestCase):
    """UCS et A* (h consistante) doivent trouver le même coût optimal."""

    CASES = [
        ("labyrinthe", {"preset": "complexe"}),
        ("labyrinthe", {"preset": "pondere"}),
        ("labyrinthe", {"preset": "portails"}),
        ("labyrinthe", {"preset": "diagonal"}),
        ("navigation", {"start": "Rouyn-Noranda", "goal": "Gaspé"}),
        ("npuzzle", {"preset": "moyen"}),
        ("arithmetique", {"preset": "24_3388"}),
        ("equation", {"preset": "fractions"}),
    ]

    def test_ucs_equals_astar(self):
        for name, params in self.CASES:
            with self.subTest(name=name, params=params):
                u, a = run(name, params, "ucs"), run(name, params, "astar")
                self.assertEqual(u.status, SUCCESS)
                self.assertEqual(a.status, SUCCESS)
                self.assertAlmostEqual(u.cost, a.cost, places=6)
                self.assertLessEqual(a.stats.expanded, u.stats.expanded)

    def test_astar_tree_is_optimal_with_admissible_h(self):
        g = run("npuzzle", {"preset": "moyen"}, "astar", "graph")
        t = run("npuzzle", {"preset": "moyen"}, "astar", "tree")
        self.assertEqual(t.status, SUCCESS)
        self.assertEqual(g.cost, t.cost)

    def test_bfs_minimises_depth_in_graph_mode(self):
        g = run("navigation", {"start": "Rouyn-Noranda", "goal": "Gaspé"}, "bfs", "graph")
        t = run("navigation", {"start": "Rouyn-Noranda", "goal": "Gaspé"}, "bfs", "tree")
        self.assertEqual(g.depth, t.depth)

    def test_known_optimal_costs(self):
        self.assertEqual(run("npuzzle", {"preset": "difficile"}).cost, 31)  # 8-puzzle le plus dur
        self.assertEqual(run("labyrinthe", {"preset": "simple"}).cost, 11)

    def test_solution_path_is_valid(self):
        p = build_problem("labyrinthe", {"preset": "pondere"})
        r = search(p, "astar", "graph")
        path = r.goal_node.path()
        self.assertEqual(path[0].state, p.initial_state)
        self.assertTrue(p.is_goal(path[-1].state))
        g = 0
        for a, b in zip(path, path[1:]):
            self.assertIn(b.action, list(p.actions(a.state)))
            self.assertEqual(p.result(a.state, b.action), b.state)
            g += p.step_cost(a.state, b.action, b.state)
        self.assertAlmostEqual(g, r.cost)


class TestNoSolutionAndLimits(unittest.TestCase):
    def test_exhaustion_reports_failure(self):
        for name, params in [("labyrinthe", {"preset": "sans_solution"}),
                             ("navigation", {"start": "Gaspé", "goal": "Îles-de-la-Madeleine"}),
                             ("arithmetique", {"preset": "24_impossible"}),
                             ("arithmetique", {"preset": "compte_impossible"})]:
            with self.subTest(name=name):
                r = run(name, params, "bfs")
                self.assertEqual(r.status, FAILURE)
                self.assertIn("entièrement exploré", r.message)

    def test_precheck(self):
        self.assertEqual(run("npuzzle", {"preset": "insoluble"}).status, FAILURE)
        self.assertEqual(run("npuzzle", {"preset": "insoluble"}).stats.expanded, 0)
        self.assertEqual(run("equation", {"preset": "sans_solution"}).status, FAILURE)

    def test_memory_limit_stops_the_agent(self):
        r = run("npuzzle", {"preset": "15_difficile"}, limits={"max_memory_nodes": 20_000, "max_time": 30})
        self.assertEqual(r.status, CUTOFF)
        self.assertIn("mémoire", r.message)

    def test_time_limit(self):
        r = run("labyrinthe", {"preset": "complexe"}, "bfs", "tree", limits={"max_time": 0.2, "max_memory_nodes": None})
        self.assertEqual(r.status, CUTOFF)

    def test_depth_limit_is_a_cutoff_not_a_failure(self):
        r = run("npuzzle", {"preset": "moyen"}, "bfs", "graph", limits={"max_depth": 5})
        self.assertEqual(r.status, CUTOFF)


class TestHeuristics(unittest.TestCase):
    def test_admissible_heuristics_are_consistent(self):
        for name, params, h in [("labyrinthe", {"preset": "portails"}, "manhattan"),
                                ("labyrinthe", {"preset": "diagonal"}, "octile"),
                                ("navigation", {"start": "Chicoutimi", "goal": "Montréal"}, "vol_oiseau"),
                                ("navigation", {"start": "Chicoutimi", "goal": "Montréal"}, "longitude"),
                                ("npuzzle", {"preset": "facile"}, "conflits_lineaires"),
                                ("equation", {"preset": "deux_membres"}, "defauts_div2")]:
            with self.subTest(h=h):
                self.assertTrue(check({"problem": name, "params": params, "heuristic": h,
                                       "max_states": 5000})["consistante"])

    def test_bad_heuristics_are_detected(self):
        for name, params, h in [("labyrinthe", {"preset": "portails"}, "manhattan_naif"),
                                ("labyrinthe", {"preset": "diagonal"}, "manhattan"),
                                ("navigation", {"start": "Chicoutimi", "goal": "Montréal"}, "vol_oiseau_x2")]:
            with self.subTest(h=h):
                self.assertFalse(check({"problem": name, "params": params, "heuristic": h})["consistante"])

    def test_custom_heuristic_callable(self):
        p = build_problem("labyrinthe", {"preset": "simple"})
        p.set_heuristic(lambda s: 0)
        self.assertEqual(search(p, "astar").cost, 11)


class TestExtensibility(unittest.TestCase):
    def test_new_strategy_in_a_few_lines(self):
        @register
        class Deepest(Strategy):
            name, label = "test_deepest", "test"

            def priority(self, node, order):
                return -node.depth
        try:
            self.assertEqual(run("labyrinthe", {"preset": "simple"}, "test_deepest").status, SUCCESS)
        finally:
            del STRATEGIES["test_deepest"]

    def test_new_problem_without_touching_the_engine(self):
        class Counter(Problem):
            """Atteindre n à partir de 1 avec +1 et ×2."""
            name = "compteur"
            heuristics = {"zero": "h = 0"}

            def __init__(self, n):
                self.n = n
                super().__init__()

            initial_state = 1

            def actions(self, s):
                return ["+1", "×2"]

            def result(self, s, a):
                return s + 1 if a == "+1" else s * 2

            def is_goal(self, s):
                return s == self.n

        r = search(Counter(37), "bfs", "graph")
        self.assertEqual(r.status, SUCCESS)
        self.assertEqual(r.depth, 7)  # 1→2→4→8→9→18→36→37

    def test_extension_strategies(self):
        self.assertEqual(run("npuzzle", {"preset": "moyen"}, "wastar").status, SUCCESS)
        self.assertEqual(run("labyrinthe", {"preset": "moyen"}, "dfs").status, SUCCESS)


class TestApi(unittest.TestCase):
    def test_json_api(self):
        r = solve({"problem": "arithmetique", "params": {"numbers": "2 3 5 7", "target": 24}})
        self.assertTrue(r["found"])
        self.assertTrue(r["expression"].endswith("= 24"))
        c = compare({"problem": "equation", "params": {"preset": "simple"}})
        self.assertEqual(len(c["rows"]), 8)
        self.assertIn("labyrinthe", catalog()["problems"])
        self.assertEqual({t["name"] for t in tool_definitions()},
                         {"aussi_solve", "aussi_compare", "aussi_check_heuristic"})

    def test_bad_inputs_raise_value_error(self):
        with self.assertRaises(ValueError):
            solve({"problem": "inconnu"})
        with self.assertRaises(ValueError):
            solve({"problem": "labyrinthe", "strategy": "magie"})
        with self.assertRaises(ValueError):
            solve({"problem": "npuzzle", "params": {"tiles": "1 2 3"}})


if __name__ == "__main__":
    unittest.main()
