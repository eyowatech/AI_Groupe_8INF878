"""Tests HTTP ciblés de l'interface web des jeux."""

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from aussi.web.server import Handler


class TestWebGameAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post_json(self, path, body):
        request = Request(
            self.base_url + path,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            return json.loads(response.read())

    def test_web_page_exposes_game_tab(self):
        with urlopen(self.base_url) as response:
            page = response.read().decode()
        self.assertIn("Jeux (TP2)", page)
        self.assertIn("/api/game/decide", page)

    def test_game_state_and_decision_routes(self):
        request = {"game": "tictactoe", "params": {}, "moves": []}
        state = self.post_json("/api/game/state", request)
        self.assertEqual(len(state["coups_legaux"]), 9)

        result = self.post_json(
            "/api/game/decide",
            request | {"agent": "mcts:sims=50,graine=1"},
        )
        action = result["decision"]["action_str"]
        self.assertIn(action, state["coups_legaux"])
        self.assertEqual(result["apres"]["au_trait"], "O")


if __name__ == "__main__":
    unittest.main()
