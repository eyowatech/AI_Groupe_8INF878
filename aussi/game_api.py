"""API JSON des jeux d'AUSSI : tout passe par des dictionnaires.

La ligne de commande et les expériences n'utilisent que ces fonctions ; un LLM
peut les appeler comme « outils » (`tool_definitions()`).

Une position est décrite par le jeu, ses paramètres et la LISTE DES COUPS
joués depuis le début (ex. ["4", "4", "3"]) : c'est générique (aucun format de
plateau propre à un jeu), sans état caché côté serveur, et facile à produire
pour un humain comme pour un LLM.

Ajouter un jeu = l'enregistrer dans GAMES ; rien d'autre ne change.
"""

from __future__ import annotations

from .core import AGENT_KINDS, Game, make_agent, play_match
from .games.connect4 import Connect4
from .games.nim import Nim
from .games.tictactoe import TicTacToe

GAMES = {
    "tictactoe": {
        "cls": TicTacToe,
        "description": "Tic-Tac-Toe : aligner k symboles sur une grille m×n (3×3, k=3 par défaut). Coup = numéro de case (1 en haut à gauche).",
        "params": {"rows": {"type": "integer", "default": 3}, "cols": {"type": "integer", "default": 3},
                   "k": {"type": "integer", "default": 3}},
    },
    "puissance4": {
        "cls": Connect4,
        "description": "Puissance 4 : déposer un jeton dans une colonne, aligner k jetons (6×7, k=4 par défaut). Coup = numéro de colonne (1 à gauche).",
        "params": {"rows": {"type": "integer", "default": 6}, "cols": {"type": "integer", "default": 7},
                   "k": {"type": "integer", "default": 4}},
    },
    "nim": {
        "cls": Nim,
        "description": "Nim : retirer n objets d'un tas ; qui prend le dernier gagne. Coup = 'tas:nombre' (ex. '2:3'). Jeu SANS évaluation dédiée.",
        "params": {"piles": {"type": "string", "default": "1 3 5", "description": "tailles des tas"}},
    },
}


def build_game(name: str, params: dict | None = None) -> Game:
    if name not in GAMES:
        raise ValueError(f"Jeu inconnu '{name}'. Choix : {', '.join(GAMES)}")
    params = {k: v for k, v in (params or {}).items() if v is not None}
    if name == "nim" and "piles" in params:
        piles = params["piles"]
        params["piles"] = tuple(int(x) for x in (piles.split() if isinstance(piles, str) else piles))
    else:
        params = {k: int(v) for k, v in params.items()}
    return GAMES[name]["cls"](**params)


def replay(game: Game, moves: list[str] | None):
    state = game.initial_state()
    for m in moves or []:
        if game.is_terminal(state):
            raise ValueError(f"Coup '{m}' joué après la fin de la partie")
        state = game.result(state, game.parse_action(state, str(m)))
    return state


def describe_state(game: Game, state) -> dict:
    terminal = game.is_terminal(state)
    out = {
        "jeu": game.summary(),
        "plateau": game.render(state),
        "terminal": terminal,
        "au_trait": None if terminal else game.player_to_str(game.to_move(state)),
        "coups_legaux": [] if terminal else [game.action_to_str(a) for a in game.actions(state)],
    }
    if terminal:
        w = game.winner(state)
        out["issue"] = "partie nulle" if w is None else f"{game.player_to_str(w)} gagne"
    return out


def catalog() -> dict:
    return {
        "games": {name: {"label": spec["cls"].label, "description": spec["description"], "params": spec["params"],
                         "evaluations": spec["cls"].evaluations,
                         "default_evaluation": spec["cls"].default_evaluation}
                  for name, spec in GAMES.items()},
        "agents": AGENT_KINDS,
    }


def state(req: dict) -> dict:
    """req = {game, params?, moves?}"""
    game = build_game(req["game"], req.get("params"))
    return describe_state(game, replay(game, req.get("moves")))


def decide(req: dict) -> dict:
    """AUSSI choisit un coup dans une position. req = {game, params?, moves?, agent}"""
    game = build_game(req["game"], req.get("params"))
    s = replay(game, req.get("moves"))
    if game.is_terminal(s):
        raise ValueError("La partie est terminée : aucun coup à jouer.")
    agent = make_agent(req.get("agent", "minimax"))
    decision = agent.choose(game, s)
    return {"position": describe_state(game, s), "agent": agent.describe(), "decision": decision.to_dict(),
            "apres": describe_state(game, game.result(s, decision.action))}


def play(req: dict) -> dict:
    """Partie complète AUSSI contre AUSSI. req = {game, params?, moves?, first, second, max_plies?}"""
    game = build_game(req["game"], req.get("params"))
    first, second = game.players()
    agents = {first: make_agent(req.get("first", "minimax")), second: make_agent(req.get("second", "mcts"))}
    res = play_match(game, agents, replay(game, req.get("moves")), max_plies=req.get("max_plies"))
    return {"jeu": game.summary(),
            "agents": {game.player_to_str(p): a.describe() for p, a in agents.items()},
            **res.to_dict(game)}


def tournament(req: dict, on_game=None) -> dict:
    """n parties entre les agents A et B en alternant qui commence.

    req = {game, params?, a, b, n?, openings?, seed?}. Avec openings = k > 0,
    chaque paire de parties part d'une même ouverture de k demi-coups tirés au
    hasard, jouée une fois avec A en premier et une fois avec B en premier :
    sans cela, deux agents déterministes rejoueraient toujours la même partie.
    on_game(i, résumé) est appelé après chaque partie."""
    import random

    game = build_game(req["game"], req.get("params"))
    first, second = game.players()
    n, k = int(req.get("n", 10)), int(req.get("openings", 0))
    rng = random.Random(req.get("seed", 0))
    score = {"A": 0, "nulle": 0, "B": 0}
    by_side = {"A_premier": {"A": 0, "nulle": 0, "B": 0}, "B_premier": {"A": 0, "nulle": 0, "B": 0}}
    stats = {"A": [], "B": []}
    games = []
    opening, start = [], game.initial_state()
    for i in range(n):
        if i % 2 == 0:   # nouvelle ouverture pour chaque paire
            opening, start = [], game.initial_state()
            while len(opening) < k:
                start = game.initial_state()
                opening = []
                for _ in range(k):
                    a = rng.choice(game.actions(start))
                    opening.append(game.action_to_str(a))
                    start = game.result(start, a)
                    if game.is_terminal(start):
                        break
                if game.is_terminal(start):
                    opening = []
        a_first = i % 2 == 0
        agents = {"A": make_agent(req["a"]), "B": make_agent(req["b"])}
        names = {first: "A", second: "B"} if a_first else {first: "B", second: "A"}
        res = play_match(game, {p: agents[names[p]] for p in names}, start)
        tag = "nulle" if res.winner is None else names[res.winner]
        score[tag] += 1
        by_side["A_premier" if a_first else "B_premier"][tag] += 1
        label = {game.player_to_str(p): names[p] for p in names}
        for d in res.decisions:
            stats[label[d.player]].append(d)
        summary = {"partie": i + 1, "premier": names[first], "gagnant": tag, "ouverture": " ".join(opening),
                   "demi_coups": res.plies + len(opening),
                   "coups": " ".join(d.action_str for d in res.decisions)}
        games.append(summary)
        if on_game:
            on_game(i, summary)

    def agg(decisions):
        if not decisions:
            return {}
        out = {"coups": len(decisions), "temps_moyen_s": sum(d.time_s for d in decisions) / len(decisions)}
        for key in ("profondeur_terminee", "noeuds", "simulations"):
            vals = [d.details[key] for d in decisions if key in d.details]
            if vals:
                out[f"{key}_moyen"] = sum(vals) / len(vals)
        return out

    return {"jeu": game.summary(), "A": make_agent(req["a"]).describe(), "B": make_agent(req["b"]).describe(),
            "parties": n, "ouvertures": k, "score": score, "par_premier_joueur": by_side,
            "stats_A": agg(stats["A"]), "stats_B": agg(stats["B"]), "detail": games}


AGENT_SPEC_DOC = ("Agent sous la forme 'type:option=valeur,...'. Types : "
                  + "; ".join(f"{k} ({v})" for k, v in AGENT_KINDS.items() if k != "humain")
                  + ". Ex. 'minimax:temps=1,eval=fenetres', 'mcts:temps=0.5,c=1.4', 'aleatoire'.")


def tool_definitions() -> list[dict]:
    """Descriptions d'outils prêtes pour un LLM (format « tools » de l'API Claude)."""
    games_desc = "; ".join(f"{k}: {v['description']}" for k, v in GAMES.items())
    position = {
        "game": {"type": "string", "enum": list(GAMES), "description": games_desc},
        "params": {"type": "object", "description": "paramètres du jeu (rows, cols, k ; piles pour nim)"},
        "moves": {"type": "array", "items": {"type": "string"}, "description": "coups joués depuis le début, dans l'ordre"},
    }
    return [
        {"name": "aussi_game_state",
         "description": "Affiche une position : plateau, joueur au trait, coups légaux, issue si terminée.",
         "input_schema": {"type": "object", "required": ["game"], "properties": position}},
        {"name": "aussi_decide",
         "description": "AUSSI choisit et explique un coup dans une position (coup, temps, profondeur/nœuds ou simulations/visites).",
         "input_schema": {"type": "object", "required": ["game"], "properties": {
             **position, "agent": {"type": "string", "description": AGENT_SPEC_DOC}}}},
        {"name": "aussi_play",
         "description": "Joue une partie complète entre deux agents AUSSI et renvoie l'issue et chaque décision.",
         "input_schema": {"type": "object", "required": ["game"], "properties": {
             **position,
             "first": {"type": "string", "description": "agent du premier joueur. " + AGENT_SPEC_DOC},
             "second": {"type": "string", "description": "agent du second joueur"}}}},
    ]


TOOLS = {"aussi_game_state": state, "aussi_decide": decide, "aussi_play": play}
