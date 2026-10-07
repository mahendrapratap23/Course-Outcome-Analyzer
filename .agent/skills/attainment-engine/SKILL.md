---
name: attainment-engine
description: Pure-function computation engine for NBA/NAAC direct and indirect CO attainment, attainment level rubrics, PO roll-up, at-risk student identification, and score distributions.
---

# Attainment Engine

Pure computational functions without web dependencies for academic outcome analytics.

## Core Computations
1. **`co_attainment(marks, threshold=60)`**:
   Computes the direct percentage of students who scored `>= threshold%` in their aggregate marks for each CO.
2. **`level(pct)`**:
   NBA 3-tier attainment level rubric:
   - `>= 70%` -> Level 3
   - `60% - 69%` -> Level 2
   - `50% - 59%` -> Level 1
   - `< 50%` -> Level 0
3. **`final_co(direct_pct, indirect_pct, w_direct=0.8)`**:
   Combined direct (`w_direct`, default 0.8) and indirect survey attainment (`1 - w_direct`, default 0.2).
4. **`po_attainment(co_levels, co_po_matrix)`**:
   Weighted-average roll-up of CO attainment levels into Program Outcomes (PO1-PO6) based on matrix weights (1-3).
5. **`weak_students(marks, threshold=60, min_cos=2)`**:
   Filters and identifies students struggling across 2 or more Course Outcomes with specific weak CO lists.
6. **`score_distribution(marks, co)`**:
   Histogram binning (e.g., 0-20, 20-40, 40-60, 60-80, 80-100) for visual distribution charts.
