# Next Session Tasks
## Session 4 — Baselines and Splits

---

## Goal
Get real baseline numbers running on this dataset under all four DrEval split types, and
generate/save reusable split indices. This is the deferred Task 3-4 from Session 3's
original plan (statistical analysis ran long and expanded scope — see
`results/analysis_summary.md` for what got covered instead).

---

## Tasks (in order)

**Task 1: Generate and save all four splits**
- Use drevalpy's split logic to generate LPO, LCO, LDO, **and LTO** (not just LCO/LPO as
  originally scoped — LTO was added in Session 3 as a 4th split type)
- Save to `data/splits/` as JSON for reproducibility
- Verify: no cell line in both train and test (LCO/LTO), no drug in both (LDO)
- Confirm whether `drug_response_experiment()`'s `test_mode` param accepts a list
  (`["LPO","LCO","LDO","LTO"]`) directly, or needs four separate calls — check before
  writing the run loop

**Task 2: Run lightweight baselines locally (CPU, Jupyter, no Colab needed)**
- `NaiveTissueDrugMeanPredictor`, `RandomForest`, `MultiViewXGBoost` — all in
  `drevalpy.models.MODEL_FACTORY`, called by name string, no reimplementation
- Run under all four splits
- `RandomForest` (gene-expression-only) is the primary baseline to beat; `MultiViewXGBoost`
  is secondary context with a different omics mix (CNV+methylation+mutation, NOT protein —
  see Key Decisions in `SESSION_MEMORY.md`)

**Task 3: Run GPU baselines on Colab**
- `DIPK`, `DrugGNN`, `SimpleNeuralNetwork` — same `MODEL_FACTORY` pattern, but these train
  per-fold with early stopping and a hyperparameter search, so budget real compute time
- Suggest sanity-checking runtime on a single split (LCO) before kicking off all four
- Mount Drive, save results back for comparison with the local run

**Task 4: Consolidate results**
- One table: model × split × Pearson r (and RMSE), all on the same test folds
- Compare against the DrEval Challenge Leaderboard numbers from the CTRPv2 image
  (different dataset, so not a direct comparison — context only, not a target to hit)

---

## Context
- See `PLAN.md` → Week 2 Day 8-10 for original baseline code sketches (NaiveMeanPredictor,
  RNARandomForest classes) — superseded by calling drevalpy's built-in models instead of
  reimplementing
- `results/analysis_summary.md` has the full Session 3 findings if any baseline result
  looks like it needs a sanity check against the stats/clustering work (e.g. does
  `RandomForest`'s LTO performance look consistent with the blood-vs-solid correlation
  difference found in notebook 02?)
- Working dataset: 836 cell lines × 287 drugs (three-way overlap, GDSC2 ∩ CCLE ∩ ProCan)
- Primary metric: Pearson r under LCO; LTO is the second priority given Session 3's
  blood-vs-solid result
