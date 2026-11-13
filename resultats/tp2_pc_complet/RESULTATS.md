# AUSSI TP2 : résultats bruts

Généré par `python -m aussi experiences-jeux` (Python 3.13.9, x86_64), durée 930 s.
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
| P4 : empêcher un trois ouvert | 1/1 | 1/1 | 1/1 | 8/10 | 10/10 | 10/10 |

## 2. Tic-Tac-Toe : validation

| A | B | parties | victoires_A | nulles | victoires_B | temps_moyen_A_s |
|---|---|---:|---:|---:|---:|---:|
| minimax:temps=none | aleatoire | 100 | 92 | 8 | 0 | 0.032 |
| minimax:temps=none | minimax:temps=none | 2 | 0 | 2 | 0 | 0.022 |
| mcts:temps=none,sims=50 | aleatoire | 20 | 18 | 1 | 1 | 0.001 |
| mcts:temps=none,sims=50 | minimax:temps=none | 20 | 0 | 12 | 8 | 0.001 |
| mcts:temps=none,sims=200 | aleatoire | 20 | 19 | 1 | 0 | 0.003 |
| mcts:temps=none,sims=200 | minimax:temps=none | 20 | 0 | 19 | 1 | 0.002 |
| mcts:temps=none,sims=1000 | aleatoire | 20 | 19 | 1 | 0 | 0.012 |
| mcts:temps=none,sims=1000 | minimax:temps=none | 20 | 0 | 20 | 0 | 0.009 |
| mcts:temps=none,sims=5000 | aleatoire | 20 | 19 | 1 | 0 | 0.051 |
| mcts:temps=none,sims=5000 | minimax:temps=none | 20 | 0 | 20 | 0 | 0.042 |

## 3. Alpha-bêta au Tic-Tac-Toe (exploration complète)

| position | alpha_beta | profondeur | noeuds_derniere_iteration | noeuds_total | temps_s | coup | valeur |
|---|---|---:|---:|---:|---:|---|---:|
| grille vide | True | 9 | 20 865 | 48 842 | 0.132 | 1 | 0 |
| grille vide | False | 9 | 549 945 | 1 290 105 | 3.361 | 1 | 0 |
| après « 1 » | True | 8 | 2 069 | 5 888 | 0.016 | 5 | 0 |
| après « 1 » | False | 8 | 59 704 | 140 496 | 0.360 | 5 | 0 |
| après « 5 » | True | 8 | 2 458 | 6 674 | 0.017 | 1 | 0 |
| après « 5 » | False | 8 | 55 504 | 131 976 | 0.330 | 1 | 0 |

## 4. Puissance 4 : ce que le budget permet

| position | temps_s | moteur | profondeur | noeuds | noeuds_par_s | simulations | coup |
|---|---:|---|---:|---:|---:|---:|---|
| vide | 0.100 | minimax (alpha-bêta, centre d'abord) | 6 | 6 793 | 67 917 | — | 4 |
| vide | 0.100 | minimax (alpha-bêta, ordre 1..7) | 5 | 6 232 | 62 304 | — | 3 |
| vide | 0.100 | minimax (sans alpha-bêta) | 4 | 5 898 | 58 974 | — | 4 |
| vide | 0.100 | mcts (c=√2) | — | 1 068 | — | 1 067 | 4 |
| vide | 0.500 | minimax (alpha-bêta, centre d'abord) | 8 | 35 128 | 70 253 | — | 4 |
| vide | 0.500 | minimax (alpha-bêta, ordre 1..7) | 6 | 30 798 | 61 594 | — | 4 |
| vide | 0.500 | minimax (sans alpha-bêta) | 5 | 27 541 | 55 081 | — | 3 |
| vide | 0.500 | mcts (c=√2) | — | 5 375 | — | 5 374 | 4 |
| vide | 1 | minimax (alpha-bêta, centre d'abord) | 9 | 68 433 | 68 432 | — | 4 |
| vide | 1 | minimax (alpha-bêta, ordre 1..7) | 6 | 59 789 | 59 788 | — | 4 |
| vide | 1 | minimax (sans alpha-bêta) | 5 | 56 573 | 56 572 | — | 3 |
| vide | 1 | mcts (c=√2) | — | 10 750 | — | 10 749 | 4 |
| vide | 2 | minimax (alpha-bêta, centre d'abord) | 9 | 136 944 | 68 471 | — | 4 |
| vide | 2 | minimax (alpha-bêta, ordre 1..7) | 7 | 112 215 | 56 107 | — | 3 |
| vide | 2 | minimax (sans alpha-bêta) | 5 | 115 541 | 57 770 | — | 3 |
| vide | 2 | mcts (c=√2) | — | 22 337 | — | 22 338 | 4 |
| milieu | 0.100 | minimax (alpha-bêta, centre d'abord) | 7 | 7 135 | 71 335 | — | 3 |
| milieu | 0.100 | minimax (alpha-bêta, ordre 1..7) | 5 | 5 644 | 56 429 | — | 3 |
| milieu | 0.100 | minimax (sans alpha-bêta) | 4 | 5 234 | 52 325 | — | 3 |
| milieu | 0.100 | mcts (c=√2) | — | 1 515 | — | 1 645 | 3 |
| milieu | 0.500 | minimax (alpha-bêta, centre d'abord) | 9 | 35 259 | 70 515 | — | 3 |
| milieu | 0.500 | minimax (alpha-bêta, ordre 1..7) | 6 | 29 147 | 58 289 | — | 3 |
| milieu | 0.500 | minimax (sans alpha-bêta) | 5 | 25 584 | 51 165 | — | 3 |
| milieu | 0.500 | mcts (c=√2) | — | 7 538 | — | 8 140 | 3 |
| milieu | 1 | minimax (alpha-bêta, centre d'abord) | 9 | 66 161 | 66 160 | — | 3 |
| milieu | 1 | minimax (alpha-bêta, ordre 1..7) | 7 | 58 630 | 58 629 | — | 3 |
| milieu | 1 | minimax (sans alpha-bêta) | 5 | 50 192 | 50 191 | — | 3 |
| milieu | 1 | mcts (c=√2) | — | 15 700 | — | 16 977 | 3 |
| milieu | 2 | minimax (alpha-bêta, centre d'abord) | 10 | 148 453 | 74 226 | — | 3 |
| milieu | 2 | minimax (alpha-bêta, ordre 1..7) | 8 | 134 590 | 67 294 | — | 3 |
| milieu | 2 | minimax (sans alpha-bêta) | 5 | 118 332 | 59 165 | — | 3 |
| milieu | 2 | mcts (c=√2) | — | 31 994 | — | 34 727 | 3 |

## 5. Puissance 4 : tournois (ouvertures aléatoires de 2 demi-coups, couleurs alternées)

| groupe | A | B | parties | victoires_A | nulles | victoires_B | score_A | prof_moy_A | sims_moy_A | prof_moy_B | sims_moy_B | duree_s |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| contre aléatoire | minimax:temps=0.1 | aleatoire | 10 | 10 | 0 | 0 | 1 | 4.680 | — | — | — | 3.500 |
| contre aléatoire | mcts:temps=0.1 | aleatoire | 10 | 10 | 0 | 0 | 1 | — | 4 627 | — | — | 5.300 |
| évaluations | minimax:temps=0.1,eval=fenetres_centre | minimax:temps=0.1,eval=neutre | 30 | 22 | 4 | 4 | 0.800 | 6.540 | — | 8.240 | — | 70.4 |
| évaluations | minimax:temps=0.1,eval=fenetres_centre | minimax:temps=0.1,eval=centre | 30 | 18 | 5 | 7 | 0.683 | 6.580 | — | 8.110 | — | 72.1 |
| évaluations | minimax:temps=0.1,eval=fenetres_centre | minimax:temps=0.1,eval=fenetres | 30 | 14 | 6 | 10 | 0.567 | 6.060 | — | 6.050 | — | 67.8 |
| minimax contre mcts | minimax:temps=0.1 | mcts:temps=0.1 | 10 | 8 | 0 | 2 | 0.800 | 5.930 | — | — | 5 979 | 23.9 |
| minimax contre mcts | minimax:temps=0.5 | mcts:temps=0.5 | 10 | 4 | 1 | 5 | 0.450 | 7.640 | — | — | 47 811 | 140.2 |
| minimax contre mcts | minimax:temps=1.0 | mcts:temps=1.0 | 10 | 7 | 0 | 3 | 0.700 | 7.640 | — | — | 67 027 | 245.7 |
| constante c | mcts:temps=0.2,c=0.5 | mcts:temps=0.2,c=1.414 | 10 | 6 | 0 | 4 | 0.600 | — | 17 223 | — | 14 794 | 61.1 |
| constante c | mcts:temps=0.2,c=3.0 | mcts:temps=0.2,c=1.414 | 10 | 4 | 1 | 5 | 0.450 | — | 12 066 | — | 13 255 | 61.9 |
