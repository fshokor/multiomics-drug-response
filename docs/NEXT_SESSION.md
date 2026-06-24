# Next Session

## Goal
PCA-residual decomposition in cell-line space — remove tissue confound from RNA and
protein before feature selection, then re-run the cross-attention model to test whether
protein contributes genuinely independent signal.

## Context
The central blocker identified across nb07–13: top-variance feature selection loads
both RNA and protein with tissue-of-origin signal, making the two modalities
indistinguishable as standalone predictors (RNA LCO ~0.22, protein LCO ~0.22) and
preventing the attention mechanism from learning RNA-protein complementarity.

Current best results (5-fold):
- RF RNA+Drug: LCO 0.838 ± 0.013  (LCO ceiling, beats all DL)
- rna_enc+protein_enc+drug_enc: LCO 0.801 ± 0.017, LDO 0.368 ± 0.081
- gated+drug_enc: LCO 0.800 ± 0.016, LDO 0.383 ± 0.045  (most stable LDO)
- AX fp+attn: LCO 0.795 ± 0.018, LDO 0.389 ± 0.083  (best mean LDO)

Cross-attention does not improve over encoder concat under current features.
Protein does not contribute to LCO in any model.

## What to do

### Step 1 — PCA-residual feature extraction (new notebook: 14_pca_residual.ipynb)

Unit of analysis: cell-line space (rows = cell lines, columns = genes/proteins).
NOT gene-wise regression across cell lines (already tried, doesn't work).

For each omics modality independently:
1. Fit PCA on train cell lines only (fold-safe).
2. Choose n_components to remove: either fixed (e.g. top 20 PCs capturing tissue
   variance) or by explained variance threshold (e.g. remove PCs until cumulative
   variance < 50% — to be decided).
3. Project train cell lines into PCA space, compute residuals
   (original - reconstruction from top PCs).
4. Apply same PCA transform + residual to val and test cell lines.
5. Use residual matrix as the feature input instead of raw features.

Key decision to confirm at session start: how many PCs to remove.
Options:
  a) Fixed k (e.g. k=20) — simple, interpretable
  b) Scree plot / elbow — inspect variance explained, pick k visually
  c) Tissue label regression — remove PCs that predict tissue type above chance
     (most principled, slightly more complex)
Recommend: start with (b), generate scree plot for RNA and protein, decide k together
before writing the training loop.

### Step 2 — Sanity checks on residual features

After computing residuals, verify:
- RNA and protein single-modal RF performance drops vs top-variance baseline
  (tissue signal removed → lower performance expected).
- RNA and protein residuals are no longer correlated at r=0.996 across cell lines
  (this was the confound diagnostic from earlier).
- Residual features still carry drug-response signal (RF RNA-residual + drug > naive).

If sanity checks fail (residuals carry no signal), the tissue confound is deeper than
PCA can address and a different approach is needed.

### Step 3 — Re-run key models on residual features

If sanity checks pass, re-run on fold 0 first:
1. RF: RNA-residual + Drug, Protein-residual + Drug, both + Drug
2. rna_enc+protein_enc+drug_enc (encoder concat)
3. AX: fp+attn (cross-attention)

Compare to current results. Three falsifiable predictions:
1. RNA and protein single-modal performance diverges (they no longer carry same signal).
2. rna_enc+protein_enc+drug_enc LCO improves over RNA-only encoder + drug.
3. Cross-attention (AX) improves over encoder concat (AY) — attention finds
   complementary structure that concat cannot exploit.

If all three hold: protein contributes genuinely independent signal, multimodal
hypothesis confirmed, pitch narrative is complete.
If (1) holds but (2)/(3) don't: residuals carry independent signal but the model
cannot exploit it — architecture or optimization issue.
If (1) fails: tissue confound is not removable by linear PCA, need nonlinear approach.

## Files to read at session start
- SESSION_MEMORY.md (current state)
- RESULTS_SUMMARY.md (full results nb07–13)
- nb14 does not exist yet — create fresh

## Do not re-run
- nb09–13 single-fold results (done, documented in RESULTS_SUMMARY.md)
- Multi-fold results for arms that are not in the Step 3 list above
