# NEXT SESSION
## Multiomics Relationship Modeling — NeurIPS 2021 Single-Cell Dataset

---

## Context: What Changed This Session

**Full strategic pivot.** The GDSC2/CCLE/ProCan dataset (~836 cell lines) is too small
for DL to learn relational structure between modalities. The project reframes entirely:

**Old question:** Can RNA+protein fusion beat RNA-alone for drug response prediction?
**New question:** What is the structure of the relationship between omics layers,
and where and why does it break down?

**New dataset:** NeurIPS 2021 Multimodal Single-Cell Integration benchmark
- CITE-seq: RNA + protein (ADT) measured simultaneously in the same cell (~66–81K cells)
- Multiome: RNA + ATAC (chromatin accessibility) measured simultaneously
- 10 healthy human donors, bone marrow cells
- Freely available, no application needed
- Format: h5ad (AnnData) — standard scanpy format

**Why single-cell:** RNA and protein are co-measured in the SAME cell at the SAME time.
No tissue composition confound. Clean causal axis. Scale sufficient for DL.

**GDSC project:** Parked. Do not delete. May return for drug response angle later.

---

## Download Links

**Primary — GEO (raw h5ad files):**
`https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE194122`

**Alternative — competition page:**
`https://openproblems.bio/events/2021-09_neurips`

**Files to download:**
- CITE-seq: `GSE194122_openproblems_neurips2021_cite_gex_processed_training.h5ad`
  → RNA modality (GEX), ~70K cells
- CITE-seq: `GSE194122_openproblems_neurips2021_cite_adt_processed_training.h5ad`
  → Protein modality (ADT), same cells
- Multiome: `GSE194122_openproblems_neurips2021_multiome_gex_processed_training.h5ad`
  → RNA modality
- Multiome: `GSE194122_openproblems_neurips2021_multiome_atac_processed_training.h5ad`
  → ATAC modality (chromatin accessibility)

**Environment:** WSL2, Colab kernel

---

## This Week's Goal

Study the relationships between omics layers at single-cell resolution:
1. **RNA ↔ Protein** (CITE-seq): where does the RNA→protein relationship hold,
   where does it break down, and is that breakdown cell-type-specific?
2. **RNA ↔ ATAC** (Multiome): how does chromatin accessibility relate to
   gene expression, and which genes are most/least regulated by accessibility?

These are two parallel tracks, one notebook each, same analytical logic.

---

## Notebook Plan

### nb01_neurips — Data Download & QC
**Goal:** Load both datasets, run QC, understand structure.

```python
# Key imports
import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Load CITE-seq RNA
cite_rna = sc.read_h5ad('data/cite_gex_training.h5ad')
print(cite_rna)         # n_obs × n_vars
print(cite_rna.obs)     # cell metadata: donor, cell type, batch, site
print(cite_rna.var)     # gene metadata

# Load CITE-seq Protein
cite_adt = sc.read_h5ad('data/cite_adt_training.h5ad')
print(cite_adt)         # same cells, ~140 surface proteins

# Load Multiome RNA
multi_rna = sc.read_h5ad('data/multiome_gex_training.h5ad')

# Load Multiome ATAC
multi_atac = sc.read_h5ad('data/multiome_atac_training.h5ad')
```

**QC checks per dataset:**
- Cell count and feature count per donor
- % mitochondrial reads (RNA)
- Distribution of total counts per cell
- Confirm cell barcodes match between modality pairs
- Check obs columns: donor_id, cell_type, batch, site

**Output:** QC report, confirmed cell-barcode alignment between paired modalities

---

### nb02_neurips — RNA-Protein Relationship (CITE-seq)
**Goal:** Characterize the RNA→protein relationship at single-cell resolution.

**Step 1 — Identify overlapping features**
```python
# Find genes measured in both RNA and protein
# ADT proteins are surface proteins (CD markers etc.)
# Map ADT names to gene symbols
# Expected overlap: ~100-140 genes with both RNA and protein measured
common_genes = set(cite_rna.var_names) & set(cite_adt.var_names)
```

**Step 2 — Per-gene RNA-protein correlation**
- For each gene in the overlap: Pearson r between RNA and protein across all cells
- Expected: wide distribution, median ~0.3–0.5 (lower than bulk due to noise)
- Plot: histogram of per-gene correlations
- Identify: top 20 most coupled, top 20 most independent genes

**Step 3 — Cell-type stratification (KEY ANALYSIS)**
- Split cells by annotated cell type (T cells, B cells, NK cells, monocytes etc.)
- For each cell type × gene: compute RNA-protein correlation
- Find genes where coupling is:
  - High in one cell type, low in another (cell-type-specific regulation)
  - Universally coupled (housekeeping translation)
  - Universally independent (post-transcriptional regulation)
- Plot: heatmap of gene × cell type RNA-protein correlations

**Step 4 — Donor effect**
- Compute RNA-protein correlation per gene per donor
- Are the coupling patterns consistent across the 10 donors?
- High inter-donor consistency = biological signal, not technical noise

**Step 5 — Deviation characterization**
- Fit linear model: `protein ~ RNA` per gene across cells
- Residual = deviation from RNA-predicted protein level
- For each cell: compute mean absolute deviation across all genes
- Do certain cell types show systematically higher deviation?
- This is the single-cell analog of your GDSC analysis

**Output:** 
- Per-gene coupling score (R²) across cell types
- Ranked list: most/least predictable proteins from RNA
- Deviation score per cell, annotated by cell type

---

### nb03_neurips — RNA-ATAC Relationship (Multiome)
**Goal:** Characterize the chromatin accessibility → gene expression relationship.

**Step 1 — Feature linkage**
- ATAC peaks need to be linked to genes (peaks within gene body or promoter ±2kb)
- Use pybedtools or snapatac2 for peak-to-gene linkage
- Expected: each gene linked to 1–20 ATAC peaks

**Step 2 — Per-gene ATAC-RNA correlation**
- For each gene: correlate its promoter accessibility (ATAC) with its expression (RNA)
- Expected: weaker correlation than RNA-protein (~0.2–0.4)
- This is because chromatin accessibility is necessary but not sufficient for expression
- Plot: histogram of per-gene ATAC-RNA correlations

**Step 3 — Cell-type stratification**
- Same analysis as nb02 but for ATAC-RNA
- Find genes where accessibility-expression coupling is cell-type-specific
- These are genes under active regulatory control in specific lineages

**Step 4 — Compare RNA-Protein vs RNA-ATAC relationship structure**
- Which genes are coupled in both modality pairs?
- Which genes are coupled in one but not the other?
- This reveals: genes regulated at the chromatin level vs post-transcriptional level

**Output:**
- Per-gene ATAC-RNA correlation across cell types
- Comparison table: RNA-protein vs RNA-ATAC coupling per gene

---

### nb04_neurips — Joint Relationship Model (DL)
**Goal:** Train a DL model to learn the relationship structure, not predict accuracy.

**This is NOT a prediction task. The model is an analysis tool.**

**Architecture: Variational Autoencoder (VAE) with two encoders**
```python
# Two modalities → shared latent space → per-modality decoder
# The latent space captures shared structure
# The reconstruction error captures modality-specific signal

class MultimodalVAE(nn.Module):
    def __init__(self, rna_dim, adt_dim, latent_dim=32):
        # Encoder 1: RNA → latent
        # Encoder 2: ADT → latent
        # Shared latent space (mean + logvar)
        # Decoder 1: latent → RNA reconstruction
        # Decoder 2: latent → ADT reconstruction
```

**What to extract from the trained model:**
- Latent representation per cell → does it separate cell types cleanly?
- Per-gene reconstruction error → genes hard to reconstruct = independently regulated
- Cross-modal prediction: RNA encoder → ADT decoder (RNA→protein prediction)
- Attention/gradient weights: which RNA features most predict which proteins?

**Comparison baseline:**
- Linear regression (RNA → protein per gene) — already done statistically in nb02
- VAE should capture non-linear relationships that linear misses
- If VAE doesn't outperform linear: relationship is linear, DL adds nothing
- This is a valid scientific finding either way

**Scale:** 66K cells is sufficient for a small VAE (latent_dim=32, hidden=256)
Run on Colab GPU — should train in <30 minutes

**Output:**
- Latent space UMAP colored by cell type, donor, coupling score
- Per-gene reconstruction error (RNA→protein direction)
- Ranked list: genes where VAE outperforms linear (non-linear regulation signal)

---

## Key Scientific Questions To Answer This Week

By end of week, you should be able to answer:

1. **Is the RNA-protein relationship linear or non-linear at single-cell resolution?**
   (nb02 statistical + nb04 VAE comparison)

2. **Is post-transcriptional regulation cell-type-specific or universal?**
   (nb02 Step 3)

3. **Are chromatin accessibility and expression coupled the same way as RNA and protein?**
   (nb03 vs nb02 comparison)

4. **Which genes are regulated at chromatin level vs post-transcriptional level?**
   (nb03 Step 4)

5. **Can a shared latent space capture both RNA and protein simultaneously?**
   (nb04 VAE latent space analysis)

---

## Technical Notes

**AnnData structure:**
```python
adata.X          # expression matrix (cells × genes), often sparse
adata.obs        # cell metadata (donor_id, cell_type, batch, site)
adata.var        # feature metadata (gene names, highly variable flags)
adata.obsm       # embeddings (PCA, UMAP)
adata.obsp       # graphs (connectivities, distances)
```

**Preprocessing already done in h5ad files:**
- Library size normalization
- Log transformation
- Highly variable gene selection (for RNA)
- Check `adata.uns` for preprocessing details before re-normalizing

**Cell type annotations:**
- Should be in `adata.obs['cell_type']` or similar column
- If not present: run leiden clustering + marker gene annotation
- Bone marrow cell types expected: HSC, progenitors, T cells, B cells, NK cells, monocytes, dendritic cells

**ATAC-specific:**
- ATAC data is peak × cell matrix (binary or count)
- Peaks need genomic coordinates (in `adata.var`)
- Use gene activity scores as a first approximation before peak-to-gene linkage

**Memory:** h5ad files can be large (~2–5GB each). Load with `backed='r'` if memory constrained:
```python
adata = sc.read_h5ad('file.h5ad', backed='r')
```

---

## Do NOT Do This Week

- Do not revisit GDSC/CCLE/ProCan data
- Do not frame results as prediction accuracy — frame as relationship structure
- Do not chase SOTA performance — the VAE is an analysis tool, not a benchmark entry
- Do not add more datasets (TCGA, CPTAC) — NeurIPS dataset is sufficient for this week
- Do not work on the Genopole Shaker application — separate task, separate session

---

## Broader Context (keep in mind)

**Genopole Shaker application deadline: July 15, 2026** — two weeks away.
Results from this week's analysis will feed directly into the application narrative.
The pitch: *computational platform for understanding multi-omics regulatory relationships,
with single-cell resolution, identifying where RNA-protein and RNA-ATAC coupling
breaks down across cell types — foundation for biomarker discovery.*

**TCGA-BRCA dataset** (RNA + RPPA + clinical) identified as next dataset after this week.
Links saved: `https://xenabrowser.net/datapages/` and `http://linkedomics.org/data_download/TCGA-BRCA/`

**GDSC project parked** — nb01–nb17 complete, results saved. Core finding: naive fusion
fails at 836 cell lines, relationship signal exists in RNA-protein deviation.
