"""Interface texte des jeux : affichage et saisie au clavier.

C'est la seule partie qui fait des `print` et des `input`. Elle ne fait que
brancher des agents sur `play_match` ; la remplacer (web, LLM...) ne touche
ni aux règles ni aux moteurs.
"""

from __future__ import annotations

from . import game_api
from .core import make_agent, play_match


class Quit(Exception):
    pass


def ask_human(game, state):
    legal = [game.action_to_str(a) for a in game.actions(state)]
    who = game.player_to_str(game.to_move(state))
    while True:
        try:
            text = input(f"  {who}, votre coup ({' '.join(legal)} ; q pour quitter) : ").strip()
        except EOFError:
            raise Quit from None
        if text.lower() in ("q", "quit", "quitter"):
            raise Quit
        try:
            return game.parse_action(state, text)
        except ValueError as e:
            print(f"  {e}")


def print_decision(n, game, decision, after):
    print(f"\n── demi-coup {n} · {decision.player} ({decision.agent}) joue {decision.action_str}"
          f" · réflexion {decision.time_s:.3f} s")
    for line in decision.explanation:
        print(f"   {line}")
    print(game.render(after))


def play(game_name, params, specs, moves=None, quiet=False):
    game = game_api.build_game(game_name, params)
    players = game.players()
    agents = {p: make_agent(spec, ask=ask_human) for p, spec in zip(players, specs)}
    state = game_api.replay(game, moves)
    print(f"{game.summary()}")
    for p, a in agents.items():
        print(f"  {game.player_to_str(p)} : {a.describe()}")
    print(game.render(state))
    count = [len(moves or [])]

    def on_decision(game, before, decision, after):
        count[0] += 1
        print_decision(count[0], game, decision, after)

    try:
        res = play_match(game, agents, state, on_decision=None if quiet else on_decision)
    except Quit:
        print("\nPartie abandonnée.")
        return
    total = {p: sum(d.time_s for d in res.decisions if d.player == game.player_to_str(p)) for p in players}
    if quiet:
        print(game.render(res.final_state))
    print(f"\nIssue : {res.outcome(game)} en {res.plies} demi-coups. "
          f"Coups : {' '.join(d.action_str for d in res.decisions)}")
    print("Temps de réflexion total : " + ", ".join(f"{game.player_to_str(p)} {t:.2f} s" for p, t in total.items()))


def decide(game_name, params, spec, moves):
    res = game_api.decide({"game": game_name, "params": params, "moves": moves, "agent": spec})
    print(res["position"]["plateau"])
    d = res["decision"]
    print(f"\n{res['agent']}\n{d['player']} joue {d['action_str']} · réflexion {d['time_s']:.3f} s")
    for line in d["explanation"]:
        print(f"   {line}")


def tournament(game_name, params, a, b, n, openings=0):
    print(f"A = {a}\nB = {b}\n")
    res = game_api.tournament({"game": game_name, "params": params, "a": a, "b": b, "n": n, "openings": openings},
                              on_game=lambda i, g: print(f"  partie {g['partie']:>3} : {g['premier']} commence → "
                                                         f"{g['gagnant']:<5} ({g['demi_coups']} demi-coups)"
                                                         + (f" ouverture {g['ouverture']}" if g['ouverture'] else "")))
    s = res["score"]
    print(f"\n{res['jeu']} — {n} parties : A {s['A']} · nulles {s['nulle']} · B {s['B']}")
    for side, sc in res["par_premier_joueur"].items():
        print(f"  {side.replace('_', ' ')} : A {sc['A']} · nulles {sc['nulle']} · B {sc['B']}")
    for who in ("A", "B"):
        st = res[f"stats_{who}"]
        print(f"  {who} : " + ", ".join(f"{k} {v:.3g}" for k, v in st.items()))
    return res
