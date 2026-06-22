# Random Forest Baselines — Results & Conclusions

Notebook: `11_random_forest.ipynb` | 5 folds, mean ± std | Fixed hyperparameters: `n_estimators=500, max_features='sqrt'`

**Feature selection method:** RNA and protein arms use the **top 1,000 highest-variance features**, selected independently per arm and per fold from **train-fold cell lines only** (leakage-safe — selection never sees val/test cell lines). Drug arms use 2048-bit Morgan fingerprints (radius=2). No drug-response-aware selection is used yet for protein (see caveat below).

---

## Results

| Arm | Split | Correlation | Spearman | RMSE | R2 | ROC-AUC |
|---|---|---|---|---|---|---|
| Drug | LCO | 0.790 ± 0.020 | 0.726 ± 0.018 | 1.652 ± 0.053 | 0.618 ± 0.026 | 0.858 ± 0.011 |
| Drug | LDO | 0.104 ± 0.155 | 0.094 ± 0.160 | 2.566 ± 0.380 | -0.028 ± 0.056 | 0.528 ± 0.086 |
| Drug | LPO | 0.788 ± 0.015 | 0.724 ± 0.009 | 1.660 ± 0.047 | 0.616 ± 0.022 | 0.854 ± 0.005 |
| Drug | LTO | 0.794 ± 0.011 | 0.738 ± 0.008 | 1.768 ± 0.131 | 0.570 ± 0.047 | 0.862 ± 0.004 |
| Protein | LCO | 0.232 ± 0.011 | 0.250 ± 0.022 | 2.616 ± 0.023 | 0.050 ± 0.007 | 0.618 ± 0.008 |
| Protein | LDO | 0.320 ± 0.042 | 0.340 ± 0.037 | 2.446 ± 0.393 | 0.066 ± 0.076 | 0.660 ± 0.023 |
| Protein | LPO | 0.306 ± 0.009 | 0.330 ± 0.010 | 2.558 ± 0.015 | 0.094 ± 0.005 | 0.656 ± 0.005 |
| Protein | LTO | 0.224 ± 0.045 | 0.232 ± 0.045 | 2.638 ± 0.036 | 0.044 ± 0.018 | 0.606 ± 0.021 |
| RNA | LCO | 0.224 ± 0.013 | 0.244 ± 0.015 | 2.622 ± 0.026 | 0.046 ± 0.009 | 0.618 ± 0.004 |
| RNA | LDO | 0.320 ± 0.042 | 0.340 ± 0.037 | 2.450 ± 0.396 | 0.066 ± 0.076 | 0.660 ± 0.023 |
| RNA | LPO | 0.306 ± 0.009 | 0.330 ± 0.010 | 2.558 ± 0.015 | 0.094 ± 0.005 | 0.654 ± 0.005 |
| RNA | LTO | 0.220 ± 0.047 | 0.226 ± 0.048 | 2.648 ± 0.041 | 0.038 ± 0.016 | 0.600 ± 0.023 |
| RNA+Drug | LCO | 0.838 ± 0.013 | 0.790 ± 0.014 | 1.474 ± 0.048 | 0.696 ± 0.021 | 0.890 ± 0.007 |
| RNA+Drug | LDO | 0.350 ± 0.077 | 0.356 ± 0.075 | 2.420 ± 0.392 | 0.088 ± 0.070 | 0.654 ± 0.047 |
| RNA+Drug | LPO | 0.860 ± 0.012 | 0.824 ± 0.009 | 1.376 ± 0.056 | 0.736 ± 0.022 | 0.904 ± 0.005 |
| RNA+Drug | LTO | 0.834 ± 0.023 | 0.790 ± 0.020 | 1.508 ± 0.050 | 0.686 ± 0.035 | 0.890 ± 0.014 |
| Protein+Drug | LCO | 0.838 ± 0.018 | 0.792 ± 0.015 | 1.464 ± 0.057 | 0.700 ± 0.025 | 0.890 ± 0.007 |
| Protein+Drug | LDO | 0.340 ± 0.074 | 0.346 ± 0.075 | 2.426 ± 0.394 | 0.082 ± 0.070 | 0.654 ± 0.047 |
| Protein+Drug | LPO | 0.858 ± 0.015 | 0.824 ± 0.009 | 1.376 ± 0.056 | 0.738 ± 0.022 | 0.904 ± 0.005 |
| Protein+Drug | LTO | 0.836 ± 0.026 | 0.794 ± 0.024 | 1.492 ± 0.060 | 0.692 ± 0.037 | 0.890 ± 0.014 |
| RNA+Protein+Drug | LCO | 0.838 ± 0.013 | 0.792 ± 0.015 | 1.468 ± 0.049 | 0.702 ± 0.023 | 0.890 ± 0.007 |
| RNA+Protein+Drug | LDO | 0.336 ± 0.070 | 0.342 ± 0.073 | 2.428 ± 0.394 | 0.076 ± 0.067 | 0.652 ± 0.043 |
| RNA+Protein+Drug | LPO | 0.862 ± 0.011 | 0.826 ± 0.005 | 1.372 ± 0.052 | 0.738 ± 0.022 | 0.904 ± 0.005 |
| RNA+Protein+Drug | LTO | 0.836 ± 0.026 | 0.796 ± 0.025 | 1.500 ± 0.058 | 0.690 ± 0.039 | 0.890 ± 0.014 |

---

## Conclusions

- **RF is currently the strongest baseline in the project by a clear margin.** Combined arms (RNA+Drug, Protein+Drug) reach LCO r≈0.838, well above the best DL single-modality result so far (drug-FP MLP, r=0.73) and the naive `NaiveTissueDrugMeanPredictor` under the new splits (LCO r=0.762). This is the real bar the fusion model needs to clear, not the naive baselines or single-modality DL numbers.

- **Adding omics to drug fingerprint genuinely helps, on both axes that matter.** RNA+Drug and Protein+Drug both beat Drug-only on LCO (0.838 vs 0.790) and clear it more comfortably on LTO (0.834–0.836 vs 0.794). They also partially recover LDO performance that Drug-only catastrophically loses (0.340–0.350 vs 0.104) — omics context gives the model something to fall back on for unseen drugs, which fingerprint-only cannot. This is the first result in the project showing the kind of complementary value multimodal fusion is supposed to deliver — encouraging, but see the caveat below before reading too much into *which* omics layer is responsible.

- **RNA+Drug and Protein+Drug are statistically indistinguishable from each other** (LCO: 0.838 vs 0.838; LPO: 0.860 vs 0.858; LTO: 0.834 vs 0.836; LDO: 0.350 vs 0.340 — all well within one std of each other). Combined with the earlier finding that RNA-only and protein-only predictions correlate at r=0.996 with each other, this confirms the **top-1,000-variance feature selection is not capturing modality-specific signal for either arm** — both omics layers are most likely converging on the same tissue-of-origin proxy, not on independent RNA- or protein-specific biology. The model cannot currently tell you whether protein contributes anything beyond RNA, because both arms are functionally interchangeable under this selection method.

- **Drug-only repeats the same per-drug-mean pattern seen in every model so far** (DL and naive alike): strong when the drug has been seen during training (LCO/LPO/LTO ≈ 0.79), collapses when it hasn't (LDO = 0.104, barely above chance, R² negative). RF's drug-only LCO (0.790) is meaningfully stronger than the MLP's drug-FP arm (0.73) — RF is simply a stronger fingerprint-only model, not evidence of anything biological.

- **Variance and ROC-AUC track correlation closely across all arms**, with no major outliers — no sign of an additional bug beyond the known selection confound (RMSE, R², and ROC-AUC all move in the expected direction alongside Correlation/Spearman within each row).

- **RNA+Protein+Drug (all three modalities combined) shows essentially no improvement over either two-way combination** (LCO: 0.838, identical to both RNA+Drug and Protein+Drug; LPO: 0.862, only marginally above 0.860/0.858; LTO: 0.836, identical; LDO: 0.336, actually slightly *below* RNA+Drug's 0.350, well within noise). Adding the second omics layer on top of the first contributes nothing measurable — exactly what you'd expect given RNA and protein are already converging on the same signal individually. This is further confirmation (not new evidence, but a consistent replication) that the current selection method gives the model two redundant copies of the same information rather than two complementary ones. A working fusion model should show RNA+Protein+Drug clearly beating both two-way arms — this flat result is the cleanest illustration yet of why the protein selection fix is a blocker, not a nice-to-have.

- **Action required before the fusion model:** protein feature selection must change from top-variance to an RNA-divergence-aware method (e.g. partial correlation controlling for the gene's own RNA expression, or residual variance after regressing protein on RNA) before RNA+Drug vs Protein+Drug vs RNA+Protein+Drug — or the eventual cross-attention fusion model — can be trusted as a genuine test of multimodal complementarity. Until then, treat all protein-involving numbers in this table as provisional.
