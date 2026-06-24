# Multimodal Drug Response Prediction — Results Summary
## Notebooks 09–13 | Fold 0 exploration + 5-fold evaluation

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

### Open question
PCA-residual decomposition in cell-line space — remove tissue principal components from
both RNA and protein before feature selection — is the required next experiment.
If tissue signal is the dominant confound, residual features should show:
1. RNA and protein single-modal performance drops (tissue signal removed).
2. RNA-protein cross-attention finds genuinely complementary signal.
3. Protein contributes positively to LCO for the first time.

This is the experiment that either confirms or closes the multimodal hypothesis.

---

*Generated after notebooks 09–13 | 5-fold CV | GDSC2 × CCLE × ProCan | fold structure: drevalpy LCO/LDO/LTO/LPO*
