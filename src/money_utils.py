from decimal import Decimal

class MoneyParserError(RuntimeError):
    pass

_UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19,
}

_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

_SCALES = {
    "hundred": 100,
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
}


def _clean(words : str) -> list[str]:
    s = (words or "").lower()
    s = s.replace("-", " ")
    tokens = [t for t in s.split() if t not in {"and", "dollars", "dollar"}]
    return tokens

def words_to_number(words : str) -> Decimal:
    tokens = _clean(words=words)

    if not tokens:
        raise MoneyParserError("empty words")
    
    total, current = 0, 0
    for t in tokens:
        if t in _UNITS:
            current += _UNITS[t]
        elif t in _TENS:
            current += _TENS[t]
        elif t in _SCALES:
            scale = _SCALES[t]
            if scale == 100:
                current = (current or 1) * 100
            else:
                total += current * scale
                current = 0
        else:
            raise MoneyParserError(f"Illegal token '{t}'")

    return Decimal(total + current)