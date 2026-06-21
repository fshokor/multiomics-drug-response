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

---

## Session 4 — Splits, Pivot Away From drevalpy, Custom Baselines

**Scope:** Originally scoped as drevalpy baselines + splits (Session 3's deferred
Tasks 3-4). Splits were completed as planned; the baselines work pivoted hard
partway through once drevalpy's actual capabilities were verified against its
installed source rather than assumed.

**Task 1 — Splits (as planned):**
- `notebooks/04_splits.ipynb`: generated and saved LPO, LCO, LDO, LTO (5-fold
  each) to `data/splits/*.json`, plus the filtered `response_pairs.parquet`
  (the real, post-filtering pair count, not the theoretical 836×287 grid) to
  `data/processed/`.
- Added a composition/leakage sanity-check table (per-fold overlap counts,
  unseen-fraction, tissue TVD) and switched LCO from plain `GroupKFold` to
  `StratifiedGroupKFold` (stratified by tissue) after the sanity check showed
  meaningfully better tissue-composition balance across folds.
- Real numbers confirmed: 176,197 total pairs (≈86% of the theoretical
  204,931 ceiling).

**Major pivot — drevalpy's actual baseline capabilities, verified from its
installed 1.5.1 source (not docs, not assumption):**
- Confirmed `drug_response_experiment()` generates and manages its own
  train/val/test splits internally — doesn't consume notebook 04's splits at
  all. `test_mode` is a single string, not a list (four separate calls needed).
- **Correction to an earlier wrong statement (echoing the project's own
  `NEXT_SESSION.md` note):** drevalpy's `RandomForest`/`ElasticNet`/etc.
  baselines *do* use proteomics — `cell_line_views: [gene_expression,
  proteomics]` in their yaml is a grid-search **alternative** (try one or the
  other, pick by validation RMSE), not "never protein" as previously assumed.
  `MultiViewXGBoost` similarly includes a proteomics-only option.
- **What's still true:** no drevalpy baseline does genuine RNA+protein
  **fusion** — `cell_line_views` as a flat list always means "pick one,"
  never "concatenate both." This — not the protein-blindness — is the actual
  reason drevalpy's harness can't serve this project's core hypothesis test.
- **Decision:** abandoned `drug_response_experiment()` for the RNA-vs-protein
  comparison. Built independent notebooks instead, using notebook 04's splits
  and parquet directly: `07_custom_baselines_sklearn.ipynb`
  (`NaiveTissueDrugMeanPredictor`, `RandomForest`, `XGBoost` — `ElasticNet`
  removed per request) and `08_custom_baselines_dl.ipynb`
  (`SimpleNeuralNetwork`, `DrugGNN` — `DIPK` deliberately deferred, ~1,100
  lines upstream with BIONIC network features this project has no pipeline
  for). Architectures and hyperparameter grids matched to drevalpy's actual
  source for each model. Confirmed: multi-drug models throughout (global
  model, drug identity via fingerprint/graph) — required for LDO to be
  meaningful at all.

**Notebook 07 iteration — several rounds of real fixes, not just polish:**
- Colab compatibility (mirrors the `BASE_PATH` pattern from `00_colab_setup.ipynb`).
- Redesigned hyperparameter selection to run **once per (model, arm)** on a
  designated reference fold, not once per fold — cuts total grid evaluations
  from 80 to 4. Added `HPAM_MODE` toggle (`"search"` vs `"fixed"` with a
  user-supplied params dict), tested both end-to-end.
- Split the combined run loop into independent per-model cells
  (`NaiveTissueDrugMeanPredictor`, `RandomForest`, `XGBoost`), each
  runnable/re-runnable on its own; summary table dedupes on
  `(split, fold, arm, model)` to stay safe under reruns.
- Added progress printing throughout (per hyperparameter combo during search,
  per-fit "fitting... done (Xs)") so long-running cells are never silent.
- `SAVE_PREDICTIONS_FOLDS = {0}` added — disk space is limited, so raw
  per-pair prediction CSVs now only get written for fold 0; `summary.csv`
  still logs every fold's metrics regardless.
- **Critical memory bug found and fixed:** `build_feature_matrix` was
  materializing the *full* omics-width matrix (17,738 RNA / 6,692 protein
  columns) per training pair **before** top-K feature selection ever ran —
  for ~140,957 train rows that's ~11.1 GB (RNA) allocated before any
  reduction, which is what was crashing the kernel locally and on Colab, not
  the grid search itself. Fixed by computing top-variance genes/proteins on
  the compact per-cell-line table first (≤836 rows), then only expanding the
  already-reduced columns out to per-pair rows. **Confirmed working** —
  RandomForest is running successfully on real data with this fix as of the
  end of this session.
- **Naive predictor fallback fixed:** `NaiveTissueDrugMeanPredictor`'s
  original single-level fallback (straight to the global dataset mean for any
  unseen `(tissue, drug)` combo) made every LDO and LTO prediction constant —
  Pearson r was undefined (NaN) for all 10 of those folds. Added an
  intermediate fallback chain: `(tissue, drug)` → drug-only mean → tissue-only
  mean → dataset mean. This is a deliberate deviation from drevalpy's literal
  `naive_pred.py` (single-level fallback), necessary for the per-split
  comparison to mean anything. **Real result post-fix, worth remembering for
  the pitch:** naive predictor is strong under LPO/LCO (r≈0.86–0.87, matching
  DrEval's "naive mean is a tough baseline" finding), much weaker under LDO
  (r≈0.20–0.24 — tissue-only fallback carries little signal), strong again
  under LTO (r≈0.83–0.85 — drug-mean fallback recovers most of it). Takeaway:
  **drug identity carries far more predictive weight than tissue identity**
  for this naive baseline — sets very different bars to beat per split type.
- **Gap found, not yet fixed everywhere:** omics CSVs were never actually
  NaN-imputed (only index-deduped) — proteomics in particular has real
  missingness. Decision: flat `fillna(0)`, matching the project's existing
  Session 2 choice (BDRN paper justification) over drevalpy's own
  median-center + downshifted-normal imputation. Confirmed present in
  notebook 07; **not yet confirmed/ported to notebook 08.**

**Notebook 08 — built and structurally validated, NOT yet run on real data:**
- `SimpleNeuralNetwork` (`FeedForwardNetwork`, raw PyTorch not
  `pytorch_lightning`) and `DrugGNN` (`DrugGraphNet`, 3-layer `GCNConv`)
  architectures matched exactly to drevalpy's source, including the
  asymmetric last-hidden-layer detail in `FeedForwardNetwork` (no BN/dropout
  on the final hidden layer, unlike the others).
  `drug_chemberta_embeddings` (a second drug view in drevalpy's
  `SimpleNeuralNetwork`) dropped — no ChemBERTa pipeline in this project,
  fingerprints only.
  After hyperparameter selection, the early-stopped model from the winning
  trial is used directly for test prediction — not refit on train+val, unlike
  the sklearn baselines (deliberate, to avoid overfitting without a held-out
  set for early stopping).
- Same Colab compatibility, per-model run cells, progress printing
  (per-epoch, with a "best so far" trail and early-stop summary), and locally
  scoped warning suppression as notebook 07.
- **Could not be executed in this sandbox** — broken torch install, unrelated
  to the project's real environment (confirmed working with CUDA in Session
  2). Validated via syntax checks and RDKit graph-construction logic only.
- **Almost certainly has the same memory bug notebook 07 had**, just unhit
  because no real run has completed there yet. **This is the explicit focus
  of Session 5** (see `NEXT_SESSION.md`).

**Other:**
- `xgboost` confirmed as a genuinely new dependency (`pip install xgboost`,
  also an optional drevalpy extra discovered along the way:
  `pip install drevalpy[xgboost]`) — not in the original Session 2 package
  list.
- One upstream deviation flagged and kept: `MultiViewXGBoost`'s yaml defines
  `reg_lambda` but drevalpy's own `build_model()` never reads it (likely an
  upstream bug) — wired it through properly in the custom notebooks instead
  of reproducing the omission.

**Carried forward to Session 5:** port the memory + NaN-handling fixes to
notebook 08, run it end-to-end on real data, then build the Task 4
consolidation notebook once both 07 and 08 have real `summary.csv` files.
DIPK and the orphaned drevalpy-harness notebooks (05/06) remain open,
non-blocking decisions.

## Session — Baselines under new split structure (naive, RF, single-modality DL)
 
- Built `09_custom_MLP.ipynb`: single-modality DL baselines (RNA, protein, drug fingerprint via `NN1Omics`; drug graph via new `DrugGNN`/GCNConv). Fixed a protein NaN propagation bug (`fillna(0)` was missing post-dedupe). Extended `evaluateMT()` with RMSE, Spearman, R², ROC-AUC, and a NaN-safe constant-prediction guard.
- Built `10_naive_predictors.ipynb`: all 6 drevalpy naive baselines (`NaivePredictor`, `NaiveDrugMeanPredictor`, `NaiveCellLineMeanPredictor`, `NaiveTissueMeanPredictor`, `NaiveTissueDrugMeanPredictor`, `NaiveMeanEffectsPredictor`) under the new shared-train/four-test-set fold structure. Confirmed `NaiveMeanEffectsPredictor` is the real bar to beat per drevalpy. Noted the strict single-fallback `NaiveTissueDrugMeanPredictor` is not comparable to the project's earlier 3-level chained-fallback version from notebook 07/old splits.
- Built `11_random_forest.ipynb`: RF ablation across RNA, Protein, RNA+Drug, Protein+Drug, Drug-only arms, fixed hyperparameters, leakage-safe top-variance feature selection (train-fold cell lines only), mean ± std summary across 5 folds.
- **Key finding:** RNA-only and protein-only RF predictions are nearly identical (r=0.996 between the two arms' predictions) — top-variance feature selection collapses both omics layers onto a shared tissue-of-origin proxy rather than modality-specific signal. This invalidates the current RNA-vs-protein comparison and must be fixed (RNA-divergence-aware protein selection, e.g. partial correlation or residual variance) before the fusion model, since the project hypothesis depends on RNA/protein carrying genuinely independent information.
- Next session: implement corrected protein feature selection, re-validate protein-only and protein+drug results.