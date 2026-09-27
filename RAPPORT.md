# AUSSI : expérience comparative des stratégies de recherche

Données complètes : [resultats/RESULTATS.md](resultats/RESULTATS.md), [resultats/strategies.csv](resultats/strategies.csv),
[resultats/heuristiques.csv](resultats/heuristiques.csv). Pour reproduire : `python3 -m aussi experiences`.

## 1. Protocole

- **22 instances** couvrant les cinq familles : 7 labyrinthes (dont un pondéré, un avec portails, un en
  8 directions et un sans solution), 4 trajets routiers (dont un vers une ville isolée), 5 N-Puzzles
  (du 8-puzzle facile au 15-puzzle mélangé 400 coups), 4 jeux arithmétiques (dont un impossible) et
  2 équations.
- **4 stratégies × 2 modes** = 176 exécutions, toutes avec **le même code de recherche** ; seule la
  fonction de priorité change. Heuristique par défaut de chaque problème (toutes admissibles et consistantes).
- **Limites** par exécution : 3 s et 500 000 nœuds en mémoire. Au-delà, AUSSI se met en « arrêt de travail ».
- **Expérience 2** : A* en Graph-Search, avec plusieurs heuristiques sur 8 instances.
- Temps mesurés sur une seule exécution (Python 3.14, MacBook Pro) : il faut les lire comme des ordres de
  grandeur. Les compteurs de nœuds, eux, sont déterministes.

## 2. Synthèse

| Stratégie | Mode | Résolues | Optimales | Arrêts | Développés (médiane) | Max mémoire (médiane) |
|---|---|---:|---:|---:|---:|---:|
| BFS | graph | 17/19 | 12/18 | 2 | 114 | 156 |
| BFS | tree | 10/19 | 7/18 | 11 | 257 | 874 |
| UCS | graph | 17/19 | 17/18 | 2 | 155 | 159 |
| UCS | tree | 8/19 | 8/18 | 13 | 2 105 | 3 036 |
| Greedy | graph | **19/19** | 10/18 | 0 | 94 | 100 |
| Greedy | tree | 10/19 | 7/18 | 11 | 8 | 17 |
| **A\*** | **graph** | 18/19 | **18/18** | 1 | 96 | 122 |
| A\* | tree | 14/19 | 14/18 | 7 | 662 | 62,5 |

*19 instances ont une solution trouvée par au moins une stratégie ; le coût optimal est connu pour 18 d'entre
elles (toutes sauf le 15-puzzle difficile). Les médianes portent sur les exécutions réussies, donc sur des
ensembles d'instances différents d'une ligne à l'autre : il faut les comparer avec prudence.*

## 3. Observations

### 3.1 A* en Graph-Search est le meilleur compromis

C'est la seule configuration qui trouve **toujours** la solution optimale quand elle trouve une solution
(18/18). Elle développe en outre beaucoup moins de nœuds que les stratégies non informées :

| Instance | BFS graph | UCS graph | A\* graph | Réduction A\* / UCS |
|---|---:|---:|---:|---:|
| 8-puzzle moyen (28 coups) | 171 028 | 177 134 | 1 440 | ÷ 123 |
| 8-puzzle difficile (31 coups) | 181 347 | 181 438 | 6 744 | ÷ 27 |
| 15-puzzle facile (28 coups) | arrêt | arrêt | 1 128 | — |
| Labyrinthe complexe 61×61 | 926 | 937 | 662 | ÷ 1,4 |

Dans un labyrinthe, le gain est modeste : la distance de Manhattan ignore les murs, et le chemin réel fait
de longs détours. Au taquin, l'heuristique est bien plus informative et le gain atteint deux ordres de grandeur.

### 3.2 BFS n'est optimal qu'à coûts uniformes

BFS minimise le **nombre d'actions**, pas le coût. Dès que les coûts varient, il se trompe :

| Instance | BFS (coût / profondeur) | Optimal UCS / A\* (coût / profondeur) |
|---|---|---|
| Labyrinthe pondéré | 204 / 92 | 203 / 100 |
| Labyrinthe en 8 directions | 31,5 / 19 | 22,5 / 20 |
| Rouyn-Noranda → Gaspé | 1 701,2 km / 8 | 1 588,9 km / 9 |
| Gatineau → Baie-Comeau | 912,7 km / 6 | 881,9 km / 9 |

Le chemin optimal est souvent **plus long en étapes** : il fait un détour pour éviter l'eau ou la montagne,
ou il passe par plus de villes pour rouler moins. Sur les problèmes à coût unitaire (taquin, jeu arithmétique,
équations), BFS est optimal.

### 3.3 Greedy est rapide mais ne garantit rien

Greedy en Graph-Search est la seule configuration qui résout **les 19 instances**, et c'est de loin la plus
rapide (0,14 s au total). C'est même la seule qui résout le 15-puzzle difficile : 437 nœuds développés, alors
qu'A* s'arrête après 184 394. Mais la qualité des solutions en souffre :

- 15-puzzle difficile : 92 coups, sans point de comparaison optimal ;
- 8-puzzle difficile : 47 coups au lieu de 31 ; 8-puzzle moyen : 48 au lieu de 28 ;
- labyrinthe pondéré : coût 353 au lieu de 203 (+74 %).

Greedy convient donc quand il faut **une** solution vite, et A* quand il faut **la meilleure**.

### 3.4 Tree-Search : catastrophique dès qu'il y a des cycles

Dans un labyrinthe, un réseau routier ou un taquin, les actions sont réversibles : sans mémoire des états
visités, la recherche revisite sans fin les mêmes états.

- Sur 28 exécutions de labyrinthes en Tree-Search, **seulement 5 réussissent** : BFS, UCS et A* sur le
  7×10, puis Greedy et A* sur le terrain ouvert en 8 directions. Toutes les autres atteignent la limite de
  500 000 nœuds, y compris sur le labyrinthe emmuré, où il est impossible de conclure. Greedy tourne même en rond sur le labyrinthe 7×10 (799 232 nœuds développés pour une solution à 11 pas),
  car il oscille entre deux cases qui lui semblent proches du but.
- **UCS en Tree-Search** est le pire (13 arrêts). Sur Rouyn-Noranda → Gaspé, il échoue là où la version
  Graph-Search ne développe que 26 nœuds.
- **A\* en Tree-Search** survit bien mieux (14 réussites) : une bonne heuristique limite les retours en arrière.
  Au 8-puzzle difficile, il trouve l'optimum (31), mais en développant 207 865 nœuds contre 6 744 en
  Graph-Search (×31).

Tree-Search n'a d'intérêt que lorsque l'espace d'états est **un arbre sans cycles**. C'est le cas du jeu
arithmétique : chaque opération retire un nombre, donc la profondeur est bornée. Il y trouve toujours la
solution, et avec moins de mémoire que Graph-Search (Greedy/A* : 44 à 46 nœuds contre 256 à 337), puisqu'il
ne maintient pas la table `reached`.

### 3.5 Détection des problèmes sans solution

| Instance | Comment AUSSI conclut | Coût de la preuve |
|---|---|---|
| Labyrinthe emmuré | exploration complète (graph) | 149 nœuds |
| Gaspé → Îles-de-la-Madeleine | exploration complète (graph) | 27 nœuds |
| 1, 1, 1, 1 → 24 | exploration complète (graph **et** tree, car l'arbre est fini) | 20 / 1 615 nœuds |
| 8-puzzle insoluble | `precheck` : parité des inversions | 0 nœud |
| 2x + 3 = 2x + 5 | `precheck` : les x s'annulent, contradiction | 0 nœud |

En Tree-Search sur un graphe à cycles, l'exploration ne se termine jamais. AUSSI répond alors « arrêt de
travail » et **ne prétend pas** qu'il n'y a pas de solution. Cette distinction entre `echec` (aucune solution,
c'est prouvé) et `arret` (on ne sait pas) est essentielle pour un agent fiable.

### 3.6 Influence de l'heuristique (A*, Graph-Search)

| Instance | h = 0 (≡ UCS) | mal placées | Manhattan | conflits linéaires |
|---|---:|---:|---:|---:|
| 8-puzzle moyen | 177 134 | 59 067 | 1 440 | **786** |
| 8-puzzle difficile | 181 438 | 121 528 | 6 744 | **3 835** |
| 15-puzzle facile | — | arrêt | 1 128 | **627** |

*(nœuds développés ; le coût trouvé est identique partout : 28, 31 et 28.)*

Plus l'heuristique admissible est **informée** (plus proche de h\*), moins A* développe de nœuds, et le
facteur de branchement effectif b\* baisse de 1,54 à 1,24. L'optimalité est toujours préservée.

Heuristiques **non admissibles** :

- **vol_oiseau × 2** (navigation) : 15 nœuds au lieu de 26, mais un trajet de 1 634,5 km au lieu de
  1 588,9 km. La surestimation fait perdre l'optimalité, comme le prédit la théorie. Le vérificateur
  d'AUSSI la signale : `NON admissible`.
- **manhattan_naif** (labyrinthe à portails) : elle ignore les portails. Du côté du départ, elle surestime
  donc *tous* les nœuds d'environ la même quantité, portail compris. Le classement relatif des nœuds est
  préservé, si bien qu'A* emprunte quand même le portail et trouve l'optimum (45, avec 78 nœuds au lieu de 93).
  Une heuristique non admissible ne donne pas *toujours* une mauvaise réponse ; elle ne donne simplement
  plus de *garantie*.
- **Manhattan en 8 directions** : non admissible (la diagonale coûte √2 < 2), mais elle trouve ici l'optimum
  (22,5) avec 73 nœuds, contre 67 pour l'octile, qui est correcte.

## 4. Conclusions

1. **A\* + Graph-Search + heuristique consistante** est le choix par défaut : optimal, complet, et le plus
   économe parmi les méthodes optimales. C'est la configuration par défaut d'AUSSI.
2. La **qualité de l'heuristique** compte davantage que tout le reste : entre h = 0 et les conflits
   linéaires, le travail est divisé par 225 au 8-puzzle moyen.
3. **Greedy** est l'outil de secours quand A* dépasse les limites (15-puzzle difficile) : AUSSI peut
   renvoyer une solution non optimale plutôt qu'aucune.
4. **Tree-Search** n'est à réserver qu'aux espaces sans cycles (jeu arithmétique), où il économise la mémoire.
5. Les **limites** transforment un plantage potentiel (plusieurs Go de mémoire au 15-puzzle) en un diagnostic
   propre, et elles distinguent « impossible » de « trop difficile ».

**Pistes d'amélioration** : IDA\* pour le 15-puzzle (mémoire linéaire ; une nouvelle stratégie hors
file de priorité, donc un second moteur), bases de données de motifs (*pattern databases*) comme
heuristique, et répétition des mesures de temps pour obtenir des intervalles de confiance.
