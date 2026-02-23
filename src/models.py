from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal

class DeedExtract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    doc_id: str
    county_raw: str
    state: str
    date_signed: date
    date_recorded : date
    grantor : str
    grantee : str
    # assuming we need non - zero amount to be a valid deed
    amount_numeric : Decimal = Field(..., description='Digit amount', gt=0)
    amount_words : str = Field(..., description="spelled out amount")
    apn : str
    status : str


class CountyTaxInfo(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name : str
    tax_rate : Decimal


class DeedEnriched(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    deed : DeedExtract
    county_tax_info : CountyTaxInfo

    @property
    def tax_rate(self):
        return self.county_tax_info.tax_rate