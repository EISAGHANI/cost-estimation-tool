from dataclasses import dataclass, field
from decimal import Decimal

REMOVAL_EXEMPTION_LIMIT = Decimal("8000")  # qualifying relocation costs up to £8,000 are exempt

TAXABLE_CASH = "Taxable cash"
TAXABLE_BENEFIT = "Taxable benefit in kind"
NOT_TAXABLE = "Not taxable in the UK"


@dataclass
class BenefitLine:
    name: str
    cost: Decimal     # £ the employer pays
    treatment: str    # one of the three tags above
    taxable: Decimal  # £ added to UK taxable pay
    note: str
    source_keys: list = field(default_factory=list)


def housing(annual_rent: Decimal) -> BenefitLine:
    return BenefitLine(
        name="Housing in London (rent paid to the landlord)",
        cost=annual_rent,
        treatment=TAXABLE_BENEFIT,
        taxable=annual_rent,
        note=("Accommodation the employer rents is taxed on the greater of its annual value "
              "or the rent paid. The rent is used."),
        source_keys=["uk_accommodation_value"],
    )


def relocation_allowance(amount: Decimal) -> BenefitLine:
    return BenefitLine(
        name="Relocation allowance (cash)",
        cost=amount,
        treatment=TAXABLE_CASH,
        taxable=amount,
        note=("A cash payment that does not repay receipted qualifying costs counts as "
              "earnings, so it is taxed like salary."),
        source_keys=["uk_relocation_report"],
    )


def removal_costs(moving: Decimal, temporary_housing: Decimal) -> list:
    items = [
        ("Moving costs (flights, shipping)", moving,
         "Qualifying relocation cost (moving).", ["uk_relocation_exempt"]),
        ("Temporary housing (serviced apartment, 4 weeks)", temporary_housing,
         "Qualifying relocation cost (temporary living accommodation before the long-term home).",
         ["uk_relocation_exempt", "hmrc_temporary_accommodation"]),
    ]
    remaining = REMOVAL_EXEMPTION_LIMIT
    lines = []
    for name, cost, note, keys in items:
        exempt = min(cost, remaining)
        remaining -= exempt
        taxable = cost - exempt
        if taxable > 0:
            note += (f" £{exempt:,.2f} falls within the £8,000 limit; the excess of "
                     f"£{taxable:,.2f} is taxable.")
            keys = keys + ["uk_relocation_report"]
        lines.append(BenefitLine(name, cost, TAXABLE_BENEFIT if taxable > 0 else NOT_TAXABLE,
                                 taxable, note, keys))
    return lines