# Implementation Plan
## Multimodal Drug Response Prediction — One Month Sprint

---

## Overview

**Goal:** Working prototype + pitch-ready results in 4 weeks  
**Hardware:** Local machine for data prep + Colab (free GPU) for DL training  
**Stack:** Python 3.10+, PyTorch, PyTorch Geometric, drevalpy, RDKit, scikit-learn  
**Output:** GitHub repo + benchmark results + pitch narrative  

---

## Week 1 — Environment, Data, and Processing

### Day 1–2: Environment and GitHub Setup

**Step 1: Create GitHub repository**
```bash
# On GitHub: create repo named "multiomics-drug-response"
# Then locally:
git clone https://github.com/YOUR_USERNAME/multiomics-drug-response.git
cd multiomics-drug-response

# Create folder structure
mkdir -p data/raw/{gdsc2,ccle,procan,chembl,mapping}
mkdir -p data/processed data/splits
mkdir -p notebooks src/{data,features,models,training,analysis}
mkdir -p configs results/{figures,tables,checkpoints} tests

# Touch init files
touch src/__init__.py
touch src/{data,features,models,training,analysis}/__init__.py
```

**Step 2: Create .gitignore**
```
# .gitignore
data/raw/
data/processed/
results/checkpoints/
*.h5
*.pkl
*.pt
__pycache__/
*.pyc
.env
*.csv
*.txt
!data/splits/*.json    # keep split indices
```

**Step 3: Set up Python environment**
```bash
# Create conda environment
conda create -n multiomics python=3.10
conda activate multiomics

# Core packages
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install torch-geometric
pip install torch-scatter torch-sparse -f https://data.pyg.org/whl/torch-2.0.0+cu118.html

# Biology / chemistry
pip install rdkit
pip install chembl-webresource-client   # ChEMBL API
pip install drevalpy                     # DrEval framework

# Data science
pip install pandas numpy scipy scikit-learn
pip install matplotlib seaborn plotly
pip install jupyter ipykernel

# Utilities
pip install pyyaml tqdm requests

# Save environment
pip freeze > requirements.txt
conda env export > environment.yml
```

**Step 4: Colab setup cell (save in notebooks/00_colab_setup.ipynb)**
```python
# Run this at the top of every Colab notebook
!pip install torch-geometric drevalpy rdkit-pypi chembl-webresource-client -q

# Mount Drive (to persist data between sessions)
from google.colab import drive
drive.mount('/content/drive')

# Set base path
BASE_PATH = '/content/drive/MyDrive/multiomics_project'
import os; os.makedirs(BASE_PATH, exist_ok=True)
```

---

### Day 2–3: Download All Data

**Download 1: GDSC2 drug response**
```python
import requests, os

# GDSC2 fitted IC50 data
url = "https://cog.sanger.ac.uk/cancerrxgene/GDSC_bulk_data_csv_v8.5/GDSC2_fitted_dose_response_27Oct23.csv"
# If URL changes, go to: https://www.cancerrxgene.org/downloads/bulk_download
# Download: "Fitted dose response parameters GDSC2"

# Also download: drug annotations (name, target, pathway)
# File: "Drug annotations" on the same page
```

**Download 2: CCLE RNA-seq (DepMap portal)**
```python
# Go to: https://depmap.org/portal/data_page/?tab=allData
# Search for "OmicsExpressionProteinCodingGenesTPMLogp1"
# This is: log2(TPM + 1) for protein-coding genes, ~1,019 cell lines
# Direct URL changes with releases — download manually or via API:

import urllib.request
# Latest release URL (check depmap.org for current):
url = "https://depmap.org/portal/download/api/downloads/fileContent?file=OmicsExpressionProteinCodingGenesTPMLogp1.csv&downloadToken=..."
# Alternatively use the depmap Python package:
# pip install depmap
```

**Download 3: ProCan proteomics**
```python
# figshare direct download
import urllib.request

url = "https://figshare.com/ndownloader/files/35468115"
# This is: ProCan-DepMapSanger_protein_matrix_8498_averaged.csv
# ~495 MB — download once and keep locally

urllib.request.urlretrieve(url, "data/raw/procan/procan_protein_matrix.csv")

# Alternative: Cell Model Passports
# https://cellmodelpassports.sanger.ac.uk/downloads
# Download: "Proteomics" dataset
```

**Download 4: Cell line mapping (CRITICAL — do this first)**
```python
# Cell Model Passports — master ID mapping table
url = "https://cog.sanger.ac.uk/cmp/download/model_list_latest.csv.gz"
# This maps: model_id (Sanger) ↔ CCLE_name ↔ COSMIC_ID ↔ DepMap_ID
# This is the key file that lets you join all three datasets

import pandas as pd
mapping = pd.read_csv("data/raw/mapping/model_list_latest.csv.gz")
# Key columns: model_id, CCLE_ID, cosmic_id, depmap_id, cell_line_name
```

**Download 5: Drug SMILES from ChEMBL**
```python
from chembl_webresource_client.new_client import new_client

molecule = new_client.molecule

def get_smiles(drug_name):
    """Get canonical SMILES for a drug by name."""
    results = molecule.filter(pref_name__iexact=drug_name).only(['molecule_chembl_id', 'molecule_structures'])
    for r in results:
        if r.get('molecule_structures'):
            return r['molecule_structures'].get('canonical_smiles')
    return None

# Load GDSC2 drug list, get SMILES for each
# Save to data/raw/chembl/drug_smiles.csv
```

---

### Day 3–5: Data Processing and Harmonization

**This is the hardest part. Budget 2 full days.**

**Step 1: Understand each file's structure**
```python
import pandas as pd

# GDSC2 drug response
gdsc = pd.read_csv("data/raw/gdsc2/GDSC2_fitted_dose_response.csv")
print(gdsc.columns.tolist())
# Key columns: CELL_LINE_NAME, DRUG_NAME, DRUG_ID, LN_IC50, AUC, TISSUE
print(gdsc['CELL_LINE_NAME'].nunique())  # ~969 cell lines
print(gdsc['DRUG_NAME'].nunique())       # ~575 drugs

# CCLE RNA-seq (rows = cell lines, cols = genes)
rna = pd.read_csv("data/raw/ccle/OmicsExpressionProteinCodingGenesTPMLogp1.csv", index_col=0)
print(rna.shape)  # (~1019, ~19000)
# Index format: "ACH-000001" (DepMap IDs)

# ProCan proteomics (rows = cell lines, cols = proteins)
protein = pd.read_csv("data/raw/procan/procan_protein_matrix.csv", index_col=0)
print(protein.shape)  # (~949, ~8498)
# Index format: Sanger model IDs (e.g., "SIDM00001")
```

**Step 2: Standardize all cell line names to one ID system**
```python
# Use DepMap ID as the universal key (most complete mapping)
mapping = pd.read_csv("data/raw/mapping/model_list_latest.csv.gz")

# Create lookup dictionaries
sanger_to_depmap = dict(zip(mapping['model_id'], mapping['depmap_id']))
ccle_to_depmap   = dict(zip(mapping['CCLE_ID'], mapping['depmap_id']))
name_to_depmap   = dict(zip(mapping['cell_line_name'].str.upper(), mapping['depmap_id']))

# Convert ProCan index: Sanger ID → DepMap ID
protein.index = protein.index.map(sanger_to_depmap)
protein = protein[protein.index.notna()]  # drop unmapped

# RNA already uses DepMap IDs — keep as is

# GDSC2 uses cell line names — convert to DepMap ID
gdsc['depmap_id'] = gdsc['CELL_LINE_NAME'].str.upper().map(name_to_depmap)
# For unmatched: try fuzzy matching or manual curation of top 20 mismatches
gdsc_clean = gdsc[gdsc['depmap_id'].notna()]
```

**Step 3: Find three-way overlap**
```python
rna_ids     = set(rna.index)
protein_ids = set(protein.index)
gdsc_ids    = set(gdsc_clean['depmap_id'].unique())

# Two-way overlaps
rna_gdsc     = rna_ids & gdsc_ids
protein_gdsc = protein_ids & gdsc_ids

# Three-way overlap (multimodal dataset)
all_three = rna_ids & protein_ids & gdsc_ids
print(f"RNA ∩ GDSC:          {len(rna_gdsc)}")
print(f"Protein ∩ GDSC:      {len(protein_gdsc)}")
print(f"RNA ∩ Protein ∩ GDSC: {len(all_three)}")  # expect ~811–911

# Save overlap IDs
import json
with open("data/processed/cell_line_ids_three_way.json", "w") as f:
    json.dump(list(all_three), f)
```

**Step 4: Build clean feature matrices**
```python
# Filter to three-way overlap, sort consistently
common_ids = sorted(list(all_three))

rna_matrix     = rna.loc[common_ids]          # shape: (N, ~19000)
protein_matrix = protein.loc[common_ids]      # shape: (N, ~8498)
gdsc_filtered  = gdsc_clean[gdsc_clean['depmap_id'].isin(common_ids)]

# Handle missing proteins: replace NaN with 0
# (justified by BDRN paper: low-expression proteins are truly near-zero)
protein_matrix = protein_matrix.fillna(0)

# Normalize features (z-score per feature across cell lines)
from sklearn.preprocessing import StandardScaler
rna_scaled     = StandardScaler().fit_transform(rna_matrix)
protein_scaled = StandardScaler().fit_transform(protein_matrix)

# Save processed matrices
import numpy as np
np.save("data/processed/rna_matrix.npy", rna_scaled)
np.save("data/processed/protein_matrix.npy", protein_scaled)
pd.DataFrame(rna_scaled, index=common_ids, columns=rna_matrix.columns).to_parquet("data/processed/rna.parquet")
pd.DataFrame(protein_scaled, index=common_ids, columns=protein_matrix.columns).to_parquet("data/processed/protein.parquet")
gdsc_filtered.to_parquet("data/processed/drug_response.parquet")
```

**Step 5: Build drug features**
```python
from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np

def smiles_to_fingerprint(smiles, radius=2, n_bits=2048):
    """Convert SMILES to Morgan fingerprint."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    return np.array(fp)

# Load drug SMILES, generate fingerprints
drug_smiles = pd.read_csv("data/raw/chembl/drug_smiles.csv")
drug_fp = {}
for _, row in drug_smiles.iterrows():
    fp = smiles_to_fingerprint(row['smiles'])
    if fp is not None:
        drug_fp[row['drug_name']] = fp

# For GNN: also build molecular graphs (for PyTorch Geometric)
# Done in src/features/drug_features.py (see models section)
```

---

### Day 5: Implement and Save Data Splits

```python
# src/data/splits.py
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

def make_lpo_splits(df, n_splits=5, seed=42):
    """Leave Pairs Out: random split of drug-cell line pairs."""
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    splits = []
    for train_idx, test_idx in kf.split(df):
        splits.append({'train': train_idx.tolist(), 'test': test_idx.tolist()})
    return splits

def make_lco_splits(df, n_splits=5, seed=42):
    """Leave Cell line Out: hold out entire cell lines."""
    cell_lines = df['depmap_id'].unique()
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    splits = []
    for train_cl, test_cl in kf.split(cell_lines):
        train_cells = set(cell_lines[train_cl])
        test_cells  = set(cell_lines[test_cl])
        train_idx = df[df['depmap_id'].isin(train_cells)].index.tolist()
        test_idx  = df[df['depmap_id'].isin(test_cells)].index.tolist()
        splits.append({'train': train_idx, 'test': test_idx})
    return splits

def make_ldo_splits(df, n_splits=5, seed=42):
    """Leave Drug Out: hold out entire drugs."""
    drugs = df['DRUG_NAME'].unique()
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    splits = []
    for train_d, test_d in kf.split(drugs):
        train_drugs = set(drugs[train_d])
        test_drugs  = set(drugs[test_d])
        train_idx = df[df['DRUG_NAME'].isin(train_drugs)].index.tolist()
        test_idx  = df[df['DRUG_NAME'].isin(test_drugs)].index.tolist()
        splits.append({'train': train_idx, 'test': test_idx})
    return splits

# IMPORTANT TIP: save splits before training anything
# Use the SAME splits for ALL models — baseline and DL
# This is the only way to make comparisons fair
```

**Key tips for splits:**
- Generate splits ONCE, save as JSON, never regenerate
- Always fit scalers on train fold only, apply to test fold
- For LCO: ensure no cell line appears in both train and test (obvious but easy to get wrong)
- For LDO: remove drugs with <10 cell line measurements before splitting

---

## Week 2 — Statistical Analysis and Baselines

### Day 6–7: Statistical Analysis of Modality Relationships

Run these in `notebooks/03_statistical_analysis.ipynb`

```python
# Analysis 1: RNA-protein correlation landscape
# For each gene: Pearson r between its RNA and protein expression across cell lines
rna_df     = pd.read_parquet("data/processed/rna.parquet")
protein_df = pd.read_parquet("data/processed/protein.parquet")

# Find common genes (genes measured in both RNA and protein)
# ProCan proteins are indexed by gene name — map to gene symbols
common_genes = rna_df.columns.intersection(protein_df.columns)
print(f"Common genes: {len(common_genes)}")  # expect ~7,000–8,000

rna_common     = rna_df[common_genes]
protein_common = protein_df[common_genes]

from scipy import stats
gene_corr = {}
for gene in common_genes:
    r, p = stats.pearsonr(rna_common[gene], protein_common[gene])
    gene_corr[gene] = {'pearson_r': r, 'p_value': p}

gene_corr_df = pd.DataFrame(gene_corr).T
print(f"Median gene-wise RNA-protein Pearson r: {gene_corr_df['pearson_r'].median():.3f}")
# Expected: ~0.43–0.44

# Analysis 2: Which proteins are most INDEPENDENT from RNA?
# These are the ones most likely to add new information
# Independence = low RNA-protein correlation BUT high protein-IC50 correlation
```

```python
# Analysis 3: RNA → IC50 and Protein → IC50 correlations per gene
# For each gene: how much does its expression predict drug response?
gdsc = pd.read_parquet("data/processed/drug_response.parquet")

# For one drug (e.g., most tested drug): correlate each gene with IC50
drug = gdsc['DRUG_NAME'].value_counts().index[0]
drug_response = gdsc[gdsc['DRUG_NAME'] == drug].set_index('depmap_id')['LN_IC50']

# Align indices
common_cells = rna_df.index.intersection(drug_response.index)
rna_sub      = rna_df.loc[common_cells]
drug_sub     = drug_response.loc[common_cells]

rna_ic50_corr = rna_sub.corrwith(drug_sub)
# Rank genes by |correlation| with IC50 — top features

# Repeat for protein
protein_sub = protein_df.loc[common_cells, protein_df.columns.intersection(rna_df.columns)]
protein_ic50_corr = protein_sub.corrwith(drug_sub)

# Analysis 4: Protein-specific contribution BEYOND RNA
# Partial correlation: protein → IC50, controlling for RNA of same gene
# High partial correlation = protein adds unique signal
```

```python
# Analysis 5: Blood vs solid cancer RNA-protein correlation
cancer_type = pd.read_csv("data/raw/mapping/model_list_latest.csv.gz")[['depmap_id', 'cancer_type']]
blood_types = ['Haematopoietic and Lymphoid', 'Leukemia', 'Lymphoma']
# Separate cell lines, compute correlation in each group
# Expected: blood ~0.58, solid ~0.53
```

**What this tells you for the model:**
- Proteins with low RNA-protein r AND high protein-IC50 r → include in model
- Proteins with high RNA-protein r → likely redundant, lower priority
- This analysis IS your "avoid redundant information" design principle implemented statistically

---

### Day 8–9: Implement Baselines

```python
# src/models/baselines.py

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet
from sklearn.metrics import r2_score
from scipy.stats import pearsonr

class NaiveMeanPredictor:
    """
    Baseline: predict the mean IC50 for each drug across training cell lines.
    This is the hardest baseline to beat — DrEval showed most DL models fail.
    """
    def fit(self, X, y, drug_ids):
        self.drug_means = {}
        for drug in np.unique(drug_ids):
            mask = drug_ids == drug
            self.drug_means[drug] = y[mask].mean()
        self.global_mean = y.mean()

    def predict(self, drug_ids):
        return np.array([self.drug_means.get(d, self.global_mean) for d in drug_ids])


class RNARandomForest:
    """
    Tuned Random Forest on RNA features + drug fingerprint.
    Concatenate RNA embedding (top-500 genes by variance) + drug fingerprint (2048-d).
    """
    def __init__(self, n_estimators=500, max_features='sqrt'):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_features=max_features,
            n_jobs=-1,
            random_state=42
        )

    def fit(self, rna, drug_fp, y):
        # Reduce RNA dimensionality: top-500 genes by variance (fit on train only)
        self.top_gene_idx = np.argsort(rna.var(axis=0))[-500:]
        X = np.hstack([rna[:, self.top_gene_idx], drug_fp])
        self.model.fit(X, y)

    def predict(self, rna, drug_fp):
        X = np.hstack([rna[:, self.top_gene_idx], drug_fp])
        return self.model.predict(X)
```

**Tip:** Tune Random Forest hyperparameters with Optuna or simple grid search on validation fold — this step matters enormously. An untuned RF is not a fair baseline.

---

### Day 9–10: Run DrEval Baselines

```python
# drevalpy integrates GDSC2 data and baselines natively
from drevalpy import drug_response_experiment

# Run built-in baselines: naive mean + Random Forest + ElasticNet
drug_response_experiment(
    models=["NaiveMeanPredictor", "RandomForest", "ElasticNet"],
    baselines=["NaiveMeanPredictor"],
    response_data="GDSC2",
    metric="mse",
    n_cv_splits=5,
    test_mode="LCO",      # run once for LCO
    run_id="baselines_lco"
)

# Repeat for LPO and LDO
# This gives you the authoritative baseline numbers to beat
```

**Tip:** DrEval handles data loading, splitting, and evaluation automatically. Use it for baselines. For your custom DL model, implement the same split logic manually and compare on the same test folds.

---

## Week 3 — Deep Learning Model Implementation

Run on **Google Colab** with GPU. Upload data to Google Drive first.

### Day 11–12: Drug GNN

```python
# src/features/drug_features.py
# Build molecular graph from SMILES for PyTorch Geometric

import torch
from torch_geometric.data import Data
from rdkit import Chem
from rdkit.Chem import AllChem

ATOM_FEATURES = ['atomic_num', 'degree', 'formal_charge',
                  'hybridization', 'is_aromatic', 'num_hs']

def atom_to_features(atom):
    return [
        atom.GetAtomicNum(),
        atom.GetDegree(),
        atom.GetFormalCharge(),
        int(atom.GetHybridization()),
        int(atom.GetIsAromatic()),
        atom.GetTotalNumHs()
    ]

def smiles_to_graph(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    x = torch.tensor([atom_to_features(a) for a in mol.GetAtoms()],
                      dtype=torch.float)
    edges = []
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        edges += [[i, j], [j, i]]  # undirected
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    return Data(x=x, edge_index=edge_index)
```

---

### Day 12–14: Cross-Attention Fusion Model

```python
# src/models/fusion_model.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool

class DrugGNN(nn.Module):
    """GNN encoder for drug molecular graph."""
    def __init__(self, in_dim=6, hidden=256, out_dim=256):
        super().__init__()
        self.conv1 = GCNConv(in_dim, hidden)
        self.conv2 = GCNConv(hidden, hidden)
        self.conv3 = GCNConv(hidden, out_dim)
        self.bn1 = nn.BatchNorm1d(hidden)
        self.bn2 = nn.BatchNorm1d(hidden)

    def forward(self, x, edge_index, batch):
        x = F.relu(self.bn1(self.conv1(x, edge_index)))
        x = F.relu(self.bn2(self.conv2(x, edge_index)))
        x = self.conv3(x, edge_index)
        return global_mean_pool(x, batch)  # (batch_size, out_dim)


class OmicsEncoder(nn.Module):
    """MLP encoder for a single omics modality."""
    def __init__(self, in_dim, hidden=512, out_dim=256, dropout=0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.BatchNorm1d(hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, out_dim),
            nn.BatchNorm1d(out_dim),
            nn.ReLU()
        )

    def forward(self, x):
        return self.net(x)


class CrossAttentionFusion(nn.Module):
    """
    Cross-attention fusion of RNA and protein embeddings.
    RNA embedding attends to protein embedding to learn which
    proteins add information beyond their RNA counterpart.
    """
    def __init__(self, dim=256, n_heads=4, dropout=0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, n_heads, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 2),
            nn.ReLU(),
            nn.Linear(dim * 2, dim)
        )

    def forward(self, rna_emb, protein_emb):
        # rna_emb, protein_emb: (batch, dim)
        # Reshape for attention: (batch, seq_len=1, dim)
        q = rna_emb.unsqueeze(1)
        k = protein_emb.unsqueeze(1)
        v = protein_emb.unsqueeze(1)

        attn_out, _ = self.attn(q, k, v)           # (batch, 1, dim)
        fused = self.norm1(q + attn_out).squeeze(1) # residual + norm
        fused = self.norm2(fused + self.ffn(fused))  # FFN + norm
        return fused  # (batch, dim)


class MultiModalDrugResponseModel(nn.Module):
    """
    Full model: RNA + Protein → CrossAttention → fused cell embedding
                Drug SMILES → GNN → drug embedding
                Concat → MLP → predicted ln(IC50)
    """
    def __init__(self, rna_dim, protein_dim, drug_node_dim=6,
                 embed_dim=256, dropout=0.3):
        super().__init__()
        self.rna_encoder     = OmicsEncoder(rna_dim, 512, embed_dim, dropout)
        self.protein_encoder = OmicsEncoder(protein_dim, 512, embed_dim, dropout)
        self.fusion          = CrossAttentionFusion(embed_dim)
        self.drug_encoder    = DrugGNN(drug_node_dim, 256, embed_dim)

        self.predictor = nn.Sequential(
            nn.Linear(embed_dim * 2, 512),  # fused_cell + drug
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1)
        )

    def forward(self, rna, protein, drug_data, protein_mask=None):
        """
        rna:          (batch, rna_dim)
        protein:      (batch, protein_dim)
        drug_data:    PyTorch Geometric batch
        protein_mask: (batch,) bool — True if protein available
                      If None, assume all available
        """
        rna_emb     = self.rna_encoder(rna)
        protein_emb = self.protein_encoder(protein)

        # Modality dropout: randomly zero out protein during training
        if self.training and protein_mask is None:
            mask = torch.rand(rna_emb.shape[0]) > 0.3  # 30% dropout
            protein_emb = protein_emb * mask.float().unsqueeze(1).to(protein_emb.device)

        fused_cell = self.fusion(rna_emb, protein_emb)
        drug_emb   = self.drug_encoder(drug_data.x, drug_data.edge_index, drug_data.batch)

        combined = torch.cat([fused_cell, drug_emb], dim=1)
        return self.predictor(combined).squeeze(1)
```

---

### Day 14–15: Training Loop

```python
# src/training/train.py

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch_geometric.loader import DataLoader as GeoDataLoader
from scipy.stats import pearsonr
import numpy as np

def train_epoch(model, loader, optimizer, device):
    model.train()
    total_loss = 0
    for batch in loader:
        rna, protein, drug_data, y = [b.to(device) for b in batch]
        optimizer.zero_grad()
        pred = model(rna, protein, drug_data)
        loss = nn.MSELoss()(pred, y)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)

def evaluate(model, loader, device):
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for batch in loader:
            rna, protein, drug_data, y = [b.to(device) for b in batch]
            pred = model(rna, protein, drug_data)
            preds.extend(pred.cpu().numpy())
            targets.extend(y.cpu().numpy())
    preds, targets = np.array(preds), np.array(targets)
    pearson_r, _ = pearsonr(preds, targets)
    rmse = np.sqrt(np.mean((preds - targets) ** 2))
    return {'pearson_r': pearson_r, 'rmse': rmse}

def train(model, train_loader, val_loader, n_epochs=100, lr=1e-3, device='cuda'):
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
    best_val_r = -1
    best_state = None

    for epoch in range(n_epochs):
        train_loss = train_epoch(model, train_loader, optimizer, device)
        val_metrics = evaluate(model, val_loader, device)
        scheduler.step(val_metrics['rmse'])

        if val_metrics['pearson_r'] > best_val_r:
            best_val_r = val_metrics['pearson_r']
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        if epoch % 10 == 0:
            print(f"Epoch {epoch}: loss={train_loss:.4f}, "
                  f"val_r={val_metrics['pearson_r']:.4f}")

    model.load_state_dict(best_state)
    return model
```

**Key training tips:**
- Use early stopping (patience=20 epochs) to prevent overfitting on the small dataset
- Gradient clipping (max_norm=1.0) stabilizes training with cross-attention
- Batch size: 256–512 (GPU memory permitting on Colab)
- Learning rate: start at 1e-3, let scheduler reduce
- Always checkpoint the best validation model, not the final epoch
- For LCO: train on 4 folds, validate on 1 fold — no cell line leaks across folds

---

## Week 4 — Evaluation, Ablation, and Results

### Day 16–18: Full Benchmark

Run all models under all splits and record results systematically.

```python
# Evaluation checklist — run for EVERY model × EVERY split:
# □ Naive mean predictor    × LPO, LCO, LDO
# □ Tuned Random Forest     × LPO, LCO, LDO  (RNA only)
# □ ElasticNet              × LPO, LCO, LDO  (RNA only)
# □ BDRN (RNA + drug GNN)   × LPO, LCO, LDO
# □ BDRN (protein + drug GNN) × LPO, LCO, LDO
# □ Your model (RNA + protein + GNN) × LPO, LCO, LDO
#
# Critical: ALL models evaluated on the SAME test folds

# Metrics to report for each:
# - Pearson r (primary)
# - RMSE
# - Normalized R²
# - Per-tissue-type breakdown (blood vs solid cancer)
```

---

### Day 18–19: Ablation Study

```python
# Test each component's contribution independently
# This is what separates a real scientific contribution from just "my model is better"

# Ablation 1: Remove cross-attention → replace with concatenation
#   → shows cross-attention specifically matters, not just having protein

# Ablation 2: Remove modality dropout
#   → shows dropout improves robustness

# Ablation 3: Use all proteins vs top-K selected proteins
#   → shows statistical pre-selection helps

# Ablation 4: Protein alone (no RNA) in your architecture
#   → confirms RNA is still the primary modality

# Randomization test (DrEval approach):
# Randomly shuffle protein features → if performance drops, protein is genuinely useful
# If performance stays same → protein is not contributing
```

---

### Day 19–20: Blood vs Solid Cancer Analysis

```python
# This is your most important scientific finding
cancer_types = pd.read_csv("data/raw/mapping/model_list_latest.csv.gz")[
    ['depmap_id', 'cancer_type', 'tissue']
]

blood_keywords = ['haematopoietic', 'lymphoid', 'leukemia', 'lymphoma', 'myeloma']

def is_blood_cancer(tissue):
    return any(kw in str(tissue).lower() for kw in blood_keywords)

# For LCO test set:
# Split results by blood vs solid cancer cell lines
# Show: in solid cancers (low RNA-protein correlation), 
#       multimodal model improves MORE over RNA-alone than in blood cancers
# This is your hypothesis validated
```

---

### Day 20–21: Results Visualization and Pitch Preparation

```python
# Figure 1: RNA-protein correlation landscape (boxplot by cancer type)
# Figure 2: Baseline comparison table (LPO vs LCO vs LDO) — all models
# Figure 3: Your model vs BDRN under LCO — the main result
# Figure 4: Ablation study bar chart
# Figure 5: Blood vs solid cancer breakdown
# Figure 6: Attention weights heatmap — which proteins does the model attend to?
#           This makes the model interpretable for the pitch
```

---

## General Tips and Pitfalls

### Data pitfalls
- **Cell line naming is the #1 time sink.** Use Cell Model Passports mapping table. Handle case sensitivity, spaces, dashes.
- **Fit scalers on train only.** Never normalize using test set statistics — data leakage.
- **ProCan missing values.** Replace with 0, not mean imputation. BDRN validated this choice.
- **GDSC2 has duplicate cell line entries** for the same cell line measured at different time points. Average them or take the most recent.
- **Drug SMILES failures.** ~10% of drugs won't be found in ChEMBL by name. Use PubChem as a fallback. For remaining failures, drop from dataset.

### Modeling pitfalls
- **Never compare models evaluated on different subsets.** RNA-only uses ~969 cells, multimodal uses ~911. Evaluate both on the ~911 overlap.
- **Cross-attention with dim=1 doesn't make sense.** RNA and protein embeddings must be the same dimension for attention.
- **Batch normalization breaks with batch_size=1.** Set drop_last=True in DataLoader.
- **GNN batching is different from regular batching.** Use PyTorch Geometric's DataLoader, not PyTorch's.
- **LCO split leakage.** Double-check that the same cell line never appears in both train and test after splitting. One line of code: `assert len(set(train_cells) & set(test_cells)) == 0`.

### Colab tips
- Mount Google Drive at the start of every session — data resets otherwise
- Use `torch.cuda.empty_cache()` if you get OOM errors
- Save checkpoints to Drive every 10 epochs — Colab disconnects randomly
- Use `!nvidia-smi` to check which GPU you got (T4 is fine, A100 is lucky)
- Keep data as `.npy` or `.parquet` — much faster to load than CSV on Colab

### Evaluation tips
- Report confidence intervals: run each split 3 times with different random seeds, report mean ± std
- Statistical significance: paired t-test between your model and the best baseline across folds
- The randomization test is non-negotiable: randomly permute protein features, show performance drops — this proves protein is causally contributing, not just correlated noise

---

## Timeline Summary

| Week | Days | Deliverable |
|---|---|---|
| Week 1 | 1–2 | Environment + GitHub repo set up |
| Week 1 | 2–3 | All data downloaded and verified |
| Week 1 | 3–5 | Data processed, harmonized, splits saved |
| Week 2 | 6–7 | Statistical analysis: correlation landscapes |
| Week 2 | 8–9 | Baselines implemented and evaluated |
| Week 2 | 9–10 | DrEval baselines run |
| Week 3 | 11–12 | Drug GNN implemented and tested |
| Week 3 | 12–14 | Cross-attention fusion model implemented |
| Week 3 | 14–15 | Training loop + first training run on Colab |
| Week 4 | 16–18 | Full benchmark: all models × all splits |
| Week 4 | 18–19 | Ablation studies |
| Week 4 | 19–20 | Blood vs solid cancer analysis |
| Week 4 | 20–21 | Figures, pitch narrative, README finalized |

---

## Success Criteria

**Minimum (pitch-ready):**
- All baselines running and evaluated under LCO
- Your model running and producing results under LCO
- Any improvement over RNA-alone under LCO, even small

**Good:**
- Statistically significant improvement under LCO
- Ablation study showing cross-attention specifically matters
- Blood vs solid cancer breakdown confirming hypothesis

**Strong:**
- Improvement under both LCO and LDO
- Interpretable attention weights showing biologically meaningful protein contributions
- Results comparable to or better than BDRN on LCO
