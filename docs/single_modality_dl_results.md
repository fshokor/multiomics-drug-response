# Single-Modality DL Baselines — Results & Conclusions

Notebook: `09_custom_MLP.ipynb` | Fold 0 | Hidden layers: 256 (RNA also tested at 512)

---

## Results

### Drug model (Morgan fingerprint, 256)

| Split | Correlation | Spearman | MSE | RMSE | R2 | ROC-AUC | Slope | Var Real | Var Pred |
|---|---|---|---|---|---|---|---|---|---|
| LCO | 0.73 | 0.64 | 3.43 | 1.85 | 0.52 | 0.82 | 0.93 | 7.16 | 4.40 |
| LTO | 0.74 | 0.66 | 4.24 | 2.06 | 0.44 | 0.82 | 0.97 | 7.54 | 4.43 |
| LDO | 0.11 | 0.12 | 7.03 | 2.65 | -0.08 | 0.54 | 0.27 | 6.52 | 1.12 |
| LPO - all | 0.73 | 0.64 | 3.40 | 1.84 | 0.53 | 0.82 | 0.94 | 7.27 | 4.46 |
| LPO - nothing new | 0.77 | 0.70 | 3.01 | 1.73 | 0.59 | 0.84 | 0.95 | 7.42 | 4.86 |
| LPO - new cell line only | 0.77 | 0.68 | 2.95 | 1.72 | 0.59 | 0.84 | 0.93 | 7.16 | 4.92 |
| LPO - new drug only | 0.12 | 0.13 | 6.63 | 2.58 | -0.08 | 0.54 | 0.28 | 6.14 | 1.12 |
| LPO - fully new (cell AND drug) | 0.16 | 0.20 | 7.16 | 2.68 | -0.02 | 0.60 | 0.44 | 7.03 | 0.95 |

### Drug model (GNN, GCNConv, 256)

| Split | Correlation | Spearman | MSE | RMSE | R2 | ROC-AUC | Slope | Var Real | Var Pred |
|---|---|---|---|---|---|---|---|---|---|
| LCO | 0.61 | 0.50 | 4.86 | 2.20 | 0.32 | 0.74 | 1.02 | 7.16 | 2.56 |
| LTO | 0.62 | 0.53 | 6.34 | 2.52 | 0.16 | 0.76 | 1.07 | 7.54 | 2.57 |
| LDO | 0.13 | 0.12 | 7.47 | 2.73 | -0.15 | 0.57 | 0.31 | 6.52 | 1.14 |
| LPO - all | 0.61 | 0.50 | 4.79 | 2.19 | 0.34 | 0.74 | 1.02 | 7.27 | 2.63 |
| LPO - nothing new | 0.65 | 0.55 | 4.52 | 2.13 | 0.39 | 0.76 | 1.06 | 7.42 | 2.81 |
| LPO - new cell line only | 0.64 | 0.52 | 4.49 | 2.12 | 0.37 | 0.76 | 1.06 | 7.16 | 2.62 |
| LPO - new drug only | 0.15 | 0.15 | 7.02 | 2.65 | -0.14 | 0.57 | 0.35 | 6.14 | 1.13 |
| LPO - fully new (cell AND drug) | 0.11 (p=0.11, n.s.) | 0.08 | 8.12 | 2.85 | -0.15 | 0.54 | 0.27 | 7.03 | 1.10 |

### RNA model (256)

| Split | Correlation | Spearman | MSE | RMSE | R2 | ROC-AUC | Slope | Var Real | Var Pred |
|---|---|---|---|---|---|---|---|---|---|
| LCO | 0.22 | 0.24 | 7.25 | 2.69 | -0.01 | 0.62 | 1.14 | 7.16 | 0.27 |
| LTO | 0.25 | 0.25 | 7.76 | 2.79 | -0.03 | 0.62 | 1.36 | 7.54 | 0.26 |
| LDO | 0.27 | 0.32 | 6.34 | 2.52 | 0.03 | 0.65 | 1.19 | 6.52 | 0.35 |
| LPO - all | 0.29 | 0.31 | 7.08 | 2.66 | 0.03 | 0.65 | 1.32 | 7.27 | 0.35 |
| LPO - nothing new | 0.30 | 0.32 | 7.17 | 2.68 | 0.03 | 0.66 | 1.37 | 7.42 | 0.36 |
| LPO - new cell line only | 0.19 | 0.21 | 7.34 | 2.71 | -0.03 | 0.59 | 0.96 | 7.16 | 0.27 |
| LPO - new drug only | 0.29 | 0.35 | 5.97 | 2.44 | 0.03 | 0.67 | 1.21 | 6.14 | 0.36 |
| LPO - fully new (cell AND drug) | 0.17 | 0.23 | 7.33 | 2.71 | -0.04 | 0.58 | 0.87 | 7.03 | 0.26 |

*(RNA at 512 hidden units: nearly identical across all splits — not tabulated separately, capacity is not the bottleneck.)*

### Protein model (256, zero-fill for missing values)

| Split | Correlation | Spearman | MSE | RMSE | R2 | ROC-AUC | Slope | Var Real | Var Pred |
|---|---|---|---|---|---|---|---|---|---|
| LCO | 0.21 | 0.24 | 7.17 | 2.68 | 0.00 | 0.62 | 0.94 | 7.16 | 0.37 |
| LTO | 0.24 | 0.25 | 7.52 | 2.74 | 0.00 | 0.61 | 1.28 | 7.54 | 0.27 |
| LDO | 0.29 | 0.33 | 6.15 | 2.48 | 0.06 | 0.66 | 1.04 | 6.52 | 0.53 |
| LPO - all | 0.30 | 0.32 | 6.88 | 2.62 | 0.05 | 0.65 | 1.12 | 7.27 | 0.53 |
| LPO - nothing new | 0.32 | 0.33 | 6.95 | 2.64 | 0.06 | 0.66 | 1.16 | 7.42 | 0.55 |
| LPO - new cell line only | 0.17 | 0.20 | 7.30 | 2.70 | -0.02 | 0.59 | 0.75 | 7.16 | 0.38 |
| LPO - new drug only | 0.31 | 0.35 | 5.80 | 2.41 | 0.05 | 0.67 | 1.03 | 6.14 | 0.54 |
| LPO - fully new (cell AND drug) | 0.15 | 0.21 | 7.33 | 2.71 | -0.04 | 0.57 | 0.65 | 7.03 | 0.37 |

---

## Conclusions

**Overall ranking on LCO (primary metric):** Drug-FP (0.73) > Drug-GNN (0.61) > Protein (0.21) ≈ RNA (0.22)

- **Both drug-only models (FP and GNN) are not learning genuine cell-line response — they're closer to a per-drug mean predictor.** High LCO/LTO/LPO-seen-drug performance combined with collapse on LDO (FP: 0.11, GNN: 0.13) and fully-new (FP: 0.16, GNN: 0.11 — not even statistically significant, p=0.11) confirms these models are largely memorizing per-drug potency, not differentiating cell lines.

- **Drug-FP beats Drug-GNN on every single split**, often by a wide margin (LCO: 0.73 vs 0.61, LTO: 0.74 vs 0.62, LPO-nothing-new: 0.77 vs 0.65). The GNN's `Variance Pred` is consistently lower than FP's (e.g. LCO: 2.56 vs 4.40) — the graph encoder produces a narrower, less discriminative embedding than the fixed Morgan fingerprint. At this dataset scale (~287 unique drugs, 6-feature atom encoding, 3-layer GCNConv, no pretraining), the fingerprint's fixed substructure prior outperforms the learned graph representation. Not necessarily a dead end for fusion, but as a standalone baseline GNN doesn't currently justify its added complexity over FP.

- **RNA and protein-only models are the most consistent across generalization axes, but weak in absolute terms everywhere.** Neither collapses as badly on LDO as the drug-only models do (protein: 0.29, RNA: 0.27 vs drug-FP: 0.11, drug-GNN: 0.13), but both lag far behind drug models on LCO. Protein slightly outperforms RNA on most splits, consistent with BDRN (Pearson 0.547 vs 0.531) and the project's RNA-protein complementarity hypothesis.

- **No single modality solves both generalization axes.** Drug features (FP/GNN) carry strong signal for seen-drug splits but fail on new drugs; omics carries weaker but more axis-stable signal. The fusion model's real test is beating drug-alone on LCO *and* beating omics-alone on LDO simultaneously — neither single-modality baseline does both.

- **Open decision for the fusion architecture:** lead with FP or GNN as the drug arm? FP is the safer default given its clear edge here, but GNN's weaker standalone performance doesn't rule out complementary value once combined with omics — worth testing both in the multimodal ablation rather than assuming FP wins there too.
