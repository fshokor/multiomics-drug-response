# Progress Log

---

## Session 1 — Project Planning
- Defined project scope: RNA + protein cross-attention fusion for drug response prediction
- Chose datasets: GDSC2, CCLE RNA-seq, ProCan proteomics, ChEMBL SMILES
- Wrote README.md (hypothesis, architecture, related work, company landscape)
- Wrote PLAN.md (full 4-week implementation plan with code)
- Identified evaluation protocol: LPO/LCO/LDO via DrEval
- Primary metric: Pearson r under LCO

---

## Session 2 — Environment + Data Download Scripts
- Created full repo folder structure
- Created `.gitignore`, `environment.yml`, `requirements.txt` stub
- Wrote `src/data/download.py` — downloads Cell Model Passports, GDSC2, ProCan; instructions for CCLE; ChEMBL API test; verification
- Created `notebooks/01_data_download.ipynb` — verification notebook
- Installed core packages in sandbox: pandas, numpy, scipy, sklearn, rdkit
- **TODO (local machine):** run `python src/data/download.py`, then `notebooks/01_data_download.ipynb`
