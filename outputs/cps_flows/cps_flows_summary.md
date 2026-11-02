# Age profile and flows of floor occupations in manufacturing, matched CPS months (DL-44) — exploratory

Generated: 2026-10-30 02:24 UTC

Files: 80 monthly files, jan20pub.zip to sep26pub.zip. Civilian adult records: 6,539,550. Linked pairs: 4,326,472 (93,032 in an A2/A3 universe). Bootstrap: household clusters, B = 1000, seed 20261029. Rates are percent per month. Manufacturing as a whole, not NAICS 3363; people who move house are not linked; monthly status transitions include classification error.

## Link quality (all civilian adults)

|   year |   eligible_records |   linked_pairs |   link_rate_pct |
|-------:|-------------------:|---------------:|----------------:|
|   2020 |             718364 |         636047 |         88.541  |
|   2021 |             784305 |         706065 |         90.0243 |
|   2022 |             751008 |         674794 |         89.8518 |
|   2023 |             735287 |         661916 |         90.0214 |
|   2024 |             733763 |         661520 |         90.1545 |
|   2025 |             589271 |         526953 |         89.4246 |
|   2026 |             515713 |         459177 |         89.0373 |

## A1 — age profile, employed in manufacturing (pooled person-months)

| check         | group                       | band   |   n_den |   n_num |     pct |      lo |      hi | reportable   | not_reportable_reason   | role     |
|:--------------|:----------------------------|:-------|--------:|--------:|--------:|--------:|--------:|:-------------|:------------------------|:---------|
| all_records   | maintenance_M               | 16-34  |   12843 |    3290 | 26.6165 | 24.986  | 28.35   | True         |                         | headline |
| all_records   | maintenance_M               | 35-54  |   12843 |    5688 | 44.8058 | 42.9715 | 46.8601 | True         |                         | headline |
| all_records   | maintenance_M               | 55-64  |   12843 |    3058 | 23.2427 | 21.6866 | 24.8994 | True         |                         | headline |
| all_records   | maintenance_M               | 65+    |   12843 |     807 |  5.3351 |  4.5383 |  6.1423 | True         |                         | headline |
| all_records   | maintenance_M               | 55+    |   12843 |    3865 | 28.5778 | 26.794  | 30.3657 | True         |                         | headline |
| all_records   | machinists_8030             | 16-34  |    6712 |    1757 | 27.8969 | 25.4419 | 30.2957 | True         |                         | headline |
| all_records   | machinists_8030             | 35-54  |    6712 |    2672 | 40.2562 | 37.6963 | 43.0202 | True         |                         | headline |
| all_records   | machinists_8030             | 55-64  |    6712 |    1760 | 25.3191 | 22.8041 | 27.6873 | True         |                         | headline |
| all_records   | machinists_8030             | 65+    |    6712 |     523 |  6.5278 |  5.3769 |  7.9453 | True         |                         | headline |
| all_records   | machinists_8030             | 55+    |    6712 |    2283 | 31.8469 | 29.148  | 34.404  | True         |                         | headline |
| all_records   | mixed_7905                  | 16-34  |    1794 |     577 | 33.1296 | 28.5503 | 38.0763 | True         |                         | headline |
| all_records   | mixed_7905                  | 35-54  |    1794 |     755 | 42.8293 | 37.7196 | 47.6527 | True         |                         | headline |
| all_records   | mixed_7905                  | 55-64  |    1794 |     380 | 19.9852 | 15.9355 | 24.059  | True         |                         | headline |
| all_records   | mixed_7905                  | 65+    |    1794 |      82 |  4.0559 |  2.2334 |  6.1762 | True         |                         | headline |
| all_records   | mixed_7905                  | 55+    |    1794 |     462 | 24.041  | 19.535  | 28.4847 | True         |                         | headline |
| all_records   | mixed_8225                  | 16-34  |    7410 |    2201 | 32.4195 | 30.0616 | 34.7782 | True         |                         | headline |
| all_records   | mixed_8225                  | 35-54  |    7410 |    3139 | 41.8559 | 39.5552 | 44.322  | True         |                         | headline |
| all_records   | mixed_8225                  | 55-64  |    7410 |    1606 | 20.4454 | 18.561  | 22.5087 | True         |                         | headline |
| all_records   | mixed_8225                  | 65+    |    7410 |     464 |  5.2793 |  4.272  |  6.332  | True         |                         | headline |
| all_records   | mixed_8225                  | 55+    |    7410 |    2070 | 25.7246 | 23.6174 | 27.9197 | True         |                         | headline |
| all_records   | rest_R                      | 16-34  |  112171 |   35084 | 33.3856 | 32.7411 | 34.0562 | True         |                         | headline |
| all_records   | rest_R                      | 35-54  |  112171 |   47751 | 42.7125 | 42.0107 | 43.3875 | True         |                         | headline |
| all_records   | rest_R                      | 55-64  |  112171 |   22652 | 18.9415 | 18.3875 | 19.4782 | True         |                         | headline |
| all_records   | rest_R                      | 65+    |  112171 |    6684 |  4.9603 |  4.6791 |  5.2332 | True         |                         | headline |
| all_records   | rest_R                      | 55+    |  112171 |   29336 | 23.9019 | 23.305  | 24.4592 | True         |                         | headline |
| all_records   | production_P                | 16-34  |  128087 |   39619 | 33.043  | 32.4489 | 33.6407 | True         |                         | headline |
| all_records   | production_P                | 35-54  |  128087 |   54317 | 42.537  | 41.8851 | 43.1989 | True         |                         | headline |
| all_records   | production_P                | 55-64  |  128087 |   26398 | 19.3734 | 18.8615 | 19.9012 | True         |                         | headline |
| all_records   | production_P                | 65+    |  128087 |    7753 |  5.0466 |  4.7657 |  5.2969 | True         |                         | headline |
| all_records   | production_P                | 55+    |  128087 |   34151 | 24.42   | 23.8565 | 24.9714 | True         |                         | headline |
| all_records   | all_manufacturing           | 16-34  |  349998 |   96978 | 30.0202 | 29.6162 | 30.3771 | True         |                         | headline |
| all_records   | all_manufacturing           | 35-54  |  349998 |  154666 | 44.3331 | 43.9029 | 44.7477 | True         |                         | headline |
| all_records   | all_manufacturing           | 55-64  |  349998 |   74726 | 20.0065 | 19.6823 | 20.3292 | True         |                         | headline |
| all_records   | all_manufacturing           | 65+    |  349998 |   23628 |  5.6402 |  5.456  |  5.8196 | True         |                         | headline |
| all_records   | all_manufacturing           | 55+    |  349998 |   98354 | 25.6468 | 25.2685 | 26.022  | True         |                         | headline |
| no_allocation | maintenance_M               | 16-34  |   12512 |    3189 | 26.4507 | 24.7957 | 28.2227 | True         |                         | check    |
| no_allocation | maintenance_M               | 35-54  |   12512 |    5545 | 44.8262 | 42.9459 | 46.9466 | True         |                         | check    |
| no_allocation | maintenance_M               | 55-64  |   12512 |    2999 | 23.4211 | 21.7996 | 25.1151 | True         |                         | check    |
| no_allocation | maintenance_M               | 65+    |   12512 |     779 |  5.302  |  4.5061 |  6.1124 | True         |                         | check    |
| no_allocation | maintenance_M               | 55+    |   12512 |    3778 | 28.7231 | 26.9302 | 30.5114 | True         |                         | check    |
| no_allocation | machinists_8030             | 16-34  |    6577 |    1718 | 27.6939 | 25.2194 | 30.0745 | True         |                         | check    |
| no_allocation | machinists_8030             | 35-54  |    6577 |    2608 | 40.1572 | 37.5598 | 42.992  | True         |                         | check    |
| no_allocation | machinists_8030             | 55-64  |    6577 |    1743 | 25.6857 | 23.1225 | 28.1461 | True         |                         | check    |
| no_allocation | machinists_8030             | 65+    |    6577 |     508 |  6.4632 |  5.321  |  7.9195 | True         |                         | check    |
| no_allocation | machinists_8030             | 55+    |    6577 |    2251 | 32.1489 | 29.4184 | 34.7562 | True         |                         | check    |
| no_allocation | mixed_7905                  | 16-34  |    1750 |     561 | 33.1178 | 28.4377 | 38.0727 | True         |                         | check    |
| no_allocation | mixed_7905                  | 35-54  |    1750 |     740 | 42.9679 | 37.8128 | 48.1383 | True         |                         | check    |
| no_allocation | mixed_7905                  | 55-64  |    1750 |     373 | 20.1581 | 16.0545 | 24.3569 | True         |                         | check    |
| no_allocation | mixed_7905                  | 65+    |    1750 |      76 |  3.7562 |  1.9382 |  5.9073 | True         |                         | check    |
| no_allocation | mixed_7905                  | 55+    |    1750 |     449 | 23.9143 | 19.3648 | 28.4762 | True         |                         | check    |
| no_allocation | mixed_8225                  | 16-34  |    7231 |    2134 | 32.2127 | 29.8743 | 34.5519 | True         |                         | check    |
| no_allocation | mixed_8225                  | 35-54  |    7231 |    3080 | 42.1107 | 39.6938 | 44.5821 | True         |                         | check    |
| no_allocation | mixed_8225                  | 55-64  |    7231 |    1584 | 20.6294 | 18.6655 | 22.757  | True         |                         | check    |
| no_allocation | mixed_8225                  | 65+    |    7231 |     433 |  5.0473 |  4.0221 |  6.1142 | True         |                         | check    |
| no_allocation | mixed_8225                  | 55+    |    7231 |    2017 | 25.6766 | 23.6085 | 27.9555 | True         |                         | check    |
| no_allocation | rest_R                      | 16-34  |  109194 |   33973 | 33.1545 | 32.5004 | 33.8242 | True         |                         | check    |
| no_allocation | rest_R                      | 35-54  |  109194 |   46625 | 42.8607 | 42.1453 | 43.5648 | True         |                         | check    |
| no_allocation | rest_R                      | 55-64  |  109194 |   22166 | 19.0769 | 18.5218 | 19.6359 | True         |                         | check    |
| no_allocation | rest_R                      | 65+    |  109194 |    6430 |  4.9079 |  4.6272 |  5.1829 | True         |                         | check    |
| no_allocation | rest_R                      | 55+    |  109194 |   28596 | 23.9848 | 23.3865 | 24.5524 | True         |                         | check    |
| no_allocation | production_P                | 16-34  |  124752 |   38386 | 32.8165 | 32.2107 | 33.4314 | True         |                         | check    |
| no_allocation | production_P                | 35-54  |  124752 |   53053 | 42.6781 | 42.0192 | 43.3542 | True         |                         | check    |
| no_allocation | production_P                | 55-64  |  124752 |   25866 | 19.5258 | 18.9852 | 20.0746 | True         |                         | check    |
| no_allocation | production_P                | 65+    |  124752 |    7447 |  4.9796 |  4.6898 |  5.2315 | True         |                         | check    |
| no_allocation | production_P                | 55+    |  124752 |   33313 | 24.5054 | 23.9339 | 25.069  | True         |                         | check    |
| no_allocation | all_manufacturing           | 16-34  |  337780 |   92889 | 29.7622 | 29.3482 | 30.1329 | True         |                         | check    |
| no_allocation | all_manufacturing           | 35-54  |  337780 |  149699 | 44.4714 | 44.0352 | 44.907  | True         |                         | check    |
| no_allocation | all_manufacturing           | 55-64  |  337780 |   72650 | 20.1869 | 19.8512 | 20.5199 | True         |                         | check    |
| no_allocation | all_manufacturing           | 65+    |  337780 |   22542 |  5.5794 |  5.3955 |  5.7615 | True         |                         | check    |
| no_allocation | all_manufacturing           | 55+    |  337780 |   95192 | 25.7664 | 25.3819 | 26.1557 | True         |                         | check    |
| all_records   | all_employed_all_industries | 16-34  | 3765898 | 1183433 | 34.5636 | 34.4241 | 34.7113 | True         |                         | headline |
| all_records   | all_employed_all_industries | 35-54  | 3765898 | 1586002 | 41.9723 | 41.8254 | 42.1265 | True         |                         | headline |
| all_records   | all_employed_all_industries | 55-64  | 3765898 |  676331 | 16.6381 | 16.5342 | 16.7417 | True         |                         | headline |
| all_records   | all_employed_all_industries | 65+    | 3765898 |  320132 |  6.826  |  6.7605 |  6.8973 | True         |                         | headline |
| all_records   | all_employed_all_industries | 55+    | 3765898 |  996463 | 23.4641 | 23.3442 | 23.5876 | True         |                         | headline |
| no_allocation | all_employed_all_industries | 16-34  | 3643303 | 1139433 | 34.3889 | 34.2493 | 34.5401 | True         |                         | check    |
| no_allocation | all_employed_all_industries | 35-54  | 3643303 | 1538271 | 42.1005 | 41.9471 | 42.2579 | True         |                         | check    |
| no_allocation | all_employed_all_industries | 55-64  | 3643303 |  656753 | 16.7109 | 16.6041 | 16.8174 | True         |                         | check    |
| no_allocation | all_employed_all_industries | 65+    | 3643303 |  308846 |  6.7997 |  6.7304 |  6.8719 | True         |                         | check    |
| no_allocation | all_employed_all_industries | 55+    | 3643303 |  965599 | 23.5106 | 23.3893 | 23.6359 | True         |                         | check    |

## A1 — share aged 55+ by year

| check         | group         | band   |   n_den |   n_num |     pct |      lo |      hi | reportable   | not_reportable_reason   |   year | role     |
|:--------------|:--------------|:-------|--------:|--------:|--------:|--------:|--------:|:-------------|:------------------------|-------:|:---------|
| all_records   | maintenance_M | 55+    |    2127 |     642 | 27.0753 | 23.643  | 30.7132 | True         |                         |   2020 | headline |
| all_records   | maintenance_M | 55+    |    2085 |     662 | 30.5549 | 26.7732 | 34.5724 | True         |                         |   2021 | headline |
| all_records   | maintenance_M | 55+    |    1940 |     571 | 28.2926 | 24.4766 | 32.2994 | True         |                         |   2022 | headline |
| all_records   | maintenance_M | 55+    |    1956 |     599 | 28.5245 | 24.4878 | 32.1788 | True         |                         |   2023 | headline |
| all_records   | maintenance_M | 55+    |    1859 |     569 | 30.3469 | 26.1693 | 34.6706 | True         |                         |   2024 | headline |
| all_records   | maintenance_M | 55+    |    1689 |     483 | 27.6124 | 23.7814 | 31.8264 | True         |                         |   2025 | headline |
| all_records   | maintenance_M | 55+    |    1187 |     339 | 27.3119 | 22.6299 | 32.3248 | True         |                         |   2026 | headline |
| all_records   | production_P  | 55+    |   20596 |    5488 | 23.726  | 22.5808 | 24.8781 | True         |                         |   2020 | headline |
| all_records   | production_P  | 55+    |   21509 |    5491 | 23.7892 | 22.6914 | 25.0104 | True         |                         |   2021 | headline |
| all_records   | production_P  | 55+    |   20375 |    5480 | 25.1849 | 24.0001 | 26.409  | True         |                         |   2022 | headline |
| all_records   | production_P  | 55+    |   20106 |    5367 | 24.3188 | 23.2248 | 25.6178 | True         |                         |   2023 | headline |
| all_records   | production_P  | 55+    |   18245 |    4909 | 24.6824 | 23.4915 | 25.8889 | True         |                         |   2024 | headline |
| all_records   | production_P  | 55+    |   15380 |    4103 | 24.4673 | 23.2097 | 25.7677 | True         |                         |   2025 | headline |
| all_records   | production_P  | 55+    |   11876 |    3313 | 24.9008 | 23.4593 | 26.367  | True         |                         |   2026 | headline |
| no_allocation | maintenance_M | 55+    |    2072 |     625 | 27.0281 | 23.5174 | 30.6894 | True         |                         |   2020 | check    |
| no_allocation | maintenance_M | 55+    |    2028 |     645 | 30.5992 | 26.7528 | 34.6817 | True         |                         |   2021 | check    |
| no_allocation | maintenance_M | 55+    |    1891 |     562 | 28.6695 | 24.7895 | 32.7256 | True         |                         |   2022 | check    |
| no_allocation | maintenance_M | 55+    |    1903 |     584 | 28.6735 | 24.5083 | 32.4453 | True         |                         |   2023 | check    |
| no_allocation | maintenance_M | 55+    |    1812 |     554 | 30.4052 | 26.2264 | 34.7613 | True         |                         |   2024 | check    |
| no_allocation | maintenance_M | 55+    |    1648 |     471 | 27.5935 | 23.7187 | 31.8953 | True         |                         |   2025 | check    |
| no_allocation | maintenance_M | 55+    |    1158 |     337 | 27.8968 | 23.0846 | 33.0704 | True         |                         |   2026 | check    |
| no_allocation | production_P  | 55+    |   20068 |    5350 | 23.7261 | 22.5919 | 24.8889 | True         |                         |   2020 | check    |
| no_allocation | production_P  | 55+    |   20836 |    5306 | 23.8132 | 22.6794 | 25.0425 | True         |                         |   2021 | check    |
| no_allocation | production_P  | 55+    |   19840 |    5355 | 25.3365 | 24.1294 | 26.5762 | True         |                         |   2022 | check    |
| no_allocation | production_P  | 55+    |   19617 |    5252 | 24.4331 | 23.3142 | 25.7266 | True         |                         |   2023 | check    |
| no_allocation | production_P  | 55+    |   17841 |    4806 | 24.7316 | 23.5578 | 25.9058 | True         |                         |   2024 | check    |
| no_allocation | production_P  | 55+    |   14966 |    4003 | 24.578  | 23.2717 | 25.878  | True         |                         |   2025 | check    |
| no_allocation | production_P  | 55+    |   11584 |    3241 | 25.0657 | 23.5893 | 26.5506 | True         |                         |   2026 | check    |

## A2 — destination at t of production workers in manufacturing at t-1

| check                  | role                  | age_band   | category                |   n_den |   n_num |     pct |      lo |      hi | reportable   | not_reportable_reason   |
|:-----------------------|:----------------------|:-----------|:------------------------|--------:|--------:|--------:|--------:|--------:|:-------------|:------------------------|
| headline_no_allocation | headline (DL-42 rule) | all        | mfg_same_occupation     |   80890 |   73891 | 90.9771 | 90.7169 | 91.2273 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | mfg_other_production    |   80890 |    1651 |  2.1304 |  1.9977 |  2.2617 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | mfg_maintenance         |   80890 |      82 |  0.0993 |  0.0766 |  0.1231 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | mfg_other_occupation    |   80890 |    1034 |  1.3538 |  1.2569 |  1.4505 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | outside_mfg_maintenance |   80890 |      29 |  0.0406 |  0.025  |  0.0573 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | outside_mfg_other       |   80890 |    1371 |  1.8248 |  1.7203 |  1.9482 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | unemployed              |   80890 |    1030 |  1.3374 |  1.2455 |  1.4355 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | retired                 |   80890 |     419 |  0.4424 |  0.3942 |  0.4913 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | disabled                |   80890 |     200 |  0.2485 |  0.2084 |  0.2892 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | all        | other_nilf              |   80890 |    1183 |  1.5457 |  1.4426 |  1.6596 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | mfg_same_occupation     |   24315 |   21862 | 89.4885 | 88.9793 | 89.9667 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | mfg_other_production    |   24315 |     532 |  2.2814 |  2.0418 |  2.5449 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | mfg_maintenance         |   24315 |      26 |  0.1085 |  0.0634 |  0.1558 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | mfg_other_occupation    |   24315 |     334 |  1.4716 |  1.2896 |  1.6552 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | outside_mfg_maintenance |   24315 |      10 |  0.0411 |  0.0154 |  0.0715 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | outside_mfg_other       |   24315 |     579 |  2.5008 |  2.2782 |  2.7432 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | unemployed              |   24315 |     401 |  1.6706 |  1.4905 |  1.8746 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | retired                 |   24315 |       9 |  0.0326 |  0.0097 |  0.0618 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | disabled                |   24315 |      34 |  0.1522 |  0.0953 |  0.2129 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | other_nilf              |   24315 |     528 |  2.2527 |  2.0311 |  2.4843 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | mfg_same_occupation     |   34433 |   31743 | 91.8785 | 91.4906 | 92.2256 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | mfg_other_production    |   34433 |     733 |  2.2126 |  2.0202 |  2.4271 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | mfg_maintenance         |   34433 |      34 |  0.095  |  0.0616 |  0.1297 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | mfg_other_occupation    |   34433 |     426 |  1.303  |  1.1624 |  1.4505 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | outside_mfg_maintenance |   34433 |      15 |  0.054  |  0.0286 |  0.0869 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | outside_mfg_other       |   34433 |     536 |  1.6169 |  1.4716 |  1.7913 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | unemployed              |   34433 |     418 |  1.2867 |  1.1422 |  1.4312 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | retired                 |   34433 |      30 |  0.0822 |  0.0494 |  0.1185 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | disabled                |   34433 |      76 |  0.2152 |  0.1634 |  0.271  | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | other_nilf              |   34433 |     422 |  1.2561 |  1.1224 |  1.4007 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | mfg_same_occupation     |   22142 |   20286 | 91.3407 | 90.8716 | 91.8078 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | mfg_other_production    |   22142 |     386 |  1.7997 |  1.5768 |  2.0261 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | mfg_maintenance         |   22142 |      22 |  0.0949 |  0.0551 |  0.1408 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | mfg_other_occupation    |   22142 |     274 |  1.2904 |  1.1361 |  1.4633 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | outside_mfg_maintenance |   22142 |       4 |  0.0171 |  0.0022 |  0.037  | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | outside_mfg_other       |   22142 |     256 |  1.3185 |  1.1475 |  1.5096 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | unemployed              |   22142 |     211 |  1.0002 |  0.849  |  1.1331 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | retired                 |   22142 |     380 |  1.5727 |  1.3984 |  1.7587 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | disabled                |   22142 |      90 |  0.4273 |  0.3275 |  0.5328 | True         |                         |
| headline_no_allocation | headline (DL-42 rule) | 55+        | other_nilf              |   22142 |     233 |  1.1386 |  0.971  |  1.3193 | True         |                         |
| all_pairs              | all pairs             | all        | mfg_same_occupation     |   83923 |   74741 | 88.4369 | 88.1531 | 88.7106 | True         |                         |
| all_pairs              | all pairs             | all        | mfg_other_production    |   83923 |    1831 |  2.2912 |  2.1532 |  2.4286 | True         |                         |
| all_pairs              | all pairs             | all        | mfg_maintenance         |   83923 |      93 |  0.1078 |  0.0845 |  0.1333 | True         |                         |
| all_pairs              | all pairs             | all        | mfg_other_occupation    |   83923 |    1496 |  1.9146 |  1.8016 |  2.0262 | True         |                         |
| all_pairs              | all pairs             | all        | outside_mfg_maintenance |   83923 |      56 |  0.0732 |  0.0541 |  0.0955 | True         |                         |
| all_pairs              | all pairs             | all        | outside_mfg_other       |   83923 |    2483 |  3.2282 |  3.091  |  3.3858 | True         |                         |
| all_pairs              | all pairs             | all        | unemployed              |   83923 |    1083 |  1.3513 |  1.2556 |  1.4442 | True         |                         |
| all_pairs              | all pairs             | all        | retired                 |   83923 |     468 |  0.4782 |  0.4294 |  0.5279 | True         |                         |
| all_pairs              | all pairs             | all        | disabled                |   83923 |     242 |  0.2944 |  0.2499 |  0.3336 | True         |                         |
| all_pairs              | all pairs             | all        | other_nilf              |   83923 |    1430 |  1.8243 |  1.7102 |  1.9366 | True         |                         |
| all_pairs              | all pairs             | 16-34      | mfg_same_occupation     |   25420 |   22179 | 86.4502 | 85.9026 | 87.0016 | True         |                         |
| all_pairs              | all pairs             | 16-34      | mfg_other_production    |   25420 |     613 |  2.5351 |  2.2848 |  2.8137 | True         |                         |
| all_pairs              | all pairs             | 16-34      | mfg_maintenance         |   25420 |      28 |  0.113  |  0.0699 |  0.1603 | True         |                         |
| all_pairs              | all pairs             | 16-34      | mfg_other_occupation    |   25420 |     485 |  2.1117 |  1.8768 |  2.3353 | True         |                         |
| all_pairs              | all pairs             | 16-34      | outside_mfg_maintenance |   25420 |      19 |  0.0833 |  0.048  |  0.1253 | True         |                         |
| all_pairs              | all pairs             | 16-34      | outside_mfg_other       |   25420 |     979 |  4.1626 |  3.8658 |  4.4819 | True         |                         |
| all_pairs              | all pairs             | 16-34      | unemployed              |   25420 |     425 |  1.6851 |  1.5047 |  1.8877 | True         |                         |
| all_pairs              | all pairs             | 16-34      | retired                 |   25420 |      11 |  0.0412 |  0.015  |  0.0724 | True         |                         |
| all_pairs              | all pairs             | 16-34      | disabled                |   25420 |      39 |  0.1643 |  0.1077 |  0.2241 | True         |                         |
| all_pairs              | all pairs             | 16-34      | other_nilf              |   25420 |     642 |  2.6535 |  2.4075 |  2.8894 | True         |                         |
| all_pairs              | all pairs             | 35-54      | mfg_same_occupation     |   35599 |   32061 | 89.5125 | 89.082  | 89.8915 | True         |                         |
| all_pairs              | all pairs             | 35-54      | mfg_other_production    |   35599 |     790 |  2.3018 |  2.1117 |  2.5276 | True         |                         |
| all_pairs              | all pairs             | 35-54      | mfg_maintenance         |   35599 |      40 |  0.1045 |  0.0684 |  0.1414 | True         |                         |
| all_pairs              | all pairs             | 35-54      | mfg_other_occupation    |   35599 |     627 |  1.8577 |  1.6889 |  2.0379 | True         |                         |
| all_pairs              | all pairs             | 35-54      | outside_mfg_maintenance |   35599 |      26 |  0.0807 |  0.0486 |  0.1182 | True         |                         |
| all_pairs              | all pairs             | 35-54      | outside_mfg_other       |   35599 |     975 |  2.9652 |  2.7542 |  3.2015 | True         |                         |
| all_pairs              | all pairs             | 35-54      | unemployed              |   35599 |     440 |  1.3083 |  1.1617 |  1.4553 | True         |                         |
| all_pairs              | all pairs             | 35-54      | retired                 |   35599 |      35 |  0.0944 |  0.062  |  0.1311 | True         |                         |
| all_pairs              | all pairs             | 35-54      | disabled                |   35599 |     100 |  0.292  |  0.2236 |  0.358  | True         |                         |
| all_pairs              | all pairs             | 35-54      | other_nilf              |   35599 |     505 |  1.4829 |  1.3368 |  1.6479 | True         |                         |
| all_pairs              | all pairs             | 55+        | mfg_same_occupation     |   22904 |   20501 | 89.1747 | 88.67   | 89.6972 | True         |                         |
| all_pairs              | all pairs             | 55+        | mfg_other_production    |   22904 |     428 |  1.9588 |  1.7289 |  2.185  | True         |                         |
| all_pairs              | all pairs             | 55+        | mfg_maintenance         |   22904 |      25 |  0.1065 |  0.0636 |  0.1541 | True         |                         |
| all_pairs              | all pairs             | 55+        | mfg_other_occupation    |   22904 |     384 |  1.7567 |  1.5653 |  1.9531 | True         |                         |
| all_pairs              | all pairs             | 55+        | outside_mfg_maintenance |   22904 |      11 |  0.0473 |  0.0206 |  0.0811 | True         |                         |
| all_pairs              | all pairs             | 55+        | outside_mfg_other       |   22904 |     529 |  2.4692 |  2.2195 |  2.7339 | True         |                         |
| all_pairs              | all pairs             | 55+        | unemployed              |   22904 |     218 |  0.9938 |  0.8441 |  1.1242 | True         |                         |
| all_pairs              | all pairs             | 55+        | retired                 |   22904 |     422 |  1.6928 |  1.5181 |  1.8871 | True         |                         |
| all_pairs              | all pairs             | 55+        | disabled                |   22904 |     103 |  0.4663 |  0.3633 |  0.5771 | True         |                         |
| all_pairs              | all pairs             | 55+        | other_nilf              |   22904 |     283 |  1.3339 |  1.1522 |  1.517  | True         |                         |
| i_reversal             | check                 | all        | mfg_same_occupation     |   80890 |   74320 | 91.5425 | 91.279  | 91.7901 | True         |                         |
| i_reversal             | check                 | all        | mfg_other_production    |   80890 |    1538 |  1.9858 |  1.8744 |  2.1025 | True         |                         |
| i_reversal             | check                 | all        | mfg_maintenance         |   80890 |      80 |  0.097  |  0.0742 |  0.121  | True         |                         |
| i_reversal             | check                 | all        | mfg_other_occupation    |   80890 |     992 |  1.2935 |  1.2018 |  1.3867 | True         |                         |
| i_reversal             | check                 | all        | outside_mfg_maintenance |   80890 |      28 |  0.0393 |  0.0239 |  0.0563 | True         |                         |
| i_reversal             | check                 | all        | outside_mfg_other       |   80890 |    1323 |  1.7534 |  1.6514 |  1.8724 | True         |                         |
| i_reversal             | check                 | all        | unemployed              |   80890 |     932 |  1.2068 |  1.1215 |  1.2956 | True         |                         |
| i_reversal             | check                 | all        | retired                 |   80890 |     397 |  0.4197 |  0.3716 |  0.4669 | True         |                         |
| i_reversal             | check                 | all        | disabled                |   80890 |     184 |  0.2308 |  0.1918 |  0.2693 | True         |                         |
| i_reversal             | check                 | all        | other_nilf              |   80890 |    1096 |  1.4311 |  1.3361 |  1.5405 | True         |                         |
| i_reversal             | check                 | 16-34      | mfg_same_occupation     |   24315 |   21990 | 90.0463 | 89.5514 | 90.5058 | True         |                         |
| i_reversal             | check                 | 16-34      | mfg_other_production    |   24315 |     502 |  2.152  |  1.9326 |  2.3822 | True         |                         |
| i_reversal             | check                 | 16-34      | mfg_maintenance         |   24315 |      24 |  0.1015 |  0.0589 |  0.1479 | True         |                         |
| i_reversal             | check                 | 16-34      | mfg_other_occupation    |   24315 |     320 |  1.4112 |  1.2305 |  1.5935 | True         |                         |
| i_reversal             | check                 | 16-34      | outside_mfg_maintenance |   24315 |      10 |  0.0411 |  0.0154 |  0.0715 | True         |                         |
| i_reversal             | check                 | 16-34      | outside_mfg_other       |   24315 |     559 |  2.388  |  2.1727 |  2.6206 | True         |                         |
| i_reversal             | check                 | 16-34      | unemployed              |   24315 |     365 |  1.5106 |  1.338  |  1.693  | True         |                         |
| i_reversal             | check                 | 16-34      | retired                 |   24315 |       9 |  0.0326 |  0.0097 |  0.0618 | True         |                         |
| i_reversal             | check                 | 16-34      | disabled                |   24315 |      33 |  0.1478 |  0.0927 |  0.2071 | True         |                         |
| i_reversal             | check                 | 16-34      | other_nilf              |   24315 |     503 |  2.169  |  1.9516 |  2.3897 | True         |                         |
| i_reversal             | check                 | 35-54      | mfg_same_occupation     |   34433 |   31919 | 92.4313 | 92.075  | 92.7487 | True         |                         |
| i_reversal             | check                 | 35-54      | mfg_other_production    |   34433 |     685 |  2.07   |  1.8922 |  2.2641 | True         |                         |
| i_reversal             | check                 | 35-54      | mfg_maintenance         |   34433 |      34 |  0.095  |  0.0616 |  0.1297 | True         |                         |
| i_reversal             | check                 | 35-54      | mfg_other_occupation    |   34433 |     411 |  1.2424 |  1.1062 |  1.3853 | True         |                         |
| i_reversal             | check                 | 35-54      | outside_mfg_maintenance |   34433 |      14 |  0.0511 |  0.0256 |  0.0827 | True         |                         |
| i_reversal             | check                 | 35-54      | outside_mfg_other       |   34433 |     515 |  1.5528 |  1.4066 |  1.7233 | True         |                         |
| i_reversal             | check                 | 35-54      | unemployed              |   34433 |     375 |  1.1495 |  1.0172 |  1.2808 | True         |                         |
| i_reversal             | check                 | 35-54      | retired                 |   34433 |      26 |  0.0712 |  0.0412 |  0.1037 | True         |                         |
| i_reversal             | check                 | 35-54      | disabled                |   34433 |      68 |  0.1965 |  0.15   |  0.2495 | True         |                         |
| i_reversal             | check                 | 35-54      | other_nilf              |   34433 |     386 |  1.1402 |  1.0192 |  1.2814 | True         |                         |
| i_reversal             | check                 | 55+        | mfg_same_occupation     |   22142 |   20411 | 91.9371 | 91.5089 | 92.3923 | True         |                         |
| i_reversal             | check                 | 55+        | mfg_other_production    |   22142 |     351 |  1.6321 |  1.4297 |  1.8344 | True         |                         |
| i_reversal             | check                 | 55+        | mfg_maintenance         |   22142 |      22 |  0.0949 |  0.0551 |  0.1408 | True         |                         |
| i_reversal             | check                 | 55+        | mfg_other_occupation    |   22142 |     261 |  1.2308 |  1.0792 |  1.4013 | True         |                         |
| i_reversal             | check                 | 55+        | outside_mfg_maintenance |   22142 |       4 |  0.0171 |  0.0022 |  0.037  | True         |                         |
| i_reversal             | check                 | 55+        | outside_mfg_other       |   22142 |     249 |  1.2873 |  1.1118 |  1.4831 | True         |                         |
| i_reversal             | check                 | 55+        | unemployed              |   22142 |     192 |  0.9181 |  0.7772 |  1.0535 | True         |                         |
| i_reversal             | check                 | 55+        | retired                 |   22142 |     362 |  1.5011 |  1.3292 |  1.6853 | True         |                         |
| i_reversal             | check                 | 55+        | disabled                |   22142 |      83 |  0.3944 |  0.3013 |  0.4959 | True         |                         |
| i_reversal             | check                 | 55+        | other_nilf              |   22142 |     207 |  0.987  |  0.8375 |  1.1456 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | mfg_same_occupation     |   56223 |   51552 | 91.3193 | 90.9987 | 91.6049 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | mfg_other_production    |   56223 |    1159 |  2.1483 |  1.9948 |  2.3103 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | mfg_maintenance         |   56223 |      55 |  0.0962 |  0.0689 |  0.1257 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | mfg_other_occupation    |   56223 |     736 |  1.3916 |  1.2754 |  1.5081 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | outside_mfg_maintenance |   56223 |      26 |  0.0519 |  0.032  |  0.0759 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | outside_mfg_other       |   56223 |     963 |  1.8346 |  1.7052 |  1.9816 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | unemployed              |   56223 |     527 |  1.0082 |  0.9137 |  1.1061 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | retired                 |   56223 |     296 |  0.4499 |  0.3893 |  0.5077 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | disabled                |   56223 |     140 |  0.2564 |  0.2101 |  0.3029 | True         |                         |
| ii_excl_2020_2021      | check                 | all        | other_nilf              |   56223 |     769 |  1.4437 |  1.327  |  1.57   | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | mfg_same_occupation     |   16957 |   15336 | 89.9484 | 89.3647 | 90.4842 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | mfg_other_production    |   16957 |     361 |  2.2283 |  1.9618 |  2.5431 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | mfg_maintenance         |   16957 |      20 |  0.1188 |  0.0647 |  0.1778 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | mfg_other_occupation    |   16957 |     234 |  1.5019 |  1.262  |  1.7306 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | outside_mfg_maintenance |   16957 |      10 |  0.0573 |  0.0212 |  0.0995 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | outside_mfg_other       |   16957 |     404 |  2.5414 |  2.2616 |  2.8298 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | unemployed              |   16957 |     213 |  1.2899 |  1.1099 |  1.4891 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | retired                 |   16957 |       7 |  0.0354 |  0.0085 |  0.0734 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | disabled                |   16957 |      24 |  0.1654 |  0.0946 |  0.2389 | True         |                         |
| ii_excl_2020_2021      | check                 | 16-34      | other_nilf              |   16957 |     348 |  2.1132 |  1.8629 |  2.3679 | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | mfg_same_occupation     |   23709 |   21902 | 92.0983 | 91.6596 | 92.516  | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | mfg_other_production    |   23709 |     517 |  2.2807 |  2.0578 |  2.5308 | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | mfg_maintenance         |   23709 |      20 |  0.0796 |  0.0421 |  0.1206 | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | mfg_other_occupation    |   23709 |     302 |  1.3409 |  1.1545 |  1.5291 | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | outside_mfg_maintenance |   23709 |      13 |  0.0668 |  0.0313 |  0.107  | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | outside_mfg_other       |   23709 |     385 |  1.6422 |  1.446  |  1.8464 | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | unemployed              |   23709 |     216 |  0.9813 |  0.8353 |  1.1345 | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | retired                 |   23709 |      20 |  0.0779 |  0.0411 |  0.1169 | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | disabled                |   23709 |      51 |  0.2093 |  0.1473 |  0.2732 | True         |                         |
| ii_excl_2020_2021      | check                 | 35-54      | other_nilf              |   23709 |     283 |  1.223  |  1.0547 |  1.3861 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | mfg_same_occupation     |   15557 |   14314 | 91.7375 | 91.1847 | 92.2325 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | mfg_other_production    |   15557 |     281 |  1.8283 |  1.542  |  2.0987 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | mfg_maintenance         |   15557 |      15 |  0.0954 |  0.0485 |  0.1533 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | mfg_other_occupation    |   15557 |     200 |  1.3379 |  1.1534 |  1.5563 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | outside_mfg_maintenance |   15557 |       3 |  0.0203 |  0      |  0.0464 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | outside_mfg_other       |   15557 |     174 |  1.2708 |  1.0661 |  1.4968 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | unemployed              |   15557 |      98 |  0.7006 |  0.5487 |  0.8503 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | retired                 |   15557 |     269 |  1.5866 |  1.3794 |  1.7897 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | disabled                |   15557 |      65 |  0.4487 |  0.3291 |  0.5752 | True         |                         |
| ii_excl_2020_2021      | check                 | 55+        | other_nilf              |   15557 |     138 |  0.9739 |  0.7996 |  1.1636 | True         |                         |

## A3 — inflow to and outflow from maintenance in manufacturing

| check                  | role                  | age_band   | category            |   n_den |   n_num |    pct |     lo |     hi | reportable   | not_reportable_reason   | direction   |
|:-----------------------|:----------------------|:-----------|:--------------------|--------:|--------:|-------:|-------:|-------:|:-------------|:------------------------|:------------|
| headline_no_allocation | headline (DL-42 rule) | all        | production          |    8267 |      92 | 1.128  | 0.8682 | 1.3878 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | all        | other_employed      |    8267 |     184 | 2.31   | 1.9414 | 2.6985 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | all        | unemployed          |    8267 |      62 | 0.7474 | 0.5445 | 0.9665 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | all        | retired             |    8267 |      43 | 0.4952 | 0.3265 | 0.6805 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | all        | disabled            |    8267 |      17 | 0.2059 | 0.103  | 0.3396 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | all        | other_nilf          |    8267 |      55 | 0.7093 | 0.5235 | 0.9105 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | all        | production          |    8241 |      88 | 1.0661 | 0.8324 | 1.3266 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | all        | other_employed      |    8241 |     186 | 2.313  | 1.9361 | 2.6593 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | all        | unemployed          |    8241 |      61 | 0.7155 | 0.5203 | 0.9454 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | all        | not_in_labour_force |    8241 |      81 | 1.0178 | 0.784  | 1.2807 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | production          |    2059 |      26 | 1.3384 | 0.7774 | 1.9251 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | other_employed      |    2059 |      54 | 2.7606 | 1.9033 | 3.5897 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | unemployed          |    2059 |      22 | 1.0817 | 0.6282 | 1.5643 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | retired             |    2059 |       1 | 0.0505 | 0      | 0.1591 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | disabled            |    2059 |       1 | 0.043  | 0      | 0.1609 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | other_nilf          |    2059 |      24 | 1.1749 | 0.7257 | 1.7322 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | production          |    2053 |      27 | 1.4022 | 0.841  | 2.0079 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | other_employed      |    2053 |      54 | 2.6979 | 1.9195 | 3.5567 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | unemployed          |    2053 |      21 | 1.1064 | 0.6238 | 1.7138 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 16-34      | not_in_labour_force |    2053 |      24 | 1.2488 | 0.7029 | 1.8389 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | production          |    3646 |      42 | 1.1216 | 0.7587 | 1.5233 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | other_employed      |    3646 |      84 | 2.3407 | 1.7979 | 2.9647 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | unemployed          |    3646 |      19 | 0.5061 | 0.2665 | 0.8047 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | retired             |    3646 |       3 | 0.0851 | 0      | 0.2137 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | disabled            |    3646 |       7 | 0.204  | 0.0526 | 0.3986 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | other_nilf          |    3646 |      23 | 0.7396 | 0.4491 | 1.0372 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | production          |    3633 |      38 | 1.0143 | 0.6671 | 1.3816 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | other_employed      |    3633 |      78 | 2.2386 | 1.7037 | 2.7926 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | unemployed          |    3633 |      31 | 0.7349 | 0.4648 | 1.0403 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 35-54      | not_in_labour_force |    3633 |      21 | 0.6645 | 0.3672 | 1.0331 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 55+        | production          |    2562 |      24 | 0.9531 | 0.5406 | 1.4385 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 55+        | other_employed      |    2562 |      46 | 1.869  | 1.3463 | 2.535  | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 55+        | unemployed          |    2562 |      21 | 0.8176 | 0.4561 | 1.1935 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 55+        | retired             |    2562 |      39 | 1.5024 | 0.9804 | 2.1068 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 55+        | disabled            |    2562 |       9 | 0.3516 | 0.1194 | 0.6406 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 55+        | other_nilf          |    2562 |       8 | 0.2557 | 0.0853 | 0.4667 | True         |                         | outflow     |
| headline_no_allocation | headline (DL-42 rule) | 55+        | production          |    2555 |      23 | 0.8493 | 0.4932 | 1.2722 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 55+        | other_employed      |    2555 |      54 | 2.0875 | 1.462  | 2.6756 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 55+        | unemployed          |    2555 |       9 | 0.3435 | 0.1162 | 0.6312 | True         |                         | inflow      |
| headline_no_allocation | headline (DL-42 rule) | 55+        | not_in_labour_force |    2555 |      36 | 1.3481 | 0.9053 | 1.86   | True         |                         | inflow      |
| all_pairs              | all pairs             | all        | production          |    8524 |     120 | 1.4579 | 1.1672 | 1.7647 | True         |                         | outflow     |
| all_pairs              | all pairs             | all        | other_employed      |    8524 |     308 | 3.9583 | 3.4955 | 4.5047 | True         |                         | outflow     |
| all_pairs              | all pairs             | all        | unemployed          |    8524 |      63 | 0.7427 | 0.5527 | 0.9583 | True         |                         | outflow     |
| all_pairs              | all pairs             | all        | retired             |    8524 |      48 | 0.5448 | 0.3677 | 0.7395 | True         |                         | outflow     |
| all_pairs              | all pairs             | all        | disabled            |    8524 |      17 | 0.1989 | 0.0995 | 0.3269 | True         |                         | outflow     |
| all_pairs              | all pairs             | all        | other_nilf          |    8524 |      71 | 0.913  | 0.6907 | 1.137  | True         |                         | outflow     |
| all_pairs              | all pairs             | all        | production          |    8518 |      99 | 1.1595 | 0.9118 | 1.4221 | True         |                         | inflow      |
| all_pairs              | all pairs             | all        | other_employed      |    8518 |     341 | 4.1045 | 3.6123 | 4.5885 | True         |                         | inflow      |
| all_pairs              | all pairs             | all        | unemployed          |    8518 |      67 | 0.7831 | 0.5749 | 1.0145 | True         |                         | inflow      |
| all_pairs              | all pairs             | all        | not_in_labour_force |    8518 |     106 | 1.2957 | 1.0228 | 1.5893 | True         |                         | inflow      |
| all_pairs              | all pairs             | 16-34      | production          |    2129 |      34 | 1.7629 | 1.0953 | 2.4371 | True         |                         | outflow     |
| all_pairs              | all pairs             | 16-34      | other_employed      |    2129 |      87 | 4.7034 | 3.5712 | 5.7716 | True         |                         | outflow     |
| all_pairs              | all pairs             | 16-34      | unemployed          |    2129 |      22 | 1.0406 | 0.603  | 1.5055 | True         |                         | outflow     |
| all_pairs              | all pairs             | 16-34      | retired             |    2129 |       1 | 0.0486 | 0      | 0.1524 | True         |                         | outflow     |
| all_pairs              | all pairs             | 16-34      | disabled            |    2129 |       1 | 0.0414 | 0      | 0.1551 | True         |                         | outflow     |
| all_pairs              | all pairs             | 16-34      | other_nilf          |    2129 |      33 | 1.5574 | 1.0093 | 2.1868 | True         |                         | outflow     |
| all_pairs              | all pairs             | 16-34      | production          |    2126 |      29 | 1.4799 | 0.9188 | 2.1042 | True         |                         | inflow      |
| all_pairs              | all pairs             | 16-34      | other_employed      |    2126 |      95 | 4.8087 | 3.7341 | 5.893  | True         |                         | inflow      |
| all_pairs              | all pairs             | 16-34      | unemployed          |    2126 |      24 | 1.2144 | 0.7048 | 1.8559 | True         |                         | inflow      |
| all_pairs              | all pairs             | 16-34      | not_in_labour_force |    2126 |      32 | 1.5426 | 0.9561 | 2.2601 | True         |                         | inflow      |
| all_pairs              | all pairs             | 35-54      | production          |    3768 |      56 | 1.4511 | 1.0489 | 1.9151 | True         |                         | outflow     |
| all_pairs              | all pairs             | 35-54      | other_employed      |    3768 |     142 | 4.0461 | 3.3261 | 4.838  | True         |                         | outflow     |
| all_pairs              | all pairs             | 35-54      | unemployed          |    3768 |      20 | 0.5338 | 0.2915 | 0.8242 | True         |                         | outflow     |
| all_pairs              | all pairs             | 35-54      | retired             |    3768 |       4 | 0.13   | 0.0071 | 0.3069 | True         |                         | outflow     |
| all_pairs              | all pairs             | 35-54      | disabled            |    3768 |       7 | 0.1965 | 0.0504 | 0.3848 | True         |                         | outflow     |
| all_pairs              | all pairs             | 35-54      | other_nilf          |    3768 |      28 | 0.9123 | 0.5723 | 1.2665 | True         |                         | outflow     |
| all_pairs              | all pairs             | 35-54      | production          |    3767 |      44 | 1.1055 | 0.736  | 1.4898 | True         |                         | inflow      |
| all_pairs              | all pairs             | 35-54      | other_employed      |    3767 |     155 | 4.2057 | 3.4431 | 4.95   | True         |                         | inflow      |
| all_pairs              | all pairs             | 35-54      | unemployed          |    3767 |      34 | 0.827  | 0.5429 | 1.1703 | True         |                         | inflow      |
| all_pairs              | all pairs             | 35-54      | not_in_labour_force |    3767 |      31 | 0.9328 | 0.5764 | 1.3118 | True         |                         | inflow      |
| all_pairs              | all pairs             | 55+        | production          |    2627 |      30 | 1.1976 | 0.7382 | 1.7104 | True         |                         | outflow     |
| all_pairs              | all pairs             | 55+        | other_employed      |    2627 |      79 | 3.1637 | 2.4323 | 4.0245 | True         |                         | outflow     |
| all_pairs              | all pairs             | 55+        | unemployed          |    2627 |      21 | 0.7962 | 0.4442 | 1.1586 | True         |                         | outflow     |
| all_pairs              | all pairs             | 55+        | retired             |    2627 |      43 | 1.6162 | 1.0884 | 2.2452 | True         |                         | outflow     |
| all_pairs              | all pairs             | 55+        | disabled            |    2627 |       9 | 0.3424 | 0.1167 | 0.6244 | True         |                         | outflow     |
| all_pairs              | all pairs             | 55+        | other_nilf          |    2627 |      10 | 0.3424 | 0.1338 | 0.605  | True         |                         | outflow     |
| all_pairs              | all pairs             | 55+        | production          |    2625 |      26 | 0.9579 | 0.579  | 1.4022 | True         |                         | inflow      |
| all_pairs              | all pairs             | 55+        | other_employed      |    2625 |      91 | 3.3266 | 2.5655 | 4.1345 | True         |                         | inflow      |
| all_pairs              | all pairs             | 55+        | unemployed          |    2625 |       9 | 0.3343 | 0.1128 | 0.6156 | True         |                         | inflow      |
| all_pairs              | all pairs             | 55+        | not_in_labour_force |    2625 |      43 | 1.6298 | 1.1466 | 2.1917 | True         |                         | inflow      |
| i_reversal             | check                 | all        | production          |    8267 |      89 | 1.0973 | 0.8488 | 1.363  | True         |                         | outflow     |
| i_reversal             | check                 | all        | other_employed      |    8267 |     178 | 2.2543 | 1.8978 | 2.6478 | True         |                         | outflow     |
| i_reversal             | check                 | all        | unemployed          |    8267 |      57 | 0.6868 | 0.4896 | 0.8959 | True         |                         | outflow     |
| i_reversal             | check                 | all        | retired             |    8267 |      41 | 0.4744 | 0.3115 | 0.6568 | True         |                         | outflow     |
| i_reversal             | check                 | all        | disabled            |    8267 |      14 | 0.163  | 0.0762 | 0.2687 | True         |                         | outflow     |
| i_reversal             | check                 | all        | other_nilf          |    8267 |      47 | 0.6151 | 0.4449 | 0.8075 | True         |                         | outflow     |
| i_reversal             | check                 | all        | production          |    8215 |      85 | 1.0402 | 0.8059 | 1.2979 | True         |                         | inflow      |
| i_reversal             | check                 | all        | other_employed      |    8215 |     177 | 2.191  | 1.8243 | 2.5322 | True         |                         | inflow      |
| i_reversal             | check                 | all        | unemployed          |    8215 |      60 | 0.7015 | 0.51   | 0.9258 | True         |                         | inflow      |
| i_reversal             | check                 | all        | not_in_labour_force |    8215 |      68 | 0.9009 | 0.6787 | 1.15   | True         |                         | inflow      |
| i_reversal             | check                 | 16-34      | production          |    2059 |      26 | 1.3384 | 0.7774 | 1.9251 | True         |                         | outflow     |
| i_reversal             | check                 | 16-34      | other_employed      |    2059 |      53 | 2.7332 | 1.9015 | 3.5615 | True         |                         | outflow     |
| i_reversal             | check                 | 16-34      | unemployed          |    2059 |      21 | 1.0233 | 0.5885 | 1.4971 | True         |                         | outflow     |
| i_reversal             | check                 | 16-34      | retired             |    2059 |       1 | 0.0505 | 0      | 0.1591 | True         |                         | outflow     |
| i_reversal             | check                 | 16-34      | disabled            |    2059 |       0 | 0      | 0      | 0      | False        | no event                | outflow     |
| i_reversal             | check                 | 16-34      | other_nilf          |    2059 |      21 | 1.0455 | 0.6158 | 1.5684 | True         |                         | outflow     |
| i_reversal             | check                 | 16-34      | production          |    2043 |      25 | 1.321  | 0.7705 | 1.8777 | True         |                         | inflow      |
| i_reversal             | check                 | 16-34      | other_employed      |    2043 |      51 | 2.4819 | 1.7183 | 3.2988 | True         |                         | inflow      |
| i_reversal             | check                 | 16-34      | unemployed          |    2043 |      20 | 1.0499 | 0.558  | 1.6583 | True         |                         | inflow      |
| i_reversal             | check                 | 16-34      | not_in_labour_force |    2043 |      20 | 1.0975 | 0.5923 | 1.6494 | True         |                         | inflow      |
| i_reversal             | check                 | 35-54      | production          |    3646 |      40 | 1.072  | 0.7124 | 1.4571 | True         |                         | outflow     |
| i_reversal             | check                 | 35-54      | other_employed      |    3646 |      81 | 2.2595 | 1.7137 | 2.8579 | True         |                         | outflow     |
| i_reversal             | check                 | 35-54      | unemployed          |    3646 |      16 | 0.4448 | 0.2248 | 0.72   | True         |                         | outflow     |
| i_reversal             | check                 | 35-54      | retired             |    3646 |       3 | 0.0851 | 0      | 0.2137 | True         |                         | outflow     |
| i_reversal             | check                 | 35-54      | disabled            |    3646 |       5 | 0.1327 | 0.0228 | 0.2759 | True         |                         | outflow     |
| i_reversal             | check                 | 35-54      | other_nilf          |    3646 |      20 | 0.6579 | 0.375  | 0.9627 | True         |                         | outflow     |
| i_reversal             | check                 | 35-54      | production          |    3626 |      37 | 1.0026 | 0.6637 | 1.3711 | True         |                         | inflow      |
| i_reversal             | check                 | 35-54      | other_employed      |    3626 |      74 | 2.1287 | 1.6191 | 2.6916 | True         |                         | inflow      |
| i_reversal             | check                 | 35-54      | unemployed          |    3626 |      31 | 0.7362 | 0.4655 | 1.0421 | True         |                         | inflow      |
| i_reversal             | check                 | 35-54      | not_in_labour_force |    3626 |      19 | 0.6106 | 0.3239 | 0.9814 | True         |                         | inflow      |
| i_reversal             | check                 | 55+        | production          |    2562 |      23 | 0.9239 | 0.5144 | 1.419  | True         |                         | outflow     |
| i_reversal             | check                 | 55+        | other_employed      |    2562 |      44 | 1.8267 | 1.3029 | 2.4957 | True         |                         | outflow     |
| i_reversal             | check                 | 55+        | unemployed          |    2562 |      20 | 0.7562 | 0.4137 | 1.1125 | True         |                         | outflow     |
| i_reversal             | check                 | 55+        | retired             |    2562 |      37 | 1.4319 | 0.9037 | 2.0222 | True         |                         | outflow     |
| i_reversal             | check                 | 55+        | disabled            |    2562 |       9 | 0.3516 | 0.1194 | 0.6406 | True         |                         | outflow     |
| i_reversal             | check                 | 55+        | other_nilf          |    2562 |       6 | 0.1731 | 0.0432 | 0.3609 | True         |                         | outflow     |
| i_reversal             | check                 | 55+        | production          |    2546 |      23 | 0.8514 | 0.4948 | 1.276  | True         |                         | inflow      |
| i_reversal             | check                 | 55+        | other_employed      |    2546 |      52 | 2.0307 | 1.4029 | 2.6237 | True         |                         | inflow      |
| i_reversal             | check                 | 55+        | unemployed          |    2546 |       9 | 0.3443 | 0.1166 | 0.6326 | True         |                         | inflow      |
| i_reversal             | check                 | 55+        | not_in_labour_force |    2546 |      29 | 1.1671 | 0.7605 | 1.6564 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | all        | production          |    5764 |      66 | 1.2232 | 0.9012 | 1.5436 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | all        | other_employed      |    5764 |     139 | 2.5069 | 2.075  | 3.0226 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | all        | unemployed          |    5764 |      32 | 0.5368 | 0.3437 | 0.7459 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | all        | retired             |    5764 |      35 | 0.5879 | 0.3676 | 0.8369 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | all        | disabled            |    5764 |      13 | 0.2421 | 0.1089 | 0.4021 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | all        | other_nilf          |    5764 |      38 | 0.6774 | 0.4632 | 0.9285 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | all        | production          |    5728 |      58 | 1.0131 | 0.7306 | 1.3224 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | all        | other_employed      |    5728 |     136 | 2.4583 | 1.982  | 2.9141 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | all        | unemployed          |    5728 |      30 | 0.422  | 0.2646 | 0.6081 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | all        | not_in_labour_force |    5728 |      63 | 1.1134 | 0.8061 | 1.4488 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 16-34      | production          |    1500 |      20 | 1.4315 | 0.7558 | 2.1712 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 16-34      | other_employed      |    1500 |      41 | 2.8773 | 1.8963 | 3.9266 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 16-34      | unemployed          |    1500 |      13 | 0.8078 | 0.3913 | 1.3352 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 16-34      | retired             |    1500 |       1 | 0.0684 | 0      | 0.2166 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 16-34      | disabled            |    1500 |       1 | 0.0583 | 0      | 0.2164 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 16-34      | other_nilf          |    1500 |      18 | 1.1037 | 0.5914 | 1.7118 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 16-34      | production          |    1493 |      21 | 1.5037 | 0.8398 | 2.2643 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 16-34      | other_employed      |    1493 |      39 | 2.866  | 1.8972 | 3.9062 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 16-34      | unemployed          |    1493 |      11 | 0.6156 | 0.2306 | 1.0881 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 16-34      | not_in_labour_force |    1493 |      21 | 1.4413 | 0.7446 | 2.2016 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 35-54      | production          |    2509 |      28 | 1.1356 | 0.6905 | 1.6292 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 35-54      | other_employed      |    2509 |      62 | 2.5253 | 1.8568 | 3.2777 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 35-54      | unemployed          |    2509 |       8 | 0.3237 | 0.1    | 0.6271 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 35-54      | retired             |    2509 |       2 | 0.1084 | 0      | 0.2885 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 35-54      | disabled            |    2509 |       5 | 0.2098 | 0.0322 | 0.4474 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 35-54      | other_nilf          |    2509 |      17 | 0.7842 | 0.4376 | 1.1895 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 35-54      | production          |    2498 |      21 | 0.7996 | 0.4302 | 1.1951 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 35-54      | other_employed      |    2498 |      60 | 2.4955 | 1.8194 | 3.2373 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 35-54      | unemployed          |    2498 |      15 | 0.4764 | 0.2261 | 0.7931 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 35-54      | not_in_labour_force |    2498 |      17 | 0.788  | 0.4043 | 1.2751 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 55+        | production          |    1755 |      18 | 1.1667 | 0.6143 | 1.8359 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 55+        | other_employed      |    1755 |      36 | 2.1433 | 1.4242 | 2.9872 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 55+        | unemployed          |    1755 |      11 | 0.6129 | 0.2584 | 0.992  | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 55+        | retired             |    1755 |      32 | 1.7826 | 1.104  | 2.6008 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 55+        | disabled            |    1755 |       7 | 0.4574 | 0.1359 | 0.8716 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 55+        | other_nilf          |    1755 |       3 | 0.1295 | 0      | 0.3241 | True         |                         | outflow     |
| ii_excl_2020_2021      | check                 | 55+        | production          |    1737 |      16 | 0.8895 | 0.4615 | 1.4209 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 55+        | other_employed      |    1737 |      37 | 2.0281 | 1.3496 | 2.77   | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 55+        | unemployed          |    1737 |       4 | 0.1615 | 0.0041 | 0.4213 | True         |                         | inflow      |
| ii_excl_2020_2021      | check                 | 55+        | not_in_labour_force |    1737 |      25 | 1.3102 | 0.7841 | 1.9309 | True         |                         | inflow      |

## A3 — balance

| check                  | role                  | ratio                                          |   value |     lo |     hi |   weighted_numerator |   weighted_denominator |   events_numerator |   events_denominator |   share_draws_gt_1 | reportable   |
|:-----------------------|:----------------------|:-----------------------------------------------|--------:|-------:|-------:|---------------------:|-----------------------:|-------------------:|---------------------:|-------------------:|:-------------|
| headline_no_allocation | headline (DL-42 rule) | inflow from production / outflow to retirement |  2.1441 | 1.3977 | 3.4369 |     278697           |       129981           |                 88 |                   43 |              1     | True         |
| headline_no_allocation | headline (DL-42 rule) | all inflow / all outflow                       |  0.91   | 0.8024 | 1.0345 |          1.3365e+06  |            1.46873e+06 |                416 |                  453 |              0.059 | True         |
| all_pairs              | all pairs             | inflow from production / outflow to retirement |  2.1189 | 1.4192 | 3.2663 |     313591           |       147999           |                 99 |                   48 |              1     | True         |
| all_pairs              | all pairs             | all inflow / all outflow                       |  0.9353 | 0.8467 | 1.0372 |          1.98588e+06 |            2.12329e+06 |                613 |                  627 |              0.101 | True         |
| i_reversal             | check                 | inflow from production / outflow to retirement |  2.1776 | 1.4202 | 3.5128 |     271132           |       124507           |                 85 |                   41 |              1     | True         |
| i_reversal             | check                 | all inflow / all outflow                       |  0.9073 | 0.7907 | 1.0367 |          1.25991e+06 |            1.38869e+06 |                390 |                  426 |              0.068 | True         |
| ii_excl_2020_2021      | check                 | inflow from production / outflow to retirement |  1.7097 | 1.0302 | 3.0102 |     190214           |       111258           |                 58 |                   35 |              0.981 | True         |
| ii_excl_2020_2021      | check                 | all inflow / all outflow                       |  0.8603 | 0.7335 | 0.9896 |     940086           |            1.09278e+06 |                287 |                  323 |              0.021 | True         |
