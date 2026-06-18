# Next Session Tasks
## Session 3 — Statistical Analysis and Baselines

---

## Goal
Understand the data before touching the model. Run baselines. Confirm we can
reproduce drevalpy benchmark numbers under LCO.

---

## Tasks (in order)

**Task 1: RNA-protein correlation analysis**
- Load gene_expression.csv and proteomics.csv
- Find common genes (gene symbols appear in both)
- Compute per-gene Pearson r between RNA and protein across cell lines
- Expected median ~0.44
- Plot distribution — this is Figure 1 of the paper

**Task 2: Which proteins are most independent from RNA?**
- Low RNA-protein r = protein carries unique information
- High protein-IC50 r = protein is predictive of drug response
- These are the proteins our cross-attention should learn to weight highly
- Save top-K independent proteins list

**Task 3: Run drevalpy baselines under LCO**
- NaiveDrugMeanPredictor
- ElasticNet (gene expression)
- RandomForest (gene expression)
- Use drevalpy's drug_response_experiment() API
- Record Pearson r — these are the numbers to beat

**Task 4: Implement LCO split logic**
- Use drevalpy's split_dataset() to generate LCO splits
- Save to data/splits/ as JSON for reproducibility
- Verify: no cell line in both train and test

---

## Context
- See PLAN.md → Week 2 for full code
- Working dataset: 836 cell lines × 287 drugs × 204,931 pairs
- Primary metric: Pearson r under LCO
- Expected baseline Pearson r under LCO: ~0.3–0.4
