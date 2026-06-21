# Multimodal Integration — Plan & Ideas

## Hypothesis

RNA and protein are weakly correlated (~0.42 gene-wise, ~0.54 cell-line-wise) — partially independent biological signal. Naive concatenation is documented to fail (DrEval, Turbine) because it lets one modality dominate, introduces redundant features, and never explicitly models where the two modalities disagree. Cross-attention fusion should let the model learn which proteins diverge from their RNA counterpart and weight them accordingly.

## Build order

**1. Single-modality baselines** (cheap, fast, no fusion question yet — isolates how much signal each input carries alone):
- RNA only (no drug input)
- Protein only (no drug input)
- Drug fingerprint only (no omics)
- Drug graph only (no omics)

**2. Two-modality pairs** (omics + drug):
- RNA + drug fingerprint / RNA + drug graph
- Protein + drug fingerprint / Protein + drug graph

**3. Three-modality naive concatenation** (RNA + protein + drug, both drug encodings) — the documented failure-mode baseline that motivates everything below.

**4. Fusion architectures** — the actual research contribution.

## Fusion strategies — cost vs. value

| Strategy | What it does | Cost | Status |
|---|---|---|---|
| Naive concatenation | Flat concat of (top-K) RNA + protein + drug | Free | Baseline, expected to underperform |
| Projected-then-concat | Each modality → MLP → same-dim embedding, then concat | Cheap (reuses planned `OmicsEncoder`) | Add as a control — isolates whether any gain comes from attention itself vs. just having learned, same-dim embeddings before fusion |
| **Cross-attention fusion** | RNA embedding attends to protein embedding (query=RNA, key/value=protein) → residual + LayerNorm → FFN + residual/norm | Medium | **Primary target.** Matches PLAN.md architecture, directly tests the hypothesis |
| Gated fusion | Learned per-sample gate decides how much protein to mix into RNA | Cheap | Good ablation arm alongside cross-attention; gate value is also interpretable (when does the model lean on protein?) |
| Late fusion / ensemble | Separate RNA-only and protein-only predictors, combine predictions | Cheap | Strong, simple sanity baseline — surprisingly hard to beat in practice |
| RNA→protein residual selection | Train an RNA→protein regression; use the **prediction residual** (not raw gene-wise correlation) to identify which proteins carry independent signal | Medium | Upgrade to the existing statistical pre-selection plan. **Not** for imputing missing protein — an RNA-predicted protein value carries no information beyond RNA itself, so it can't support a synergy claim. Use only for feature selection. |
| Drug–omics interaction (Hadamard / bilinear) | Explicit multiplicative term between drug embedding and cell embedding before the final MLP | Cheap | Worth an ablation arm — plain concatenation is inefficient at learning gene-drug interaction effects (e.g. "this gene matters because it's this drug's target") from data alone |
| Drug–gene cross-attention | Drug attends over individual genes instead of one fixed cell embedding | Expensive | Future work / pitch narrative — likely out of scope for the timeline unless the cheap interaction test below shows strong signal |
| Contrastive aligned latent space (scMODAL-style) | Align RNA/protein embeddings of the same cell line before fusion | Expensive | Future work, name-check in pitch only |
| Mixture-of-experts / tissue-conditioned gating | Gate conditioned on known tissue type rather than learned purely from embeddings | Cheap–medium | Biologically motivated variant of gated fusion; worth considering if gated fusion shows promise |

## Cheap diagnostic before committing to drug–gene interaction modeling

Per-drug feature importance: regress IC50 on RNA features separately per drug, check whether the top genes line up with known ChEMBL drug targets/pathways. If yes, there's exploitable interaction signal a flat concat-MLP likely isn't capturing efficiently, and the expensive drug-gene attention version becomes worth considering. If no, skip it.

## Open questions

- Order: build naive concat → projected-concat → cross-attention first, or interleave the interaction-term ablation earlier?
- How many of the "cheap" arms (gated fusion, late fusion, Hadamard interaction) actually make it in given the one-month timeline, vs. cross-attention alone plus naive concat as the headline comparison?
