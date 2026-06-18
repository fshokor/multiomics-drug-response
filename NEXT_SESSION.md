# Next Session Tasks
## Session 3 — Data Processing and Harmonization

---

## Prerequisites (must be done before this session)
- [ ] Run `python src/data/download.py` on local machine
- [ ] Manually download CCLE RNA-seq from depmap.org
- [ ] Run `notebooks/01_data_download.ipynb` and confirm all 4 files loaded correctly
- [ ] Paste actual numbers into SESSION_MEMORY.md (cell line counts, shapes)

---

## Goal for This Session
Process raw data into clean, joined feature matrices ready for model training.

---

## Tasks (in order)

**Task 1: Understand raw file structures**
- Print columns, dtypes, index formats for all 4 files
- Identify the exact column names for: cell line ID in GDSC2, DepMap ID in mapping, Sanger ID in ProCan
- Note any surprises vs what PLAN.md expects

**Task 2: Standardize cell line IDs to DepMap**
- Build lookup dicts: Sanger → DepMap, CCLE name → DepMap, cell line name → DepMap
- Convert ProCan index (Sanger → DepMap)
- Convert GDSC2 cell line names → DepMap
- Report: how many cell lines fail to map in each dataset?

**Task 3: Find three-way overlap**
- Compute: RNA ∩ GDSC, Protein ∩ GDSC, RNA ∩ Protein ∩ GDSC
- Save overlap IDs to `data/splits/cell_line_ids_three_way.json`
- Expected: 811–911 three-way overlap

**Task 4: Build clean feature matrices**
- Filter RNA, protein, GDSC2 to three-way overlap
- Handle ProCan missing values: fill NaN with 0
- Normalize: z-score per feature (fit on full matrix here; per-fold normalization comes later)
- Save: `data/processed/rna.parquet`, `data/processed/protein.parquet`, `data/processed/drug_response.parquet`

**Task 5: Drug SMILES download**
- Load GDSC2 drug list
- Query ChEMBL API for all drugs (batch query)
- Fallback to PubChem for misses
- Save: `data/raw/chembl/drug_smiles.csv`
- Report: how many drugs found / total?

**Task 6: Implement data splits**
- Write `src/data/splits.py` with make_lpo_splits, make_lco_splits, make_ldo_splits
- Generate all three splits (5-fold each)
- Save to `data/splits/` as JSON
- Verify: assert no cell line overlap in LCO, no drug overlap in LDO

---

## Code to write
- `src/data/preprocess.py` — harmonization + feature matrix construction
- `src/data/splits.py` — split generation (already in PLAN.md)

---

## Context
- See PLAN.md → Week 1 → Day 3-5 for full code
- Key risk: cell line name matching — expect ~5–15% failures, handle with fuzzy match or manual map
