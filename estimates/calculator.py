from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from .sources import sources
from .tax import benefits, swiss
from .tax.gross_up import gross_up
from .tax.social_security import applicable_social_security
from .tax.uk import uk_income_tax

PENNY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(PENNY, rounding=ROUND_HALF_UP)


@dataclass
class AssignmentInputs:
    home_country: str
    host_country: str
    duration_months: int
    exchange_rate: Decimal              # CHF per £1
    base_salary_chf: Decimal
    bonus_chf: Decimal
    housing_monthly_gbp: Decimal
    relocation_allowance_chf: Decimal   # year 1 only
    moving_costs_gbp: Decimal           # year 1 only
    temporary_housing_gbp: Decimal      # year 1 only
    hypothetical_swiss_tax_chf: Decimal


@dataclass
class Line:
    label: str
    amount: Decimal                     # £, rounded to pence
    working: str = ""                   # how the figure was worked out
    tag: str = ""                       # UK treatment, for benefits
    sources: list = field(default_factory=list)


@dataclass
class YearEstimate:
    year: int
    home_pay: list
    benefits: list
    host_tax: list
    deductions: list
    taxable_pay_before_tax: Decimal     # I
    gross_up: object                    # GrossUpResult
    uk_tax: object                      # UKTaxResult on I + T

    @staticmethod
    def _sum(lines):
        return sum((line.amount for line in lines), Decimal("0"))

    @property
    def home_pay_total(self):
        return self._sum(self.home_pay)

    @property
    def benefits_total(self):
        return self._sum(self.benefits)

    @property
    def host_tax_total(self):
        return self._sum(self.host_tax)

    @property
    def deductions_total(self):
        return self._sum(self.deductions)

    @property
    def total_cost(self):
        return self.home_pay_total + self.benefits_total + self.host_tax_total - self.deductions_total

    @property
    def multiple_of_home_pay(self):
        return (self.total_cost / self.home_pay_total).quantize(PENNY)


@dataclass
class AssignmentEstimate:
    inputs: AssignmentInputs
    social_security: object             # SocialSecurityDecision
    years: list
    assumptions: list

    @property
    def total_cost(self):
        return sum((year.total_cost for year in self.years), Decimal("0"))

    @property
    def total_home_pay(self):
        return sum((year.home_pay_total for year in self.years), Decimal("0"))

    @property
    def multiple_of_home_pay(self):
        return (self.total_cost / self.total_home_pay).quantize(PENNY)


def estimate_assignment(inputs: AssignmentInputs) -> AssignmentEstimate:
    decision = applicable_social_security(inputs.home_country, inputs.host_country,inputs.duration_months)
    if decision.uk_nic_due:
        raise ValueError("Assignments where UK National Insurance applies are not covered by this tool.")
    years = [_estimate_year(inputs, year, decision)
             for year in range(1, inputs.duration_months // 12 + 1)]
    return AssignmentEstimate(inputs, decision, years, _assumptions(inputs))


def _estimate_year(inputs: AssignmentInputs, year: int, decision) -> YearEstimate:
    rate = inputs.exchange_rate

    def to_gbp(chf):
        return money(Decimal(chf) / rate)

    gross_chf = inputs.base_salary_chf + inputs.bonus_chf

    # 1. Home pay: what the employee would earn in Zurich.
    home_pay = [
        Line("Base salary", to_gbp(inputs.base_salary_chf),
             f"CHF {inputs.base_salary_chf:,.2f} at CHF {rate} per £1"),
        Line("Bonus", to_gbp(inputs.bonus_chf),
             f"CHF {inputs.bonus_chf:,.2f} at CHF {rate} per £1"),
    ]

    # 2. Assignment benefits, each tagged with its UK treatment.
    benefit_lines = [benefits.housing(money(inputs.housing_monthly_gbp * 12))]
    if year == 1:
        benefit_lines.append(benefits.relocation_allowance(to_gbp(inputs.relocation_allowance_chf)))
        benefit_lines += benefits.removal_costs(money(inputs.moving_costs_gbp),
                                                money(inputs.temporary_housing_gbp))
    benefit_rows = [
        Line(b.name, b.cost, f"{b.note} Taxable in the UK: £{b.taxable:,.2f}.", b.treatment,
             sources(*b.source_keys))
        for b in benefit_lines
    ]
    taxable_benefits = sum((b.taxable for b in benefit_lines), Decimal("0"))

    # 4 (needed first). Hypothetical Swiss deductions, as if the employee had stayed home.
    hypo_tax = to_gbp(inputs.hypothetical_swiss_tax_chf)
    employee_ss = swiss.social_security_share(gross_chf)
    hypo_ss = to_gbp(employee_ss.total)
    deductions = [
        Line("Hypothetical Swiss income tax", hypo_tax,
             f"CHF {inputs.hypothetical_swiss_tax_chf:,.2f}: federal, cantonal and communal tax, "
             f"single, city of Zurich, no church tax",
             sources=sources("ch_tax_calculator")),
        Line("Hypothetical Swiss social security (employee share)", hypo_ss,
             f"AHV/IV/EO 5.3% of CHF {gross_chf:,.2f} = CHF {employee_ss.ahv_iv_eo:,.2f}; "
             f"unemployment 1.1% of CHF {min(gross_chf, swiss.ALV_CEILING_CHF):,.2f} = "
             f"CHF {employee_ss.alv:,.2f}",
             sources=sources("ch_ss_rates")),
    ]

    # 3. Host tax: UK tax on I, grossed up because the tax the employer pays is itself income.
    taxable_pay = sum((line.amount for line in home_pay), Decimal("0")) - hypo_tax - hypo_ss + taxable_benefits
    result = gross_up(taxable_pay)
    uk_tax = uk_income_tax(result.grossed_up_income)
    employer_ss = swiss.social_security_share(gross_chf)
    host_tax = [
        Line("UK income tax, including tax on tax", money(result.tax),
             f"I = £{taxable_pay:,.2f} (home pay − hypothetical deductions + taxable benefits). "
             f"Solving T = UKTax(I + T) took {len(result.steps)} rounds: "
             f"tax on £{result.grossed_up_income:,.2f} is £{result.tax:,.2f}.",
             sources=sources("hmrc_gross_up", "uk_income_tax_rates", "uk_allowance_taper")),
        Line("UK National Insurance", Decimal("0.00"), decision.rule,
             sources=sources("uk_ss_from_switzerland")),
        Line("Swiss social security paid during the assignment", to_gbp(employee_ss.total + employer_ss.total),
             f"Employee share CHF {employee_ss.total:,.2f} + employer share CHF {employer_ss.total:,.2f}. "
             f"The employee's share is recovered through the hypothetical deduction below.",
             sources=sources("ch_ss_rates", "uk_ss_from_switzerland")),
    ]

    return YearEstimate(year, home_pay, benefit_rows, host_tax, deductions,
                        taxable_pay, result, uk_tax)


def _assumptions(inputs: AssignmentInputs) -> list:
    return [
        "Tax equalisation: the employee keeps home pay minus hypothetical Swiss tax and "
        "social security; the employer pays the actual UK tax.",
        "The employee is UK tax resident in both years and leaves Swiss tax residence. "
        "UK 2026/27 rates and bands are used for both years.",
        f"Exchange rate fixed at CHF {inputs.exchange_rate} per £1 for the whole assignment.",
        "Swiss social security continues under a certificate of coverage, so no UK National "
        "Insurance (Class 1 or Class 1A) is due. Contributions are on salary and bonus only.",
        "Left out: occupational pension (BVG), Swiss family allowance and accident insurance "
        "contributions, and church tax.",
        "Hypothetical Swiss income tax is the figure entered above, taken from the official "
        "Swiss Federal Tax Administration calculator.",
        "The relocation allowance, moving costs and temporary housing are paid in year 1 only.",
        "This is an exercise, not tax advice.",
    ]