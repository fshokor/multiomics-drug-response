# Session Memory
## Last updated: Session 3

---

## Current State

**Phase:** Week 2, Day 6-7 complete — statistical analysis and similarity/clustering
diagnostics done (notebooks 02 and 03), including extra scope beyond the original plan
(tissue-confound checks, blood-vs-solid hypothesis test, drug similarity, pair
heterogeneity). Full results in `results/analysis_summary.md`.

**Status:** Protein data pipeline is now fixed and validated end-to-end. Core hypothesis
(protein carries more independent signal in solid vs. blood cancers) has direct
statistical support. Ready to move to baselines and splits (Task 3-4, deferred from
Session 3 — see `NEXT_SESSION.md`).

---

## Data Layout

```
data/
├── GDSC2/
│   ├── GDSC2.csv                  ← drug response (cell_line_name, drug_name, LN_IC50,
│   │                                 tissue, cellosaurus_id, + curve-fit columns)
│   ├── gene_expression.csv        ← RNA-seq log2(TPM+1), cellosaurus_id index,
│   │                                 includes a `cell_line_name` column + ~9 "Unnamed"
│   │                                 junk columns mixed into the gene columns
│   ├── proteomics.csv             ← ProCan, cellosaurus_id index, columns are
│   │                                 `UniProtID;EntryName_HUMAN` (NOT gene symbols —
│   │                                 see Key Decisions)
│   ├── cell_line_names.csv        ← cellosaurus_id ↔ cell_line_name ↔ tissue
│   ├── drug_smiles.csv            ← pubchem_id, drug_name, canonical_smiles,
│   │                                 cactvs_fingerprint, fingerprint (precomputed,
│   │                                 not used — see Key Decisions)
│   ├── drug_fingerprints/
│   └── drug_graphs/
└── meta/
    ├── tissue_mapping.csv
    └── gene_lists/
```

## Key Numbers

| Dataset | Value |
|---|---|
| GDSC2 cell lines | 969 |
| Gene expression cell lines (post-dedup) | 1,010 (4 duplicates dropped) |
| Proteomics cell lines (post-dedup) | 860 (2 duplicates dropped) |
| **Three-way overlap (`common_ids`)** | **836** |
| Proteomics, multi-peptide-confidence set | **6,692 proteins** (not the full 8,498 release) |
| Proteins matched to RNA gene symbols | 6,667 (mygene) → 5,887-7,373 intersection with RNA depending on min-N filter |
| GDSC2 drugs | 287 |
| Tissue categories | 26 (e.g. blood/lymphoid are simply `Blood` and `Lymph`, not the literature's typical naming) |

## Universal Key
- `cellosaurus_id` (e.g. `CVCL_0001`) — used by `gene_expression.csv` and `proteomics.csv`
- `GDSC2.csv` uses `cell_line_name` → map via `cell_line_names.csv`

## Key Decisions (Session 3 additions)

- **Protein columns are NOT gene symbols.** Format is `UniProtID;EntryName_HUMAN` (a
  UniProt mnemonic). The mnemonic frequently diverges from the official HGNC gene symbol
  (e.g. ribosomal protein family: `RL4_HUMAN` vs. real symbol `RPL4`). Parsing the
  mnemonic directly only matched ~3,700 genes; mapping by **UniProt accession** (the part
  before `;`) via `mygene` recovers ~6,667-8,404 depending on protein set used. This
  mapping must be re-derived (or persisted/loaded) in every notebook that touches
  proteomics — it bit us twice in notebook 03 before we caught it both times.
- **Use the 6,692-protein multi-peptide-confidence ProCan subset, not the full 8,498.**
  This is the original ProCan paper's own QC filter (>1 supporting peptide per protein).
  Recovers literature-consistent correlation (~0.41-0.42) without needing additional
  missingness filtering — tested, confirmed not to need a further completeness cut.
- **Always dedup `cellosaurus_id` rows** in `rna`/`protein` immediately after loading
  (`rna[~rna.index.duplicated(keep="first")]` etc.) — un-deduped indices cause silent
  row-count mismatches in any function doing `.loc[cell_ids]` + `.values` (hit this bug
  three separate times across notebooks 02 and 03).
- **Drug fingerprints:** use RDKit Morgan fingerprints computed from `canonical_smiles`
  (`rdFingerprintGenerator.GetMorganGenerator`, radius=2, 2048 bits) — NOT the precomputed
  `cactvs_fingerprint`/`fingerprint` columns in `drug_smiles.csv` (those are PubChem
  CACTVS substructure-key fingerprints, a different scheme, inconsistent with the rest of
  the project's fingerprint choice in PLAN.md).
- **LTO confirmed as a native drevalpy split mode** (alongside LPO/LCO/LDO) — already
  added to the project's split plan per an earlier session decision.
- **drevalpy's own multi-omics baselines do NOT use proteomics** — they use CNV,
  methylation, and mutation alongside gene expression. ProCan/protein is entirely this
  project's own addition; there's no drevalpy-native apples-to-apples multi-omics
  baseline for "does protein help." Frame `RandomForest` (gene-expression-only) as the
  primary baseline to beat; `MultiViewXGBoost` etc. as secondary context with a different
  omics combination, not a protein comparison.
- **drevalpy's baseline models are called by name string** via `MODEL_FACTORY` /
  `drug_response_experiment()` — no need to reimplement DIPK, DrugGNN, MultiViewXGBoost,
  etc. Validation splits respect the same disjointness logic as the test split
  automatically (confirmed from the DrEval paper).

## Key Results (Session 3) — see `results/analysis_summary.md` for full detail

- Gene-wise RNA-protein correlation: median Pearson 0.415, Spearman 0.407 — matches
  independent literature reanalysis of this exact dataset (OnCorr: 0.42).
- **Blood vs. solid cell-line-wise correlation: 0.389 vs. 0.371, p = 7.3e-11** — direct
  statistical support for the project's core hypothesis. Only emerged after the protein
  mapping/confidence-filtering fixes above; the naive/uncleaned pipeline showed no
  significant difference (p=0.26).
- Independent-protein candidate list saved: `data/processed/top_independent_proteins.csv`
  (cross-validated by two methods, single-drug pass on 5-Fluorouracil).
- Cell-line clustering: RNA vs. protein ARI ≈ 0.42 (PCA/UMAP, consistent); Skin and Blood
  are the only tissues with strong cross-modality identity.
- Drug set is highly diverse (median Tanimoto 0.104); found duplicate-named compounds
  (need cleanup) and real analog families (keep together in LDO splits) — see summary doc.
- Pair-level heterogeneity: median within/across cluster IC50 variance ratio = 0.760 —
  cell-line clusters capture real, moderate response structure.

## Scripts & Notebooks
- `src/data/download.py` — full pipeline: drevalpy download + ProCan conversion + verification
- `notebooks/01_data_download.ipynb` — verification notebook, all cells passing
- `notebooks/02_statistical_analysis.ipynb` — RNA-protein correlation, tissue/blood-solid
  analysis, independent-protein signal (Task 1 & 2, reorganized into clear subsections)
- `notebooks/03_similarity_clustering.ipynb` — HVG selection, cell-line clustering
  (PCA/UMAP/t-SNE), drug similarity, pair-level heterogeneity
- `results/analysis_summary.md` — full write-up of all Session 3 findings
