# AUSSI V3 : jeux adversariaux et généralisation

*8INF878 – Intelligence artificielle agentique, travail n° 2*

Code : [README.md](README.md#tp2--jeux-contre-un-adversaire). Données : [resultats/tp2/](resultats/tp2/RESULTATS.md).
Reproduire : `python3 -m aussi experiences-jeux` (~15 min) ; tests : `python3 -m unittest discover tests`.

## 1. Un moteur, plusieurs jeux

**Contrat `Game`** ([aussi/core/game.py](aussi/core/game.py)) : `initial_state`, `players`, `to_move`,
`actions`, `result`, `is_terminal`, `utility(s, p)`, plus des évaluations nommées `e_<nom>(s, p)`.
Trois décisions de conception en découlent :

- **États immuables.** `result` retourne un nouvel état (tuples, `NamedTuple`). Une recherche ne peut donc
  pas modifier la partie réelle, sans copie défensive ni « défaire le coup ». Seule `play_match` fait
  avancer la partie, et seulement après avoir vérifié que l'action rendue par l'agent est légale.
- **Actions opaques.** Les moteurs reçoivent une action de `actions` et la rendent à `result`, rien de
  plus. La conversion texte ↔ action (`action_to_str`, `parse_action`) appartient au jeu et ne sert qu'aux
  interfaces.
- **Point de vue explicite.** `utility` et les évaluations prennent le joueur en paramètre. Les moteurs
  demandent toujours la valeur pour le joueur au trait à la racine et déterminent MAX/MIN avec `to_move`,
  sans présumer l'alternance.

**Séparation en couches.** `core/` (moteurs, agents, boucle de partie) n'importe aucun jeu ; `games/`
n'importe aucun algorithme ; seul `game_cli.py` fait des `print` et des `input`. Un test vérifie par
expression régulière que `minimax.py` et `mcts.py` ne contiennent aucun nom de jeu ni aucune notion de
grille.

**Preuve par un troisième jeu.** Nim a été ajouté comme « jeu inconnu » : 65 lignes, commentaires compris, et aucune évaluation.
Sans toucher aux moteurs, Minimax y joue le coup prédit par la théorie (laisser un XOR des tas nul) et MCTS
trouve le coup gagnant. La base `AlignmentGame` factorise les règles communes à Tic-Tac-Toe et à
Puissance 4 (aligner k pions sur m×n) ; c'est une factorisation de *règles*, invisible pour les moteurs.
Elle rend aussi jouables les variantes (`--param rows=4 --param cols=4 --param k=3`).

**Interface évolutive.** Un agent rend une `Decision` (coup, temps, compteurs, explication) sans rien
afficher. L'humain est un `ExternalAgent(ask)`, et un LLM peut prendre sa place avec la même signature.
L'API JSON ([aussi/game_api.py](aussi/game_api.py)) représente une position par la liste des coups joués
depuis le début, sans état caché, et expose trois outils au format JSON Schema.

## 2. Minimax à approfondissement itératif

**Boucle.** Profondeurs 1, 2, 3, ... (1 = un demi-coup). Le temps est vérifié à chaque nœud ; à
l'échéance, une exception remonte toute la pile et l'itération en cours est abandonnée. AUSSI joue le
meilleur coup de la **dernière itération terminée**. Si aucune ne l'est, il joue le premier coup légal
(coup de secours). Arrêts anticipés : l'arbre a été exploré en entier (aucune coupure en profondeur, ce
qui arrive au Tic-Tac-Toe), une victoire forcée a été trouvée, ou tous les coups perdent.

**Valeurs.** Elles sont toujours exprimées du point de vue du joueur qui réfléchit. Une estimation est
dans [-1, 1]. Un état terminal vaut `u × (1000 − ply)`, où `u` est l'utilité normalisée et `ply` la
distance à la racine. Toute certitude domine donc toute estimation, et entre deux victoires AUSSI préfère
la plus rapide (entre deux défaites, la plus lente). Sans ce terme, Minimax peut « tourner autour » d'une
victoire acquise sans la conclure.

**Alpha-bêta et ordre des coups.** À chaque itération, les coups de la racine sont triés selon les
valeurs de l'itération précédente : c'est le principal bénéfice de l'approfondissement itératif, au-delà
de la gestion du temps. Le jeu peut aussi proposer un ordre dans `actions` : Puissance 4 donne les
colonnes du centre vers les bords. C'est une connaissance du jeu, pas du moteur.

**Compteurs.** *Profondeur terminée* : voir plus haut. *Nœuds* : appels à la fonction de valeur (feuilles
comprises, racine exclue), **cumulés sur toutes les itérations, y compris celle interrompue**. C'est le
travail réellement payé, pas seulement celui de l'itération retenue. À la racine, `≤ v` marque une borne
alpha-bêta : la valeur exacte n'a pas été calculée parce que le coup est prouvé moins bon.

## 3. Fonctions d'évaluation

Elles sont passées au moteur comme une simple fonction `f(état, joueur) → [-1, 1]`. En changer
(`eval=...` ou une fonction Python quelconque) ne touche pas à Minimax. Pour un jeu sans évaluation,
`e_neutre` (0) est héritée de `Game`.

| Jeu | Évaluation | Définition | Justification |
|---|---|---|---|
| Tic-Tac-Toe | `fenetres` (défaut) | Σ sur les lignes sans pion adverse de 4^(n−1) (n = mes pions), moins la même somme pour l'adversaire, puis `tanh` | Une ligne qui contient un pion adverse ne peut plus être gagnée ; plus une ligne libre est remplie, plus elle est proche de la victoire. |
| Puissance 4 | `fenetres` | Même formule sur les 69 fenêtres de 4 cases (1, 4, 16 pour 1, 2, 3 pions) | Une fenêtre de 4 cases est une victoire potentielle ; un trois ouvert vaut 16 fois un pion isolé. |
| Puissance 4 | `fenetres_centre` (défaut) | `fenetres` + 3 par pion dans la colonne centrale | Un pion au centre participe au plus grand nombre de fenêtres (heuristique classique). |
| Puissance 4 | `centre` | Seulement les pions au centre | Évaluation volontairement pauvre, pour la comparaison. |
| Tous | `neutre` | 0 | Repli pour un jeu inconnu. |

La pondération géométrique (×4) garantit qu'une fenêtre à n+1 pions pèse plus que plusieurs fenêtres à
n pions. `tanh` ramène le score dans ]−1, 1[ sans saturer, et garde l'estimation sous toute valeur prouvée.

## 4. MCTS (UCT)

Une simulation = les quatre étapes complètes ([aussi/core/mcts.py](aussi/core/mcts.py)).
**Sélection** : on descend par UCT = W/N + c·√(ln N_parent / N) tant que le nœud est entièrement développé.
**Expansion** : un nœud qui a encore des actions non essayées en développe une, tirée au hasard.
**Simulation** : coups uniformes parmi les actions légales jusqu'à la fin. **Rétropropagation** :
chaque nœud ajoute la récompense (1 victoire, 0,5 nulle, 0 défaite) **du joueur qui a joué le coup menant à
lui**. C'est ce joueur qui choisit entre les frères à l'étape de sélection, donc UCT maximise toujours le
point de vue de celui qui décide, sans inversion de signe. C'est cette convention qui rend le code
indépendant du jeu.

**Enfants non visités.** Un enfant n'est créé qu'au moment de sa première simulation, et UCT ne
s'applique qu'une fois toutes les actions essayées. Il n'y a donc jamais de division par N = 0, et chaque
coup est essayé au moins une fois avant d'être départagé.

**Budget et choix final.** Temps et/ou nombre de simulations : on s'arrête dès que l'un des deux est
épuisé. À la racine, AUSSI joue l'action **la plus visitée**, un critère plus robuste que la meilleure
moyenne, qui peut reposer sur peu de visites. Le coup de secours est le premier coup légal. **Affichage** :
nombre de simulations terminées, puis visites N et Q = W/N de chaque action racine, Q étant le gain moyen
du joueur qui réfléchit. La somme des N à la racine égale le nombre de simulations (vérifié par un test).

## 5. Expériences

Machine : MacBook Pro (arm64), Python 3.14, un seul cœur, exécution séquentielle. Les compteurs liés au
temps (profondeur, nœuds, simulations) dépendent de la machine. Pour éviter que deux agents déterministes
ne rejouent toujours la même partie, les tournois de Puissance 4 partent d'**ouvertures aléatoires de
2 demi-coups**, chacune jouée deux fois en inversant les couleurs.

### 5.1 Validation tactique et Tic-Tac-Toe

- **Positions tactiques** (9 positions : gagner, bloquer, éviter la fourchette, créer ou empêcher un trois
  ouvert à Puissance 4). Minimax les réussit toutes dès 0,05 s. MCTS réussit 89/90 essais à 0,05 s (une
  erreur sur « empêcher un trois ouvert », qui demande de voir 4 demi-coups plus loin) et 90/90 à partir de
  0,2 s.
- **Minimax complet** (sans limite de temps, il explore jusqu'aux états terminaux) contre l'aléatoire :
  **94 victoires, 6 nulles, 0 défaite sur 100 parties**, en alternant qui commence. Minimax contre Minimax :
  nulle, la valeur théorique du jeu (la racine vaut 0).
- **MCTS contre Minimax parfait** : il perd 7 parties sur 20 avec 50 simulations par coup et 5 sur 20 avec
  200, puis fait **20 nulles sur 20 dès 1 000 simulations**. MCTS converge vers le jeu parfait quand le
  budget couvre l'arbre, qui est petit (moins de 6 000 positions distinctes).

### 5.2 Effet d'alpha-bêta (Tic-Tac-Toe, arbre complet)

| Position | Sans élagage | Alpha-bêta | Réduction |
|---|---:|---:|---:|
| Grille vide (profondeur 9) | 549 945 nœuds, 2,8 s | 20 865 nœuds, 0,11 s | ×26 |
| Après « 1 » | 59 704 | 2 069 | ×29 |

Même coup et même valeur (0), comme le garantit la théorie. 549 945 est exactement le nombre de nœuds de
l'arbre de jeu complet du Tic-Tac-Toe, ce qui valide aussi le compteur. Le coût total cumulé sur toutes les
itérations (48 842) n'est que 2,3 fois celui de la dernière : le surcoût de l'approfondissement itératif
reste modeste.

### 5.3 Puissance 4 : ce que le budget achète

<!-- RESULTATS_PROFONDEUR -->

### 5.4 Puissance 4 : tournois

<!-- RESULTATS_TOURNOIS -->

## 6. Limites et pistes

- **Table de transposition.** Au Puissance 4, beaucoup d'ordres de coups mènent à la même position. Une
  table indexée sur l'état (déjà hachable) avec des bornes exactes, inférieures ou supérieures ferait
  gagner une à deux profondeurs.
- **Effet d'horizon.** L'évaluation est appelée sur des positions instables (une menace immédiate juste
  derrière la profondeur limite). Une extension de recherche sur les coups forcés réduirait ce défaut.
- **MCTS.** Réutiliser le sous-arbre d'un coup à l'autre ; remplacer les simulations uniformes par des
  simulations « légères » (jouer un coup gagnant ou bloquant quand il existe) ; RAVE. Toutes ces
  améliorations gardent le moteur générique si la politique de simulation devient un paramètre, comme
  l'évaluation pour Minimax.
- **Performance.** Python plafonne à environ 75 000 nœuds/s. Une représentation par masques de bits
  (*bitboards*) accélérerait Puissance 4 d'un ordre de grandeur, sans toucher aux moteurs.
