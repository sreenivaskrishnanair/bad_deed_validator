from pathlib import Path
import json
from .models import CountyTaxInfo
from typing import Tuple, List
from decimal import Decimal

# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------
class CountyNotFoundError(RuntimeError):
    """ 
        Intentionally Aggressive exception for not exact match. 
        Reason: wrong county decleration can cause incorrect tax implications.
    """
    pass

# ---------------------------------------------------------------------------
# Loading from File
# ---------------------------------------------------------------------------
def load_counties(path : Path) -> List[CountyTaxInfo]:
    with open(path, 'r') as f:
        raw_data = json.load(f)
    return [CountyTaxInfo.model_validate(i) for i in raw_data]

# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------
def _normalize(s):
    s = (s or "")
    s = s.lower()
    s = s.replace(".", " ")
    s = s.replace(",", " ")
    s = s.replace("|", " ")
    s = s.replace("/", " ")
    s = s.replace("\\", " ")
    s = s.replace("county", " ")
    return " ".join(s.split())


# Explicit Allow list of well know abbreviations instead of fuzzy match 
# for deterministic, auditable behavior
ALLOWED_ABBREVIATIONS = {
    "s clara": "santa clara", 
    "s mateo": "san mateo", 
    "s cruz" : "santa cruz" 
}

# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------
def resolve_county(county_raw : str, counties : List[CountyTaxInfo]) -> CountyTaxInfo:
    """
        Core Logic:
            1. normalize raw county.
            2. check against exact matching strategy
        Edge cases:
            1. Fuzzy match (intentionally omitted) Artifact of Paranoid Engineering
            2. no match reject cleanly
    """

    if not county_raw:
        raise CountyNotFoundError("County field is empty")
    
    county = _normalize(county_raw)
    county = ALLOWED_ABBREVIATIONS.get(county, county)

    for c in counties:
        if _normalize(c.name) == county:
            return c
    
    raise CountyNotFoundError('No county found with exact match or allow list of abbreviations')
    