"""Serveur web local d'AUSSI (bibliothèque standard uniquement).

    GET  /                 interface
    GET  /api/catalog      problèmes, préréglages, heuristiques, stratégies, modes
    GET  /api/tools        définitions d'outils pour un LLM
    POST /api/solve        {problem, params, strategy, mode, heuristic, limits}
    POST /api/compare      {problem, params, heuristic, limits}
    POST /api/check        {problem, params, heuristic}

L'interface n'est qu'un client de l'API JSON : un LLM (ou tout autre
programme) peut l'utiliser exactement de la même façon.
"""

from __future__ import annotations

import json
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .. import api

STATIC = Path(__file__).parent / "index.html"
POST_ROUTES = {"/api/solve": api.solve, "/api/compare": api.compare, "/api/check": api.check}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False, default=str).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, STATIC.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/catalog":
            self._json(200, api.catalog())
        elif self.path == "/api/tools":
            self._json(200, api.tool_definitions())
        else:
            self._json(404, {"error": "introuvable"})

    def do_POST(self):
        route = POST_ROUTES.get(self.path)
        if route is None:
            return self._json(404, {"error": "introuvable"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(length) or b"{}")
            self._json(200, route(req))
        except (ValueError, KeyError) as e:
            self._json(400, {"error": str(e)})
        except Exception as e:  # noqa: BLE001 — on renvoie l'erreur au client
            traceback.print_exc()
            self._json(500, {"error": f"{type(e).__name__}: {e}"})

    def log_message(self, fmt, *args):
        print(f"[AUSSI] {self.address_string()} {fmt % args}")


def serve(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    print(f"AUSSI écoute sur {url}  (Ctrl+C pour arrêter)")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAUSSI se met en veille.")
    finally:
        server.server_close()
