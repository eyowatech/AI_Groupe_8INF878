"""Point d'entrée : python -m aussi <commande>

    web                              interface web locale (défaut)
    solve PROBLEME [options]         résoudre et afficher le rapport
    compare PROBLEME [options]       toutes les stratégies × modes
    check PROBLEME [options]         vérifier l'heuristique
    experiences                      expérience comparative -> resultats/
    catalog | tools                  catalogue / définitions d'outils LLM (JSON)

  Jeux (TP2) :
    jouer JEU [-1 AGENT] [-2 AGENT]  partie (humain, minimax, mcts, aleatoire)
    decider JEU --coups "..." -a AGENT   un seul coup expliqué
    tournoi JEU -a AGENT -b AGENT -n N   N parties en alternant qui commence
    experiences-jeux                 expériences du rapport -> resultats/tp2/
    jeux | outils-jeux               catalogue / outils LLM des jeux (JSON)

Exemples :
    python -m aussi solve labyrinthe --preset complexe -s astar -m graph
    python -m aussi solve navigation --param start=Alma --param goal=Sherbrooke
    python -m aussi solve npuzzle --preset 15_difficile -s astar --time 5
    python -m aussi solve arithmetique --param numbers="2 3 5 7" --param target=24
    python -m aussi solve equation --param equation="5x - 7 = 2x + 8"
    python -m aussi jouer tictactoe -1 humain -2 minimax
    python -m aussi jouer puissance4 -1 minimax:temps=1 -2 mcts:temps=1
    python -m aussi decider puissance4 --coups "4 4 3 3" -a mcts:sims=20000
    python -m aussi tournoi puissance4 -a minimax:temps=0.5 -b mcts:temps=0.5 -n 10
    python -m aussi jouer nim --param piles="3 4 5" -1 humain -2 minimax:temps=2
"""

from __future__ import annotations

import argparse
import json
import sys

from . import api


def _params(args) -> dict:
    params = {}
    if getattr(args, "preset", None):
        params["preset"] = args.preset
    for kv in args.param or []:
        k, _, v = kv.partition("=")
        if v.lower() in ("true", "false"):
            params[k] = v.lower() == "true"
        else:
            params[k] = v
    return params


def main(argv=None):
    ap = argparse.ArgumentParser(prog="aussi", description="AUSSI — moteur générique de résolution de problèmes")
    sub = ap.add_subparsers(dest="cmd")

    w = sub.add_parser("web", help="interface web locale")
    w.add_argument("--port", type=int, default=8000)
    w.add_argument("--no-browser", action="store_true")

    for name in ("solve", "compare", "check"):
        p = sub.add_parser(name)
        p.add_argument("problem", choices=list(api.PROBLEMS))
        p.add_argument("--preset")
        p.add_argument("--param", action="append", help="clé=valeur (répétable)")
        p.add_argument("-s", "--strategy", default="astar")
        p.add_argument("-m", "--mode", default="graph", choices=["graph", "tree"])
        p.add_argument("--heuristic")
        p.add_argument("--time", type=float, default=10.0, help="limite de temps (s)")
        p.add_argument("--memory", type=int, default=2_000_000, help="limite de nœuds en mémoire")
        p.add_argument("--json", action="store_true", help="sortie JSON")

    e = sub.add_parser("experiences", help="expérience comparative")
    e.add_argument("--time", type=float, default=3.0)
    e.add_argument("--memory", type=int, default=500_000)
    e.add_argument("--out", default="resultats")

    sub.add_parser("catalog")
    sub.add_parser("tools")

    from . import game_api
    agent_help = "ex. humain, aleatoire, minimax:temps=1,profondeur=6,eval=fenetres, mcts:temps=1,sims=5000,c=1.41"
    for name in ("jouer", "decider", "tournoi"):
        p = sub.add_parser(name)
        p.add_argument("game", choices=list(game_api.GAMES))
        p.add_argument("--param", action="append", help="clé=valeur (rows, cols, k ; piles pour nim)")
        p.add_argument("--coups", default="", help="coups déjà joués depuis le début, séparés par des espaces")
        p.add_argument("--json", action="store_true", help="sortie JSON")
        if name == "jouer":
            p.add_argument("-1", "--premier", default="humain", help="agent du premier joueur ; " + agent_help)
            p.add_argument("-2", "--second", default="minimax:temps=1", help="agent du second joueur")
            p.add_argument("-q", "--quiet", action="store_true", help="n'affiche que l'issue")
        elif name == "decider":
            p.add_argument("-a", "--agent", default="minimax:temps=1", help=agent_help)
        else:
            p.add_argument("-a", default="minimax:temps=0.5", help="agent A ; " + agent_help)
            p.add_argument("-b", default="mcts:temps=0.5", help="agent B")
            p.add_argument("-n", type=int, default=10, help="nombre de parties")
            p.add_argument("--ouvertures", type=int, default=0,
                           help="demi-coups aléatoires au début de chaque paire de parties")
    ex = sub.add_parser("experiences-jeux", help="expériences du rapport TP2")
    ex.add_argument("--rapide", action="store_true", help="budgets et nombres de parties réduits")
    ex.add_argument("--out", default="resultats/tp2")
    sub.add_parser("jeux")
    sub.add_parser("outils-jeux")

    args = ap.parse_args(argv)
    cmd = args.cmd or "web"

    if cmd == "web":
        from .web.server import serve
        serve(port=getattr(args, "port", 8000), open_browser=not getattr(args, "no_browser", False))
    elif cmd in ("solve", "compare", "check"):
        req = {"problem": args.problem, "params": _params(args), "strategy": args.strategy,
               "mode": args.mode, "heuristic": args.heuristic,
               "limits": {"max_time": args.time, "max_memory_nodes": args.memory}}
        res = getattr(api, cmd)(req)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
        elif cmd == "solve":
            print(res["report"])
            if res.get("expression"):
                print(f"Expression : {res['expression']}")
        elif cmd == "compare":
            from .experiments import table
            rows = [{"strategie": r["strategy"], "mode": r["mode"], "statut": r["status"], "cout": r["cost"],
                     "profondeur": r["depth"], "generes": r["generated"], "developpes": r["expanded"],
                     "max_open": r["max_frontier"], "temps_s": round(r["time_s"], 4)} for r in res["rows"]]
            print(f"{res['problem']}  (h = {res['heuristic']})\n")
            print(table(rows, list(rows[0])))
        else:
            print(json.dumps(res, ensure_ascii=False, indent=2))
    elif cmd == "experiences":
        from .experiments import main as run
        run(args.time, args.memory, args.out)
    elif cmd in ("jouer", "decider", "tournoi"):
        from . import game_cli
        params = _params(args)
        moves = args.coups.split()
        if args.json:
            req = {"game": args.game, "params": params, "moves": moves}
            if cmd == "jouer":
                res = game_api.play(req | {"first": args.premier, "second": args.second})
            elif cmd == "decider":
                res = game_api.decide(req | {"agent": args.agent})
            else:
                res = game_api.tournament(req | {"a": args.a, "b": args.b, "n": args.n,
                                                "openings": args.ouvertures})
            print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
        elif cmd == "jouer":
            game_cli.play(args.game, params, [args.premier, args.second], moves, args.quiet)
        elif cmd == "decider":
            game_cli.decide(args.game, params, args.agent, moves)
        else:
            game_cli.tournament(args.game, params, args.a, args.b, args.n, args.ouvertures)
    elif cmd == "experiences-jeux":
        from .game_experiments import main as run
        run(args.out, quick=args.rapide)
    elif cmd == "jeux":
        print(json.dumps(game_api.catalog(), ensure_ascii=False, indent=2))
    elif cmd == "outils-jeux":
        print(json.dumps(game_api.tool_definitions(), ensure_ascii=False, indent=2))
    elif cmd == "catalog":
        print(json.dumps(api.catalog(), ensure_ascii=False, indent=2))
    elif cmd == "tools":
        print(json.dumps(api.tool_definitions(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
