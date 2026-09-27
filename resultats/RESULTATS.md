# AUSSI — résultats de l'expérience comparative

Limites par exécution : 3.0 s, 500,000 nœuds en mémoire. « arret » = AUSSI s'est mis en arrêt de travail (limite atteinte). Temps mesurés sur une seule exécution : ordre de grandeur seulement.

## Synthèse par stratégie et mode

22 instances. « Résolues » : sur les instances dont une solution a été trouvée par au moins une stratégie. « Optimales » : coût égal au coût optimal (UCS/A*), sur les instances où ce coût est connu.

| Stratégie | Mode | Résolues | Optimales | Arrêts (limite) | Développés (médiane) | Max mémoire (médiane) | Temps total (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| bfs | graph | 17/19 | 12/18 | 2 | 114 | 156 | 3.00 |
| bfs | tree | 10/19 | 7/18 | 11 | 257 | 874 | 15.98 |
| ucs | graph | 17/19 | 17/18 | 2 | 155 | 159 | 3.95 |
| ucs | tree | 8/19 | 8/18 | 13 | 2 104.5 | 3 035.5 | 19.39 |
| greedy | graph | 19/19 | 10/18 | 0 | 94 | 100 | 0.14 |
| greedy | tree | 10/19 | 7/18 | 11 | 8 | 17 | 29.66 |
| astar | graph | 18/19 | 18/18 | 1 | 96 | 122 | 2.06 |
| astar | tree | 14/19 | 14/18 | 7 | 662 | 62.5 | 22.06 |

## Expérience 2 — influence de l'heuristique (A*, Graph-Search)

| probleme | heuristique | statut | cout | developpes | max_memoire | temps_s | b_effectif |
|---|---|---|---:|---:|---:|---:|---:|
| 8-Puzzle moyen | zero | succes | 28 | 177 134 | 185 035 | 0.782 | 1.536 |
| 8-Puzzle moyen | mal_placees | succes | 28 | 59 067 | 102 943 | 0.330 | 1.473 |
| 8-Puzzle moyen | manhattan | succes | 28 | 1 440 | 3 054 | 0.009 | 1.270 |
| 8-Puzzle moyen | conflits_lineaires | succes | 28 | 786 | 1 674 | 0.008 | 1.239 |
| 8-Puzzle difficile | zero | succes | 31 | 181 438 | 185 725 | 0.813 | 1.470 |
| 8-Puzzle difficile | mal_placees | succes | 31 | 121 528 | 168 619 | 0.696 | 1.450 |
| 8-Puzzle difficile | manhattan | succes | 31 | 6 744 | 13 566 | 0.041 | 1.309 |
| 8-Puzzle difficile | conflits_lineaires | succes | 31 | 3 835 | 7 925 | 0.042 | 1.282 |
| 15-Puzzle 15_facile | mal_placees | arret | — | 170 215 | 499 999 | 1.443 | — |
| 15-Puzzle 15_facile | manhattan | succes | 28 | 1 128 | 3 373 | 0.010 | 1.265 |
| 15-Puzzle 15_facile | conflits_lineaires | succes | 28 | 627 | 1 901 | 0.013 | 1.235 |
| Labyrinthe complexe 61×61 (4 dir.) | zero | succes | 216 | 937 | 955 | 0.003 | 1.016 |
| Labyrinthe complexe 61×61 (4 dir.) | manhattan | succes | 216 | 662 | 674 | 0.002 | 1.014 |
| Labyrinthe complexe 61×61 (4 dir.) | euclidienne | succes | 216 | 704 | 720 | 0.002 | 1.014 |
| Labyrinthe portails 41×41 (4 dir.) | zero | succes | 45 | 155 | 159 | 0.000 | 1.071 |
| Labyrinthe portails 41×41 (4 dir.) | manhattan | succes | 45 | 93 | 103 | 0.000 | 1.055 |
| Labyrinthe portails 41×41 (4 dir.) | manhattan_naif | succes | 45 | 78 | 92 | 0.000 | 1.049 |
| Labyrinthe diagonal 10×20 (8 dir.) | zero | succes | 22.5 | 115 | 154 | 0.001 | 1.284 |
| Labyrinthe diagonal 10×20 (8 dir.) | octile | succes | 22.5 | 67 | 141 | 0.000 | 1.240 |
| Labyrinthe diagonal 10×20 (8 dir.) | manhattan | succes | 22.5 | 73 | 141 | 0.001 | 1.245 |
| Navigation Rouyn-Noranda → Gaspé | zero | succes | 1 588.9 | 26 | 27 | 0.000 | 1.420 |
| Navigation Rouyn-Noranda → Gaspé | longitude | succes | 1 588.9 | 26 | 29 | 0.000 | 1.420 |
| Navigation Rouyn-Noranda → Gaspé | vol_oiseau | succes | 1 588.9 | 26 | 33 | 0.000 | 1.420 |
| Navigation Rouyn-Noranda → Gaspé | vol_oiseau_x2 | succes | 1 634.5 | 15 | 30 | 0.000 | 1.155 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | zero | succes | 3 | 254 | 448 | 0.002 | 8.123 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | operations_restantes | succes | 3 | 240 | 256 | 0.002 | 7.619 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | ecart_cible | succes | 3 | 104 | 344 | 0.002 | 7.133 |

## Détail — toutes les exécutions

| probleme | strategie | mode | statut | cout | profondeur | generes | developpes | max_open | max_memoire | temps_s |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Labyrinthe simple 7×10 (4 dir.) | bfs | graph | succes | 11 | 11 | 44 | 21 | 2 | 22 | 0.000 |
| Labyrinthe simple 7×10 (4 dir.) | bfs | tree | succes | 11 | 11 | 3 841 | 1 913 | 1 926 | 1 924 | 0.005 |
| Labyrinthe simple 7×10 (4 dir.) | ucs | graph | succes | 11 | 11 | 48 | 23 | 3 | 27 | 0.000 |
| Labyrinthe simple 7×10 (4 dir.) | ucs | tree | succes | 11 | 11 | 7 706 | 3 840 | 3 866 | 3 864 | 0.012 |
| Labyrinthe simple 7×10 (4 dir.) | greedy | graph | succes | 11 | 11 | 36 | 17 | 3 | 19 | 0.000 |
| Labyrinthe simple 7×10 (4 dir.) | greedy | tree | arret | — | — | 1 198 850 | 799 232 | 399 619 | 399 618 | 3.001 |
| Labyrinthe simple 7×10 (4 dir.) | astar | graph | succes | 11 | 11 | 36 | 17 | 3 | 19 | 0.000 |
| Labyrinthe simple 7×10 (4 dir.) | astar | tree | succes | 11 | 11 | 36 | 17 | 19 | 16 | 0.000 |
| Labyrinthe moyen 21×21 (4 dir.) | bfs | graph | succes | 92 | 92 | 226 | 112 | 3 | 115 | 0.000 |
| Labyrinthe moyen 21×21 (4 dir.) | bfs | tree | arret | — | — | 1 023 717 | 523 716 | 500 002 | 500 000 | 1.924 |
| Labyrinthe moyen 21×21 (4 dir.) | ucs | graph | succes | 92 | 92 | 230 | 114 | 3 | 118 | 0.000 |
| Labyrinthe moyen 21×21 (4 dir.) | ucs | tree | arret | — | — | 1 023 717 | 523 716 | 500 002 | 500 000 | 1.968 |
| Labyrinthe moyen 21×21 (4 dir.) | greedy | graph | succes | 92 | 92 | 191 | 94 | 4 | 100 | 0.000 |
| Labyrinthe moyen 21×21 (4 dir.) | greedy | tree | arret | — | — | 1 000 004 | 500 003 | 500 002 | 500 000 | 2.229 |
| Labyrinthe moyen 21×21 (4 dir.) | astar | graph | succes | 92 | 92 | 199 | 99 | 2 | 101 | 0.000 |
| Labyrinthe moyen 21×21 (4 dir.) | astar | tree | arret | — | — | 1 000 628 | 500 627 | 500 002 | 500 000 | 2.974 |
| Labyrinthe complexe 61×61 (4 dir.) | bfs | graph | succes | 216 | 216 | 1 885 | 926 | 13 | 947 | 0.002 |
| Labyrinthe complexe 61×61 (4 dir.) | bfs | tree | arret | — | — | 1 022 403 | 522 402 | 500 002 | 500 000 | 1.935 |
| Labyrinthe complexe 61×61 (4 dir.) | ucs | graph | succes | 216 | 216 | 1 907 | 937 | 13 | 955 | 0.003 |
| Labyrinthe complexe 61×61 (4 dir.) | ucs | tree | arret | — | — | 1 022 403 | 522 402 | 500 002 | 500 000 | 1.993 |
| Labyrinthe complexe 61×61 (4 dir.) | greedy | graph | succes | 272 | 272 | 738 | 359 | 16 | 382 | 0.001 |
| Labyrinthe complexe 61×61 (4 dir.) | greedy | tree | arret | — | — | 1 000 004 | 500 003 | 500 002 | 500 000 | 2.326 |
| Labyrinthe complexe 61×61 (4 dir.) | astar | graph | succes | 216 | 216 | 1 346 | 662 | 15 | 674 | 0.002 |
| Labyrinthe complexe 61×61 (4 dir.) | astar | tree | arret | — | — | 991 222 | 491 776 | 499 447 | 499 445 | 3.000 |
| Labyrinthe pondere 31×31 (4 dir.) | bfs | graph | succes | 204 | 92 | 918 | 446 | 11 | 449 | 0.001 |
| Labyrinthe pondere 31×31 (4 dir.) | bfs | tree | arret | — | — | 896 056 | 396 055 | 500 002 | 500 000 | 1.635 |
| Labyrinthe pondere 31×31 (4 dir.) | ucs | graph | succes | 203 | 100 | 840 | 407 | 9 | 413 | 0.001 |
| Labyrinthe pondere 31×31 (4 dir.) | ucs | tree | arret | — | — | 944 767 | 444 766 | 500 002 | 500 000 | 1.853 |
| Labyrinthe pondere 31×31 (4 dir.) | greedy | graph | succes | 353 | 132 | 469 | 224 | 17 | 207 | 0.001 |
| Labyrinthe pondere 31×31 (4 dir.) | greedy | tree | arret | — | — | 1 163 142 | 775 424 | 387 719 | 387 718 | 3.001 |
| Labyrinthe pondere 31×31 (4 dir.) | astar | graph | succes | 203 | 100 | 821 | 397 | 9 | 408 | 0.001 |
| Labyrinthe pondere 31×31 (4 dir.) | astar | tree | arret | — | — | 934 788 | 434 786 | 500 003 | 500 000 | 2.663 |
| Labyrinthe portails 41×41 (4 dir.) | bfs | graph | succes | 45 | 45 | 312 | 153 | 6 | 156 | 0.000 |
| Labyrinthe portails 41×41 (4 dir.) | bfs | tree | arret | — | — | 961 212 | 461 211 | 500 002 | 500 000 | 1.818 |
| Labyrinthe portails 41×41 (4 dir.) | ucs | graph | succes | 45 | 45 | 316 | 155 | 6 | 159 | 0.000 |
| Labyrinthe portails 41×41 (4 dir.) | ucs | tree | arret | — | — | 961 212 | 461 211 | 500 002 | 500 000 | 1.836 |
| Labyrinthe portails 41×41 (4 dir.) | greedy | graph | succes | 45 | 45 | 169 | 81 | 6 | 81 | 0.000 |
| Labyrinthe portails 41×41 (4 dir.) | greedy | tree | arret | — | — | 854 528 | 427 264 | 427 265 | 427 263 | 3.001 |
| Labyrinthe portails 41×41 (4 dir.) | astar | graph | succes | 45 | 45 | 193 | 93 | 6 | 103 | 0.000 |
| Labyrinthe portails 41×41 (4 dir.) | astar | tree | arret | — | — | 778 054 | 354 304 | 423 751 | 423 749 | 3.001 |
| Labyrinthe diagonal 10×20 (8 dir.) | bfs | graph | succes | 31.5 | 19 | 681 | 114 | 12 | 131 | 0.001 |
| Labyrinthe diagonal 10×20 (8 dir.) | bfs | tree | arret | — | — | 608 805 | 108 802 | 500 004 | 499 999 | 0.896 |
| Labyrinthe diagonal 10×20 (8 dir.) | ucs | graph | succes | 22.5 | 20 | 669 | 115 | 32 | 154 | 0.001 |
| Labyrinthe diagonal 10×20 (8 dir.) | ucs | tree | arret | — | — | 611 517 | 111 513 | 500 005 | 499 997 | 0.951 |
| Labyrinthe diagonal 10×20 (8 dir.) | greedy | graph | succes | 28.1 | 19 | 101 | 19 | 32 | 79 | 0.000 |
| Labyrinthe diagonal 10×20 (8 dir.) | greedy | tree | succes | 28.1 | 19 | 101 | 19 | 82 | 77 | 0.000 |
| Labyrinthe diagonal 10×20 (8 dir.) | astar | graph | succes | 22.5 | 20 | 378 | 67 | 46 | 141 | 0.000 |
| Labyrinthe diagonal 10×20 (8 dir.) | astar | tree | succes | 22.5 | 20 | 58 905 | 12 218 | 46 687 | 46 682 | 0.110 |
| Labyrinthe sans_solution 21×21 (4 dir.) | bfs | graph | echec | — | — | 297 | 149 | 3 | 149 | 0.000 |
| Labyrinthe sans_solution 21×21 (4 dir.) | bfs | tree | arret | — | — | 1 023 717 | 523 716 | 500 002 | 500 000 | 1.985 |
| Labyrinthe sans_solution 21×21 (4 dir.) | ucs | graph | echec | — | — | 297 | 149 | 3 | 149 | 0.000 |
| Labyrinthe sans_solution 21×21 (4 dir.) | ucs | tree | arret | — | — | 1 023 717 | 523 716 | 500 002 | 500 000 | 1.994 |
| Labyrinthe sans_solution 21×21 (4 dir.) | greedy | graph | echec | — | — | 297 | 149 | 4 | 149 | 0.000 |
| Labyrinthe sans_solution 21×21 (4 dir.) | greedy | tree | arret | — | — | 1 000 004 | 500 003 | 500 002 | 500 000 | 2.195 |
| Labyrinthe sans_solution 21×21 (4 dir.) | astar | graph | echec | — | — | 297 | 149 | 2 | 149 | 0.001 |
| Labyrinthe sans_solution 21×21 (4 dir.) | astar | tree | arret | — | — | 1 000 628 | 500 627 | 500 002 | 500 000 | 2.950 |
| Navigation Chicoutimi → Montréal | bfs | graph | succes | 494.8 | 3 | 24 | 7 | 8 | 18 | 0 |
| Navigation Chicoutimi → Montréal | bfs | tree | succes | 494.8 | 3 | 32 | 9 | 21 | 17 | 0 |
| Navigation Chicoutimi → Montréal | ucs | graph | succes | 494.2 | 3 | 60 | 21 | 6 | 28 | 0 |
| Navigation Chicoutimi → Montréal | ucs | tree | succes | 494.2 | 3 | 67 127 | 23 799 | 43 328 | 43 324 | 0.062 |
| Navigation Chicoutimi → Montréal | greedy | graph | succes | 494.2 | 3 | 14 | 3 | 7 | 13 | 0 |
| Navigation Chicoutimi → Montréal | greedy | tree | succes | 494.2 | 3 | 14 | 3 | 11 | 7 | 0 |
| Navigation Chicoutimi → Montréal | astar | graph | succes | 494.2 | 3 | 34 | 10 | 9 | 24 | 0 |
| Navigation Chicoutimi → Montréal | astar | tree | succes | 494.2 | 3 | 71 | 23 | 48 | 45 | 0.000 |
| Navigation Rouyn-Noranda → Gaspé | bfs | graph | succes | 1 701.2 | 8 | 76 | 26 | 6 | 28 | 0 |
| Navigation Rouyn-Noranda → Gaspé | bfs | tree | succes | 1 701.2 | 8 | 7 719 | 2 253 | 5 465 | 5 463 | 0.005 |
| Navigation Rouyn-Noranda → Gaspé | ucs | graph | succes | 1 588.9 | 9 | 76 | 26 | 5 | 27 | 0 |
| Navigation Rouyn-Noranda → Gaspé | ucs | tree | arret | — | — | 771 111 | 271 109 | 500 003 | 500 000 | 1.038 |
| Navigation Rouyn-Noranda → Gaspé | greedy | graph | succes | 1 701.2 | 8 | 28 | 8 | 10 | 26 | 0.000 |
| Navigation Rouyn-Noranda → Gaspé | greedy | tree | succes | 1 701.2 | 8 | 28 | 8 | 20 | 18 | 0 |
| Navigation Rouyn-Noranda → Gaspé | astar | graph | succes | 1 588.9 | 9 | 76 | 26 | 10 | 33 | 0.000 |
| Navigation Rouyn-Noranda → Gaspé | astar | tree | succes | 1 588.9 | 9 | 1 970 | 672 | 1 298 | 1 295 | 0.003 |
| Navigation Gatineau → Baie-Comeau | bfs | graph | succes | 912.7 | 6 | 69 | 23 | 7 | 29 | 0 |
| Navigation Gatineau → Baie-Comeau | bfs | tree | succes | 912.7 | 6 | 1 257 | 368 | 888 | 883 | 0.001 |
| Navigation Gatineau → Baie-Comeau | ucs | graph | succes | 881.9 | 9 | 74 | 25 | 6 | 30 | 0 |
| Navigation Gatineau → Baie-Comeau | ucs | tree | succes | 881.9 | 9 | 10 791 | 3 200 | 7 591 | 7 589 | 0.008 |
| Navigation Gatineau → Baie-Comeau | greedy | graph | succes | 912.7 | 6 | 24 | 6 | 10 | 22 | 0 |
| Navigation Gatineau → Baie-Comeau | greedy | tree | succes | 912.7 | 6 | 24 | 6 | 18 | 15 | 0 |
| Navigation Gatineau → Baie-Comeau | astar | graph | succes | 881.9 | 9 | 48 | 15 | 9 | 28 | 0.000 |
| Navigation Gatineau → Baie-Comeau | astar | tree | succes | 881.9 | 9 | 119 | 38 | 81 | 79 | 0.000 |
| Navigation Gaspé → Îles-de-la-Madeleine | bfs | graph | echec | — | — | 77 | 27 | 7 | 29 | 0.000 |
| Navigation Gaspé → Îles-de-la-Madeleine | bfs | tree | arret | — | — | 704 745 | 204 744 | 500 002 | 499 997 | 0.777 |
| Navigation Gaspé → Îles-de-la-Madeleine | ucs | graph | echec | — | — | 77 | 27 | 6 | 29 | 0.000 |
| Navigation Gaspé → Îles-de-la-Madeleine | ucs | tree | arret | — | — | 772 227 | 272 226 | 500 002 | 499 999 | 1.078 |
| Navigation Gaspé → Îles-de-la-Madeleine | greedy | graph | echec | — | — | 80 | 28 | 5 | 28 | 0.000 |
| Navigation Gaspé → Îles-de-la-Madeleine | greedy | tree | arret | — | — | 1 233 791 | 822 528 | 411 264 | 411 263 | 3.022 |
| Navigation Gaspé → Îles-de-la-Madeleine | astar | graph | echec | — | — | 77 | 27 | 6 | 29 | 0.000 |
| Navigation Gaspé → Îles-de-la-Madeleine | astar | tree | arret | — | — | 789 903 | 289 901 | 500 003 | 500 000 | 1.911 |
| 8-Puzzle facile | bfs | graph | succes | 8 | 8 | 421 | 149 | 112 | 368 | 0.001 |
| 8-Puzzle facile | bfs | tree | succes | 8 | 8 | 4 029 | 1 392 | 2 636 | 2 633 | 0.005 |
| 8-Puzzle facile | ucs | graph | succes | 8 | 8 | 687 | 260 | 146 | 548 | 0.001 |
| 8-Puzzle facile | ucs | tree | succes | 8 | 8 | 11 131 | 4 028 | 7 103 | 7 101 | 0.013 |
| 8-Puzzle facile | greedy | graph | succes | 8 | 8 | 23 | 8 | 8 | 20 | 0.000 |
| 8-Puzzle facile | greedy | tree | succes | 8 | 8 | 23 | 8 | 15 | 12 | 0.000 |
| 8-Puzzle facile | astar | graph | succes | 8 | 8 | 23 | 8 | 8 | 20 | 0.000 |
| 8-Puzzle facile | astar | tree | succes | 8 | 8 | 23 | 8 | 15 | 12 | 0.000 |
| 8-Puzzle moyen | bfs | graph | succes | 28 | 28 | 455 676 | 171 028 | 24 053 | 185 035 | 0.626 |
| 8-Puzzle moyen | bfs | tree | arret | — | — | 785 025 | 285 023 | 500 003 | 499 999 | 1.239 |
| 8-Puzzle moyen | ucs | graph | succes | 28 | 28 | 473 571 | 177 134 | 24 053 | 185 035 | 0.701 |
| 8-Puzzle moyen | ucs | tree | arret | — | — | 785 025 | 285 023 | 500 003 | 499 999 | 1.268 |
| 8-Puzzle moyen | greedy | graph | succes | 48 | 48 | 1 052 | 385 | 218 | 753 | 0.002 |
| 8-Puzzle moyen | greedy | tree | arret | — | — | 833 334 | 333 333 | 500 002 | 500 000 | 2.467 |
| 8-Puzzle moyen | astar | graph | succes | 28 | 28 | 3 815 | 1 440 | 823 | 3 054 | 0.009 |
| 8-Puzzle moyen | astar | tree | succes | 28 | 28 | 35 107 | 13 792 | 21 315 | 21 312 | 0.106 |
| 8-Puzzle difficile | bfs | graph | succes | 31 | 31 | 483 564 | 181 347 | 25 134 | 185 725 | 0.678 |
| 8-Puzzle difficile | bfs | tree | arret | — | — | 768 727 | 268 726 | 500 002 | 499 999 | 1.218 |
| 8-Puzzle difficile | ucs | graph | succes | 31 | 31 | 483 837 | 181 438 | 25 134 | 185 725 | 0.698 |
| 8-Puzzle difficile | ucs | tree | arret | — | — | 768 727 | 268 726 | 500 002 | 499 999 | 1.187 |
| 8-Puzzle difficile | greedy | graph | succes | 47 | 47 | 278 | 104 | 65 | 222 | 0.001 |
| 8-Puzzle difficile | greedy | tree | arret | — | — | 751 728 | 251 726 | 500 003 | 499 999 | 2.218 |
| 8-Puzzle difficile | astar | graph | succes | 31 | 31 | 17 749 | 6 744 | 3 549 | 13 566 | 0.041 |
| 8-Puzzle difficile | astar | tree | succes | 31 | 31 | 527 149 | 207 865 | 319 284 | 319 281 | 1.778 |
| 15-Puzzle 15_facile | bfs | graph | arret | — | — | 531 651 | 170 939 | 164 532 | 499 998 | 0.836 |
| 15-Puzzle 15_facile | bfs | tree | arret | — | — | 723 613 | 223 611 | 500 003 | 500 000 | 1.185 |
| 15-Puzzle 15_facile | ucs | graph | arret | — | — | 531 651 | 170 939 | 164 532 | 499 998 | 0.854 |
| 15-Puzzle 15_facile | ucs | tree | arret | — | — | 723 613 | 223 611 | 500 003 | 500 000 | 1.127 |
| 15-Puzzle 15_facile | greedy | graph | succes | 48 | 48 | 2 744 | 870 | 910 | 2 647 | 0.007 |
| 15-Puzzle 15_facile | greedy | tree | arret | — | — | 763 529 | 305 408 | 458 122 | 458 120 | 3.001 |
| 15-Puzzle 15_facile | astar | graph | succes | 28 | 28 | 3 452 | 1 128 | 1 137 | 3 373 | 0.010 |
| 15-Puzzle 15_facile | astar | tree | succes | 28 | 28 | 98 224 | 32 973 | 65 251 | 65 248 | 0.371 |
| 15-Puzzle 15_difficile | bfs | graph | arret | — | — | 531 827 | 171 143 | 164 432 | 500 000 | 0.737 |
| 15-Puzzle 15_difficile | bfs | tree | arret | — | — | 723 603 | 223 602 | 500 002 | 499 999 | 1.166 |
| 15-Puzzle 15_difficile | ucs | graph | arret | — | — | 531 827 | 171 143 | 164 432 | 500 000 | 0.860 |
| 15-Puzzle 15_difficile | ucs | tree | arret | — | — | 723 603 | 223 602 | 500 002 | 499 999 | 1.148 |
| 15-Puzzle 15_difficile | greedy | graph | succes | 92 | 92 | 1 368 | 437 | 486 | 1 404 | 0.004 |
| 15-Puzzle 15_difficile | greedy | tree | arret | — | — | 759 687 | 303 872 | 455 816 | 455 814 | 3.001 |
| 15-Puzzle 15_difficile | astar | graph | arret | — | — | 543 445 | 184 394 | 159 454 | 499 997 | 1.867 |
| 15-Puzzle 15_difficile | astar | tree | arret | — | — | 681 738 | 247 040 | 434 699 | 434 697 | 3.001 |
| Arithmétique [2, 3, 5, 7] → 24 (tous les nombres) | bfs | graph | succes | 3 | 3 | 881 | 114 | 321 | 751 | 0.003 |
| Arithmétique [2, 3, 5, 7] → 24 (tous les nombres) | bfs | tree | succes | 3 | 3 | 1 010 | 140 | 870 | 865 | 0.002 |
| Arithmétique [2, 3, 5, 7] → 24 (tous les nombres) | ucs | graph | succes | 3 | 3 | 1 523 | 434 | 385 | 1 011 | 0.005 |
| Arithmétique [2, 3, 5, 7] → 24 (tous les nombres) | ucs | tree | succes | 3 | 3 | 2 683 | 1 009 | 2 208 | 2 207 | 0.006 |
| Arithmétique [2, 3, 5, 7] → 24 (tous les nombres) | greedy | graph | succes | 3 | 3 | 558 | 284 | 45 | 337 | 0.002 |
| Arithmétique [2, 3, 5, 7] → 24 (tous les nombres) | greedy | tree | succes | 3 | 3 | 687 | 652 | 47 | 46 | 0.002 |
| Arithmétique [2, 3, 5, 7] → 24 (tous les nombres) | astar | graph | succes | 3 | 3 | 558 | 284 | 45 | 337 | 0.002 |
| Arithmétique [2, 3, 5, 7] → 24 (tous les nombres) | astar | tree | succes | 3 | 3 | 687 | 652 | 47 | 46 | 0.002 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | bfs | graph | succes | 3 | 3 | 562 | 87 | 167 | 414 | 0.002 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | bfs | tree | succes | 3 | 3 | 988 | 146 | 838 | 834 | 0.002 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | ucs | graph | succes | 3 | 3 | 610 | 254 | 176 | 448 | 0.002 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | ucs | tree | succes | 3 | 3 | 2 375 | 987 | 1 938 | 1 937 | 0.005 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | greedy | graph | succes | 3 | 3 | 508 | 240 | 25 | 256 | 0.002 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | greedy | tree | succes | 3 | 3 | 709 | 677 | 45 | 44 | 0.002 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | astar | graph | succes | 3 | 3 | 508 | 240 | 25 | 256 | 0.002 |
| Arithmétique [3, 3, 8, 8] → 24 (tous les nombres) | astar | tree | succes | 3 | 3 | 709 | 677 | 45 | 44 | 0.002 |
| Arithmétique [1, 1, 1, 1] → 24 (tous les nombres) | bfs | graph | echec | — | — | 97 | 20 | 12 | 29 | 0.000 |
| Arithmétique [1, 1, 1, 1] → 24 (tous les nombres) | bfs | tree | echec | — | — | 1 615 | 1 615 | 1 290 | 1 289 | 0.005 |
| Arithmétique [1, 1, 1, 1] → 24 (tous les nombres) | ucs | graph | echec | — | — | 97 | 20 | 12 | 29 | 0.000 |
| Arithmétique [1, 1, 1, 1] → 24 (tous les nombres) | ucs | tree | echec | — | — | 1 615 | 1 615 | 1 290 | 1 289 | 0.005 |
| Arithmétique [1, 1, 1, 1] → 24 (tous les nombres) | greedy | graph | echec | — | — | 97 | 20 | 10 | 24 | 0.000 |
| Arithmétique [1, 1, 1, 1] → 24 (tous les nombres) | greedy | tree | echec | — | — | 1 615 | 1 615 | 40 | 39 | 0.005 |
| Arithmétique [1, 1, 1, 1] → 24 (tous les nombres) | astar | graph | echec | — | — | 97 | 20 | 10 | 24 | 0.000 |
| Arithmétique [1, 1, 1, 1] → 24 (tous les nombres) | astar | tree | echec | — | — | 1 615 | 1 615 | 40 | 39 | 0.005 |
| Arithmétique [1, 3, 7, 10, 25, 50] → 765 (sous-ensemble permis) | bfs | graph | succes | 3 | 3 | 21 832 | 683 | 10 125 | 20 914 | 0.117 |
| Arithmétique [1, 3, 7, 10, 25, 50] → 765 (sous-ensemble permis) | bfs | tree | succes | 3 | 3 | 34 921 | 1 114 | 33 781 | 33 751 | 0.183 |
| Arithmétique [1, 3, 7, 10, 25, 50] → 765 (sous-ensemble permis) | ucs | graph | succes | 3 | 3 | 188 064 | 10 812 | 60 990 | 132 784 | 0.819 |
| Arithmétique [1, 3, 7, 10, 25, 50] → 765 (sous-ensemble permis) | ucs | tree | arret | — | — | 531 564 | 31 551 | 500 014 | 499 999 | 1.833 |
| Arithmétique [1, 3, 7, 10, 25, 50] → 765 (sous-ensemble permis) | greedy | graph | succes | 3 | 3 | 21 835 | 683 | 10 132 | 20 931 | 0.122 |
| Arithmétique [1, 3, 7, 10, 25, 50] → 765 (sous-ensemble permis) | greedy | tree | succes | 3 | 3 | 34 924 | 1 114 | 33 810 | 33 780 | 0.192 |
| Arithmétique [1, 3, 7, 10, 25, 50] → 765 (sous-ensemble permis) | astar | graph | succes | 3 | 3 | 21 835 | 683 | 10 132 | 20 931 | 0.124 |
| Arithmétique [1, 3, 7, 10, 25, 50] → 765 (sous-ensemble permis) | astar | tree | succes | 3 | 3 | 34 924 | 1 114 | 33 810 | 33 780 | 0.186 |
| Équation 5x - 7 = 2x + 8 | bfs | graph | succes | 3 | 3 | 22 | 6 | 8 | 18 | 0.000 |
| Équation 5x - 7 = 2x + 8 | bfs | tree | succes | 3 | 3 | 26 | 7 | 17 | 13 | 0.000 |
| Équation 5x - 7 = 2x + 8 | ucs | graph | succes | 3 | 3 | 37 | 11 | 8 | 21 | 0.000 |
| Équation 5x - 7 = 2x + 8 | ucs | tree | succes | 3 | 3 | 82 | 25 | 57 | 54 | 0.000 |
| Équation 5x - 7 = 2x + 8 | greedy | graph | succes | 3 | 3 | 22 | 6 | 8 | 18 | 0.000 |
| Équation 5x - 7 = 2x + 8 | greedy | tree | succes | 3 | 3 | 26 | 7 | 19 | 16 | 0.000 |
| Équation 5x - 7 = 2x + 8 | astar | graph | succes | 3 | 3 | 22 | 6 | 8 | 18 | 0.000 |
| Équation 5x - 7 = 2x + 8 | astar | tree | succes | 3 | 3 | 26 | 7 | 19 | 16 | 0.000 |
| Équation 4x + 1 = 7x - 3/2 | bfs | graph | succes | 3 | 3 | 22 | 6 | 8 | 18 | 0.000 |
| Équation 4x + 1 = 7x - 3/2 | bfs | tree | succes | 3 | 3 | 26 | 7 | 17 | 13 | 0.000 |
| Équation 4x + 1 = 7x - 3/2 | ucs | graph | succes | 3 | 3 | 37 | 11 | 8 | 21 | 0.000 |
| Équation 4x + 1 = 7x - 3/2 | ucs | tree | succes | 3 | 3 | 82 | 25 | 57 | 54 | 0.000 |
| Équation 4x + 1 = 7x - 3/2 | greedy | graph | succes | 3 | 3 | 22 | 6 | 8 | 18 | 0.000 |
| Équation 4x + 1 = 7x - 3/2 | greedy | tree | succes | 3 | 3 | 26 | 7 | 19 | 16 | 0.000 |
| Équation 4x + 1 = 7x - 3/2 | astar | graph | succes | 3 | 3 | 22 | 6 | 8 | 18 | 0.000 |
| Équation 4x + 1 = 7x - 3/2 | astar | tree | succes | 3 | 3 | 26 | 7 | 19 | 16 | 0.000 |
