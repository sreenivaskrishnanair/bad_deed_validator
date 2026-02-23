from .models import DeedEnriched
from .money_utils import MoneyParserError, words_to_number
from dataclasses import dataclass
from decimal import Decimal

# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------
class ValidationError(RuntimeError):
    pass

class DateOrderError(ValidationError):
    pass

class AmountMisMatchError(ValidationError):
    pass


# ---------------------------------------------------------------------------
# Return Result
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ValidationResult:
    closing_tax : Decimal


def monetize(x : Decimal) -> Decimal:
    return x.quantize(Decimal("0.01")) 

def validate(enriched : DeedEnriched) -> ValidationResult:
    deed = enriched.deed

    # 1. check for signing fate:
    if deed.date_recorded < deed.date_signed:
        raise DateOrderError(f'Impossible for date_recorded to be before date_signed')
    
    # money mathcing check
    try:
        words_val = monetize(words_to_number(deed.amount_words))
    except MoneyParserError as e:
        raise AmountMisMatchError(f"Cannot parse amount words reliably: {e}")
    
    numeric_val = monetize(deed.amount_numeric)

    if words_val != numeric_val:
        raise AmountMisMatchError('numeric val, and word val dont match up')
    
    tax_rate = Decimal(enriched.tax_rate)
    closing_tax = monetize(tax_rate * numeric_val)

    return ValidationResult(closing_tax=closing_tax)
