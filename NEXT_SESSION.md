# Next Session
 
## Primary task: fix protein feature selection
 
The current top-variance feature selection collapses RNA-only and protein-only models onto the same signal (confirmed: r=0.996 between their predictions on identical test data) — almost certainly tissue-of-origin, since both omics layers have tissue as their dominant variance driver. This needs to be fixed before any further protein-involving work, including the fusion model.
 
**Plan to confirm before implementing (per usual workflow):**
 
1. Implement a new protein selection function — candidates, in order of preference:
   - **Partial correlation**: for each protein, correlate protein → IC50 controlling for that gene's own RNA expression (regress out RNA, keep proteins whose residual still predicts IC50)
   - **Residual variance**: regress each protein on its RNA counterpart, rank proteins by variance of the *residual* (the part RNA doesn't explain), select top-K from that ranking
   - Both should be computed from train-fold cell lines only, same leakage discipline as the current `select_top_variance_cols`
2. Keep RNA selection as top-variance (no change needed — RNA has no complementarity requirement)
3. Re-run protein-only RF (notebook 11) with the new selection, compare against the current tissue-confounded result
4. Re-check the RNA-pred vs protein-pred correlation with the new selection — should drop substantially if the fix works
5. Once confirmed, propagate the fix to:
   - Protein+Drug RF arm (notebook 11) — currently provisional
   - Protein-only / Protein+Drug DL baselines (notebook 09) if not already affected the same way (untested — worth checking MLP protein arm too, same risk applies)
## Secondary / optional
 
- Decide whether to add the chained-fallback `NaiveTissueDrugMeanPredictor` variant to notebook 10 under the new splits, for a stronger naive comparison point (old chained version under old splits is not comparable)
## Do not revisit unless asked
- RNA selection method (top-variance is fine, no complementarity requirement)
- Split structure (`splits.json`, one shared train + 4 test sets) — finalized
- RF hyperparameters (fixed defaults: `n_estimators=500, max_features='sqrt'`)
- `evaluateMT()` metric set and NaN-handling — finalized this session, working correctly
 