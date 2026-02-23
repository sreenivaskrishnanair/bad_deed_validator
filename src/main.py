from .validator import ValidationError, validate

from .county_lookup import load_counties, resolve_county

from .extractor import Extractor, LLMConfig, LLMExtractor
from .models import DeedEnriched
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Provider OCR TEXT
# ---------------------------------------------------------------------------
OCR_TEXT = """
*** RECORDING REQ *** 
Doc: DEED-TRUST-0042 
County: S. Clara  |  State: CA 
Date Signed: 2024-01-15 
Date Recorded: 2024-01-10 
Grantor:  T.E.S.L.A. Holdings LLC 
Grantee:  John  &  Sarah  Connor 
Amount: $1,250,000.00 (One Million Two Hundred Thousand Dollars) 
APN: 992-001-XA 
Status: PRELIMINARY 
*** END ***
"""


# ---------------------------------------------------------------------------
# Requested Orchestration
# ---------------------------------------------------------------------------
def run(ocr_text : str, cfg : LLMConfig) -> None:
    """
        Core Logic:
            1. Build the extractor.
            2. extract raw deed from OCR
            3. extract county name and tax rate
            4. validate the data
    """
    extractor = LLMExtractor(cfg)
    deed = extractor.extract(ocr_text)

    counties = load_counties(Path('counties.json'))
    county_tax_info = resolve_county(deed.county_raw, counties)
    
    enriched_deed = DeedEnriched(deed=deed, county_tax_info=county_tax_info)
    
    try:
        result = validate(enriched_deed)
    except ValidationError as e:
        raise SystemExit(f"[REJECTED] {e}")

    print("[ACCEPTED]")
    print(enriched_deed)
    print(f"closing_tax=${result.closing_tax}")



if __name__ == '__main__':

    cfg = LLMConfig(
        model='gpt-4.1-mini', 
        api_key=os.environ.get('OPENAI_API_KEY')
    )
    run(OCR_TEXT, cfg)
