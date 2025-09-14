from __future__ import annotations
import pandas as pd
from typing import Dict, List
CEDE_MAP = {"LocID":"location_id","LocationID":"location_id","Address":"address","City":"city","State":"state","PostalCode":"postcode","Postcode":"postcode","ZipCode":"postcode","Country":"country","CountryCode":"country","Latitude":"latitude","Longitude":"longitude","StructureTIV":"tiv_building","ContentTIV":"tiv_content","BITIV":"tiv_bi","BI TIV":"tiv_bi","TIV":"tiv","GrossTIV":"tiv","PML":"pml","PML1":"pml","PML%":"pml_percent","PMLPercent":"pml_percent","LOB":"class","Class":"class"}
OED_MAP = {"LocationID":"location_id","LocNumber":"location_id","StreetAddress":"address","City":"city","State":"state","PostalCode":"postcode","ZipCode":"postcode","CountryCode":"country","Latitude":"latitude","Longitude":"longitude","InsuredValue":"tiv","InsuredValueTotal":"tiv","TIV":"tiv","BuildingTIV":"tiv_building","ContentsTIV":"tiv_content","BITIV":"tiv_bi","GrossTIV":"tiv","PML":"pml","PMLPercent":"pml_percent","LOB":"class"}
SCHEMA_REGISTRY: Dict[str, Dict[str, str]] = {"cede": CEDE_MAP, "oed": OED_MAP}
CANONICAL_COLUMNS: List[str] = ["location_id","address","city","state","postcode","country","latitude","longitude","tiv","tiv_building","tiv_content","tiv_bi","pml","pml_percent","class"]
def detect_schema(df: pd.DataFrame) -> str:
    cols = set(df.columns)
    if {"LocID","PML"}.issubset(cols) or {"StructureTIV","ContentTIV"}.issubset(cols): return "cede"
    if {"LocationID","InsuredValue"}.issubset(cols) or {"LocationID","StreetAddress"}.issubset(cols): return "oed"
    return "custom"
def transform_to_internal(df: pd.DataFrame, schema: str) -> pd.DataFrame:
    if schema == "custom":
        norm = {c: c.strip().replace(" ","").replace(".","").replace("-","") for c in df.columns}
        return df.rename(columns=norm)
    mapping = SCHEMA_REGISTRY[schema]; return df.rename(columns=mapping)
def to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    for c in CANONICAL_COLUMNS:
        if c not in df.columns: df[c] = None
    # derive tiv
    if "tiv" in df.columns and getattr(df["tiv"], "isna", lambda: False)().all():
        parts = [c for c in ["tiv_building","tiv_content","tiv_bi"] if c in df.columns]
        if parts: df["tiv"] = df[parts].apply(pd.to_numeric, errors="coerce").fillna(0.0).sum(axis=1)
    # derive pml
    if "pml" in df.columns and getattr(df["pml"], "isna", lambda: False)().all():
        if "pml_percent" in df.columns:
            tiv = pd.to_numeric(df.get("tiv"), errors="coerce"); pct = pd.to_numeric(df["pml_percent"], errors="coerce")/100.0
            df["pml"] = (tiv * pct).fillna(0.0)
    if "country" in df.columns:
        df["country"] = df["country"].astype(str).str.upper().replace({"UK":"GB"})
    if "postcode" in df.columns:
        df["postcode"] = df["postcode"].astype(str).str.upper()
    return df[CANONICAL_COLUMNS]
