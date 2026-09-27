"""Point d'entrée : python -m aussi <commande>

    web                              interface web locale (défaut)
    solve PROBLEME [options]         résoudre et afficher le rapport
    compare PROBLEME [options]       toutes les stratégies × modes
    check PROBLEME [options]         vérifier l'heuristique
    experiences                      expérience comparative -> resultats/
    catalog | tools                  catalogue / définitions d'outils LLM (JSON)

Exemples :
    python -m aussi solve labyrinthe --preset complexe -s astar -m graph
    python -m aussi solve navigation --param start=Alma --param goal=Sherbrooke
    python -m aussi solve npuzzle --preset 15_difficile -s astar --time 5
    python -m aussi solve arithmetique --param numbers="2 3 5 7" --param target=24
    python -m aussi solve equation --param equation="5x - 7 = 2x + 8"
"""

from __future__ import annotations

import argparse
import json
import sys

from . import api


def _params(args) -> dict:
    params = {}
    if args.preset:
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
    elif cmd == "catalog":
        print(json.dumps(api.catalog(), ensure_ascii=False, indent=2))
    elif cmd == "tools":
        print(json.dumps(api.tool_definitions(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
