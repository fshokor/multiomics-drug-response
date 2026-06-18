"""
Data preparation script — downloads and prepares all datasets.

Usage:
    python src/data/download.py

What this does:
    1. Downloads GDSC2 (drug response + gene expression + drug features) via drevalpy
    2. Expects ProCan proteomics to be manually downloaded (figshare blocks automation)
    3. Converts ProCan to drevalpy format using cellosaurus_id as universal key
    4. Verifies three-way overlap

Manual step required before running:
    Download: ProCan-DepMapSanger_protein_matrix_8498_averaged.txt (90 MB)
    From:     https://figshare.com/articles/dataset/Pan-cancer_proteomic_map_of_949_human_cell_lines/19345397
    Save to:  data/raw/procan/ProCan-DepMapSanger_protein_matrix_8498_averaged.txt

Final data layout:
    data/
    ├── GDSC2/
    │   ├── GDSC2.csv                ← drug response (pubchem_id × cellosaurus_id)
    │   ├── gene_expression.csv      ← RNA-seq (cellosaurus_id index)
    │   ├── proteomics.csv           ← ProCan converted (cellosaurus_id index)
    │   ├── cell_line_names.csv      ← cellosaurus_id ↔ cell_line_name ↔ tissue
    │   ├── drug_smiles.csv          ← SMILES strings
    │   ├── drug_fingerprints/       ← Morgan fingerprints
    │   └── drug_graphs/             ← PyG molecular graphs
    └── meta/
        ├── tissue_mapping.csv
        └── gene_lists/
"""

import pandas as pd
import requests
from pathlib import Path

ROOT      = Path(__file__).resolve().parents[2]
DATA_PATH = str(ROOT / "data")

PROCAN_RAW  = ROOT / "data" / "raw" / "procan" / "ProCan-DepMapSanger_protein_matrix_8498_averaged.txt"
PROCAN_DEST = ROOT / "data" / "GDSC2" / "proteomics.csv"
CL_NAMES    = ROOT / "data" / "GDSC2" / "cell_line_names.csv"


# ── Step 1: Download GDSC2 bundle via drevalpy ────────────────────────────────

def download_drevalpy_data() -> None:
    """
    Download GDSC2 + meta via drevalpy from Zenodo.

    This gives us:
      - GDSC2.csv              (drug response, cellosaurus_id keyed)
      - gene_expression.csv    (CCLE RNA-seq, cellosaurus_id index)
      - cell_line_names.csv    (cellosaurus_id ↔ cell_line_name ↔ tissue)
      - drug_smiles.csv        (SMILES for all drugs)
      - drug_fingerprints/     (Morgan fingerprints)
      - drug_graphs/           (PyG molecular graphs)
      - methylation.csv, mutations.csv, copy_number_variation_gistic.csv
    """
    print("[1/3] Downloading GDSC2 bundle via drevalpy...")
    from drevalpy.datasets.loader import download_dataset
    download_dataset("GDSC2", data_path=DATA_PATH)
    download_dataset("meta",  data_path=DATA_PATH)
    print("      Done.\n")


# ── Step 2: Convert ProCan to drevalpy format ─────────────────────────────────

def convert_procan() -> None:
    """
    Convert ProCan proteomics matrix to drevalpy format.

    ProCan index format:  'SIDM00018;K052'  (Sanger ID ; cell line name)
    drevalpy index format: cellosaurus_id   (e.g. 'CVCL_1234')

    Mapping: extract cell line name from ProCan index → normalize →
             look up in cell_line_names.csv → get cellosaurus_id
    """
    print("[2/3] Converting ProCan proteomics to drevalpy format...")

    # Check ProCan file exists
    if not PROCAN_RAW.exists():
        print(f"""
      [ERROR] ProCan file not found at:
              {PROCAN_RAW}

      Please download it manually:
        1. Go to: https://figshare.com/articles/dataset/Pan-cancer_proteomic_map_of_949_human_cell_lines/19345397
        2. Download: ProCan-DepMapSanger_protein_matrix_8498_averaged.txt (90 MB)
        3. Save to:  data/raw/procan/
        4. Re-run this script
        """)
        return

    # Check drevalpy data exists
    if not CL_NAMES.exists():
        print("      [ERROR] cell_line_names.csv not found. Run download_drevalpy_data() first.")
        return

    # Load ProCan
    procan = pd.read_csv(PROCAN_RAW, sep="\t", index_col=0)
    print(f"      ProCan raw shape: {procan.shape}")  # expect (949, 8498)

    # Load drevalpy cell line name → cellosaurus_id mapping
    cl_names = pd.read_csv(CL_NAMES)  # cols: cellosaurus_id, cell_line_name, tissue
    print(f"      Cell line names loaded: {len(cl_names)} entries")

    # Normalize function: remove dashes, spaces, underscores, uppercase
    def normalize(s: str) -> str:
        return str(s).upper().replace("-", "").replace(" ", "").replace("_", "")

    # Build normalized name → cellosaurus_id lookup
    cl_names["name_norm"] = cl_names["cell_line_name"].map(normalize)
    name_to_cvcl = dict(zip(cl_names["name_norm"], cl_names["cellosaurus_id"]))

    # Extract cell line name from ProCan index (format: 'SIDM00018;K052')
    procan_names      = pd.Series(procan.index.str.split(";").str[1])
    procan_names_norm = procan_names.map(normalize)

    # Map to cellosaurus_id
    procan.index      = procan_names_norm.map(name_to_cvcl).values
    procan            = procan[pd.notna(procan.index)]
    procan.index.name = "cellosaurus_id"

    print(f"      Mapped to cellosaurus_id: {procan.shape[0]} cell lines matched")
    print(f"      Unmatched (dropped):      {949 - procan.shape[0]}")

    # Save
    PROCAN_DEST.parent.mkdir(parents=True, exist_ok=True)
    procan.to_csv(PROCAN_DEST)
    print(f"      Saved to {PROCAN_DEST}\n")


# ── Step 3: Verify ────────────────────────────────────────────────────────────

def verify() -> None:
    """Verify all files exist and report three-way overlap."""
    print("[3/3] Verification")

    checks = {
        "GDSC2 response":    ROOT / "data" / "GDSC2" / "GDSC2.csv",
        "Gene expression":   ROOT / "data" / "GDSC2" / "gene_expression.csv",
        "Proteomics":        ROOT / "data" / "GDSC2" / "proteomics.csv",
        "Cell line names":   ROOT / "data" / "GDSC2" / "cell_line_names.csv",
        "Drug SMILES":       ROOT / "data" / "GDSC2" / "drug_smiles.csv",
        "Tissue mapping":    ROOT / "data" / "meta"  / "tissue_mapping.csv",
    }

    all_ok = True
    for label, path in checks.items():
        if path.exists():
            size = path.stat().st_size / 1e6
            print(f"      [OK]      {label}: {size:.0f} MB")
        else:
            print(f"      [MISSING] {label}: {path}")
            all_ok = False

    # Three-way overlap using cellosaurus_id as universal key
    gdsc2_path = ROOT / "data" / "GDSC2" / "GDSC2.csv"
    ge_path    = ROOT / "data" / "GDSC2" / "gene_expression.csv"
    prot_path  = ROOT / "data" / "GDSC2" / "proteomics.csv"
    cl_path    = ROOT / "data" / "GDSC2" / "cell_line_names.csv"

    if all(p.exists() for p in [gdsc2_path, ge_path, prot_path, cl_path]):
        gdsc2    = pd.read_csv(gdsc2_path, dtype={"pubchem_id": str}, low_memory=False)
        ge       = pd.read_csv(ge_path,   index_col=0)
        prot     = pd.read_csv(prot_path, index_col=0)
        cl_names = pd.read_csv(cl_path)

        # GDSC2 uses cell_line_name — convert to cellosaurus_id via cl_names
        name_to_cvcl = dict(zip(cl_names["cell_line_name"], cl_names["cellosaurus_id"]))
        gdsc2_cvcl   = set(gdsc2["cell_line_name"].map(name_to_cvcl).dropna())

        ge_cls   = set(ge.index.astype(str))
        prot_cls = set(prot.index.astype(str))
        overlap  = gdsc2_cvcl & ge_cls & prot_cls

        print(f"\n      GDSC2 cell lines (via cvcl):    {len(gdsc2_cvcl)}")
        print(f"      Gene expression cell lines:     {len(ge_cls)}")
        print(f"      Proteomics cell lines:          {len(prot_cls)}")
        print(f"      Three-way overlap:              {len(overlap)}  (expected ~800-900)")
        print(f"\n      GDSC2 unique drugs:             {gdsc2['pubchem_id'].nunique()}")
        print(f"      Gene expression genes:          {ge.shape[1]}")
        print(f"      Proteins:                       {prot.shape[1]}")

    if all_ok:
        print("\n      All files present. Ready for Session 3.")
    else:
        print("\n      Some files missing — check errors above.")


if __name__ == "__main__":
    print("=== Multiomics Drug Response — Data Preparation ===\n")
    download_drevalpy_data()
    convert_procan()
    verify()
