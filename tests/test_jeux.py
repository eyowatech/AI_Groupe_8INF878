"""Tests des jeux d'AUSSI (TP2) :  python -m unittest discover tests"""

import functools
import inspect
import re
import unittest

from aussi import game_api
from aussi.core import (MCTS, Agent, Decision, IllegalMove, IterativeDeepeningMinimax, MCTSAgent,
                        MinimaxAgent, RandomAgent, make_agent, play_match)
from aussi.core import mcts as mcts_module
from aussi.core import minimax as minimax_module
from aussi.games.connect4 import Connect4
from aussi.games.nim import Nim
from aussi.games.tictactoe import TicTacToe


def position(game, moves: str):
    return game_api.replay(game, moves.split())


def minimax_move(game, state, **kw):
    kw.setdefault("time_limit", None)
    kw.setdefault("evaluation", game.evaluation())
    return game.action_to_str(IterativeDeepeningMinimax(**kw).search(game, state).action)


def mcts_move(game, state, sims=3000, seed=1):
    return game.action_to_str(MCTS(None, sims, seed=seed).search(game, state).action)


class TestGameContract(unittest.TestCase):
    def test_result_does_not_modify_state(self):
        for game in (TicTacToe(), Connect4(), Nim((2, 3))):
            s = game.initial_state()
            copy = tuple(s)
            game.result(s, game.actions(s)[0])
            self.assertEqual(tuple(s), copy)

    def test_search_does_not_modify_real_state(self):
        game = Connect4()
        s = position(game, "4 4 3")
        before = tuple(s)
        IterativeDeepeningMinimax(0.2, evaluation=game.evaluation()).search(game, s)
        MCTS(None, 500, seed=0).search(game, s)
        self.assertEqual(tuple(s), before)

    def test_connect4_gravity_and_win(self):
        game = Connect4()
        s = position(game, "1 2 1 2 1 2")
        self.assertFalse(game.is_terminal(s))
        s = game.result(s, game.parse_action(s, "1"))
        self.assertTrue(game.is_terminal(s))
        self.assertEqual(game.winner(s), "X")
        self.assertEqual(game.utility(s, "X"), -game.utility(s, "O"))

    def test_full_column_is_not_legal(self):
        game = Connect4()
        s = position(game, "1 1 1 1 1 1")
        self.assertNotIn(0, game.actions(s))

    def test_tictactoe_draw(self):
        game = TicTacToe()
        s = position(game, "1 2 3 5 4 6 8 7 9")
        self.assertTrue(game.is_terminal(s))
        self.assertIsNone(game.winner(s))
        self.assertEqual(game.utility(s, "X"), 0)


class TestTactics(unittest.TestCase):
    """Victoire immédiate et blocage, pour les deux moteurs et les deux jeux."""

    CASES = [  # (jeu, coups joués, coups acceptés, description)
        (TicTacToe(), "1 4 2 5", {"3"}, "X gagne tout de suite (plutôt que bloquer 6)"),
        (TicTacToe(), "1 5 2", {"3"}, "O doit bloquer"),
        (TicTacToe(), "5 1 9", {"3", "7"}, "O doit jouer un coin pour éviter la fourchette"),
        (Connect4(), "4 4 3 3 2 2", {"1", "5"}, "X gagne tout de suite"),
        (Connect4(), "4 1 3 1 2", {"5"}, "O doit bloquer"),
    ]

    def test_minimax(self):
        for game, moves, ok, desc in self.CASES:
            with self.subTest(desc):
                limit = None if isinstance(game, TicTacToe) else 1.0
                self.assertIn(minimax_move(game, position(game, moves), time_limit=limit), ok)

    def test_mcts(self):
        for game, moves, ok, desc in self.CASES:
            with self.subTest(desc):
                self.assertIn(mcts_move(game, position(game, moves), sims=5000), ok)


class TestMinimax(unittest.TestCase):
    def test_never_loses_tictactoe_from_empty_board(self):
        game = TicTacToe()
        for seed in range(10):
            for side in game.players():
                agents = {side: MinimaxAgent(time_limit=None),
                          game.opponent(side): RandomAgent(seed)}
                res = play_match(game, agents)
                self.assertNotEqual(res.winner, game.opponent(side), f"graine {seed}, côté {side}")

    def test_perfect_play_is_a_draw(self):
        game = TicTacToe()
        res = play_match(game, {p: MinimaxAgent(time_limit=None) for p in game.players()})
        self.assertIsNone(res.winner)

    def test_alpha_beta_same_value_fewer_nodes(self):
        game = TicTacToe()
        s = position(game, "1")
        ab = IterativeDeepeningMinimax(None, alpha_beta=True).search(game, s)
        mm = IterativeDeepeningMinimax(None, alpha_beta=False).search(game, s)
        self.assertEqual(ab.value, mm.value)
        self.assertTrue(ab.exhaustive and mm.exhaustive)
        self.assertLess(ab.nodes, mm.nodes)
        # sans élagage, toutes les valeurs à la racine sont exactes
        self.assertTrue(all(exact for _, _, exact in mm.root_values))

    def test_no_completed_iteration_returns_legal_fallback(self):
        game = Connect4()
        s = game.initial_state()
        r = IterativeDeepeningMinimax(time_limit=0).search(game, s)
        self.assertTrue(r.fallback)
        self.assertEqual(r.completed_depth, 0)
        self.assertIn(r.action, game.actions(s))

    def test_keeps_last_completed_iteration_on_timeout(self):
        game = Connect4()
        r = IterativeDeepeningMinimax(time_limit=0.05, evaluation=game.evaluation()).search(game, game.initial_state())
        self.assertTrue(r.timed_out)
        self.assertGreaterEqual(r.completed_depth, 1)
        self.assertEqual(r.completed_depth, r.iterations[-1].depth)
        self.assertEqual(r.action, r.iterations[-1].action)

    def test_max_depth(self):
        game = Connect4()
        r = IterativeDeepeningMinimax(time_limit=None, max_depth=3).search(game, game.initial_state())
        self.assertEqual(r.completed_depth, 3)
        self.assertEqual([it.depth for it in r.iterations], [1, 2, 3])
        self.assertFalse(r.timed_out)

    def test_evaluation_is_replaceable_and_uses_root_player(self):
        game = Connect4()
        seen = set()

        def prefer_left(state, player):   # une évaluation quelconque, sans toucher à Minimax
            seen.add(player)
            return 0.5 if state.cells[-game.cols] == player else 0.0

        s = position(game, "4")
        r = IterativeDeepeningMinimax(None, max_depth=1, evaluation=prefer_left).search(game, s)
        self.assertEqual(seen, {"O"})
        self.assertEqual(game.action_to_str(r.action), "1")

    def test_prefers_fastest_win(self):
        game = TicTacToe()
        s = position(game, "1 4 2 5")
        r = IterativeDeepeningMinimax(None).search(game, s)
        self.assertGreater(r.value, minimax_module.PROVEN)
        self.assertEqual(round(minimax_module.WIN - r.value), 1)


class TestMCTS(unittest.TestCase):
    def test_counts_and_most_visited(self):
        game = Connect4()
        r = MCTS(None, 800, seed=3).search(game, game.initial_state())
        self.assertEqual(r.simulations, 800)
        self.assertEqual(sum(c.visits for c in r.root_children), 800)
        self.assertEqual(r.action, max(r.root_children, key=lambda c: c.visits).action)
        self.assertEqual(len(r.root_children), 7)   # chaque action essayée au moins une fois

    def test_no_simulation_returns_legal_fallback(self):
        game = TicTacToe()
        s = game.initial_state()
        for engine in (MCTS(None, 0), MCTS(0.0, None)):
            r = engine.search(game, s)
            self.assertTrue(r.fallback)
            self.assertIn(r.action, game.actions(s))

    def test_beats_random_at_tictactoe(self):
        game = TicTacToe()
        for seed in range(6):
            res = play_match(game, {"X": MCTSAgent(None, 2000, seed=seed), "O": RandomAgent(seed)})
            self.assertNotEqual(res.winner, "O")

    def test_exploration_constant_is_exposed(self):
        self.assertEqual(MCTS(None, 10, c=0.3).c, 0.3)
        self.assertEqual(make_agent("mcts:sims=10,c=0.3").engine.c, 0.3)


class TestGenericity(unittest.TestCase):
    def test_engines_contain_no_game_rules(self):
        forbidden = re.compile(r"tictactoe|tic-tac|puissance|connect|colonne|column|grille|grid|rows|cols|nim\b",
                               re.IGNORECASE)
        for module in (minimax_module, mcts_module):
            with self.subTest(module.__name__):
                self.assertIsNone(forbidden.search(inspect.getsource(module)))

    def test_unknown_game_with_neutral_evaluation(self):
        """Nim n'a aucune évaluation : Minimax joue quand même parfaitement
        (théorème de Bouton : laisser un XOR nul)."""
        game = Nim((3, 4, 5))
        s = game.initial_state()
        r = IterativeDeepeningMinimax(None).search(game, s)
        after = game.result(s, r.action)
        self.assertEqual(functools.reduce(lambda a, b: a ^ b, after.piles), 0)
        res = play_match(game, {0: MinimaxAgent(time_limit=None), 1: MCTSAgent(None, 300, seed=0)})
        self.assertEqual(res.winner, 0)

    def test_mcts_on_unknown_game(self):
        game = Nim((1, 2))   # seul coup gagnant : retirer 1 du tas 2
        self.assertEqual(mcts_move(game, game.initial_state(), sims=2000), "2:1")


class TestInterface(unittest.TestCase):
    def test_illegal_move_is_rejected(self):
        class Cheater(Agent):
            def choose(self, game, state):
                return Decision(99, "99", "X", "tricheur", 0.0)

        game = TicTacToe()
        with self.assertRaises(IllegalMove):
            play_match(game, {"X": Cheater(), "O": RandomAgent(0)})

    def test_parse_spec(self):
        a = make_agent("minimax:temps=0.5,profondeur=4,eval=neutre,alphabeta=non")
        self.assertEqual((a.time_limit, a.max_depth, a.evaluation, a.alpha_beta), (0.5, 4, "neutre", False))
        with self.assertRaises(ValueError):
            make_agent("humain")   # pas d'interface pour saisir les coups

    def test_api_decide_and_play(self):
        res = game_api.decide({"game": "puissance4", "moves": ["4", "4", "3", "3", "2", "2"],
                               "agent": "minimax:temps=0.5"})
        self.assertIn(res["decision"]["action_str"], {"1", "5"})
        self.assertGreaterEqual(res["decision"]["details"]["profondeur_terminee"], 1)
        res = game_api.decide({"game": "tictactoe", "agent": "mcts:sims=200,graine=1"})
        self.assertEqual(res["decision"]["details"]["simulations"], 200)
        res = game_api.play({"game": "tictactoe", "first": "minimax", "second": "minimax"})
        self.assertEqual(res["issue"], "partie nulle")

    def test_tool_definitions(self):
        names = [t["name"] for t in game_api.tool_definitions()]
        self.assertEqual(set(names), set(game_api.TOOLS))

    def test_tournament_alternates_first_player(self):
        res = game_api.tournament({"game": "tictactoe", "a": "minimax", "b": "aleatoire:graine=1",
                                   "n": 4, "openings": 1})
        self.assertEqual(res["score"]["B"], 0)
        self.assertEqual([g["premier"] for g in res["detail"]], ["A", "B", "A", "B"])


if __name__ == "__main__":
    unittest.main()
