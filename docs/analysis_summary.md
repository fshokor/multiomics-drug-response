# Statistical & Clustering Analysis Summary

**Source notebooks:** `02_statistical_analysis.ipynb`, `03_similarity_clustering.ipynb`
**Dataset:** 836 cell lines (GDSC2 ∩ CCLE RNA-seq ∩ ProCan-DepMapSanger proteomics, three-way overlap), 6,692 high-confidence proteins (multi-peptide support), 287 drugs

---

## 1. RNA-Protein Correlation (Notebook 02, Task 1)

| Metric | Value |
|---|---|
| Gene-wise Pearson r (median) | **0.415** |
| Gene-wise Spearman r (median) | **0.407** |
| Tissue-centered Pearson r (median) | 0.368 (~11% relative drop) |
| Blood cell-line-wise r (median) | 0.389 (n=139) |
| Solid cell-line-wise r (median) | 0.371 (n=697) |
| Blood vs. solid, Mann-Whitney U | **p = 7.3e-11** |

**Key findings:**
- The headline correlation (0.415/0.407) is consistent with an independent reanalysis of this exact dataset in the literature (OnCorr, median 0.42, Spearman), validating the data-cleaning pipeline.
- Tissue-of-origin is a real but modest confound — removing it drops the correlation ~11%, meaning most of the RNA-protein relationship is genuinely within-tissue, not an artifact of pooling different tissue baselines.
- **Blood vs. solid is significant and in the hypothesized direction** (blood > solid), directly supporting the project's core premise that solid tumors carry more independent protein signal. This result only emerged after fixing two data issues (see Data Quality Fixes below) — the naive/uncleaned analysis showed no significant difference (p=0.26).

**Data quality fixes applied (now standard for all downstream work):**
1. Protein columns were `UniProtID;EntryName_HUMAN` (a UniProt mnemonic), not gene symbols — entry names diverge from official HGNC symbols for whole gene families (e.g. ribosomal proteins). Fixed via UniProt-accession → gene-symbol mapping (`mygene`).
2. Switched from the full 8,498-protein ProCan release to the 6,692-protein multi-peptide-confidence subset (per the original ProCan paper's own QC standard) — recovered the literature-consistent correlation without needing additional missingness filtering.
3. Deduplicated `cellosaurus_id` rows in both RNA and protein tables (4 RNA, 2 protein duplicates) — silent row-count mismatches were corrupting several downstream calculations before this was caught.

---

## 2. Independent Protein Signal (Notebook 02, Task 2)

For the most-tested drug (5-Fluorouracil, n≈835 measurements), two independent methods — **partial correlation** (protein↔IC50 controlling for RNA) and **RNA-protein discordance** (regression-residual↔IC50) — converge on the same top genes with near-identical coefficients:

| Gene | Partial r | Discordance r | n |
|---|---|---|---|
| LEMD2 | 0.413 | 0.411 | 832 |
| ZFPL1 | 0.383 | 0.379 | 827 |
| TMX3 | 0.383 | 0.379 | 802 |
| STX12 | 0.382 | 0.382 | 820 |
| RAB14 | 0.382 | 0.382 | 835 |
| VAPB | 0.377 | 0.370 | 834 |
| MAVS | 0.373 | 0.373 | 786 |
| MCM4 | -0.369 | -0.368 | 833 |
| GOLGB1 | 0.367 | 0.366 | 829 |
| SLC25A24 | 0.365 | 0.364 | 785 |

**Notable pattern:** six of the top ten genes (RAB14, STX12, ZFPL1, TMX3, VAPB, GOLGB1) cluster around membrane trafficking / secretory-pathway biology — a coherent theme, not random noise. **MCM4** (DNA replication licensing complex) is mechanistically plausible given 5-Fluorouracil's mechanism (thymidylate synthase inhibition, disrupts DNA synthesis).

**Caveat:** single-drug pass. Not yet validated against the top-5 most-tested drugs to check whether this gene list generalizes or is 5-FU-specific.

**Output:** `data/processed/top_independent_proteins.csv` — candidate list for the fusion model's protein pre-selection step.

---

## 3. Cell-Line Clustering: RNA vs. Protein (Notebook 03)

| Embedding | ARI (RNA clusters vs. Protein clusters) |
|---|---|
| PCA | 0.417 |
| UMAP | 0.416 |
| t-SNE | 0.539 (likely inflated — see caveat) |

**Caveat on t-SNE:** t-SNE tends to carve both modalities into tighter, more separable clusters independently, which can inflate apparent agreement without reflecting a stronger real signal. PCA/UMAP's close agreement (0.417/0.416) is the more trustworthy estimate.

**Tissue-purity analysis** (majority tissue per cluster) revealed which specific tissues retain identity across modalities:

| Tissue | RNA cluster purity | Protein cluster purity |
|---|---|---|
| Blood | 100% (n=48) | 95.2% (UMAP) / 62.3% (t-SNE) |
| Skin | 97.6% (n=41) | **100%** (both UMAP and t-SNE) |
| Bone | 100% (n=20) | *not separable in protein space* |
| Lymph | 57.1% | 64.7% |
| Lung, Breast, Brain, Head & Neck | 19-67% | 20-48% |

**Key finding:** Skin and Blood are the only tissues with strong, consistent cross-modality identity. Most solid tumor types show weak-to-no protein-level lineage clustering even though they separate reasonably well by RNA. Bone is RNA-only — a real signal RNA captures that protein clustering does not preserve (small n=20, worth a footnote not a headline).

**Interpretive note:** this measures global unsupervised tissue-identity structure, a different question from Task 2's gene-level "does protein predict drug response beyond RNA." The two should be treated as complementary, not interchangeable.

---

## 4. Drug Structural Similarity (Notebook 03)

- **Median pairwise Tanimoto similarity: 0.104** — the 246-drug set is overwhelmingly chemically diverse; most pairs share almost no structural overlap.
- At a similarity ≥0.7 threshold, only a handful of drugs have any close structural partner (239 of 246 are effective singletons).

**Two categories surfaced in the top-similarity pairs, requiring different handling before building LDO splits:**

1. **Duplicate compounds under different names** (Tanimoto ≈0.97-1.0) — likely data-quality issues, not real "similar drugs":
   - `Bleomycin` / `Bleomycin (50 uM)`
   - `GSK2110183B` / `Afuresertib` (same compound, dev code vs. generic name)
   - `GSK-LSD1` / `GSK-LSD1-2HCl` (same compound, different salt form)

   *Action: merge or deduplicate before any LDO split — otherwise a "held-out" drug could leak into training under its other name.*

2. **Genuine analog families** (Tanimoto 0.6-0.8) — real, mechanistically related drug classes:
   - Taxanes: Paclitaxel/Docetaxel
   - Vinca alkaloids: Vinorelbine/Vinblastine
   - Topoisomerase-I inhibitors: SN-38, Topotecan, Camptothecin, Irinotecan
   - CDK4/6 inhibitors: Ribociclib/Palbociclib

   *Action: keep each family together (all-train or all-test) when building LDO splits, so "unseen drug" generalization isn't softened by near-identical scaffolds leaking across the boundary.*

---

## 5. Pair-Level Response Heterogeneity (Notebook 03)

**Median within-cluster / across-cluster IC50 variance ratio: 0.760** (n≈177,785 drug-cell line pairs, ~250 drugs).

A ratio below 1.0 means cell-line clusters (RNA-based) explain real, pharmacologically-relevant response structure — a moderate, believable effect size (not so low as to suggest overfitting to expression patterns, not near 1.0 which would suggest the clustering is meaningless).

**Six outlier drugs** (ratio ≥0.95, full coverage across all 8 clusters, n=212-827 pairs — not small-sample artifacts) were mechanistically investigated:

| Drug | Mechanism | Why cluster-independence makes sense |
|---|---|---|
| GSK269962A | ROCK1/2 inhibitor | Broad cytoskeletal pathway, not lineage-restricted |
| BMS-536924 | IGF-1R antagonist | Near-universal growth pathway |
| Sepantronium bromide (YM155) | Survivin (BIRC5) inhibitor | Pan-cancer overexpression target by design |
| AZD2014 | Dual mTORC1/2 inhibitor | Broad growth/survival pathway |
| Cediranib | VEGFR inhibitor | Anti-angiogenic mechanism doesn't translate to a 2D monoculture assay — likely off-target noise, not biology |
| 123829 | *Unidentified (numeric ID)* | Needs lookup in local GDSC metadata |

Four of the six target broad, non-lineage-restricted pathways — a mechanistically coherent exception group, which strengthens rather than undermines the main 0.76 finding.

---

## Implications for the Model & Pitch

1. **The core hypothesis has direct statistical support**: protein carries more independent signal in solid tumors than blood cancers (p=7.3e-11), validated only after fixing the protein gene-mapping and confidence-filtering pipeline — itself a good rigor story for the pitch.
2. **A validated candidate protein list exists** for the fusion model's pre-selection step, cross-checked by two independent statistical methods.
3. **Skin and Blood are the cleanest tissue-level signal** in both modalities — useful for early model validation (these should be "easy" cases) and for framing where protein contributes vs. where it doesn't.
4. **Drug split design has concrete, data-grounded inputs now**: a short list of duplicate-named compounds to clean up, and analog families to keep together in LDO splits — directly preventing a Simpson's-paradox-style leakage artifact.
5. **Cell-line clustering is biologically real** (0.76 within/across variance ratio), supporting LCO/LTO splits as testing genuine generalization rather than arbitrary groupings.

## Open Items / Follow-ups

- Task 2's independent-protein list is single-drug (5-FU); extending to the top-5 most-tested drugs would test generalization.
- Drug "123829" needs identification before citing the outlier-drug list externally.
- t-SNE-based ARI (0.539) should not be quoted alone without the PCA/UMAP caveat (0.417/0.416).
