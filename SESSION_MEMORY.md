# Session Memory
*Current project state — read at the start of every session. Last updated: end of Session 4.*

---

## Project in one paragraph

Testing whether principled cross-attention fusion of RNA-seq and proteomics
improves drug response prediction over RNA-alone, under rigorous LCO/LDO/LTO/LPO
evaluation splits, for a one-month Inria Startup Studio pitch. Directly addresses
Turbine Research Lab's Open Problem 2 (Multimodal Synergy) and the gap DrEval's
benchmark identified (naive multimodal concatenation fails; most published models
barely beat a naive mean predictor under honest splits).

---

## Data

- **GDSC2** (drug response, `LN_IC50`) + **CCLE RNA-seq** + **ProCan-DepMapSanger
  proteomics** + **ChEMBL/RDKit drug features**.
- Universal cell line key: `cellosaurus_id`.
- Three-way overlap: **836 cell lines × 287 drugs**.
- **Real, post-filtering pair count (confirmed from notebook 04): 176,197 pairs**
  (filtered to: cell line in three-way overlap, drug has a valid SMILES, IC50 not
  null) — not the theoretical 836×287=204,931 grid.
- Feature widths (confirmed): **RNA = 17,738 genes**, **protein = 6,692 proteins**
  (Session 3's QC-filtered ProCan multi-peptide-confidence subset), **drug
  fingerprint = 2048 bits** (Morgan, radius=2).
- **Omics NaN handling: flat `fillna(0)`** — deliberate choice from Session 2
  (BDRN paper justification), not drevalpy's own median-center + downshifted-normal
  imputation. Confirmed present in notebook 07; needs porting to notebook 08
  (Session 5 task).

---

## Splits

`notebooks/04_splits.ipynb` — LPO, LCO, LDO, LTO, 5-fold each, saved to
`data/splits/{lpo,lco,ldo,lto}.json` (row indices into `data/processed/
response_pairs.parquet`, which shares the same 0..n-1 index space).

- **LCO uses `StratifiedGroupKFold`** (stratified by tissue, grouped by
  `cellosaurus_id`) — switched from plain `GroupKFold` after a composition
  sanity-check showed meaningfully better tissue-balance across folds.
- LDO groups by `drug_name`, LTO groups by `tissue`, LPO is plain random
  `KFold` on pair indices.
- Validated: zero group leakage where required (LCO/LDO/LTO), near-full overlap
  where expected (LPO), tissue TVD low except LTO (which is supposed to be high
  — that's the point of the split).

---

## Baselines — the big pivot

**Originally planned:** run drevalpy's `drug_response_experiment()` for local
(CPU) and GPU baselines (Session 4's `05_baselines_local.ipynb` /
`06_baselines_gpu.ipynb`, now orphaned).

**What actually happened:** verified drevalpy's real capabilities from its
installed 1.5.1 source, found it can't isolate RNA vs protein vs fusion the way
this project needs to (no baseline does genuine RNA+protein concatenation/fusion
— `cell_line_views` as a flat list means "pick one via grid search," never
"combine both"). Pivoted to fully independent custom notebooks built on notebook
04's splits/parquet directly:

- **`07_custom_baselines_sklearn.ipynb`** — `NaiveTissueDrugMeanPredictor`,
  `RandomForest`, `XGBoost` (ElasticNet removed per request). RNA-only and
  protein-only run and reported separately for every split/fold; fusion
  deliberately deferred (not built into these baselines).
- **`08_custom_baselines_dl.ipynb`** — `SimpleNeuralNetwork`, `DrugGNN`. `DIPK`
  deliberately out of scope (~1,100 lines upstream, needs BIONIC network
  features this project has no pipeline for — revisit only if asked).
- All models: **multi-drug** (global model, drug identity via fingerprint/graph,
  not one model per drug) — required for LDO to be meaningful at all.
- Architectures/hyperparameter grids matched to drevalpy's actual source per
  model, with deviations explicitly flagged where they exist (see below).

### Notebook 07 — current design, confirmed working

- Colab-compatible (`BASE_PATH` auto-detect/mount pattern, same as
  `00_colab_setup.ipynb`).
- **Hyperparameter selection runs once per (model, arm)**, not once per fold —
  on a designated reference fold (`GRID_SEARCH_SPLIT`/`GRID_SEARCH_FOLD_INDEX`,
  both configurable), then reused across all 4 splits × 5 folds. `HPAM_MODE`
  toggle: `"search"` (grid search as above) or `"fixed"` (skip search, use a
  user-supplied `FIXED_PARAMS` dict directly).
- Each model runs in its own independent cell (`NaiveTissueDrugMeanPredictor`,
  `RandomForest`, `XGBoost`), safely re-runnable individually — summary table
  dedupes on `(split, fold, arm, model)`.
- Progress printing throughout (per hyperparameter combo, per-fit
  "fitting... done (Xs)") — no silent long-running cells.
- `SAVE_PREDICTIONS_FOLDS = {0}` — disk space is limited, so raw per-pair
  prediction CSVs only get written for fold 0; `summary.csv` still logs every
  fold's metrics regardless.
- **Critical memory fix (this is the one to remember):** feature selection
  (`select_top_variance_genes`) must run on the compact per-cell-line table
  (≤836 rows) *before* building any per-pair matrix — never build the full
  17,738/6,692-column matrix across ~140,957 pairs first and reduce after.
  Getting this backwards is what crashed RandomForest (≈11 GB allocation for
  RNA alone) both locally and on Colab. **Confirmed fixed and running
  successfully on real data as of end of Session 4.**
- **Naive predictor fallback chain:** `(tissue, drug)` → drug-only mean →
  tissue-only mean → dataset mean (deviates from drevalpy's literal
  single-level fallback, necessary so LDO/LTO don't collapse to constant
  predictions with undefined Pearson r).
- **Real result, worth remembering for the pitch:** naive predictor strong
  under LPO/LCO (r≈0.86–0.87, matches DrEval's "naive mean is a tough
  baseline"), weak under LDO (r≈0.20–0.24), strong under LTO (r≈0.83–0.85).
  **Drug identity carries far more predictive weight than tissue identity**
  for this baseline — sets very different bars to beat per split type, and is
  itself a relevant framing point for the pitch.

### Notebook 08 — built, NOT yet run on real data

- `FeedForwardNetwork` and `DrugGraphNet` architectures matched exactly to
  drevalpy's source (raw PyTorch, not `pytorch_lightning`). Same per-model-cell
  pattern, progress printing, warning suppression as 07.
- **Almost certainly has the identical memory bug** notebook 07 had — unhit
  only because no real run has completed there yet. **This is Session 5's
  explicit focus** — see `NEXT_SESSION.md`.
- Could not be executed in this sandbox session (broken torch install there,
  unrelated to the project's real working environment) — validated via syntax
  checks only, not a real run.

### Known upstream deviations, all deliberate and flagged

- `MultiViewXGBoost`'s yaml defines `reg_lambda` but drevalpy's own
  `build_model()` never reads it (likely upstream bug) — wired it through
  properly here instead of reproducing the omission.
- `NaiveTissueDrugMeanPredictor`'s fallback chain (above) extends drevalpy's
  single-level fallback.
- `SimpleNeuralNetwork`'s second drug view (`drug_chemberta_embeddings`)
  dropped — fingerprints only, no ChemBERTa pipeline in this project.
- Feature selection criterion is **variance-based** here; drevalpy itself uses
  **completeness-based** selection for protein (`feature_threshold=0.7`,
  fallback to top-1000-most-complete) and a **fixed curated landmark gene
  list** for RNA (not data-driven at all). Not yet changed — flagged as a real
  difference worth a decision, not urgent.

---

## On the horizon

- **Session 5 (next):** port the memory + NaN-handling fixes from 07 to 08,
  confirm notebook 08 runs end-to-end on real data without crashing (see
  `NEXT_SESSION.md` for the full task list).
- **Task 4 — consolidation:** not started. Needs real `summary.csv` from both
  07 and 08 first. One table: model × split × arm × Pearson r/RMSE, all on the
  same notebook-04 folds.
- **DIPK:** open decision, not started, non-blocking.
- **`05`/`06` (drevalpy-harness notebooks):** orphaned by the pivot. Still
  useful as outside context (maps to the published DrEval leaderboard style)
  but can't isolate RNA vs protein vs fusion. No action needed unless that
  outside comparison is wanted.
- Beyond Session 5: the actual cross-attention fusion model (Week 3 of
  `PLAN.md`) — two `OmicsEncoder` MLPs → `CrossAttentionFusion` → concatenate
  with `DrugGNN` embedding → MLP predictor → `ln(IC50)`. Worth deciding then
  whether to reuse notebook 04's splits directly (simple, already built) or
  see if there's value in matching whatever mechanism ends up most convenient
  from the custom baseline notebooks for apples-to-apples comparison — they
  already share the same splits, so this should be straightforward.

---

## Things to never silently re-decide

- Multi-drug models only (not per-drug) — required for LDO to mean anything.
- Flat `fillna(0)` for omics NaNs, not drevalpy's median-center+impute.
- Variance-based feature selection (top-K, computed per-fold from train-only
  unique cell lines) — not completeness-based, not a fixed landmark list.
- `ElasticNet` is out, replaced by `XGBoost`, in the sklearn baseline set.
- Feature selection must happen before per-pair matrix expansion, always —
  this is the load-bearing fix from this session, easy to accidentally regress
  if functions get refactored again.
