from dataclasses import dataclass, field
from decimal import Decimal

PERSONAL_ALLOWANCE = Decimal("12570")
TAPER_THRESHOLD = Decimal("100000")

BANDS = [
    ("Basic rate", Decimal("37700"), Decimal("0.20")),
    ("Higher rate", Decimal("125140"), Decimal("0.40")),
    ("Additional rate", None, Decimal("0.45")),
]


@dataclass
class BandLine:
    name: str
    amount: Decimal
    rate: Decimal
    tax: Decimal

    @property
    def percent(self) -> str:
        return f"{self.rate * 100:.0f}%"


@dataclass
class UKTaxResult:
    income: Decimal
    personal_allowance: Decimal
    taxable_income: Decimal
    bands: list = field(default_factory=list)
    total: Decimal = Decimal("0")


def personal_allowance(income: Decimal) -> Decimal:
    """Personal Allowance after the taper above £100,000."""
    if income <= TAPER_THRESHOLD:
        return PERSONAL_ALLOWANCE
    reduction = (income - TAPER_THRESHOLD) / 2
    return max(Decimal("0"), PERSONAL_ALLOWANCE - reduction)


def uk_income_tax(income: Decimal) -> UKTaxResult:
    income = Decimal(income)
    allowance = personal_allowance(income)
    taxable = max(Decimal("0"), income - allowance)

    result = UKTaxResult(income=income, personal_allowance=allowance, taxable_income=taxable)
    lower = Decimal("0")
    for name, upper, rate in BANDS:
        if taxable <= lower:
            break
        top = taxable if upper is None else min(taxable, upper)
        amount = top - lower
        tax = amount * rate
        result.bands.append(BandLine(name, amount, rate, tax))
        result.total += tax
        lower = top
    return result