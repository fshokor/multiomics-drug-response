# Next Session Tasks
## Session 5 — Fix Memory in DL Baselines (Notebook 08)

---

## Goal

Apply the same memory and correctness fixes notebook 07 just received to
notebook 08 (`SimpleNeuralNetwork`, `DrugGNN`) — it almost certainly has the
identical bug, just never hit it yet because no real run has completed there.
Confirm fixed notebook 08 actually runs end-to-end on real data without
crashing, on both local and Colab.

---

## Context: what broke in 07, and why 08 likely has the same problem

`build_feature_matrix` (07) and `build_feature_matrix`/`build_omics_matrix` (08)
share the same pattern: `OMICS[arm].loc[sub[COL_CELLOSAURUS]]` expands a cell
line's full omics row **once per drug pair**, not once per cell line. With
~140,957 train pairs and the *full, unreduced* column widths:

- RNA: 17,738 genes → ~140,957 × 17,738 × 4 bytes ≈ **11.1 GB**, RNA arm
- Protein: 6,692 proteins → ~140,957 × 6,692 × 4 bytes ≈ **4.9 GB**, protein arm

...materialized **before** any top-K feature selection ever ran. That's what
crashed RandomForest in notebook 07, both locally and on Colab. The fix there:
select top-variance genes/proteins from the **compact per-cell-line table**
first (≤836 rows, not duplicated per pair), then only ever expand the
*already-reduced* columns out to per-pair rows. RandomForest is confirmed
running successfully on real data with this fix as of the end of this session.

Notebook 08's `fit_predict_simple_nn` and `fit_predict_drug_gnn` call
`select_top_variance_columns` **after** building the full matrix — same bug,
unconfirmed whether it's been hit yet (no real run completed there this
session). Drug fingerprint concatenation in `SimpleNeuralNetwork`'s feature
builder doubles down on this the same way 07's RF/XGBoost did.

---

## Tasks (in order)

**Task 1: Port the feature-selection-before-expansion fix to notebook 08**
- Add a `select_top_variance_genes(arm, cell_line_ids, k)` helper (identical
  logic to notebook 07's) operating on the unique-cell-line table.
- Update `build_feature_matrix` (SimpleNeuralNetwork path — omics + fingerprint
  concatenated) and `build_omics_matrix` (DrugGNN path — omics only, drug kept
  separate as a graph) to accept a pre-selected gene/protein list, same as 07.
- Update `fit_predict_simple_nn` and `fit_predict_drug_gnn` to compute the
  selected gene list once per call (on `train_inner_idx`'s cell lines, like 07
  does on `train_idx`/`train_inner_idx`), before building any matrix.

**Task 2: Fix missing NaN handling**
- Confirmed gap (applies to both 07 and 08): omics CSVs are loaded with no
  `fillna` at all, only index-deduped. Add `rna = rna.fillna(0)` /
  `protein = protein.fillna(0)` right after the dedup lines in notebook 08's
  load cell (07 should already have this from this session — verify it
  actually landed, don't assume).
- Decision already made: flat zero-fill, matching the project's Session 2
  choice (BDRN paper justification) — not drevalpy's median-center +
  downshifted-normal imputation. Revisit only if asked.

**Task 3: Check GPU-memory-specific risks unique to the DL path**
- `train_simple_nn`/`train_drug_gnn` move `X_val`/`y_val` to `DEVICE` in one
  shot and run a single full-batch forward pass for validation each epoch —
  fine on CPU, but on a memory-constrained Colab GPU this could spike VRAM
  independently of system RAM, even after the Task 1 fix. Consider chunking
  the validation forward pass if `DEVICE.type == "cuda"` and validation set is
  large.
- `DrugGNN`'s `batch_size` defaults to 1024 (matches drevalpy) — confirm this
  is still reasonable after the Task 1 fix, lower if needed.

**Task 4: Mirror notebook 07's other recent additions onto 08, if not already present**
- `SAVE_PREDICTIONS_FOLDS` (only persist raw prediction CSVs for fold 0, full
  metrics still logged to `summary.csv` for every fold) — added to 07 this
  session for disk space; confirm whether 08 already has it or needs porting.
- Locally-scoped `warnings.catch_warnings()` around `pearsonr` calls — 08
  already has this per this session's earlier edit, just confirm it survived
  any later changes.

**Task 5: Real end-to-end run**
- Run notebook 08 on real data (local or Colab) for at least one split/fold to
  confirm no crash, sane non-degenerate outputs, and reasonable per-epoch
  timing via the progress printing already in place.

---

## Carried forward, not blocking Session 5 unless time allows

- **Task 4 from Session 4 (consolidation)** — still not built. Needs a real
  `summary.csv` from both notebook 07 and notebook 08 to consolidate against;
  do this once 08 is confirmed working.
- **DIPK** — still an open scope decision (no notebook 09 started). ~1,100
  lines upstream, needs BIONIC network features this project doesn't have a
  pipeline for. Revisit only if explicitly requested.
- **`05_baselines_local.ipynb` / `06_baselines_gpu.ipynb`** (the original
  drevalpy-harness notebooks) — orphaned by the pivot to 07/08. Still useful
  as outside context (maps to the published DrEval leaderboard style) but
  can't isolate RNA vs protein vs fusion the way 07/08 do. No action needed
  unless you want that outside-context comparison.
- **Feature selection criterion** — currently variance-based (07/08 both).
  drevalpy itself uses completeness-based selection for protein
  (`feature_threshold=0.7`, fallback top-1000-most-complete) and a fixed
  curated landmark gene list for RNA (not variance-driven for either). Flagged
  as a real deviation, not yet changed — your call whether to revisit.

---

## Key numbers worth keeping handy

- Train pairs (LCO fold 0, real data): 140,957 train / 35,259 test (approx.,
  varies slightly per split type/fold)
- Drug fingerprint width: 2048 (fixed)
- RNA width: 17,738 genes (`gene_expression.csv`)
- Protein width: 6,692 proteins (Session 3's QC-filtered ProCan subset)
- `TOP_K_FEATURES = 1000` (current default, same for both arms) — post-fix
  matrix size for either arm: ~140,957 × 3048 × 4 bytes ≈ 1.7 GB
