# tests/test_integration.py
from pathlib import Path
import os

import pytest

from src.county_lookup import load_counties, resolve_county, CountyNotFoundError
from src.extractor import LLMConfig, LLMExtractor
from src.models import DeedEnriched
from src.validator import validate, DateOrderError, AmountMisMatchError


pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set; set env please",
)


def _expected_exception(name: str):
    n = name.lower()

    if "unknown_county" in n:
        return CountyNotFoundError
    if "bad_dates" in n:
        return DateOrderError
    if "bad_money" in n:
        return AmountMisMatchError
    if "should_accept" in n:
        return None

    return Exception


def _ocr_files():
    resources_dir = Path(__file__).parent / "resources"
    files = sorted(resources_dir.glob("*.txt"))
    if not files:
        raise RuntimeError(f"No OCR samples found in {resources_dir}")
    return files


@pytest.fixture(scope="session")
def extractor():
    cfg = LLMConfig(
        model="gpt-4.1-mini",
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    return LLMExtractor(cfg)


@pytest.fixture(scope="session")
def counties():
    return load_counties(Path("counties.json"))


@pytest.mark.parametrize("ocr_file", _ocr_files(), ids=lambda p: p.name)
def test_integration_each_ocr_resource_real_llm(ocr_file: Path, extractor, counties) -> None:
    ocr_text = ocr_file.read_text(encoding="utf-8")
    expected_exc = _expected_exception(ocr_file.name)

    deed = extractor.extract(ocr_text)

    if expected_exc is CountyNotFoundError:
        with pytest.raises(CountyNotFoundError):
            resolve_county(deed.county_raw, counties)
        return

    county_tax_info = resolve_county(deed.county_raw, counties)
    enriched = DeedEnriched(deed=deed, county_tax_info=county_tax_info)

    if expected_exc is None:
        res = validate(enriched)
        assert res.closing_tax is not None
    else:
        with pytest.raises(expected_exc):
            validate(enriched)