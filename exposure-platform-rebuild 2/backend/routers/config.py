
from fastapi import APIRouter
router = APIRouter()

CONFIG = {
  "metadata": {"version":"2025.08-full", "effective_from":"2025-08-10", "author":"CUO"},
  "targets": {"min_roe":0.10, "max_cor":0.90},
  "jurisdiction_overrides": {
    "UK":{"severity_factors":{"property":1.0,"casualty":1.0,"marine":1.0,"energy":1.1}},
    "US":{"severity_factors":{"property":1.2,"casualty":1.25,"marine":1.1,"energy":1.2}},
    "EU":{"severity_factors":{"property":1.05,"casualty":1.0,"marine":1.0,"energy":1.1}},
    "LatAm":{"severity_factors":{"property":1.15,"casualty":1.15,"marine":1.1,"energy":1.2}},
    "EMEA":{"severity_factors":{"property":1.1,"casualty":1.1,"marine":1.15,"energy":1.2}}
  },
  "classes": {
    "property":{"facultative":{"capacity_limit":250000000,"base_rates":{"pd_rate":0.0035,"bi_rate":0.004},
      "referral_triggers":["tsi_over_capacity","incomplete_cope_data"],
      "dynamic_thresholds":{"aal_referral_min":250000,"pml_referral_percent_tsi":0.25}}},
    "marine":{"cargo":{"capacity_limit":25000000,"base_rates":{"electronics":0.0035,"grain":0.0015,"minerals":0.001,"other":0.002},
      "commodity_factors":{"electronics":1.5,"grain":1.0,"minerals":0.8},
      "voyage_factors":{"piracy_zone":1.2,"war_zone":1.3},
      "dynamic_thresholds":{"cargo_value_referral":10000000,"piracy_zone_factor":1.2}}},
    "casualty":{"gl":{"capacity_limit":50000000,"base_rates_per_1k_turnover":{"low":1.25,"medium":1.75,"high":2.5},
      "dynamic_thresholds":{"venue_severity_referral":1.6,"turnover_referral_min":25000000}}},
    "energy":{"offshore":{"capacity_limit":250000000,"base_rates":{"fixed":0.006,"floating":0.008},
      "dynamic_thresholds":{"political_violence_load":0.2}}}
  }
}

@router.get("/effective")
def effective(jurisdiction:str="US", class_:str|None=None, product:str|None=None):
    return CONFIG
