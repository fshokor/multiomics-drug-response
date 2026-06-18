# Session Memory
## Last updated: Session 2

---

## Current State

**Phase:** Week 1 complete — data downloaded and verified
**Status:** All data ready. Three-way overlap confirmed. Ready for processing and baselines.

---

## Data Layout

```
data/
├── GDSC2/
│   ├── GDSC2.csv                  ← drug response (cell_line_name × pubchem_id)
│   ├── gene_expression.csv        ← RNA-seq, cellosaurus_id index
│   ├── proteomics.csv             ← ProCan converted, cellosaurus_id index
│   ├── cell_line_names.csv        ← cellosaurus_id ↔ cell_line_name ↔ tissue
│   ├── drug_smiles.csv
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
| Gene expression cell lines | 1,010 |
| Proteomics cell lines | 860 |
| **Three-way overlap** | **836** |
| GDSC2 drugs | 287 |
| Drug-cell line pairs in overlap | 204,931 |
| Genes | 17,738 |
| Proteins | 8,498 |

## Universal Key
- `cellosaurus_id` (e.g. `CVCL_0001`) — used by gene_expression.csv and proteomics.csv
- GDSC2.csv uses `cell_line_name` → map via `cell_line_names.csv`

## Key Decisions
- drevalpy Zenodo bundle used for GDSC2 + gene expression + drug features
- ProCan downloaded manually from figshare (90 MB .txt, tab-separated)
- ProCan index format: `SIDM00018;K052` → extract name after `;` → normalize → map to cellosaurus_id
- 862 ProCan cell lines mapped (87 unmatched, acceptable)
- drevalpy version 1.5.1, Python 3.11

## Scripts
- `src/data/download.py` — full pipeline: drevalpy download + ProCan conversion + verification
- `notebooks/01_data_download.ipynb` — verification notebook, all cells passing
