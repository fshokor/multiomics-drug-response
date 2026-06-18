# MultiModal Drug Response Prediction
### Can RNA + Protein fusion beat RNA-alone for cancer drug sensitivity prediction?

---

## The Problem

Predicting how a specific cancer cell will respond to a drug — before testing it in the lab — is one of the central challenges in precision oncology. If we could reliably predict drug sensitivity from a tumor's molecular profile, we could match patients to the right treatment faster, skip ineffective drugs, and reduce trial-and-error in the clinic.

Large-scale pharmacogenomic datasets (GDSC, CCLE) have made this tractable: thousands of drug response measurements across hundreds of cancer cell lines, each profiled molecularly. Machine learning models trained on these datasets have shown promise — but a critical 2026 benchmark study (DrEval, Bernett et al., *Nature Communications*) revealed that most published models are overly optimistic. Under honest evaluation splits — where the model must generalize to **unseen cell lines** (LCO) or **unseen drugs** (LDO) — deep learning models barely beat a naive mean predictor, and no complex model outperforms a properly tuned Random Forest on gene expression alone.

This raises the central question this project addresses:

> **If gene expression captures most predictive signal, can adding proteomics reveal genuinely complementary information — and can a principled fusion architecture exploit it?**

Most prior work either uses gene expression alone, or naively concatenates omics modalities. Naive concatenation has been shown to fail (Turbine Research Lab, 2026) because it violates assumptions about modality pairing, allows one modality to dominate, and introduces redundant features. We test whether a cross-attention fusion architecture — designed to learn the complementarity between RNA and protein — can achieve genuine multimodal synergy under rigorous LCO and LDO evaluation splits.

---

## What We Are Trying to Achieve

**Scientific goal:** Demonstrate that RNA + protein fusion, implemented with a principled cross-attention architecture, improves drug response prediction over RNA-alone — specifically under cell-line-exclusive (LCO) evaluation, and specifically in solid cancers where RNA-protein correlation is lowest (~0.53) and the two modalities carry the most independent information.

**Technical deliverable:** A working DL model (cross-attention fusion of RNA + protein + drug GNN) benchmarked against rigorous baselines using the DrEval framework, with all results reported under LPO, LCO, and LDO splits.

**Startup/pitch goal:** A proof-of-capability prototype demonstrating that (1) we understand the failure modes of naive multimodal integration, (2) we've designed an architecture to address them, and (3) we can show measurable improvement under honest evaluation — directly addressing Turbine Research Lab's open Problem 2 (Multimodal Synergy).

---

## Hypothesis

RNA and protein expression are weakly correlated (~0.44 gene-wise, ~0.54 cell-line-wise Pearson r) in cancer cell lines, meaning they carry partially independent biological information. Naive concatenation fails because it does not account for this partial independence. A cross-attention fusion model that explicitly learns which proteins diverge most from their RNA counterparts — and weights them accordingly — will show genuine multimodal improvement under LCO, specifically in solid tumors.

---

## Data

| Dataset | Description | Source | Size |
|---|---|---|---|
| **GDSC2** | Drug response (IC50/AUC) for ~969 cell lines × ~575 drugs | [cancerrxgene.org](https://www.cancerrxgene.org/downloads/bulk_download) | ~10 MB |
| **CCLE RNA-seq** | Gene expression (TPM) for ~1,019 cell lines × ~20,000 genes | [depmap.org](https://depmap.org/portal/) | ~200 MB |
| **ProCan-DepMapSanger** | Proteomics (8,498 proteins) for 949 cell lines | [figshare](https://doi.org/10.6084/m9.figshare.19345397) / [Sanger](https://cellmodelpassports.sanger.ac.uk) | ~495 MB |
| **ChEMBL** | Drug SMILES strings for ~575 GDSC2 drugs | [ebi.ac.uk/chembl](https://www.ebi.ac.uk/chembl/) | API |
| **Cell Model Passports** | Cell line ID mapping (CCLE ↔ GDSC ↔ Sanger) | [cellmodelpassports.sanger.ac.uk](https://cellmodelpassports.sanger.ac.uk/downloads) | <5 MB |

**Effective dataset after three-way join:** ~811–911 cell lines × ~400–500 drugs ≈ ~100,000 usable drug-cell line pairs.

---

## Model Architecture

```
Cell line input:
  RNA vector (20,000 genes)     → MLP encoder → RNA embedding (256-d)
  Protein vector (top-K proteins) → MLP encoder → Protein embedding (256-d)
  Cross-attention(RNA, Protein) → Fused cell embedding (256-d)

Drug input:
  SMILES → GNN (GCNConv) → Drug embedding (256-d)

Prediction:
  Concat(Fused cell, Drug) → MLP → predicted ln(IC50)
```

Key design choices:
- **Cross-attention fusion** instead of naive concatenation — learns which proteins add information beyond their RNA counterpart
- **Modality dropout** (30%) during training — forces robustness to missing proteomics
- **GNN for drug** (GCNConv from PyTorch Geometric) — state-of-the-art drug representation
- **Statistical pre-selection** of proteins by independent predictive contribution beyond RNA

---

## Evaluation Protocol

Following DrEval (Bernett et al., 2026):

| Split | Description | Clinical relevance |
|---|---|---|
| **LPO** | Leave random pairs out | Matrix completion / imputation |
| **LCO** | Leave cell line out | New patient generalization |
| **LDO** | Leave drug out | New drug generalization |

All results reported under all three splits. **LCO is the primary metric.** Random split (LPO) reported as secondary context only.

Baselines to beat:
1. Naive mean predictor (predict average IC50 per drug)
2. Tuned Random Forest on RNA alone
3. BDRN (protein alone, GCNConv) — Zheng et al. 2024
4. BDRN (RNA alone, GCNConv) — Zheng et al. 2024

---

## Related Work

### Key Papers

| Paper | Year | Key Finding | Relevance |
|---|---|---|---|
| **DrEval** — Bernett, Iversen, List et al. *Nature Comms* | 2026 | DL barely beats naive mean under LCO/LDO; extra omics don't help with naive concatenation | Defines our evaluation protocol and the gap we address |
| **BDRN** — Zheng, Huang, Wong et al. *bioRxiv* | 2024 | Protein alone slightly beats RNA alone (Pearson 0.547 vs 0.531); never tested RNA+protein combined | Our direct baseline; we extend to true multimodal fusion |
| **ProCan-DepMapSanger** — Gonçalves et al. *Cancer Cell* | 2022 | 8,498 proteins across 949 cell lines; proteome ≈ transcriptome for drug prediction | Our proteomics dataset |
| **Make multimodality work for you** — Turbine TRAIL blog | 2026 | Identifies 3 failure modes of naive fusion: pairing, smoothness, extrapolation | Frames our problem and hypothesis directly |
| **scMODAL** — Wang, Zhao et al. *Nature Comms* | 2025 | Feature-link-guided cross-modal alignment via GAN | Architectural inspiration for fusion design |
| **Network-based multi-omics review** — Jiang et al. *BioData Mining* | 2025 | GNN taxonomy for drug discovery; identifies gap in cell-line network representation | Landscape map |
| **Ahlmann-Eltze et al.** *Nature Methods* | 2025 | Foundation models don't beat PCA/linear baselines for perturbation prediction | Justifies our "simple first" approach |

### Companies in This Space

| Company | Focus | Stage | Notes |
|---|---|---|---|
| **Turbine.ai** (Budapest) | Simulated cancer cells for drug combination discovery | Series B | Mechanistic + ML hybrid; open research problems published publicly |
| **Owkin** (Paris/NYC) | Federated learning on hospital data for drug discovery | Series B | Strong French presence; RNA-centric models |
| **Recursion** (Salt Lake City) | Phenomics foundation models (Cell Painting) | Public (RXRX) | Image-first, not omics-first |
| **Insilico Medicine** | Generative AI for drug target ID and molecule design | Late stage | Has Phase 2 drug candidate |
| **Insitro** | Multiomics + ML for target discovery | Series C | Partnered with BMS and Gilead |
| **One Bioscience** (France) | AI drug discovery | Early | French ecosystem |
| **Orakel Oncology** (France) | Oncology AI | Early | French ecosystem |
| **Unlearn.ai** | Digital twins for clinical trial control arms | Series B | FDA-cleared for some indications |
| **Arc Institute** | Virtual cell models (STATE) | Non-profit | Released Tahoe-100M, Virtual Cell Challenge |

---

## Repository Structure

```
multiomics-drug-response/
├── README.md
├── requirements.txt
├── environment.yml
├── .gitignore
│
├── data/
│   ├── raw/                    # Downloaded raw files (git-ignored)
│   │   ├── gdsc2/
│   │   ├── ccle/
│   │   ├── procan/
│   │   └── chembl/
│   ├── processed/              # Cleaned, joined, normalized (git-ignored)
│   │   ├── cell_lines.csv
│   │   ├── drug_features.csv
│   │   └── drug_response.csv
│   └── splits/                 # LPO, LCO, LDO split indices
│
├── notebooks/
│   ├── 01_data_download.ipynb
│   ├── 02_data_processing.ipynb
│   ├── 03_statistical_analysis.ipynb
│   ├── 04_baselines.ipynb
│   ├── 05_dreval_benchmark.ipynb
│   ├── 06_model_training.ipynb (Colab)
│   └── 07_results_analysis.ipynb
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── download.py
│   │   ├── preprocess.py
│   │   ├── harmonize.py        # Cell line name matching
│   │   └── splits.py           # LPO, LCO, LDO split logic
│   ├── features/
│   │   ├── __init__.py
│   │   ├── drug_features.py    # SMILES → Morgan fingerprint / GNN graph
│   │   └── omics_features.py   # RNA normalization, protein imputation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── baselines.py        # Naive mean, Random Forest, ElasticNet
│   │   ├── bdrn.py             # BDRN reproduction (GNN + MLP, RNA or protein)
│   │   └── fusion_model.py     # Cross-attention multimodal model
│   ├── training/
│   │   ├── __init__.py
│   │   ├── train.py
│   │   └── evaluate.py
│   └── analysis/
│       ├── __init__.py
│       ├── correlation.py      # RNA-protein correlation analysis
│       └── visualization.py
│
├── configs/
│   ├── default.yaml
│   └── colab.yaml
│
├── results/
│   ├── figures/
│   ├── tables/
│   └── checkpoints/            # git-ignored
│
└── tests/
    ├── test_data.py
    ├── test_models.py
    └── test_splits.py
```

---

## Acknowledgements

This project directly addresses open Problem 2 (Multimodal Synergy) published by Turbine Research & AI Labs (TRAIL): [turbine.science/research](https://turbine.science/research).

Evaluation framework: DrEval by Bernett, Iversen, List et al. [github.com/daisybio/drevalpy](https://github.com/daisybio/drevalpy)
