# Session Memory
## Last updated: Session 2

---

## Current State

**Phase:** Week 1 — Environment + Data Download  
**Status:** Repo scaffolded. Data download scripts written. Data NOT yet downloaded (requires local machine).

---

## What Exists

### Repo structure
- Full folder structure created at `multiomics-drug-response/`
- `.gitignore` in place (ignores data/raw, data/processed, checkpoints, csv, npy, parquet)
- `environment.yml` created for conda setup
- `requirements.txt` stub in place

### Code written
- `src/data/download.py` — standalone script to download all 4 raw data files + verify + ChEMBL API test
- `notebooks/01_data_download.ipynb` — verification notebook to run after download

### Data status
- **NOT DOWNLOADED** — all download scripts written but require local machine execution
- External domains (cog.sanger.ac.uk, depmap.org, figshare.com, ebi.ac.uk) not reachable from Claude sandbox

### Packages installed (in Claude sandbox only)
- pandas 2.3.3, numpy 2.4.4, scipy 1.17.1, sklearn 1.8.0, rdkit, requests
- drevalpy and torch NOT installed (disk space constraint in sandbox; install locally)

---

## Key Numbers (to fill in after local download)
- Cell Model Passports: ??? rows
- GDSC2: ??? cell lines × ??? drugs
- CCLE RNA-seq: ??? cell lines × ??? genes
- ProCan: ??? cell lines × ??? proteins
- Three-way overlap: ??? cell lines (expected 811–911)

---

## Decisions Made This Session
- Universal cell line ID: DepMap ID (already in PLAN.md, confirmed)
- Download order: Cell Model Passports first, always

---

## Blockers / Notes
- CCLE RNA-seq requires manual download from depmap.org portal (no direct API URL)
- ChEMBL API not testable in sandbox (ebi.ac.uk blocked) — test locally
- drevalpy requires torch; full install on local machine or Colab only
