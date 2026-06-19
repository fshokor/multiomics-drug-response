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

## Session 3 — Statistical Analysis & Similarity/Clustering
 
**Scope:** Expanded beyond the original plan (Tasks 1-2: RNA-protein correlation,
independent protein signal) to include tissue-confound checks, the blood-vs-solid
hypothesis test, cell-line/drug similarity clustering, and pair-level heterogeneity
analysis. Tasks 3-4 (baselines, splits) deferred to Session 4.
 
**Key fixes:**
- Diagnosed and fixed a protein-to-gene-symbol mapping bug (UniProt mnemonic vs. official
  symbol) that was silently excluding ~4,800 proteins from every correlation calculation.
- Switched to ProCan's 6,692-protein multi-peptide-confidence subset, recovering
  literature-consistent correlation numbers.
- Fixed duplicate-`cellosaurus_id` row bugs (3 separate occurrences across two notebooks).
**Key result:** Blood vs. solid RNA-protein correlation difference is statistically
significant (p = 7.3e-11) in the hypothesized direction — direct support for the
project's core multimodal hypothesis. This only emerged after the data-quality fixes
above; the naive pipeline showed no effect.
 
**Deliverables:**
- `notebooks/02_statistical_analysis.ipynb` (reorganized into labeled subsections)
- `notebooks/03_similarity_clustering.ipynb`
- `data/processed/top_independent_proteins.csv` — candidate protein list for the fusion
  model, cross-validated by two independent statistical methods
- `results/analysis_summary.md` — full write-up of all findings
- `SESSION_MEMORY.md`, `NEXT_SESSION.md` updated accordingly
**Carried forward to Session 4:** drevalpy baselines (local CPU + Colab GPU) and
generating/saving all four splits (LPO, LCO, LDO, LTO).