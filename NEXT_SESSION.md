# NEXT SESSION
## Multimodal Drug Response Prediction — Relationship Analysis Phase

---

## Context: What Happened This Session

This session was a strategic planning session — no new code was written. Key decisions made:

**Scientific reframing:** The project's contribution is no longer framed as "can fusion beat RNA-alone?" (answered: no, at this scale). The new framing is: **study the relationships between RNA and protein, and between omics and drug response**, to understand *why* and *how* these modalities interact to produce drug sensitivity outcomes.

**Key insight agreed on:** Prediction accuracy is the wrong objective when modalities are causally linked (RNA → protein). The scientifically valuable signal lives in the *deviations* — where protein diverges from what RNA predicts — and in *how those deviations are drug-relevant*.

**Future dataset identified but deferred:** TCGA-BRCA (RNA + RPPA protein + clinical: age, race, stage, survival) via UCSC Xena (`https://xenabrowser.net/datapages/`) or LinkedOmics (`http://linkedomics.org/data_download/TCGA-BRCA/`). Do NOT start this yet — finish current dataset first.

---

## Current State

- **Notebooks completed:** nb01–nb14
- **Data on disk:** GDSC2 drug response + CCLE RNA-seq + ProCan proteomics (~836 cell lines, 287 drugs, 6,692 proteins)
- **Key saved artifact from nb14:** PCA residuals saved to disk — RNA-protein cross-modal correlation r=−0.03 after IC50-correlation-based feature selection on residualized data. **Load these at the start of nb15, do not recompute.**
- **Environment:** WSL2 local machine, Colab kernel (not local Python), conda `multiomics` env

---

## What To Do This Session: nb15

**Goal:** Characterize the structure of RNA-protein deviations across cell lines and genes.

### Step 1 — Load saved residuals (do not recompute)
```python
# Load PCA residuals saved from nb14
# protein_residuals: (n_cell_lines, n_genes) — protein expression unexplained by RNA
# Confirm shape and check for NaNs
```

### Step 2 — Per-gene deviation characterization
For each gene in the aligned RNA-protein set:
- Fit linear model: `protein ~ RNA` across cell lines
- Residual = deviation from RNA-predicted protein level
- Save: slope, intercept, R², residual std per gene
- This gives you a "predictability score" per gene — low R² = protein is independent of RNA for that gene

### Step 3 — Cluster genes by deviation pattern
- Use the residual matrix (cell lines × genes) 
- Cluster genes by their deviation profiles across cell lines (k-means or hierarchical, k=5–8)
- Check: do clusters correspond to known gene families or biological processes? (expect: kinases, membrane proteins, secreted proteins to deviate more)
- Plot: heatmap of top-deviation genes × cell lines, annotated by tissue type

### Step 4 — Tissue-of-origin stratification
- Split cell lines by tissue (blood vs solid, or by cancer type)
- For each tissue group: compute median RNA-protein correlation per gene
- Find genes where deviation is tissue-specific vs universal
- This tells you whether post-transcriptional dysregulation is cancer-type-specific

### Step 5 — Identify "high-deviation, high-predictive" genes
- Cross-reference with IC50-correlation features from nb14
- Find genes where: (a) protein deviates strongly from RNA prediction AND (b) protein level correlates with drug response
- These are the most biologically interesting genes — protein under independent regulatory control AND clinically relevant

---

## Notebook nb16 (plan for session after nb15)

**Goal:** Link RNA-protein deviations to drug response.

- For each drug × gene pair: correlate residual (protein - RNA-predicted protein) with LN_IC50
- Rank gene-drug pairs by this deviation-IC50 correlation
- Compare: does the deviation signal predict response better than RNA alone for top pairs?
- Output: ranked table of gene-drug pairs where deviation matters

---

## Notebook nb17 (plan for two sessions from now)

**Goal:** Drug-specific RNA-protein coupling.

- Split cell lines into sensitive vs resistant per drug (median LN_IC50 split)
- In each group: compute RNA-protein Pearson r per gene
- Find genes where coupling differs between sensitive and resistant (large delta r)
- These are candidates where the RNA→protein regulatory axis is disrupted specifically in the drug response context

---

## Code Style Reminders

- One run cell per model arm — no shared loops
- No print statements inside functions — use return values
- No hardcoded paths — use constants at top of notebook
- Suppress Python warnings at top: `import warnings; warnings.filterwarnings('ignore')`
- Report results as mean ± std where applicable
- Deduplication check: always deduplicate on cellosaurus_id immediately after loading any CSV

---

## Do NOT Do This Session

- Do not touch TCGA data — deferred to future session
- Do not re-run nb14 or recompute PCA residuals — load from disk
- Do not add new modalities (CNV, methylation) — out of scope
- Do not revisit prediction accuracy framing — the question is relationships, not accuracy
- Do not re-discuss dataset choices

---

## Pitch Context (keep in mind for framing results)

Target: Turbine Research Lab (TRAIL), addressing their open Problem 2 (Multimodal Synergy).

Narrative: *We showed naive fusion fails. We identified why (modality redundancy from RNA→protein causal coupling). We now characterize where the coupling breaks down, which genes are under independent post-transcriptional regulation, and whether those deviations are drug-relevant. This is the correct multimodal question.*

Results from nb15–nb17 should feed directly into this narrative.
