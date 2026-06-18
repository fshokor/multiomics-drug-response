"""
Data download script — run this locally (not in Claude sandbox).
Downloads all raw data files for the multiomics drug response project.

Usage:
    python src/data/download.py

All files saved to data/raw/. Requires ~700 MB free disk space.
"""

import os
import urllib.request
import requests
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
RAW  = ROOT / "data" / "raw"


def download_file(url: str, dest: Path, label: str) -> None:
    """Download a file with progress reporting."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"  [SKIP] {label} already exists at {dest}")
        return
    print(f"  Downloading {label}...")
    urllib.request.urlretrieve(url, dest)
    size_mb = dest.stat().st_size / 1e6
    print(f"  [OK] {label} → {dest} ({size_mb:.1f} MB)")


def download_cell_model_passports() -> None:
    """Cell line ID mapping: Sanger ↔ CCLE ↔ DepMap IDs."""
    print("\n[1/4] Cell Model Passports mapping")
    download_file(
        url="https://cog.sanger.ac.uk/cmp/download/model_list_latest.csv.gz",
        dest=RAW / "mapping" / "model_list_latest.csv.gz",
        label="Cell Model Passports"
    )


def download_gdsc2() -> None:
    """GDSC2 fitted dose response parameters."""
    print("\n[2/4] GDSC2 drug response")
    # Check cancerrxgene.org/downloads/bulk_download if this URL changes
    download_file(
        url="https://cog.sanger.ac.uk/cancerrxgene/GDSC_bulk_data_csv_v8.5/GDSC2_fitted_dose_response_27Oct23.csv",
        dest=RAW / "gdsc2" / "GDSC2_fitted_dose_response.csv",
        label="GDSC2 dose response"
    )


def download_procan() -> None:
    """ProCan-DepMapSanger proteomics matrix (~495 MB)."""
    print("\n[3/4] ProCan proteomics")
    download_file(
        url="https://figshare.com/ndownloader/files/35468115",
        dest=RAW / "procan" / "procan_protein_matrix.csv",
        label="ProCan protein matrix"
    )


def download_ccle_instructions() -> None:
    """CCLE RNA-seq must be downloaded manually from DepMap portal."""
    print("\n[4/4] CCLE RNA-seq (manual download required)")
    print("  1. Go to: https://depmap.org/portal/data_page/?tab=allData")
    print("  2. Search for: OmicsExpressionProteinCodingGenesTPMLogp1")
    print("  3. Download the CSV file")
    print(f"  4. Save to: {RAW / 'ccle' / 'OmicsExpressionProteinCodingGenesTPMLogp1.csv'}")
    print("  (~200 MB)")


def test_chembl_api() -> None:
    """Quick sanity check that the ChEMBL API is reachable."""
    print("\n[ChEMBL API test]")
    from chembl_webresource_client.new_client import new_client
    molecule = new_client.molecule

    test_drugs = ["Erlotinib", "Imatinib", "Gefitinib", "Paclitaxel", "Docetaxel"]
    results = {}
    for drug in test_drugs:
        hits = molecule.filter(pref_name__iexact=drug).only(
            ['molecule_chembl_id', 'molecule_structures']
        )
        for r in hits:
            if r.get('molecule_structures'):
                smiles = r['molecule_structures'].get('canonical_smiles')
                if smiles:
                    results[drug] = smiles
                    break
        if drug not in results:
            results[drug] = None

    for drug, smiles in results.items():
        status = "OK" if smiles else "NOT FOUND"
        print(f"  [{status}] {drug}: {smiles[:40] + '...' if smiles else 'None'}")


def verify_downloads() -> None:
    """Spot-check downloaded files."""
    import pandas as pd

    print("\n── Verification ────────────────────────────────────────────────")

    # Cell Model Passports
    mapping_path = RAW / "mapping" / "model_list_latest.csv.gz"
    if mapping_path.exists():
        mapping = pd.read_csv(mapping_path)
        required_cols = ['model_id', 'CCLE_ID', 'depmap_id', 'cell_line_name']
        missing = [c for c in required_cols if c not in mapping.columns]
        print(f"  Mapping: {mapping.shape[0]} rows, {mapping.shape[1]} cols")
        print(f"  Required columns present: {not missing}")
        if missing:
            print(f"  MISSING COLUMNS: {missing}")
            print(f"  Actual columns: {mapping.columns.tolist()[:10]}")
    else:
        print("  Mapping: NOT DOWNLOADED")

    # GDSC2
    gdsc_path = RAW / "gdsc2" / "GDSC2_fitted_dose_response.csv"
    if gdsc_path.exists():
        gdsc = pd.read_csv(gdsc_path)
        print(f"  GDSC2: {gdsc.shape[0]:,} rows × {gdsc.shape[1]} cols")
        print(f"  Cell lines: {gdsc['CELL_LINE_NAME'].nunique()}")
        print(f"  Drugs: {gdsc['DRUG_NAME'].nunique()}")
        print(f"  Columns: {gdsc.columns.tolist()}")
    else:
        print("  GDSC2: NOT DOWNLOADED")

    # CCLE RNA
    ccle_path = RAW / "ccle" / "OmicsExpressionProteinCodingGenesTPMLogp1.csv"
    if ccle_path.exists():
        rna = pd.read_csv(ccle_path, index_col=0, nrows=5)
        print(f"  CCLE RNA: index format sample: {rna.index[:3].tolist()}")
        print(f"  CCLE RNA: {rna.shape[1]} genes (from first 5 rows)")
    else:
        print("  CCLE RNA: NOT DOWNLOADED (manual step required)")

    # ProCan
    procan_path = RAW / "procan" / "procan_protein_matrix.csv"
    if procan_path.exists():
        prot = pd.read_csv(procan_path, index_col=0, nrows=5)
        print(f"  ProCan: index format sample: {prot.index[:3].tolist()}")
        print(f"  ProCan: {prot.shape[1]} proteins (from first 5 rows)")
    else:
        print("  ProCan: NOT DOWNLOADED")


if __name__ == "__main__":
    print("=== Multiomics Drug Response — Data Download ===")
    download_cell_model_passports()
    download_gdsc2()
    download_procan()
    download_ccle_instructions()
    test_chembl_api()
    verify_downloads()
    print("\nDone. Run notebooks/01_data_download.ipynb for detailed inspection.")
