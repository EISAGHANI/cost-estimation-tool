from dataclasses import dataclass, field
from decimal import Decimal

from .uk import uk_income_tax

TOLERANCE = Decimal("0.01")
MAX_ITERATIONS = 100


@dataclass
class GrossUpResult:
    base_income: Decimal       
    tax: Decimal                
    grossed_up_income: Decimal 
    steps: list = field(default_factory=list)


def gross_up(base_income: Decimal) -> GrossUpResult:
    base_income = Decimal(base_income)
    tax = Decimal("0")
    steps = []
    for round_number in range(1, MAX_ITERATIONS + 1):
        new_tax = uk_income_tax(base_income + tax).total
        steps.append((round_number, tax, new_tax))
        if abs(new_tax - tax) < TOLERANCE:
            return GrossUpResult(base_income, new_tax, base_income + new_tax, steps)
        tax = new_tax
    raise ValueError("The tax-on-tax calculation did not settle. Please check the amounts entered.")