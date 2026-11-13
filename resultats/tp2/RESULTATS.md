# AUSSI TP2 : résultats bruts

Généré par `python -m aussi experiences-jeux` (Python 3.14.3, arm64), durée 851 s.
Les temps et les compteurs qui en dépendent (profondeur, nœuds, simulations) varient d'une machine à l'autre.

## 1. Tests tactiques (coup correct / essais ; MCTS répété avec des graines différentes)

| position | minimax 0.05 s | minimax 0.2 s | minimax 1.0 s | mcts 0.05 s | mcts 0.2 s | mcts 1.0 s |
|---|---|---|---|---|---|---|
| morpion : gagner (au lieu de bloquer) | 1/1 | 1/1 | 1/1 | 10/10 | 10/10 | 10/10 |
| morpion : bloquer | 1/1 | 1/1 | 1/1 | 10/10 | 10/10 | 10/10 |
| morpion : éviter la fourchette | 1/1 | 1/1 | 1/1 | 10/10 | 10/10 | 10/10 |
| P4 : gagner (horizontal) | 1/1 | 1/1 | 1/1 | 10/10 | 10/10 | 10/10 |
| P4 : gagner (vertical) | 1/1 | 1/1 | 1/1 | 10/10 | 10/10 | 10/10 |
| P4 : bloquer (horizontal) | 1/1 | 1/1 | 1/1 | 10/10 | 10/10 | 10/10 |
| P4 : bloquer (vertical) | 1/1 | 1/1 | 1/1 | 10/10 | 10/10 | 10/10 |
| P4 : créer un trois ouvert (gain en 3) | 1/1 | 1/1 | 1/1 | 10/10 | 10/10 | 10/10 |
| P4 : empêcher un trois ouvert | 1/1 | 1/1 | 1/1 | 9/10 | 10/10 | 10/10 |

## 2. Tic-Tac-Toe : validation

| A | B | parties | victoires_A | nulles | victoires_B | temps_moyen_A_s |
|---|---|---:|---:|---:|---:|---:|
| minimax:temps=none | aleatoire | 100 | 94 | 6 | 0 | 0.027 |
| minimax:temps=none | minimax:temps=none | 2 | 0 | 2 | 0 | 0.019 |
| mcts:temps=none,sims=50 | aleatoire | 20 | 19 | 1 | 0 | 0.001 |
| mcts:temps=none,sims=50 | minimax:temps=none | 20 | 0 | 13 | 7 | 0.001 |
| mcts:temps=none,sims=200 | aleatoire | 20 | 18 | 1 | 1 | 0.002 |
| mcts:temps=none,sims=200 | minimax:temps=none | 20 | 0 | 15 | 5 | 0.002 |
| mcts:temps=none,sims=1000 | aleatoire | 20 | 19 | 1 | 0 | 0.009 |
| mcts:temps=none,sims=1000 | minimax:temps=none | 20 | 0 | 20 | 0 | 0.007 |
| mcts:temps=none,sims=5000 | aleatoire | 20 | 19 | 1 | 0 | 0.037 |
| mcts:temps=none,sims=5000 | minimax:temps=none | 20 | 0 | 20 | 0 | 0.031 |

## 3. Alpha-bêta au Tic-Tac-Toe (exploration complète)

| position | alpha_beta | profondeur | noeuds_derniere_iteration | noeuds_total | temps_s | coup | valeur |
|---|---|---:|---:|---:|---:|---|---:|
| grille vide | True | 9 | 20 865 | 48 842 | 0.111 | 1 | 0 |
| grille vide | False | 9 | 549 945 | 1 290 105 | 2.801 | 1 | 0 |
| après « 1 » | True | 8 | 2 069 | 5 888 | 0.013 | 5 | 0 |
| après « 1 » | False | 8 | 59 704 | 140 496 | 0.299 | 5 | 0 |
| après « 5 » | True | 8 | 2 458 | 6 674 | 0.014 | 1 | 0 |
| après « 5 » | False | 8 | 55 504 | 131 976 | 0.276 | 1 | 0 |

## 4. Puissance 4 : ce que le budget permet

| position | temps_s | moteur | profondeur | noeuds | noeuds_par_s | simulations | coup |
|---|---:|---|---:|---:|---:|---:|---|
| vide | 0.100 | minimax (alpha-bêta, centre d'abord) | 6 | 7 384 | 73 793 | — | 4 |
| vide | 0.100 | minimax (alpha-bêta, ordre 1..7) | 5 | 6 585 | 65 841 | — | 3 |
| vide | 0.100 | minimax (sans alpha-bêta) | 4 | 6 285 | 62 838 | — | 4 |
| vide | 0.100 | mcts (c=√2) | — | 1 380 | — | 1 379 | 4 |
| vide | 0.500 | minimax (alpha-bêta, centre d'abord) | 8 | 38 102 | 76 201 | — | 4 |
| vide | 0.500 | minimax (alpha-bêta, ordre 1..7) | 6 | 33 942 | 67 881 | — | 4 |
| vide | 0.500 | minimax (sans alpha-bêta) | 5 | 30 801 | 61 599 | — | 3 |
| vide | 0.500 | mcts (c=√2) | — | 6 948 | — | 6 947 | 4 |
| vide | 1 | minimax (alpha-bêta, centre d'abord) | 9 | 77 139 | 77 138 | — | 4 |
| vide | 1 | minimax (alpha-bêta, ordre 1..7) | 6 | 67 092 | 67 091 | — | 4 |
| vide | 1 | minimax (sans alpha-bêta) | 5 | 60 775 | 60 775 | — | 3 |
| vide | 1 | mcts (c=√2) | — | 8 466 | — | 8 465 | 4 |
| vide | 2 | minimax (alpha-bêta, centre d'abord) | 9 | 155 374 | 77 686 | — | 4 |
| vide | 2 | minimax (alpha-bêta, ordre 1..7) | 7 | 130 809 | 65 404 | — | 3 |
| vide | 2 | minimax (sans alpha-bêta) | 5 | 122 492 | 61 246 | — | 3 |
| vide | 2 | mcts (c=√2) | — | 28 873 | — | 28 933 | 4 |
| milieu | 0.100 | minimax (alpha-bêta, centre d'abord) | 7 | 7 959 | 79 583 | — | 3 |
| milieu | 0.100 | minimax (alpha-bêta, ordre 1..7) | 5 | 6 359 | 63 581 | — | 3 |
| milieu | 0.100 | minimax (sans alpha-bêta) | 4 | 5 666 | 56 650 | — | 3 |
| milieu | 0.100 | mcts (c=√2) | — | 1 775 | — | 1 914 | 3 |
| milieu | 0.500 | minimax (alpha-bêta, centre d'abord) | 9 | 38 494 | 76 986 | — | 3 |
| milieu | 0.500 | minimax (alpha-bêta, ordre 1..7) | 7 | 33 243 | 66 485 | — | 3 |
| milieu | 0.500 | minimax (sans alpha-bêta) | 5 | 28 743 | 57 485 | — | 3 |
| milieu | 0.500 | mcts (c=√2) | — | 9 476 | — | 10 206 | 3 |
| milieu | 1 | minimax (alpha-bêta, centre d'abord) | 10 | 75 891 | 75 890 | — | 3 |
| milieu | 1 | minimax (alpha-bêta, ordre 1..7) | 7 | 66 219 | 66 217 | — | 3 |
| milieu | 1 | minimax (sans alpha-bêta) | 5 | 58 195 | 58 194 | — | 3 |
| milieu | 1 | mcts (c=√2) | — | 6 956 | — | 7 514 | 3 |
| milieu | 2 | minimax (alpha-bêta, centre d'abord) | 10 | 119 751 | 59 875 | — | 3 |
| milieu | 2 | minimax (alpha-bêta, ordre 1..7) | 8 | 129 352 | 64 675 | — | 3 |
| milieu | 2 | minimax (sans alpha-bêta) | 5 | 115 834 | 57 917 | — | 3 |
| milieu | 2 | mcts (c=√2) | — | 41 076 | — | 44 516 | 3 |

## 5. Puissance 4 : tournois (ouvertures aléatoires de 2 demi-coups, couleurs alternées)

| groupe | A | B | parties | victoires_A | nulles | victoires_B | score_A | prof_moy_A | sims_moy_A | prof_moy_B | sims_moy_B | duree_s |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| contre aléatoire | minimax:temps=0.2 | aleatoire | 10 | 10 | 0 | 0 | 1 | 5.380 | — | — | — | 9.400 |
| contre aléatoire | mcts:temps=0.2 | aleatoire | 10 | 10 | 0 | 0 | 1 | — | 16 538 | — | — | 10.2 |
| évaluations | minimax:temps=0.2,eval=fenetres_centre | minimax:temps=0.2,eval=neutre | 10 | 7 | 2 | 1 | 0.800 | 7.450 | — | 9.020 | — | 43.8 |
| évaluations | minimax:temps=0.2,eval=fenetres_centre | minimax:temps=0.2,eval=centre | 10 | 5 | 3 | 2 | 0.650 | 7.330 | — | 8.890 | — | 46.7 |
| évaluations | minimax:temps=0.2,eval=fenetres_centre | minimax:temps=0.2,eval=fenetres | 10 | 4 | 0 | 6 | 0.400 | 7.210 | — | 7.030 | — | 52.6 |
| minimax contre mcts | minimax:temps=0.1 | mcts:temps=0.1 | 10 | 7 | 0 | 3 | 0.700 | 5.890 | — | — | 9 106 | 25.4 |
| minimax contre mcts | minimax:temps=0.5 | mcts:temps=0.5 | 10 | 6 | 0 | 4 | 0.600 | 7.340 | — | — | 56 210 | 129.1 |
| minimax contre mcts | minimax:temps=1.0 | mcts:temps=1.0 | 10 | 6 | 1 | 3 | 0.650 | 7.700 | — | — | 105 642 | 257.3 |
| constante c | mcts:temps=0.2,c=0.5 | mcts:temps=0.2,c=1.414 | 10 | 7 | 0 | 3 | 0.700 | — | 20 075 | — | 17 294 | 54.4 |
| constante c | mcts:temps=0.2,c=3.0 | mcts:temps=0.2,c=1.414 | 10 | 3 | 0 | 7 | 0.300 | — | 11 376 | — | 13 880 | 51 |
