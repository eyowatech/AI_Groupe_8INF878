# AUSSI — Agent Universel de Support Super Intelligent

Moteur générique de résolution de problèmes par recherche dans un espace d'états.
Un **seul** algorithme, `SEARCH(problem, strategy, mode)`, résout cinq familles de
problèmes très différentes ; seules la formulation du problème et son heuristique changent.

Python ≥ 3.10, **aucune dépendance externe** (bibliothèque standard uniquement).

## Démarrage rapide

```bash
python3 -m aussi                     # interface web locale → http://127.0.0.1:8000
python3 -m aussi solve labyrinthe --preset complexe -s astar -m graph
python3 -m aussi solve navigation --param start=Alma --param goal=Sherbrooke
python3 -m aussi solve npuzzle --preset 15_difficile --time 5       # arrêt de travail
python3 -m aussi solve arithmetique --param numbers="2 3 5 7" --param target=24
python3 -m aussi solve equation --param equation="5x - 7 = 2x + 8"
python3 -m aussi compare npuzzle --preset moyen                     # 4 stratégies × 2 modes
python3 -m aussi check navigation --heuristic vol_oiseau_x2          # vérifier une heuristique
python3 -m aussi experiences                                         # expérience → resultats/
python3 -m unittest discover tests                                   # 18 tests
```

Lien direct vers l'interface (pratique pour une démo, ou pour un LLM qui génère un lien) :
`http://127.0.0.1:8000/#problem=npuzzle&preset=difficile&strategy=astar&mode=tree&run=solve`

## Architecture

```
aussi/
├── core/                    ← le moteur : ne connaît AUCUN problème
│   ├── problem.py           contrat abstrait Problem
│   ├── strategies.py        BFS, UCS, Greedy, A* (+ DFS, Weighted A* en extension)
│   ├── search.py            SEARCH(problem, strategy, mode, limits) + statistiques
│   └── heuristic_check.py   vérification empirique admissibilité / consistance
├── problems/                ← formulations : ne connaissent AUCUN algorithme
│   ├── maze.py              labyrinthes (murs, terrains pondérés, portails, 8 directions)
│   ├── navigation.py        villes du Québec + routes pondérées (mini Google Maps)
│   ├── npuzzle.py           taquin n×n
│   ├── arithmetic.py        jeu du 24 / « Le compte est bon »
│   └── equation.py          équations linéaires a·x + b = c·x + d
├── api.py                   API JSON unique : catalog / solve / compare / check / tool_definitions
├── web/                     serveur http.server + index.html (client de l'API)
├── experiments.py           expérience comparative
└── __main__.py              ligne de commande (client de l'API)
```

Le couplage est volontairement à sens unique : `problems` et les interfaces dépendent de
`core`, jamais l'inverse.

### Le contrat `Problem`

| Méthode | Rôle |
|---|---|
| `initial_state`, `actions(s)`, `result(s, a)`, `is_goal(s)` | formulation (obligatoire) |
| `step_cost(s, a, s')` | coût d'une action (1 par défaut) |
| `state_key(s)` | clé des états répétés en Graph-Search (ex. jeu du 24 : seules les *valeurs* comptent) |
| `precheck()` | preuve optionnelle d'absence de solution (parité du taquin, `2x+3 = 2x+5`) |
| `heuristics` + `h_<nom>(s)` | heuristiques nommées ; `set_heuristic(callable)` accepte aussi une fonction quelconque |
| `describe_action`, `render`, `to_view`, `view_meta` | présentation (trace, interface) |

### Une stratégie = une fonction de priorité

Le moteur est une recherche meilleur-d'abord unique (file de priorité). Une stratégie
fournit seulement `priority(node, order)` :

| Stratégie | Priorité | Remarques |
|---|---|---|
| BFS | `order` (FIFO) | test du but à la génération ; en Graph-Search la 1re atteinte d'un état gagne |
| UCS | `g(n)` | |
| Greedy | `h(n)` | |
| A* | `(g+h, h)` | à f égal, on préfère le nœud le plus proche du but |
| DFS *(extension)* | `-order` (LIFO) | 5 lignes |
| Weighted A* *(extension)* | `g + 2h` | 5 lignes |

Ajouter une stratégie :

```python
@register
class MaStrategie(Strategy):
    name, label = "ma", "Ma stratégie"
    uses_heuristic = True
    def priority(self, node, order):
        return node.g + 3 * node.h
```

Elle apparaît immédiatement dans l'interface, la CLI et les outils LLM.

### Tree-Search vs Graph-Search

`mode="tree"` : aucune mémoire des états visités (un état peut être développé plusieurs fois,
et les cycles ne sont pas détectés). `mode="graph"` : table `reached` (clé d'état → meilleur g
connu), comme `BEST-FIRST-SEARCH` de Russell & Norvig (4e éd.). Un état déjà atteint n'est
réinséré que si l'on trouve un chemin strictement moins coûteux (UCS, Greedy, A*) ; les
entrées périmées de la file sont ignorées au dépilement. Cette réouverture garde A* optimal
même avec une heuristique admissible mais non consistante.

### Arrêt de travail (limites)

`Limits(max_time=10, max_memory_nodes=2_000_000, max_expanded=None, max_depth=None)`.
Quand une limite est atteinte, AUSSI s'arrête proprement avec le statut `arret` et le
motif (« Arrêt de travail : limite mémoire atteinte… ») au lieu de saturer la machine.
`MemoryError` est aussi interceptée. Une recherche tronquée par `max_depth` est
rapportée comme `arret`, jamais comme « aucune solution ».

Les trois statuts possibles :

- `succes` : solution trouvée ;
- `echec` : aucune solution (prouvée par `precheck` ou espace d'états entièrement exploré) ;
- `arret` : une limite a été atteinte, on ne sait pas.

### Statistiques rapportées

Solution (trace des actions), coût, profondeur, nœuds générés, nœuds développés, taille
max de OPEN, nombre max de nœuds en mémoire (OPEN + `reached`), temps, facteur de
branchement effectif b*.

## Les problèmes

| Problème | Préréglages | Heuristiques (✔ = admissible et consistante) |
|---|---|---|
| Labyrinthe | simple, moyen, complexe (61×61 avec boucles), pondéré, portails, diagonal, sans_solution ; ou grille libre | manhattan ✔, octile ✔, euclidienne ✔, manhattan_naif ✘ (ignore les portails), zero |
| Navigation | 28 villes, 38 routes ; Îles-de-la-Madeleine isolée (aucune route) | vol_oiseau ✔, longitude ✔ (moins informée), vol_oiseau_x2 ✘, zero |
| N-Puzzle | facile, moyen, difficile (31 coups), 15_facile, 15_difficile, insoluble ; ou tuiles / mélange libres | manhattan ✔, mal_placees ✔, conflits_lineaires ✔, zero |
| Arithmétique | 24_2357, 24_fractions, 24_3388, 24_impossible, compte_est_bon, compte_impossible ; ou nombres + cible libres | operations_restantes ✔, ecart_cible ✘ (pour Greedy), zero |
| Équation | simple, deux_membres, fractions, x_a_droite, sans_solution, infinie ; ou équation libre | defauts_div2 ✔, defauts ✘, zero |

Justifications :

- **Labyrinthe** : chaque pas coûte au moins `coût_min` (le terrain le moins cher), donc
  `coût_min × distance` est un minorant. Avec des portails, h = min(distance directe,
  distance au portail le plus proche + 1 + distance du portail le plus proche du but).
  En 8 directions, Manhattan surestime (une diagonale coûte √2 < 2) : il faut l'octile.
- **Navigation** : chaque route mesure `distance orthodromique × détour` avec un détour ≥ 1,
  donc le vol d'oiseau est un minorant, et il est consistant par l'inégalité triangulaire.
- **Équation** : une action corrige au plus 2 « défauts » (termes mal placés), d'où ⌈défauts/2⌉.

`python3 -m aussi check …` (ou le bouton « Vérifier l'heuristique ») teste la consistance
sur tous les arcs de l'espace d'états (ou un échantillon de 20 000 états) et l'admissibilité
le long d'un chemin optimal calculé par UCS. C'est ce qui permet de changer d'heuristique
« sans causer de problèmes majeurs » : une heuristique fautive est détectée immédiatement.

## Vers un LLM

L'interface web et la CLI ne sont que des clients de `aussi/api.py`, qui ne manipule que des
dictionnaires JSON. `api.tool_definitions()` (ou `python3 -m aussi tools`, ou
`GET /api/tools`) renvoie trois outils décrits en JSON Schema (`aussi_solve`, `aussi_compare`,
`aussi_check_heuristic`), directement utilisables comme *tools* d'un LLM. `api.TOOLS` associe
chaque nom d'outil à sa fonction : une boucle agentique n'a qu'à appeler
`api.TOOLS[name](input)` et renvoyer le résultat au modèle.

## Expérience comparative

Voir [RAPPORT.md](RAPPORT.md) pour l'analyse, et [resultats/](resultats/) pour les données
brutes (`strategies.csv`, `heuristiques.csv`, `RESULTATS.md`).
