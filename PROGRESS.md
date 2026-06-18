# Progress Log

---

## Session 1 — Project Planning
- Defined project scope: RNA + protein cross-attention fusion for drug response prediction
- Chose datasets: GDSC2, CCLE RNA-seq, ProCan proteomics, ChEMBL SMILES
- Wrote README.md (hypothesis, architecture, related work, company landscape)
- Wrote PLAN.md (full 4-week implementation plan with code)
- Identified evaluation protocol: LPO/LCO/LDO via DrEval
- Primary metric: Pearson r under LCO

---

## Session 2 — Environment + Data Download Scripts
- Created full repo folder structure
- Created `.gitignore`, `environment.yml`, `requirements.txt` stub
- Pivoted data strategy: use drevalpy Zenodo data instead of raw GDSC2/CCLE downloads
  - Guarantees split consistency with published baselines
  - Eliminates CCLE manual download and cell line name harmonization
  - Only novel addition is ProCan proteomics (still downloaded manually)
- Wrote `src/data/download.py`:
  - drevalpy handles GDSC2 + gene expression automatically
  - ProCan downloaded from figshare, converted to drevalpy format (cell_line_name index)
  - Cell Model Passports used for Sanger ID → cell_line_name mapping
  - Verification step reports three-way overlap
- Created `notebooks/01_data_download.ipynb`
- **TODO (local machine):** conda env create -f environment.yml, then python src/data/download.py

---

## Session 2 — Environment + Data Download
- Rebuilt conda environment with Python 3.11 (drevalpy 1.5.x requires >=3.11)
- Installed all 15 packages successfully
- Downloaded GDSC2 bundle via drevalpy (Zenodo): drug response, gene expression, drug SMILES/fingerprints/graphs
- Downloaded ProCan manually from figshare (ProCan-DepMapSanger_protein_matrix_8498_averaged.txt, 90 MB)
- Converted ProCan to drevalpy format: extracted cell line name from SIDM;name index, normalized, mapped to cellosaurus_id via cell_line_names.csv
- Confirmed three-way overlap: 836 cell lines, 287 drugs, 204,931 pairs
- Updated download.py and 01_data_download.ipynb to reflect actual data layout
