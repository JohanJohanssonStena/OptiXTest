# TODO: Fix SOCP Probability Caps Bug

## Overview

Fix the incorrect linear variance cap constraints in the iterative probability tightening loop. Change to proper SOC norm constraints on standard deviation to ensure effective capping of failing elements.

## Steps

1. **Edit \_build_or_update_prob_caps in start_combined (export4/OptiX.py)**:

   - Update rhs computation: Set s = max(0, delta / z); rhs = w_out _ s (cap on ||sigma ._ x||\_2).
   - This stores the correct std cap in prob_caps[ri][e].

2. **Edit socp_optimize method (export4/OptiX.py)**:

   - In the per-recipe loop, for each prob_cap: Replace linear sum constraint with SOC: constraints.append( cp.norm( cp.multiply( sigma_all[:, e], x ), 2 ) <= rhs ).
   - Remove the row = sigma_all[:, e] \*\* 2 line.

3. **Test the changes**:

   - Run the application: python export4/OptiX.py.
   - Load sample Lager/Styrplaner files.
   - Enable SOCP, set target_prob to 70%, run optimization.
   - Verify in Window3 that all recipes meet target % with fewer iterations (check console/logs for convergence).
   - If solver issues, suggest installing cvxpy solvers (e.g., pip install cvxpy[scs]).

4. **Cleanup**:
   - Update TODO.md to mark steps as completed.
   - If successful, attempt_completion with summary.
