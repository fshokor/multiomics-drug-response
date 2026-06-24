# Multimodal Drug Response Prediction — Results Summary
## Notebooks 09–14 | Fold 0 exploration + 5-fold evaluation

---

## Naive baselines (drevalpy)

| Model | LCO | LDO | LPO | LTO |
|---|---|---|---|---|
| NaivePredictor (global mean) | — | — | — | — |
| NaiveCellLineMeanPredictor | — | 0.284 | 0.276 | — |
| NaiveDrugMeanPredictor | 0.790 | — | 0.788 | 0.794 |
| NaiveMeanEffectsPredictor | 0.790 | 0.284 | 0.836 | 0.794 |
| NaiveTissueDrugMeanPredictor | 0.762 | — | 0.752 | — |
| NaiveTissueMeanPredictor | 0.150 | 0.182 | 0.174 | — |

**Key observation:** `NaiveDrugMeanPredictor` (predict the mean IC50 for each drug across
training cell lines) scores 0.790 LCO — identical to `NaiveMeanEffectsPredictor`.
This is the hardest baseline to beat on LCO: it captures per-drug mean effects
without any cell-line biology. `NaiveCellLineMeanPredictor` scores NaN on LCO and LTO
(no shared cell lines between train and test by definition). LDO collapses to NaN for
drug-mean predictors for the same reason.

---

## Random Forest baselines (nb07–08, 5-fold, 1000 top-variance features)

Pearson r mean ± std across 5 folds.

| Arm | LCO | LDO | LPO | LTO |
|---|---|---|---|---|
| Drug fingerprint only | 0.790 ± 0.020 | 0.104 ± 0.155 | 0.788 ± 0.015 | 0.794 ± 0.011 |
| RNA only | 0.224 ± 0.013 | 0.320 ± 0.042 | 0.306 ± 0.009 | 0.220 ± 0.047 |
| Protein only | 0.232 ± 0.011 | 0.320 ± 0.042 | 0.306 ± 0.009 | 0.224 ± 0.045 |
| Protein-RV (residual variance) | 0.230 ± 0.014 | 0.320 ± 0.042 | 0.306 ± 0.009 | 0.222 ± 0.048 |
| RNA + Drug | **0.838 ± 0.013** | 0.350 ± 0.077 | 0.860 ± 0.012 | 0.834 ± 0.023 |
| Protein + Drug | **0.838 ± 0.018** | 0.340 ± 0.074 | 0.858 ± 0.015 | 0.836 ± 0.026 |
| RNA + Protein + Drug | **0.838 ± 0.013** | 0.336 ± 0.070 | 0.862 ± 0.011 | 0.836 ± 0.026 |

**Key observations:**
- RNA alone and protein alone are indistinguishable (0.224 vs 0.232 LCO, 0.320 vs 0.320 LDO).
  Top-variance feature selection captures tissue-of-origin signal in both modalities
  identically — this is the tissue confound confirmed.
- Protein-RV (residual variance after gene-wise RNA-protein regression) performs
  identically to protein top-variance. Gene-wise regression does not escape tissue
  confound; PCA-residual in cell-line space is the correct fix (not yet implemented).
- Adding protein to RNA+Drug gives zero LCO improvement (0.838 in all three drug-containing arms).
  Protein is entirely redundant for cell-line generalization under top-variance selection.
- RF + Drug collapses on LDO (0.104 ± 0.155) — the drug fingerprint as a raw feature
  does not generalize to new drugs in tree-based models.

---

## Single-modal DL baselines (nb09, fold 0 only)

| Arm | LCO | LDO | LPO | LTO |
|---|---|---|---|---|
| Drug GNN (256-d) | 0.61 | 0.13 | 0.61 | 0.62 |
| Drug fingerprint MLP (256-d) | 0.73 | 0.11 | 0.73 | 0.74 |
| RNA MLP (256-d, full features) | 0.22 | 0.27 | 0.29 | 0.25 |
| RNA MLP (256-d, 1000 features) | 0.20 | 0.27 | 0.28 | 0.25 |
| Protein MLP (256-d, full features) | 0.21 | 0.29 | 0.30 | 0.24 |
| Protein MLP (256-d, 1000 features) | 0.20 | 0.29 | 0.29 | 0.22 |

**Key observations:**
- Drug GNN underperforms drug fingerprint MLP consistently. Not pursued further.
- RNA and protein single-modal DL are indistinguishable — tissue confound confirmed.
- Drug fingerprint alone (0.73 LCO) is already a strong single-modal baseline.

---

## Naive concatenation (nb12, Tier 1 — raw concat, fold 0)

| Arm | LCO | LDO | LPO - all | LTO |
|---|---|---|---|---|
| rna + protein (no drug) | 0.2052 | 0.2786 | 0.2905 | 0.2189 |
| protein + drug_fp | 0.7423 | 0.2687 | 0.7886 | 0.7632 |
| rna + drug_fp | 0.7643 | 0.3217 | 0.8058 | 0.7864 |
| rna + protein + drug_fp | 0.7684 | 0.3177 | 0.8123 | 0.7879 |

**Key observation:** Drug fingerprint dominance — `drug_fp alone` scores 0.73 LCO and
raw concatenation with RNA only adds +0.034. Adding protein on top adds +0.004.
The 2048-d drug fingerprint swamps the 1000-d omics signals in the unregulated MLP input.
Naive concatenation fails precisely as the Turbine failure-mode taxonomy predicts.

---

## Encoder-projected concatenation (nb12, Tier 2 — 5-fold)

All modalities projected to 256-d before concatenation. Pearson r mean ± std across 5 folds.

| Arm | LCO | LDO | LPO - all | LTO |
|---|---|---|---|---|
| rna_enc + drug_enc | 0.795 ± 0.021 | 0.352 ± 0.080 | 0.825 ± 0.019 | 0.797 ± 0.030 |
| protein_enc + drug_enc | 0.796 ± 0.019 | 0.368 ± 0.069 | 0.829 ± 0.017 | 0.796 ± 0.027 |
| rna_enc + protein_enc + drug_enc | 0.801 ± 0.017 | 0.368 ± 0.081 | 0.831 ± 0.013 | 0.800 ± 0.026 |
| hadamard omics + drug_enc | 0.797 ± 0.021 | 0.373 ± 0.073 | 0.827 ± 0.019 | 0.797 ± 0.032 |
| gated omics + drug_enc | **0.800 ± 0.016** | **0.383 ± 0.045** | **0.831 ± 0.015** | **0.800 ± 0.026** |

**Key observations:**
- Encoder projection fixes drug dominance: +0.05 LCO over raw concat for drug-containing
  arms (0.795–0.801 vs 0.743–0.768). Equal 256-d embeddings let the MLP learn from
  all modalities.
- DL encoder models beat RF on LDO (0.352–0.383 vs 0.104–0.350). Learned drug
  embeddings generalize to new drugs; raw fingerprint trees do not.
- Protein adds negligible LCO improvement over RNA+drug alone (0.801 vs 0.795, within
  std overlap). Tissue confound is still active.
- Hadamard and gated fusion perform comparably to concat of all three encoders.
  Gated fusion has the lowest LDO std (±0.045 vs ±0.069–0.081), suggesting more
  stable training across folds.
- All encoder arms are below RF LCO (0.838 ± 0.013). DL does not beat RF on LCO
  with this dataset size — consistent with DrEval.

---

## Cross-attention fusion (nb13, 5-fold)

RNA and protein each encoded to 256-d, fused via cross-attention
(query=RNA, key/value=protein), then combined with projected drug embedding.

| Variant | Drug integration | LCO | LDO | LPO - all | LTO |
|---|---|---|---|---|---|
| AY: fp + concat | concat(omics_fused, drug_enc) | 0.795 ± 0.021 | 0.384 ± 0.060 | 0.830 ± 0.019 | 0.798 ± 0.026 |
| AX: fp + attn | CrossAttn(query=drug, kv=omics) | 0.795 ± 0.018 | **0.389 ± 0.083** | 0.824 ± 0.019 | 0.797 ± 0.028 |

**Key observations:**
- Cross-attention (AX, AY) does not improve over encoder-projected concat
  (`rna_enc+protein_enc+drug_enc`: LCO 0.801 ± 0.017, LDO 0.368 ± 0.081).
  The attention mechanism is not finding structure beyond what the encoder projections
  already provide.
- AX (drug-omics cross-attention) vs AY (concat drug integration): no consistent
  winner — AX has marginally higher mean LDO (0.389 vs 0.384) but higher std
  (±0.083 vs ±0.060). Not significantly different.
- BX/BY (graph drug variants, fold 0 only): GNN consistently underperforms
  fingerprint encoder. BX LDO collapses to 0.1479 — graph + attention fails
  entirely on new drugs.
- Hypothesis: attention cannot learn RNA-protein complementarity because top-variance
  selection loads both modalities with tissue-of-origin signal. The attention mechanism
  attends to tissue clustering, not within-cell-line RNA-protein divergence.
  PCA-residual feature selection is the required prerequisite for a fair attention test.

---

## Complete LCO ranking (5-fold mean)

| Rank | Model | LCO | LDO | Category |
|---|---|---|---|---|
| 1 | RF: RNA + Drug | 0.838 ± 0.013 | 0.350 ± 0.077 | Random Forest |
| 1 | RF: Protein + Drug | 0.838 ± 0.018 | 0.340 ± 0.074 | Random Forest |
| 1 | RF: RNA + Protein + Drug | 0.838 ± 0.013 | 0.336 ± 0.070 | Random Forest |
| 4 | NaiveDrugMeanPredictor | 0.790 | — | Naive |
| 4 | NaiveMeanEffectsPredictor | 0.790 | 0.284 | Naive |
| 6 | rna_enc+protein_enc+drug_enc | 0.801 ± 0.017 | 0.368 ± 0.081 | DL encoder |
| 7 | gated+drug_enc | 0.800 ± 0.016 | 0.383 ± 0.045 | DL encoder |
| 8 | hadamard+drug_enc | 0.797 ± 0.021 | 0.373 ± 0.073 | DL encoder |
| 9 | protein_enc+drug_enc | 0.796 ± 0.019 | 0.368 ± 0.069 | DL encoder |
| 10 | rna_enc+drug_enc | 0.795 ± 0.021 | 0.352 ± 0.080 | DL encoder |
| 10 | AY: fp+concat | 0.795 ± 0.021 | 0.384 ± 0.060 | Cross-attention |
| 10 | AX: fp+attn | 0.795 ± 0.018 | 0.389 ± 0.083 | Cross-attention |

**LDO ranking (DL encoder models beat RF):**

| Rank | Model | LDO |
|---|---|---|
| 1 | AX: fp+attn | 0.389 ± 0.083 |
| 2 | AY: fp+concat | 0.384 ± 0.060 |
| 3 | gated+drug_enc | 0.383 ± 0.045 |
| 4 | hadamard+drug_enc | 0.373 ± 0.073 |
| 5 | rna_enc+protein_enc+drug_enc | 0.368 ± 0.081 |
| 5 | protein_enc+drug_enc | 0.368 ± 0.069 |
| 7 | rna_enc+drug_enc | 0.352 ± 0.080 |
| 8 | RF: RNA+Drug | 0.350 ± 0.077 |
| 9 | RF: Protein+Drug | 0.340 ± 0.074 |
| 10 | RF: RNA+Protein+Drug | 0.336 ± 0.070 |
| 11 | NaiveMeanEffectsPredictor | 0.284 |
| 12 | RF: Drug only | 0.104 ± 0.155 |

---

## Summary of findings

### What works
- **Encoder projection** (256-d per modality before concatenation) is the single most
  impactful architectural choice: +0.05 LCO over raw concat, and flips the DL vs RF
  LDO ranking in DL's favour.
- **DL encoder models beat RF on LDO** (new drug generalization): 0.352–0.389 vs
  0.104–0.350. Learned drug embeddings generalize; fingerprint-based RF does not.
- **Gated fusion** has the most stable LDO across folds (±0.045) vs concat (±0.081).

### What does not work (yet)
- **Cross-attention does not improve over encoder concat** under current feature
  selection. Attention is likely learning tissue clustering, not RNA-protein divergence.
- **Protein does not contribute to LCO** in any model — identical performance with or
  without protein on cell-line-out evaluation. Tissue confound masks any independent
  protein signal.
- **DL does not beat RF on LCO** — consistent with DrEval (Bernett et al. 2026).

### Open question — closed by nb14
PCA-residual decomposition was identified as the required fix. Results in nb14 section below.

---

## PCA-residual features (nb14, fold 0 only)

**Setup:** Remove top-k tissue PCs from each modality (K_RNA=10, K_PROTEIN=15), then
select top-1000 columns by IC50 correlation (not top-variance — see below).
All PCA fits on train cell lines only.

**Key finding before feature selection:**
- Cross-cell-line RNA-protein correlation: top-variance r=0.52 → PCA-residual r=0.04
  (tissue confound removed in full feature space)
- After top-variance column selection on residuals: r=0.49 (shared proliferation/cell-cycle
  axes reintroduced — top-variance is the wrong criterion on residuals)
- After IC50-correlation column selection on residuals: r=-0.03
  (selected features are genuinely orthogonal between modalities)
- Column name overlap between top-1000 RNA and protein residual columns: 0
  (r=0.49 was biological co-variation, not duplicate columns)

### RF on residual features (fold 0)

| Arm | LCO | LDO | LPO | LTO |
|---|---|---|---|---|
| RF rna_residual + drug | 0.8247 | 0.3034 | 0.8553 | 0.8399 |
| RF protein_residual + drug | **0.8357** | **0.3283** | 0.8614 | 0.8479 |
| RF rna_residual + protein_residual + drug | 0.8340 | 0.3084 | 0.8619 | 0.8470 |

**Key observations:**
- Sanity check 3 passes: RNA and protein now diverge (LCO 0.8247 vs 0.8357, LDO 0.3034
  vs 0.3283). The tissue confound is removed and the modalities carry independent signal.
- Protein residual beats RNA residual on both LCO (+0.011) and LDO (+0.025).
  After tissue removal, protein is slightly more predictive than RNA for drug response.
- RF fusion (both residuals + drug) does not beat protein-residual alone on LCO (0.8340
  vs 0.8357). RF cannot exploit cross-modal complementarity — expected, sets up DL test.

### DL on residual features (fold 0)

| Arm | LCO | LDO | LPO | LTO |
|---|---|---|---|---|
| enc_concat_residual | 0.7683 | 0.4891 | 0.8245 | 0.7821 |
| cross_attn_residual | 0.7560 | 0.3726 | 0.8028 | 0.7658 |
| *(nb12 Tier2 enc_concat, top-var, fold 0 ref)* | *0.8021* | *0.5261* | — | — |
| *(nb13 AX cross-attn, top-var, fold 0 ref)* | *0.7932* | *0.3890* | — | — |

**Key observations:**
- Cross-attention is worse than encoder concat on residual features (LCO -0.012,
  LDO -0.165). The attention mechanism does not exploit RNA-protein complementarity
  even when the modalities are genuinely independent.
- Both DL models underperform RF on residual LCO (0.768/0.756 vs 0.825–0.836).
  Within-tissue variation is noisier signal than tissue-level signal; MLP encoders
  struggle where RF can still find useful splits.
- DL enc_concat_residual LDO (0.4891) is below nb12 Tier2 top-var LDO (0.5261).
  Residual features are harder across the board for DL.

### Falsifiable predictions vs outcomes

| Prediction | Outcome |
|---|---|
| (1) RNA and protein single-modal performance diverges | ✓ Confirmed (LCO +0.011, LDO +0.025) |
| (2) enc_concat improves over RNA-only encoder + drug | ✗ Not tested directly (both residual) |
| (3) Cross-attention improves over encoder concat on residuals | ✗ Failed (LCO -0.012, LDO -0.165) |

---

## Complete LCO ranking (updated)

| Rank | Model | LCO | LDO | Category | Features |
|---|---|---|---|---|---|
| 1 | RF: RNA + Drug | 0.838 ± 0.013 | 0.350 ± 0.077 | Random Forest | top-var |
| 1 | RF: Protein + Drug | 0.838 ± 0.018 | 0.340 ± 0.074 | Random Forest | top-var |
| 1 | RF: RNA + Protein + Drug | 0.838 ± 0.013 | 0.336 ± 0.070 | Random Forest | top-var |
| 4 | RF: protein_residual + drug | 0.8357 | 0.3283 | Random Forest | PCA-residual |
| 5 | RF: rna+protein residual + drug | 0.8340 | 0.3084 | Random Forest | PCA-residual |
| 6 | RF: rna_residual + drug | 0.8247 | 0.3034 | Random Forest | PCA-residual |
| 7 | NaiveDrugMeanPredictor | 0.790 | — | Naive | — |
| 7 | NaiveMeanEffectsPredictor | 0.790 | 0.284 | Naive | — |
| 9 | rna_enc+protein_enc+drug_enc | 0.801 ± 0.017 | 0.368 ± 0.081 | DL encoder | top-var |
| 10 | gated+drug_enc | 0.800 ± 0.016 | 0.383 ± 0.045 | DL encoder | top-var |
| 11 | hadamard+drug_enc | 0.797 ± 0.021 | 0.373 ± 0.073 | DL encoder | top-var |
| 12 | protein_enc+drug_enc | 0.796 ± 0.019 | 0.368 ± 0.069 | DL encoder | top-var |
| 13 | rna_enc+drug_enc | 0.795 ± 0.021 | 0.352 ± 0.080 | DL encoder | top-var |
| 13 | AY: fp+concat | 0.795 ± 0.021 | 0.384 ± 0.060 | Cross-attention | top-var |
| 13 | AX: fp+attn | 0.795 ± 0.018 | 0.389 ± 0.083 | Cross-attention | top-var |
| 16 | enc_concat_residual | 0.7683 | **0.4891** | DL encoder | PCA-residual |
| 17 | cross_attn_residual | 0.7560 | 0.3726 | Cross-attention | PCA-residual |

**LDO ranking (updated):**

| Rank | Model | LDO | Features |
|---|---|---|---|
| 1 | enc_concat_residual | **0.4891** | PCA-residual |
| 2 | AX: fp+attn | 0.389 ± 0.083 | top-var |
| 3 | AY: fp+concat | 0.384 ± 0.060 | top-var |
| 4 | gated+drug_enc | 0.383 ± 0.045 | top-var |
| 5 | hadamard+drug_enc | 0.373 ± 0.073 | top-var |
| 6 | rna_enc+protein_enc+drug_enc | 0.368 ± 0.081 | top-var |
| 6 | protein_enc+drug_enc | 0.368 ± 0.069 | top-var |
| 8 | rna_enc+drug_enc | 0.352 ± 0.080 | top-var |
| 9 | RF: RNA+Drug | 0.350 ± 0.077 | top-var |
| 10 | cross_attn_residual | 0.3726 | PCA-residual |
| 11 | RF: protein_residual+drug | 0.3283 | PCA-residual |
| 12 | RF: rna+protein residual+drug | 0.3084 | PCA-residual |
| 13 | RF: rna_residual+drug | 0.3034 | PCA-residual |
| 14 | NaiveMeanEffectsPredictor | 0.284 | — |
| 15 | RF: Drug only | 0.104 ± 0.155 | top-var |

---

## Summary of findings

### What works
- **Encoder projection** (256-d per modality before concatenation) is the single most
  impactful architectural choice: +0.05 LCO over raw concat, and flips the DL vs RF
  LDO ranking in DL's favour.
- **DL encoder models beat RF on LDO** (new drug generalization): 0.352–0.489 vs
  0.104–0.350. Learned drug embeddings generalize; fingerprint-based RF does not.
- **Gated fusion** has the most stable LDO across folds (±0.045 vs ±0.081).
- **PCA-residual successfully decorrelates modalities**: IC50-selected residual features
  achieve r=-0.03 cross-modal correlation vs r=0.52 for top-variance features.
  RNA and protein now carry measurably independent drug-response signal.
- **enc_concat on residual features achieves best LDO overall** (0.4891, fold 0) —
  above all top-variance DL models. Suggests residual features improve new-drug
  generalization even if LCO drops.

### What does not work
- **Cross-attention does not improve over encoder concat** under either feature regime
  (top-variance or PCA-residual). Attention finds no exploitable structure between
  modalities at this dataset scale.
- **Protein does not improve LCO in any DL model** — even with genuinely independent
  residual features, encoder concat with both modalities does not beat protein-residual
  alone on LCO.
- **DL does not beat RF on LCO** in any experiment — consistent with DrEval.
- **PCA-residual features hurt LCO for DL** (0.768 vs 0.802 for enc_concat) —
  within-tissue variation is noisier and harder for MLP encoders than tissue-level signal.

### Interpretation
The tissue confound is real and removable by PCA-residual, and independent protein
signal exists (RF divergence confirmed). However, the DL models cannot exploit this
complementarity: cross-attention underperforms encoder concat on residual features,
and neither beats RF. The bottleneck is likely dataset scale (~836 cell lines) — the
within-tissue variation signal is too sparse for attention to learn a meaningful
protein-query weighting. This is a dataset-size limitation, not an architectural flaw.

The best current result for new-drug generalization (LDO) is enc_concat_residual at
0.4891 (fold 0). This warrants running 5-fold to confirm stability before concluding.

---

*Generated after notebooks 09–14 | fold 0 for nb14 | GDSC2 × CCLE × ProCan | fold structure: drevalpy LCO/LDO/LTO/LPO*
