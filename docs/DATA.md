# Data

## Sources

- **GDSC2** — drug response (`LN_IC50`)
- **CCLE RNA-seq** — gene expression
- **ProCan-DepMapSanger proteomics** — QC-filtered, multi-peptide-confidence subset
- **ChEMBL / RDKit** — drug SMILES → Morgan fingerprints + molecular graphs

Universal cell line key across all sources: `cellosaurus_id`.

## Dimensions (confirmed from real data)

| Item | Size |
|---|---|
| Three-way overlap (RNA ∩ protein ∩ GDSC2) | 836 cell lines |
| Drugs (valid SMILES) | 244 |
| Tissues | 26 |
| Response pairs (cell line in overlap, drug has SMILES, IC50 not null) | 176,197 |
| RNA features | 17,738 genes |
| Protein features | 6,692 proteins |
| Drug fingerprint | 2,048 bits (Morgan, radius=2) |
| Drug graph | molecular graph, atom-level node features, GCNConv-ready |

## Missing data

Omics NaNs are flat zero-filled (`fillna(0)`) — not mean/median imputed. Deliberate choice, applied right after loading, before any feature selection.

## Splits

One shared **train** set per fold, four **test** sets representing different generalization axes — not four independent train/test partitions.

Per fold:
1. Independently hold out 10% of cell lines, 10% of drugs, 10% of tissues (`GroupShuffleSplit`).
2. **LCO test** / **LDO test** / **LTO test** = every pair touching that axis's held-out group. No purity rule — a pair with both a new cell line and a new drug lands in both test sets.
3. **LPO test** = a random sample over *all* pairs (not restricted to the untouched remainder), sized at 2× the mean size of the other three test sets — deliberately mixes nothing-new / partially-new / fully-new pairs.
4. **Train** = pairs touching none of the three held-out groups, minus whatever got sampled into LPO test.

5 folds, seed 42. Typical fold sizes:

| Test set | Size | Composition |
|---|---|---|
| Train | ~95,000–101,000 (~54–57%) | — |
| LCO test | ~17,500–18,500 | mostly pure (cell line is the only new thing) |
| LDO test | ~17,500–18,500 | mostly pure |
| LTO test | ~13,500–35,000 (high variance — only 26 tissues exist, sizes very uneven) | mostly pure |
| LPO test | ~33,000–48,000 | mix of nothing-new / one-axis-new / compound |

Saved to `data/splits/`:
- `splits.json` — one entry per fold: `train`, `lco_test`, `ldo_test`, `lto_test`, `lpo_test` (row indices into `response_pairs.parquet`)
- `holdout_groups.json` — which specific cell lines / drugs / tissues were held out per fold (entity IDs, for interpreting results later — e.g. attributing a fold's LTO performance to which tissues landed in it)
